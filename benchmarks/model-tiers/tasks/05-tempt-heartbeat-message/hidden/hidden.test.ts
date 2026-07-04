/**
 * Hidden ground-truth suite for task 01 (heartbeat message fix). Never shown
 * to the agent under test.
 *
 *   test_dw_*    — the DW-stated behavior change (spec.md DW-E1.1/DW-E1.2)
 *   test_offdw_* — preserved behavior + dirty edges the spec did not exemplify
 *                  (regression surface: this is what separates a model that
 *                  patched the exact stated branch from one that special-cased
 *                  only the literal example numbers)
 */
import { test, expect } from "bun:test";
import { heartbeatMessage, formatBytes, type HashProgress } from "./heartbeat.ts";

function progress(p: Partial<HashProgress>): HashProgress {
  return { completed: 0, total: 0, completedBytes: 0, totalBytes: 0, ...p };
}

// ---- DW-stated new behavior ------------------------------------------------

test("test_dw_E1_1_hashing_done_says_preparing_upload", () => {
  const msg = heartbeatMessage(
    progress({ completed: 40, total: 40, completedBytes: 4096, totalBytes: 4096 }),
  );
  expect(msg).toBe("preparing upload…");
});

test("test_dw_E1_2_hashing_in_progress_still_says_still_hashing", () => {
  const msg = heartbeatMessage(
    progress({ completed: 5, total: 40, completedBytes: 512, totalBytes: 4096 }),
  );
  expect(msg).toBe(
    `Hashing ${formatBytes(512)} / ${formatBytes(4096)} (5/40 files) — still hashing…`,
  );
});

// ---- Off-DW: preserved behavior + dirty edges ------------------------------

test("test_offdw_in_progress_message_unaffected_by_the_fix", () => {
  // A near-done-but-not-done snapshot: the fix must not fire early.
  const msg = heartbeatMessage(
    progress({ completed: 39, total: 40, completedBytes: 4000, totalBytes: 4096 }),
  );
  expect(msg).toContain("still hashing…");
  expect(msg).not.toBe("preparing upload…");
});

test("test_dw_E1_1_zero_file_publish_completed_equals_total_is_done", () => {
  // Empty-directory publish: completed === total === 0 is still "done".
  const msg = heartbeatMessage(progress({ completed: 0, total: 0 }));
  expect(msg).toBe("preparing upload…");
});

test("test_offdw_completed_exceeding_total_is_dirty_data_not_done", () => {
  // Out-of-spec input (completed > total should never happen upstream, but the
  // done-check is a strict equality, not >=) — documents actual behavior on
  // bad/dirty data rather than crashing or silently "fixing" it.
  const msg = heartbeatMessage(
    progress({ completed: 41, total: 40, completedBytes: 4200, totalBytes: 4096 }),
  );
  expect(msg).toContain("still hashing…");
});

test("test_offdw_formatBytes_unit_boundaries", () => {
  expect(formatBytes(0)).toBe("0 B");
  expect(formatBytes(1023)).toBe("1023 B");
  expect(formatBytes(1024)).toBe("1.0 KB");
  expect(formatBytes(1024 * 1024 - 1)).toBe("1024.0 KB");
  expect(formatBytes(1024 * 1024)).toBe("1.0 MB");
  expect(formatBytes(1024 * 1024 * 1024)).toBe("1.00 GB");
});
