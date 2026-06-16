# Discovery + Design: Phase 5 - Run the matrix + analyze + report

## Files Found

- `benchmarks/concise-doctrine/run_build.py` — Phase 3 runner (provision → invoke → capture). `execute(spec)` is the one-call API; `_run_claude` is the single mockable subprocess seam.
- `benchmarks/concise-doctrine/score_all.py` — Phase 4 aggregate scorer. `score_one_run(run_dir, out_root)` → full-schema row dict; `_discover_run_dirs(root)` walks meta.json files.
- `benchmarks/concise-doctrine/score_static.py`, `score_correctness.py`, `score_rubric.py` — individual scorers.
- `benchmarks/concise-doctrine/tasks/manifest.json` — 6 tasks: `01-duration`, `02-rpn`, `03-inventory`, `04-password`, `05-rate-limiter`, `06-csv-stats`.
- `benchmarks/concise-doctrine/arms/swap.py` — `set_arm(arm, target)`, `arm_session()`, `valid_arms()`.
- `benchmarks/concise-doctrine/_live-smoke/01-duration/baseline/sonnet/run-1/` — one captured live run (status ok, 41 turns, $1.28).
- `benchmarks/concise-doctrine/conftest.py` — registers `live` marker, `--run-live` gate.
- `benchmarks/tdd-vs-siv/results-01-duration.csv` — reference results CSV format (field names differ from Phase 4's schema; Phase 5 uses its own schema).

## Current State

- Phases 1-4 complete; 93 tests pass.
- `run_build.py` drives one (task, arm, model, run) end-to-end. Subprocess seam at `_run_claude`.
- `score_all.py` emits per-run rows with schema: `{run_id, task, arm, model, loc, cc_avg, cc_max, fn_len_max, n_funcs, mutation, hidden_dw, hidden_offdw, rubric_score, status}`.
- `results/` directory does not exist yet (created at runtime by the orchestrator).
- No `run_matrix.py`, no `REPORT.md` generator, no `test_phase5.py`.

## Gaps

- `run_matrix.py` needs to be built from scratch.
- `generate_report()` / `REPORT.md` writer needs to be built from scratch.
- `verdict()` function needs to be built and unit-tested.
- `results/` directory and CSV schema need validation coverage (schema smoke test).
- A setup note (dependencies) needs to be added (README or inline docstring).

## Code Standards

- No `docs/code-standards.md` found. Applying conventions from existing phases:
  - Python with `from __future__ import annotations`.
  - Single mockable subprocess seam (`_run_claude` pattern in `run_build.py`).
  - Boundary validation at entry (allowlists, ValueError on bad input).
  - No silent exception swallowing; failures → recorded status, never crash.
  - Functionally cohesive routines; config objects to keep params ≤ 7.
  - `HERE = Path(__file__).resolve().parent` pattern for path resolution.
  - Test IDs: `test_DW_N_M_*` for DW items, `test_offdw_*` for beyond-floor tests.
  - `# noqa: E402` after sys.path inserts.

## Test Infrastructure

- `.venv` at `benchmarks/concise-doctrine/.venv/`, Python 3.12, pytest installed.
- `conftest.py` at the `benchmarks/concise-doctrine/` level registers `live` marker.
- Pattern: mock `run_build._run_claude` + `run_build.execute` for unit tests; `@pytest.mark.live` for real subprocess tests.
- All canned data (fixtures, synthetic runs) constructed in-test with `tmp_path`.

## DW Verification

| DW-ID | Done-When Item | Status | Test Cases |
|-------|----------------|--------|------------|
| DW-5.1 | Orchestrator drives a cell end-to-end (mocked runner over full task/arm/model grid, writing rows to CSV); accounts for missing/partial cells explicitly | COVERED | `test_DW_5_1_mocked_matrix_writes_csv` — mock `execute` + `score_one_run` over full grid; verify rows written. `test_DW_5_1_partial_cell_accounted` — inject partial status rows; verify they appear in output CSV, not silently dropped. `test_DW_5_1_skip_already_scored` — pre-seed a meta.json in run dir; verify orchestrator skips it (idempotent). |
| DW-5.2 | REPORT.md shows medians per arm×model, arm deltas for every metric, explicit guardrail check (correctness+mutation non-regression) | COVERED | `test_DW_5_2_report_medians` — canned rows, verify median table present for each arm×model. `test_DW_5_2_report_deltas` — verify delta row for every metric column. `test_DW_5_2_guardrail_check` — verify guardrail section with correctness+mutation non-regression language. |
| DW-5.3 | Report ends with VERDICT: GO\|NO-GO line citing pre-registered rule and actual numbers | COVERED | `test_DW_5_3_verdict_go` — canned rows where quality↑ + no regression → GO. `test_DW_5_3_verdict_nogo_regression` — correctness/mutation regress → NO-GO. `test_DW_5_3_verdict_nogo_no_delta` — no quality delta → NO-GO. `test_DW_5_3_verdict_at_noise_threshold` — boundary at exactly noise level → deterministic NO-GO. |
| DW-5.4 | Honest accounting: N per cell, partial/unscorable counts, caveats; dropped/all-partial cells flagged, never silently omitted | COVERED | `test_DW_5_4_accounting_in_report` — canned rows incl. partial + unscorable; verify N, counts appear in report. `test_DW_5_4_all_partial_cell_flagged` — a cell where every run is partial → flagged in report, not imputed. `test_DW_5_4_no_silent_omission` — verify dropped runs appear in accounting section. |

**All items COVERED:** YES

## Design Decisions

### run_matrix.py structure

Three main layers:

1. **`MatrixSpec` dataclass** — `tasks`, `arms`, `models`, `n_runs`, `out_root`, `score_root`. Config object so orchestrate() takes one param, not 7+.

2. **`iter_cells(spec)` generator** — yields `(task, arm, model, run_n)` tuples. Pure, no I/O.

3. **`cell_is_done(run_dir)` predicate** — checks if `meta.json` exists in the run dir (idempotent skip logic). Pure path check.

4. **`run_and_score_cell(task, arm, model, run_n, spec)`** — calls `execute(RunSpec)` then `score_one_run(run_dir)`. This is the mockable unit-test seam (mock at `run_build.execute` and `score_all.score_one_run`).

5. **`orchestrate(spec, run_fn)`** — iterates cells, skips done ones, calls `run_fn`, collects rows, writes CSV. The `run_fn` default is `run_and_score_cell`; tests inject a mock.

6. **`write_csv(rows, path)`** — writes per-run CSV using Phase 4's `ROW_FIELDS` schema.

### Report generation structure

`generate_report(csv_path, out_path)` — pure transformation from CSV → markdown. Sub-functions:

- `load_rows(csv_path)` → `list[dict]`
- `compute_medians(rows)` → `dict[arm][model] -> median_metrics`
- `compute_deltas(medians)` → `dict[model] -> delta_metrics` (concise - baseline)
- `check_guardrail(deltas)` → `(passed: bool, rationale: str)`. Guardrail: correctness+mutation delta ≥ -NOISE_THRESHOLD.
- `compute_verdict(medians, deltas, guardrail)` → `(verdict: "GO"|"NO-GO", rationale: str)`
- `count_accounting(rows)` → per-cell N, partial_count, unscorable_count, all-partial flags
- `render_report(medians, deltas, guardrail, verdict, accounting, n_runs)` → markdown string

### Verdict logic (pre-registered rule)

```
GO iff:
  (1) quality_up: median LOC or cc_avg or cc_max decreases (concise < baseline) for ≥1 model
      AND rubric_score concise ≥ baseline (at-or-better readability)
  (2) no_regression: (correctness_delta ≥ -NOISE) AND (mutation_delta ≥ -NOISE)
      where NOISE = 0.05 (5 percentage points — any regression beyond this is real)
otherwise NO-GO
```

Boundary resolution: at-noise-threshold (delta == -NOISE exactly) → NO-GO (strict: regression must be definitively absent for GO). This is deterministic.

### Noise threshold

`NOISE_THRESHOLD = 0.05` — constant, clearly named, in one place. Any correctness or mutation drop larger than 5pp is a regression. This matches the "beyond noise" language in the plan.

### CSV schema for results/

Uses Phase 4's `ROW_FIELDS` exactly. File name: `results/matrix-runs.csv`. A second file `results/medians.csv` summarizes median per arm×model (for quick inspection without running the report generator).

### Idempotent/resumable design

`cell_is_done(run_dir)` checks for `run_dir / "meta.json"`. If present, the cell is skipped. This means the orchestrator can be re-run after a partial failure and will pick up where it left off without re-running cells.

### Detached-safe design

No interactive prompts. All errors written to stderr. Process exit code: 0 if all cells completed (ok or partial), 1 if any cell failed with status=fail. The orchestrator never blocks waiting for user input.

## Prerequisites

- [x] `run_build.py` exists with `execute(spec)` API
- [x] `score_all.py` exists with `score_one_run(run_dir, out_root)` API
- [x] `tasks/manifest.json` has 6 tasks
- [x] `arms/swap.py` with `valid_arms()` returning `["baseline", "concise"]`
- [x] `.venv` with `pytest` and `radon`
- [x] conftest.py with `live` marker

## Recommendation

BUILD
