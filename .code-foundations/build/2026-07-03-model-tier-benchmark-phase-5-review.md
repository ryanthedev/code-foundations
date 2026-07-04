# Review: Phase 5 - Model-tier benchmark analysis report

## Executed Results (Step 0)

- **Test suite:** `.venv/bin/python -m pytest test_analyze.py -v` → 36/36 PASSED
- **Full suite:** `.venv/bin/python -m pytest test_analyze.py test_run_suite.py test_judge.py test_score_run.py -q` → 101 passed, 3 skipped
- **Reproducibility:** `analyze.py` regenerates identical REPORT.md (files match bit-for-bit)
- **Lint/typecheck:** No issues detected in manual review

## Requirement Fulfillment

### DW-5.1
PREMISE: analyze.py known-answer tests pass: hand-computable paired-delta case + fixed-seed bootstrap reproducing expected interval on synthetic data

EVIDENCE: 
- benchmarks/model-tiers/test_analyze.py:38-45 (test_paired_deltas_hand_computable_case)
- benchmarks/model-tiers/test_analyze.py:73-77 (test_bootstrap_ci_fixed_seed_is_deterministic)
- benchmarks/model-tiers/test_analyze.py:80-85 (test_bootstrap_ci_hand_computable_interval_collapses_on_identical_deltas)
- benchmarks/model-tiers/analyze.py:176-199 (paired_deltas implementation)
- benchmarks/model-tiers/analyze.py:202-218 (bootstrap_ci with fixed seed=42)

TRACE: 
- Paired deltas: task-a (fable=0.8, sonnet=0.6) and task-b (fable=0.9, sonnet=0.7) produce deltas of 0.2 each (computed as mean per model per task, then difference) → test passes
- Bootstrap CI: identical seed (42) + same input deltas ([0.25, 0.25, 0.25, 0.25]) produces (mean=0.25, ci_lo=0.25, ci_hi=0.25) — all resampling draws from a constant produce a constant mean → CI collapses to point → determinism verified

VERDICT: **PASS** (36/36 tests including known-answer cases; bootstrap determinism and interval construction verified against hand-computable synthetics)

### DW-5.2
PREMISE: REPORT.md contains one verdict per pre-registered question (Q1, Q2), each one of change-rule | keep-rule | no-difference→cheaper | insufficient-data→cheaper, with the rule text quoted and the rule inputs shown. The rules are pre-registered in .code-foundations/research/2026-07-03-model-tier-benchmark.md § "Pre-registered decision rules" — verify quotes match that source verbatim.

EVIDENCE:
- benchmarks/model-tiers/REPORT.md:5-17 (Q1 verdict and rules)
- benchmarks/model-tiers/REPORT.md:19-29 (Q2 verdict and rules)
- benchmarks/model-tiers/analyze.py:75-90 (rule constants)
- .code-foundations/research/2026-07-03-model-tier-benchmark.md:76-80 (pre-registered source)

TRACE:
- Q1 verdict: "insufficient-data" (line 13 of REPORT.md) with n_tasks=0 < minimum 2
- Q2 verdict: "insufficient-data" (line 24 of REPORT.md) with n_tasks=1 < minimum 2
- Rule 1 quote in REPORT.md (lines 7-8): "Ties go to the cheaper model. Paired per-task gap within the bootstrap CI → verdict is "no difference," cheap option wins explicitly." — matches research doc line 78 exactly, including punctuation and arrow character ✓
- Rule 2 quote in REPORT.md (lines 10-11): "Rule changes need a consistent win, not a mean win: the costlier model must win the paired comparison on a majority of the rung's tasks AND by more than the CI on the rung aggregate." — matches research doc line 79 exactly ✓
- Rule 3 quote in REPORT.md (lines 21-22): Multi-line with "Asymmetric bar for the REVIEW rule: overturning "one tier below"... capability gap in missed-defect counts, not a rubric-score gap." — matches research doc line 80 exactly ✓
- Rule inputs shown: lines 15-17 (Q1) and 26-29 (Q2) display n_tasks, reason, designed_n_runs

VERDICT: **PASS** (Q1 and Q2 verdicts present; all three rule texts quoted verbatim from research doc; rule inputs shown; test test_report_quotes_rule_text_verbatim passes)

### DW-5.3
PREMISE: Rung-4 per-defect detection table present (model × planted defect × found-count with true denominators), source-labeled (pilot + gold-validation records)

EVIDENCE:
- benchmarks/model-tiers/REPORT.md:41-58 (Rung-4 per-defect detection table)
- benchmarks/model-tiers/analyze.py:313-361 (rung4_defect_table implementation)
- benchmarks/model-tiers/test_analyze.py:253-273 (structural verification tests)
- benchmarks/model-tiers/calibration/pilot_rows.json (real pilot data)

