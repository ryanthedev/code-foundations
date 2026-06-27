# Full Skill-Effect Sweep — build-time (Minimal gate, with-skill vs no-skill)

**Scope:** 13 of 19 skills measured for their effect on produced code when loaded into the
BUILD agent (Minimal gate — no REVIEW). 6 skills excluded as not code-gen-adherence-testable
(cc-debugging, clarify, code-standards, ca-architecture-boundaries, gof-design-patterns, planning).
sonnet, n=5/condition. Greenfield/modify controls reused from the adherence run; one shared
no-skill refactor control for Track B.

> **SCOPE LIMIT (important):** this measures *passive build-time loading only*. Production runs
> Standard/Full gates where the same skill ALSO drives a REVIEW that can FAIL the code and force a
> fix. That enforcement mechanism is NOT exercised here. These results say what a skill does to
> first-pass build output, NOT what it contributes to the full gated workflow.

## Results

| Skill | Task | Objective (with → no-skill) | Adherence-with | Effect |
|---|---|---|---|---|
| cc-control-flow-quality | rpn (greenfield) | fn_len 14 vs 32, cc 3.7 vs 5.8 | 0.97 | real |
| cc-routine-and-class-design | rate (greenfield) | LOC 30 vs 47 (−17) | 0.95 | real |
| cc-quality-practices | rpn | tests 20.8 vs 18.2 (+2.6) | 0.67 | weak |
| aposd-verifying-correctness | rpn | off-DW 1.00 vs 0.97 | 0.93 | weak |
| cc-defensive-programming | password | adversarial 1.00 vs 0.98 | 0.90 | weak |
| code-clarity-and-docs | rate | LOC +8 (docs), rubric flat | 0.96 | ~0 |
| aposd-designing-deep-modules | rate | LOC ~0 | 0.96 | ~0 |
| cc-pseudocode-programming | rpn | cc/fn ~0 | 0.87 | ~0 |
| aposd-simplifying-complexity | refactor | cc24→3.4 (= no-skill 3.2) | 0.85 | ~0 |
| cc-refactoring-guidance | refactor | cc24→3.0 (= no-skill) | 0.92 | ~0 |
| welc-legacy-code | refactor | cc24→3.0 (= no-skill) | 0.48 | ~0 |
| performance-optimization | refactor | cc24→3.6 (= no-skill) | 0.97 | ~0 |
| aposd-reviewing-module-design | refactor | cc24→3.2 (= no-skill) | 0.96 | ~0 |

Track B starter baseline: cc_max 24, fn_len_max 65, LOC 65. Every condition incl. no-skill
collapses it to cc ~3 / fn ~8 / LOC ~27, behavior preserved 5/5 — no separation (min-max ranges
fully overlap the control).

## Findings

1. **Only 2 of 13 skills move build output measurably**, both on greenfield tasks with headroom:
   cc-control-flow-quality (fn length halved) and cc-routine-and-class-design (−36% LOC).
2. **Refactor (Track B) is a clean wash** — baseline sonnet, told "refactor this," already
   maxes out the task (cc 24→3). No transform skill beats no-skill. There is no "worst" skill;
   the named trio (simplify/refactoring/welc) are indistinguishable from the control and from
   each other — welc actually produced the shortest functions.
3. **Loading ≠ doing.** The skills with a *distinctive procedure* scored LOW adherence to their
   own checklist even when loaded: welc-legacy-code 0.48 (no characterization-test-first / seams),
   cc-quality-practices 0.67. The build agent was only told "implement/refactor X" — nothing
   instructed it to RUN the skill's method, so it didn't. Skills whose guidance overlaps sonnet's
   defaults score high (0.9+) precisely because the model would do it anyway.
4. **LLM-judge metrics saturate** (mutation, readability, adherence ≈ 0.9 near ceiling). Objective
   static/behavioral metrics are the only reliable discriminators.

## Caveats

- n=5; only the two "real" effects survive the spread.
- Adherence-with is a single-judge LLM score per run (n=5 mean); treat ±0.05 as noise. The LOW
  values (welc 0.48, qa 0.67) are the informative ones — they flag un-executed protocols.
- Adherence DELTAS (with−without) are not reported per-skill because Track A/B share task controls
  graded against a different skill's checklist; only the original 3 (def/cf/clarity) had matched
  controls. Objective deltas are valid throughout (LOC/cc are skill-agnostic).
- Track B mutation is n/a (agents write sandbox-path-bound characterization tests); behavior
  preservation (hidden suite) and static reduction are the Track B spine.

## The build-side implication

Passively loading a skill into a build agent that is only told "implement X" does not make the
agent execute the skill's method. The skill helps only in the narrow gap where (a) the task leaves
headroom AND (b) the skill's guidance is something the model wouldn't already do by default. To get
more from skills at build time, the dispatch likely needs to ACTIVELY instruct the agent to run the
skill's protocol (not just load it) — or the skill's value is realized in REVIEW (gate enforcement),
which this Minimal-gate sweep deliberately excluded.
