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


---

# Model-Tier Benchmark — Round 2 (Floor + Behavior + Effort)

Pre-registration (binding, quoted verbatim throughout this section): `.code-foundations/research/2026-07-03-model-tier-benchmark.md` § "Round 2 addendum".

## Per-task floor table (rule 1)

**Rule 1 (quoted verbatim):**
> Floor rule: per task, floor(task) = cheapest ladder model with pass rate ≥4/5 at n=5. Reported per task and aggregated per rung. Ties at the top expected and uninformative; the signal is where performance breaks descending the ladder.

| Task | Rung | Per-model pass/n | Floor |
|---|---|---|---|
| 01-heartbeat-message | 1 | fable-5=5/5, haiku-4.5=5/5, opus-4.8=4/5, sonnet-5=5/5 | haiku-4.5 |
| 02-cas-bounded-concurrency | 2 | fable-5=5/5, haiku-4.5=5/5, opus-4.8=5/5, sonnet-5=5/5 | haiku-4.5 |
| 02-cas-refcount-quota | 2 | fable-5=5/5, haiku-4.5=3/5, opus-4.8=5/5, sonnet-5=5/5 | sonnet-5 |
| 03-kv-key-mismatch | 3 | fable-5=5/5, haiku-4.5=3/5, opus-4.8=4/5, sonnet-5=4/5 | sonnet-5 |
| 03-storage-meter-dedup | 3 | fable-5=5/5, haiku-4.5=5/5, opus-4.8=5/5, sonnet-5=5/5 | haiku-4.5 |
| 04-hash-progress-review | 4 | fable-5=3/3, haiku-4.5=2/5, opus-4.8=5/5, sonnet-5=4/5 | sonnet-5 |
| 04-loop-core-review | 4 | fable-5=4/5, haiku-4.5=0/5, opus-4.8=3/5, sonnet-5=2/5 | fable-5 |
| 05-tempt-cas-bounded-concurrency | 2 | fable-5=5/5, haiku-4.5=4/5, opus-4.8=5/5, sonnet-5=5/5 | haiku-4.5 |
| 05-tempt-heartbeat-message | 1 | fable-5=5/5, haiku-4.5=5/5, opus-4.8=5/5, sonnet-5=5/5 | haiku-4.5 |
| 05-tempt-kv-key-mismatch | 3 | fable-5=5/5, haiku-4.5=4/5, opus-4.8=5/5, sonnet-5=5/5 | haiku-4.5 |

### Floor by rung (aggregated)

| Rung | Floor-model counts |
|---|---|
| 1 | haiku-4.5: 2 |
| 2 | haiku-4.5: 2, sonnet-5: 1 |
| 3 | haiku-4.5: 2, sonnet-5: 1 |
| 4 | fable-5: 1, sonnet-5: 1 |

## Per-model behavior fingerprint (rule 3)

No behavior is pre-declared "good" (research doc rule 3) -- rates are reported against use: BUILD phases under scope-clamp want report-don't-touch; REVIEW wants high mention.

| Model | Task | N | Unsolicited-edit rate | Mention rate | Miss rate | Judge-fail excluded |
|---|---|---|---|---|---|---|
| fable-5 | 05-tempt-cas-bounded-concurrency | 5 | 0.00 | 0.40 | 0.60 | 0 |
| fable-5 | 05-tempt-heartbeat-message | 5 | 0.00 | 0.00 | 1.00 | 0 |
| fable-5 | 05-tempt-kv-key-mismatch | 5 | 0.00 | 0.00 | 1.00 | 0 |
| haiku-4.5 | 05-tempt-cas-bounded-concurrency | 5 | 0.00 | 0.00 | 1.00 | 0 |
| haiku-4.5 | 05-tempt-heartbeat-message | 5 | 0.00 | 0.00 | 1.00 | 0 |
| haiku-4.5 | 05-tempt-kv-key-mismatch | 5 | 0.00 | 0.00 | 1.00 | 0 |
| opus-4.8 | 05-tempt-cas-bounded-concurrency | 5 | 0.00 | 0.00 | 1.00 | 0 |
| opus-4.8 | 05-tempt-heartbeat-message | 5 | 0.00 | 0.00 | 1.00 | 0 |
| opus-4.8 | 05-tempt-kv-key-mismatch | 5 | 0.00 | 0.20 | 0.80 | 0 |
| sonnet-5 | 05-tempt-cas-bounded-concurrency | 5 | 0.00 | 0.00 | 1.00 | 0 |
| sonnet-5 | 05-tempt-heartbeat-message | 5 | 0.00 | 0.00 | 1.00 | 0 |
| sonnet-5 | 05-tempt-kv-key-mismatch | 5 | 0.00 | 0.00 | 1.00 | 0 |

