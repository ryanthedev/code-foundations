# Task: bound the CAS per-blob R2 HEAD concurrency

This is a MODIFY-EXISTING task. Three files are provided in your working directory:

`manifest-diff.ts` — `computeCasDiff(clientManifest, existingHashes, headBlob)`: for each unique
hash in the client's manifest, resolves whether it's already stored (table + R2) and returns the
list of blobs the client must upload.

`cas-publish.ts` — `verifyNeededBlobs(r2, spaceId, needed)`: after upload, HEADs each needed blob in
R2 and checks its integrity (etag === hash).

`retry.ts` — the transport-level retry/timeout helpers production wraps around R2 calls.

## Bug report

A confirmed production regression: `computeCasDiff` resolves per-blob R2 HEADs SEQUENTIALLY
(`await headBlob(hash)` in a for-loop). For a large publish (e.g. 4,662 unique blobs) that is
~4,662 serial R2 HEADs ≈ 5 minutes, exceeding the request timeout — the manifest endpoint never
returns, and the publish hangs and fails. Separately, `verifyNeededBlobs` is already parallel but
UNBOUNDED (`Promise.allSettled` over every needed blob at once) — a latent R2-throttle risk at
scale that has never yet been exercised (the manifest endpoint's bug always failed first).

## Done-When items

- DW-H2.1: Add a new module `concurrency.ts` exporting `mapWithConcurrency<T, R>(items, limit,
  fn): Promise<R[]>` and `CAS_HEAD_CONCURRENCY = 64`. The helper is order-preserving (`results[i]`
  corresponds to `items[i]` regardless of completion order), never runs more than `limit` calls of
  `fn` concurrently, handles empty `items` (resolves to `[]`, never calls `fn`), and handles `limit
  >= items.length` (workers cap at `items.length`, no idle workers). It does not catch — a
  rejecting `fn` rejects the whole call.
- DW-H2.2: `computeCasDiff` uses the helper at `CAS_HEAD_CONCURRENCY`. The resulting `needed` set
  must be IDENTICAL to the prior sequential logic for the same inputs — the two `continue`
  conditions (`inTable && inR2` and `!inTable && inR2`) preserved verbatim, `existingHashes` still
  consulted, duplicate-hash paths still collapse to one needed entry (first path wins).
- DW-H2.3: `verifyNeededBlobs` uses the helper at `CAS_HEAD_CONCURRENCY`, preserving its settled
  semantics: a rejecting OR null-resolving `headObject` call → that blob is "missing" (collected in
  `missing`, not thrown); an etag mismatch → "mismatched"; otherwise its R2 size is recorded.
- DW-H2.4: A HEAD function that records concurrent in-flight count (increment on entry, decrement
  after an artificial delay) must show, for a many-blob input (e.g. 200 blobs) run through
  `computeCasDiff`, a max-in-flight strictly greater than 1 and less than or equal to 64 — this is
  the regression test that would fail on the old serial loop (where max-in-flight is always 1).

## Output paths

- Implementation: `outputs/concurrency.ts` (new), `outputs/manifest-diff.ts`,
  `outputs/cas-publish.ts` (both modified)
- Tests: `outputs/concurrency.test.ts`, `outputs/manifest-diff.test.ts`, `outputs/cas-publish.test.ts`
- Report: `outputs/report.md` — a brief summary of what you changed and why

Run your tests and make sure they pass before finishing.
