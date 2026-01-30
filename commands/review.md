---
description: "Interactive code review - pick depth, categories, and focus areas"
argument-hint: "[--staged | --profile <name> | files...]"
allowed-tools: ["Bash", "Glob", "Grep", "Read", "Task", "Skill", "Write", "TaskCreate", "TaskUpdate", "TaskList", "AskUserQuestion"]
---

# Interactive Review

Configurable code review. Pick your depth, categories, and focus.

**With saved profile:** `/review --profile <name>` loads from `.code-foundations/profiles/`
**Manage profiles:** `/review-profile --setup`

---

## STEP 1: ASK USER FOR CONFIGURATION

```
AskUserQuestion(
  questions: [
    {
      header: "Depth",
      question: "How thorough should the review be?",
      options: [
        {label: "Quick (2-3 min)", description: "Critical issues only. 99 checks. 3 subagents."},
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
| **Quick** | - | - | 3 subagents: extraction (haiku) → checker → reviewer |
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

### Quick Mode (3 Subagents)

Dispatch extraction → checker → reviewer pipeline.

```bash
RUN_ID=$(date +%Y%m%d-%H%M%S)
BASE_DIR="/tmp/quick-review-$RUN_ID"
mkdir -p "$BASE_DIR"
```

**Agent 1: AST Extraction (haiku)**

Fast, cheap extraction of semantic units.

```
Task(
  subagent_type: "general-purpose",
  model: "haiku",
  description: "Quick: AST extraction",
  prompt: """
## AST Extraction Agent

Extract semantic units from the diff for review.

### Step 1: Get the Diff

```bash
cd {REPO_ROOT}
git diff {DIFF_ARGS} --name-only
git diff {DIFF_ARGS} --stat
```

### Step 2: Extract Units

For each changed file, read it and identify:
- Functions/methods (name, lines, characteristics)
- Classes (name, lines)

Characteristics to detect:
- has_try_catch: contains try/catch or try/except
- has_loops: contains for/while/foreach
- has_async: contains async/await
- has_null_checks: contains ?. or ?? or null checks
- nesting_depth: max nesting level

### Step 3: Write Units

Write to `{BASE_DIR}/units.json`:

```json
{
  "repo": "{REPO_ROOT}",
  "diff_args": "{DIFF_ARGS}",
  "files": [
    {
      "path": "src/auth.ts",
      "units": [
        {"name": "validateInput", "type": "function", "lines": [10, 25], "chars": {...}}
      ]
    }
  ],
  "summary": {"total_files": N, "total_units": N}
}
```

Return: "{BASE_DIR}/units.json"
"""
)
```

**Agent 2: Checker (inherited model)**

Runs 99 checks against units, outputs findings with confidence levels.

```
Task(
  subagent_type: "general-purpose",
  description: "Quick: 99 checks",
  prompt: """
## Checker Agent

Run 99 critical checks against extracted units.

### Step 1: Load Inputs

```
Read({BASE_DIR}/units.json)
Read(agents/lens/quick-checklist.md)
```

### Step 2: For Each Unit

Read the source file and execute applicable checks.

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

### Step 3: Record Findings with Confidence

For each issue, assess confidence:
- **HIGH**: Clear violation, obvious fix
- **LOW**: Might be intentional, needs context, or uncertain

Write to `{BASE_DIR}/findings.json`:

```json
{
  "findings": [
    {
      "id": "NULL-4",
      "file": "src/Handler.cs",
      "line": 104,
      "severity": "CRITICAL",
      "confidence": "HIGH",
      "issue": "First() on potentially empty list",
      "evidence": "sortedSegments.First().DepartureDate"
    },
    {
      "id": "DESIGN-10",
      "file": "src/Adapter.cs",
      "line": 54,
      "severity": "IMPORTANT",
      "confidence": "LOW",
      "issue": "Possible code duplication across methods",
      "evidence": "Similar HTTP setup in 3 methods",
      "unknown": "May be intentional for clarity or different config needs"
    }
  ],
  "summary": {"total": N, "critical": N, "important": N, "suggestions": N, "high_confidence": N, "low_confidence": N}
}
```

Return: "{BASE_DIR}/findings.json"
"""
)
```

**Agent 3: Reviewer (inherited model)**

Reviews findings, dispatches investigators for low-confidence items, produces final report.

```
Task(
  subagent_type: "general-purpose",
  description: "Quick: review & investigate",
  prompt: """
## Reviewer Agent

Review findings, investigate low-confidence items, produce final report.

### Step 1: Load Findings

```
Read({BASE_DIR}/findings.json)
Read({BASE_DIR}/units.json)
```

### Step 2: Triage Findings

Separate findings by confidence:
- **HIGH confidence**: Ready for report as-is
- **LOW confidence**: Need investigation

### Step 3: Investigate Low-Confidence Items

For each LOW confidence finding, dispatch a focused investigator:

```
Task(
  subagent_type: "general-purpose",
  model: "haiku",
  description: "Investigate: {finding.id}",
  prompt: "Investigate this potential issue:

    **{finding.id}**: {finding.issue}
    **File:** {finding.file}:{finding.line}
    **Evidence:** {finding.evidence}
    **Unknown:** {finding.unknown}

    Read the file and surrounding context. Determine:
    1. Is this a real issue or false positive?
    2. If real, what's the impact?
    3. If false positive, why?

    Return: {verdict: 'CONFIRMED'|'FALSE_POSITIVE'|'NEEDS_CONTEXT', reason: '...', recommendation: '...'}"
)
```

Dispatch investigators in parallel for efficiency.

### Step 4: Update Findings

Based on investigation results:
- CONFIRMED → Keep finding, upgrade confidence to HIGH
- FALSE_POSITIVE → Remove from findings
- NEEDS_CONTEXT → Keep as "Investigate" action item

### Step 5: Write Full Report (for PR comments)

Write detailed report to `{BASE_DIR}/REPORT.md` with:
- Change summary (what's being modified)
- Full findings table with file:line, issue, evidence
- Investigation results with reasoning
- Code fix suggestions for each finding
- Formatted for easy copy/paste into PR comments
- NO emojis - use labels: "Findings", "Questions", "Suggestions"

### Step 6: Return Terminal Summary

Return a minimal summary for terminal display:

```
## Quick Review Complete

**[N] units** across **[N] files** | **[N] findings** ([N] false positives removed)

### Results
- [N] findings
- [N] questions
- [N] suggestions

### Top Issues
1. **[ID]** [file:line] - [one-line issue description]
2. **[ID]** [file:line] - [one-line issue description]
3. **[ID]** [file:line] - [one-line issue description]

Full report: {BASE_DIR}/REPORT.md
```

Keep it brief - no code, no tables, just the essential highlights.
"""
)
```

---

## STEP 5: OFFER TO FIX

After displaying the terminal summary, ask the user:

```
AskUserQuestion(
  questions: [
    {
      header: "Action",
      question: "What would you like to do with these findings?",
      options: [
        {label: "Fix All", description: "Create a plan to fix all critical and important issues"},
        {label: "View Report", description: "Open the full report for PR comments"},
        {label: "Done", description: "No action needed right now"}
      ]
    }
  ]
)
```

### If "Fix All" selected:

Dispatch whiteboarding session with the findings:

```
Skill(code-foundations:whiteboarding, args: "Fix review findings from {BASE_DIR}/REPORT.md")
```

The whiteboarding skill will:
1. Read the full report
2. Group related findings
3. Create an implementation plan
4. Save to `docs/plans/` for execution via `/code-foundations:building`

### If "View Report" selected:

```bash
cat {BASE_DIR}/REPORT.md
```

### If "Done" selected:

End the review.

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
| `--profile <name>` | Load saved profile from `.code-foundations/profiles/` |

Example:
```bash
/review --security --staged
/review --quick src/api/
/review --full
/review --profile my-checks --staged
```

### Profile Flag

When `--profile <name>` is used:

1. Load `.code-foundations/profiles/<name>.yaml`
2. Skip STEP 1-3 (use profile config)
3. Execute based on profile mode (quick or lens)

If profile not found, error with: `Profile not found. Run /review-profile --setup <name> to create.`

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

| Preset | Skills | Checks | Best For |
|--------|--------|--------|----------|
| `--quick` | 3 agents | 99 | Pre-commit sanity |
| `--security` | 4 | ~150 | Security-sensitive changes |
| `--design` | 5 | ~250 | Refactoring, new modules |
| `--tests` | 4 | ~180 | Test coverage review |
| `--full` | 9 | ~550 | PR review, major features |
| `--profile` | varies | varies | Your saved configuration |

**Manage profiles:** `/review-profile --setup`
