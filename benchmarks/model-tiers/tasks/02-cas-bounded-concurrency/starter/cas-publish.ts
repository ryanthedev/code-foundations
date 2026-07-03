/**
 * CAS finalize helpers — verifies blob integrity for the blobs a client just
 * uploaded.
 *
 * Integrity stance: CORRECTNESS over robustness. A blob whose R2 etag ≠ its
 * claimed hash is REJECTED (no reference recorded), never substituted — wrong
 * bytes must never enter the content-addressed store.
 */
import { blobKey } from "./manifest-diff.ts";
import type { NeededBlob } from "./manifest-diff.ts";

/** Minimal R2 client surface this module needs. */
export interface R2Client {
  /**
   * HEADs an object; resolves to its etag + size, resolves to `null` if the
   * object doesn't exist, or rejects on a network/transport error.
   */
  headObject(key: string): Promise<{ etag: string; size: number } | null>;
}

/**
 * Result of verifying the blobs the client was asked to upload.
 *  - ok: true   → every needed blob exists in R2 with etag === hash. `sizes` maps
 *                 each verified hash to its R2-reported size.
 *  - ok: false  → at least one blob is missing or has a mismatched etag. `missing`
 *                 and `mismatched` name the offending PATHS. No references written.
 */
export type VerifyResult =
  | { ok: true; sizes: Map<string, number> }
  | { ok: false; missing: string[]; mismatched: string[] };

/**
 * headObjects each needed blob at `{space_id}/blobs/{hash}` and checks integrity.
 *
 * PERFORMANCE RISK: uses UNBOUNDED `Promise.allSettled` — a large finalize
 * (thousands of needed blobs) fires that many simultaneous HEADs at R2, a
 * latent throttle risk at scale (never yet exercised because the manifest
 * endpoint's own sequential bug always failed first).
 */
export async function verifyNeededBlobs(
  r2: R2Client,
  spaceId: string,
  needed: NeededBlob[],
): Promise<VerifyResult> {
  const results = await Promise.allSettled(
    needed.map((b) => r2.headObject(blobKey(spaceId, b.hash))),
  );

  const missing: string[] = [];
  const mismatched: string[] = [];
  const sizes = new Map<string, number>();

  for (let i = 0; i < needed.length; i++) {
    const blob = needed[i];
    const r = results[i];
    if (r.status === "rejected" || r.value === null) {
      missing.push(blob.path);
      continue;
    }
    if (r.value.etag !== blob.hash) {
      mismatched.push(blob.path);
      continue;
    }
    sizes.set(blob.hash, r.value.size);
  }

  if (missing.length > 0 || mismatched.length > 0) {
    return { ok: false, missing, mismatched };
  }
  return { ok: true, sizes };
}
