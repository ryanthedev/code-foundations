---
description: "Interactive code review - pick depth, categories, and focus areas"
argument-hint: "[--staged | files...]"
allowed-tools: ["Bash", "Glob", "Grep", "Read", "Task", "Skill", "Write", "TaskCreate", "TaskUpdate", "TaskList", "AskUserQuestion"]
---

# Interactive Review

Configurable code review. Pick your depth, categories, and focus.

---

## STEP 1: ASK USER FOR CONFIGURATION

```
AskUserQuestion(
  questions: [
    {
      header: "Depth",
      question: "How thorough should the review be?",
      options: [
        {label: "Quick (1-2 min)", description: "Critical issues only. 99 checks. 1 subagent."},
        {label: "Standard (3-5 min)", description: "3 categories, 7 skills, ~360 checks."},
        {label: "Deep (5-10 min)", description: "5 categories, 9 skills, ~550 checks."},
        {label: "Custom", description: "Pick specific categories and skills."}
      ]
    },
    {
      header: "Focus",
      question: "What matters most right now?",
      options: [
        {label: "Security & Errors", description: "Defensive programming, error handling, input validation."},
        {label: "Design Quality", description: "Module design, complexity, patterns, clarity."},
        {label: "Correctness", description: "Tests, edge cases, logic bugs."},
        {label: "All Areas", description: "Balanced review across all categories."}
      ]
    }
  ]
)
```

---

## STEP 2: MAP SELECTIONS TO CONFIG

### Depth Mapping

| Selection | Categories | Skills | Execution |
|-----------|------------|--------|-----------|
| **Quick** | - | - | 2 subagents: extraction (sonnet) + checker |
| **Standard** | defensive, quality, correctness | 7 | Parallel subagents |
| **Deep** | All 5 | 9 | Parallel subagents |
| **Custom** | → Ask follow-up | User picks | Parallel subagents |

### Focus Mapping

| Selection | Priority Categories | Priority Skills |
|-----------|--------------------|-----------------|
| **Security & Errors** | defensive | cc-defensive-programming, aposd-simplifying-complexity |
| **Design Quality** | quality | aposd-reviewing-module-design, cc-code-layout-and-style, cc-control-flow-quality |
| **Correctness** | correctness | aposd-verifying-correctness, cc-quality-practices |
| **All Areas** | (balanced) | All skills for selected depth |

---

## STEP 3: CUSTOM CATEGORY SELECTION (if Custom depth)

```
AskUserQuestion(
  questions: [
    {
      header: "Categories",
      question: "Which categories do you want to review?",
      multiSelect: true,
      options: [
        {label: "Defensive", description: "Error handling, security, input validation (2 skills, 75 checks)"},
        {label: "Quality", description: "Module design, code style, control flow (3 skills, 221 checks)"},
        {label: "Correctness", description: "Tests, edge cases, verification (2 skills, 146 checks)"},
        {label: "Performance", description: "Loops, async, optimization (2 skills, 80 checks)"}
      ]
    }
  ]
)
```

---

## STEP 4: EXECUTE BASED ON CONFIG

### Quick Mode (2 Subagents)

Dispatch extraction agent, then checker agent.

```bash
RUN_ID=$(date +%Y%m%d-%H%M%S)
BASE_DIR="/tmp/quick-review-$RUN_ID"
mkdir -p "$BASE_DIR"
```

**Agent 1: Extraction + Summary (sonnet)**

```
Task(
  subagent_type: "general-purpose",
  model: "sonnet",
  description: "Quick: extract & summarize",
  prompt: """
## Extraction & Summary Agent

Extract semantic units from the diff and provide change context for review.

### Step 1: Get the Diff

```bash
cd {REPO_ROOT}
git diff {DIFF_ARGS}
git diff {DIFF_ARGS} --stat
```

### Step 2: Understand the Change

Read the diff and write a **change summary**:
- What is being added/modified? (1-2 sentences)
- What is the purpose/intent? (infer from code, names, comments)
- What are the key risk areas? (error handling, null safety, edge cases)

### Step 3: Extract Units

For each changed file, identify:
- Functions/methods (name, lines, characteristics)
- Classes (name, lines)
- Significant code blocks

Characteristics to detect:
- has_try_catch: contains try/catch or try/except
- has_loops: contains for/while/foreach
- has_async: contains async/await
- has_null_checks: contains null/None/nil checks
- nesting_depth: max nesting level

### Step 4: Capture Key Diff Snippets

For the most important units (max 5), include the actual diff:
- New functions/methods being added
- Critical modifications to existing code
- Error handling blocks
- Validation logic

### Step 5: Write Output

Write to `{BASE_DIR}/context.json`:

```json
{
  "repo": "{REPO_ROOT}",
  "diff_args": "{DIFF_ARGS}",
  "change_summary": {
    "description": "Adding linked PNR validation for UMNR and generic linking flows",
    "purpose": "Validate that linked PNRs have matching segments and appropriate passengers",
    "risk_areas": ["null safety in LINQ queries", "empty collection handling", "external API responses"]
  },
  "files": [
    {
      "path": "src/auth.ts",
      "change_type": "added|modified",
      "units": [
        {
          "name": "validateInput",
          "type": "function",
          "lines": [10, 25],
          "chars": {...},
          "diff_snippet": "+public async Task<Result>..."
        }
      ]
    }
  ],
  "key_snippets": [
    {
      "file": "src/Handler.cs",
      "description": "Main validation logic with multiple null checks",
      "diff": "..."
    }
  ],
  "summary": {"total_files": N, "total_units": N, "total_lines": N}
}
```

Return: "{BASE_DIR}/context.json"
"""
)
```

