/**
 * Hidden report gate for 04-loop-core-review.
 *
 * Structural check only — the reviewer's `outputs/report.md` is merged into
 * this directory before the run. Whether the findings are CORRECT is graded by
 * the judge panel against answer-key.json (Phase 3); this gate only verifies a
 * review artifact of the required shape exists.
 */
import { describe, expect, test } from "bun:test";
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";

const REPORT = join(import.meta.dir, "report.md");

describe("review report artifact", () => {
  test("test_dw_report_exists_and_is_substantial", () => {
    expect(existsSync(REPORT)).toBe(true);
    expect(readFileSync(REPORT, "utf-8").length).toBeGreaterThan(400);
  });

  test("test_dw_report_has_overall_verdict", () => {
    const text = readFileSync(REPORT, "utf-8");
    expect(/OVERALL:\s*(PASS|FAIL)/.test(text)).toBe(true);
  });

  test("test_dw_report_covers_every_dw_item_with_a_verdict", () => {
    const text = readFileSync(REPORT, "utf-8");
    for (const id of ["DW-1.1", "DW-1.2", "DW-1.3", "DW-1.4"]) {
      expect(text.includes(id)).toBe(true);
    }
    expect(/VERDICT/.test(text)).toBe(true);
  });

  test("test_offdw_report_has_issues_section", () => {
    const text = readFileSync(REPORT, "utf-8");
    expect(/##\s*Issues/i.test(text)).toBe(true);
  });
});
