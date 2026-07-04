/**
 * File enumeration + hashing core for the publish flow.
 *
 * Split by knowledge: `listFiles` owns the enumeration rules (default
 * exclusions + .upublishignore, stat-only); `hashFiles` owns hashing,
 * byte-weighted progress, and event-loop yielding; `collectFilesWithHashes`
 * is the preserved synchronous composition of the two.
 *
 * Seams:
 *   listFiles              — stat-only walk applying the exclusion rules
 *   hashFiles              — async hasher: progress reports + event-loop yields
 *   collectFilesWithHashes — sync collect (signature/contract preserved)
 *   parseIgnoreFile        — .upublishignore line rules
 */

import { createHash } from "node:crypto";
import {
  closeSync,
  existsSync,
  openSync,
  readdirSync,
  readFileSync,
  readSync,
  statSync,
} from "node:fs";
import { join, relative } from "node:path";

// ─── Progress + result shapes ───────────────────────────────────────────────

/**
 * Hashing progress snapshot reported during the hashing phase (before any
 * upload). `completed`/`total` count files and `completedBytes`/`totalBytes`
 * count the raw bytes of those files. Both pairs are cumulative and
 * monotonically non-decreasing, reaching their totals on the final report.
 *
 * `completedBytes` and the final `totalBytes` are AUTHORITATIVE — they are the
 * bytes actually streamed through the hash, not a `statSync` size (no TOCTOU).
 * The opening report is `{ completed: 0, total, completedBytes: 0, totalBytes }`
 * — totals are already known (enumeration ran first), so for a non-empty
 * directory a percentage needs no divide-by-zero guard (the all-empty
 * `totalBytes === 0` case still needs a file-count fallback downstream).
 */
export interface HashProgress {
  /** Files hashed so far (cumulative). Starts at 0, ends at `total`. */
  completed: number;
  /** Total files to hash. */
  total: number;
  /** Bytes hashed so far (cumulative, from streamed content — not stat). */
  completedBytes: number;
  /** Total bytes to hash (sum of every file's hashed-byte count). */
  totalBytes: number;
}

/**
 * One enumerated file. `size` here is the DENOMINATOR ESTIMATE for a hashing
 * progress bar (statSync); the AUTHORITATIVE byte count is the size returned
 * later by the hash (the bytes actually streamed).
 */
export interface FileEntry {
  /** Path relative to the walk root (the map key in the hashed result). */
  relPath: string;
  /** Absolute path to the file on disk. */
  fullPath: string;
  /** `statSync` byte size — denominator estimate only, not the hashed size. */
  size: number;
}

/** Result of enumerating a directory with {@link listFiles} (no hashing). */
export interface ListFilesResult {
  /** Publishable files in walk order, each with its stat size. */
  files: FileEntry[];
  /** Files/directories excluded by default rules or .upublishignore. */
  excluded: string[];
  /** Suspicious files included that may not be site content. */
  warnings: string[];
}

/** One collected file: its MD5 digest, byte size, and absolute path on disk. */
export interface CollectedFile {
  /** MD5 hex digest of the file's bytes (matches the R2 ETag for single-part uploads). */
  hash: string;
  /** Byte size of the file, counted while hashing (no separate stat). */
  size: number;
  /** Absolute path to the file on disk. */
  fullPath: string;
}

/** Result of collecting files with MD5 hashes. */
export interface CollectWithHashesResult {
  files: Record<string, CollectedFile>;
  excluded: string[];
  warnings: string[];
}

// ─── .upublishignore ─────────────────────────────────────────────────────────

/** Parses .upublishignore content: one pattern per line, `#` comments, blanks skipped. */
export function parseIgnoreFile(content: string): string[] {
  return content
    .split("\n")
    .map((l) => l.trim())
    .filter((l) => l && !l.startsWith("#"));
}

/**
 * Pattern semantics: exact name match, `dir/` matches a directory of that
 * name, `*.ext` matches a filename suffix.
 */
function matchesIgnore(relPath: string, name: string, patterns: string[]): boolean {
  for (const p of patterns) {
    if (p === name) return true;
    if (p.startsWith("*.") && name.endsWith(p.slice(1))) return true;
  }
  return false;
}

// ─── Exclusion / warning rules ───────────────────────────────────────────────

const EXCLUDED_DIRS = new Set([".git", "node_modules", ".svn", ".hg"]);
const EXCLUDED_FILES = new Set([".DS_Store", "Thumbs.db", ".upublishignore"]);

function isDefaultExcluded(name: string, isDir: boolean): boolean {
  if (isDir) return EXCLUDED_DIRS.has(name);
  if (EXCLUDED_FILES.has(name)) return true;
  if (name === ".env" || name.startsWith(".env.")) return true;
  if (name.endsWith(".pem") || name.endsWith(".key")) return true;
  return false;
}

