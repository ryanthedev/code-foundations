/**
 * Hidden ground-truth suite for task 02 (CAS foundation: schema, refcounts,
 * hybrid quota). Never shown to the agent under test.
 *
 *   test_dw_*    — behavior a specific DW item (spec.md DW-H1.1..H1.5) states
 *   test_offdw_* — preserved behavior + dirty edges (bad data, empty input,
 *                  constraint violations) the spec did not exemplify
 */
import { test, expect, beforeEach } from "bun:test";
import { Database } from "bun:sqlite";
import { migrate } from "./schema.ts";
import {
  sumStorageForSpace,
  referenceBlobs,
  dereferenceVersion,
  sumUniqueStorageForSpace,
  projectUniqueStorage,
} from "./db.ts";

function freshDb(): Database {
  const db = new Database(":memory:");
  migrate(db);
  return db;
}

let seq = 0;
function id(prefix: string): string {
  seq += 1;
  return `${prefix}-${seq}`;
}

function insertSite(
  db: Database,
  spaceId: string,
  opts: { totalSize?: number; liveVersion?: number | null } = {},
): string {
  const siteId = id("site");
  db.run(`INSERT INTO sites (id, space_id, total_size, live_version) VALUES (?, ?, ?, ?)`, [
    siteId,
    spaceId,
    opts.totalSize ?? 0,
    opts.liveVersion ?? null,
  ]);
  return siteId;
}

function insertVersion(
  db: Database,
  siteId: string,
  opts: {
    versionNumber: number;
    status?: "archived" | "active" | "staging";
    totalSize?: number;
    storageFormat?: "prefix" | "cas";
  },
): string {
  const versionId = id("v");
  db.run(
    `INSERT INTO site_versions (id, site_id, version_number, status, total_size, storage_format)
     VALUES (?, ?, ?, ?, ?, ?)`,
    [
      versionId,
      siteId,
      opts.versionNumber,
      opts.status ?? "archived",
      opts.totalSize ?? 0,
      opts.storageFormat ?? "prefix",
    ],
  );
  return versionId;
}

function blobRefcount(db: Database, spaceId: string, hash: string): number | null {
  const row = db
    .query<{ refcount: number }, [string, string]>(
      `SELECT refcount FROM blobs WHERE space_id = ? AND hash = ?`,
    )
    .get(spaceId, hash);
  return row?.refcount ?? null;
}

// ─── DW-H1.1: migrate() idempotency + schema shape ─────────────────────────

test("test_dw_H1_1_migrate_idempotent_on_fresh_db", () => {
  const db = new Database(":memory:");
  expect(() => migrate(db)).not.toThrow();
  const tables = db
    .query<{ name: string }, []>(`SELECT name FROM sqlite_master WHERE type='table'`)
    .all()
    .map((r) => r.name);
  expect(tables).toContain("blobs");
  expect(tables).toContain("version_files");
});

test("test_dw_H1_1_migrate_idempotent_on_preexisting_pre_cas_schema", () => {
  // Simulates a db that only has the OLD (pre-Phase-1) tables — no
  // storage_format column, no blobs/version_files tables yet.
  const db = new Database(":memory:");
  db.run(`CREATE TABLE sites (id TEXT PRIMARY KEY, space_id TEXT NOT NULL, total_size INTEGER NOT NULL DEFAULT 0, live_version INTEGER)`);
  db.run(`CREATE TABLE site_versions (id TEXT PRIMARY KEY, site_id TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'archived', total_size INTEGER NOT NULL DEFAULT 0, version_number INTEGER NOT NULL)`);
  expect(() => migrate(db)).not.toThrow();
  const cols = db.query<{ name: string }, []>(`PRAGMA table_info(site_versions)`).all();
  expect(cols.some((c) => c.name === "storage_format")).toBe(true);
});

test("test_dw_H1_1_migrate_idempotent_double_run", () => {
  const db = freshDb();
  expect(() => migrate(db)).not.toThrow();
  expect(() => migrate(db)).not.toThrow();
});

test("test_dw_H1_1_storage_format_default_and_check_constraint", () => {
  const db = freshDb();
  const spaceId = id("space");
  const siteId = insertSite(db, spaceId);
  const versionId = insertVersion(db, siteId, { versionNumber: 1 });
  const row = db
    .query<{ storage_format: string }, [string]>(
      `SELECT storage_format FROM site_versions WHERE id = ?`,
    )
    .get(versionId);
  expect(row?.storage_format).toBe("prefix");
});

