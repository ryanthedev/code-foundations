# Discovery + Design: Phase 3 - Headless build-runner

## Assumption Verification (done FIRST — both HIGH-risk assumptions resolved VIABLE)

The phase brief required me to concretely investigate whether the real gated `/build` can be
driven headlessly *before* committing to a design, with UPDATE_PLAN as the honest answer if not.
I investigated; the answer is **viable — BUILD, not UPDATE_PLAN**. Evidence:

| Assumption | Verdict | Evidence (command-run, not inferred) |
|---|---|---|
| Full gated `/build` can be driven headlessly per task | **VIABLE** | `claude --help` confirms `-p/--print`, `--model`, `--max-turns`, `--output-format json`, `--permission-mode bypassPermissions`, `--plugin-dir`, `--add-dir`. A live `claude -p "Reply with exactly: OK" --output-format json --model sonnet --max-turns 2 --permission-mode bypassPermissions` returned a JSON result with `num_turns`, `total_cost_usd`, `subtype: success`, `stop_reason`, `terminal_reason`. So the subprocess, the model pin, the turn cap, and the turns/cost capture all exist and work. |
| One-phase `plan.md` drives `/build` without extra scaffolding | **VIABLE** | `tasks/01-duration/plan.md` (read) carries `## Context`, a `### Phase 1` with `**Gate:** Standard`, `**Done when:**` DW-IDs, and a `**Produces:**` block naming `outputs/duration.py` + `outputs/test_duration.py`. That is exactly the structure `commands/build.md` Phase 1 LOAD parses. No shim needed; the plan IS the build input. |

### The mechanism chosen, and why NOT the fallback

The brief named two candidate mechanisms. I evaluated both:

- **(b) `skill-eval` `run_eval`** — this is what tdd-vs-siv uses. Per the MCP server's own
  instructions and `benchmarks/tdd-vs-siv/README.md`, `run_eval` "runs each doctrine as an
  **isolated single-skill session**." It does NOT execute the multi-agent gated `/build`
  (worktree gate → BUILD subagent → REVIEW subagent → orchestrator commit). Using it would be
  the plan's documented **fallback** (snapshot-skill A/B, Approach A) — lower fidelity.
- **(a) headless `claude -p "/code-foundations:build <plan>"`** — drives the *real* gated build
  command (the chosen Approach B). Confirmed viable above. This is the primary path, so I am
  NOT returning UPDATE_PLAN. The fallback stays unused because the real path works.

### Why the real `/build` runs non-interactively in the sandbox (the two friction points, resolved)

1. **Worktree gate asks the user when on `main`** (`references/worktree-gate.md`): the table says
   "On feature branch, clean → Proceed (single-build mode)" with no prompt. The runner provisions
   each sandbox as its **own git repo on a feature branch** (`git init` + initial commit +
   `git checkout -b feature/bench`), so the gate sees a clean feature branch and proceeds without
   a prompt. `--permission-mode bypassPermissions` covers tool-permission prompts.
2. **Arm injection without mutating the real `agents/build-agent.md`** (DW-3.3): `/build`
   dispatches the `code-foundations:build-agent` subagent, whose body is the plugin's
   `agents/build-agent.md`. `claude --plugin-dir <path>` loads a plugin "for this session only."
   The runner copies the code-foundations plugin into a **per-run plugin sandbox**, overwrites
   that copy's `agents/build-agent.md` with the chosen arm variant (via Phase-2 `swap.set_arm`),
   and points `claude --plugin-dir <arm-plugin-sandbox>` at it. The real repo plugin is never
   touched — isolation by construction, not by restore.

## Files Found
- `benchmarks/concise-doctrine/arms/swap.py` — Phase-2 API I consume: `set_arm(arm, target) -> Path`,
  `variant_path(arm)`, `valid_arms()`, `arm_session(...)`. The `### Concise Implementation` heading
  is the arm marker (confirmed: present in concise variant, absent in baseline).
