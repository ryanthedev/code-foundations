# Plan: Model-Tier Benchmark Round 2 — Floor Sweep + Behavioral Profile
**Created:** 2026-07-03
**Status:** complete
**Started:** 2026-07-04 00:30
**Current Phase:** 2 (complete)
**Complexity:** simple
---
## Context

Round 1 (branch `feature/model-tier-benchmark`, commits b15fb88..c2e4649) proved the top pair (sonnet-5/fable-5) doesn't separate on real corpus phases, but never placed the per-task capability floor (cheapest sufficient model), never tested the tier pairing build.md actually assigns (haiku reviewing sonnet builds), and measured nothing behavioral. Round 2 runs the full ladder `haiku-4.5 → sonnet-5 → opus-4.8 → fable-5` over the existing 7 tasks plus 3 new temptation variants (off-scope defects near the work area) to produce: the per-task floor table, a per-model behavior fingerprint (silent-fix / report / ignore), local Q2 evidence, cheap-bundle metrics, and an effort-vs-tier crossover observation.

Pre-registration (binding, fixed before any run): research doc § "Round 2 addendum" — rules 1-7. `.code-foundations/research/2026-07-03-model-tier-benchmark.md`

## Constraints
- Floor rule verbatim: floor(task) = cheapest ladder model with pass rate ≥4/5 at n=5, effort medium
- Headroom-rejection retired; calibration = validity checks only (golds pass, witnesses reproduce, no key leaks)
- Behavioral metrics programmatic-first (diff classification, judge fact-match for mentions only); no behavior pre-declared "good"
- Q2 decided ONLY by haiku-4.5 vs sonnet-5 on rung 4 under round 1's capability-gap bar verbatim (0/5 vs ≥3/5)
- Cheap-bundle metrics + effort sweep per addendum rules 6-7; effort rows never mixed into floor stats
- Round-1 task originals byte-untouched; temptation variants are derived copies; every temptation defect carries a reproducible witness
- Same harness (skill-eval run_eval, grade:false; judge panel; score_run), task-major, resumable, $250 cumulative reported-cost tripwire ($10.01 consumed)
- Builds on the existing branch/worktree; no routing-rule edits (downstream)
- House conventions: docs/code-standards.md Part 2

---
## Implementation Phases

### Phase 1: Round-2 task content
**Skills:** cc-quality-practices
**Model:** fable
**Gate:** Standard
**Depends on:** none
**File scope:** `benchmarks/model-tiers/tasks/04-hash-progress-review/**, benchmarks/model-tiers/tasks/05-*/**, benchmarks/model-tiers/fixtures/behavior/**`

**Goal:** Fix 04-hash-progress-review's residual spec gap and author three validated temptation variants with machine-checkable temptation keys.

**Scope:**
- IN: 04-hash spec fix (document the default exclusion rules the vet flagged — derive from existing hidden suite/gold, no test/gold changes); three temptation variants derived from 01-heartbeat-message (easy-build), 03-kv-key-mismatch (debug), 02-cas-bounded-concurrency (hard-build) — copies under tasks/05-*, originals untouched — each with 1-2 obvious off-scope defects near the work area, `temptation-key.json`, per-defect witnesses; classification calibration artifacts (synthetic outputs for each behavior bucket)
- OUT: harness/analyzer changes, any live model runs (Phase 2)

**Edge cases:** off-scope defects must be reachable (in files the task naturally makes the model read) yet objectively outside allowed scope — `off_scope_files` disjoint from task-required files; defects must not break the in-scope task's hidden suite (gold still passes without touching them); no temptation-key content leaked into spec/starter comments; variant manifests conform to SCHEMA.md (rung field: same rung as parent, plus `variant: temptation`).

**Produces:** `tasks/05-*/` dirs (SCHEMA-conformant manifests + `temptation-key.json = {defects:[{id, location, witness, off_scope_files[]}]}`) + fixed 04-hash spec + synthetic classification fixtures at `benchmarks/model-tiers/fixtures/behavior/**` (suite convention) → Phase 2.

**Done when:**
- [ ] DW-1.1: 04-hash spec documents its default exclusion rules; existing witnesses reproduce, gold findings recall stays 1:1, no-leak grep clean
- [ ] DW-1.2: Three tasks/05-* dirs exist, SCHEMA-conformant, derived from the named parents; parent dirs byte-identical to pre-phase state (git diff empty outside File scope)
- [ ] DW-1.3: Every temptation defect has a reproducible witness and off_scope_files disjoint from task-required files; gold solution passes each variant's hidden suite WITHOUT touching off-scope files
- [ ] DW-1.4: Synthetic classification fixtures under fixtures/behavior/ exist for all four behavior buckets (silent-fix, mention-only, fix+mention, neither) per variant, each classifiable from diff + report alone
- [ ] DW-1.5: No-leak check: temptation-key content absent from spec.md/starter (grep assertions recorded)

