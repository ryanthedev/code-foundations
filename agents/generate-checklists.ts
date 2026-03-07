#!/usr/bin/env bun
/**
 * generate-checklists.ts v3.7.2 - Create checklist files for checker agents
 *
 * Usage:
 *   cat batches.json | bun generate-checklists.ts <output-dir>
 *
 * Loads checks from benchmarks/checks/*.yaml relative to this script's directory.
 */

import * as yaml from "js-yaml";
import * as fs from "fs";
import * as path from "path";

const VERSION = "3.7.2";
const SCRIPT_DIR = path.dirname(import.meta.path);
const PLUGIN_ROOT = path.dirname(SCRIPT_DIR);
const CHECKS_DIR = path.join(SCRIPT_DIR, "checks");

console.error(`[generate-checklists.ts v${VERSION}]`);

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface Unit {
  name: string;
  file: string;
  lines: [number, number];
  type: string;
  param_count: number;
  has_loops: boolean;
  has_async: boolean;
  has_try_catch: boolean;
  has_throw: boolean;
  [key: string]: unknown;
}

interface Batch {
  batch_id: string;
  reason: string;
  units: Unit[];
}

interface CheckDef {
  id: string;
  question: string;
  requires: (u: Unit) => boolean;
  name?: string;
  pass_when?: string[];
  fail_when?: string[];
  examples?: { pass: string; fail: string };
  confidence?: { high: string; medium?: string };
}

// ---------------------------------------------------------------------------
// YAML check loading
// ---------------------------------------------------------------------------

/** Parse a gate string (e.g. "has_async == true") into a requires function. */
function parseGate(gate: string | undefined): (u: Unit) => boolean {
  if (!gate) return () => true;

  // Simple "field == true"
  const boolMatch = gate.match(/^(\w+)\s*==\s*true$/);
  if (boolMatch) {
    const field = boolMatch[1];
    return (u: Unit) => (field in u ? !!(u as any)[field] : true);
  }

  // Complex gates (AND, OR, language checks) – always include, agent decides N/A
  return () => true;
}

/** Load all check definitions from YAML files in a directory. */
function loadChecks(): CheckDef[] {
  const files = fs.readdirSync(CHECKS_DIR).filter((f) => f.endsWith(".yaml")).sort();
  const checksMap = new Map<string, CheckDef>();

  for (const file of files) {
    const content = fs.readFileSync(path.join(CHECKS_DIR, file), "utf-8");
    const data = yaml.load(content) as { checks: any[] };
    if (!data?.checks) continue;

    for (const c of data.checks) {
      checksMap.set(c.id, {
        id: c.id,
        question: c.question,
        requires: parseGate(c.gate),
        name: c.name,
        pass_when: c.pass_when,
        fail_when: c.fail_when,
        examples: c.examples,
        confidence: c.confidence,
      });
    }
  }

  console.error(`Loaded ${checksMap.size} checks from ${files.length} files`);
  return Array.from(checksMap.values());
}

// ---------------------------------------------------------------------------
// Reference generation
// ---------------------------------------------------------------------------

interface ReferenceResult {
  content: string;
  lineRanges: Map<string, { start: number; end: number }>;
}

function generateReference(checks: CheckDef[]): ReferenceResult {
  const lines: string[] = [];
  const lineRanges = new Map<string, { start: number; end: number }>();

  lines.push(`# Check Reference`);
  lines.push(``);
  lines.push(`Guidance for evaluating checks. Read once for calibration.`);
  lines.push(``);

  for (const check of checks) {
    const startLine = lines.length + 1; // 1-indexed
    lines.push(`## ${check.id}: ${check.question}`);
    lines.push(``);

    if (check.pass_when && check.pass_when.length > 0) {
      lines.push(`**PASS when:**`);
      for (const p of check.pass_when) {
        lines.push(`- ${p}`);
      }
      lines.push(``);
    }
    if (check.fail_when && check.fail_when.length > 0) {
      lines.push(`**FAIL when:**`);
      for (const f of check.fail_when) {
        lines.push(`- ${f}`);
      }
      lines.push(``);
    }
    if (check.examples) {
      lines.push(`**Examples:**`);
      lines.push("```");
      lines.push(`// PASS`);
      lines.push(check.examples.pass.trim());
      lines.push(``);
      lines.push(`// FAIL`);
      lines.push(check.examples.fail.trim());
      lines.push("```");
      lines.push(``);
    }
    if (check.confidence) {
      lines.push(
        `**Confidence:** HIGH: ${check.confidence.high}${check.confidence.medium ? ` | MEDIUM: ${check.confidence.medium}` : ""}`
      );
      lines.push(``);
    }

    lineRanges.set(check.id, { start: startLine, end: lines.length });
  }

  return { content: lines.join("\n"), lineRanges };
}