- `benchmarks/concise-doctrine/tasks/manifest.json` — `{<id>: {kind, impl, tests, hidden, plan}}` for
  6 tasks (4 greenfield/modify ported + 05-rate-limiter, 06-csv-stats).
- `benchmarks/concise-doctrine/tasks/<id>/plan.md` — build-ready one-phase plans.
- `benchmarks/concise-doctrine/tasks/<id>/starter/<impl>.py` — present for modify tasks (e.g. 03, 04).
- `benchmarks/concise-doctrine/.venv` — Python 3.12 venv with pytest (run tests through it).
- `benchmarks/tdd-vs-siv/harness/grade.py` — Phase-4 grader; expects `<run-dir>/outputs/<impl>` +
  `<run-dir>/outputs/<tests>`. My run-dir layout MUST match so Phase 4 plugs in unchanged.
- Plugin root: `.claude-plugin/plugin.json` (name `code-foundations`), `agents/build-agent.md`,
  `commands/build.md`, `skills/`, `references/`.

## Current State
No runner exists. Phase 1 (tasks) and Phase 2 (arms + swap) are committed and green
(test_phase1.py 29 tests, test_phase2.py 25 tests). The runner is the missing piece that turns a
(task, arm, model, run) into captured `outputs/` + `meta.json`.

## Gaps
- The `claude` CLI in this env is aliased to a theme-wrapper that injects `--plugin-dir` for several
  repos including code-foundations. The runner must NOT rely on the alias (subprocess gets the real
  binary). It locates the plugin source from the repo root and passes its OWN `--plugin-dir` for the
  arm sandbox. It must also avoid double-loading code-foundations from the user's config — handled by
  pointing `--plugin-dir` at the arm sandbox and giving the build the sandbox plan path explicitly.
- Headless `/build` is genuinely expensive (subagents, per-phase commits). Validation must use the
  **minimum** real invocations: exactly 1 greenfield + 1 modify (DW-3.1). All failure/isolation logic
  (DW-3.3, DW-3.4) and arm honoring (DW-3.2) are unit-tested with **mocked subprocesses** — no live
  build cost. This matches the plan's Test Coverage note ("subprocess mocking; ≥1 live smoke per kind").

## Code Standards
No `docs/code-standards.md` in the repo (checked). Follow the repo's existing Python conventions
seen in `swap.py` / `grade.py`: `from __future__ import annotations`, module + function docstrings,
type hints, stdlib-first, `argparse` CLI, no third-party deps beyond what's vendored.

## Test Infrastructure
pytest, run via `benchmarks/concise-doctrine/.venv/bin/python -m pytest`. Phase suites live at
`benchmarks/concise-doctrine/test_phase<N>.py`, import the package under test by putting the
`concise-doctrine` dir on `sys.path`. DW tests named `test_DW_<n>_<i>_*`; beyond-floor tests
`test_offdw_*`. I follow the same conventions in `test_phase3.py`. Subprocess mocking via
`unittest.mock.patch` on the runner's single subprocess seam.

## DW Verification

