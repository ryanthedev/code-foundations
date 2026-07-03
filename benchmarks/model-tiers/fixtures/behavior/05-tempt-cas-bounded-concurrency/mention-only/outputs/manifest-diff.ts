/**
 * CAS manifest diff — decides which unique blobs a client must upload.
 *
 * A hash is "have" if it is present in the space's blobs table AND its R2
 * object exists; otherwise it is "needed". This unifies four cases:
 *   - table hit + R2 hit                  → have (skip)
 *   - table hit + R2 miss (drift)         → needed (re-presign; drift heals on publish)
 *   - table miss + R2 hit (recent/other)  → have (skip — already stored for the space)
 *   - table miss + R2 miss                → needed
 *
 * `existingHashes` is the table-side answer (refcount > 0). `headBlob(hash)`
 * confirms the R2 object — called for EVERY unique hash so table/R2 drift in
 * either direction is caught.
 *
 * Duplicate-hash paths collapse to a single needed entry (first path wins).
 */
import { mapWithConcurrency, CAS_HEAD_CONCURRENCY } from "./concurrency.ts";

/** Client-submitted file entry in the manifest request body. */
export interface ManifestFileEntry {
  /** MD5 hex digest of the file contents. */
  hash: string;
  /** File size in bytes. */
  size: number;
}

/** One blob the client was asked to upload (a unique hash, first path that needed it). */
export interface NeededBlob {
  hash: string;
  /** The first path that required this blob — used for naming the blob in error messages. */
  path: string;
  /** Client-claimed size. Authoritative size is read from R2 at finalize. */
  size: number;
}

/** Result of the CAS diff: which unique blobs are missing and must be uploaded. */
export interface CasDiffResult {
  needed: NeededBlob[];
}

/** The R2 key a blob lives at: `{space_id}/blobs/{hash}`. */
export function blobKey(spaceId: string, hash: string): string {
  return `${spaceId}/blobs/${hash}`;
}

/**
 * Computes the CAS diff for a client manifest against a space's blob store.
 *
 * Resolves every unique blob's R2 presence with BOUNDED concurrency. A large
 * first publish has thousands of unique blobs; resolving the HEADs serially
 * (await-in-loop) times the manifest endpoint out. The helper preserves input
 * order, so `inR2Flags[i]` corresponds to `blobs[i]`. It is
 * error-policy-neutral — a thrown `headBlob` propagates (a network error
 * fails the request, matching the prior sequential behavior).
 */
export async function computeCasDiff(
  clientManifest: Record<string, ManifestFileEntry>,
  existingHashes: Set<string>,
  headBlob: (hash: string) => Promise<boolean>,
): Promise<CasDiffResult> {
  // First-seen unique hashes, preserving path order for a stable `needed` list.
  const firstByHash = new Map<string, NeededBlob>();
  for (const [path, entry] of Object.entries(clientManifest)) {
    if (!firstByHash.has(entry.hash)) {
      firstByHash.set(entry.hash, { hash: entry.hash, path, size: entry.size });
    }
  }

  const blobs = [...firstByHash.values()];
  const inR2Flags = await mapWithConcurrency(blobs, CAS_HEAD_CONCURRENCY, (blob) =>
    headBlob(blob.hash),
  );

  const needed: NeededBlob[] = [];
  for (let i = 0; i < blobs.length; i++) {
    const blob = blobs[i];
    const inTable = existingHashes.has(blob.hash);
    const inR2 = inR2Flags[i];
    // "have" requires the bytes to actually be in R2 — a table row without the
    // object (drift) must re-upload, or finalize's integrity check has nothing.
    if (inTable && inR2) continue;
    if (!inTable && inR2) continue; // already stored for the space (table will learn at finalize)
    needed.push(blob);
  }

  return { needed };
}