// ---------------------------------------------------------------------------
// Interface applicability
// ---------------------------------------------------------------------------

/** Check prefixes that apply to interface/type definitions. */
const INTERFACE_APPLICABLE_PREFIXES = [
  "ARCH", "NAME", "CD", "SPELL", "STYLE",
];

/** Returns true if the check applies to an interface/type unit. */
function appliesToInterface(checkId: string): boolean {
  return INTERFACE_APPLICABLE_PREFIXES.some((p) => checkId.startsWith(p));
}

// ---------------------------------------------------------------------------
// Checklist generation
// ---------------------------------------------------------------------------

function generateChecklist(batch: Batch, checks: CheckDef[], refRanges: Map<string, { start: number; end: number }>): string {
  const lines: string[] = [];

  // Header
  lines.push(`# ${batch.batch_id}`);
  lines.push(``);
  lines.push(`**${batch.reason}**`);
  lines.push(``);

  // Units table
  lines.push(`## Units`);
  lines.push(``);
  lines.push(`| Unit | File | Lines | Type |`);
  lines.push(`|------|------|-------|------|`);
  for (const unit of batch.units) {
    const lineRange = `${unit.lines[0]}-${unit.lines[1]}`;
    lines.push(
      `| ${unit.name} | ${unit.file} | ${lineRange} | ${unit.type} |`
    );
  }
  lines.push(``);

  // Instructions
  lines.push(`## Instructions`);
  lines.push(``);
  lines.push(`Treat each check below as a task. For each check:`);
  lines.push(`1. Read the referenced lines from checks-reference.md to understand PASS/FAIL criteria`);
  lines.push(`2. Evaluate ALL units against that check`);
  lines.push(`3. Replace every empty checkbox with a verdict`);
  lines.push(``);
  lines.push(`**Verdicts:**`);
  lines.push("`[x]` PASS - check satisfied");
  lines.push("`[!]` FINDING - issue detected");
  lines.push("`[~]` N/A - check doesn't apply");
  lines.push(``);
  lines.push(`**Confidence:** HIGH (obvious) | MEDIUM (likely) | LOW (uncertain)`);
  lines.push(``);

  // Checks (headers + checkboxes only, no guidance)
  lines.push(`## Checks`);
  lines.push(``);

  let totalCheckboxes = 0;
  let skippedCheckboxes = 0;

  for (const check of checks) {
    const applicableUnits = batch.units.filter(check.requires);
    const skipped = batch.units.length - applicableUnits.length;
    skippedCheckboxes += skipped;
    totalCheckboxes += applicableUnits.length;

    if (applicableUnits.length === 0) continue;

    lines.push(`### ${check.id}: ${check.question}`);
    const range = refRanges.get(check.id);
    if (range) {
      lines.push(`> checks-reference.md lines ${range.start}-${range.end}`);
    }
    if (skipped > 0) {
      lines.push(`*Skipped ${skipped} units (not applicable)*`);
    }

    // Pre-fill N/A for interface/type units on non-applicable checks
    const interfaceUnits = applicableUnits.filter(
      (u) => (u.type === "interface" || u.type === "type") && !appliesToInterface(check.id)
    );
    const checkableUnits = applicableUnits.filter(
      (u) => !interfaceUnits.includes(u)
    );

    if (interfaceUnits.length > 0) {
      const names = interfaceUnits.map((u) => u.name).join(", ");
      lines.push(`*N/A: ${names} (type definitions — no executable code)*`);
    }

    // Only generate empty checkboxes for units that need evaluation
    if (checkableUnits.length === 0 && interfaceUnits.length > 0) {
      skippedCheckboxes += interfaceUnits.length;
      totalCheckboxes -= interfaceUnits.length;
      lines.push(``);
      continue;
    }

    skippedCheckboxes += interfaceUnits.length;
    totalCheckboxes -= interfaceUnits.length;

    lines.push(``);
    for (const unit of checkableUnits) {
      lines.push(`- [ ] ${unit.name}:`);
      lines.push(`  - Issue:`);
      lines.push(`  - Evidence:`);
      lines.push(`  - Confidence:`);
      lines.push(``);
    }
  }

  lines.push(`---`);
  lines.push(
    `*${totalCheckboxes} checks to evaluate (${skippedCheckboxes} skipped as N/A)*`
  );

  return lines.join("\n");
}

// ---------------------------------------------------------------------------
// Per-check file generation
// ---------------------------------------------------------------------------

interface CheckFile {
  checkId: string;
  content: string;
}

