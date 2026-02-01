# Phase 4: Wire into /code-foundations:review - Pseudocode

**Date:** 2026-02-01
**Branch:** feat/agent-scripts-batch-mode
**Status:** Pseudocode Complete

---

## Overview

Replace extraction agent dispatch with single shell script call in both SANITY and PR flows.

**Scope of changes:**
- SANITY STEP 1: EXTRACTION - Replace multi-agent dispatch with script call
- STEP 5: PHASE 1 - EXTRACTION (PR flow) - Same replacement
- All other phases remain unchanged

---

## SANITY STEP 1: EXTRACTION

### BEFORE (Current Implementation)

```
SANITY STEP 1: EXTRACTION (Parallel Haiku)

Mark phase in_progress
  Find phase 1 task in TaskList
  Update status to in_progress

Dispatch extraction agents
  Read file list from BASE_DIR/files.txt
  Split files into batches of 5

  For each batch:
    Dispatch extraction-agent subagent with:
      - FILES: the batch of files
      - DIFF_CMD: the diff command
      - PLUGIN_ROOT: plugin directory
      - BASE_DIR: output directory

    Wait for wave to complete (respect MAX_PARALLELISM)

Mark phase complete
  Update phase 1 status to completed
```

### AFTER (New Implementation)

```
SANITY STEP 1: EXTRACTION (Single Script Call)

Mark phase in_progress
  Find phase 1 task in TaskList
  Update status to in_progress

Execute extraction script
  Define paths:
    SCRIPT_PATH = PLUGIN_ROOT/agents/extract-with-diff.sh
    OUTPUT_FILE = BASE_DIR/units.jsonl

  Run script from repository root:
    cd REPO_ROOT
    Execute: SCRIPT_PATH DIFF_ARGS > OUTPUT_FILE
    Capture exit code and stderr

  Handle errors:
    If exit code is non-zero:
      Display error message: "Extraction script failed"
      Show stderr output for debugging
      Abort review with clear error

    If output file is empty or missing:
      Check if files.txt had any code files
      If no code files: warn but continue (non-fatal)
      If code files existed: error and abort

Mark phase complete
  Update phase 1 status to completed
```

### Detailed Pseudocode

```
# Locate phase task
tasks = TaskList()
phase1_id = find task where subject contains "Phase 1"
TaskUpdate(phase1_id, status="in_progress")

# Define script path and output location
SCRIPT_PATH = "{PLUGIN_ROOT}/agents/extract-with-diff.sh"
OUTPUT_FILE = "{BASE_DIR}/units.jsonl"

# Execute extraction script
# Note: DIFF_ARGS may be:
#   "--staged"           (staged changes)
#   ""                   (unstaged changes - empty string)
#   "HEAD"               (all uncommitted)
#   "$MERGE_BASE HEAD"   (branch diff - two arguments)

Run Bash:
  cd "{REPO_ROOT}" && "{SCRIPT_PATH}" {DIFF_ARGS} > "{OUTPUT_FILE}" 2>&1

  Store exit_code from command

If exit_code != 0:
  Display to user:
    "Extraction failed. Exit code: {exit_code}"
    "Check that tree-sitter-cli is installed: npm install -g tree-sitter-cli"
    "Script output: {stderr}"
  Abort review

If OUTPUT_FILE does not exist OR is empty:
  FILE_COUNT = count lines in "{BASE_DIR}/files.txt"
  If FILE_COUNT == 0:
    Display: "No files to extract. Review target has no changes."
    Skip to summary (no findings)
  Else:
    Display: "Extraction produced no units from {FILE_COUNT} files."
    Display: "This may indicate unsupported file types or extraction error."
    Continue (downstream phases will handle gracefully)

# Verify output has expected format (optional sanity check)
UNIT_COUNT = count lines in "{OUTPUT_FILE}"
Display: "Extracted {UNIT_COUNT} units from changed files."

# Mark complete
TaskUpdate(phase1_id, status="completed")
```

---

## STEP 5: PHASE 1 - EXTRACTION (PR Flow)

### BEFORE (Current Implementation)

```
STEP 5: PHASE 1 - EXTRACTION (Parallel Haiku)

Create tasks for each batch
  Calculate batch count based on FILE_COUNT / 5
  For each batch:
    TaskCreate with subject "Extract batch N"

Execute extraction agents (respect MAX_PARALLELISM)
  Read files from BASE_DIR/files.txt
  Split into batches

  For each wave:
    For each batch in wave:
      Dispatch extraction-agent subagent
    Wait for wave to complete

Mark extraction complete
  Mark all extraction tasks completed
```

