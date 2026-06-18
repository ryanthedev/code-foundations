# Discovery + Design: Phase 1 - Tasks-as-plans + hidden ground truth

## Files Found

- `benchmarks/tdd-vs-siv/tasks/` — 4 task dirs: 01-duration (greenfield), 02-rpn (greenfield), 03-inventory (modify), 04-password (modify)
- `benchmarks/tdd-vs-siv/tasks/manifest.json` — keys: kind, impl, tests, hidden (no `plan` field yet)
- Each task: `spec.md` (DW items + output paths) + `hidden/test_hidden.py` (`test_dw_*` + `test_offdw_*`)
- Modify tasks: `starter/` with the seed file
- `benchmarks/tdd-vs-siv/harness/grade.py` + `mutate.py` — scoring infrastructure (reusable)
- `benchmarks/tdd-vs-siv/harness/_smoke/01-duration/{with_skill,old_skill}/run-1/outputs/` — calibration pattern: thorough suite (9 tests) scores 1.0; thin DW-only suite (3 tests) scores < 1.0 on identical impl
- `benchmarks/tdd-vs-siv/README.md` — confirms harness pattern, uv venv setup, and that 04-password is the richest mutation surface

## Current State

No `benchmarks/concise-doctrine/` directory exists yet. Everything must be created. The tdd-vs-siv tasks have `spec.md` files (skill-eval prompt format) and need to be wrapped as proper build plan files (`plan.md`) that the `/build` command can consume. The hidden suites are directly portable — the grounding test format (`test_dw_*` + `test_offdw_*`) is already correct.

## Gaps

| Gap | Resolution |
|-----|-----------|
| `spec.md` format is skill-eval prompt; `/build` needs `plan.md` with phase headers, DW-IDs, Gate, Model | Wrap each spec as a one-phase plan. Preserve all DW text verbatim; add phase boilerplate. |
| Old manifest has no `plan` field | New manifest adds `plan` field per task per the Produces contract |
| 4 tasks need 2-3 new companions with richer mutation surfaces | Design 2 new greenfield tasks (rate-limiter, csv-stats) with ≥4 mutation sites each and thin-suite < 1.0 verified |
| DW-1.3 calibration requires running actual mutation scoring | Set up uv venv with pytest; run mutation_score() on reference impls against thin vs thorough suites as part of test validation |
| Mutation assumption must be verified before flagging UPDATE_PLAN | Verified below in Assumption Verification |

## Assumption Verification

**"New tasks expose a non-saturated mutation surface" (Confidence: MED)**

The existing 04-password has 2 DW items (digit-check, uppercase-check) with 4 mutation sites (two `any()` predicates, two comparison operators). TDD-scoped suite kills only 50% (0.500). The pattern: if the DW items enumerate exactly the rules, a thin suite covers exactly those rules but misses negated-boundary mutants.

For rate-limiter (token bucket): DW items cover "N calls succeed in window, N+1th fails" — a thin suite won't catch off-by-one in the count comparison (`<` vs `<=`), boundary in time window (`>=` vs `>`), or arithmetic in token replenishment. Mutation sites: at least 4 (count compare, time compare, arithmetic, bool combiner). Thin DW-only suite will miss the off-by-ones → expected thin score ~0.5–0.7.

For csv-stats: DW items cover "mean of column", "min of column", "max of column" — a thin suite passes each exact example but won't kill mutations on `sum()` vs `max()` confusion, empty-list boundary, or column-not-found path. At least 3–5 mutation sites. Expected thin score ~0.5–0.8.

**Conclusion: assumption is VALID.** The tasks can be designed to have non-saturated mutation surfaces. Proceed with BUILD.

## Code Standards

From `docs/code-standards.md`:
- Python files in benchmark tasks are implementation-only; no skill YAML conventions apply here.
- No item counts in markdown (they drift). Applied: no "Total: N" lines in plan files.
- Test functions must be externally checkable assertions, not mirrors of implementation.

## Test Infrastructure

- Python 3.12 + pytest via `uv venv -p 3.12 && uv pip install pytest`
- `benchmarks/tdd-vs-siv/harness/mutate.py` — `mutation_score(src_path, test_file)` returns `(killed, total, survivors)`
- `benchmarks/tdd-vs-siv/harness/grade.py` — `grade_run(run_dir, eval_id)` runs full scoring pipeline
- For DW-1.3 calibration tests: create a `benchmarks/concise-doctrine/tasks/_smoke/` dir mirroring the tdd-vs-siv pattern; run mutation_score() in the test for each new task.

## DW Verification