const SUSPICIOUS_NAMES = new Set([
  "nginx.conf",
  "apache.conf",
  ".htaccess",
  "Makefile",
  "Dockerfile",
  "docker-compose.yml",
  "docker-compose.yaml",
  "package.json",
  "package-lock.json",
  "bun.lockb",
  "yarn.lock",
  "pnpm-lock.yaml",
  "tsconfig.json",
  "README.md",
  "CHANGELOG.md",
  "LICENSE",
]);

function isSuspicious(name: string): boolean {
  if (SUSPICIOUS_NAMES.has(name)) return true;
  if (name.endsWith(".sh")) return true;
  return false;
}

// ─── Hashing primitives ──────────────────────────────────────────────────────

/**
 * Chunk size for streamed file hashing. Bounds collection memory: a file is
 * never read whole into memory — it is hashed through a single reused buffer
 * of this size, regardless of file size.
 */
const HASH_CHUNK_BYTES = 64 * 1024;

/**
 * Bytes hashed between mid-file event-loop yields in the async hasher. A large
 * file would otherwise block the loop for its entire hash with no yield,
 * freezing any queued progress notifications.
 */
const HASH_YIELD_BYTES = 4 * 1024 * 1024;

/** Awaits a macrotask, draining the event loop so queued I/O (e.g. a pending
 * progress notification send) can run. */
const yieldToEventLoop = (): Promise<void> => Promise.resolve();

/**
 * Computes a file's MD5 digest by streaming it through a fixed-size buffer
 * with chunked synchronous reads. The byte count is accumulated during the
 * read, so `size` reflects exactly the bytes hashed (no separate stat / TOCTOU
 * race). The fd is closed in a `finally` so a read error never leaks it.
 */
function hashFileChunked(fullPath: string): { hash: string; size: number } {
  const fd = openSync(fullPath, "r");
  try {
    const md5 = createHash("md5");
    const buffer = Buffer.allocUnsafe(HASH_CHUNK_BYTES);
    let size = 0;
    let bytesRead: number;
    while ((bytesRead = readSync(fd, buffer, 0, HASH_CHUNK_BYTES, null)) > 0) {
      md5.update(buffer.subarray(0, bytesRead));
      size += bytesRead;
    }
    return { hash: md5.digest("hex"), size };
  } finally {
    closeSync(fd);
  }
}

/**
 * Async sibling of {@link hashFileChunked}: same bounded-buffer chunked-read
 * loop, but it yields whenever `yieldEvery` bytes have been hashed since the
 * last yield, so a single multi-hundred-MB file does not block the event loop
 * for its whole hash. The byte budget is carried IN and OUT so the yield
 * cadence is global across a multi-file run.
 */
async function hashFileChunkedYielding(
  fullPath: string,
  yieldEvery: number,
  bytesSinceYield: number,
): Promise<{ hash: string; size: number; bytesSinceYield: number }> {
  const fd = openSync(fullPath, "r");
  try {
    const md5 = createHash("md5");
    const buffer = Buffer.allocUnsafe(HASH_CHUNK_BYTES);
    let size = 0;
    let sinceYield = bytesSinceYield;
    let bytesRead: number;
    while ((bytesRead = readSync(fd, buffer, 0, HASH_CHUNK_BYTES, null)) > 0) {
      md5.update(buffer.subarray(0, bytesRead));
      size += bytesRead;
      sinceYield += bytesRead;
      if (sinceYield >= yieldEvery) {
        // Mid-file yield — release the loop so a pending notification flushes.
        await yieldToEventLoop();
        sinceYield = 0;
      }
    }
    return { hash: md5.digest("hex"), size, bytesSinceYield: sinceYield };
  } finally {
    closeSync(fd);
  }
}

// ─── Enumeration ─────────────────────────────────────────────────────────────

/**
 * Recursively walks `currentDir`, applying the default + .upublishignore
 * exclusion rules and flagging suspicious files. STAT-ONLY — it never opens or
 * reads file content; each kept file's `size` is its `statSync` size.
 */
function walkFiles(
  rootDir: string,
  currentDir: string,
  result: ListFilesResult,
  ignorePatterns: string[],
): void {
  const entries = readdirSync(currentDir, { withFileTypes: true });

  for (const entry of entries) {
    const fullPath = join(currentDir, entry.name);
    const relPath = relative(rootDir, fullPath);

    if (isDefaultExcluded(entry.name, entry.isDirectory())) {
      result.excluded.push(entry.isDirectory() ? `${relPath}/` : relPath);
      continue;
    }

    if (matchesIgnore(relPath, entry.name, ignorePatterns)) {
      result.excluded.push(entry.isDirectory() ? `${relPath}/` : relPath);
      continue;
    }

    if (entry.isDirectory()) {
      walkFiles(rootDir, fullPath, result, ignorePatterns);
    } else if (entry.isFile()) {
      if (isSuspicious(entry.name)) {
        result.warnings.push(relPath);
      }
      // stat-only: record where the file is and its size — no content is read.
      result.files.push({ relPath, fullPath, size: statSync(fullPath).size });
    }
  }
}

