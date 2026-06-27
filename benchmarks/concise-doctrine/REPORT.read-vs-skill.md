# Read vs Skill-load — Checklist-Delivery A/B (quick slice)

**Question:** when the build agent is given the *same* checklist content, does delivering it
via the **Skill tool** (`Skill(code-foundations:<name>)`, self-loads checklists — current main)
produce different code than delivering it via **`Read()`** of the same `SKILL.md` + `checklists.md`?

**Design:** arms differ ONLY in the build-agent's (+ review-agent's) "Load Phase Skills" section.
Identical dispatch, identical content (SKILL.md + checklists.md for cc-defensive-programming,
cc-routine-and-class-design, code-clarity-and-docs). **Minimal gate** (build agent only, no REVIEW)
to isolate first-pass code production. sonnet, 3 tasks × 3 runs/arm = 18 runs, all `ok`.

## Results (means, n=3/arm/task)

| Metric | read | skill | Δ (skill−read) | read |
|---|---|---|---|---|
| Correctness — hidden DW | 100% | 100% | 0 | **wash** |
| Rubric (readability 0–1) | 0.91 | 0.92 | +0.01 | **wash** |
| LOC | 49.1 | 52.3 | +3.2 | read slightly leaner |
| fn_len_max | 16.8 | 21.3 | +4.6 | read shorter fns |
| cc_avg / cc_max | 4.0 | 4.1 | +0.1 | **wash** |
| mutation | mostly n/a | mostly n/a | — | unusable (see caveat) |

Per task, the LOC/fn-length lean toward `read` is **driven almost entirely by 02-rpn**
(read 48 vs skill 60 LOC; read fn 35 vs skill 45). On 04-password it's near-equal; on
05-rate-limiter it's a wash/reversed (read 84 vs skill 78 LOC). It is not a consistent effect.

## Verdict

**Wash — no meaningful code-quality difference between Read and Skill-tool delivery.**
Correctness and readability are identical; the only whisper of a difference (read slightly more
concise) is one-task-driven and well within noise at n=3. The reassuring read for the project:
**the recent Read→Skill-load migration did not cost code quality.** This slice rules out a *large*
effect; it cannot detect a small one.

> NOTE: the auto-generated `results-read-vs-skill/REPORT.md` is the concise-doctrine template;
> its baseline/concise "NO-GO" verdict does not apply to the read/skill arms and should be ignored.

## Caveats (honest)

1. **Low power:** n=3/arm/task (9/arm). Exploratory only.
2. **Mutation unusable this slice:** 10/18 runs scored `n/a (suite not green)` — a *scorer*
   artifact, not broken code. Agents wrote `from outputs.<mod> import ...`; the offline mutation
   harness runs pytest from inside `outputs/`, where that import fails. Hits both arms equally
   (5 read / 5 skill). Correctness (hidden suite, imported correctly) is 100% everywhere. Where
   mutation *was* scored it was 1.0 (saturated, non-discriminating).
3. **Static unreliable for the class task:** radon reported 0 functions / cc 0 for the
   class-based 05-rate-limiter (counts module-level `def` only). LOC is still valid there.
4. **Identical content by design:** this tests the *delivery mechanism*, not the old real-world
   before/after (which also changed the dispatch text). A large mechanism effect is ruled out.

## To strengthen (if pursued)

- Fix the mutation harness cwd/import (run pytest from the parent of `outputs/`, or rewrite the
  agent test import) → recovers the mutation metric.
- Scale: both models × more tasks × n≥5; add tasks where checklist application is load-bearing
  (security/validation-heavy) so the rubric can actually discriminate adherence.
- Add a rubric dimension that explicitly scores "did the code reflect the delivered checklist."