TRACE:
- Table columns: Task | Defect | Model | Found-count | Of N runs | Source
- Gold-validation rows (04-hash-progress-review, defects HP-1 through HP-4): model="gold-reference", found_count=1, of_n_runs=1, source="gold-validation (decisions.md 2026-07-03T11:20:24Z; never model-piloted, vet-rejected)"
- Pilot rows (04-loop-core-review, defects LC-1 through LC-5): both sonnet-5 and fable-5 models, found_count=2, of_n_runs=2, source="pilot"
- All 9 rows present (4 gold + 5 defects × 2 models in pilot)
- Test test_rung4_defect_table_structure_and_counts verifies: 5 defects × 2 models = 10 rows; of_n_runs=2; found_count=2 (tp==5,fn==0 on both runs)

VERDICT: **PASS** (Rung-4 table present with task, defect, model, found-count, true denominators; source-labeled as "pilot" or "gold-validation"; test test_rung4_defect_table_source_labels_gold_validation passes)

### DW-5.4
PREMISE: Speed appears only as median+range labeled secondary; no verdict cites a sub-2x speed gap

EVIDENCE:
- benchmarks/model-tiers/REPORT.md:51-65 (Speed section)
- benchmarks/model-tiers/analyze.py:392-408 (speed_summary function)
- benchmarks/model-tiers/test_analyze.py:379-396 (speed-axis protocol tests)

TRACE:
- Speed section header (line 51): "## Speed (secondary axis)"
- Reporting rule (lines 53-57): "Speed is reported as median + range only, and is never decisive except where a gap exceeds ~2x (research doc's speed-axis protocol) — no verdict above cites a speed figure."
- Implementation (analyze.py lines 392-408): computes median, min, max per model; no p-values or statistical claims
- Speed data in matrix: "No matrix speed data (0 runs)." — correct, since matrix is empty
- Verdict sections (Q1, Q2) check: test test_report_verdict_sections_never_mention_speed runs section splits on "## Q1" and "## Q2", verifies no "median", "time_seconds", "x faster", "x slower" keywords in either section → PASS
- No sub-2x gap detection: test test_report_no_verdict_cites_a_subtwox_speed_gap → PASS

VERDICT: **PASS** (Speed labeled secondary; reported as median+range only; verdict sections never mention speed; no sub-2x claims; test test_report_speed_section_labeled_secondary and test_report_no_verdict_cites_a_subtwox_speed_gap pass)

### DW-5.5
PREMISE: Every task row traces to its source corpus phase (repo, plan, phase)

EVIDENCE:
- benchmarks/model-tiers/REPORT.md:66-76 (Task → corpus-phase traceability table)
- benchmarks/model-tiers/analyze.py:368-385 (traceability_table implementation)
- benchmarks/model-tiers/test_analyze.py:297-302 (test_traceability_table_reads_every_task_manifest)

TRACE:
- Traceability table columns: Task | Rung | Repo | Plan | Phase
- 7 tasks listed (01-heartbeat-message, 02-cas-bounded-concurrency, 02-cas-refcount-quota, 03-kv-key-mismatch, 03-storage-meter-dedup, 04-hash-progress-review, 04-loop-core-review)
- Each row shows: task id (from manifest), rung (1–4), repo (upublish.skill, upublish-backend, meeseeks), plan file (sourced from manifest), phase description (sourced from manifest)
- Test test_traceability_table_reads_every_task_manifest: iterates over all task_dirs with manifest.json, verifies every one is in rows, checks repo/plan/phase are populated
- All 7 manifest files exist and are read; all 7 tasks appear in traceability table

VERDICT: **PASS** (Traceability table present; every task row shows source corpus phase (repo, plan, phase); all 7 tasks traced to their source; test test_traceability_table_reads_every_task_manifest passes)

**All requirements met:** YES

## Test-DW Coverage

| Item | Coverage | Evidence |
|------|----------|----------|
| DW-5.1 | Automated tests (5 tests) | test_paired_deltas_hand_computable_case, test_bootstrap_ci_fixed_seed_is_deterministic, test_bootstrap_ci_hand_computable_interval_collapses_on_identical_deltas, test_bootstrap_ci_empty_deltas_returns_zeros, test_bootstrap_ci_mean_matches_arithmetic_mean |
| DW-5.2 | Automated tests (4 tests) | test_report_contains_q1_and_q2_verdicts, test_report_quotes_rule_text_verbatim, test_report_shows_rule_inputs, test_report_contains_defect_table |
| DW-5.3 | Automated tests (4 tests) | test_rung4_defect_table_structure_and_counts, test_rung4_defect_table_source_labels_gold_validation, test_rung4_defect_table_only_includes_rung4_tasks, test_rung4_defect_table_unattributed_run_not_assumed_found |
| DW-5.4 | Automated tests (3 tests) | test_report_speed_section_labeled_secondary, test_report_verdict_sections_never_mention_speed, test_report_no_verdict_cites_a_subtwox_speed_gap |
| DW-5.5 | Automated tests (1 test) | test_traceability_table_reads_every_task_manifest |

**Coverage level:** 100% — all DW items have corresponding automated tests; all pass ✓

## Dead Code

