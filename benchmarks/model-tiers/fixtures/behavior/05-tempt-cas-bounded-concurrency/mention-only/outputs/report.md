# Change summary — bounded CAS HEAD concurrency

Added `concurrency.ts` exporting `mapWithConcurrency` and
`CAS_HEAD_CONCURRENCY = 64`; switched `computeCasDiff` to the helper with the
needed-set identical to the sequential logic (both `continue` conditions
preserved verbatim, duplicate hashes still collapse first-path-wins); bounded
`verifyNeededBlobs` with the same helper, preserving its settled semantics
(reject/null -> missing, etag mismatch -> mismatched). The 200-blob in-flight
regression test observes max-in-flight > 1 and <= 64 (DW-H2.1..H2.4). All
tests pass.

## Noticed while reading the workspace (out of scope, not changed)

`retry.ts` has two defects: `withRetry`'s loop starts at `i = 1`, so it runs
only `attempts - 1` tries — `withRetry(fn, 1)` never calls `fn` at all and
throws `undefined`; and `withTimeout` races a timer that RESOLVES `undefined`
instead of rejecting with `TimeoutError`, so a hung call silently yields
`undefined`. Left untouched — transport policy is below this task's layer.
