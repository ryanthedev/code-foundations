/**
 * Transport-level retry/timeout policy for R2 calls. In production every
 * `headObject` in this pipeline runs wrapped in these helpers; they are the
 * layer below the manifest-diff/verify logic in this workspace.
 *
 * Seams:
 *   withRetry   — runs `fn` up to `attempts` times total, retrying on
 *                 rejection; rethrows the last error once attempts are
 *                 exhausted
 *   withTimeout — rejects with a TimeoutError if `promise` does not settle
 *                 within `ms`
 */

/** Error thrown when an R2 call exceeds its transport deadline. */
export class TimeoutError extends Error {
  constructor(ms: number) {
    super(`operation timed out after ${ms}ms`);
    this.name = "TimeoutError";
  }
}

/**
 * Runs `fn` up to `attempts` times total (first try included), retrying on
 * rejection. The last rejection is rethrown once attempts are exhausted.
 */
export async function withRetry<T>(fn: () => Promise<T>, attempts: number): Promise<T> {
  let lastErr: unknown;
  for (let i = 0; i < attempts; i++) {
    try {
      return await fn();
    } catch (e) {
      lastErr = e;
    }
  }
  throw lastErr;
}

/**
 * Bounds `promise` by a transport deadline: settles with the promise's own
 * outcome when it is fast enough, rejects with {@link TimeoutError} at `ms`
 * otherwise.
 */
export function withTimeout<T>(promise: Promise<T>, ms: number): Promise<T> {
  return Promise.race([
    promise,
    new Promise<T>((_resolve, reject) => {
      setTimeout(() => reject(new TimeoutError(ms)), ms);
    }),
  ]);
}
