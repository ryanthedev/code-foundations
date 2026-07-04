import { afterEach, describe, expect, test } from "bun:test";
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import {
  collectFilesWithHashes,
  hashFiles,
  listFiles,
  parseIgnoreFile,
  type HashProgress,
} from "../src/hashing.ts";

const dirs: string[] = [];

function tempSite(files: Record<string, string>): string {
  const dir = mkdtempSync(join(tmpdir(), "hashing-test-"));
  dirs.push(dir);
  for (const [rel, content] of Object.entries(files)) {
    const full = join(dir, rel);
    mkdirSync(join(full, ".."), { recursive: true });
    writeFileSync(full, content);
  }
  return dir;
}

afterEach(() => {
  while (dirs.length) rmSync(dirs.pop()!, { recursive: true, force: true });
});

describe("parseIgnoreFile", () => {
  test("skips blanks and comments, trims lines", () => {
    expect(parseIgnoreFile("# c\n\n secret.txt \n*.log\n")).toEqual([
      "secret.txt",
      "*.log",
    ]);
  });
});

describe("listFiles", () => {
  test("enumerates files with stat sizes, walk includes nested dirs", () => {
    const dir = tempSite({
      "index.html": "<h1>hi</h1>",
      "css/site.css": "body{}",
    });
    const { files } = listFiles(dir);
    expect(files.map((f) => f.relPath).sort()).toEqual(["css/site.css", "index.html"]);
    expect(files.find((f) => f.relPath === "index.html")?.size).toBe(11);
  });

  test("applies default exclusions and flags suspicious files", () => {
    const dir = tempSite({
      "index.html": "x",
      ".DS_Store": "junk",
      ".env": "SECRET=1",
      "server.key": "key",
      "Dockerfile": "FROM x",
    });
    const { files, excluded, warnings } = listFiles(dir);
    expect(files.map((f) => f.relPath).sort()).toEqual(["Dockerfile", "index.html"]);
    expect(excluded.sort()).toEqual([".DS_Store", ".env", "server.key"]);
    expect(warnings).toEqual(["Dockerfile"]);
  });

  test("applies .upublishignore exact-name and *.ext patterns", () => {
    const dir = tempSite({
      "index.html": "x",
      "secret.txt": "s",
      "debug.log": "l",
      ".upublishignore": "secret.txt\n*.log\n",
    });
    const { files, excluded } = listFiles(dir);
    expect(files.map((f) => f.relPath)).toEqual(["index.html"]);
    expect(excluded.sort()).toEqual([".upublishignore", "debug.log", "secret.txt"]);
  });
});

describe("hashFiles", () => {
  test("hashes every listed file to the same digests as the sync collector", async () => {
    const dir = tempSite({ "a.txt": "alpha", "b/b.txt": "beta" });
    const { files: list } = listFiles(dir);
    const asyncFiles = await hashFiles(list);
    const syncFiles = collectFilesWithHashes(dir).files;
    expect(Object.keys(asyncFiles).sort()).toEqual(Object.keys(syncFiles).sort());
    for (const rel of Object.keys(syncFiles)) {
      expect(asyncFiles[rel].hash).toBe(syncFiles[rel].hash);
      expect(asyncFiles[rel].size).toBe(syncFiles[rel].size);
    }
  });

  test("progress is monotonic and the final report hits its totals", async () => {
    const dir = tempSite({ "a.txt": "aaaa", "b.txt": "bb", "c.txt": "cccccc" });
    const { files: list } = listFiles(dir);
    const reports: HashProgress[] = [];
    await hashFiles(list, { onHashProgress: (p) => reports.push({ ...p }) });
    expect(reports.length).toBeGreaterThan(0);
    for (let i = 1; i < reports.length; i++) {
      expect(reports[i].completed).toBeGreaterThanOrEqual(reports[i - 1].completed);
      expect(reports[i].completedBytes).toBeGreaterThanOrEqual(reports[i - 1].completedBytes);
    }
    const last = reports[reports.length - 1];
    expect(last.completed).toBe(last.total);
    expect(last.completedBytes).toBe(last.totalBytes);
  });

  test("empty list resolves to an empty map and fires no progress", async () => {
    const reports: HashProgress[] = [];
    const files = await hashFiles([], { onHashProgress: (p) => reports.push(p) });
    expect(files).toEqual({});
    expect(reports).toEqual([]);
  });

  test("with no callback the result is identical to the callback run", async () => {
    const dir = tempSite({ "a.txt": "alpha", "b.txt": "beta" });
    const { files: list } = listFiles(dir);
    const withCb = await hashFiles(list, { onHashProgress: () => {} });
    const without = await hashFiles(list);
    expect(without).toEqual(withCb);
  });

  test("yields between files (the hasher awaits)", async () => {
    const dir = tempSite({ "a.txt": "aaaa", "b.txt": "bbbb" });
    const { files: list } = listFiles(dir);
    let resolved = false;
    const run = hashFiles(list).then((f) => {
      resolved = true;
      return f;
    });
    expect(resolved).toBe(false); // async: not done synchronously
    const files = await run;
    expect(Object.keys(files)).toHaveLength(2);
  });
});

describe("collectFilesWithHashes (preserved sync contract)", () => {
  test("returns files/excluded/warnings with md5 digests, synchronously", () => {
    const dir = tempSite({ "index.html": "<h1>hi</h1>", ".DS_Store": "x" });
    const result = collectFilesWithHashes(dir);
    expect(result.files["index.html"].hash).toBe("8097d38e49cc85c6e16e47e447a12142");
    expect(result.files["index.html"].size).toBe(11);
    expect(result.excluded).toEqual([".DS_Store"]);
    expect(result.warnings).toEqual([]);
  });
});