// ─── DW-H1.2: referenceBlobs / dereferenceVersion are transactional ────────

test("test_dw_H1_2_referenceBlobs_rolls_back_on_injected_failure", () => {
  const db = freshDb();
  const spaceId = id("space");
  const siteId = insertSite(db, spaceId);
  const versionId = insertVersion(db, siteId, { versionNumber: 1, storageFormat: "cas" });

  // Duplicate PATH within one files list violates version_files' (version_id, path)
  // PK on the second insert — the whole operation (including the blobs upserts
  // that ran first) must roll back.
  expect(() =>
    referenceBlobs(db, spaceId, versionId, [
      { path: "a", hash: "hash1", size: 10 },
      { path: "a", hash: "hash2", size: 20 },
    ]),
  ).toThrow();

  expect(blobRefcount(db, spaceId, "hash1")).toBeNull();
  expect(blobRefcount(db, spaceId, "hash2")).toBeNull();
  const vfCount = db
    .query<{ n: number }, [string]>(`SELECT COUNT(*) as n FROM version_files WHERE version_id = ?`)
    .get(versionId);
  expect(vfCount?.n).toBe(0);
});

// ─── DW-H1.3: refcount semantics ────────────────────────────────────────────

test("test_dw_H1_3_refcount_bumps_once_per_version_not_per_path", () => {
  const db = freshDb();
  const spaceId = id("space");
  const siteId = insertSite(db, spaceId);
  const versionId = insertVersion(db, siteId, { versionNumber: 1, storageFormat: "cas" });

  referenceBlobs(db, spaceId, versionId, [
    { path: "a", hash: "shared", size: 100 },
    { path: "b", hash: "shared", size: 100 },
  ]);

  expect(blobRefcount(db, spaceId, "shared")).toBe(1);
});

test("test_dw_H1_3_refcount_bumps_again_for_a_second_version", () => {
  const db = freshDb();
  const spaceId = id("space");
  const siteId = insertSite(db, spaceId);
  const v1 = insertVersion(db, siteId, { versionNumber: 1, storageFormat: "cas" });
  const v2 = insertVersion(db, siteId, { versionNumber: 2, storageFormat: "cas" });

  referenceBlobs(db, spaceId, v1, [{ path: "a", hash: "shared", size: 100 }]);
  referenceBlobs(db, spaceId, v2, [{ path: "a", hash: "shared", size: 100 }]);

  expect(blobRefcount(db, spaceId, "shared")).toBe(2);
});

test("test_dw_H1_3_dereferenceVersion_noop_on_prefix_format_version", () => {
  const db = freshDb();
  const spaceId = id("space");
  const siteId = insertSite(db, spaceId);
  const versionId = insertVersion(db, siteId, { versionNumber: 1, storageFormat: "prefix" });

  const freed = dereferenceVersion(db, spaceId, versionId);
  expect(freed).toEqual([]);
});

test("test_dw_H1_3_dereferenceVersion_returns_zeroed_hashes", () => {
  const db = freshDb();
  const spaceId = id("space");
  const siteId = insertSite(db, spaceId);
  const versionId = insertVersion(db, siteId, { versionNumber: 1, storageFormat: "cas" });
  referenceBlobs(db, spaceId, versionId, [{ path: "a", hash: "onlyref", size: 50 }]);

  const freed = dereferenceVersion(db, spaceId, versionId);
  expect(freed).toEqual([{ hash: "onlyref", size: 50 }]);
  expect(blobRefcount(db, spaceId, "onlyref")).toBe(0);
});

test("test_dw_H1_3_refcount_never_goes_negative", () => {
  const db = freshDb();
  const spaceId = id("space");
  const siteId = insertSite(db, spaceId);
  const versionId = insertVersion(db, siteId, { versionNumber: 1, storageFormat: "cas" });
  // Force an already-zero refcount row directly (simulates prior corruption /
  // a race), then reference version_files pointing at it without going
  // through referenceBlobs (bad/dirty state).
  db.run(
    `INSERT INTO blobs (space_id, hash, size, refcount, created_at) VALUES (?, ?, ?, 0, ?)`,
    [spaceId, "zeroed", 10, "2026-01-01T00:00:00.000Z"],
  );
  db.run(`INSERT INTO version_files (version_id, path, hash, size) VALUES (?, ?, ?, ?)`, [
    versionId,
    "a",
    "zeroed",
    10,
  ]);

  const freed = dereferenceVersion(db, spaceId, versionId);
  expect(freed).toEqual([]); // guarded — not decremented, not reported as newly-freed
  expect(blobRefcount(db, spaceId, "zeroed")).toBe(0);
});

