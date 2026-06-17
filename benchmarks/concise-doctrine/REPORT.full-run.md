# Concise-Code Doctrine Benchmark — Results Report

**Arms:** baseline, concise  |  **Models:** sonnet, opus  |  **N per cell:** 5  |  **Tasks:** 6

> **Caveats:** Small N (reported honestly). Results at this sample size may not
> generalise; the report states medians and caveats rather than overclaiming.
> Mutation score may saturate at 1.0 for well-specified tasks, limiting
> upper-end discrimination. Rubric score is an LLM judgment and carries
> additional variance; objective static + mutation metrics are the spine.

## Run Accounting

| arm | model | N | ok | partial | unscorable | all-partial-flag |
|-----|-------|---|----|---------|-----------:|-----------------|
| baseline | sonnet | 30 | 30 | 0 | 0 |  |
| baseline | opus | 30 | 30 | 0 | 0 |  |
| concise | sonnet | 30 | 30 | 0 | 0 |  |
| concise | opus | 30 | 29 | 0 | 1 |  |

## Medians per Arm × Model

| arm | model | loc | cc_avg | cc_max | fn_len_max | n_funcs | mutation | hidden_dw | hidden_offdw | rubric_score |
|---|---|---|---|---|---|---|---|---|---|---|
| baseline | sonnet | 27.0000 | 5.0000 | 5.0000 | 15.0000 | 1.0000 | 1.0000 | — | — | 0.9200 |
| baseline | opus | 32.0000 | 5.0000 | 5.0000 | 15.5000 | 1.0000 | 1.0000 | — | — | 0.9200 |
| concise | sonnet | 19.0000 | 5.0000 | 5.0000 | 9.0000 | 1.0000 | 1.0000 | — | — | 0.9250 |
| concise | opus | 22.0000 | 4.0000 | 4.0000 | 15.0000 | 1.0000 | 1.0000 | — | — | 0.9200 |

## Arm Deltas (concise − baseline)

> Negative = concise is lower (better for quality metrics).
> Positive = concise is higher.

| model | loc | cc_avg | cc_max | fn_len_max | n_funcs | mutation | hidden_dw | hidden_offdw | rubric_score |
|---|---|---|---|---|---|---|---|---|---|
| sonnet | -8.0000 | 0.0000 | 0.0000 | -6.0000 | 0.0000 | 0.0000 | — | — | 0.0050 |
| opus | -10.0000 | -1.0000 | -1.0000 | -0.5000 | 0.0000 | 0.0000 | — | — | 0.0000 |

## Guardrail: Correctness + Mutation Non-Regression

**Status: PASS**

Noise threshold: 0.05 (5 percentage points).
Result: no regression beyond noise (threshold=0.05)

## Verdict

Pre-registered rule: GO iff concise arm shows quality improvement (lower LOC/
complexity at equal-or-better readability via rubric) AND correctness + mutation
do NOT regress beyond noise (threshold=0.05).

**GO** — quality improved (reduced LOC/complexity: sonnet/loc: -8.0000, sonnet/fn_len_max: -6.0000, opus/loc: -10.0000 and 3 more) with no correctness or mutation regression and equal-or-better readability.

VERDICT: GO — quality improved (reduced LOC/complexity: sonnet/loc: -8.0000, sonnet/fn_len_max: -6.0000, opus/loc: -10.0000 and 3 more) with no correctness or mutation regression and equal-or-better readability.