| DW-ID | Done-When Item | Status | Test Cases |
|-------|---------------|--------|------------|
| DW-1.1 | Existing 4 tasks are represented as build-ready `plan.md` files (DW-IDs present) with hidden suites carried over | COVERED | `test_DW_1_1_all_four_tasks_have_plan_md` — asserts each of 01–04 has a `plan.md` containing DW-IDs; `test_DW_1_1_hidden_suites_carried_over` — asserts each of 01–04 has `hidden/test_hidden.py` |
| DW-1.2 | 2-3 new tasks authored, each with `plan.md`, `hidden/test_hidden.py` (`test_dw_*` + `test_offdw_*`), and (modify tasks) a `starter/` | COVERED | `test_DW_1_2_new_tasks_have_plan_and_hidden` — checks 05 and 06 each have `plan.md` + `hidden/test_hidden.py`; `test_DW_1_2_hidden_suite_has_both_buckets` — asserts both `test_dw_*` and `test_offdw_*` functions exist in each new hidden suite |
| DW-1.3 | Each new task's hidden suite has non-saturated mutation surface — thin DW-only suite scores < 1.0 and thorough suite scores 1.0 on reference impl | COVERED | `test_DW_1_3_thin_suite_below_1_task_05` and `test_DW_1_3_thin_suite_below_1_task_06` — run mutation_score() with thin suites on reference impls; assert score < 1.0; `test_DW_1_3_thorough_suite_scores_1_task_05` and `test_DW_1_3_thorough_suite_scores_1_task_06` — run mutation_score() with thorough suites; assert score == 1.0 (gated on unmutated suite being green first) |
| DW-1.4 | `manifest.json` validates — every referenced file exists; `python -c` load check passes | COVERED | `test_DW_1_4_manifest_loads` — json.loads the manifest; `test_DW_1_4_all_referenced_files_exist` — walks every path value in the manifest and asserts existence; `test_DW_1_4_malformed_manifest_detected` — a dirty test: a manifest with a dangling path raises the expected error from the validator |

**All items COVERED:** YES

## Design Decisions

### Plan file format

The `/build` command (from `commands/build.md`) reads the plan file and dispatches phases. For a one-phase plan the required fields are: `## Phase N: <name>`, `**Gate:**`, `**Model:**`, `**Done when:**` with DW-IDs, `**Produces:**` with output paths. The tdd-vs-siv `spec.md` content (task description, DW items, output paths) is embedded verbatim in the plan's phase section. No orchestrator shim needed for one-phase plans — this is the minimal viable build-consumable format.

### DW-ID numbering

Ported tasks keep their original DW-ID numbers (DW-1.1/1.2/1.3, DW-2.1/2.2/2.3, DW-3.1/3.2, DW-4.1/4.2). New tasks use DW-5.x and DW-6.x respectively.

### New task choices

- **05-rate-limiter** (greenfield): sliding-window rate limiter — `allow(key: str) -> bool`. DW items: (a) N calls within window all succeed, (b) N+1th call in same window is rejected, (c) calls after the window expires are allowed again. Rich mutation surface: count compare (`<` vs `<=`), time arithmetic, window expiry compare.
- **06-csv-stats** (greenfield): `parse_and_summarize(csv_text: str, column: str) -> dict` returning `{min, max, mean}`. DW items: (a) correct min/max/mean on a 3-row CSV, (b) header-only (no data rows) raises `ValueError`, (c) missing column raises `KeyError`. Rich mutation surface: min vs max confusion (AST mutates `min` calls via BinOp/Constant), arithmetic in mean, comparison operators in bounds checking.

### Mutation calibration pattern (_smoke)

For each new task, create:
- `benchmarks/concise-doctrine/tasks/<id>/_smoke/impl.py` — reference implementation
- `benchmarks/concise-doctrine/tasks/<id>/_smoke/test_thin.py` — DW-only tests (one per DW item, no edge cases)
- `benchmarks/concise-doctrine/tasks/<id>/_smoke/test_thorough.py` — full suite covering DW + boundaries + errors

The DW-1.3 calibration tests import `mutation_score` from the tdd-vs-siv harness (adding it to sys.path) and verify the scoring contract.

### Manifest format

```json
{
  "<id>": {
    "kind": "greenfield|modify",
    "impl": "filename.py",
    "tests": "test_filename.py",
    "hidden": "tasks/<id>/hidden/test_hidden.py",
    "plan": "tasks/<id>/plan.md"
  }
}
```

## Prerequisites

- [x] tdd-vs-siv tasks exist (source for porting)
- [x] mutate.py and grade.py exist (reusable harness)
- [x] benchmarks/ directory exists
- [x] uv venv setup documented in tdd-vs-siv/README.md
- [ ] benchmarks/concise-doctrine/ does not yet exist (will create)

## Recommendation

BUILD — all gaps are resolvable, assumption is valid, all DW items are coverable.
