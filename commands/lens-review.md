---
description: "Lens-based review that executes every checklist item. One agent per skill, full evidence trail."
argument-hint: "<review-type> [--staged | files...]"
allowed-tools: ["Bash", "Glob", "Grep", "Read", "Task", "Skill", "Write", "TaskCreate", "TaskUpdate", "TaskList"]
---

# Lens Review Orchestrator

## Overview

Lens review dispatches **one agent per skill**, each executing their full checklist with evidence. This provides complete traceability of what was checked.

**Architecture:** Hybrid JSONL + TaskList coordination
- **JSONL streaming**: Units and results flow through append-only files (handles large diffs)
- **TaskList coordination**: Triage creates `triage:complete` task when done, skill agents check for it
- **Parallel execution**: Triage + all skill agents dispatch simultaneously

**Review types:**
- `review-changes` - 3 categories, 7 skills, 8 parallel agents
- `review-pr` - 5 categories, 9 skills, 10 parallel agents

---

## STEP 0: PARSE ARGUMENTS

```
REVIEW_TYPE = first argument (required: "review-changes" or "review-pr")
DIFF_ARGS = remaining arguments (--staged, files, etc.)

if REVIEW_TYPE not in ["review-changes", "review-pr"]:
  Error: "Usage: /lens-review <review-changes|review-pr> [--staged | files...]"
```

---

## STEP 1: SETUP

```bash
RUN_ID=$(date +%Y%m%d-%H%M%S)
BASE_DIR="/tmp/lens-review-$RUN_ID"

# Create output directories
mkdir -p "$BASE_DIR"/{defensive,quality,correctness,performance,documentation}
```

Read the config:
```
Read(agents/lens/config.yaml)
```

Store `RUN_ID` and review type for all subsequent steps.

---

## STEP 2: TRIAGE (AST-Based, Streaming)

Extract semantic units and stream to JSONL. Skill agents can start reading immediately.

### 2a: Dispatch Triage + Skill Agents Simultaneously

**All agents start at once.** Triage writes to `units.jsonl`, skill agents read from it.

```
# Dispatch triage agent
Task(triage, haiku, "Extract units to JSONL")

# Dispatch ALL skill agents in parallel (they'll read from units.jsonl)
Task(Lens: cc-defensive-programming, sonnet)
Task(Lens: aposd-simplifying-complexity, sonnet)
Task(Lens: aposd-reviewing-module-design, sonnet)
... (all skills for this review type)
```

### 2b: Triage Agent

```
Task(
  subagent_type: "general-purpose",
  model: "haiku",
  description: "Triage: extract to JSONL",
  prompt: """
## Triage Agent

Extract units and stream to JSONL file.

### Step 1: Run AST Extraction

```bash
cd agents/lens
./extract-units.sh {EXTRACT_ARGS}
```

### Step 2: Write Units to JSONL

For each unit, append one JSON line to `{BASE_DIR}/units.jsonl`:

```jsonl
{"file":"src/auth.ts","name":"validateInput","type":"function","lines":[10,25],"chars":{"has_try_catch":true,"has_loops":false,"has_async":false,"has_io_calls":true}}
{"file":"src/utils.ts","name":"formatDate","type":"function","lines":[5,15],"chars":{"has_try_catch":false,"has_loops":true,"has_async":false,"has_io_calls":false}}
```

### Step 3: Handle Fallback Files

For files without tree-sitter support, extract units manually and append to same JSONL.

### Step 4: Signal Completion via Task

When done extracting, create a task to signal skill agents:

```
TaskCreate(
  subject: "triage:complete",
  description: "Extraction done. {N} units in {BASE_DIR}/units.jsonl",
  metadata: {total_units: N, total_files: N}
)
```

Return: "{BASE_DIR}/units.jsonl"
"""
)
```

### 2c: Unit Schema (JSONL)

Each line in `units.jsonl`:

```json
{
  "file": "src/auth.ts",
  "name": "validateInput",
  "type": "function",
  "lines": [10, 25],
  "chars": {
    "has_try_catch": true,
    "has_loops": false,
    "has_async": false,
    "has_io_calls": true,
    "nesting_depth": 2
  }
}
```

### 2d: Routing Rules

Skill agents filter `units.jsonl` by characteristics:

