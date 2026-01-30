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

### Standard/Deep/Custom Mode (Task-Driven Workflow)

Dispatches **one agent per skill**, each executing their full checklist with evidence.

**Architecture:** Task-driven execution loop
- **TaskCreate first**: All tasks created upfront with dependencies
- **Batched extraction**: Max 5 files per haiku agent
- **Checkers create investigation tasks**: Each finding becomes a task
- **Main agent orchestrates**: Collects from TaskList, dispatches in batches

#### Setup

```bash
# Generate descriptive folder name
REPO_NAME=$(basename $(git rev-parse --show-toplevel))
BRANCH=$(git branch --show-current)
SHORT_ID=$(date +%H%M)
# Format: "{repo-short}-{feature-summary}-{HHMM}"
FOLDER_NAME="${REPO_NAME}-${BRANCH##*/}-$SHORT_ID"

BASE_DIR="/tmp/$FOLDER_NAME"
mkdir -p "$BASE_DIR"/{extraction,checking,investigation}
```

Get file list:
```bash
git diff {DIFF_ARGS} --name-only > $BASE_DIR/files.txt
FILE_COUNT=$(wc -l < $BASE_DIR/files.txt)
```

#### Determine Skills from Depth

| Depth | Categories | Skills |
|-------|------------|--------|
| **Standard** | defensive, quality, correctness | 7 skills |
| **Deep** | All 5 | 9 skills |
| **Custom** | User-selected | Varies |

**Standard skills:**
- defensive: cc-defensive-programming, aposd-simplifying-complexity
- quality: aposd-reviewing-module-design, cc-code-layout-and-style, cc-control-flow-quality
- correctness: aposd-verifying-correctness, cc-quality-practices

**Deep adds:**
- performance: cc-performance-tuning, aposd-optimizing-critical-paths
- documentation: cc-documentation-quality

---

#### Phase 1: EXTRACTION (Batched, Parallel)

**Create tasks:**
```
# Max 5 files per haiku agent, scale agents as needed
MAX_PER_AGENT = 5
NUM_BATCHES = max(1, ceil(FILE_COUNT / MAX_PER_AGENT))
FILES_PER_BATCH = ceil(FILE_COUNT / NUM_BATCHES)  # Balanced distribution

for batch_num in range(NUM_BATCHES):
    start = batch_num * FILES_PER_BATCH
    end = min(start + FILES_PER_BATCH, FILE_COUNT)
    TaskCreate(
        subject: "Extract batch {batch_num + 1}",
        description: "Files {start + 1}-{end} ({end - start} files)",
        activeForm: "Extracting batch {batch_num + 1}"
    )
```

**Execute (dispatch ALL in single message for true parallelism):**
```
batches = split_evenly(files, NUM_BATCHES)
for batch_num, file_batch in enumerate(batches):
    Task(
        subagent_type: "general-purpose",
        model: "haiku",
        description: "Extract batch {batch_num + 1}",
        prompt: """
        Extract semantic units from these files in {REPO_ROOT}:

        FILES: {file_batch}

        For each file, identify functions/methods/classes with characteristics:
        - has_try_catch, has_loops, has_async, has_io_calls, nesting_depth

        WRITE TO: {BASE_DIR}/extraction/batch-{batch_num}.json
        Format: {"batch": N, "files": [{"path": "...", "units": [...]}]}
        """
    )
```

**Verify & merge:**
```bash
ls $BASE_DIR/extraction/batch-*.json
jq -s '{files: map(.files) | add}' $BASE_DIR/extraction/batch-*.json > $BASE_DIR/units.json
```

Mark all extraction tasks completed.

---

#### Phase 2: CHECKING (Parallel by Skill)

**Create tasks:**
```
for skill in ENABLED_SKILLS:
    TaskCreate(
        subject: "Check: {skill}",
        description: "Run {skill} checklist against extracted units",
        activeForm: "Running {skill}"
    )
```