**Agent 2: Checker (inherited model)**

```
Task(
  subagent_type: "general-purpose",
  description: "Quick: 99 checks",
  prompt: """
## Quick Checker Agent

Run 99 critical checks against extracted units with change context.

### Step 1: Load Inputs

```
Read({BASE_DIR}/context.json)
Read(agents/lens/quick-checklist.md)
```

The context.json includes:
- **change_summary**: What this change does, its purpose, and identified risk areas
- **files/units**: Semantic units with characteristics and diff snippets
- **key_snippets**: Most important code changes to focus on

### Step 2: Prioritize Based on Risk Areas

Use the `change_summary.risk_areas` to prioritize checks:
- If "null safety" is a risk → prioritize NULL-* checks
- If "error handling" is a risk → prioritize ERR-* checks
- If "async" is mentioned → prioritize CONC-* checks

### Step 3: For Each Unit

Read the source file and execute applicable checks from the 99-item checklist.

**Check applicability:**
- Security (5): All units
- Error Handling (15): Units with has_try_catch or has_async
- Null Safety (8): All units
- Logic & Control Flow (18): Units with has_loops or nesting_depth >= 2
- Design Red Flags (15): All units
- Testing (12): Test files only
- Concurrency (8): Units with has_async
- Resources (8): Units with has_try_catch or has_async
- API Quality (10): All functions/methods

Use the `diff_snippet` when available to quickly identify issues without reading full files.

### Step 4: Record Findings

For each issue found:
```json
{"id": "ERR-3", "file": "src/auth.ts", "line": 15, "severity": "CRITICAL", "issue": "...", "evidence": "..."}
```

### Step 5: Write Report

Write to `{BASE_DIR}/REPORT.md`:

```markdown
# Quick Review Report

**Run ID:** {RUN_ID}
**Target:** {DIFF_ARGS}
**Units:** [N] across [N] files

## Change Summary
[From context.json change_summary]

## Risk Areas Identified
[From context.json - what the extraction agent flagged]

## Summary
| Category | Checks | Findings |
|----------|--------|----------|
| Security | 5 | [N] |
| Error Handling | 15 | [N] |
...

## Findings

### 🔴 Critical
| ID | File:Line | Issue |
|----|-----------|-------|

### 🟡 Important
| ID | File:Line | Issue |
|----|-----------|-------|

### 🟢 Suggestions
| ID | File:Line | Issue |
|----|-----------|-------|
```

Return the report content directly.
"""
)
```

### Standard/Deep/Custom Mode

Dispatch to lens-review orchestrator:

```
Read(commands/lens-review.md)

Execute with:
- REVIEW_TYPE = "review-changes" (standard) or "review-pr" (deep)
- CATEGORIES = selected categories
- SKILLS = filtered by focus + categories
- DIFF_ARGS = pass through from user
```

---

## PRESETS (Shortcut Flags)

Support flags to skip questions:

| Flag | Equivalent To |
|------|---------------|
| `--quick` | Depth: Quick, Focus: All |
| `--security` | Depth: Standard, Focus: Security & Errors |
| `--design` | Depth: Standard, Focus: Design Quality |
| `--tests` | Depth: Standard, Focus: Correctness |
| `--full` | Depth: Deep, Focus: All |

Example:
```bash
/review --security --staged
/review --quick src/api/
/review --full
```

---

## CONFIGURATION SUMMARY

Before executing, confirm:

```markdown
## Review Configuration

**Depth:** Standard (3-5 min)
**Focus:** Security & Errors
**Categories:** defensive, quality
**Skills:**
- cc-defensive-programming
- aposd-simplifying-complexity
- aposd-reviewing-module-design (filtered to security-relevant checks)

**Target:** --staged (12 files, 340 lines)

Proceed? [Y/n]
```

---

## Quick Reference

| Preset | Time | Skills | Checks | Best For |
|--------|------|--------|--------|----------|
| `--quick` | 1-2 min | 2 agents | 99 | Pre-commit sanity |
| `--security` | 3-5 min | 4 | ~150 | Security-sensitive changes |
| `--design` | 3-5 min | 5 | ~250 | Refactoring, new modules |
| `--tests` | 3-5 min | 4 | ~180 | Test coverage review |
| `--full` | 5-10 min | 9 | ~550 | PR review, major features |
