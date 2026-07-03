/**
 * Storage query functions for a space — legacy quota plus the CAS foundation:
 * transactional refcount mutations and the hybrid unique-bytes quota.
 *
 * All refcount mutations for one version operation run in a single SQLite
 * transaction (db.transaction). These functions trust their callers — hash
 * validation is the API barricade's job, not this layer's (out of scope here).
 */
import type { Database } from "bun:sqlite";

/** Sum of a space's storage: live site bytes + archived version bytes, no dedup. */
export function sumStorageForSpace(db: Database, spaceId: string): number {
  const row = db
    .query<{ total: number }, [string, string]>(
      `SELECT COALESCE(SUM(s.total_size), 0)
            + COALESCE((
                SELECT SUM(sv.total_size)
                FROM site_versions sv
                JOIN sites s2 ON s2.id = sv.site_id
                WHERE s2.space_id = ? AND sv.status = 'archived'
              ), 0) AS total
       FROM sites s
       WHERE s.space_id = ?`,
    )
    .get(spaceId, spaceId);
  return row?.total ?? 0;
}

/** One file entry passed to referenceBlobs: a path and its blob hash + size. */
export interface VersionFileRef {
  path: string;
  hash: string;
  size: number;
}

/**
 * Records a CAS version's blob references in a single transaction:
 *   - For each UNIQUE hash in `files`, upserts a `blobs` row with refcount += 1.
 *     The refcount counts referencing VERSIONS, so a hash appearing under several
 *     paths in THIS version bumps the refcount by exactly 1.
 *   - `created_at` is PRESERVED on conflict: a refcount-0 row being re-referenced
 *     keeps its original age, and a re-reference never double-inserts.
 *   - Inserts one `version_files` row per path.
 *
 * A failure mid-operation (e.g. a version_files PK collision) rolls the whole
 * transaction back — no partial blobs rows or refcount changes survive.
 * No-op when `files` is empty.
 */
export function referenceBlobs(
  db: Database,
  spaceId: string,
  versionId: string,
  files: VersionFileRef[],
): void {
  if (files.length === 0) return;
  const now = new Date().toISOString();

  db.transaction(() => {
    // Dedup by hash → refcount bumps once per unique hash (per version, not per path).
    const byHash = new Map<string, { hash: string; size: number }>();
    for (const f of files) {
      if (!byHash.has(f.hash)) byHash.set(f.hash, { hash: f.hash, size: f.size });
    }
    for (const { hash, size } of byHash.values()) {
      // INSERT new blob at refcount 1, or bump an existing row's refcount.
      // created_at is NOT in the UPDATE set → preserved on conflict.
      db.run(
        `INSERT INTO blobs (space_id, hash, size, refcount, created_at)
         VALUES (?, ?, ?, 1, ?)
         ON CONFLICT(space_id, hash) DO UPDATE SET refcount = refcount + 1`,
        [spaceId, hash, size, now],
      );
    }
    // One version_files row per path. A PK collision (version_id, path) throws,
    // rolling the transaction back.
    for (const f of files) {
      db.run(
        `INSERT INTO version_files (version_id, path, hash, size) VALUES (?, ?, ?, ?)`,
        [versionId, f.path, f.hash, f.size],
      );
    }
  })();
}

/**
 * Releases a CAS version's blob references in a single transaction:
 *   - Decrements refcount by 1 for each UNIQUE hash the version references
 *     (guarded: never below 0).
 *   - Deletes the version's version_files rows.
 *   - Returns the hashes (with sizes) whose refcount reached 0 — GC candidates.
 *     Returns `[]` for a prefix-format version (no rows).
 *
 * MUST run BEFORE deleting the version row: an FK cascade on version deletion
 * would otherwise erase version_files before refcounts can decrement.
 */
