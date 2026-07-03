/**
 * Storage query functions for a space.
 *
 * `sumStorageForSpace` is the LEGACY quota computation: every site's live
 * bytes, plus every archived version's bytes, full-cost, no dedup. It is the
 * baseline this phase's hybrid quota must reproduce exactly when no CAS data
 * exists yet (see spec.md DW-H1.4).
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
