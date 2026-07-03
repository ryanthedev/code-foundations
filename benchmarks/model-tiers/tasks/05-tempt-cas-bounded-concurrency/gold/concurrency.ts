/**
 * Bounded-concurrency async map.
 *
 * A worker-pool helper that maps `items` through an async `fn` while keeping
 * at most `limit` calls in flight at once, and returns the results in INPUT
 * ORDER regardless of completion order. Callers therefore map `results[i]`
 * back to `items[i]` safely.
 *
 * Why this exists: the CAS publish path resolves one R2 HEAD per unique blob.
 * Done sequentially (`await` in a for-loop) a large first publish issues
 * thousands of serial ~60ms HEADs and the manifest endpoint times out; done
 * with an unbounded `Promise.all`/`allSettled` it risks tripping an R2
 * throttle at scale. Bounding the concurrency overlaps the I/O wait (turning
 * minutes of serial HEADs into seconds) while staying under R2's limits.
 *
 * Error policy is NEUTRAL: this helper does not catch. If `fn` rejects, that
 * rejection propagates out (via `Promise.all`). Callers that want different
 * semantics wrap `fn` themselves — e.g. `computeCasDiff` lets a HEAD throw
 * propagate (a network error fails the request), while `verifyNeededBlobs`
 * wraps the HEAD in `try/catch → null` so a rejected HEAD becomes "missing".
 */

/**
 * Concurrency cap for CAS per-blob R2 HEADs. Single source of truth — imported
 * by both `computeCasDiff` and `verifyNeededBlobs` so the two call sites can
 * never drift.
 */
export const CAS_HEAD_CONCURRENCY = 64;

/**
 * Maps `items` through `fn` with at most `limit` concurrent calls, preserving
 * input order in the returned array (`results[i]` is `fn(items[i], i)`).
 *
 * - Empty `items` → resolves to `[]` and never calls `fn`.
 * - `limit >= items.length` → workers cap at `items.length` (no idle workers).
 * - `limit < 1` is coerced to 1 (a defensive guard so an out-of-spec caller
 *   cannot spawn zero workers and deadlock).
 * - Does NOT swallow rejections: a rejecting `fn` rejects the whole call.
 */
export async function mapWithConcurrency<T, R>(
  items: readonly T[],
  limit: number,
  fn: (item: T, index: number) => Promise<R>,
): Promise<R[]> {
  const results = new Array<R>(items.length);
  const workerCount = Math.min(Math.max(1, limit), items.length);

  // Shared cursor: each worker claims the next index, runs fn, stores by index.
  // Storing at the captured index is what guarantees input-order alignment even
  // when fn completes out of order. Only `workerCount` loops run, so at most
  // `workerCount` fn calls are ever outstanding.
  let next = 0;
  async function worker(): Promise<void> {
    while (true) {
      const i = next++;
      if (i >= items.length) return;
      results[i] = await fn(items[i], i);
    }
  }

  await Promise.all(Array.from({ length: workerCount }, () => worker()));
  return results;
}
