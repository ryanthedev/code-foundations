/**
 * Hidden ground-truth suite for task "02-cas-bounded-concurrency". Never
 * shown to the agent under test.
 *
 *   test_dw_*    — behavior a specific DW item (spec.md DW-H2.1..H2.4) states
 *   test_offdw_* — preserved behavior + dirty edges (bad data, empty input,
 *                  error propagation) the spec did not exemplify
 */
import { test, expect } from "bun:test";
import { mapWithConcurrency, CAS_HEAD_CONCURRENCY } from "./concurrency.ts";
import { computeCasDiff } from "./manifest-diff.ts";
import { verifyNeededBlobs, type R2Client } from "./cas-publish.ts";

// ─── DW-H2.1: mapWithConcurrency ────────────────────────────────────────────

test("test_dw_H2_1_preserves_input_order_regardless_of_completion_order", async () => {
  // Item 0 resolves LAST (longest delay) — output order must still be [0,1,2].
  const delays = [30, 10, 0];
  const results = await mapWithConcurrency([0, 1, 2], 3, async (i) => {
    await new Promise((r) => setTimeout(r, delays[i]));
    return i;
  });
  expect(results).toEqual([0, 1, 2]);
});

test("test_dw_H2_1_never_exceeds_limit_in_flight", async () => {
  let inFlight = 0;
  let maxInFlight = 0;
  const items = Array.from({ length: 20 }, (_, i) => i);
  await mapWithConcurrency(items, 4, async (i) => {
    inFlight++;
    maxInFlight = Math.max(maxInFlight, inFlight);
    await new Promise((r) => setTimeout(r, 5));
    inFlight--;
    return i;
  });
  expect(maxInFlight).toBeLessThanOrEqual(4);
  expect(maxInFlight).toBeGreaterThan(1);
});

test("test_dw_H2_1_empty_input_resolves_empty_and_never_calls_fn", async () => {
  let called = false;
  const results = await mapWithConcurrency([], 5, async () => {
    called = true;
    return 1;
  });
  expect(results).toEqual([]);
  expect(called).toBe(false);
});

test("test_dw_H2_1_limit_exceeding_items_length_caps_at_items_length", async () => {
  let concurrent = 0;
  let maxConcurrent = 0;
  const results = await mapWithConcurrency([1, 2, 3], 100, async (i) => {
    concurrent++;
    maxConcurrent = Math.max(maxConcurrent, concurrent);
    await new Promise((r) => setTimeout(r, 1));
    concurrent--;
    return i * 2;
  });
  expect(results).toEqual([2, 4, 6]);
  expect(maxConcurrent).toBeLessThanOrEqual(3);
});

test("test_offdw_mapWithConcurrency_rejection_propagates_not_caught", async () => {
  await expect(
    mapWithConcurrency([1, 2, 3], 2, async (i) => {
      if (i === 2) throw new Error("boom");
      return i;
    }),
  ).rejects.toThrow("boom");
});

test("test_offdw_CAS_HEAD_CONCURRENCY_is_64", () => {
  expect(CAS_HEAD_CONCURRENCY).toBe(64);
});

// ─── DW-H2.2: computeCasDiff uses the helper, decisions unchanged ──────────

test("test_dw_H2_2_decision_table_unchanged_all_four_cases", async () => {
  const manifest = {
    "have.txt": { hash: "have", size: 1 },
    "drift.txt": { hash: "drift", size: 2 },
    "recent.txt": { hash: "recent", size: 3 },
    "needed.txt": { hash: "needednew", size: 4 },
  };
  const existingHashes = new Set(["have", "drift"]);
  const inR2 = new Set(["have", "recent"]);
  const result = await computeCasDiff(manifest, existingHashes, async (h) => inR2.has(h));
  const neededHashes = result.needed.map((b) => b.hash).sort();
  expect(neededHashes).toEqual(["drift", "needednew"]);
});