### AFTER (New Implementation)

```
STEP 5: PHASE 1 - EXTRACTION (Single Script Call)

Mark phase in_progress
  Find phase 1 task in TaskList
  Update status to in_progress

Execute extraction script
  Define paths:
    SCRIPT_PATH = PLUGIN_ROOT/agents/extract-with-diff.sh
    OUTPUT_FILE = BASE_DIR/units.jsonl

  Run script from repository root:
    cd REPO_ROOT
    Execute: SCRIPT_PATH DIFF_ARGS > OUTPUT_FILE
    Capture exit code and stderr

  Handle errors:
    If exit code is non-zero:
      Display error with debugging info
      Abort review

    If output file is empty:
      Warn but continue

Mark phase complete
  Update phase 1 status to completed
```

### Detailed Pseudocode

```
# Locate phase task
tasks = TaskList()
phase1_id = find task where subject contains "Phase 1"
TaskUpdate(phase1_id, status="in_progress")

# Define script path and output location
SCRIPT_PATH = "{PLUGIN_ROOT}/agents/extract-with-diff.sh"
OUTPUT_FILE = "{BASE_DIR}/units.jsonl"

# Execute extraction script
Run Bash:
  cd "{REPO_ROOT}" && "{SCRIPT_PATH}" {DIFF_ARGS} > "{OUTPUT_FILE}" 2>&1

  Store exit_code from command

If exit_code != 0:
  Display to user:
    "Extraction failed. Exit code: {exit_code}"
    "Ensure tree-sitter-cli is installed globally."
  Abort review

# Count extracted units for progress display
UNIT_COUNT = count lines in "{OUTPUT_FILE}"
Display: "Extracted {UNIT_COUNT} units."

# Mark complete
TaskUpdate(phase1_id, status="completed")
```

---

## Error Handling Summary

| Error Condition | Handling |
|-----------------|----------|
| Script not found | Bash will fail with "command not found" - abort with path info |
| Script exits non-zero | Display exit code and stderr, abort review |
| Output file empty | Warn user, continue (may be valid - no code files) |
| Output file missing | Check if redirect failed, abort with error |
| Malformed JSONL | Let downstream phases fail with clear error |

**Design decision:** No fallback to extraction agents. The script approach is the intended path; if it fails, we surface the error rather than silently degrading.

---

## Integration Points

### DIFF_ARGS Mapping (from STEP 3)

| User Selection | DIFF_ARGS Value | Script Receives |
|----------------|-----------------|-----------------|
| Staged changes | `--staged` | `--staged` |
| Unstaged changes | `` (empty) | (no args) |
| All uncommitted | `HEAD` | `HEAD` |
| Branch diff | `$MERGE_BASE HEAD` | Two args: merge-base hash and `HEAD` |

### Output Consumption

The `units.jsonl` file is consumed by:
- **SANITY STEP 2:** `orchestrate-checking-agent` reads `units.jsonl`, produces `checking-batches.json`
- **STEP 6 (PR):** Same orchestrator reads `units.jsonl`

Both flows already expect `$BASE_DIR/units.jsonl` per Phase 3 updates.

---

## What Stays The Same

| Component | Status |
|-----------|--------|
| STEP 0: Find plugin directory | Unchanged |
| STEP 1-2: Parse args, validate profile | Unchanged |
| STEP 3: Get diff target | Unchanged |
| STEP 4: Setup directories | Unchanged |
| STEP 4.5: Create phase tasks | Unchanged |
| STEP 4.6: Branch by profile | Unchanged |
| SANITY STEP 2-6: Orchestrate through Summary | Unchanged |
| STEP 6 onwards (PR): Check orchestration through Summary | Unchanged |

---

## Verification Checklist

After implementation, verify:

1. [ ] `extract-with-diff.sh` is executable
2. [ ] Script path resolution uses PLUGIN_ROOT correctly
3. [ ] DIFF_ARGS is passed correctly (especially empty string case)
4. [ ] Output redirects to correct location
5. [ ] Error messages are actionable
6. [ ] Downstream phases read from `units.jsonl` (not `extraction/` directory)
7. [ ] Both `--sanity` and `--pr` flows work
8. [ ] Edge cases: no changes, binary-only changes, single file
