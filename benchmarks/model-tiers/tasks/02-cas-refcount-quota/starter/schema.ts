/**
 * Pre-CAS storage schema for a space's sites.
 *
 * A space has many sites; each site has many versions. `sites.total_size`
 * tracks the live version's bytes; archived versions keep their own
 * `total_size`. There is no dedup — every version's files are stored in full,
 * so an unchanged file re-costs its full size on every republish (the quota
 * burn this phase's DW items exist to fix).
 */
import type { Database } from "bun:sqlite";

/**
 * Applies the schema. Idempotent — safe to call on a fresh `:memory:`/file db
 * or one that has already been migrated.
 */
export function migrate(db: Database): void {
  db.run(`
    CREATE TABLE IF NOT EXISTS sites (
      id TEXT PRIMARY KEY,
      space_id TEXT NOT NULL,
      total_size INTEGER NOT NULL DEFAULT 0,
      live_version INTEGER
    )
  `);
  db.run(`
    CREATE TABLE IF NOT EXISTS site_versions (
      id TEXT PRIMARY KEY,
      site_id TEXT NOT NULL REFERENCES sites(id),
      version_number INTEGER NOT NULL,
      status TEXT NOT NULL DEFAULT 'archived' CHECK(status IN ('archived','active','staging')),
      total_size INTEGER NOT NULL DEFAULT 0
    )
  `);
}