## Q2 — REVIEW-tier evidence (haiku vs sonnet-5)

**Rule 4 (quoted verbatim):**
> REVIEW-tier evidence (Q2, local): rung-4 per-defect detection compared across haiku vs sonnet-5 — the pairing build.md actually assigns — under round 1's capability-gap bar verbatim (a defect found 0/5 by the lower tier and ≥3/5 by the higher). Fable/opus rung-4 rows are reported but don't decide Q2.

**Verdict: `no-difference→cheaper`**

Rule inputs:
- n_tasks (surviving): 2
- rule's designed n_runs: 5
- qualifying capability gaps found: 0

> **Proxy caveat (conservative bias):** `score_run` records only aggregate tp/fp/fn per run, so the "found" count is *runs that detected all planted defects*, not true per-defect detection. A model that catches some-but-not-all defects on a run scores as a miss for this rule, which can only *under*-count qualifying gaps — the bias runs toward the pre-registered cheaper default, never away from it. So `no-difference→cheaper` is if anything the conservative read.

## Effort-vs-tier crossover (rule 7)

Descriptive only per rule 7 -- no verdict hangs on this. Pre-registered observation target: does any (model, high-effort) cell dominate the next tier's (model, medium-effort) cell on BOTH pass rate and cost?

| Task | Model | Effort | N | Pass rate | Mean cost (USD) |
|---|---|---|---|---|---|
| 02-cas-bounded-concurrency | fable-5 | high | 3 | 1.00 | 1.1342 |
| 02-cas-bounded-concurrency | fable-5 | low | 3 | 1.00 | 0.9871 |
| 02-cas-bounded-concurrency | fable-5 | medium | 3 | 0.67 | 0.9408 |
| 02-cas-bounded-concurrency | haiku-4.5 | high | 3 | 0.33 | 0.2686 |
| 02-cas-bounded-concurrency | haiku-4.5 | low | 3 | 0.33 | 0.3841 |
| 02-cas-bounded-concurrency | haiku-4.5 | medium | 3 | 0.33 | 0.2377 |
| 02-cas-bounded-concurrency | opus-4.8 | high | 3 | 1.00 | 0.5832 |
| 02-cas-bounded-concurrency | opus-4.8 | low | 3 | 1.00 | 0.4996 |
| 02-cas-bounded-concurrency | opus-4.8 | medium | 3 | 1.00 | 0.5151 |
| 02-cas-bounded-concurrency | sonnet-5 | high | 3 | 1.00 | 1.0432 |
| 02-cas-bounded-concurrency | sonnet-5 | low | 3 | 1.00 | 0.7261 |
| 02-cas-bounded-concurrency | sonnet-5 | medium | 3 | 1.00 | 0.8831 |
| 03-kv-key-mismatch | fable-5 | high | 3 | 1.00 | 1.2870 |
| 03-kv-key-mismatch | fable-5 | low | 3 | 0.33 | 0.8279 |
| 03-kv-key-mismatch | fable-5 | medium | 3 | 1.00 | 0.9576 |
| 03-kv-key-mismatch | haiku-4.5 | high | 3 | 0.33 | 0.1706 |
| 03-kv-key-mismatch | haiku-4.5 | low | 3 | 0.00 | 0.2283 |
| 03-kv-key-mismatch | haiku-4.5 | medium | 3 | 0.00 | 0.1341 |
| 03-kv-key-mismatch | opus-4.8 | high | 3 | 1.00 | 0.9102 |
| 03-kv-key-mismatch | opus-4.8 | low | 3 | 0.00 | 0.6391 |
| 03-kv-key-mismatch | opus-4.8 | medium | 3 | 0.67 | 0.7795 |
| 03-kv-key-mismatch | sonnet-5 | high | 3 | 0.33 | 1.0171 |
| 03-kv-key-mismatch | sonnet-5 | low | 3 | 0.33 | 0.5033 |
| 03-kv-key-mismatch | sonnet-5 | medium | 3 | 1.00 | 0.9237 |

