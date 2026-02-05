# Checklist-Based Code Review System

**Version:** 3.6.6
**Branch:** `feat/chkrs`
**Status:** In Development

---

## Executive Summary

A code review system that produces **human-readable checklist artifacts** instead of opaque JSON logs. LLM checker agents fill in markdown checklists with verdicts (PASS/FINDING/N/A), creating reviewable documentation of every check performed.

### Why Checklists?

| Old Approach (JSONL + Bash Scripts) | New Approach (Markdown Checklists) |
|-------------------------------------|-----------------------------------|
| LLM constructs bash commands with flags | LLM edits markdown files |
| Easy to mess up quoting, escaping | Natural text editing |
| Opaque `findings.jsonl` output | Readable `batch-1.md` artifacts |
| Machine-only output | Human + machine readable |
| Schema enforced by script validation | Structure enforced by template |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           /code-foundations:review                       │
│                              (orchestrator)                              │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Step 4: Extract Units                                                   │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  extract-units.ts                                                │    │
│  │  • Uses ast-grep for semantic code parsing                       │    │
│  │  • Detects methods, classes, functions across languages          │    │
│  │  • Filters to only units touched by the diff                     │    │
│  │  • Output: units.jsonl (one JSON object per line)                │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Step 5: Create Batches                                                  │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  orchestrate-batches.sh                                          │    │
│  │  • Groups units by "logical source file"                         │    │
│  │  • Pairs test files with their source files                      │    │
│  │  • 100% deterministic based on file paths                        │    │
│  │  • Output: batches.json                                          │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Step 6: Generate Checklists                                             │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  generate-checklists.ts                                          │    │
│  │  • Creates one markdown file per batch                           │    │
│  │  • Pre-populates with units table + 14 checks                    │    │
│  │  • Empty checkboxes ready to be filled                           │    │
│  │  • Output: checklists/batch-*.md                                 │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Step 7: Dispatch Checker Agents (parallel, max 5)                       │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  checker-agent (×N)                                              │    │
│  │  • Receives: CHECKLIST_FILE, REPO_ROOT                           │    │
│  │  • Reads source code for each unit                               │    │
│  │  • Evaluates each check                                          │    │
│  │  • Uses Edit tool to fill in checkboxes                          │    │
│  │  • Output: filled-in checklist file                              │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Step 8-9: Summarize & Offer Actions                                     │
│  • Count verdicts across all checklists                                  │
│  • Display findings summary                                              │
│  • Offer: show findings, open folder, done                               │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## File Formats

### 1. Unit (from extract-units.ts)

```json
{
  "name": "ProcessOrder",
  "file": "src/Orders/OrderService.cs",
  "type": "method",
  "lines": [45, 89],
  "is_test": false,
  "tests_unit": null,
  "layer": "service",
  "params": "Order order, CancellationToken ct",
  "param_count": 2,
  "return_type": "Task<Result>",
  "has_loops": true,
  "has_async": true,
  "has_try_catch": true,
  "has_throw": false,
  "line_count": 45,
  "visibility": "public",
  "changeStatus": "modified"
}
```

### 2. Batch (from orchestrate-batches.sh)

```json
{
  "batch_id": "batch-1",
  "reason": "File: OrderService",
  "units": [
    { "name": "ProcessOrder", "file": "...", "lines": [45, 89], ... },
    { "name": "ValidateOrder", "file": "...", "lines": [91, 120], ... }
  ]
}
```

### 3. Checklist (from generate-checklists.ts)

**Empty (before checker agent):**

```markdown
# batch-1

**File: OrderService**

## Units

| Unit | File | Lines | Type |
|------|------|-------|------|
| ProcessOrder | src/Orders/OrderService.cs | 45-89 | method |
| ValidateOrder | src/Orders/OrderService.cs | 91-120 | method |

## Instructions

For each check, mark the result:
- `[x]` PASS - check satisfied, no issues
- `[!]` FINDING - issue found (add: line number + description)
- `[~]` N/A - check doesn't apply (add: reason)
- `[ ]` SKIP - not checked

## Checks

### ERR-3: Are all error-return codes checked?

- [ ] ProcessOrder:
- [ ] ValidateOrder:

### NULL-2: Does code check for null before use?

- [ ] ProcessOrder:
- [ ] ValidateOrder:

... (14 checks total)
```

