import { test, expect } from "bun:test";
import { double } from "./a";
import { triple } from "./b";

test("test_dw_1_doubles", () => {
  expect(double(4)).toBe(8);
});

test("test_dw_2_triples", () => {
  expect(triple(4)).toBe(12);
});

test("test_offdw_1_doubles_zero", () => {
  expect(double(0)).toBe(0);
});
