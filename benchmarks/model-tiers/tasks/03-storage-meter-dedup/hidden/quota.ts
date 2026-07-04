/**
 * The publish gate's storage accounting — dedup-aware and AUTHORITATIVE.
 *
 * This is what actually admits or blocks a publish, and what billing charges
 * against. It is verified against production and is NOT part of this bug:
 * treat it as the ground truth for how many bytes a space really occupies.
 *
 * The total is the sum of non-overlapping terms:
 *   CAS term    — deduplicated bytes: SUM(blobs.size) WHERE refcount > 0
 *   Prefix (a)  — live bytes of sites whose live version is NOT CAS
 *   Prefix (b)  — legacy archived history (storage_format = 'prefix')
 *
 * Seams:
 *   sumUniqueStorageForSpace — a space's real, deduplicated byte footprint
 *   checkPublishGate         — cap check used by the publish path
 */
import type { Database } from "bun:sqlite";

/** A space's real (deduplicated) storage footprint. */
export function sumUniqueStorageForSpace(db: Database, spaceId: string): number {
  const row = db
    .query<{ total: number }, [string, string, string]>(
      `SELECT COALESCE((
                SELECT SUM(b.size)
                FROM blobs b
                WHERE b.space_id = ? AND b.refcount > 0
              ), 0)
            + COALESCE((
                SELECT SUM(s.total_size)
                FROM sites s
                JOIN namespaces n ON n.id = s.namespace_id
                WHERE n.space_id = ?
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
                JOIN namespaces n2 ON n2.id = s2.namespace_id
                WHERE n2.space_id = ?
                  AND sv.status = 'archived'
                  AND sv.storage_format = 'prefix'
              ), 0) AS total`,
    )
    .get(spaceId, spaceId, spaceId);
  return row?.total ?? 0;
}

/** Publish-gate cap check: uses the deduplicated footprint. */
export function checkPublishGate(
  db: Database,
  spaceId: string,
  incomingBytes: number,
  capBytes: number,
): { allowed: boolean; used: number } {
  const used = sumUniqueStorageForSpace(db, spaceId);
  return { allowed: used + incomingBytes <= capBytes, used };
}