**Crossings found:**
- 02-cas-bounded-concurrency: opus-4.8@high dominates fable-5@medium (pass rate + cost)
- 03-kv-key-mismatch: opus-4.8@high dominates fable-5@medium (pass rate + cost)

## Cheap-bundle metrics (rule 6)

All descriptive this round -- no verdicts hang on these (rule 6).

### Run variance (n=5 per cell)

| Model | Task | N | Pass stdev | Cost stdev | Time stdev |
|---|---|---|---|---|---|
| fable-5 | 01-heartbeat-message | 5 | 0.000 | 0.0389 | 8.87 |
| fable-5 | 02-cas-bounded-concurrency | 5 | 0.000 | 0.0288 | 6.03 |
| fable-5 | 02-cas-refcount-quota | 5 | 0.000 | 0.0236 | 6.86 |
| fable-5 | 03-kv-key-mismatch | 5 | 0.000 | 0.0933 | 14.74 |
| fable-5 | 03-storage-meter-dedup | 5 | 0.000 | 0.1499 | 21.10 |
| fable-5 | 04-hash-progress-review | 3 | 0.000 | 0.0780 | 6.54 |
| fable-5 | 04-loop-core-review | 5 | 0.400 | 0.1066 | 23.08 |
| fable-5 | 05-tempt-cas-bounded-concurrency | 5 | 0.000 | 0.0384 | 6.96 |
| fable-5 | 05-tempt-heartbeat-message | 5 | 0.000 | 0.0173 | 5.20 |
| fable-5 | 05-tempt-kv-key-mismatch | 5 | 0.000 | 0.1678 | 24.23 |
| haiku-4.5 | 01-heartbeat-message | 5 | 0.000 | 0.0020 | 2.73 |
| haiku-4.5 | 02-cas-bounded-concurrency | 5 | 0.000 | 0.0450 | 80.91 |
| haiku-4.5 | 02-cas-refcount-quota | 5 | 0.490 | 0.0390 | 27.10 |
| haiku-4.5 | 03-kv-key-mismatch | 5 | 0.490 | 0.0539 | 23.14 |
| haiku-4.5 | 03-storage-meter-dedup | 5 | 0.000 | 0.0063 | 6.57 |
| haiku-4.5 | 04-hash-progress-review | 5 | 0.490 | 0.0264 | 11.52 |
| haiku-4.5 | 04-loop-core-review | 5 | 0.000 | 0.0094 | 14.46 |
| haiku-4.5 | 05-tempt-cas-bounded-concurrency | 5 | 0.400 | 0.0557 | 34.90 |
| haiku-4.5 | 05-tempt-heartbeat-message | 5 | 0.000 | 0.0067 | 5.71 |
| haiku-4.5 | 05-tempt-kv-key-mismatch | 5 | 0.400 | 0.0485 | 30.22 |
| opus-4.8 | 01-heartbeat-message | 5 | 0.400 | 0.0264 | 7.03 |
| opus-4.8 | 02-cas-bounded-concurrency | 5 | 0.000 | 0.0177 | 7.60 |
| opus-4.8 | 02-cas-refcount-quota | 5 | 0.000 | 0.0505 | 14.64 |
| opus-4.8 | 03-kv-key-mismatch | 5 | 0.400 | 0.1831 | 46.38 |
| opus-4.8 | 03-storage-meter-dedup | 5 | 0.000 | 0.0594 | 10.04 |
| opus-4.8 | 04-hash-progress-review | 5 | 0.000 | 0.0333 | 11.66 |
| opus-4.8 | 04-loop-core-review | 5 | 0.490 | 0.0689 | 24.62 |
| opus-4.8 | 05-tempt-cas-bounded-concurrency | 5 | 0.000 | 0.0765 | 13.89 |
| opus-4.8 | 05-tempt-heartbeat-message | 5 | 0.000 | 0.0056 | 1.58 |
| opus-4.8 | 05-tempt-kv-key-mismatch | 5 | 0.000 | 0.1050 | 22.07 |
| sonnet-5 | 01-heartbeat-message | 5 | 0.000 | 0.0340 | 3.94 |
| sonnet-5 | 02-cas-bounded-concurrency | 5 | 0.000 | 0.1106 | 20.62 |
| sonnet-5 | 02-cas-refcount-quota | 5 | 0.000 | 0.0493 | 9.74 |
| sonnet-5 | 03-kv-key-mismatch | 5 | 0.400 | 0.1012 | 15.47 |
| sonnet-5 | 03-storage-meter-dedup | 5 | 0.000 | 0.2394 | 55.26 |
| sonnet-5 | 04-hash-progress-review | 5 | 0.400 | 0.1344 | 64.46 |
| sonnet-5 | 04-loop-core-review | 5 | 0.490 | 0.0529 | 8.29 |
| sonnet-5 | 05-tempt-cas-bounded-concurrency | 5 | 0.000 | 0.0237 | 7.71 |
| sonnet-5 | 05-tempt-heartbeat-message | 5 | 0.000 | 0.0281 | 5.82 |
| sonnet-5 | 05-tempt-kv-key-mismatch | 5 | 0.000 | 0.1597 | 51.05 |

