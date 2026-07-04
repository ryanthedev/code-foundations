/**
 * Storage schema for a publishing platform mid-migration to CAS
 * (content-addressed storage).
 *
 * Two storage generations coexist:
 *   - `prefix` (legacy): every version's files stored in full — an archived
 *     version's `total_size` is real, additional bytes on disk.
 *   - `cas`: bytes live once per space in refcounted `blobs`; versions
 *     reference blobs, so an archived CAS version's `total_size` describes the
 *     version's CONTENT size, not additional stored bytes.
 *
 * `site_versions.storage_format` records which generation wrote each version.
 * `sites.total_size` tracks the live version's content size.
 *
 * Seams:
 *   migrate — applies the schema (idempotent, in-memory friendly)
 */
import type { Database } from "bun:sqlite";

/** Applies the schema. Safe on a fresh `:memory:` db. */
export function migrate(db: Database): void {
  db.run(`
    CREATE TABLE IF NOT EXISTS spaces (
      id TEXT PRIMARY KEY,
      user_id TEXT NOT NULL UNIQUE
    );
    CREATE TABLE IF NOT EXISTS namespaces (
      id TEXT PRIMARY KEY,
      space_id TEXT NOT NULL REFERENCES spaces(id),
      name TEXT NOT NULL,
      domain TEXT NOT NULL,
      parent_id TEXT REFERENCES namespaces(id),
      created_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS namespace_members (
      namespace_id TEXT NOT NULL REFERENCES namespaces(id),
      user_id TEXT NOT NULL,
      role TEXT NOT NULL CHECK (role IN ('admin', 'user')),
      PRIMARY KEY (namespace_id, user_id)
    );
    CREATE TABLE IF NOT EXISTS sites (
      id TEXT PRIMARY KEY,
      namespace_id TEXT NOT NULL REFERENCES namespaces(id),
      slug TEXT NOT NULL,
      total_size INTEGER NOT NULL DEFAULT 0,
      live_version INTEGER NOT NULL DEFAULT 1
    );
    CREATE TABLE IF NOT EXISTS site_versions (
      id TEXT PRIMARY KEY,
      site_id TEXT NOT NULL REFERENCES sites(id),
      version_number INTEGER NOT NULL,
      total_size INTEGER NOT NULL DEFAULT 0,
      status TEXT NOT NULL CHECK (status IN ('active', 'staging', 'archived')),
      storage_format TEXT NOT NULL CHECK (storage_format IN ('prefix', 'cas'))
    );
    CREATE TABLE IF NOT EXISTS blobs (
      space_id TEXT NOT NULL,
      hash TEXT NOT NULL,
      size INTEGER NOT NULL,
      refcount INTEGER NOT NULL DEFAULT 0,
      PRIMARY KEY (space_id, hash)
    );
  `);
}