| DW-ID | Done-When Item | Status | Test Cases |
|-------|---------------|--------|------------|
| DW-3.1 | A single invocation produces populated `outputs/` (impl+tests) + `meta.json` for a greenfield and a modify task | COVERED | `test_DW_3_1_greenfield_run_live` + `test_DW_3_1_modify_run_live` (live, marked `slow`/`live`, run once each during validation); `test_DW_3_1_capture_collects_outputs_and_meta` (unit, fake sandbox with planted `outputs/` → asserts `outputs/<impl>`, `outputs/<tests>`, and `meta.json` schema) |
| DW-3.2 | Arm selection honored — agent's effective instructions differ baseline vs concise (marker in variant) | COVERED | `test_DW_3_2_arm_plugin_sandbox_carries_marker_concise` (concise arm sandbox's `agents/build-agent.md` contains `### Concise Implementation`); `test_DW_3_2_baseline_sandbox_lacks_marker`; `test_DW_3_2_invocation_points_at_arm_plugin_dir` (the `claude` argv includes `--plugin-dir <arm-sandbox>`) |
| DW-3.3 | Failure modes (max-turns, timeout, empty output) → `status != ok`, partial artifacts retained, no crash, real `agents/build-agent.md` byte-unchanged | COVERED | `test_DW_3_3_max_turns_yields_partial`; `test_DW_3_3_timeout_yields_fail`; `test_DW_3_3_nonzero_exit_yields_fail`; `test_DW_3_3_empty_outputs_yields_fail`; `test_DW_3_3_partial_artifacts_retained`; `test_DW_3_3_real_build_agent_byte_unchanged_after_run` (hash before/after across ok+every failure path) |
| DW-3.4 | Runs isolated — two concurrent invocations don't collide on sandbox or agent-file state | COVERED | `test_DW_3_4_distinct_run_dirs_per_invocation`; `test_DW_3_4_distinct_plugin_sandboxes`; `test_DW_3_4_concurrent_runs_no_collision` (two threads, different arms, assert each sandbox holds its own arm marker and run dirs disjoint) |

**All items COVERED:** YES (4 DW-IDs in prompt, 4 in table)

## Design Decisions

Design iterated (DP-1): considered (a) one monolithic `run()` — rejected, fails functional
cohesion and would blow the param budget; (b) a class with provision/run/capture methods sharing a
config — chosen, matches the brief's "provision / run / capture as separate routines, ≤7 params via
a config object." A first-attempt single function was rejected per RF-10.

### Module: `benchmarks/concise-doctrine/run_build.py`

**Config object (parameter-count discipline, PP-4 / RF-7).** A frozen dataclass `RunSpec` carries the
five run coordinates + out root + tunables, so every routine takes `(self_or_spec)` not 7+ scalars:

```python
@dataclass(frozen=True)
class RunSpec:
    task: str            # manifest key
    arm: str             # "baseline" | "concise"
    model: str           # "sonnet" | "opus"
    run: int             # run index
    out_root: Path       # results root
    max_turns: int = 60  # turn cap (tdd-vs-siv used 50; 60 headroom for gated build)
    timeout_s: int = 1800
```

**Status enum** — `RunStatus = Literal["ok", "partial", "fail"]`, written to `meta.json`.

**Functionally-cohesive routines (RP-6), each doing one operation:**

| Routine | Cohesion | Does |
|---|---|---|
| `run_dir(spec)` | functional | pure path: `<out_root>/<task>/<arm>/<model>/run-<n>` |
| `provision_sandbox(spec, repo_root) -> Sandbox` | functional | build the per-run sandbox: temp dir, copy task `starter/` (or empty), copy plugin → arm-plugin sandbox + `set_arm`, copy the task `plan.md` in, `git init`+commit+feature-branch so the worktree gate auto-proceeds. Returns a `Sandbox` dataclass `{root, plugin_dir, plan_path, agent_file}`. |
| `invoke_build(spec, sandbox) -> CompletedInvocation` | functional | build the `claude` argv and run it via the ONE subprocess seam `_run_claude`; parse the JSON result into `{exit, num_turns, cost_usd, subtype, stop_reason, terminal_reason}`. The single external-process boundary. |
| `capture(spec, sandbox, invocation) -> RunStatus` | functional | classify status from invocation + presence of `outputs/<impl>`/`outputs/<tests>`; copy whatever landed into `run_dir(spec)/outputs/`; write `meta.json`. Partial artifacts are retained regardless of status. |
| `execute(spec, repo_root) -> Path` | sequential (ACCEPT — orchestrator) | provision → invoke → capture in required order; documented as the top-level organizer that delegates, not does work (temporal/sequential OK per cohesion guidance). try/finally cleans the sandbox temp tree; never the real plugin. |
| `_run_claude(argv, cwd, timeout_s) -> subprocess.CompletedProcess` | functional | the mockable subprocess seam — the ONLY place `subprocess.run` is called. |
| `main()` | functional | argparse CLI → `RunSpec` → `execute`. |

