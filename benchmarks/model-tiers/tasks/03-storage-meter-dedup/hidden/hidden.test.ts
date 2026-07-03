/**
 * Hidden ground-truth suite for 03-storage-meter-dedup.
 *
 * Imports the merged outputs (fixed modules overwrite the starter copies in
 * this directory). A correct fix makes the read-side stats dedup-aware WITHOUT
 * touching the gate: per-namespace total_storage becomes the live footprint,
 * and the account meter number becomes the own space's deduplicated footprint.
 * The gate (`sumUniqueStorageForSpace`, `checkPublishGate`) is pinned.
 */
import { describe, expect, test } from "bun:test";
import {
  createBlob,
  createNamespace,
  createSite,
  createSpace,
  createVersion,
  grantMember,
  openDb,
  seedCasIncident,
} from "./fixtures.ts";
import {
  getAccountStorageTotal,
  listNamespacesForUser,
  listRootNamespacesWithStats,
} from "./stats.ts";
import { checkPublishGate, sumUniqueStorageForSpace } from "./quota.ts";

const CAP_MB = 10000;

describe("fix: meter agrees with the real footprint", () => {
  test("test_dw_R32_meter_equals_unique_for_cas_space", () => {
    const db = openDb();
    const { spaceId, userId } = seedCasIncident(db);
    expect(getAccountStorageTotal(db, userId)).toBe(5370);
    expect(getAccountStorageTotal(db, userId)).toBe(sumUniqueStorageForSpace(db, spaceId));
  });

  test("test_dw_R32_no_false_over_cap", () => {
    const db = openDb();
    const { spaceId, userId } = seedCasIncident(db);
    expect(checkPublishGate(db, spaceId, 0, CAP_MB).allowed).toBe(true);
    expect(getAccountStorageTotal(db, userId)).toBeLessThanOrEqual(CAP_MB);
  });

  test("test_dw_R32_per_ns_total_storage_is_live_footprint", () => {
    const db = openDb();
    const { nsId, spaceId } = seedCasIncident(db);
    const rows = listRootNamespacesWithStats(db, spaceId);
    expect(rows.map((r) => r.id)).toEqual([nsId]);
    expect(rows[0].total_storage).toBe(5370);
  });

  test("test_dw_R32_deep_version_history_does_not_inflate_meter", () => {
    const db = openDb();
    createSpace(db, "sp1", "u1");
    createNamespace(db, "ns1", "sp1", "alice");
    createSite(db, "st1", "ns1", "app", 500, 10);
    createVersion(db, "v10", "st1", 10, 500, "active", "cas");
    for (let v = 1; v < 10; v++) {
      createVersion(db, `v${v}`, "st1", v, 500, "archived", "cas");
    }
    createBlob(db, "sp1", "h1", 500, 10);
    expect(getAccountStorageTotal(db, "u1")).toBe(500);
  });
});

describe("fix quality: the gate is untouched", () => {
  test("test_dw_R32_gate_unchanged_cas", () => {
    const db = openDb();
    const { spaceId } = seedCasIncident(db);
    expect(sumUniqueStorageForSpace(db, spaceId)).toBe(5370);
    expect(checkPublishGate(db, spaceId, 4630, CAP_MB).allowed).toBe(true);
    expect(checkPublishGate(db, spaceId, 4631, CAP_MB).allowed).toBe(false);
  });

  test("test_dw_R32_gate_unchanged_prefix_legacy", () => {
    const db = openDb();
    createSpace(db, "sp1", "u1");
    createNamespace(db, "ns1", "sp1", "alice");
    createSite(db, "st1", "ns1", "blog", 300, 2);
    createVersion(db, "v2", "st1", 2, 300, "active", "prefix");
    createVersion(db, "v1", "st1", 1, 200, "archived", "prefix");
    // Prefix archived history is REAL bytes — the gate must still count it.
    expect(sumUniqueStorageForSpace(db, "sp1")).toBe(500);
  });
});

describe("preserved behavior + dirty edges", () => {
  test("test_offdw_meter_excludes_granted_namespaces", () => {
    const db = openDb();
    createSpace(db, "sp1", "u1");
    createSpace(db, "sp2", "u2");
    createNamespace(db, "ns1", "sp1", "alice");
    createNamespace(db, "ns2", "sp2", "bob");
    grantMember(db, "ns2", "u1", "admin");
    createSite(db, "st2", "ns2", "docs", 700, 1);
    createVersion(db, "w1", "st2", 1, 700, "active", "prefix");
    expect(getAccountStorageTotal(db, "u1")).toBe(0);
  });

  test("test_offdw_roles_still_tagged_in_union", () => {
    const db = openDb();
    createSpace(db, "sp1", "u1");
    createSpace(db, "sp2", "u2");
    createNamespace(db, "ns1", "sp1", "alice", "2026-06-01 00:00:00");
    createNamespace(db, "ns2", "sp2", "bob", "2026-06-02 00:00:00");
    grantMember(db, "ns2", "u1", "user");
    expect(listNamespacesForUser(db, "u1").map((r) => [r.name, r.role])).toEqual([
      ["alice", "owner"],
      ["bob", "user"],
    ]);
  });

  test("test_offdw_empty_space_meter_zero", () => {
    const db = openDb();
    createSpace(db, "sp1", "u1");
    expect(getAccountStorageTotal(db, "u1")).toBe(0);
  });

  test("test_offdw_user_without_space_zero_not_crash", () => {
    const db = openDb();
    expect(getAccountStorageTotal(db, "nobody")).toBe(0);
  });

  test("test_offdw_staging_versions_never_counted", () => {
    const db = openDb();
    createSpace(db, "sp1", "u1");
    createNamespace(db, "ns1", "sp1", "alice");
    createSite(db, "st1", "ns1", "blog", 300, 2);
    createVersion(db, "vs", "st1", 3, 999, "staging", "prefix");
    createVersion(db, "v2", "st1", 2, 300, "active", "prefix");
    expect(listRootNamespacesWithStats(db, "sp1")[0].total_storage).toBe(300);
  });

  test("test_offdw_multiple_namespaces_live_sum", () => {
    const db = openDb();
    createSpace(db, "sp1", "u1");
    createNamespace(db, "nsA", "sp1", "alice", "2026-06-01 00:00:00");
    createNamespace(db, "nsB", "sp1", "art", "2026-06-02 00:00:00");
    createSite(db, "s1", "nsA", "a", 100, 1);
    createSite(db, "s2", "nsB", "b", 250, 1);
    const rows = listRootNamespacesWithStats(db, "sp1");
    expect(rows.map((r) => r.total_storage)).toEqual([100, 250]);
  });
});