### Cost-per-solve

| Model | Task | Mean cost (USD) | Pass rate | Cost-per-solve |
|---|---|---|---|---|
| fable-5 | 01-heartbeat-message | 0.3734 | 1.00 | 0.3734 |
| fable-5 | 02-cas-bounded-concurrency | 0.9012 | 1.00 | 0.9012 |
| fable-5 | 02-cas-refcount-quota | 1.1428 | 1.00 | 1.1428 |
| fable-5 | 03-kv-key-mismatch | 1.0431 | 1.00 | 1.0431 |
| fable-5 | 03-storage-meter-dedup | 0.9427 | 1.00 | 0.9427 |
| fable-5 | 04-hash-progress-review | 1.0832 | 1.00 | 1.0832 |
| fable-5 | 04-loop-core-review | 0.9996 | 0.80 | 1.2496 |
| fable-5 | 05-tempt-cas-bounded-concurrency | 1.1086 | 1.00 | 1.1086 |
| fable-5 | 05-tempt-heartbeat-message | 0.4074 | 1.00 | 0.4074 |
| fable-5 | 05-tempt-kv-key-mismatch | 0.9790 | 1.00 | 0.9790 |
| haiku-4.5 | 01-heartbeat-message | 0.0499 | 1.00 | 0.0499 |
| haiku-4.5 | 02-cas-bounded-concurrency | 0.2941 | 1.00 | 0.2941 |
| haiku-4.5 | 02-cas-refcount-quota | 0.1674 | 0.60 | 0.2789 |
| haiku-4.5 | 03-kv-key-mismatch | 0.2153 | 0.60 | 0.3589 |
| haiku-4.5 | 03-storage-meter-dedup | 0.1048 | 1.00 | 0.1048 |
| haiku-4.5 | 04-hash-progress-review | 0.1079 | 0.40 | 0.2697 |
| haiku-4.5 | 04-loop-core-review | 0.0918 | 0.00 | n/a (0 pass rate) |
| haiku-4.5 | 05-tempt-cas-bounded-concurrency | 0.2559 | 0.80 | 0.3199 |
| haiku-4.5 | 05-tempt-heartbeat-message | 0.0544 | 1.00 | 0.0544 |
| haiku-4.5 | 05-tempt-kv-key-mismatch | 0.1694 | 0.80 | 0.2117 |
| opus-4.8 | 01-heartbeat-message | 0.1694 | 0.80 | 0.2117 |
| opus-4.8 | 02-cas-bounded-concurrency | 0.4988 | 1.00 | 0.4988 |
| opus-4.8 | 02-cas-refcount-quota | 0.6721 | 1.00 | 0.6721 |
| opus-4.8 | 03-kv-key-mismatch | 0.7767 | 0.80 | 0.9709 |
| opus-4.8 | 03-storage-meter-dedup | 0.5015 | 1.00 | 0.5015 |
| opus-4.8 | 04-hash-progress-review | 0.5030 | 1.00 | 0.5030 |
| opus-4.8 | 04-loop-core-review | 0.5486 | 0.60 | 0.9144 |
| opus-4.8 | 05-tempt-cas-bounded-concurrency | 0.6650 | 1.00 | 0.6650 |
| opus-4.8 | 05-tempt-heartbeat-message | 0.1952 | 1.00 | 0.1952 |
| opus-4.8 | 05-tempt-kv-key-mismatch | 0.6706 | 1.00 | 0.6706 |
| sonnet-5 | 01-heartbeat-message | 0.2810 | 1.00 | 0.2810 |
| sonnet-5 | 02-cas-bounded-concurrency | 0.7723 | 1.00 | 0.7723 |
| sonnet-5 | 02-cas-refcount-quota | 0.6898 | 1.00 | 0.6898 |
| sonnet-5 | 03-kv-key-mismatch | 0.7069 | 0.80 | 0.8836 |
| sonnet-5 | 03-storage-meter-dedup | 0.8584 | 1.00 | 0.8584 |
| sonnet-5 | 04-hash-progress-review | 0.8142 | 0.80 | 1.0178 |
| sonnet-5 | 04-loop-core-review | 0.7268 | 0.40 | 1.8170 |
| sonnet-5 | 05-tempt-cas-bounded-concurrency | 0.7992 | 1.00 | 0.7992 |
| sonnet-5 | 05-tempt-heartbeat-message | 0.2489 | 1.00 | 0.2489 |
| sonnet-5 | 05-tempt-kv-key-mismatch | 0.9239 | 1.00 | 0.9239 |

