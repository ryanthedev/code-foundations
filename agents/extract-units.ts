#!/usr/bin/env bun
/**
 * extract-units.ts v3.6.9 - AST extraction with diff context
 *
 * Usage:
 *   bun extract-units.ts [--staged | --files file1 file2 | <git-diff-args>]
 *   bun extract-units.ts --status
 */

import { $ } from "bun";

const VERSION = "3.6.9";
console.error(`[extract-units.ts v${VERSION}]`);

// Language config
const LANG_CONFIG: Record<string, { lang: string; rules: string }> = {
  cs: { lang: "csharp", rules: "csharp.yaml" },
  ts: { lang: "typescript", rules: "typescript.yaml" },
  tsx: { lang: "typescript", rules: "typescript.yaml" },
  js: { lang: "typescript", rules: "typescript.yaml" },
  jsx: { lang: "typescript", rules: "typescript.yaml" },
  py: { lang: "python", rules: "python.yaml" },
  go: { lang: "go", rules: "go.yaml" },
  swift: { lang: "swift", rules: "swift.yaml" },
};

const SKIP_EXTENSIONS = new Set([
  "md", "json", "yaml", "yml", "txt", "lock", "toml", "xml", "config",
  "html", "css", "scss", "less", "svg", "png", "jpg", "jpeg", "gif", "ico"
]);

const SKIP_PATTERNS = [
  /-lock\.json$/, /\.lock$/, /\.generated\./, /\.pb\./, /_generated\./,
  /\.min\.js$/, /\.bundle\.js$/, /__snapshots__\//, /\/vendor\//, /\/node_modules\//
];

interface DiffHunk {
  file: string;
  startLine: number;
  endLine: number;
}

interface Unit {
  name: string;
  file: string;
  type: string;
  lines: [number, number];
  is_test: boolean;
  tests_unit: string | null;
  layer: string;
  changeStatus?: string;
  [key: string]: unknown;
}

// Get script directory for rules path
const scriptDir = import.meta.dir;
const rulesDir = `${scriptDir}/sg-rules`;

function getExt(file: string): string {
  return file.split(".").pop() || "";
}

function shouldSkip(file: string): boolean {
  const ext = getExt(file);
  if (SKIP_EXTENSIONS.has(ext)) return true;
  return SKIP_PATTERNS.some(p => p.test(file));
}

function getLangConfig(file: string) {
  const ext = getExt(file);
  return LANG_CONFIG[ext];
}

function isTestFile(file: string): boolean {
  const patterns = [
    /\.test\./, /\.spec\./, /^test_/, /_test\./, /Test\./, /Tests\./,
    /Spec\./, /Specs\./, /__tests__/, /\/tests\//, /\/test\//,
    /\.Tests\./, /\.Test\./
  ];
  return patterns.some(p => p.test(file));
}

