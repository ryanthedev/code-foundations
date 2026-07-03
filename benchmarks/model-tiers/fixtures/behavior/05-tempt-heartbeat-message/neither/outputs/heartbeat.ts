/**
 * Publish-progress heartbeat message formatting (upublish.skill's MCP heartbeat,
 * extracted as a pure function for testability).
 *
 * During a publish, the skill hashes local files then uploads the ones the
 * server doesn't already have. A 15s heartbeat re-emits the last known progress
 * so a slow client doesn't look hung. `heartbeatMessage` decides what that
 * re-emitted line says, given the last hashing snapshot. Once the upload phase
 * actually starts, the client switches to the upload line built by
 * ./upload-progress.ts.
 */

/** A hashing-progress snapshot (cumulative counts as of the last update). */
export interface HashProgress {
  /** Files hashed so far (cumulative). Starts at 0, ends at `total`. */
  completed: number;
  /** Total files to hash. */
  total: number;
  /** Bytes hashed so far (cumulative). */
  completedBytes: number;
  /** Total bytes to hash. */
  totalBytes: number;
}

/** Formats bytes into a human-readable string (B / KB / MB / GB). */
export function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`;
}

/**
 * Builds the heartbeat re-emit message for a post-hashing-snapshot stall.
 *
 * Once hashing has actually finished (`completed === total`), the client has
 * moved on to preparing the upload — the heartbeat says so instead of
 * re-emitting a hashing percentage that stopped changing minutes ago.
 */
export function heartbeatMessage(progress: HashProgress): string {
  const hashDone = progress.completed === progress.total;
  if (hashDone) return "preparing upload…";
  return (
    `Hashing ${formatBytes(progress.completedBytes)} / ${formatBytes(progress.totalBytes)} ` +
    `(${progress.completed}/${progress.total} files) — still hashing…`
  );
}