| Skill | Filter |
|-------|--------|
| cc-defensive-programming | `chars.has_try_catch` OR `chars.has_io_calls` OR file in `auth/`, `security/` |
| aposd-simplifying-complexity | `chars.has_try_catch` OR `chars.has_io_calls` |
| aposd-reviewing-module-design | ALL units |
| cc-code-layout-and-style | ALL units |
| cc-control-flow-quality | `chars.nesting_depth >= 3` OR `chars.has_loops` |
| aposd-verifying-correctness | `type == "test"` OR file matches `*test*` |
| cc-quality-practices | `type == "test"` OR file matches `*test*` |
| cc-performance-tuning | `chars.has_loops` OR `chars.has_async` |
| aposd-optimizing-critical-paths | `chars.has_loops` OR `chars.has_async` |
| cc-documentation-quality | file matches `*.md`, `docs/`, `README*` |

---

## STEP 3: SKILL AGENTS (Read JSONL, Check TaskList)

Skill agents are dispatched in parallel with triage (see Step 2a). Each agent:
1. Polls `units.jsonl` for units matching their filter
2. Checks TaskList for `triage:complete` to know when extraction is done
3. Executes checklist against matching units
4. Appends results to `results.jsonl`

### Agent Prompt Template

```
Task(
  subagent_type: "general-purpose",
  description: "Lens: {SKILL}",
  prompt: """
## Lens Agent: {SKILL}

You review units from the streaming JSONL file.

### PHASE 1: LOAD SKILL

```
Skill(code-foundations:{SKILL})
Read(skills/{SKILL}/checklists.md)
```

### PHASE 2: READ UNITS

Read `{BASE_DIR}/units.jsonl` and filter for units matching your criteria:

**Your filter:** {FILTER_EXPRESSION}

Example filters:
- cc-defensive-programming: `chars.has_try_catch OR chars.has_io_calls`
- aposd-reviewing-module-design: ALL units
- cc-performance-tuning: `chars.has_loops OR chars.has_async`

Parse each line as JSON, collect matching units.

### PHASE 3: CHECK FOR COMPLETION

```
tasks = TaskList()
triage_done = any(t.subject == "triage:complete" for t in tasks)
```

If `triage_done` is false and no units yet, wait briefly and re-read JSONL.
If `triage_done` is true and no matching units, write "No units assigned - PASS" and return.

### PHASE 4: EXECUTE CHECKLIST

For each matching unit:
1. Read the full file: `Read(unit.file)`
2. Focus on lines `unit.lines[0]` to `unit.lines[1]`
3. Execute EVERY checklist item (lines starting with `- [ ]`)
4. Record PASS or FINDING for each

### PHASE 5: APPEND RESULTS

For each finding, append to `{BASE_DIR}/results.jsonl`:

```jsonl
{"skill":"{SKILL}","category":"{CATEGORY}","file":"src/auth.ts","line":15,"id":"CS-1","severity":"CRITICAL","action":"fix","issue":"...","evidence":"..."}
```

### PHASE 6: WRITE SUMMARY

Write to `{BASE_DIR}/{CATEGORY}/{SKILL}.md`:

```markdown
# Lens: {SKILL}

## Summary
- Units Reviewed: [N]
- Items Checked: [N]
- Findings: [N]
- Pass Rate: [%]

## Findings

### Fix (high confidence)
| ID | File:Line | Issue | Severity |
|----|-----------|-------|----------|

### Investigate (low confidence)
| ID | File:Line | Issue | Unknown |
|----|-----------|-------|---------|

### Plan (systemic)
| ID | Description | Topic |
|----|-------------|-------|

## Evidence Log
| ID | Check | Result | Evidence |
|----|-------|--------|----------|
```

Return: "{BASE_DIR}/{CATEGORY}/{SKILL}.md"
"""
)
```

### Dispatch (All Parallel with Triage)

**review-changes (7 skill agents + 1 triage = 8 parallel):**
```
Task(Triage, haiku)
Task(Lens: cc-defensive-programming, filter: has_try_catch OR has_io_calls)
Task(Lens: aposd-simplifying-complexity, filter: has_try_catch OR has_io_calls)
Task(Lens: aposd-reviewing-module-design, filter: ALL)
Task(Lens: cc-code-layout-and-style, filter: ALL)
Task(Lens: cc-control-flow-quality, filter: nesting_depth >= 3 OR has_loops)
Task(Lens: aposd-verifying-correctness, filter: type == test)
Task(Lens: cc-quality-practices, filter: type == test)
```