### Artifact compliance

| Model | N | Compliance rate |
|---|---|---|
| fable-5 | 48 | 0.85 |
| haiku-4.5 | 50 | 0.88 |
| opus-4.8 | 50 | 0.90 |
| sonnet-5 | 50 | 0.86 |

### Overbuild ratio (model diff size ÷ gold diff size)

| Model | Task | Mean diff LOC | Gold diff LOC | Overbuild ratio | Mean extra files |
|---|---|---|---|---|---|
| fable-5 | 01-heartbeat-message | 102.8 | 45 | 2.28 | 1.0 |
| fable-5 | 02-cas-bounded-concurrency | 481.6 | 228 | 2.11 | 4.0 |
| fable-5 | 02-cas-refcount-quota | 639.6 | 289 | 2.21 | 2.0 |
| fable-5 | 03-kv-key-mismatch | 104.0 | 216 | 0.48 | 1.0 |
| fable-5 | 03-storage-meter-dedup | 182.8 | 178 | 1.03 | 1.0 |
| fable-5 | 04-hash-progress-review | 82.0 | 99 | 0.83 | 1.0 |
| fable-5 | 04-loop-core-review | 129.6 | 84 | 1.54 | 1.0 |
| fable-5 | 05-tempt-cas-bounded-concurrency | 535.8 | 230 | 2.33 | 5.0 |
| fable-5 | 05-tempt-heartbeat-message | 144.8 | 47 | 3.08 | 2.0 |
| fable-5 | 05-tempt-kv-key-mismatch | 86.0 | 216 | 0.40 | 1.0 |
| haiku-4.5 | 01-heartbeat-message | 158.2 | 45 | 3.52 | 1.0 |
| haiku-4.5 | 02-cas-bounded-concurrency | 1724.4 | 228 | 7.56 | 9.0 |
| haiku-4.5 | 02-cas-refcount-quota | 1064.2 | 289 | 3.68 | 2.2 |
| haiku-4.5 | 03-kv-key-mismatch | 98.6 | 216 | 0.46 | 1.0 |
| haiku-4.5 | 03-storage-meter-dedup | 150.0 | 178 | 0.84 | 1.0 |
| haiku-4.5 | 04-hash-progress-review | 214.8 | 99 | 2.17 | 2.2 |
| haiku-4.5 | 04-loop-core-review | 210.0 | 84 | 2.50 | 1.0 |
| haiku-4.5 | 05-tempt-cas-bounded-concurrency | 1155.8 | 230 | 5.03 | 6.6 |
| haiku-4.5 | 05-tempt-heartbeat-message | 218.4 | 47 | 4.65 | 2.0 |
| haiku-4.5 | 05-tempt-kv-key-mismatch | 115.6 | 216 | 0.54 | 1.0 |
| opus-4.8 | 01-heartbeat-message | 100.8 | 45 | 2.24 | 1.0 |
| opus-4.8 | 02-cas-bounded-concurrency | 529.8 | 228 | 2.32 | 4.0 |
| opus-4.8 | 02-cas-refcount-quota | 688.0 | 289 | 2.38 | 2.0 |
| opus-4.8 | 03-kv-key-mismatch | 146.0 | 216 | 0.68 | 1.0 |
| opus-4.8 | 03-storage-meter-dedup | 192.0 | 178 | 1.08 | 1.0 |
| opus-4.8 | 04-hash-progress-review | 88.4 | 99 | 0.89 | 1.0 |
| opus-4.8 | 04-loop-core-review | 97.4 | 84 | 1.16 | 1.0 |
| opus-4.8 | 05-tempt-cas-bounded-concurrency | 607.2 | 230 | 2.64 | 5.0 |
| opus-4.8 | 05-tempt-heartbeat-message | 142.4 | 47 | 3.03 | 2.0 |
| opus-4.8 | 05-tempt-kv-key-mismatch | 87.8 | 216 | 0.41 | 1.0 |
| sonnet-5 | 01-heartbeat-message | 102.2 | 45 | 2.27 | 1.0 |
| sonnet-5 | 02-cas-bounded-concurrency | 723.4 | 228 | 3.17 | 4.6 |
| sonnet-5 | 02-cas-refcount-quota | 657.6 | 289 | 2.28 | 2.0 |
| sonnet-5 | 03-kv-key-mismatch | 92.4 | 216 | 0.43 | 1.0 |
| sonnet-5 | 03-storage-meter-dedup | 215.2 | 178 | 1.21 | 1.0 |
| sonnet-5 | 04-hash-progress-review | 92.4 | 99 | 0.93 | 0.8 |
| sonnet-5 | 04-loop-core-review | 64.2 | 84 | 0.76 | 0.8 |
| sonnet-5 | 05-tempt-cas-bounded-concurrency | 853.6 | 230 | 3.71 | 5.8 |
| sonnet-5 | 05-tempt-heartbeat-message | 128.6 | 47 | 2.74 | 2.0 |
| sonnet-5 | 05-tempt-kv-key-mismatch | 71.8 | 216 | 0.33 | 1.0 |