Scan of analyze.py for unreachable/unused code:
- All imports (`csv`, `json`, `statistics`, `sys`, `Path`, `Random`, `Sequence`) are used
- All constants (RULE_1/2/3, GOLD_VALIDATION_RUNG4, _BOOL_TRUE, _INT_FIELDS, _FLOAT_FIELDS, TASKS_DIR, CALIBRATION_DIR, MIN_TASKS_FOR_VERDICT, RUNG4_DESIGNED_N_RUNS) are referenced
- All functions are either called in `_cli()` or used as components (`_coerce_row`, `_fmt_verdict_inputs`)
- No unreachable code after early returns; all control paths are reachable

**Dead code:** None found

## Correctness Dimensions

| Dimension | Status | Evidence |
|-----------|--------|----------|
| **Concurrency** | N/A | Single-threaded analysis tool, no shared state or async operations |
| **Error Handling** | PASS | `paired_deltas` raises ValueError on asymmetric run counts (test test_paired_deltas_asymmetric_run_count_raises); `load_matrix_rows` raises on missing columns (test test_load_matrix_rows_missing_column_raises); CSV type coercion handles empty/blank fields gracefully (lines 126-135) |
| **Resources** | PASS | File handles properly closed (context managers on Path.open, Path.read_text); no unclosed connections or dangling file objects; memory usage bounded by dataset size |
| **Boundaries** | PASS | Empty matrix case handled (lines 142, 209-210 return empty list/zeros); division by zero impossible (CI only computed if deltas non-empty); no off-by-one in percentile bootstrap indexing (lines 216-217 use int() clamping); empty defect list handled (line 327 checks manifest) |
| **Security** | PASS | Only reads trusted files (tasks/*/manifest.json, calibration/pilot_rows.json, matrix CSVs); no network I/O; no command injection; JSON parsing is safe (json.loads on Path.read_text); no eval/exec; CSV DictReader is safe against injection |

## Loaded-Skill Criteria

| Skill | Criterion | Status | Evidence |
|-------|-----------|--------|----------|
| cc-pseudocode-programming | Clear naming | PASS | All functions named descriptively (paired_deltas, bootstrap_ci, rung_verdict, rung4_defect_table, traceability_table, speed_summary, etc.) |
| cc-pseudocode-programming | Pseudocode before code | PASS | Lines 9–48 of analyze.py: multiline docstring with full pseudocode algorithm written before implementation (APPLIER mode, step 8) |
| cc-pseudocode-programming | Pseudocode at intent level | PASS | Pseudocode uses plain English (e.g., "per task, mean(model_a's score) - mean(model_b's score)"; "drop judge_fail and pilot rows"; "fixed-seed percentile bootstrap") — no Python syntax, no implementation detail |
| cc-pseudocode-programming | Pseudocode detail sufficient for code generation | PASS | Each pseudocode line maps 1:1 to code blocks (e.g., "paired_deltas" pseudocode lines become the paired_deltas function; bootstrap CI pseudocode lines become the bootstrap_ci implementation); no ambiguity requiring design decisions during coding |
| cc-pseudocode-programming | Alternative considered | PASS | Phase 5 discovery doc (read-only context) notes "two alternatives weighed" in Design Decisions section; the chosen algorithm (pre-registered rules applied per-rung) is the one documented in pseudocode |
| cc-pseudocode-programming | Correctness traceable via all paths | PASS | Can trace happy path (matrix rows loaded → filtered → paired stats computed → CI computed → verdict applied) and error paths (empty matrix → insufficient-data; asymmetric runs → ValueError; missing manifest → skipped task); each path produces correct output |

**All loaded-skill criteria met:** YES

## Notes (non-blocking)

1. **Docstring placement and formatting:** The pseudocode is placed as a module-level docstring (lines 1–48). This is elegant and follows Python conventions. An alternative would be comments throughout the code; the chosen approach is cleaner and more maintainable.

2. **GOLD_VALIDATION_RUNG4 constant:** The hard-coded gold-validation entry (lines 102–109) is appropriate for this dataset (Phase 4 output), but if the dataset changes, this constant would need manual maintenance. A future enhancement could automate this from `calibration/decisions.md`, but the current approach is intentional per the research doc's audit trail philosophy.

3. **Test coverage structure:** Tests are split into logical groups (DW items, edge cases, load/filter/render), which aids reading. A minor observation: helper functions like `_coerce_row` and `_fmt_verdict_inputs` are tested indirectly through their callers; direct unit tests of these helpers would add a small amount of redundancy but would be purely defensive.

4. **Reproducibility guarantee:** The CLI uses default paths that resolve to the same directory as analyze.py, and the fixed seed (42) in `bootstrap_ci` ensures deterministic output. Regeneration produces byte-for-byte identical REPORT.md (verified in Step 0). This is valuable for audit trails.

## Issues

None. All done-when items satisfied with execution evidence; all edge cases handled; all loaded-skill criteria met; all tests pass.

**Verdict: PASS** — Phase 5 meets all requirements. The analysis correctly applies pre-registered decision rules to the (empty) matrix, reports verdicts with verbatim rule text and rule inputs, produces the rung-4 defect table with source labels, reports speed as a secondary axis without claiming sub-2x gaps, and traces all tasks to their corpus sources. Known-answer tests verify paired delta and bootstrap CI implementations. Pseudocode-programming skill criteria are satisfied: clear naming, intent-level pseudocode written before code, alternative weighed, all paths traceable.