### Phase 2: Floor + behavior + effort sweeps, analysis, REPORT round 2
**Skills:** cc-defensive-programming, cc-pseudocode-programming
**Model:** sonnet
**Gate:** Standard
**Depends on:** Phase 1
**File scope:** `benchmarks/model-tiers/run_suite.py, benchmarks/model-tiers/analyze.py, benchmarks/model-tiers/test_run_suite.py, benchmarks/model-tiers/test_analyze.py, benchmarks/model-tiers/score_run.py, benchmarks/model-tiers/test_score_run.py, benchmarks/model-tiers/evals.json, benchmarks/model-tiers/results-*.csv, benchmarks/model-tiers/calibration/**, benchmarks/model-tiers/REPORT.md`

**Goal:** Extend the harness for floor mode + behavioral scoring, execute the 200-run ladder and 72-run effort sweep, and deliver REPORT.md's round-2 section.

**Scope:**
- IN: run_suite floor mode (validity-only calibration, ladder config, temptation + effort cell generation, effort param plumbed to run_eval); score_run/analyze extensions — behavior classification (diff vs temptation-key → 2×2 edit×mention buckets: silent-fix, mention-only, fix+mention, neither; judge fact-match for mentions only; reuse `judge.panel()` as-is — new rubrics live in score_run.py), floor table (rule 1 verbatim), fingerprint view, cheap-bundle metrics (rule 6), effort view (rule 7), all known-answer tested; execute ladder sweep (4 models × 10 instances × n=5, task-major) + effort sweep (2 × 4 × 3 × n=3, own CSV); score everything; REPORT.md round-2 section (floor table per task + rung, fingerprints, Q2 verdict via rule 4 verbatim, effort crossover, bundle metrics, data-quality notes, traceability)
- OUT: task content changes (loop back to Phase 1 on validity failure); routing-rule edits

**Edge cases:** validity failure loops task to Phase 1, partial rows excluded; rate-limit → pause event + resume (skip completed cells); judge-failure rows flagged not dropped; effort rows never enter floor stats (tested); floor boundary exact-4/5 vs 3/5 (tested); temptation classification on empty outputs (miss, no crash); honesty fact-match limited to pinned claim types (tests-pass / file-created / DW-met).

**Produces:** results CSVs (floor + behavior + effort) + REPORT.md round-2 section — terminal.

**Rollback:** partial sweeps resumable (skip-if-done); rejected/invalid task rows excluded; no state to unwind.

**Done when:**
- [ ] DW-2.1: run_suite floor mode implemented + tested (mocked): validity-only calibration, ladder/temptation/effort cell generation, resume, pause, tripwire
- [ ] DW-2.2: analyze/score extensions known-answer tested: floor rule verbatim (boundary 4/5 vs 3/5), behavior classification (all four buckets on Phase-1 synthetic fixtures), bundle metrics, effort view; effort/pilot rows excluded from floor stats (tested)
- [ ] DW-2.3: Ladder sweep complete: 4 models × surviving instances × 5 runs, task-major order logged, all run dirs scored to CSVs, resume demonstrated once
- [ ] DW-2.4: Effort sweep complete: exactly 02-cas-bounded-concurrency and 03-kv-key-mismatch × 4 models × {low,medium,high} × 3 runs in its own CSV
- [ ] DW-2.5: REPORT.md round-2 section: per-task floor table + rung aggregation, per-model fingerprint, Q2 verdict (rule 4 quoted verbatim, inputs shown), effort-crossover observation, bundle metrics, judge-failure data-quality note, task traceability
- [ ] DW-2.6: Cumulative reported cost logged and under the $250 tripwire

---
## Test Coverage
**Level:** 100%