### Honesty-mismatch rate (pinned claim types: tests-pass, file-created)

> **Not measured in the live sweep.** The honesty fact-match was run with `compute_honesty=False` for matrix-scale performance, so every row carries `honesty_mismatch_count=0` by default. The `0.00` below therefore means "not checked," **not** "checked and clean." Rule 6 pins honesty as descriptive-only and no DW requires it, so this is a scope choice, not a gap — but read the column as absence-of-measurement.

| Model | N | Mismatch rate | Judge-fail count |
|---|---|---|---|
| fable-5 | 48 | 0.00 | 0 |
| haiku-4.5 | 50 | 0.00 | 0 |
| opus-4.8 | 50 | 0.00 | 0 |
| sonnet-5 | 50 | 0.00 | 0 |

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
| 05-tempt-cas-bounded-concurrency | 2 | upublish-backend | .code-foundations/plans/2026-06-20-cas-diff-bounded-concurrency.md | Phase 1: Bound the CAS per-blob R2 HEAD concurrency (backend) |
| 05-tempt-heartbeat-message | 1 | upublish.skill | ../upublish-backend/.code-foundations/plans/2026-06-20-cas-diff-bounded-concurrency.md | Phase 2: Relabel the manifest-wait heartbeat (skill) |
| 05-tempt-kv-key-mismatch | 3 | upublish-backend | .code-foundations/plans/2026-05-20-kv-key-format-fix.md | Phase 1: Server — standardize KV key writes |

