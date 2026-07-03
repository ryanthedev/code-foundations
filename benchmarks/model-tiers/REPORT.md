# Model-Tier Benchmark — Analysis Report (Phase 5)

**Data reality:** the calibration gate (Phase 4) rejected all 7 candidate tasks before the matrix ran (5 for both-perfect/both-fail saturation, 2 for a residual spec gap looping back to earlier phases). No `results-*.csv` exists. The verdicts below are computed against that empty matrix first, per the pre-registered edge rule; a clearly separate section below reports what the calibration pilots actually measured.

## Q1 — Fable 5 vs Opus 4.8 horizon split

**Rule 1 (quoted verbatim):**
> Ties go to the cheaper model. Paired per-task gap within the bootstrap CI → verdict is “no difference,” cheap option wins explicitly.

**Rule 2 (quoted verbatim):**
> Rule changes need a consistent win, not a mean win: the costlier model must win the paired comparison on a majority of the rung's tasks AND by more than the CI on the rung aggregate.

**Verdict: `insufficient-data`**

Rule inputs:
- n_tasks (surviving): 0
- reason: 0 surviving task(s) < required minimum 2

## Q2 — REVIEW one tier below BUILD

**Rule 3 (quoted verbatim):**
> Asymmetric bar for the REVIEW rule: overturning “one tier below” (a permanent cost increase on every build) requires the higher-tier reviewer to catch planted violations the lower tier missed entirely — operationalized at n=5 as: a violation the lower tier found in 0 of 5 runs that the higher tier found in ≥3 of 5. A capability gap in missed-defect counts, not a rubric-score gap.

**Verdict: `insufficient-data`**

Rule inputs:
- n_tasks (surviving): 1
- reason: 1 surviving rung-4 task(s) < required minimum 2; rule 3 is pinned at n=5 runs per model -- actual runs observed fall short of that design
- rule's designed n_runs: 5

## Calibration-level evidence (not matrix data)

