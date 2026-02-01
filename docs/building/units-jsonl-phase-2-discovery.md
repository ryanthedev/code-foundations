# Phase 2: Diff Integration Discovery

**Date:** 2026-02-01
**Branch:** feat/agent-scripts-batch-mode
**Status:** Discovery Complete

## Overview

Create `extract-with-diff.sh` that combines git diff with unit extraction to produce units.jsonl with diff, changeStatus, and summary fields.

---

## Question 1: Git Diff Parsing

### Getting Changed Files
```bash
git diff --name-status <args>
# Output: M  src/api/users.ts
#         A  src/api/auth.ts
#         D  src/old/legacy.ts
```

### Getting Diff Hunks with Line Numbers
```bash
git diff -U3 <args> -- <file>
# Output includes:
# @@ -15,6 +15,20 @@ function createUser
# +  const { email } = req.body;
# +  if (!email) throw new Error();
```

### Hunk Header Format
```
@@ -oldstart,oldcount +newstart,newcount @@ [context]
```
- `+newstart,newcount` gives us the line range in the new file
- Match against unit lines for overlap

---

## Question 2: Hunk-to-Unit Matching

### Overlap Detection Algorithm
```
Unit overlaps hunk if:
  unit_start <= hunk_end AND unit_end >= hunk_start
```

### Pseudocode
```
FOR each unit in file:
  matching_hunks = []
  FOR each hunk in file_hunks:
    hunk_start = hunk.new_start
    hunk_end = hunk.new_start + hunk.new_count - 1

    IF unit.lines[0] <= hunk_end AND unit.lines[1] >= hunk_start:
      matching_hunks.append(hunk)

  IF matching_hunks is not empty:
    unit.diff = concatenate(matching_hunks)
    output(unit)
```

---

## Question 3: Diff Field Format

### Minimal Format (for token efficiency)
```
@@ -15,6 +15,20 @@
+  const { email } = req.body;
+  if (!email) throw new Error();

   const user = await db.create();
```

- Include hunk header for context
- No git headers (diff --git, index, ---, +++)
- Preserves +/- markers for change visibility

---

## Question 4: changeStatus Determination

### File-Level Status from git
```bash
git diff --name-status <args>
# A = added (new file)
# M = modified
# D = deleted
# R = renamed (treat as modified)
```

### Mapping
| Git Status | changeStatus |
|------------|--------------|
| A | added |
| M | modified |
| D | deleted |
| R | modified |

### Special Case: Deleted Files
For deleted files, extract units from `HEAD` version:
```bash
git show HEAD:<file> > /tmp/deleted_file
extract-units.sh --files /tmp/deleted_file
```

---

## Question 5: Summary Generation

### Tier 1: Heuristic Approach
Pattern-based summary generation (no LLM needed):

| Pattern in Diff | Summary |
|-----------------|---------|
| New function (all `+` lines) | "Add {name} function" |
| Mostly additions | "Extend {name} with new logic" |
| Error handling patterns | "Add error handling to {name}" |
| Async/await patterns | "Add async handling" |
| Mostly deletions | "Simplify {name}" |
| Balanced changes | "Refactor {name}" |

### Implementation
```bash
generate_summary() {
  local name="$1" diff="$2"
  local added=$(echo "$diff" | grep -c '^+[^+]')
  local removed=$(echo "$diff" | grep -c '^-[^-]')

  if (( removed == 0 && added > 0 )); then
    echo "Add $name"
  elif (( added > removed * 2 )); then
    echo "Extend $name"
  elif (( removed > added * 2 )); then
    echo "Simplify $name"
  else
    echo "Update $name"
  fi
}
```

---

## Question 6: Performance Considerations

### Target: <2s for typical PR (10-20 files)

### Optimization Strategies
1. **Single git diff call** - Get all hunks at once, parse in memory
2. **Cache parsed hunks** - Build lookup table by file
3. **Stream processing** - Output JSONL as units are processed
4. **Skip non-code files** - Same filter as extract-units.sh

### Complexity Analysis
- git diff: O(1) call
- Parse hunks: O(files × hunks)
- Match units: O(units × hunks_per_file)
- Total: O(files × units × hunks) ≈ linear for typical PRs

---

## Implementation Plan

### Script Structure
```bash
#!/usr/bin/env bash
# extract-with-diff.sh

# 1. Parse git diff args
# 2. Get file change statuses
# 3. Get all diff hunks
# 4. For each changed file:
#    a. Extract units via extract-units.sh
#    b. Match units to hunks
#    c. Generate summaries
#    d. Output JSONL
```

### Output Format (JSONL)
Each line is a complete JSON object:
```json
{"file":"src/api/users.ts","name":"createUser","type":"function","lines":[15,67],"diff":"@@ -15,6 +15,20 @@\n+  const { email } = req.body;","changeStatus":"modified","summary":"Add email validation","is_test":false,"layer":"api",...}
```

---

## Integration Points

### Input: Git diff arguments
- `--staged` (staged changes)
- `branch` (compare to branch)
- `commit1..commit2` (commit range)
- No args (unstaged changes)

### Output: units.jsonl to stdout
- One JSON object per line
- Only units that overlap with diff hunks
- Ready for orchestrate-checking-agent consumption

---

## Test Cases

1. **Single file, single hunk** - Basic overlap
2. **Single file, multiple hunks** - Hunk concatenation
3. **New file (A status)** - changeStatus: added
4. **Deleted file (D status)** - Extract from HEAD
5. **No overlapping units** - File changed but no function touched
