# Discovery + Design: Phase 4 - Scoring Extensions

## Files Found

- `benchmarks/concise-doctrine/run_build.py` — Phase 3 runner (produces run dirs)
- `benchmarks/concise-doctrine/conftest.py` — pytest config (live marker gate)
- `benchmarks/concise-doctrine/tasks/manifest.json` — 6 tasks, impl/tests/hidden filenames
- `benchmarks/concise-doctrine/_live-smoke/01-duration/baseline/sonnet/run-1/` — real run dir (meta.json + outputs/)
- `benchmarks/concise-doctrine/arms/` — swap.py + baseline/concise variants
- `benchmarks/tdd-vs-siv/harness/grade.py` — tdd-vs-siv grader (grade_run, _run_pytest, mutation_score import)
- `benchmarks/tdd-vs-siv/harness/mutate.py` — mutation_score(src_path, test_file, timeout)
- `benchmarks/tdd-vs-siv/harness/_smoke/01-duration/old_skill/run-1/outputs/` — thin-suite fixture
- `benchmarks/tdd-vs-siv/harness/_smoke/01-duration/with_skill/run-1/outputs/` — thorough-suite fixture
- `benchmarks/tdd-vs-siv/tasks/manifest.json` — tdd-vs-siv 4-task manifest (no `plan` field)
- `benchmarks/tdd-vs-siv/results-smoke.csv` — known grading output for DW-4.2 calibration

## Current State

- Phase 3 runner exists and is proven (one live smoke run at `_live-smoke/`).
- `radon` is NOT installed in `.venv`; installed during discovery (`uv pip install radon` → radon 6.0.1).
- `radon.raw.analyze(src).loc` gives LOC; `radon.visitors.ComplexityVisitor.from_code(src).functions` gives per-function CC + lineno/endline (fn_len = endline - lineno + 1).
- tdd-vs-siv `grade.py` / `mutate.py` exist and are reusable but are wired to tdd-vs-siv's `manifest.json` root path (`ROOT = HERE.parent`). The new adapter must re-route to concise-doctrine's manifest and task root.
- tdd-vs-siv `results-smoke.csv` gives a known score (`old_skill` → mutation 1.0, `with_skill` → mutation 1.0, hidden_dw 6/6). The known values DW-4.2 validates against.
- The live-smoke run's `duration.py` has 33 LOC, 1 function (`parse_duration`), CC=4, fn_len=25 (lineno 9, endline 33).
- No `score_static.py`, `score_rubric.py`, `score_all.py` exist yet (Phase 4 creates them).
- The `skill-eval compare_outputs` MCP tool is available for blind A/B.

## Gaps

