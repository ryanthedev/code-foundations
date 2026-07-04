/**
 * Pristine-starter check (DW-1.2, second clause — SCHEMA.md "Pristine-starter
 * check"). Imports ONLY the symbols the starter already exports (`migrate`,
 * `sumStorageForSpace`) — proves the untouched starter is not already broken.
 * Run against the pristine starter, never against outputs/.
 */
import { test, expect } from "bun:test";
import { Database } from "bun:sqlite";
import { migrate } from "./schema.ts";
import { sumStorageForSpace } from "./db.ts";

test("test_offdw_pristine_migrate_creates_sites_and_site_versions", () => {
  const db = new Database(":memory:");
  expect(() => migrate(db)).not.toThrow();
  const tables = db
    .query<{ name: string }, []>(`SELECT name FROM sqlite_master WHERE type='table'`)
    .all()
    .map((r) => r.name);
  expect(tables).toContain("sites");
  expect(tables).toContain("site_versions");
});

test("test_offdw_pristine_sumStorageForSpace_sums_live_plus_archived", () => {
  const db = new Database(":memory:");
  migrate(db);
  db.run(`INSERT INTO sites (id, space_id, total_size, live_version) VALUES ('s1','sp1',300,1)`);
  db.run(
    `INSERT INTO site_versions (id, site_id, version_number, status, total_size) VALUES ('v1','s1',1,'active',300)`,
  );
  db.run(
    `INSERT INTO site_versions (id, site_id, version_number, status, total_size) VALUES ('v0','s1',0,'archived',150)`,
  );
  expect(sumStorageForSpace(db, "sp1")).toBe(450);
});

test("test_offdw_pristine_sumStorageForSpace_empty_space_is_zero", () => {
  const db = new Database(":memory:");
  migrate(db);
  expect(sumStorageForSpace(db, "nope")).toBe(0);
});
