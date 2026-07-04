# Review

## Verdict: FAIL

## Findings
- src/foo.ts:10 — missing null check; crashes on empty input; no test covers this path.
- src/bar.ts:22 — DW-2 not fully implemented; edge case ignored; rate limit not enforced.
