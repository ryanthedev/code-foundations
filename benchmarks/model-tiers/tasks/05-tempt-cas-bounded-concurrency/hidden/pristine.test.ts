/**
 * Pristine-starter check (DW-1.2, second clause — SCHEMA.md "Pristine-starter
 * check"). Imports ONLY the symbols the starter already exports
 * (`computeCasDiff`, `verifyNeededBlobs`) — proves the untouched starter
 * already makes the CORRECT decisions (just slowly / riskily). Run against
 * the pristine starter, never against outputs/.
 */
import { test, expect } from "bun:test";
import { computeCasDiff } from "./manifest-diff.ts";
import { verifyNeededBlobs, type R2Client } from "./cas-publish.ts";

test("test_offdw_pristine_computeCasDiff_table_and_r2_hit_is_have", async () => {
  const result = await computeCasDiff(
    { "a.txt": { hash: "h1", size: 10 } },
    new Set(["h1"]),
    async () => true,
  );
  expect(result.needed).toEqual([]);
});

test("test_offdw_pristine_computeCasDiff_table_miss_r2_miss_is_needed", async () => {
  const result = await computeCasDiff(
    { "a.txt": { hash: "h1", size: 10 } },
    new Set(),
    async () => false,
  );
  expect(result.needed).toEqual([{ hash: "h1", path: "a.txt", size: 10 }]);
});

test("test_offdw_pristine_computeCasDiff_duplicate_hash_collapses_to_first_path", async () => {
  const result = await computeCasDiff(
    {
      "b.txt": { hash: "shared", size: 5 },
      "a.txt": { hash: "shared", size: 5 },
    },
    new Set(),
    async () => false,
  );
  expect(result.needed.length).toBe(1);
  expect(result.needed[0].path).toBe("b.txt"); // first-seen (object key order)
});

test("test_offdw_pristine_verifyNeededBlobs_ok_when_all_verified", async () => {
  const r2: R2Client = { headObject: async (key) => ({ etag: key.split("/").pop()!, size: 42 }) };
  const result = await verifyNeededBlobs(r2, "space1", [{ hash: "h1", path: "a.txt", size: 42 }]);
  expect(result.ok).toBe(true);
});

test("test_offdw_pristine_verifyNeededBlobs_mismatched_etag", async () => {
  const r2: R2Client = { headObject: async () => ({ etag: "wrong", size: 1 }) };
  const result = await verifyNeededBlobs(r2, "space1", [{ hash: "h1", path: "a.txt", size: 1 }]);
  expect(result.ok).toBe(false);
  if (!result.ok) expect(result.mismatched).toEqual(["a.txt"]);
});