test("test_dw_H1_3_created_at_preserved_on_re_reference", () => {
  const db = freshDb();
  const spaceId = id("space");
  const siteId = insertSite(db, spaceId);
  const v1 = insertVersion(db, siteId, { versionNumber: 1, storageFormat: "cas" });
  referenceBlobs(db, spaceId, v1, [{ path: "a", hash: "aged", size: 10 }]);
  const before = db
    .query<{ created_at: string }, [string, string]>(
      `SELECT created_at FROM blobs WHERE space_id = ? AND hash = ?`,
    )
    .get(spaceId, "aged");

  dereferenceVersion(db, spaceId, v1); // refcount -> 0
  const v2 = insertVersion(db, siteId, { versionNumber: 2, storageFormat: "cas" });
  referenceBlobs(db, spaceId, v2, [{ path: "b", hash: "aged", size: 10 }]); // re-reference

  const after = db
    .query<{ created_at: string; refcount: number }, [string, string]>(
      `SELECT created_at, refcount FROM blobs WHERE space_id = ? AND hash = ?`,
    )
    .get(spaceId, "aged");
  expect(after?.created_at).toBe(before?.created_at);
  expect(after?.refcount).toBe(1);
  const rowCount = db
    .query<{ n: number }, [string, string]>(
      `SELECT COUNT(*) as n FROM blobs WHERE space_id = ? AND hash = ?`,
    )
    .get(spaceId, "aged");
  expect(rowCount?.n).toBe(1);
});

// ─── DW-H1.4: hybrid quota ───────────────────────────────────────────────────

test("test_dw_H1_4_sumUnique_equals_legacy_on_cas_free_fixture", () => {
  const db = freshDb();
  const spaceId = id("space");
  const siteA = insertSite(db, spaceId, { totalSize: 300, liveVersion: 1 });
  insertVersion(db, siteA, { versionNumber: 1, status: "active", totalSize: 300, storageFormat: "prefix" });
  insertVersion(db, siteA, { versionNumber: 0, status: "archived", totalSize: 150, storageFormat: "prefix" });

  const legacy = sumStorageForSpace(db, spaceId);
  const hybrid = sumUniqueStorageForSpace(db, spaceId);
  expect(hybrid).toBe(legacy);
  expect(hybrid).toBe(450);
});

test("test_dw_H1_4_shared_blob_counted_once_across_two_versions", () => {
  const db = freshDb();
  const spaceId = id("space");
  const siteId = insertSite(db, spaceId, { liveVersion: 2 });
  const v1 = insertVersion(db, siteId, { versionNumber: 1, status: "archived", storageFormat: "cas" });
  const v2 = insertVersion(db, siteId, { versionNumber: 2, status: "active", storageFormat: "cas" });
  referenceBlobs(db, spaceId, v1, [{ path: "a", hash: "shared", size: 1000 }]);
  referenceBlobs(db, spaceId, v2, [{ path: "a", hash: "shared", size: 1000 }]);

  expect(sumUniqueStorageForSpace(db, spaceId)).toBe(1000);
});

test("test_dw_H1_4_transition_fixture_counts_every_byte_once", () => {
  const db = freshDb();
  const spaceId = id("space");

  // Site A: live version is CAS-format, referencing a 500-byte blob.
  const siteA = insertSite(db, spaceId, { liveVersion: 1 });
  const aLive = insertVersion(db, siteA, { versionNumber: 1, status: "active", storageFormat: "cas" });
  referenceBlobs(db, spaceId, aLive, [{ path: "x", hash: "casblob", size: 500 }]);

  // Site B: unrelated site with an archived prefix-format version (legacy history).
  const siteB = insertSite(db, spaceId, { totalSize: 0, liveVersion: 2 });
  insertVersion(db, siteB, { versionNumber: 2, status: "active", totalSize: 0, storageFormat: "prefix" });
  insertVersion(db, siteB, { versionNumber: 1, status: "archived", totalSize: 200, storageFormat: "prefix" });

  // Expected: CAS term (500) + prefix term(a) (siteB's live total_size=0, since its
  // live version is prefix-format sites.total_size counts — 0 here) + prefix term(b)
  // (siteB's archived prefix version, 200). siteA's total_size is NOT counted
  // (its live version is CAS-format) — no double count.
  expect(sumUniqueStorageForSpace(db, spaceId)).toBe(700);
});

