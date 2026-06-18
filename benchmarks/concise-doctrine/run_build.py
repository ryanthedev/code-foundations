"""Headless build-runner for the concise-doctrine full-build A/B (Phase 3).

Drives the *real* gated `/code-foundations:build` flow for ONE
(task, arm, model, run) into an isolated sandbox and captures the produced
implementation + tests.

Why this shape (verified in discovery, not assumed):
  - The full gated build is drivable headlessly via the `claude` CLI:
    `claude -p "/code-foundations:build <plan>" --output-format json --model M
            --max-turns N --permission-mode bypassPermissions --plugin-dir <arm-plugin>`
    The JSON result carries `num_turns`, `total_cost_usd`, exit/`is_error`,
    `stop_reason`, `terminal_reason` — everything meta.json needs.
  - The arm variable is `agents/build-agent.md`. `/build` dispatches the
    `code-foundations:build-agent` subagent whose body is that file. To honor an
    arm WITHOUT mutating the repo's real agent file, each run gets its own
    *plugin sandbox* (a copy of the code-foundations plugin) whose
    `agents/build-agent.md` is the chosen arm variant, and `claude` is pointed at
    it with `--plugin-dir`. The real plugin is never written — isolation by
    construction (DW-3.3, DW-3.4).
  - A one-phase task `plan.md` is valid `/build` input as-is (no shim).

Boundary discipline (cc-defensive-programming): the `claude` subprocess and the
filesystem are external. Inputs are validated at entry (arm/task/model allowlists);
the subprocess is run via a list-argv (no shell, no injection); timeouts, non-zero
exits, unparseable JSON, and empty output are caught and recorded as a run `status`
— never an unhandled crash, never a silent swallow.

CLI:
  run_build.py --task <id> --arm <baseline|concise> --model <sonnet|opus>
               --run <n> --out <root>
  → writes <root>/<task>/<arm>/<model>/run-<n>/outputs/ (produced impl + tests)
    and  <root>/<task>/<arm>/<model>/run-<n>/meta.json
         {task, arm, model, run, status, exit, turns, cost_usd, ...}
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

# `arms.swap` is the Phase-2 arm-swap API. Make `benchmarks/concise-doctrine`
# importable as the package parent so `from arms import swap` resolves whether the
# runner is launched from the repo root or its own directory.
HERE = Path(__file__).resolve().parent  # benchmarks/concise-doctrine
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from arms import swap  # noqa: E402

# Repo root = .../code-foundations (HERE is benchmarks/concise-doctrine).
REPO_ROOT = HERE.parent.parent
MANIFEST_PATH = HERE / "tasks" / "manifest.json"

# Plugin source dirs copied into each per-run plugin sandbox. The plugin manifest
# (.claude-plugin) plus the agent/command/skill/reference bodies the build needs.
_PLUGIN_PARTS = (".claude-plugin", "agents", "commands", "skills", "references")

# Allowlists for the two free-text-ish coordinates (defense at the boundary).
_MODELS = ("sonnet", "opus")

RunStatus = Literal["ok", "partial", "fail"]


# --------------------------------------------------------------------------- #
# Value types (frozen — no behavior beyond construction; validated at the edge) #
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class RunSpec:
    """The five run coordinates + output root + tunables for one invocation.

    A config object so every routine takes one parameter, not 7+ scalars
    (parameter-count discipline). Validated by `RunSpec.validated(...)`.
    """

    task: str
    arm: str
    model: str
    run: int
    out_root: Path
    max_turns: int = 60
    timeout_s: int = 1800

    @staticmethod
    def validated(
        task: str,
        arm: str,
        model: str,
        run: int,
        out_root: Path | str,
        max_turns: int = 60,
        timeout_s: int = 1800,
    ) -> "RunSpec":
        """Construct a RunSpec, rejecting bad coordinates at the boundary.

        Bad arm/task/model raise ValueError (with the valid set) rather than
        flowing a bogus value into a path or a subprocess argv.
        """
        if arm not in swap.valid_arms():
            raise ValueError(
                f"unknown arm {arm!r}; expected one of {swap.valid_arms()}"
            )
        tasks = tuple(_manifest())
        if task not in tasks:
            raise ValueError(f"unknown task {task!r}; expected one of {tasks}")
        if model not in _MODELS:
            raise ValueError(f"unknown model {model!r}; expected one of {_MODELS}")
        if run < 0:
            raise ValueError(f"run index must be >= 0, got {run}")
        return RunSpec(
            task=task,
            arm=arm,
            model=model,
            run=run,
            out_root=Path(out_root),
            max_turns=max_turns,
            timeout_s=timeout_s,
        )


@dataclass(frozen=True)
class Sandbox:
    """Filesystem locations the runner provisions for one run."""

    root: Path          # the sandbox working dir (cwd for the build)
    plugin_dir: Path    # the per-run plugin copy with the arm swapped in
    plan_path: Path     # the task plan.md copied into the sandbox
    agent_file: Path    # plugin_dir/agents/build-agent.md (the swapped arm)


@dataclass(frozen=True)
class CompletedInvocation:
    """Parsed result of one headless `claude` build subprocess."""

    exit: int
    timed_out: bool
    is_error: bool
    num_turns: int | None
    cost_usd: float | None
    stop_reason: str | None
    terminal_reason: str | None
    raw_result: str          # the `result` text or a short error note


# --------------------------------------------------------------------------- #
# Pure helpers                                                                  #
# --------------------------------------------------------------------------- #

def _manifest() -> dict:
    """Load the task manifest (the task-id allowlist + per-task file names)."""
    return json.loads(MANIFEST_PATH.read_text())


def run_dir(spec: RunSpec) -> Path:
    """Pure path: <out_root>/<task>/<arm>/<model>/run-<n>. No filesystem writes."""
    return spec.out_root / spec.task / spec.arm / spec.model / f"run-{spec.run}"


# --------------------------------------------------------------------------- #
# Functionally-cohesive stages: provision -> invoke -> capture                  #
# --------------------------------------------------------------------------- #

def provision_sandbox(spec: RunSpec, repo_root: Path = REPO_ROOT) -> Sandbox:
    """Build the isolated sandbox for one run (one operation: provision).

    Steps: temp dir; seed with the task `starter/` (modify) or empty (greenfield);
    copy the plugin into an arm-plugin sandbox and swap the arm onto its
    `agents/build-agent.md`; copy the task `plan.md` in; `git init` + commit +
    feature branch so the build's worktree gate auto-proceeds non-interactively.

    Never writes to the real `repo_root/agents/build-agent.md` — the swap target is
    always the sandbox copy.
    """
    spec_entry = _manifest()[spec.task]
    root = Path(tempfile.mkdtemp(prefix=f"runbuild-{spec.task}-{spec.arm}-"))

    # 1. Per-run plugin sandbox: copy the plugin, then swap the arm onto ITS
    #    agents/build-agent.md. The real plugin (repo_root) is read, never written.
    plugin_dir = root / "plugin"
    plugin_dir.mkdir()
    for part in _PLUGIN_PARTS:
        src = repo_root / part
        if src.is_dir():
            shutil.copytree(src, plugin_dir / part)
        elif src.exists():
            shutil.copy2(src, plugin_dir / part)
    agent_file = plugin_dir / "agents" / "build-agent.md"
    swap.set_arm(spec.arm, agent_file)  # arm variant -> sandbox agent file only

    # 2. Seed the working tree: modify tasks start from starter/; greenfield empty.
    work = root / "work"
    work.mkdir()
    starter = HERE / "tasks" / spec.task / "starter"
    if spec_entry["kind"] == "modify" and starter.is_dir():
        for item in starter.iterdir():
            dest = work / item.name
            if item.is_dir():
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, dest)

    # 3. Copy the task plan into the sandbox at the path /build expects.
    plans_dir = work / ".code-foundations" / "plans"
    plans_dir.mkdir(parents=True)
    plan_path = plans_dir / f"{spec.task}-plan.md"
    # manifest "plan" is e.g. "tasks/01-duration/plan.md", relative to HERE.
    shutil.copy2(HERE / spec_entry["plan"], plan_path)

    # 4. git init + commit + feature branch so the build's worktree gate sees a
    #    clean feature branch and auto-proceeds (no interactive prompt).
    _git_init_feature_branch(work)

    return Sandbox(root=root, plugin_dir=plugin_dir, plan_path=plan_path,
                   agent_file=agent_file)


def _git_init_feature_branch(work: Path) -> None:
    """Make `work` a git repo on a clean feature branch (worktree-gate auto-pass)."""
    env_cmds = [
        ["git", "init", "-q"],
        ["git", "config", "user.email", "bench@example.invalid"],
        ["git", "config", "user.name", "bench"],
        ["git", "checkout", "-q", "-b", "feature/bench"],
        ["git", "add", "-A"],
        ["git", "commit", "-q", "-m", "sandbox seed", "--allow-empty"],
    ]
    for cmd in env_cmds:
        subprocess.run(cmd, cwd=work, check=True, capture_output=True, text=True)


def invoke_build(spec: RunSpec, sandbox: Sandbox) -> CompletedInvocation:
    """Run the headless gated build once and parse its JSON result (one operation).

    The single external-process boundary. Builds a list argv (no shell), runs it via
    `_run_claude`, and converts timeout / non-zero exit / unparseable JSON into a
    recorded CompletedInvocation — not an exception that escapes.
    """
    prompt = f"/code-foundations:build {sandbox.plan_path}"
    argv = [
        "claude", "-p", prompt,
        "--output-format", "json",
        "--model", spec.model,
        "--max-turns", str(spec.max_turns),
        "--permission-mode", "bypassPermissions",
        "--plugin-dir", str(sandbox.plugin_dir),
        "--add-dir", str(sandbox.root),
    ]

    try:
        proc = _run_claude(argv, cwd=sandbox.root, timeout_s=spec.timeout_s)
    except subprocess.TimeoutExpired:
        # Recorded failure, not a silent swallow: the run timed out.
        return CompletedInvocation(
            exit=124, timed_out=True, is_error=True, num_turns=None,
            cost_usd=None, stop_reason=None, terminal_reason="timeout",
            raw_result="subprocess timed out",
        )

    return _parse_invocation(proc)


def _parse_invocation(proc: subprocess.CompletedProcess) -> CompletedInvocation:
    """Convert a finished `claude` process into a CompletedInvocation.

    A non-zero exit, an `is_error` result, or unparseable JSON all become a
    recorded error (no exception escapes; no field is silently defaulted to a
    success-looking value).
    """
    exit_code = proc.returncode
    try:
        payload = json.loads(proc.stdout)
    except (json.JSONDecodeError, TypeError):
        # Unparseable output is a failure we can see, not one we hide.
        return CompletedInvocation(
            exit=exit_code, timed_out=False, is_error=True, num_turns=None,
            cost_usd=None, stop_reason=None, terminal_reason="unparseable-json",
            raw_result=(proc.stdout or "")[:500],
        )

    is_error = bool(payload.get("is_error")) or exit_code != 0
    return CompletedInvocation(
        exit=exit_code,
        timed_out=False,
        is_error=is_error,
        num_turns=payload.get("num_turns"),
        cost_usd=payload.get("total_cost_usd"),
        stop_reason=payload.get("stop_reason"),
        terminal_reason=payload.get("terminal_reason"),
        raw_result=str(payload.get("result", ""))[:500],
    )


def capture(spec: RunSpec, sandbox: Sandbox, invocation: CompletedInvocation) -> RunStatus:
    """Classify status, copy artifacts to the run dir, write meta.json (one operation).

    Status ∈ {ok, partial, fail} per the discovery table. Whatever impl/tests landed
    are copied into `run_dir(spec)/outputs/` regardless of status (partial artifacts
    retained). meta.json records status + all raw invocation fields.
    """
    spec_entry = _manifest()[spec.task]
    out = run_dir(spec)
    outputs = out / "outputs"
    outputs.mkdir(parents=True, exist_ok=True)

    # Collect whatever impl/tests landed in the sandbox `outputs/` (partial-safe).
    produced = sandbox.root / "work" / "outputs"
    impl_src = produced / spec_entry["impl"]
    tests_src = produced / spec_entry["tests"]
    impl_found = impl_src.is_file()
    tests_found = tests_src.is_file()
    if impl_found:
        shutil.copy2(impl_src, outputs / spec_entry["impl"])
    if tests_found:
        shutil.copy2(tests_src, outputs / spec_entry["tests"])

    status = _classify(invocation, impl_found, tests_found)

    meta = {
        "task": spec.task,
        "arm": spec.arm,
        "model": spec.model,
        "run": spec.run,
        "status": status,
        "exit": invocation.exit,
        "turns": invocation.num_turns,
        "cost_usd": invocation.cost_usd,
        "stop_reason": invocation.stop_reason,
        "terminal_reason": invocation.terminal_reason,
        "impl_found": impl_found,
        "tests_found": tests_found,
    }
    (out / "meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    return status


# Signals that the agent stopped because it ran out of turns rather than failing
# outright (max-turns is a *partial* if any artifact landed, not a hard fail).
_MAX_TURNS_SIGNALS = ("max_turns", "max-turns", "maxturns")


def _classify(invocation: CompletedInvocation, impl_found: bool, tests_found: bool) -> RunStatus:
    """Map an invocation + artifact presence to ok | partial | fail.

    Correctness over robustness (this is a measurement pipeline): an ambiguous
    outcome resolves to fail/partial, never optimistically to ok. A wrong "ok"
    would score a failed build as a good one.
    """
    if invocation.timed_out:
        return "fail"

    landed = impl_found and tests_found
    reason = " ".join(
        str(x).lower() for x in (invocation.stop_reason, invocation.terminal_reason) if x
    )
    hit_max_turns = any(sig in reason for sig in _MAX_TURNS_SIGNALS)

    if hit_max_turns:
        # Out of turns: partial if anything usable landed, else a hard fail.
        return "partial" if (impl_found or tests_found) else "fail"
    if invocation.is_error:
        return "fail"
    # Clean exit but the contract artifacts are absent -> not a usable run.
    return "ok" if landed else "fail"


def execute(spec: RunSpec, repo_root: Path = REPO_ROOT) -> Path:
    """Orchestrate provision -> invoke -> capture for one run; return the run dir.

    Sequential organizer (delegates, does no work itself). The sandbox temp tree is
    always cleaned in a finally; the real plugin is never touched.
    """
    sandbox = provision_sandbox(spec, repo_root)
    try:
        invocation = invoke_build(spec, sandbox)
        capture(spec, sandbox, invocation)
    finally:
        shutil.rmtree(sandbox.root, ignore_errors=True)
    return run_dir(spec)


# --------------------------------------------------------------------------- #
# The single mockable subprocess seam                                          #
# --------------------------------------------------------------------------- #

def _run_claude(argv: list[str], cwd: Path, timeout_s: int) -> subprocess.CompletedProcess:
    """Run the `claude` CLI. The ONE place subprocess.run is called (mock here).

    List argv + no shell = no command injection (SM-3). `check=False` because a
    non-zero exit is a recorded run status, not an exception.
    """
    return subprocess.run(
        argv, cwd=str(cwd), capture_output=True, text=True,
        timeout=timeout_s, check=False,
    )


def main(argv: list[str] | None = None) -> int:
    """CLI entry: parse args -> RunSpec -> execute. Returns a process exit code."""
    parser = argparse.ArgumentParser(
        prog="run_build.py",
        description="Headless gated-/build runner for one (task, arm, model, run).",
    )
    parser.add_argument("--task", required=True, help="manifest task id")
    parser.add_argument("--arm", required=True, help="baseline | concise")
    parser.add_argument("--model", required=True, help="sonnet | opus")
    parser.add_argument("--run", required=True, type=int, help="run index")
    parser.add_argument("--out", required=True, help="results root dir")
    parser.add_argument("--max-turns", type=int, default=60)
    parser.add_argument("--timeout-s", type=int, default=1800)
    args = parser.parse_args(argv)

    # Validate at the boundary; a bad coordinate is a usage error (exit 2), not a crash.
    try:
        spec = RunSpec.validated(
            task=args.task, arm=args.arm, model=args.model, run=args.run,
            out_root=args.out, max_turns=args.max_turns, timeout_s=args.timeout_s,
        )
    except ValueError as exc:
        parser.error(str(exc))

    out = execute(spec)
    status = json.loads((out / "meta.json").read_text())["status"]
    print(f"{status} -> {out}")
    # Process exit code mirrors the run status so callers/CI can branch on it.
    return 0 if status == "ok" else (2 if status == "fail" else 1)


if __name__ == "__main__":
    raise SystemExit(main())
