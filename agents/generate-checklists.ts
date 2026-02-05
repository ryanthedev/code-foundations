#!/usr/bin/env bun
/**
 * generate-checklists.ts v3.6.10 - Create checklist files for checker agents
 *
 * Usage:
 *   cat batches.json | bun generate-checklists.ts <output-dir>
 *   bun generate-checklists.ts <output-dir> < batches.json
 */

const VERSION = "3.6.10";
console.error(`[generate-checklists.ts v${VERSION}]`);

// The 14 core checks for sanity review
// Each check has a `requires` function that returns true if the check applies to the unit
const CORE_CHECKS: Array<{
  id: string;
  question: string;
  requires: (u: Unit) => boolean;
}> = [
  {
    id: "ERR-3",
    question: "Are all error-return codes checked?",
    requires: () => true, // Always check - hard to infer statically
  },
  {
    id: "ERR-8",
    question: "Are partial failures handled (rollback, cleanup)?",
    requires: (u) => u.has_try_catch || u.has_async,
  },
  {
    id: "NULL-2",
    question: "Does code check for null before use?",
    requires: (u) => u.param_count > 0 || u.type !== "constructor",
  },
  {
    id: "NULL-4",
    question: "Are array indexes within bounds?",
    requires: (u) => u.has_loops, // Proxy: array access often in loops
  },
  {
    id: "NULL-5",
    question: "Are array references free of off-by-one errors?",
    requires: (u) => u.has_loops,
  },
  {
    id: "NULL-6",
    question: "What happens with empty input?",
    requires: (u) => u.param_count > 0,
  },
  {
    id: "LOGIC-1",
    question: "Does the loop end under all conditions?",
    requires: (u) => u.has_loops,
  },
  {
    id: "LOGIC-6",
    question: "Does recursive code have a path to stop?",
    requires: () => true, // Hard to detect recursion statically
  },
  {
    id: "LOGIC-11",
    question: "Are all cases covered in switch/if-else?",
    requires: () => true, // Always relevant
  },
  {
    id: "LOGIC-15",
    question: "No accidental assignment in conditionals?",
    requires: () => true, // Always relevant
  },
  {
    id: "CONC-2",
    question: "Is each shared access point protected?",
    requires: (u) => u.has_async,
  },
  {
    id: "CONC-3",
    question: "Are there no TOCTOU race conditions?",
    requires: (u) => u.has_async,
  },
  {
    id: "RES-1",
    question: "Does every acquire have corresponding release?",
    requires: (u) => u.has_try_catch, // Resource cleanup often in try-finally
  },
  {
    id: "PERF-1",
    question: "Are database queries not in loops (N+1)?",
    requires: (u) => u.has_loops && u.has_async,
  },
];

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

function generateChecklist(batch: Batch): string {
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
    lines.push(`| ${unit.name} | ${unit.file} | ${lineRange} | ${unit.type} |`);
  }
  lines.push(``);

  // Instructions
  lines.push(`## Instructions`);
  lines.push(``);
  lines.push(`For each check, replace the empty checkbox with a detailed verdict:`);
  lines.push(``);
  lines.push(`\`[x]\` PASS - check satisfied`);
  lines.push(`\`[!]\` FINDING - issue detected`);
  lines.push(`\`[~]\` N/A - check doesn't apply`);
  lines.push(``);
  lines.push(`Confidence: HIGH (obvious) | MEDIUM (likely) | LOW (uncertain)`);
  lines.push(``);

  // Checks
  lines.push(`## Checks`);
  lines.push(``);

  let totalCheckboxes = 0;
  let skippedCheckboxes = 0;

  for (const check of CORE_CHECKS) {
    const applicableUnits = batch.units.filter(check.requires);
    const skipped = batch.units.length - applicableUnits.length;
    skippedCheckboxes += skipped;
    totalCheckboxes += applicableUnits.length;

    // Skip entire check section if no units apply
    if (applicableUnits.length === 0) continue;

    lines.push(`### ${check.id}: ${check.question}`);
    if (skipped > 0) {
      lines.push(`*Skipped ${skipped} units (not applicable)*`);
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

  // Summary at end
  lines.push(`---`);
  lines.push(`*${totalCheckboxes} checks to evaluate (${skippedCheckboxes} skipped as N/A)*`);

  return lines.join("\n");
}

async function main() {
  const outputDir = process.argv[2];

  if (!outputDir) {
    console.error("Usage: cat batches.json | bun generate-checklists.ts <output-dir>");
    process.exit(1);
  }

  // Read batches from stdin
  const input = await Bun.stdin.text();
  const batches: Batch[] = JSON.parse(input);

  // Create output directory
  const checklistDir = `${outputDir}/checklists`;
  await Bun.write(`${checklistDir}/.keep`, ""); // ensures dir exists

  // Generate checklist for each batch
  for (const batch of batches) {
    const checklist = generateChecklist(batch);
    const filename = `${checklistDir}/${batch.batch_id}.md`;
    await Bun.write(filename, checklist);
    console.error(`Created: ${filename}`);
  }

  console.log(JSON.stringify({
    checklist_dir: checklistDir,
    count: batches.length,
    files: batches.map(b => `${checklistDir}/${b.batch_id}.md`)
  }, null, 2));
}

main();
