/**
 * Stats query tests. Per-namespace total_storage is the LIVE footprint;
 * the account headline number is the dedup-aware own-space footprint.
 */
import { describe, expect, test } from "bun:test";
import {
  createNamespace,
  createSite,
  createSpace,
  createVersion,
  grantMember,
  openDb,
} from "./fixtures.ts";
import {
  getAccountStorageTotal,
  listNamespacesForUser,
  listRootNamespacesWithStats,
} from "./stats.ts";

describe("listRootNamespacesWithStats", () => {
  test("total_storage is the live footprint; archived history is not re-added", () => {
    const db = openDb();
    createSpace(db, "sp1", "u1");
    createNamespace(db, "ns1", "sp1", "alice");
    createSite(db, "st1", "ns1", "blog", 300, 2);
    createVersion(db, "v2", "st1", 2, 300, "active", "prefix");
    createVersion(db, "v1", "st1", 1, 200, "archived", "prefix");
    const rows = listRootNamespacesWithStats(db, "sp1");
    expect(rows).toHaveLength(1);
    expect(rows[0].site_count).toBe(1);
    expect(rows[0].total_storage).toBe(300);
  });

  test("staging versions are excluded from total_storage", () => {
    const db = openDb();
    createSpace(db, "sp1", "u1");
    createNamespace(db, "ns1", "sp1", "alice");
    createSite(db, "st1", "ns1", "blog", 300, 2);
    createVersion(db, "vs", "st1", 3, 999, "staging", "prefix");
    const rows = listRootNamespacesWithStats(db, "sp1");
    expect(rows[0].total_storage).toBe(300);
  });

  test("namespace with no sites reports zero", () => {
    const db = openDb();
    createSpace(db, "sp1", "u1");
    createNamespace(db, "ns1", "sp1", "alice");
    const rows = listRootNamespacesWithStats(db, "sp1");
    expect(rows[0].site_count).toBe(0);
    expect(rows[0].total_storage).toBe(0);
  });
});

describe("listNamespacesForUser", () => {
  test("returns owned namespaces tagged owner and granted ones with their role", () => {
    const db = openDb();
    createSpace(db, "sp1", "u1");
    createSpace(db, "sp2", "u2");
    createNamespace(db, "ns1", "sp1", "alice", "2026-06-01 00:00:00");
    createNamespace(db, "ns2", "sp2", "bob", "2026-06-02 00:00:00");
    grantMember(db, "ns2", "u1", "user");
    const rows = listNamespacesForUser(db, "u1");
    expect(rows.map((r) => [r.name, r.role])).toEqual([
      ["alice", "owner"],
      ["bob", "user"],
    ]);
  });
});

describe("getAccountStorageTotal", () => {
  test("reports the own space's deduplicated footprint; granted namespaces are not billed to the user", () => {
    const db = openDb();
    createSpace(db, "sp1", "u1");
    createSpace(db, "sp2", "u2");
    createNamespace(db, "ns1", "sp1", "alice");
    createNamespace(db, "ns2", "sp2", "bob");
    grantMember(db, "ns2", "u1", "admin");
    createSite(db, "st1", "ns1", "blog", 300, 1);
    createVersion(db, "v1", "st1", 1, 300, "active", "prefix");
    createSite(db, "st2", "ns2", "docs", 700, 1);
    expect(getAccountStorageTotal(db, "u1")).toBe(300);
  });
});