## Test Plan
- [ ] T-1.1: 04-hash witnesses reproduce + gold recall 1:1 + no-leak grep (DW-1.1) — Integration
- [ ] T-1.2: Parent-task byte-identity check via git diff scope assertion (DW-1.2) — Unit
- [ ] T-1.3: Per-variant: gold passes hidden suite with zero off-scope edits; every witness reproduces (DW-1.3) — Integration
- [ ] T-1.4: **Dirty:** classification fixtures — all four buckets distinguishable; ambiguous edit (in-scope file, off-scope line) classified per key's location granularity (DW-1.4) — Unit
- [ ] T-1.5: No-leak grep assertions per variant (DW-1.5) — Unit
- [ ] T-2.1: Floor-mode unit tests: validity-only gate, cell generation (ladder/temptation/effort), resume-if-done, pause, tripwire (DW-2.1) — Unit
- [ ] T-2.2: Floor rule boundary: exactly 4/5 → floor, 3/5 → not floor (DW-2.2) — Unit
- [ ] T-2.3: **Dirty:** effort/pilot rows injected into floor input → excluded or raise (DW-2.2) — Unit
- [ ] T-2.4: **Dirty:** empty outputs on temptation variant → miss bucket, no crash (DW-2.2) — Unit
- [ ] T-2.5: **Dirty:** judge-failure row in behavior scoring → flagged, mention undetermined, not dropped (DW-2.2) — Unit
- [ ] T-2.6: Honesty fact-match: pinned claim types only; report claiming "tests pass" against failing artifact → mismatch recorded (DW-2.2) — Unit
- [ ] T-2.7: Sweep completeness: CSV row count = models × instances × n per sweep, task-major order in logs (DW-2.3, DW-2.4) — Integration
- [ ] T-2.8: REPORT round-2 content checks (programmatic greps): floor table rows per task, fingerprint per model, rule-4 verbatim quote, effort section, traceability (DW-2.5) — Unit
- [ ] T-2.9: Cumulative-cost line present in REPORT round-2 section, parses, and is < $250 (DW-2.6) — Unit

---
## Notes
- Skills for both phases already loaded in the planning session; build agents re-invoke via dispatch
- Temptation variant ids live under tasks/05-* (exact slugs are the build agent's choice within File scope)
- Phase 2 executes live model runs; if a rate-limit window closes mid-sweep, BLOCKED-with-resume-note is the expected path, not failure (round-1 precedent)
- Effort sweep cells use run_eval's `effort` enum directly (low|medium|high verified in schema)
- The two phases share no files (05-* content vs harness/CSV/REPORT) but are strictly ordered by the Produces seam
---
## Execution Log
_To be filled during /code-foundations:build_

### Phase 1: Round-2 task content (Gate: Standard)
- [x] BUILD: Discovery + design + implementation complete
- [x] REVIEW: Verification passed (reviewer independently re-ran witnesses, golds, no-leak greps)
- [x] Committed
Commit: 58a7d08
Summary: tasks/05-tempt-* (3 variants, 5 off-scope defects w/ witnesses, temptation-key.json per variant), fixtures/behavior/ (13 classification fixtures, all four buckets + dirty in-scope-edit case, validate.sh 27-check gate), 04-hash spec exclusion rules documented; parents byte-identical. Reviewer note for Phase 2: fixture set is 12 clean : 1 dirty -- harden classifier tests accordingly.

### Phase 2: Floor + behavior + effort sweeps, analysis, REPORT round 2 (Gate: Standard)
- [x] BUILD: harness floor-mode + behavior/bundle/effort scoring + analysis extensions; live sweep executed
- [x] REVIEW: PASS — independent opus reviewer re-derived every REPORT figure from the CSVs (floor cells, Q2 inputs, fingerprint rates, $172.56 cumulative cost), ran suite (192 passed, 3 skipped) + `validate.sh` (all checks passed); all six DW items verified, no correctness defect. Two non-blocking honesty notes folded into REPORT (honesty `0.00` = not-measured disclosure; Q2 per-defect proxy conservative-bias caveat).
- [x] Committed
Commit: recorded in grug memory (model-tier-benchmark-round2-results) and this session's summary — a commit cannot inscribe its own hash; the Phase-2 commit is the one whose message reads "Phase: R2 2/2".
Summary: run_suite floor mode (validity-only gate, LADDER_MODELS haiku→sonnet→opus→fable, effort cells, haiku-4.5 verified live); score_run behavior classification + cheap-bundle metrics; analyze floor table/fingerprint/effort-crossover + render_round2_section; 200-row ladder sweep + 72-row effort sweep executed live; 68 new tests (192 passed, 3 skipped). Live cost cumulative $172.56 (< $250 tripwire).
Data-quality follow-ups (in REPORT): 03-kv/05-tempt-kv starter contamination disclosed with downstream recommendation; honesty fact-match not computed live (descriptive-only per rule 6).
