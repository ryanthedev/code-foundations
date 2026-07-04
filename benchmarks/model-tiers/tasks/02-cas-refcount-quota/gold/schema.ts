/**
 * Storage schema for a space's sites — pre-CAS tables plus the CAS foundation:
 * a per-space refcounted blob store (`blobs`) and each CAS version's path→hash
 * map (`version_files`). Bytes live once per space at `{space_id}/blobs/{hash}`
 * (the R2 layer is out of scope here — Phase 2); `blobs.refcount` counts the
 * number of VERSIONS referencing a hash, not the number of paths or sites.
 */
import type { Database } from "bun:sqlite";

/**
 * Applies the schema. Idempotent — safe to call on a fresh `:memory:`/file db,
 * one that only has the pre-CAS tables (`sites`/`site_versions`), or one that
 * has already been fully migrated.
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

  // storage_format: added via ALTER + try/catch — SQLite has no
  // "ADD COLUMN IF NOT EXISTS", and this must be safe to re-run on a db that
  // already has the column (idempotency, DW-H1.1).
  try {
    db.run(
      `ALTER TABLE site_versions ADD COLUMN storage_format TEXT NOT NULL DEFAULT 'prefix'
         CHECK(storage_format IN ('prefix','cas'))`,
    );
  } catch (e) {
    if (!(e instanceof Error) || !/duplicate column/i.test(e.message)) throw e;
  }

  db.run(`
    CREATE TABLE IF NOT EXISTS blobs (
      space_id    TEXT NOT NULL,
      hash        TEXT NOT NULL,
      size        INTEGER NOT NULL,
      refcount    INTEGER NOT NULL DEFAULT 0,
      created_at  TEXT NOT NULL,
      PRIMARY KEY (space_id, hash)
    )
  `);
  // Quota-path index: the unique-bytes sum must not full-scan large spaces.
  db.run(`CREATE INDEX IF NOT EXISTS blobs_space_refcount ON blobs(space_id, refcount)`);
  db.run(`
    CREATE TABLE IF NOT EXISTS version_files (
      version_id  TEXT NOT NULL REFERENCES site_versions(id) ON DELETE CASCADE,
      path        TEXT NOT NULL,
      hash        TEXT NOT NULL,
      size        INTEGER NOT NULL,
      PRIMARY KEY (version_id, path)
    )
  `);
}