test("test_dw_H2_2_duplicate_hash_paths_collapse_to_one_needed_entry", async () => {
  const result = await computeCasDiff(
    { "b.txt": { hash: "shared", size: 5 }, "a.txt": { hash: "shared", size: 5 } },
    new Set(),
    async () => false,
  );
  expect(result.needed.length).toBe(1);
  expect(result.needed[0].path).toBe("b.txt");
});

test("test_offdw_computeCasDiff_headBlob_throw_propagates", async () => {
  await expect(
    computeCasDiff(
      { "a.txt": { hash: "h1", size: 1 } },
      new Set(),
      async () => {
        throw new Error("r2 network error");
      },
    ),
  ).rejects.toThrow("r2 network error");
});

test("test_offdw_computeCasDiff_empty_manifest_returns_empty_needed", async () => {
  const result = await computeCasDiff({}, new Set(), async () => true);
  expect(result.needed).toEqual([]);
});

// ─── DW-H2.3: verifyNeededBlobs settled semantics preserved ────────────────

test("test_dw_H2_3_rejected_head_is_missing_not_thrown", async () => {
  const r2: R2Client = {
    headObject: async () => {
      throw new Error("network blip");
    },
  };
  const result = await verifyNeededBlobs(r2, "space1", [{ hash: "h1", path: "a.txt", size: 1 }]);
  expect(result.ok).toBe(false);
  if (!result.ok) expect(result.missing).toEqual(["a.txt"]);
});

test("test_dw_H2_3_null_head_is_missing", async () => {
  const r2: R2Client = { headObject: async () => null };
  const result = await verifyNeededBlobs(r2, "space1", [{ hash: "h1", path: "a.txt", size: 1 }]);
  expect(result.ok).toBe(false);
  if (!result.ok) expect(result.missing).toEqual(["a.txt"]);
});

test("test_dw_H2_3_collects_all_offenders_not_just_first", async () => {
  const r2: R2Client = {
    headObject: async (key) => {
      if (key.endsWith("bad1")) return null;
      if (key.endsWith("bad2")) return { etag: "wrong", size: 1 };
      return { etag: key.split("/").pop()!, size: 1 };
    },
  };
  const result = await verifyNeededBlobs(r2, "space1", [
    { hash: "bad1", path: "p1.txt", size: 1 },
    { hash: "bad2", path: "p2.txt", size: 1 },
    { hash: "ok", path: "p3.txt", size: 1 },
  ]);
  expect(result.ok).toBe(false);
  if (!result.ok) {
    expect(result.missing).toEqual(["p1.txt"]);
    expect(result.mismatched).toEqual(["p2.txt"]);
  }
});

test("test_offdw_verifyNeededBlobs_empty_needed_is_ok_empty_sizes", async () => {
  const r2: R2Client = { headObject: async () => ({ etag: "x", size: 1 }) };
  const result = await verifyNeededBlobs(r2, "space1", []);
  expect(result.ok).toBe(true);
  if (result.ok) expect(result.sizes.size).toBe(0);
});

// ─── DW-H2.4: the regression test the old serial loop fails ───────────────

test("test_dw_H2_4_computeCasDiff_runs_headBlob_bounded_and_parallel", async () => {
  let inFlight = 0;
  let maxInFlight = 0;
  const manifest: Record<string, { hash: string; size: number }> = {};
  for (let i = 0; i < 200; i++) {
    manifest[`file${i}.txt`] = { hash: `hash${i}`, size: 1 };
  }
  await computeCasDiff(manifest, new Set(), async () => {
    inFlight++;
    maxInFlight = Math.max(maxInFlight, inFlight);
    await new Promise((r) => setTimeout(r, 5));
    inFlight--;
    return false;
  });
  // The old serial for-loop gives maxInFlight === 1. Bounded concurrency at
  // cap 64 over 200 items must show real parallelism, capped at 64.
  expect(maxInFlight).toBeGreaterThan(1);
  expect(maxInFlight).toBeLessThanOrEqual(64);
});