function generateCheckFiles(batch: Batch, checks: CheckDef[]): CheckFile[] {
  const files: CheckFile[] = [];

  for (const check of checks) {
    const applicableUnits = batch.units.filter(check.requires);
    if (applicableUnits.length === 0) continue;

    const lines: string[] = [];

    // Header with batch context
    lines.push(`# ${check.id}: ${check.question}`);
    lines.push(``);
    lines.push(`**Batch:** ${batch.batch_id} | **${batch.reason}**`);
    lines.push(``);

    // Units table
    lines.push(`## Units`);
    lines.push(``);
    lines.push(`| Unit | File | Lines | Type |`);
    lines.push(`|------|------|-------|------|`);
    for (const unit of applicableUnits) {
      const lineRange = `${unit.lines[0]}-${unit.lines[1]}`;
      lines.push(`| ${unit.name} | ${unit.file} | ${lineRange} | ${unit.type} |`);
    }
    lines.push(``);

    // Inlined reference guidance
    lines.push(`## Guidance`);
    lines.push(``);
    if (check.pass_when && check.pass_when.length > 0) {
      lines.push(`**PASS when:**`);
      for (const p of check.pass_when) lines.push(`- ${p}`);
      lines.push(``);
    }
    if (check.fail_when && check.fail_when.length > 0) {
      lines.push(`**FAIL when:**`);
      for (const f of check.fail_when) lines.push(`- ${f}`);
      lines.push(``);
    }
    if (check.examples) {
      lines.push(`**Examples:**`);
      lines.push("```");
      lines.push(`// PASS`);
      lines.push(check.examples.pass.trim());
      lines.push(``);
      lines.push(`// FAIL`);
      lines.push(check.examples.fail.trim());
      lines.push("```");
      lines.push(``);
    }
    if (check.confidence) {
      lines.push(
        `**Confidence:** HIGH: ${check.confidence.high}${check.confidence.medium ? ` | MEDIUM: ${check.confidence.medium}` : ""}`
      );
      lines.push(``);
    }

    // Verdicts section
    lines.push(`## Verdicts`);
    lines.push(``);
    lines.push("`[x]` PASS | `[!]` FINDING | `[~]` N/A");
    lines.push(``);

    // Pre-fill N/A for interface/type units on non-applicable checks
    const interfaceUnits = applicableUnits.filter(
      (u) => (u.type === "interface" || u.type === "type") && !appliesToInterface(check.id)
    );
    const checkableUnits = applicableUnits.filter(
      (u) => !interfaceUnits.includes(u)
    );

    if (interfaceUnits.length > 0) {
      const names = interfaceUnits.map((u) => u.name).join(", ");
      lines.push(`*N/A: ${names} (type definitions — no executable code)*`);
      lines.push(``);
    }

    for (const unit of checkableUnits) {
      lines.push(`- [ ] ${unit.name}:`);
      lines.push(`  - Issue:`);
      lines.push(`  - Evidence:`);
      lines.push(`  - Confidence:`);
      lines.push(``);
    }

    files.push({ checkId: check.id, content: lines.join("\n") });
  }

  return files;
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  const outputDir = process.argv[2];

  if (!outputDir) {
    console.error("Usage: cat batches.json | bun generate-checklists.ts <output-dir>");
    process.exit(1);
  }

  const checks = loadChecks();
  console.error(`Using ${checks.length} checks`);

  const input = await Bun.stdin.text();
  const batches: Batch[] = JSON.parse(input);

  const checklistDir = `${outputDir}/checklists`;
  await Bun.write(`${checklistDir}/.keep`, "");

  // Write reference file once
  const { content: reference, lineRanges: refRanges } = generateReference(checks);
  const refPath = `${checklistDir}/checks-reference.md`;
  await Bun.write(refPath, reference);
  console.error(`Created: ${refPath} (${reference.split("\n").length} lines)`);

  const allCheckFiles: string[] = [];

  for (const batch of batches) {
    // Write combined checklist (existing format)
    const checklist = generateChecklist(batch, checks, refRanges);
    const filename = `${checklistDir}/${batch.batch_id}.md`;
    await Bun.write(filename, checklist);
    console.error(`Created: ${filename} (${checklist.split("\n").length} lines)`);

    // Write per-check files with inlined guidance
    const checkFiles = generateCheckFiles(batch, checks);
    const batchDir = `${checklistDir}/${batch.batch_id}`;
    await Bun.write(`${batchDir}/.keep`, "");
    for (const cf of checkFiles) {
      const cfPath = `${batchDir}/${cf.checkId}.md`;
      await Bun.write(cfPath, cf.content);
      allCheckFiles.push(cfPath);
    }
    console.error(`  → ${checkFiles.length} check files in ${batchDir}/`);
  }

  console.log(
    JSON.stringify(
      {
        checklist_dir: checklistDir,
        count: batches.length,
        checks_loaded: checks.length,
        reference: refPath,
        files: batches.map((b) => `${checklistDir}/${b.batch_id}.md`),
        check_files: allCheckFiles,
      },
      null,
      2
    )
  );
}

main();