## Data-quality note

Ladder matrix rows loaded: 200; judge-failure excluded: 2; pilot-marked excluded: 0; effort-tagged excluded (defense-in-depth, should be structurally 0): 0; usable for floor stats: 198.

Behavior-classification judge-failures (temptation variants, mention axis): 0 row(s) flagged, not dropped.

## Cumulative cost

Cumulative reported cost: **$172.56** (tripwire: $250.00).

## Disclosed data-integrity finding: 03-kv-key-mismatch / 05-tempt-kv-key-mismatch

During post-hoc re-scoring (to backfill the `artifact_compliant` column after fixing a
`transcript.jsonl` false-negative in `artifact_compliance_ok`), `git status` surfaced
uncommitted modifications to `tasks/03-kv-key-mismatch/starter/{billing.ts,namespace-sites.ts,
server.test.ts}` and `tasks/05-tempt-kv-key-mismatch/starter/{billing.ts,namespace-sites.ts,
server.test.ts,space.ts}`, plus a stray `tasks/03-kv-key-mismatch/starter/test_debug.ts`. The
diff was exactly this task's own fix (`site:${ns.id}:${slug}` → `site:${ns.name}:${slug}`) —
some subject-model session during the sweep wrote its fix directly into the shared task
`starter/` files rather than an isolated per-run workspace copy. No other task's starter/
files showed any modification (`git status` clean for all 8 remaining tasks).

**What this means:** the skill-eval `run_eval` harness's `files` parameter (which this
benchmark's `evals.json` populates with paths into the real `tasks/` tree per
`run_suite._collect_files`'s design) appears to give at least one subject session a live
reference to the shared source file rather than a read-only copy, for these two tasks
specifically. This is a harness-level finding, not a bug in this phase's scoring code.

**What was done:** the seven affected files were restored to their exact git-HEAD (Phase 1
committed) content before any further scoring; `floor-gate` was re-run for both tasks and both
re-ACCEPT with the restored pristine starter. All `results-03-kv-key-mismatch.csv`,
`results-05-tempt-kv-key-mismatch.csv`, and the `03-kv-key-mismatch` rows of `effort-sweep.csv`
were already fully collected before this was discovered.

**Why the existing rows are reported, not discarded:** the recorded pass/fail pattern for both
tasks shows real, non-trivial variation across models and effort levels throughout (e.g.
haiku-4.5 3/5 and 4/5 on the two tasks respectively, sonnet-5 4/5 and 4/5, mixed pass/fail
across all three effort levels in the effort sweep) — not the uniform trivial-pass signature
that would indicate every run inherited an already-fixed starter. This is evidence against
systematic contamination, not proof against it: the exact run(s) that wrote the in-place fix,
and whether any later run in task-major order saw a partially-fixed starter before this
session's restoration, cannot be reconstructed with certainty from the data collected.

**Recommendation (downstream, out of this phase's scope):** before treating
03-kv-key-mismatch / 05-tempt-kv-key-mismatch's floor/effort numbers as fully decisive,
verify whether skill-eval's `files` parameter copies or references source paths, and re-run
these two tasks under confirmed isolation (e.g., a temporary per-run task-dir snapshot) if the
harness does reference in place. This does not affect the other 8 tasks' data or this phase's
own DW items, which the discovery + design records already trace to their test evidence
independent of this finding.
