# Concise-Code Doctrine Benchmark — Results Report

**Arms:** baseline, concise  |  **Models:** sonnet  |  **N per cell:** 1  |  **Tasks:** 1

> **Caveats:** Small N (reported honestly). Results at this sample size may not
> generalise; the report states medians and caveats rather than overclaiming.
> Mutation score may saturate at 1.0 for well-specified tasks, limiting
> upper-end discrimination. Rubric score is an LLM judgment and carries
> additional variance; objective static + mutation metrics are the spine.

## Run Accounting

| arm | model | N | ok | partial | unscorable | all-partial-flag |
|-----|-------|---|----|---------|-----------:|-----------------|
| baseline | sonnet | 1 | 1 | 0 | 0 |  |
| concise | sonnet | 1 | 1 | 0 | 0 |  |

## Medians per Arm × Model

| arm | model | loc | cc_avg | cc_max | fn_len_max | n_funcs | mutation | hidden_dw | hidden_offdw | rubric_score |
|---|---|---|---|---|---|---|---|---|---|---|
| baseline | sonnet | 19.0000 | 4.0000 | 4.0000 | 13.0000 | 1.0000 | 1.0000 | — | — | — |
| concise | sonnet | 19.0000 | 4.0000 | 4.0000 | 14.0000 | 1.0000 | 1.0000 | — | — | — |

## Arm Deltas (concise − baseline)

> Negative = concise is lower (better for quality metrics).
> Positive = concise is higher.

| model | loc | cc_avg | cc_max | fn_len_max | n_funcs | mutation | hidden_dw | hidden_offdw | rubric_score |
|---|---|---|---|---|---|---|---|---|---|
| sonnet | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.0000 | — | — | — |

## Guardrail: Correctness + Mutation Non-Regression

**Status: PASS**

Noise threshold: 0.05 (5 percentage points).
Result: no regression beyond noise (threshold=0.05)

## Verdict

Pre-registered rule: GO iff concise arm shows quality improvement (lower LOC/
complexity at equal-or-better readability via rubric) AND correctness + mutation
do NOT regress beyond noise (threshold=0.05).

**NO-GO** — no quality improvement detected: concise arm shows no reduction in LOC/complexity metrics (('loc', 'cc_avg', 'cc_max', 'fn_len_max')) across any model.

VERDICT: NO-GO — no quality improvement detected: concise arm shows no reduction in LOC/complexity metrics (('loc', 'cc_avg', 'cc_max', 'fn_len_max')) across any model.
