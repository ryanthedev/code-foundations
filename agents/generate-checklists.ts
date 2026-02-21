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
// Checklist generation
// ---------------------------------------------------------------------------

function generateChecklist(batch: Batch, checks: CheckDef[]): string {
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
  lines.push(
    `For each check, replace the empty checkbox with a detailed verdict:`
  );
  lines.push(``);
  lines.push("`[x]` PASS - check satisfied");
  lines.push("`[!]` FINDING - issue detected");
  lines.push("`[~]` N/A - check doesn't apply");
  lines.push(``);
  lines.push(`Confidence: HIGH (obvious) | MEDIUM (likely) | LOW (uncertain)`);
  lines.push(``);

  // Checks
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
    if (skipped > 0) {
      lines.push(`*Skipped ${skipped} units (not applicable)*`);
    }

    if (check.pass_when && check.pass_when.length > 0) {
      lines.push(``);
      lines.push(`**PASS when:**`);
      for (const p of check.pass_when) {
        lines.push(`- ${p}`);
      }
    }
    if (check.fail_when && check.fail_when.length > 0) {
      lines.push(``);
      lines.push(`**FAIL when:**`);
      for (const f of check.fail_when) {
        lines.push(`- ${f}`);
      }
    }
    if (check.examples) {
      lines.push(``);
      lines.push(`**Examples:**`);
      lines.push("```");
      lines.push(`// PASS`);
      lines.push(check.examples.pass.trim());
      lines.push(``);
      lines.push(`// FAIL`);
      lines.push(check.examples.fail.trim());
      lines.push("```");
    }
    if (check.confidence) {
      lines.push(``);
      lines.push(
        `**Confidence:** HIGH: ${check.confidence.high}${check.confidence.medium ? ` | MEDIUM: ${check.confidence.medium}` : ""}`
      );
    }

    lines.push(``);
    for (const unit of applicableUnits) {
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

  for (const batch of batches) {
    const checklist = generateChecklist(batch, checks);
    const filename = `${checklistDir}/${batch.batch_id}.md`;
    await Bun.write(filename, checklist);
    console.error(`Created: ${filename}`);
  }

  console.log(
    JSON.stringify(
      {
        checklist_dir: checklistDir,
        count: batches.length,
        checks_loaded: checks.length,
        files: batches.map((b) => `${checklistDir}/${b.batch_id}.md`),
      },
      null,
      2
    )
  );
}

main();