export function dereferenceVersion(
  db: Database,
  spaceId: string,
  versionId: string,
): Array<{ hash: string; size: number }> {
  const freed: Array<{ hash: string; size: number }> = [];

  db.transaction(() => {
    const rows = db
      .query<{ path: string; hash: string; size: number }, [string]>(
        `SELECT path, hash, size FROM version_files WHERE version_id = ?`,
      )
      .all(versionId);

    if (rows.length === 0) return; // prefix-format version or already dereferenced

    // Dedup by hash → one decrement per referencing version.
    const byHash = new Map<string, { hash: string; size: number }>();
    for (const r of rows) {
      if (!byHash.has(r.hash)) byHash.set(r.hash, { hash: r.hash, size: r.size });
    }

    for (const { hash, size } of byHash.values()) {
      // Guard: only decrement a positive refcount — never drive it negative.
      const result = db.run(
        `UPDATE blobs SET refcount = refcount - 1
         WHERE space_id = ? AND hash = ? AND refcount > 0`,
        [spaceId, hash],
      );
      if (result.changes === 0) {
        console.error(
          `[cas] dereferenceVersion: refcount underflow guarded for space=${spaceId} hash=${hash} version=${versionId} (row missing or already 0)`,
        );
        continue;
      }
      const after = db
        .query<{ refcount: number }, [string, string]>(
          `SELECT refcount FROM blobs WHERE space_id = ? AND hash = ?`,
        )
        .get(spaceId, hash);
      if (after && after.refcount === 0) freed.push({ hash, size });
    }

    db.run(`DELETE FROM version_files WHERE version_id = ?`, [versionId]);
  })();

  return freed;
}

/**
 * Hybrid unique-bytes quota for a space:
 *   CAS term:    SUM(blobs.size) for blobs with refcount > 0.
 *   Prefix term (a): sites.total_size for sites whose LIVE version is prefix-format.
 *   Prefix term (b): SUM(site_versions.total_size) for archived prefix-format versions.
 *
 * The two prefix terms and the CAS term cannot overlap: prefix versions never
 * have blobs/version_files rows, and a CAS-live site's `sites.total_size` is
 * dropped (its bytes are counted via the CAS term instead). On a CAS-free space
 * (no blobs rows, every version storage_format = 'prefix') the CAS term is 0 and
 * the prefix terms reproduce `sumStorageForSpace` EXACTLY.
 *
 * Transition case (CAS-live site with archived prefix history elsewhere in the
 * space): live bytes count via the CAS term, archived prefix versions via the
 * prefix term — every byte counted exactly once.
 */
export function sumUniqueStorageForSpace(db: Database, spaceId: string): number {
  const row = db
    .query<{ total: number }, [string, string, string]>(
      `SELECT COALESCE((
                SELECT SUM(b.size) FROM blobs b WHERE b.space_id = ? AND b.refcount > 0
              ), 0)
            + COALESCE((
                SELECT SUM(s.total_size)
                FROM sites s
                WHERE s.space_id = ?
                  AND NOT EXISTS (
                    SELECT 1 FROM site_versions lv
                    WHERE lv.site_id = s.id
                      AND lv.version_number = s.live_version
                      AND lv.storage_format = 'cas'
                  )
              ), 0)
            + COALESCE((
                SELECT SUM(sv.total_size)
                FROM site_versions sv
                JOIN sites s2 ON s2.id = sv.site_id
                WHERE s2.space_id = ?
                  AND sv.status = 'archived'
                  AND sv.storage_format = 'prefix'
              ), 0) AS total`,
    )
    .get(spaceId, spaceId, spaceId);
  return row?.total ?? 0;
}

/**
 * Projects the post-publish unique-bytes storage for a space: the current
 * hybrid total plus the sizes of incoming blobs NOT already present (refcount
 * > 0) for the space. Incoming files are deduplicated by hash first.
 *
 * On a CAS-free space, no incoming hash is ever already in `blobs`, so the
 * incoming term is the sum of all incoming sizes — exactly the legacy
 * "incomingSize" the manifest endpoint's existing quota tests assert.
 */
export function projectUniqueStorage(
  db: Database,
  spaceId: string,
  incoming: Array<{ hash: string; size: number }>,
): number {
  const base = sumUniqueStorageForSpace(db, spaceId);

  const byHash = new Map<string, number>();
  for (const f of incoming) {
    if (!byHash.has(f.hash)) byHash.set(f.hash, f.size);
  }

  const present = db.query<{ hash: string }, [string]>(
    `SELECT hash FROM blobs WHERE space_id = ? AND refcount > 0`,
  );
  const alreadyPresent = new Set(present.all(spaceId).map((r) => r.hash));

  let incomingNew = 0;
  for (const [hash, size] of byHash) {
    if (!alreadyPresent.has(hash)) incomingNew += size;
  }
  return base + incomingNew;
}
