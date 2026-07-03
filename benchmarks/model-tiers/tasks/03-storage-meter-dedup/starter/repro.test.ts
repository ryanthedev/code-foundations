/**
 * FAILING REPRO — the bug this task is about.
 *
 * Live incident: a pro user (10 GB cap) publishes a large CAS site. The
 * publish SUCCEEDS — the gate sees 5370 MB of real, deduplicated bytes — but
 * the settings meter shows "10740 MB / 10000 MB", a false over-cap warning,
 * because it also counts the archived deduplicated version as if its bytes
 * were stored again.
 *
 * Run: bun test repro.test.ts   (expected: FAILS on this starter)
 */
import { describe, expect, test } from "bun:test";
import { openDb, seedCasIncident } from "./fixtures.ts";
import { getAccountStorageTotal } from "./stats.ts";
import { checkPublishGate, sumUniqueStorageForSpace } from "./quota.ts";

const CAP_MB = 10000;

describe("repro: settings meter must agree with the real storage footprint", () => {
  test("meter equals the gate's deduplicated footprint", () => {
    const db = openDb();
    const { spaceId, userId } = seedCasIncident(db);
    expect(getAccountStorageTotal(db, userId)).toBe(sumUniqueStorageForSpace(db, spaceId));
  });

  test("no false over-cap: a user the gate admits is not shown as over cap", () => {
    const db = openDb();
    const { spaceId, userId } = seedCasIncident(db);
    const gate = checkPublishGate(db, spaceId, 0, CAP_MB);
    expect(gate.allowed).toBe(true); // (control) the gate is correct
    expect(getAccountStorageTotal(db, userId)).toBeLessThanOrEqual(CAP_MB);
  });
});
