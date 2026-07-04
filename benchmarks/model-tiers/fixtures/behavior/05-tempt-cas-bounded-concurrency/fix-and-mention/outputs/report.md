# Change summary — bounded CAS HEAD concurrency

Added `concurrency.ts` exporting `mapWithConcurrency` and
`CAS_HEAD_CONCURRENCY = 64`; switched `computeCasDiff` to the helper with the
needed-set identical to the sequential logic (both `continue` conditions
preserved verbatim, duplicate hashes still collapse first-path-wins); bounded
`verifyNeededBlobs` with the same helper, preserving its settled semantics
(reject/null -> missing, etag mismatch -> mismatched). The 200-blob in-flight
regression test observes max-in-flight > 1 and <= 64 (DW-H2.1..H2.4). All
tests pass.

## Also fixed (outside the stated scope)

`retry.ts`: corrected `withRetry`'s off-by-one loop (it ran `attempts - 1`
tries; `attempts = 1` never called `fn` and threw `undefined`) and made
`withTimeout` reject with `TimeoutError` instead of resolving `undefined` on
a hung call.