/**
 * Enumerates the publishable files under `dirPath` — applying the default and
 * .upublishignore exclusion rules and flagging suspicious files — WITHOUT
 * reading any file's content. This is the stat-only enumeration primitive both
 * hashing paths build on.
 */
export function listFiles(dirPath: string): ListFilesResult {
  let ignorePatterns: string[] = [];
  const ignoreFile = join(dirPath, ".upublishignore");
  try {
    if (existsSync(ignoreFile)) {
      ignorePatterns = parseIgnoreFile(readFileSync(ignoreFile, "utf-8"));
    }
  } catch {
    // No readable .upublishignore — use defaults only
  }

  const result: ListFilesResult = { files: [], excluded: [], warnings: [] };
  walkFiles(dirPath, dirPath, result, ignorePatterns);
  return result;
}

// ─── Async, progress-instrumented hashing ────────────────────────────────────

/**
 * Hashes an enumerated file list (from {@link listFiles}), reporting
 * byte-weighted progress as it goes, and yielding to the event loop during the
 * work so queued notifications can flush. Yields MID-FILE once `yieldEvery`
 * bytes have streamed AND at every file boundary.
 *
 * `onHashProgress` (if supplied) fires with everything at zero before any file
 * is hashed — totals come from the list's stat sizes — then after each file
 * completes with cumulative counts. The counts are monotonically
 * non-decreasing; the final report's `totalBytes` equals the cumulative hashed
 * sum, so `completedBytes === totalBytes` holds exactly even if a file's
 * on-disk size changed between the stat and the hash. An EMPTY list fires no
 * progress at all.
 *
 * `onHashProgress` must be synchronous and non-throwing (it is called
 * directly); a throw propagates out.
 */
export async function hashFiles(
  list: FileEntry[],
  opts?: {
    onHashProgress?: (progress: HashProgress) => void;
    yieldEvery?: number;
  },
): Promise<Record<string, CollectedFile>> {
  const files: Record<string, CollectedFile> = {};

  // Empty list: fire nothing (mirrors the uploader's empty short-circuit).
  if (list.length === 0) return files;

  const onHashProgress = opts?.onHashProgress;
  const yieldEvery = opts?.yieldEvery ?? HASH_YIELD_BYTES;

  const total = list.length;
  // statSync denominator estimate; the final report pins totals to real sums.
  const statTotalBytes = list.reduce((sum, e) => sum + e.size, 0);

  let completed = 0;
  let completedBytes = 0;
  // Carried across files so the mid-file yield cadence is global.
  let bytesSinceYield = 0;

  for (let i = 0; i < total; i++) {
    const entry = list[i];
    const hashed = await hashFileChunkedYielding(entry.fullPath, yieldEvery, bytesSinceYield);
    files[entry.relPath] = { hash: hashed.hash, size: hashed.size, fullPath: entry.fullPath };
    bytesSinceYield = hashed.bytesSinceYield;

    completed += 1;
    completedBytes += entry.size;
    const isLast = i === total - 1;
    // On the final file, pin totalBytes to the cumulative sum so the closing
    // report hits completedBytes === totalBytes exactly; before that, report
    // the stat estimate as the denominator.
    onHashProgress?.({
      completed,
      total,
      completedBytes,
      totalBytes: isLast ? completedBytes : statTotalBytes,
    });

    // Guarantee a yield at every file boundary (except after the very last
    // file — nothing remains to overlap). Reset the budget so the next file
    // starts a fresh mid-file cadence.
    if (!isLast && bytesSinceYield > 0) {
      await yieldToEventLoop();
      bytesSinceYield = 0;
    }
  }

  return files;
}

// ─── Synchronous collect (preserved contract) ────────────────────────────────

/**
 * Recursively collects files from a directory, applying exclusion rules, and
 * computes an MD5 hash for each file. Re-expressed as {@link listFiles} plus a
 * synchronous hash loop — the signature and return contract are unchanged and
 * it stays SYNCHRONOUS (returns a non-Promise). The async,
 * progress-instrumented path is {@link hashFiles}.
 */
export function collectFilesWithHashes(dirPath: string): CollectWithHashesResult {
  const { files: list, excluded, warnings } = listFiles(dirPath);

  const files: Record<string, CollectedFile> = {};
  for (const entry of list) {
    const { hash, size } = hashFileChunked(entry.fullPath);
    files[entry.relPath] = { hash, size, fullPath: entry.fullPath };
  }

  return { files, excluded, warnings };
}
