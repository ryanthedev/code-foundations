/**
 * Deterministic seed helpers shared by every test in this workspace.
 * Test plumbing only — not part of the system under test; do not modify.
 *
 * Seams:
 *   openDb                  — fresh migrated in-memory database
 *   createSpace/createNamespace/createSite/createVersion/createBlob/grantMember
 */
import { Database } from "bun:sqlite";
import { migrate } from "./schema.ts";

export function openDb(): Database {
  const db = new Database(":memory:");
  migrate(db);
  return db;
}

export function createSpace(db: Database, id: string, userId: string): void {
  db.run(`INSERT INTO spaces (id, user_id) VALUES (?, ?)`, [id, userId]);
}

export function createNamespace(
  db: Database,
  id: string,
  spaceId: string,
  name: string,
  createdAt = "2026-06-01 00:00:00",
): void {
  db.run(
    `INSERT INTO namespaces (id, space_id, name, domain, parent_id, created_at)
     VALUES (?, ?, ?, 'upubli.sh', NULL, ?)`,
    [id, spaceId, name, createdAt],
  );
}

export function createSite(
  db: Database,
  id: string,
  namespaceId: string,
  slug: string,
  totalSize: number,
  liveVersion: number,
): void {
  db.run(
    `INSERT INTO sites (id, namespace_id, slug, total_size, live_version)
     VALUES (?, ?, ?, ?, ?)`,
    [id, namespaceId, slug, totalSize, liveVersion],
  );
}

export function createVersion(
  db: Database,
  id: string,
  siteId: string,
  versionNumber: number,
  totalSize: number,
  status: "active" | "staging" | "archived",
  storageFormat: "prefix" | "cas",
): void {
  db.run(
    `INSERT INTO site_versions (id, site_id, version_number, total_size, status, storage_format)
     VALUES (?, ?, ?, ?, ?, ?)`,
    [id, siteId, versionNumber, totalSize, status, storageFormat],
  );
}

export function createBlob(
  db: Database,
  spaceId: string,
  hash: string,
  size: number,
  refcount: number,
): void {
  db.run(`INSERT INTO blobs (space_id, hash, size, refcount) VALUES (?, ?, ?, ?)`, [
    spaceId,
    hash,
    size,
    refcount,
  ]);
}

export function grantMember(
  db: Database,
  namespaceId: string,
  userId: string,
  role: "admin" | "user",
): void {
  db.run(`INSERT INTO namespace_members (namespace_id, user_id, role) VALUES (?, ?, ?)`, [
    namespaceId,
    userId,
    role,
  ]);
}

/**
 * Seeds the live-incident shape from the bug report (units: MB):
 * one pro space, one namespace, one CAS site with a 5370 MB live version and
 * 1 archived CAS version of the same content (bytes deduped in blobs).
 */
export function seedCasIncident(db: Database): {
  spaceId: string;
  userId: string;
  nsId: string;
} {
  const spaceId = "space-cas";
  const userId = "user-cas";
  createSpace(db, spaceId, userId);
  createNamespace(db, "ns-cas", spaceId, "ryan");
  createSite(db, "site-cas", "ns-cas", "bigsite", 5370, 5);
  createVersion(db, "v5", "site-cas", 5, 5370, "active", "cas");
  createVersion(db, "v4", "site-cas", 4, 5370, "archived", "cas");
  // The actual bytes: one deduplicated blob set, stored once.
  createBlob(db, spaceId, "blobset-a", 5370, 2);
  return { spaceId, userId, nsId: "ns-cas" };
}
