import { test, expect } from "bun:test";
import { add } from "./add";

test("test_dw_1_adds_positive_numbers", () => {
  expect(add(2, 3)).toBe(5);
});

test("test_offdw_1_adds_negative_numbers", () => {
  expect(add(-1, -1)).toBe(-2);
});
