/**
 * Upload-progress line formatting (the phase AFTER hashing).
 *
 * Once hashing completes and the CAS diff returns, the client uploads the
 * blobs the server doesn't already have, and the progress line switches from
 * the hashing heartbeat (./heartbeat.ts) to the upload line built here.
 *
 * Seams:
 *   uploadPercent    — integer percentage of bytes uploaded, clamped to 0-100
 *   uploadStatusLine — the full "Uploading …" line the client prints
 */

/** An upload-progress snapshot (cumulative counts as of the last update). */
export interface UploadProgress {
  /** Blobs uploaded so far (cumulative). Starts at 0, ends at `needed`. */
  uploaded: number;
  /** Total blobs the server asked for (the CAS diff's `needed` count). */
  needed: number;
  /** Bytes uploaded so far (cumulative). */
  uploadedBytes: number;
  /** Total bytes across all needed blobs. */
  neededBytes: number;
}

/**
 * Integer percentage of bytes uploaded, clamped to 0-100. A publish whose
 * blobs are all already stored (nothing needed) is a complete upload — 100.
 */
export function uploadPercent(p: UploadProgress): number {
  const pct = Math.round((p.uploadedBytes / p.neededBytes) * 100);
  return Math.min(100, Math.max(0, pct));
}

/**
 * Formats bytes into a human-readable string, mirroring heartbeat.ts's
 * formatBytes thresholds (1024-based B / KB / MB).
 */
function formatUploadBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024).toFixed(1)} MB`;
}

/** Builds the upload-phase progress line the client prints between updates. */
export function uploadStatusLine(p: UploadProgress): string {
  return (
    `Uploading ${formatUploadBytes(p.uploadedBytes)} / ${formatUploadBytes(p.neededBytes)} ` +
    `(${uploadPercent(p)}%) — ${p.uploaded}/${p.needed} blobs`
  );
}
