# Discovery + Design: Phase 5 - Analysis + REPORT

## Files Found
- `benchmarks/model-tiers/score_run.py` — `ROW_FIELDS = [task, rung, model, run_n, correct, score, tp, fp, fn, judge_fail, time_seconds, tokens, cost_usd]`, the Phase 4/5 seam. No `pilot` field in ROW_FIELDS itself.
- `benchmarks/model-tiers/judge.py` — panel() cross-vendor judge, not consumed here (Phase 5 reads scored CSVs/JSON only).
- `benchmarks/model-tiers/SCHEMA.md` — task manifest contract (`source.repo`, `source.plan`, `source.phase` — exactly DW-5.5's traceability fields).
- `benchmarks/model-tiers/calibration/status.json` — all 7 tasks `"rejected"`.
- `benchmarks/model-tiers/calibration/pilot_rows.json` — 6 tasks (all but `04-hash-progress-review`), each task keyed to 2-4 pilot-run dicts (`fable-5`, `fable-5-confirm`, `sonnet-5`, `sonnet-5-confirm` where a confirmation round ran), each row shaped like a ROW_FIELDS row plus extra `pilot: true` and `run_n` keys.
- `benchmarks/model-tiers/calibration/decisions.md` — prose log; the one line load-bearing for DW-5.3's second source (`2026-07-03T11:20:24Z [gold_validation] ... rung-4 full recall (5/5, 5/5 defects) for 04-loop-core-review, 04-hash-progress-review via live 3-judge panel`) — this is a gold-solution validation (DW-4.6), never a model-under-test pilot, for `04-hash-progress-review` (vet-rejected twice, never piloted).
- `benchmarks/model-tiers/tasks/*/manifest.json` (7 dirs) — `source.{repo,plan,phase}` present on every task, confirmed by direct read.
- `benchmarks/model-tiers/tasks/04-loop-core-review/answer-key.json` — 5 defects (`LC-1`..`LC-5`).
- `benchmarks/model-tiers/tasks/04-hash-progress-review/answer-key.json` — 4 defects (`HP-1`..`HP-4`), **not 5** — DW-5.3's table must read the real defect count per task, not assume 5.
- No `results-*.csv` anywhere under `benchmarks/model-tiers/` — confirmed by `find`/`grep`. Matrix is vacuously empty, matching the orchestrator's CRITICAL DATA-REALITY NOTE.
- `docs/code-standards.md` § Python conventions — module docstring states phase/role + seams; `from __future__ import annotations`; `pathlib.Path`; `argparse` CLI on every runnable module; dataclasses for specs (none needed here — plain dicts match `ROW_FIELDS`' existing dict shape).
- No `analyze.py` / `test_analyze.py` / `REPORT.md` exist yet — this phase creates all three from scratch.

## Current State
Phases 1-4 are complete and out of scope to touch. The matrix is real but has **zero surviving tasks and zero `results-*.csv` rows** — every one of the 7 candidate tasks was calibration-rejected (5 for headroom/saturation, 2 for a residual spec gap that loops back to earlier phases). The only empirical data available are: (a) 18 individual pilot-run dicts across 6 tasks in `pilot_rows.json` (9 sonnet-5/fable-5 paired comparisons when grouped by task+run_n — see Design Decisions on the "12" figure named in the phase context), and (b) one gold-validation recall note in `decisions.md` prose for the task that never reached pilot.

## Gaps
- Phase context prose says "12 paired pilot comparisons"; a direct count from `pilot_rows.json` (grouping by task + `run_n`, requiring both `sonnet-5` and `fable-5` present) yields **9** pairs (18 individual rows). This is computed in code from the actual JSON, not hand-typed, and the discrepancy is reported honestly in REPORT.md rather than silently overridden or silently trusted — see Design Decisions.
- The plan's Scope line (`per-defect rung-4 detection counts (model × defect × found/5)`) suggests a `/5` denominator, but real pilot data only reached n=2 runs per model (not the designed n=5) and the dispatch prompt's literal DW-5.3 text omits `/5` entirely (`found-count`). Building a table that claims `/5` would fabricate 3 runs that never happened. Design decision: report the true denominator (2 for the piloted task, 1 for the gold-validation-only task) and state explicitly that the rule's designed n=5 was never reached — this is exactly the "insufficient data" grounds for Q2, not a table-formatting nuance to paper over.
- `manifest["_task_dir"]` seam and `ROW_FIELDS` import are read-only reuse from Phase 3; no gap there.

## Code Standards
- `from __future__ import annotations`, `pathlib.Path` throughout, module docstring naming phase + seams (score_run.py/judge.py's own docstrings are the house model).
- `argparse` CLI entry point (`_cli`) mirroring `score_run.py`'s `_cli` shape.
- Task ids `NN-slug`; DW items `DW-N.M`.
- Constants for pre-registered rule text live at module level, quoted verbatim from the research doc (comment cites the exact doc section) — analysis must not invent thresholds (approach note, verbatim).

## Test Infrastructure
- `pytest` via the suite's own `.venv` (`benchmarks/model-tiers/.venv`, Python 3.12.13). `test_score_run.py`/`test_run_suite.py`/`test_judge.py` are the house style: plain `pytest` functions (no classes), `tmp_path` fixture for isolated file I/O, injectable seams (`judge_fns` in `test_score_run.py`) instead of real subprocess/CLI calls. `test_analyze.py` follows the same pattern: synthetic in-memory/tmp_path CSV rows for the known-answer tests (DW-5.1), and read-only reads of the real `calibration/pilot_rows.json` + `tasks/*/answer-key.json`/`manifest.json` for the DW-5.3/DW-5.5 structural tests (scope explicitly allows read-only consumption of calibration/).

## DW Verification

| DW-ID | Done-When Item | Status | Test Cases |
|-------|---------------|--------|------------|
| DW-5.1 | analyze.py known-answer tests pass: hand-computable paired-delta case + fixed-seed bootstrap reproducing expected interval on synthetic data | COVERED | `test_paired_deltas_hand_computable_case`, `test_bootstrap_ci_fixed_seed_is_deterministic`, `test_bootstrap_ci_hand_computable_interval_collapses_on_identical_deltas`, `test_paired_deltas_asymmetric_run_count_raises` (T-5.6) |
| DW-5.2 | REPORT.md contains one verdict per pre-registered question, rule text quoted, rule inputs shown | COVERED | `test_report_contains_q1_and_q2_verdicts`, `test_report_quotes_rule_text_verbatim`, `test_report_shows_rule_inputs`, `test_rung_verdict_judge_fail_rows_excluded_but_counted` (T-5.2), `test_rung_verdict_single_surviving_task_is_insufficient_data` (T-5.3) |
| DW-5.3 | Rung-4 per-defect detection table present (model × planted defect × found-count) — the Q2 evidence (source-labeled: pilot + gold-validation records) | COVERED | `test_rung4_defect_table_structure_and_counts`, `test_rung4_defect_table_source_labels`, `test_report_contains_defect_table` |
| DW-5.4 | Speed appears only as median+range labeled secondary; no verdict cites a sub-2x speed gap | COVERED | `test_speed_summary_median_and_range`, `test_report_speed_section_labeled_secondary`, `test_report_verdict_sections_never_mention_speed` |
| DW-5.5 | Every task row traces to its source corpus phase (repo, plan, phase) | COVERED | `test_traceability_table_reads_every_task_manifest`, `test_report_contains_traceability_table_for_all_tasks` |

**All items COVERED:** YES

## Design Decisions

**Interface (per cc-pseudocode-programming — pseudocode written before code, iterated until code-generation is near-automatic):**

```
FUNCTION load_matrix_rows(matrix_dir) -> list[dict]:
    Find every results-*.csv under matrix_dir, sorted for determinism.
    IF none found: RETURN [] (the vacuous-matrix case — never raises)
    Parse each as a DictReader, coerce numeric/bool fields per ROW_FIELDS.
    RETURN the concatenated rows.

FUNCTION filter_stat_rows(rows) -> (usable, quality_note):
    usable = rows where judge_fail is not truthy AND pilot is not truthy.
    quality_note = counts of total / judge_fail-excluded / pilot-excluded.
    RETURN usable, quality_note   # judge-failure and pilot rows are dropped
                                  # from correctness stats but the counts are
                                  # surfaced, never silently discarded.

FUNCTION paired_deltas(rows, model_a, model_b, field="score") -> dict[task, float]:
    Group usable rows by (task, model); average `field` across each group's runs.
    FOR each task present under BOTH models:
        IF the two models' run counts for that task differ: RAISE ValueError
           (an unfiltered pilot row or a genuine data anomaly leaked through —
           silently averaging mismatched n would misstate the comparison; T-5.6)
        delta[task] = mean(model_a) - mean(model_b)
    RETURN delta   # tasks missing either side are simply absent, not zeroed

FUNCTION bootstrap_ci(deltas, seed=42, n_resamples=10000, alpha=0.05) -> (mean, lo, hi):
    IF deltas empty: RETURN (0.0, 0.0, 0.0)
    rng = Random(seed)                      # fixed seed -> deterministic, reproducible
    resample_means = [mean(rng.choices(deltas, k=len(deltas))) for _ in range(n_resamples)]
    sort resample_means; RETURN (mean(deltas), percentile(alpha/2), percentile(1-alpha/2))

FUNCTION rung_verdict(rung_rows, cheaper, costlier, min_tasks=2) -> dict:
    usable, quality_note = filter_stat_rows(rung_rows)
    deltas = paired_deltas(usable, costlier, cheaper)   # positive = costlier scores higher
    IF len(deltas) < min_tasks: RETURN {verdict: "insufficient-data", n_tasks: len(deltas), ...}
    mean, lo, hi = bootstrap_ci(list(deltas.values()))
    majority_win = count(d > 0 for d in deltas.values()) > len(deltas) / 2
    consistent_win = majority_win AND lo > 0        # rule 2: CI excludes zero, favors costlier
    IF consistent_win: RETURN {verdict: "change-rule", ...}
    IF lo <= 0 <= hi:  RETURN {verdict: "no-difference→cheaper", ...}   # rule 1: tie -> cheaper
    RETURN {verdict: "keep-rule", ...}   # directional signal short of rule 2's bar

FUNCTION rung4_defect_table(pilot_rows_json, answer_keys) -> list[dict]:
    FOR each rung-4 task's answer-key defects:
        IF pilot rows exist for this task (grouped by model):
            found_count = number of that model's runs where tp==len(defects) and fn==0
                          (aggregate recall was full every recorded run; a run with
                          fn>0 would need real per-defect judge output to attribute —
                          none exists in this dataset, so such a run is marked
                          "unattributed" defensively rather than assumed-found)
            source = "pilot"
        ELSE: use the gold-validation constant (decisions.md's dated log line,
              source = "gold-validation", model = "gold-reference")
    RETURN rows: {task, defect_id, model, found_count, of_n_runs, source}

FUNCTION traceability_table(tasks_dir) -> list[dict]:
    FOR each tasks/*/manifest.json: {task: id, repo, plan, phase} from manifest["source"]
    RETURN rows   # all 7 tasks, regardless of matrix survival

FUNCTION render_report(...) -> str:
    Assemble REPORT.md: data-reality note: Q1 verdict (rungs 2-4, rule 1+2 text
    quoted verbatim, inputs shown) -> Q2 verdict (rung 4, rule 3 text quoted
    verbatim, inputs shown) -> calibration-level evidence section (code-computed
    pilot pair count, not the phase-context's rounded figure) -> rung-4 per-defect
    table -> speed (secondary, median+range only) -> traceability table ->
    data-quality note -> follow-up register.
```

**Alternative considered:** computing Q1/Q2 verdicts inline inside `render_report` rather than as standalone `rung_verdict`/`review_tier_verdict` functions. Rejected — DW-5.1 requires unit-testable known-answer behavior on synthetic data; folding the math into string templating would make the hand-computable case untestable without parsing markdown.

**Verdict-label mapping is a documented interpretation, not an invented threshold.** The research doc's pre-registered rules literally define only two things: "ties → cheaper" (rule 1) and "a consistent win, not a mean win" (rule 2, majority-of-tasks AND CI-clears-zero). The plan's `Produces:` line names a 4-value enum (`change-rule | keep-rule | no-difference→cheaper | insufficient-data`) without assigning each label a formula. `rung_verdict` maps: CI clears zero + majority → `change-rule`; CI contains zero → `no-difference→cheaper` (rule 1's literal tie case); majority-but-CI-doesn't-clear-zero (a directional signal short of rule 2's bar) → `keep-rule`. This mapping is stated here and in the module docstring so it is auditable, not silently assumed. It does not affect this run's actual verdicts (both questions resolve to `insufficient-data` at n=0 before this mapping is ever consulted).

**The "12 paired pilot comparisons" figure in the phase context does not match a direct count.** Grouping `pilot_rows.json` entries by `(task, run_n)` and requiring both `sonnet-5` and `fable-5` present yields **9** pairs (18 individual rows: 4+4+2+2+2+4 across the 6 piloted tasks). `analyze.py` computes this count from the JSON file itself (never hand-typed) and REPORT.md states the code-derived number with its exact method, noting the phase-context's rounded "~12" apparently also counts pre-bugfix pilot rounds that were superseded (and overwritten, since `pilot_rows.json` is keyed by task) in the final snapshot for `03-kv-key-mismatch` and `03-storage-meter-dedup` (the scorer-bug incident in `decisions.md`). Reporting the verifiable number rather than repeating an unverified one follows directly from not inventing/assuming figures.

**`review_tier_verdict` (Q2) is distinct from `rung_verdict`.** Q2's rule 3 is a per-defect capability-gap test (lower tier misses a defect in 0-of-5 runs that the higher tier catches in ≥3-of-5), not the generic paired-score delta rule 1/2 use for Q1. It consumes `rung4_defect_table`'s per-defect found-counts directly rather than `paired_deltas`.

## Prerequisites
- [x] Required files exist (calibration artifacts, task manifests/answer-keys) — verified by direct read.
- [x] Dependencies available (`pytest` in the suite's `.venv`; stdlib `csv`/`random`/`statistics`/`json` only — no new third-party deps).
- [x] `score_run.ROW_FIELDS` importable as the schema seam.

## Recommendation
BUILD. No plan amendment needed — the plan's own CRITICAL DATA-REALITY NOTE anticipates the empty-matrix case and the Scope/Done-When items are all satisfiable against real, already-produced Phase 1-4 artifacts (task manifests, answer keys, calibration pilot/decision records) plus a fully-testable-on-synthetic-data stats module.
