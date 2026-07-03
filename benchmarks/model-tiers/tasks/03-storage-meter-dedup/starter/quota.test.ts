/**
 * Publish-gate accounting tests. This function is verified against production
 * and pins the AUTHORITATIVE storage numbers the meter should agree with.
 */
import { describe, expect, test } from "bun:test";
import {
  createBlob,
  createNamespace,
  createSite,
  createSpace,
  createVersion,
  openDb,
  seedCasIncident,
} from "./fixtures.ts";
import { checkPublishGate, sumUniqueStorageForSpace } from "./quota.ts";

describe("sumUniqueStorageForSpace", () => {
  test("CAS space counts deduplicated blob bytes once", () => {
    const db = openDb();
    const { spaceId } = seedCasIncident(db);
    expect(sumUniqueStorageForSpace(db, spaceId)).toBe(5370);
  });

  test("prefix legacy space counts live plus archived bytes (no dedup exists there)", () => {
    const db = openDb();
    createSpace(db, "sp1", "u1");
    createNamespace(db, "ns1", "sp1", "alice");
    createSite(db, "st1", "ns1", "blog", 300, 2);
    createVersion(db, "v2", "st1", 2, 300, "active", "prefix");
    createVersion(db, "v1", "st1", 1, 200, "archived", "prefix");
    expect(sumUniqueStorageForSpace(db, "sp1")).toBe(500);
  });

  test("mixed space: CAS blobs + non-CAS live + prefix archived", () => {
    const db = openDb();
    createSpace(db, "sp1", "u1");
    createNamespace(db, "ns1", "sp1", "alice");
    // CAS site
    createSite(db, "st1", "ns1", "app", 1000, 3);
    createVersion(db, "v3", "st1", 3, 1000, "active", "cas");
    createBlob(db, "sp1", "h1", 1000, 1);
    // prefix site with archived history
    createSite(db, "st2", "ns1", "blog", 300, 2);
    createVersion(db, "w2", "st2", 2, 300, "active", "prefix");
    createVersion(db, "w1", "st2", 1, 200, "archived", "prefix");
    expect(sumUniqueStorageForSpace(db, "sp1")).toBe(1500);
  });

  test("empty space is zero", () => {
    const db = openDb();
    createSpace(db, "sp1", "u1");
    expect(sumUniqueStorageForSpace(db, "sp1")).toBe(0);
  });
});

describe("checkPublishGate", () => {
  test("admits a publish that fits under the cap", () => {
    const db = openDb();
    const { spaceId } = seedCasIncident(db);
    const gate = checkPublishGate(db, spaceId, 1000, 10000);
    expect(gate.allowed).toBe(true);
    expect(gate.used).toBe(5370);
  });

  test("blocks a publish that would exceed the cap", () => {
    const db = openDb();
    const { spaceId } = seedCasIncident(db);
    expect(checkPublishGate(db, spaceId, 4631, 10000).allowed).toBe(false);
    expect(checkPublishGate(db, spaceId, 4630, 10000).allowed).toBe(true);
  });
});