- `radon` was not installed but is now fixed.
- No `score_*` files exist — all are created here.
- The tdd-vs-siv `grade.py` has hardcoded ROOT = its own parent; the adapter must isolate this instead of importing it directly (risk: it imports `mutate` from `sys.path` and reads its own manifest).
- The rubric judge must be a fresh-context subprocess (isolated from this process's context). The plan says to mock it in unit tests.
- `skill-eval compare_outputs` is the blind A/B tool. In tests this should be mocked; one live invocation is allowed per the cost constraint.

## Code Standards

From `docs/code-standards.md`: This is a Python benchmark, not a skill/command. The code-standards.md covers markdown authoring conventions for skills, not Python code. Conventions to apply from the phase plan and CC skills:

- Routines functionally cohesive (one operation), ≤7 params; use a config/dataclass object for grouped state.
- Validate inputs at entry (missing files, unparseable Python → `unscorable`, never a crash; no empty catch).
- No `from grade import grade_run` with a mutated sys.path — copy/adapt the relevant logic directly or wrap carefully.
- Error-handling strategy: Correctness (data pipeline context): never return 1.0 when suite is red; prefer explicit `unscorable` sentinel over returning a neutral/default value.

## Test Infrastructure

- pytest via `.venv/bin/python -m pytest`
- `conftest.py` gates `live`-marked tests behind `--run-live`
- Pattern from test_phase3.py: DW-ID-prefixed test names (`test_DW_4_1_*`, `test_DW_4_2_*`, …), off-DW tests named `test_offdw_*`
- Subprocess mocking used for costly external calls (mock `_run_claude` seam in phase 3)
- Phase 4 analog: mock the rubric judge LLM subprocess + mock `compare_outputs` in unit tests; one real invocation allowed for DW-4.3 integration smoke

## DW Verification

| DW-ID | Done-When Item | Status | Test Cases |
|-------|---------------|--------|------------|
| DW-4.1 | Static scorer returns LOC, cyclomatic (avg+max), max fn length, fn count for a known fixture with hand-verified values | COVERED | `test_DW_4_1_known_fixture` — hand-verified values from the live-smoke `duration.py` (LOC=33, cc_avg=4.0, cc_max=4, fn_len_max=25, n_funcs=1) and the tdd-vs-siv thin-fixture (LOC=15, cc_avg=4.0, cc_max=4, fn_len_max=10, n_funcs=1); `test_DW_4_1_boundary_empty_file`, `test_DW_4_1_boundary_single_fn`, `test_DW_4_1_boundary_no_functions` |
| DW-4.2 | Mutation/correctness adapter reproduces tdd-vs-siv-style scores on an existing `tdd-vs-siv` run, and returns 0/`unscorable` (not 1.0) when the suite is red or env is broken | COVERED | `test_DW_4_2_reproduces_tdd_smoke` — runs adapter on `tdd-vs-siv/harness/_smoke/01-duration/with_skill/run-1/` against tdd-vs-siv's manifest; `test_DW_4_2_red_suite_unscorable`, `test_DW_4_2_broken_env_unscorable` |
| DW-4.3 | Rubric judge returns a 0-1 score + rationale from a fresh context; blind A/B returns a winner for a paired (baseline, concise) output with labels hidden | COVERED | `test_DW_4_3_rubric_mocked` (mock subprocess, validate 0-1 + rationale fields); `test_DW_4_3_ab_mocked` (mock compare_outputs, validate winner field with labels hidden); one live integration test `test_DW_4_3_rubric_live` (skipped by default, `live` marker) |
| DW-4.4 | `score_all.py` emits the full row schema for ok and partial runs without crashing on missing artifacts | COVERED | `test_DW_4_4_full_row_ok_run` (uses _live-smoke dir), `test_DW_4_4_partial_missing_impl`, `test_DW_4_4_partial_missing_tests`, `test_DW_4_4_unparseable_impl` |

**All items COVERED:** YES

## Design Decisions

### Module layout

Four files in `benchmarks/concise-doctrine/`:

```
score_static.py    — radon-based static metrics, pure function + CLI
score_rubric.py    — fresh-context rubric judge + blind A/B helper, + CLI
score_correctness.py — thin adapter wrapping grade_run + mutation_score logic from tdd-vs-siv
score_all.py       — orchestrator: walk run dirs, call the three scorers, emit CSV rows
```

The plan says "thin adapter so existing `harness/grade.py` + `harness/mutate.py` run against the new run-dir layout." We do NOT import `grade.py` directly (it hardcodes ROOT to tdd-vs-siv and reads its own manifest). Instead we copy/adapt the two functions we need (`_run_pytest`, `grade_run` logic) into `score_correctness.py`, parameterized to use concise-doctrine's manifest. `mutate.mutation_score` IS safe to import (no hardcoded paths) — we import it from the tdd-vs-siv harness with a sys.path injection.

### score_static.py interface

```python
def static_metrics(impl_path: Path) -> dict:
    """Return {loc, cc_avg, cc_max, fn_len_max, n_funcs} or raises ValueError on parse error."""
```

Raises `ValueError` for non-parseable Python (caller records `unscorable`). Returns zeroed values for empty files (n_funcs=0, cc_avg=0.0, cc_max=0, fn_len_max=0, loc=0). LOC = `radon.raw.analyze(src).loc`. CC per-function from `ComplexityVisitor`. fn_len = endline - lineno + 1 per function (handles nested functions by taking max across all functions including closures).

### score_rubric.py interface

```python
def rubric_judge(impl_text: str, rationale_prompt: str | None = None) -> dict:
    """Call a fresh-context subprocess. Returns {score: float, rationale: str}."""

def blind_ab(run_dir_a: Path, run_dir_b: Path, task: str) -> dict:
    """Blind A/B via skill-eval compare_outputs. Returns {winner: 'A'|'B'|'tie', rationale: str}."""
```

Fresh-context = subprocess calling `claude -p "<rubric prompt + code>"` with no injected skills and `--output-format json`. Mocked in unit tests via a `_judge_subprocess` seam.

`blind_ab` uses the `skill-eval compare_outputs` MCP tool. Since we're in a subprocess context (not inside a live MCP session), we call it via the `mcp__plugin_oberskills_skill-eval__compare_outputs` tool — but that's only available inside Claude. The plan says "over `skill-eval compare_outputs`". The safe approach: `blind_ab` invokes `compare_outputs` via a subprocess call to `claude -p "use skill-eval compare_outputs to compare these two outputs"` OR is designed to be called from within a Claude session. Since Phase 5 drives the matrix from within Claude, the A/B call is orchestration-time, not scorer-time. For the scorer module, `blind_ab` will be a thin wrapper that calls `compare_outputs` via Claude subprocess (same pattern as rubric judge). Mocked in unit tests.

### score_correctness.py interface

```python
def score_run(run_dir: Path, task: str, manifest: dict, hidden_root: Path) -> dict:
    """Grade one run: agent_tests_pass, hidden_dw, hidden_offdw, mutation, mutation_score.
    Gates mutation on green agent suite first.
    Returns {agent_tests_pass, hidden_dw, hidden_offdw, mutation_killed, mutation_total, mutation_score}
    or {status: 'unscorable', reason: str} on broken env / missing files.
    """
```

Gates: impl missing → unscorable immediately. Suite red → mutation_score = 'n/a (suite not green)'. `subprocess.TimeoutExpired` → catches and records as (0,0). No empty catches.

### score_all.py output schema

```python
{
  "run_id": str,       # "<task>/<arm>/<model>/run-<n>"
  "task": str,
  "arm": str,
  "model": str,
  "loc": int | None,
  "cc_avg": float | None,
  "cc_max": int | None,
  "fn_len_max": int | None,
  "n_funcs": int | None,
  "mutation": str | float | None,   # float 0-1, or "n/a (suite not green)", or None
  "hidden_dw": str | None,          # "P/T" fraction string
  "hidden_offdw": str | None,
  "rubric_score": float | None,
  "status": str,        # "ok" | "partial" | "unscorable"
}
```

`status` from `meta.json` drives behavior: `ok` → all scorers run; `partial` → score what's present, flag missing; missing `meta.json` → `status=unscorable`.

### CC/defensive skill application

- `static_metrics`: 1 param, functional cohesion — PASS.
- `score_run`: 4 params, functional cohesion — PASS.
- `rubric_judge`: 2 params (impl_text, optional prompt) — PASS.
- `blind_ab`: 3 params — PASS.
- `score_all.py` main function: uses `argparse` config object — no >7 param functions.
- Input validation at entry: `impl_path` existence checked before `radon`; `run_dir` existence checked; `meta.json` parse wrapped in try/except (JSON decode error → unscorable); Python parse error in static_metrics → ValueError (caller catches).
- No empty catches anywhere. All exceptions either re-raised with context or recorded as `unscorable` with reason.
- Assertion vs error-handling: missing files are anticipated runtime errors (not bugs) → error handling, not assertions.

## Prerequisites

- [x] `.venv` exists at `benchmarks/concise-doctrine/.venv`
- [x] `radon` installed (confirmed during discovery, radon 6.0.1)
- [x] `benchmarks/tdd-vs-siv/harness/mutate.py` accessible (reuse via sys.path)
- [x] `benchmarks/concise-doctrine/tasks/manifest.json` exists (6 tasks)
- [x] Live smoke run exists for DW-4.4 integration test
- [x] tdd-vs-siv smoke fixtures exist for DW-4.2 calibration

## Recommendation

BUILD — all prerequisites met, design is clear, all DW items coverable.
