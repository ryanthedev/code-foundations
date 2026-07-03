# Review: verify this implementation against its requirements

Independently verify the implementation in the files below against the
requirements below. You did not write this code and have no information
about how or why it was written. Do NOT assume it is correct or complete.
Assume requirements may be unmet and bugs may be present; verify each item
from scratch against the actual code and executed test results. Do NOT
introduce requirements that are not listed here.

FIRST ACTION: run the test suite (command under "How to run the suite") via
Bash and capture its output BEFORE reading any source file. A passing suite is
evidence, not a verdict — requirements may be unmet in ways the suite never
exercises.

## Requirements to verify (Done-When items)

For EACH item, fill the template. A PASS verdict REQUIRES execution evidence
(a passing test you ran, or observed behavior from code you executed) — not
"implemented". Do NOT skip items.

- DW-1.1: All domain types + port interfaces are strict-clean with no `any`
  anywhere under `src/core/`.
  PREMISE: ___  EVIDENCE (file:line): ___  TRACE (input→output): ___  VERDICT: ___
- DW-1.2: `resolveStop` returns the correct first-to-trip reason for each
  single condition AND a deterministic precedence when ≥2 trip together.
  PREMISE: ___  EVIDENCE (file:line): ___  TRACE (input→output): ___  VERDICT: ___
- DW-1.3: A `StopCondition` with no explicit limit resolves to a default
  max-iteration cap (never unbounded).
  PREMISE: ___  EVIDENCE (file:line): ___  TRACE (input→output): ___  VERDICT: ___
- DW-1.4: Boundary-violation greps find no infra imports under `src/core/`.
  PREMISE: ___  EVIDENCE (file:line): ___  TRACE (input→output): ___  VERDICT: ___

## Edge cases — verify handling

These are explicit requirements with the same verdict standing as the DW items
above: an unhandled case listed here is a FAIL, not a Note. Verify the
implementation handles each.

- All three stop conditions tripping in the same iteration (the resulting
  reason must follow the defined precedence/ordering).
- Zero-iteration job (`maxIterations: 0`).
- Loop disabled (one-shot): a fresh state with default config must not
  spuriously stop.
- Empty/invalid `StopCondition` (no condition set → must default to a safe
  cap, not infinite).
- Cumulative token accounting: `tokensUsed` is the input + output total across
  usage events, and the budget comparison uses it.
- A stop condition that is NOT configured must never be the reported stop
  reason.

## Files to review

- src/core/types.ts
- src/core/ports.ts
- src/core/loop.ts
- test/core/loop.test.ts
- test/core/boundaries.test.ts

## How to run the suite

```
bun test
```

Run it directly via Bash and capture the output.

## Output

Write your review to `outputs/report.md`. It MUST contain:

1. The captured suite output (pass/fail counts).
2. The filled PREMISE/EVIDENCE/TRACE/VERDICT template for every DW item.
3. An `## Issues` section: one entry per defect found — exact location
   (file:line), what is wrong, and why it violates a requirement above. Write
   "none" if you found none.
4. A final line: `OVERALL: PASS` or `OVERALL: FAIL`.