function inferLayer(file: string): string {
  if (isTestFile(file)) return "test";
  if (/\/(api|Api|controllers|Controllers|routes|handlers)\//i.test(file)) return "api";
  if (/\/(services|Services|usecases|App)\//i.test(file)) return "service";
  if (/\/(domain|Domain|models|Models|entities|Core)\//i.test(file)) return "domain";
  if (/\/(data|Data|repositories|Repositories|persistence)\//i.test(file)) return "data";
  if (/\/(Adapters|adapters|providers|clients|gateways|external)\//i.test(file)) return "integration";
  if (/\/(infra|infrastructure|Middleware|middleware|Extensions|hosting)\//i.test(file)) return "infra";
  if (/\/(config|Config|Constants|constants)\//i.test(file)) return "config";
  return "unknown";
}

function inferTestsUnit(file: string): string | null {
  const basename = file.split("/").pop() || "";
  const match = basename.match(/^(.+?)(\.test|\.spec|_test|Test|Tests|Spec|Specs)\./);
  return match ? match[1] : null;
}

function mapRuleToType(ruleId: string): string | null {
  const mapping: Record<string, string> = {
    "cs-method": "method", "cs-async-method": "method",
    "cs-class": "class", "cs-record": "class", "cs-enum": "class", "cs-struct": "class",
    "cs-interface": "interface", "cs-delegate": "interface",
    "cs-constructor": "constructor", "cs-property": "property",
    "ts-function": "function", "ts-arrow-const": "function", "ts-arrow-let": "function",
    "ts-method": "method", "ts-class": "class", "ts-interface": "interface",
    "py-function": "function", "py-function-typed": "function", "py-async-function": "function",
    "py-method": "method", "py-method-typed": "method", "py-async-method": "method",
    "py-class": "class", "py-class-with-bases": "class",
    "go-function": "function", "go-method": "method", "go-struct": "class", "go-interface": "interface",
    "swift-function": "function", "swift-class": "class", "swift-struct": "class",
    "swift-protocol": "interface", "swift-init": "constructor",
  };
  for (const [prefix, type] of Object.entries(mapping)) {
    if (ruleId.startsWith(prefix.replace(/-/g, "-"))) return type;
  }
  return null;
}

async function runSg(file: string, rulesFile: string): Promise<any[]> {
  try {
    const result = await $`sg scan --rule ${rulesFile} ${file} --json`.quiet();
    return JSON.parse(result.stdout.toString());
  } catch {
    return [];
  }
}

async function extractUnits(file: string): Promise<Unit[]> {
  const config = getLangConfig(file);
  if (!config) return [];

  const rulesFile = `${rulesDir}/${config.rules}`;
  const matches = await runSg(file, rulesFile);

  const units: Unit[] = [];
  const is_test = isTestFile(file);
  const layer = inferLayer(file);
  const tests_unit = is_test ? inferTestsUnit(file) : null;

  for (const match of matches) {
    if (!match.ruleId) continue;
    const type = mapRuleToType(match.ruleId);
    if (!type) continue;

    const startLine = (match.range?.start?.line ?? 0) + 1;
    const endLine = (match.range?.end?.line ?? 0) + 1;
    const text = match.text || "";

    // Extract name from metaVariables or text
    let name = match.metaVariables?.single?.NAME?.text
      || match.metaVariables?.NAME?.text
      || "";
    if (!name) {
      const nameMatch = text.match(/(?:function|class|def|func|struct|interface|enum)\s+([a-zA-Z_][a-zA-Z0-9_]*)/);
      name = nameMatch?.[1] || text.split("\n")[0].match(/\b([a-zA-Z_][a-zA-Z0-9_]*)\s*[(<{]/)?.[1] || "unknown";
    }

    // Extract params and return type
    const params = match.metaVariables?.single?.PARAMS?.text || match.metaVariables?.PARAMS?.text || "";
    const returnType = match.metaVariables?.single?.RET?.text || match.metaVariables?.RET?.text || null;

    // Detect patterns in code
    // Require opening paren to avoid matching "for" in comments like "is for retrieving"
    const hasLoops = /\b(for|while|foreach)\s*\(/.test(text);
    const hasAsync = /\b(async|await)\b/.test(text);
    const hasTryCatch = /\b(try\s*{|try:)/.test(text);
    const hasThrow = /\b(throw|raise|panic)\b/.test(text);

    // Extract visibility
    let visibility: string | null = null;
    if (/\bpublic\b/.test(text)) visibility = "public";
    else if (/\bprivate\b/.test(text)) visibility = "private";
    else if (/\bprotected\b/.test(text)) visibility = "protected";
    else if (/\binternal\b/.test(text)) visibility = "internal";

    units.push({
      name,
      file,
      type,
      lines: [startLine, endLine],
      is_test,
      tests_unit,
      layer,
      params,
      param_count: params ? (params.match(/,/g)?.length ?? 0) + (params.trim() ? 1 : 0) : 0,
      return_type: returnType,
      has_loops: hasLoops,
      has_async: hasAsync,
      has_try_catch: hasTryCatch,
      has_throw: hasThrow,
      line_count: endLine - startLine + 1,
      visibility,
    });
  }

  // Dedupe by name+startLine (overlapping rules like cs-method/cs-async-method)
  const seen = new Set<string>();
  return units.filter(u => {
    const key = `${u.name}:${u.lines[0]}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

async function parseDiffRanges(gitArgs: string[]): Promise<DiffHunk[]> {
  try {
    const result = await $`git diff -U0 ${gitArgs}`.quiet();
    const output = result.stdout.toString();

    const hunks: DiffHunk[] = [];
    let currentFile = "";

    for (const line of output.split("\n")) {
      const fileMatch = line.match(/^diff --git.*\sb\/(.+)$/);
      if (fileMatch) {
        currentFile = fileMatch[1];
        continue;
      }

      const hunkMatch = line.match(/^@@.*\+(\d+)(?:,(\d+))?\s*@@/);
      if (hunkMatch && currentFile) {
        const start = parseInt(hunkMatch[1]);
        const count = parseInt(hunkMatch[2] || "1");
        if (count > 0) {
          hunks.push({ file: currentFile, startLine: start, endLine: start + count - 1 });
        }
      }
    }

    return hunks;
  } catch {
    return [];
  }
}

async function getFileStatuses(gitArgs: string[]): Promise<Map<string, string>> {
  try {
    const result = await $`git diff --name-status ${gitArgs}`.quiet();
    const map = new Map<string, string>();

    for (const line of result.stdout.toString().split("\n")) {
      const [status, file] = line.split("\t");
      if (file) {
        map.set(file, status === "A" ? "added" : status === "D" ? "deleted" : "modified");
      }
    }

    return map;
  } catch {
    return new Map();
  }
}

function overlaps(a: [number, number], b: { startLine: number; endLine: number }): boolean {
  return a[0] <= b.endLine && a[1] >= b.startLine;
}

async function main() {
  const args = process.argv.slice(2);

  // Status check
  if (args[0] === "--status") {
    try {
      const result = await $`sg --version`.quiet();
      console.log(JSON.stringify({ sg_available: true, version: result.stdout.toString().trim() }));
    } catch {
      console.log(JSON.stringify({ sg_available: false, error: "ast-grep not installed" }));
    }
    return;
  }

  // Files mode
  if (args[0] === "--files") {
    const files = args.slice(1).filter(f => !shouldSkip(f) && getLangConfig(f));
    for (const file of files) {
      const units = await extractUnits(file);
      for (const unit of units) {
        console.log(JSON.stringify(unit));
      }
    }
    return;
  }

  // Diff mode
  const gitArgs = args.length ? args : [];
  const [hunks, fileStatuses] = await Promise.all([
    parseDiffRanges(gitArgs),
    getFileStatuses(gitArgs),
  ]);

  // Group hunks by file
  const hunksByFile = new Map<string, DiffHunk[]>();
  for (const hunk of hunks) {
    const list = hunksByFile.get(hunk.file) || [];
    list.push(hunk);
    hunksByFile.set(hunk.file, list);
  }

  // Process each file
  for (const [file, status] of fileStatuses) {
    if (shouldSkip(file) || !getLangConfig(file)) continue;

    const fileHunks = hunksByFile.get(file);
    if (!fileHunks?.length) continue;

    const units = await extractUnits(file);

    for (const unit of units) {
      // Check overlap with any hunk
      if (fileHunks.some(h => overlaps(unit.lines, h))) {
        console.log(JSON.stringify({ ...unit, file, changeStatus: status }));
      }
    }
  }
}

main().catch(console.error);