9 sonnet-5/fable-5 paired pilot comparisons (18 individual pilot runs) across the 6 tasks that reached piloting, at effort=medium, n=2 per task where a confirmation round ran. Every comparison tied at perfect correctness (including 5/5 and 5/5 planted-defect recall on the two rung-4 pilots recorded in `calibration/pilot_rows.json`). This count is computed directly from that file's contents (grouped by task + run_n, both models present); the phase context's rounded figure of ~12 apparently also counts pre-bugfix pilot rounds for `03-kv-key-mismatch`/`03-storage-meter-dedup` that were superseded and overwritten in the final JSON snapshot (see `calibration/decisions.md`'s [SCORER_BUG_FOUND] entry).

**Scope limits:** pilot n is 1-2 per model per task (never the rule's designed n=5); only the cheapest (sonnet-5) and priciest (fable-5) matrix arms were ever piloted — Opus 4.8 was never piloted, so Q1's actual pair (Fable vs Opus) has zero direct evidence, pilot or matrix; effort was pinned at medium throughout (no sweep).

**Implication under rule 1 (ties → cheaper), at the task-population level only:** for the corpus-sourced tasks as authored, sonnet-5 and fable-5 are indistinguishable — every surviving-quality task tied at perfect. This does not answer Q1 (no Opus data) or Q2 (n=2 << designed n=5) as pre-registered; it is a related but distinct signal: the task population as currently authored does not reach the difficulty band where tiers separate, which is why the matrix itself is empty.

**Follow-up register:** (1) `04-hash-progress-review` has a residual spec gap (DW-2.2's default `.upublishignore` exclusion rules are still undefined) — loops back to Phase 2 a second time per `calibration/decisions.md`'s final `[re_vet]` entry. (2) A harder-task round two (rungs 2-4 rewritten to reach the tier-separation band the research doc's own web survey identified) is the path to a decisive Q1/Q2 verdict; this round's saturation is itself informative evidence that the current corpus sample sits below that band.

## Rung-4 per-defect detection table (Q2 evidence)

| Task | Defect | Model | Found-count | Of N runs | Source |
|---|---|---|---|---|---|
| 04-hash-progress-review | HP-1-missing-opening-zero-report | gold-reference | 1 | 1 | gold-validation (decisions.md 2026-07-03T11:20:24Z; never model-piloted, vet-rejected) |
| 04-hash-progress-review | HP-2-microtask-yield | gold-reference | 1 | 1 | gold-validation (decisions.md 2026-07-03T11:20:24Z; never model-piloted, vet-rejected) |
| 04-hash-progress-review | HP-3-stat-bytes-reported | gold-reference | 1 | 1 | gold-validation (decisions.md 2026-07-03T11:20:24Z; never model-piloted, vet-rejected) |
| 04-hash-progress-review | HP-4-dir-pattern-dropped | gold-reference | 1 | 1 | gold-validation (decisions.md 2026-07-03T11:20:24Z; never model-piloted, vet-rejected) |
| 04-loop-core-review | LC-1-conditional-default-cap | fable-5 | 2 | 2 | pilot |
| 04-loop-core-review | LC-2-usage-fold-drops-input-tokens | fable-5 | 2 | 2 | pilot |
| 04-loop-core-review | LC-3-unconfigured-predicate-trips | fable-5 | 2 | 2 | pilot |
| 04-loop-core-review | LC-4-infra-import-in-core | fable-5 | 2 | 2 | pilot |
| 04-loop-core-review | LC-5-any-in-run-event | fable-5 | 2 | 2 | pilot |
| 04-loop-core-review | LC-1-conditional-default-cap | sonnet-5 | 2 | 2 | pilot |
| 04-loop-core-review | LC-2-usage-fold-drops-input-tokens | sonnet-5 | 2 | 2 | pilot |
| 04-loop-core-review | LC-3-unconfigured-predicate-trips | sonnet-5 | 2 | 2 | pilot |
| 04-loop-core-review | LC-4-infra-import-in-core | sonnet-5 | 2 | 2 | pilot |
| 04-loop-core-review | LC-5-any-in-run-event | sonnet-5 | 2 | 2 | pilot |

## Speed (secondary axis)

Speed is reported as median + range only, and is never decisive except where a gap exceeds ~2x (research doc's speed-axis protocol) — no verdict above cites a speed figure.

No matrix speed data (0 runs).

## Task → corpus-phase traceability

| Task | Rung | Repo | Plan | Phase |
|---|---|---|---|---|
| 01-heartbeat-message | 1 | upublish.skill | ../upublish-backend/.code-foundations/plans/2026-06-20-cas-diff-bounded-concurrency.md | Phase 2: Relabel the manifest-wait heartbeat (skill) |
| 02-cas-bounded-concurrency | 2 | upublish-backend | .code-foundations/plans/2026-06-20-cas-diff-bounded-concurrency.md | Phase 1: Bound the CAS per-blob R2 HEAD concurrency (backend) |
| 02-cas-refcount-quota | 2 | upublish-backend | .code-foundations/plans/2026-06-03-cas-dedup-resume.md | Phase 1: Foundation — schema, refcounts, hybrid quota |
| 03-kv-key-mismatch | 3 | upublish-backend | .code-foundations/plans/2026-05-20-kv-key-format-fix.md | Phase 1: Server — standardize KV key writes |
| 03-storage-meter-dedup | 3 | upublish-backend | ../upublish/.code-foundations/plans/2026-06-22-storage-meter-dedup-fix.md | Phase 1: Backend — dedup-aware storage reporting |
| 04-hash-progress-review | 4 | upublish.skill | .code-foundations/plans/2026-06-20-cross-client-publish-progress-timeouts.md | Phase 2: Hashing instrumentation (lib core) |
| 04-loop-core-review | 4 | meeseeks | .code-foundations/plans/2026-06-28-meeseeks-cron-loop-manager.md | Phase 1: Core domain + ports |

## Data-quality note

Matrix rows loaded: 0; judge-failure excluded: 0; pilot-marked excluded: 0; usable for paired stats: 0.