**Filled (after checker agent):**

```markdown
### ERR-3: Are all error-return codes checked?

- [x] ProcessOrder: PASS
- [!] ValidateOrder: FINDING line 98 - SaveAsync return value not checked

### NULL-2: Does code check for null before use?

- [!] ProcessOrder: FINDING line 52 - order.Items accessed without null check
- [x] ValidateOrder: PASS
```

---

## The 14 Core Checks

These checks are distilled from *Code Complete* and represent the highest-impact defensive programming practices.

| ID | Category | Question |
|----|----------|----------|
| ERR-3 | Error Handling | Are all error-return codes checked? |
| ERR-8 | Error Handling | Are partial failures handled (rollback, cleanup)? |
| NULL-2 | Null Safety | Does code check for null before use? |
| NULL-4 | Bounds | Are array indexes within bounds? |
| NULL-5 | Bounds | Are array references free of off-by-one errors? |
| NULL-6 | Edge Cases | What happens with empty input? |
| LOGIC-1 | Control Flow | Does the loop end under all conditions? |
| LOGIC-6 | Control Flow | Does recursive code have a path to stop? |
| LOGIC-11 | Control Flow | Are all cases covered in switch/if-else? |
| LOGIC-15 | Control Flow | No accidental assignment in conditionals? |
| CONC-2 | Concurrency | Is each shared access point protected? |
| CONC-3 | Concurrency | Are there no TOCTOU race conditions? |
| RES-1 | Resources | Does every acquire have corresponding release? |
| PERF-1 | Performance | Are database queries not in loops (N+1)? |

---

## Scripts Reference

### extract-units.ts

**Purpose:** Extract semantic code units from changed files using ast-grep.

**Usage:**
```bash
bun extract-units.ts <git-diff-args>
bun extract-units.ts --staged
bun extract-units.ts --files file1.ts file2.cs
bun extract-units.ts --status  # check ast-grep availability
```

**Supported Languages:**
- C# (.cs)
- TypeScript/JavaScript (.ts, .tsx, .js, .jsx)
- Python (.py)
- Go (.go)
- Swift (.swift)

**Output:** JSONL to stdout (one unit per line)

**Dependencies:**
- bun
- ast-grep (`sg`)

---

### orchestrate-batches.sh

**Purpose:** Group units into batches by logical source file.

**Usage:**
```bash
cat units.jsonl | ./orchestrate-batches.sh > batches.json
```

**Batching Logic:**
1. Normalize file paths (strip test suffixes)
2. Group by normalized path
3. Test files are grouped with their source files
4. Each batch gets a unique `batch_id`

**Output:** JSON array of batches to stdout

**Dependencies:**
- bash
- jq

---

### generate-checklists.ts

**Purpose:** Create empty checklist markdown files for checker agents.

**Usage:**
```bash
cat batches.json | bun generate-checklists.ts <output-dir>
```

**Output:**
```
<output-dir>/checklists/batch-1.md
<output-dir>/checklists/batch-2.md
...
```

Also outputs JSON manifest to stdout:
```json
{
  "checklist_dir": "/tmp/review/checklists",
  "count": 8,
  "files": ["/tmp/review/checklists/batch-1.md", ...]
}
```

**Dependencies:**
- bun

---

## Checker Agent

**File:** `agents/checker-agent.md`

**Role:** Fill in a single checklist file with verdicts.

**Input:**
- `CHECKLIST_FILE`: Path to the checklist markdown file
- `REPO_ROOT`: Path to the repository being reviewed

**Tools Available:**
- `Read` - read source files and checklist
- `Edit` - update checkboxes in checklist
- `Glob` - find files
- `Grep` - search code

**Workflow:**
1. Read the checklist to parse units table
2. For each unit, read the source code with context
3. For each check × unit, determine verdict
4. Use Edit to update checkbox: `- [ ] UnitName: ` → `- [x] UnitName: PASS`

**Verdict Format:**

| Verdict | Symbol | Format |
|---------|--------|--------|
| PASS | `[x]` | `- [x] UnitName: PASS` |
| FINDING | `[!]` | `- [!] UnitName: FINDING line 42 - description` |
| N/A | `[~]` | `- [~] UnitName: N/A - reason` |

**N/A Guidance:**

