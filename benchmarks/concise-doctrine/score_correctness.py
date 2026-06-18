"""Correctness + mutation adapter for the concise-doctrine benchmark (Phase 4).

Adapts the tdd-vs-siv grading logic (grade.py + mutate.py) to the concise-doctrine
run-dir layout:

  <root>/<task>/<arm>/<model>/run-<n>/
    outputs/<impl>
    outputs/<tests>
    meta.json

Key difference from tdd-vs-siv grade.py: that file hard-codes ROOT to its own
parent directory and reads the tdd-vs-siv manifest. This adapter:
  - Accepts the manifest and hidden_root explicitly (no global path coupling).
  - Gates mutation on the unmutated agent suite being green first (tdd-vs-siv
    gotcha: broken env fakes a perfect mutation score).
  - Returns status='unscorable' (never 1.0) when the suite is red or the env
    is broken. Never swallows exceptions silently.

CLI:
  score_correctness.py --run-dir <d> [--task <id>]
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent  # benchmarks/concise-doctrine
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

# tdd-vs-siv harness provides the AST mutation engine; it has no hardcoded
# paths — safe to import via sys.path injection.
TDD_HARNESS = HERE.parent / "tdd-vs-siv" / "harness"
if str(TDD_HARNESS) not in sys.path:
    sys.path.insert(0, str(TDD_HARNESS))

from mutate import mutation_score  # noqa: E402

MANIFEST_PATH = HERE / "tasks" / "manifest.json"
# hidden/ paths in manifest are relative to benchmarks/concise-doctrine
HIDDEN_ROOT = HERE


# ---------------------------------------------------------------------------
# core helpers — one operation each, ≤4 params
# ---------------------------------------------------------------------------

def _run_pytest(workdir: Path, test_file: str, name_filter: str | None = None) -> tuple[int, int]:
    """Return (passed, total) from pytest, or (0, 0) on timeout / collection error."""
    cmd = [
        sys.executable, "-m", "pytest", test_file,
        "-q", "--no-header", "-p", "no:cacheprovider",
    ]
    if name_filter:
        cmd += ["-k", name_filter]
    try:
        r = subprocess.run(cmd, cwd=workdir, capture_output=True, timeout=120, text=True)
    except subprocess.TimeoutExpired:
        return 0, 0
    out = r.stdout + r.stderr
    passed = sum(int(m.group(1)) for m in re.finditer(r"(\d+) passed", out))
    failed = sum(int(m.group(1)) for m in re.finditer(r"(\d+) failed", out))
    errors = sum(int(m.group(1)) for m in re.finditer(r"(\d+) error", out))
    return passed, passed + failed + errors


def _count_test_functions(test_src: str) -> int:
    """Count `def test_` definitions in *test_src*."""
    return len(re.findall(r"^\s*def test_", test_src, re.M))


def score_run(run_dir: Path, task: str, manifest: dict, hidden_root: Path) -> dict:
    """Grade one run: agent suite + hidden suite + mutation score.

    Mutation is gated on the agent's own suite being green first (a broken env
    otherwise fakes a perfect score — the known tdd-vs-siv gotcha).

    Returns a dict with keys:
      agent_tests_pass, n_agent_tests,
      hidden_dw, hidden_offdw,
      mutation_killed, mutation_total, mutation_score
    Or {'status': 'unscorable', 'reason': str} on entry-validation failure.
    """
    spec = manifest[task]
    outputs = run_dir / "outputs"
    impl_path = outputs / spec["impl"]
    tests_path = outputs / spec["tests"]
    hidden_path = hidden_root / spec["hidden"]

    row: dict = {
        "agent_tests_pass": None,
        "n_agent_tests": 0,
        "hidden_dw": None,
        "hidden_offdw": None,
        "mutation_killed": None,
        "mutation_total": None,
        "mutation_score": None,
    }

    if not impl_path.exists():
        return {"status": "unscorable", "reason": f"impl missing: {spec['impl']}"}

    # Count agent tests if tests exist.
    if tests_path.exists():
        row["n_agent_tests"] = _count_test_functions(tests_path.read_text())

    with tempfile.TemporaryDirectory() as _d:
        work = Path(_d)
        shutil.copy(impl_path, work / spec["impl"])

        # 1. Agent suite against agent code (sanity check).
        if tests_path.exists():
            shutil.copy(tests_path, work / spec["tests"])
            p, t = _run_pytest(work, spec["tests"])
            row["agent_tests_pass"] = (t > 0 and p == t)

        # 2. Hidden suite — correctness, bucketed by DW prefix.
        if hidden_path.exists():
            shutil.copy(hidden_path, work / "test_hidden.py")
            dw_p, dw_t = _run_pytest(work, "test_hidden.py", name_filter="test_dw_")
            off_p, off_t = _run_pytest(work, "test_hidden.py", name_filter="test_offdw_")
            row["hidden_dw"] = f"{dw_p}/{dw_t}"
            row["hidden_offdw"] = f"{off_p}/{off_t}"
            (work / "test_hidden.py").unlink()

        # 3. Mutation score — only when the unmutated agent suite is green.
        #    A red suite makes every mutant "fail" for the wrong reason — the
        #    mutation score would be artificially inflated to 1.0, hiding the truth.
        if tests_path.exists() and row["agent_tests_pass"] is True:
            try:
                k, n, _ = mutation_score(work / spec["impl"], work / spec["tests"])
                row["mutation_killed"] = k
                row["mutation_total"] = n
                row["mutation_score"] = round(k / n, 3) if n else None
            except Exception as exc:
                # Mutation engine failure is recorded, not swallowed.
                row["mutation_score"] = f"error: {exc}"
        elif tests_path.exists() and row["agent_tests_pass"] is False:
            row["mutation_score"] = "n/a (suite not green)"
        elif not tests_path.exists():
            row["mutation_score"] = "n/a (tests missing)"

    return row


def grade_run_dir(run_dir: Path) -> dict:
    """Top-level entry point: resolve task from meta.json, then call score_run.

    Returns score_run's dict, plus 'task', 'impl_found', 'tests_found' fields.
    """
    def _unscorable(reason: str) -> dict:
        return {"status": "unscorable", "reason": reason}

    if not run_dir.is_dir():
        return _unscorable(f"run_dir does not exist: {run_dir}")

    meta_path = run_dir / "meta.json"
    if not meta_path.exists():
        return _unscorable("meta.json missing")

    try:
        meta = json.loads(meta_path.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        return _unscorable(f"meta.json unreadable: {exc}")

    task = meta.get("task")
    if not task:
        return _unscorable("meta.json missing 'task' field")

    try:
        manifest = json.loads(MANIFEST_PATH.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        return _unscorable(f"manifest unreadable: {exc}")

    if task not in manifest:
        return _unscorable(f"task {task!r} not in manifest")

    spec = manifest[task]
    outputs = run_dir / "outputs"
    impl_found = (outputs / spec["impl"]).exists()
    tests_found = (outputs / spec["tests"]).exists()

    scored = score_run(run_dir, task, manifest, HIDDEN_ROOT)
    if isinstance(scored, dict) and scored.get("status") == "unscorable":
        return scored | {"task": task, "impl_found": impl_found, "tests_found": tests_found}

    return scored | {
        "task": task,
        "impl_found": impl_found,
        "tests_found": tests_found,
        "run_status": meta.get("status", "unknown"),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cli(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="Correctness + mutation scorer")
    ap.add_argument("--run-dir", required=True, help="run dir containing outputs/ and meta.json")
    ap.add_argument("--task", help="task id (overrides meta.json lookup)")
    args = ap.parse_args(argv)

    run_dir = Path(args.run_dir)

    if args.task:
        try:
            manifest = json.loads(MANIFEST_PATH.read_text())
        except (json.JSONDecodeError, OSError) as exc:
            print(json.dumps({"status": "unscorable", "reason": str(exc)}))
            sys.exit(1)
        if args.task not in manifest:
            print(json.dumps({"status": "unscorable", "reason": f"task {args.task!r} not in manifest"}))
            sys.exit(1)
        result = score_run(run_dir, args.task, manifest, HIDDEN_ROOT)
    else:
        result = grade_run_dir(run_dir)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    _cli()