**Status classification (correctness over robustness — this is a measurement pipeline, p.197):**

| Condition | status |
|---|---|
| subprocess timeout (`TimeoutExpired`) | `fail` |
| non-zero exit / JSON `is_error` / unparseable JSON | `fail` |
| `terminal_reason`/`stop_reason` indicates max-turns AND some artifact landed | `partial` |
| max-turns AND nothing landed | `fail` |
| exit 0 but `outputs/` empty or missing impl/tests | `fail` |
| exit 0, impl + tests present | `ok` |

A `partial` keeps whatever impl+tests landed (DW-3.3). Nothing is silently swallowed — every failure
path records a `status` + the raw invocation fields in `meta.json` (no empty catch; EC-3 / RF-2).

### Defensive-programming decisions (barricade, cc-defensive-programming)

- **External boundary = the `claude` subprocess + filesystem** (SKILL: "any data crossing a process
  boundary is external"). Validate at entry: `RunSpec.arm` via `swap.valid_arms()` (ValueError on
  bogus — DW like Phase-2's `set_arm("bogus")`); `task` must be a manifest key (KeyError→ValueError
  with the valid keys); model in `{sonnet, opus}`.
- **No empty catch (EC-3, RF-2):** `subprocess.TimeoutExpired` and JSON-parse errors are caught,
  logged into `meta.json`, and converted to `status="fail"` — a *recorded* failure, never silent.
- **Command-injection (SM-3, RF-7):** argv is a **list** passed to `subprocess.run` (no `shell=True`,
  no string concatenation). Task id / arm / model are validated against allowlists before use.
- **Path traversal (SM-1):** `task` is looked up as a manifest key, never joined raw into a path; the
  out root is the caller's; the sandbox is `mkdtemp`. No user string is path-joined unvalidated.
- **Real-agent-file safety (DW-3.3):** the runner NEVER writes to `<repo>/agents/build-agent.md`.
  `set_arm` is called only against the per-run plugin sandbox copy. A regression test hashes the real
  file before/after every status path.
- **Correctness stance:** a wrong "ok" would corrupt the benchmark (a failed build scored as a good
  one). So ambiguous outcomes resolve to `fail`/`partial`, never optimistically to `ok`.

### Run-dir / meta.json contract (pins Phase 4's input — Produces)

```
<out_root>/<task>/<arm>/<model>/run-<n>/
  outputs/<impl>.py        # collected from sandbox outputs/ (grade.py reads exactly here)
  outputs/<tests>.py
  meta.json                # {task, arm, model, run, status, exit, turns, cost_usd,
                           #  stop_reason, terminal_reason, impl_found, tests_found}
```

`outputs/<impl>` + `outputs/<tests>` filenames come from `manifest.json[task]` — identical to what
`grade.py` expects, so Phase 4 plugs in with no adapter beyond the run-dir walk it already has.

## Prerequisites
- [x] Phase 1 tasks + manifest exist and validate
- [x] Phase 2 `swap.set_arm` + arm variants exist (marker confirmed)
- [x] `claude` CLI present, headless flags confirmed working (live JSON probe)
- [x] `.venv` with pytest present
- [x] git available for sandbox init

## Recommendation
**BUILD.** Both HIGH-risk assumptions verified viable by direct command execution — the real gated
`/build` is drivable headlessly via `claude -p` with the arm injected through a per-run
`--plugin-dir` sandbox, and one-phase plans are valid `/build` input. The fallback (snapshot-skill
A/B) is NOT needed. Build the `run_build.py` runner with provision/invoke/capture as separate
cohesive routines and a `RunSpec` config object; unit-test failure + isolation + arm-honoring with
mocked subprocesses; prove DW-3.1 with exactly one live greenfield + one live modify run.
