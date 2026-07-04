import { test, expect } from "bun:test";
import { normalize } from "./util";

test("test_repro_trims_and_uppercases", () => {
  expect(normalize("  hi  ")).toBe("HI");
});