**Execute (dispatch ALL in single message):**
```
for skill in ENABLED_SKILLS:
    Task(
        subagent_type: "general-purpose",
        description: "Check: {skill}",
        prompt: """
        Run {skill} checklist against extracted units.

        INPUTS:
        - Read({BASE_DIR}/units.json)
        - Read(skills/{skill}/checklists.md)
        - git diff {DIFF_ARGS} for actual code

        FILTER: {FILTER_FOR_SKILL}  # See routing table below

        For each finding record:
        - id, file, line, severity (CRITICAL/IMPORTANT/SUGGESTION)
        - confidence (HIGH/LOW), issue, evidence, recommendation
        - unknown (if LOW confidence)

        WRITE TO: {BASE_DIR}/checking/{skill}.json

        **CRITICAL: For EVERY finding, create an investigation task:**
        TaskCreate(
            subject: "Investigate: {finding.id}",
            description: "{finding.file}:{finding.line} - {finding.issue}",
            activeForm: "Investigating {finding.id}",
            metadata: {
                "finding_id": "{finding.id}",
                "file": "{finding.file}",
                "line": "{finding.line}",
                "issue": "{finding.issue}",
                "confidence": "{finding.confidence}",
                "severity": "{finding.severity}",
                "skill": "{skill}"
            }
        )

        ALL findings get investigated - confidence informs priority, not whether to verify.
        """
    )
```

**Routing Filters:**

| Skill | Filter |
|-------|--------|
| cc-defensive-programming | `has_try_catch` OR `has_io_calls` OR file in `auth/`, `security/` |
| aposd-simplifying-complexity | `has_try_catch` OR `has_io_calls` |
| aposd-reviewing-module-design | ALL units |
| cc-code-layout-and-style | ALL units |
| cc-control-flow-quality | `nesting_depth >= 3` OR `has_loops` |
| aposd-verifying-correctness | `type == "test"` OR file matches `*test*` |
| cc-quality-practices | `type == "test"` OR file matches `*test*` |
| cc-performance-tuning | `has_loops` OR `has_async` |
| aposd-optimizing-critical-paths | `has_loops` OR `has_async` |
| cc-documentation-quality | file matches `*.md`, `docs/`, `README*` |

Mark all checking tasks completed. Investigation tasks already created by checkers.

---

#### Phase 3: INVESTIGATION (Main Agent Dispatches)

**Why main agent**: Main agent can dispatch multiple Task calls in single message = true parallelism. Orchestrator subagent dispatches sequentially = bottleneck.

**Get pending investigation tasks:**
```
tasks = TaskList()
investigate_tasks = [t for t in tasks if t.subject.startswith("Investigate:")]
```

**Batch into groups of max 5:**
```
MAX_PER_AGENT = 5
NUM_BATCHES = ceil(len(investigate_tasks) / MAX_PER_AGENT)
batches = split_evenly(investigate_tasks, NUM_BATCHES)
```

**Dispatch ALL in ONE message (true parallel):**
```
for batch_num, batch in enumerate(batches):
    Task(
        subagent_type: "general-purpose",
        model: "haiku",
        description: "Investigate batch {batch_num + 1}",
        prompt: """
        Investigate these findings in {REPO_ROOT}:

        {for task in batch:}
        - **{task.metadata.finding_id}** [{task.metadata.severity}]
          Issue: {task.metadata.issue}
          File: {task.metadata.file}:{task.metadata.line}

        For EACH finding:
        1. Read the file and surrounding context
        2. Determine: CONFIRMED, FALSE_POSITIVE, or NEEDS_CONTEXT
        3. Explain why

        WRITE TO: {BASE_DIR}/investigation/batch-{batch_num + 1}.json
        Format: {"batch": N, "findings": [{"id": "...", "verdict": "...", "reason": "..."}]}
        """
    )
```

Mark all investigation tasks completed.

---

#### Phase 4: REPORT

**Dispatch report agent:**
```
Task(
    subagent_type: "general-purpose",
    description: "Generate final report",
    prompt: """
    Generate the final review report.

    INPUTS:
    - Read all {BASE_DIR}/extraction/*.json for file summary
    - Read all {BASE_DIR}/checking/*.json for findings
    - Read all {BASE_DIR}/investigation/*.json for verdicts

    TASKS:
    1. Summarize what changed (2-3 sentences + file table)
    2. Apply verdicts: CONFIRMED→Findings, FALSE_POSITIVE→remove, NEEDS_CONTEXT→Questions
    3. Group by severity (CRITICAL, IMPORTANT, SUGGESTION)

    WRITE TO: {BASE_DIR}/REPORT.md
    """
)
```

---

#### Terminal Summary

```markdown
## Review Complete

**{DEPTH}** | **{N} files** | **{N} skills** | **{N} findings**

### Phases Completed
- Extraction: {N} batches ({N} files)
- Checking: {N} skills ({N} findings created investigation tasks)
- Investigation: {N} batches ({N} confirmed, {N} false positives)
- Report: generated

### Results
- {N} confirmed findings
- {N} questions (need context)
- {N} false positives removed

Full report: {BASE_DIR}/REPORT.md
```

#### User Decision

Same as Quick mode: ask user which actions to execute (Fix/Investigate/Plan).

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
