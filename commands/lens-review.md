---
description: "Lens-based review that executes every checklist item. One agent per skill, full evidence trail."
argument-hint: "<review-type> [--staged | files...]"
allowed-tools: ["Bash", "Glob", "Grep", "Read", "Task", "Skill", "Write", "TaskCreate", "TaskUpdate", "TaskList"]
---

# Lens Review Orchestrator

## Overview

Lens review dispatches **one agent per skill**, each executing their full checklist with evidence. This provides complete traceability of what was checked.

**Review types:**
- `review-changes` - 3 categories, 7 skills, 7 agents
- `review-pr` - 5 categories, 9 skills, 9 agents

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

## STEP 2: TRIAGE

Get the diff and route chunks to categories:

```bash
# Determine diff command
if [[ "$DIFF_ARGS" == "--staged" ]]; then
  DIFF_CMD="git diff --cached"
elif [[ -n "$DIFF_ARGS" ]]; then
  DIFF_CMD="git diff $DIFF_ARGS"
else
  DIFF_CMD="git diff"
fi
```

Dispatch triage agent:

```
Task(
  subagent_type: "general-purpose",
  model: "haiku",
  description: "Triage diff for lens review",
  prompt: """
Triage this diff for routing to review categories.

Run: `{DIFF_CMD}` to get the full diff.

Route each file/chunk to categories based on patterns:

DEFENSIVE (error handling, security):
- Files in auth/, security/
- Code with: try, catch, error, exception, validate, sanitize, auth, token, password

QUALITY (catch-all for code structure):
- All code files not matching other patterns

CORRECTNESS (tests):
- Files: *_test.*, *.test.*, *.spec.*, test/, tests/
- Code with: test, assert, expect, mock

PERFORMANCE (review-pr only):
- Code with: loop, for, while, async, await, cache, buffer, batch
- Files in perf/, benchmark/

DOCUMENTATION (review-pr only):
- Files: *.md, docs/, README*

Write JSON files to {BASE_DIR}/:

For each category, write `{category}.json`:
```json
[
  {
    "file": "path/to/file.ext",
    "lines": [start, end],
    "description": "what this change does",
    "diff": "@@ -45,10 +45,27 @@\n actual diff hunk..."
  }
]
```

Write metadata:
```bash
echo '{"run_id":"{RUN_ID}","review_type":"{REVIEW_TYPE}","total_files":N,"total_lines":N}' > {BASE_DIR}/metadata.json
```

Return: "{BASE_DIR}"
"""
)
```

---

## STEP 3: DISPATCH SKILL AGENTS

Read the config to get skills for this review type:

```yaml
# For review-changes:
defensive: [cc-defensive-programming, aposd-simplifying-complexity]
quality: [aposd-reviewing-module-design, cc-code-layout-and-style, cc-control-flow-quality]
correctness: [aposd-verifying-correctness, cc-quality-practices]

# For review-pr, add:
performance: [cc-performance-tuning, aposd-optimizing-critical-paths]
documentation: [cc-documentation-quality]
```

**Dispatch ALL skill agents in parallel.** One Task call per skill.

### Agent Prompt Template

For each skill, use this prompt:

```
Task(
  subagent_type: "general-purpose",
  model: "sonnet",
  description: "Lens: {SKILL}",
  prompt: """
## Lens Agent: {SKILL}

You are a lens agent executing ONE skill's checklist.

### PHASE 1: LOAD

1. Load skill context:
   Skill(code-foundations:{SKILL})

2. Read checklist:
   Read(skills/{SKILL}/checklists.md)

3. Read assigned chunks:
   Read({BASE_DIR}/{CATEGORY}.json)

   If empty [], write "No chunks assigned - PASS" and return.

4. For each chunk, read full file:
   Read(chunk.file)

### PHASE 2: EXECUTE CHECKLIST

For EACH line starting with `- [ ]`:

1. Extract ID and check text
2. Apply check to all code chunks
3. Record:
   - **PASS**: One-line evidence why it passes
   - **FINDING**: File:line, evidence, severity, suggested fix

### PHASE 3: OUTPUT

Write to `{BASE_DIR}/{CATEGORY}/{SKILL}.md`:

```markdown
# Lens: {SKILL}

## Summary
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
[every checklist item with PASS/FINDING]
```

Return: "{BASE_DIR}/{CATEGORY}/{SKILL}.md"
"""
)
```

### Dispatch Order

**review-changes (7 agents):**
```
# Defensive (2 skills)
Task(Lens: cc-defensive-programming, defensive)
Task(Lens: aposd-simplifying-complexity, defensive)

# Quality (3 skills)
Task(Lens: aposd-reviewing-module-design, quality)
Task(Lens: cc-code-layout-and-style, quality)
Task(Lens: cc-control-flow-quality, quality)

# Correctness (2 skills)
Task(Lens: aposd-verifying-correctness, correctness)
Task(Lens: cc-quality-practices, correctness)
```

**review-pr (9 agents):** All above, plus:
```
# Performance (2 skills)
Task(Lens: cc-performance-tuning, performance)
Task(Lens: aposd-optimizing-critical-paths, performance)

# Documentation (1 skill)
Task(Lens: cc-documentation-quality, documentation)
```

---

## STEP 4: WAIT AND COLLECT

Wait for all agents to complete. Collect output file paths.

---

## STEP 5: SYNTHESIZE PER CATEGORY

For each category, merge skill results:

```
Task(
  subagent_type: "general-purpose",
  model: "haiku",
  description: "Merge {CATEGORY} results",
  prompt: """
Merge lens results for {CATEGORY} category.

Read all skill results:
{list of {BASE_DIR}/{CATEGORY}/{SKILL}.md files}

Create merged summary at {BASE_DIR}/{CATEGORY}/summary.md:

```markdown
# {CATEGORY} Review

## Skills Executed
| Skill | Items | Findings | Pass Rate |
|-------|-------|----------|-----------|

## All Findings

### Fix
[merged from all skills, sorted by severity]

### Investigate
[merged from all skills]

### Plan
[merged from all skills]

## Category Verdict: [from verdict_scale in config]
```

Return: "{BASE_DIR}/{CATEGORY}/summary.md"
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
| review-changes | 3 | 7 | 7 + 1 triage + 3 merge + 1 report = 12 |
| review-pr | 5 | 9 | 9 + 1 triage + 5 merge + 1 report = 16 |

Most agents are haiku (fast, cheap). Skill agents are sonnet (reasoning).