**review-pr (9 skill agents + 1 triage = 10 parallel):** Above plus:
```
Task(Lens: cc-performance-tuning, filter: has_loops OR has_async)
Task(Lens: aposd-optimizing-critical-paths, filter: has_loops OR has_async)
Task(Lens: cc-documentation-quality, filter: file matches *.md)
```

---

## STEP 4: WAIT FOR COMPLETION

All agents (triage + skills) were dispatched in parallel in Step 2a.

Wait for all Task calls to return. Each skill agent writes:
- Findings to `{BASE_DIR}/results.jsonl` (streaming, append-only)
- Summary to `{BASE_DIR}/{CATEGORY}/{SKILL}.md`

---

## STEP 5: AGGREGATE FROM RESULTS.JSONL

Read `{BASE_DIR}/results.jsonl` to aggregate findings:

```
Task(
  subagent_type: "general-purpose",
  description: "Aggregate results",
  prompt: """
Aggregate findings from results.jsonl.

Read `{BASE_DIR}/results.jsonl` - each line is:
```jsonl
{"skill":"...","category":"...","file":"...","line":N,"id":"...","severity":"...","action":"fix|investigate|plan","issue":"...","evidence":"..."}
```

### Group by Category

For each category (defensive, quality, correctness, performance, documentation):

1. Filter lines by `category`
2. Group by `action` (fix, investigate, plan)
3. Sort by `severity` (CRITICAL > IMPORTANT > SUGGESTION)

### Write Category Summaries

For each category, write `{BASE_DIR}/{CATEGORY}/summary.md`:

```markdown
# {CATEGORY} Review

## Skills Executed
| Skill | Findings |
|-------|----------|
[count findings per skill in this category]

## Findings

### Fix
| Severity | File:Line | Issue | Skill |
|----------|-----------|-------|-------|

### Investigate
| File:Line | Issue | Unknown | Skill |
|-----------|-------|---------|-------|

### Plan
| Issue | Topic | Skill |
|-------|-------|-------|

## Category Verdict: [VULNERABLE/FRAGILE/ADEQUATE/HARDENED for defensive, etc.]
```

Return: list of summary paths
"""
)
```

---

## STEP 6: FINAL REPORT

Merge all category summaries:

```markdown
# Lens Review Report

## Run Info
- **Run ID:** {RUN_ID}
- **Review Type:** {REVIEW_TYPE}
- **Files:** [count]
- **Lines:** [count]
- **Skills Executed:** [count]
- **Total Items Checked:** [count]

## Overall Verdict: [READY / NEEDS WORK / BLOCKED]

| Category | Verdict | Items | Findings |
|----------|---------|-------|----------|
| defensive | [verdict] | [N] | [N] |
| quality | [verdict] | [N] | [N] |
| correctness | [verdict] | [N] | [N] |
| performance | [verdict] | [N] | [N] |  (review-pr only)
| documentation | [verdict] | [N] | [N] |  (review-pr only)

---

## Fix (Execute Now)

[All CRITICAL/IMPORTANT findings with code fixes, grouped by file]

---

## Investigate (Need Context)

[All uncertain findings, grouped by category]

---

## Plan (Spin Off)

[All systemic issues needing /code-foundations:whiteboarding]

---

## Evidence Summary

| Category | Skill | Items | Findings |
|----------|-------|-------|----------|
[full breakdown]

Full evidence logs: {BASE_DIR}/{category}/{skill}.md
```

Write to `{BASE_DIR}/REPORT.md` and output to user.

---

## STEP 7: USER DECISION

Same as review-changes: ask user which actions to execute (Fix/Investigate/Plan).

---

## Quick Reference

| Review Type | Categories | Skills | Agents |
|-------------|------------|--------|--------|
| review-changes | 3 | 7 | 1 triage + 7 skills (parallel) + 1 aggregate = 9 |
| review-pr | 5 | 9 | 1 triage + 9 skills (parallel) + 1 aggregate = 11 |

### Coordination

| File | Purpose |
|------|---------|
| `units.jsonl` | Triage streams units here (append-only) |
| `results.jsonl` | Skill agents stream findings here (append-only) |
| TaskList: `triage:complete` | Signals extraction done |

### Agent Types

| Agent | Model | Role |
|-------|-------|------|
| Triage | haiku | Extract units, write JSONL, signal done |
| Skill (x7-9) | (inherited) | Read JSONL, filter, execute checklist, append findings |
| Aggregate | (inherited) | Read results.jsonl, write summaries |

Skill and aggregate agents inherit the user's configured model. Triage uses haiku (mechanical work).