| If unit has... | These checks are N/A |
|----------------|---------------------|
| No loops | LOGIC-1, PERF-1 |
| No async/threading | CONC-2, CONC-3 |
| No array access | NULL-4, NULL-5 |
| No recursion | LOGIC-6 |
| No status-returning calls | ERR-3 |
| No resource acquisition | RES-1 |

---

## Output Directory Structure

```
$BASE_DIR/
├── units.jsonl              # Raw extraction output
├── batches.json             # Batching output
└── checklists/
    ├── batch-1.md           # Filled by checker agent
    ├── batch-2.md
    ├── batch-3.md
    └── ...
```

---

## Local Development

### Alias Setup

Add to `~/.zshrc`:
```bash
alias ccf="PLUGIN_DIR=/Users/r/repos/code-foundations claude --plugin-dir /Users/r/repos/code-foundations"
```

The `PLUGIN_DIR` environment variable tells the review command to use the local repo instead of searching the plugin cache.

### Testing Flow

```bash
# 1. Source updated alias
source ~/.zshrc

# 2. Navigate to test repo
cd ~/repos/PricingAPI

# 3. Run review with local plugin
ccf
/code-foundations:review --sanity main
```

### Version Bumping

When making changes, bump version in:
- `.claude-plugin/plugin.json`
- `commands/review.md` (frontmatter + echo)
- `agents/extract-units.ts`
- `agents/orchestrate-batches.sh`
- `agents/generate-checklists.ts`

---

## Design Decisions

### Why Markdown Checklists?

1. **LLM-native:** Editing markdown is what LLMs do well. Constructing bash commands with precise flags is error-prone.

2. **Artifacts:** Checklists are reviewable documentation. You can see exactly what was checked and what wasn't.

3. **Transparency:** No black-box JSONL. Every verdict is visible with its reasoning.

4. **Simplicity:** No schema validation scripts. The template structure enforces consistency.

### Why ast-grep over tree-sitter?

1. **Rule-based extraction:** Define patterns in YAML, not code
2. **Cross-language:** Same approach works for all supported languages
3. **Faster iteration:** Change rules without rebuilding parsers

### Why TypeScript (Bun) over Bash?

1. **JSON handling:** Native, no subprocess spawning for jq
2. **Speed:** 130 units in 0.35s vs 13 units in 2.5s
3. **Maintainability:** No escaping nightmares with multi-line content

### Why File-Based Batching?

1. **Deterministic:** Same input always produces same batches
2. **Logical grouping:** Source + test files reviewed together
3. **Parallelizable:** Each batch is independent

---

## Future Considerations

### Investigation Phase (Not Yet Implemented)

After checking, findings could be verified:
- Read findings from checklists (grep for `[!]`)
- Dispatch investigation agents
- Verify each finding, provide fix or mark as false positive

### PR Profile (614 Checks)

The current implementation uses the "sanity" profile (14 checks). The full "PR" profile would:
- Load all skill checklists
- Group by check ID prefix (GC-, EH-, etc.)
- Require more sophisticated checklist generation

### Dashboard

A web-based dashboard could:
- Parse all checklist files
- Visualize findings by category
- Show coverage (checks × units)
- Link to source code

---

## Appendix: Example Session

```
❯ ccf
❯ /code-foundations:review --sanity main

⏺ code-foundations:review v3.6.6

⏺ PLUGIN_ROOT: /Users/r/repos/code-foundations

## Review Configuration

**Profile:** sanity - 14 core checks
**Target:** Branch diff against main (14 files)
**Output:** /tmp/PricingAPI-feature-2025

⏺ Extracted 130 units
⏺ Created 8 batches
⏺ Generated 8 checklists

⏺ Dispatching checker agents...
  [1/8] batch-1.md (15 units)
  [2/8] batch-2.md (57 units)
  [3/8] batch-3.md (31 units)
  ...

⏺ Review Complete

**8 batches** | **130 units** | **14 checks each**

### Results
- 🔴 Findings: 12
- ✅ Passes: 1547
- ⚪ N/A: 261

### Top Findings
- [!] ValidateOrder: FINDING line 98 - SaveAsync return value not checked
- [!] ProcessPayment: FINDING line 156 - database query inside for loop
- [!] GetUserById: FINDING line 42 - userId not checked for null
...
```
