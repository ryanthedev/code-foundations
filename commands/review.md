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
        {label: "Quick (1-2 min)", description: "Critical issues only. 99 checks. No subagents."},
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
| **Quick** | - | - | Direct execution, no subagents |
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

### Quick Mode (Direct Execution)

No subagents. Run 99 critical checks inline.

Load the quick review checklist:
```
Read(agents/lens/quick-checklist.md)
```

Execute all 99 checks against the diff. Output findings directly, no files.

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
| `--quick` | 1-2 min | 0 | 99 | Pre-commit sanity |
| `--security` | 3-5 min | 4 | ~150 | Security-sensitive changes |
| `--design` | 3-5 min | 5 | ~250 | Refactoring, new modules |
| `--tests` | 3-5 min | 4 | ~180 | Test coverage review |
| `--full` | 5-10 min | 9 | ~550 | PR review, major features |