// ─── DW-H1.5: projectUniqueStorage ───────────────────────────────────────────

test("test_dw_H1_5_project_adds_only_new_incoming_bytes", () => {
  const db = freshDb();
  const spaceId = id("space");
  const siteId = insertSite(db, spaceId, { liveVersion: 1 });
  const v1 = insertVersion(db, siteId, { versionNumber: 1, status: "active", storageFormat: "cas" });
  referenceBlobs(db, spaceId, v1, [{ path: "a", hash: "existing", size: 100 }]);

  const projected = projectUniqueStorage(db, spaceId, [
    { hash: "existing", size: 100 }, // already present — contributes 0 new
    { hash: "new", size: 50 },
  ]);
  expect(projected).toBe(100 + 50);
});

test("test_dw_H1_5_project_dedups_incoming_by_hash", () => {
  const db = freshDb();
  const spaceId = id("space");
  const projected = projectUniqueStorage(db, spaceId, [
    { hash: "dup", size: 30 },
    { hash: "dup", size: 30 },
  ]);
  expect(projected).toBe(30); // counted once, not twice
});

test("test_dw_H1_5_project_on_cas_free_space_equals_legacy_plus_incoming", () => {
  const db = freshDb();
  const spaceId = id("space");
  insertSite(db, spaceId, { totalSize: 100, liveVersion: 1 });
  const projected = projectUniqueStorage(db, spaceId, [{ hash: "n1", size: 40 }]);
  expect(projected).toBe(sumStorageForSpace(db, spaceId) + 40);
});

test("test_offdw_project_empty_incoming_returns_base_unchanged", () => {
  const db = freshDb();
  const spaceId = id("space");
  insertSite(db, spaceId, { totalSize: 77, liveVersion: 1 });
  const projected = projectUniqueStorage(db, spaceId, []);
  expect(projected).toBe(sumUniqueStorageForSpace(db, spaceId));
  expect(projected).toBe(77);
});

// ─── Off-DW: dirty/bad data + preserved behavior ───────────────────────────

test("test_offdw_referenceBlobs_empty_files_is_noop", () => {
  const db = freshDb();
  const spaceId = id("space");
  const siteId = insertSite(db, spaceId);
  const versionId = insertVersion(db, siteId, { versionNumber: 1, storageFormat: "cas" });
  expect(() => referenceBlobs(db, spaceId, versionId, [])).not.toThrow();
  const count = db.query<{ n: number }, []>(`SELECT COUNT(*) as n FROM blobs`).get();
  expect(count?.n).toBe(0);
});

test("test_offdw_bad_storage_format_value_rejected_by_check_constraint", () => {
  const db = freshDb();
  const spaceId = id("space");
  const siteId = insertSite(db, spaceId);
  expect(() =>
    db.run(
      `INSERT INTO site_versions (id, site_id, version_number, status, total_size, storage_format)
       VALUES (?, ?, ?, ?, ?, ?)`,
      [id("v"), siteId, 1, "archived", 0, "bogus"],
    ),
  ).toThrow();
});

test("test_offdw_dereferenceVersion_on_nonexistent_version_returns_empty", () => {
  const db = freshDb();
  const spaceId = id("space");
  expect(dereferenceVersion(db, spaceId, "does-not-exist")).toEqual([]);
});

test("test_offdw_sumUniqueStorageForSpace_empty_space_is_zero", () => {
  const db = freshDb();
  expect(sumUniqueStorageForSpace(db, id("space"))).toBe(0);
});

test("test_offdw_sumStorageForSpace_unaffected_by_cas_rows_in_other_space", () => {
  // Regression: legacy sumStorageForSpace must not be perturbed by the new
  // blobs/version_files tables existing (cross-space isolation).
  const db = freshDb();
  const spaceA = id("space");
  const spaceB = id("space");
  const siteA = insertSite(db, spaceA, { totalSize: 42, liveVersion: 1 });
  insertVersion(db, siteA, { versionNumber: 1, status: "active", totalSize: 42, storageFormat: "prefix" });
  const siteB = insertSite(db, spaceB, { liveVersion: 1 });
  const vB = insertVersion(db, siteB, { versionNumber: 1, status: "active", storageFormat: "cas" });
  referenceBlobs(db, spaceB, vB, [{ path: "x", hash: "other-space-blob", size: 999 }]);

  expect(sumStorageForSpace(db, spaceA)).toBe(42);
});
