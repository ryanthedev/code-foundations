---
description: "Manage custom review profiles - create, edit, list, or run reviews with saved configurations"
argument-hint: "[--setup | --list | --use <profile> | --delete <profile>]"
allowed-tools: ["Bash", "Glob", "Grep", "Read", "Task", "Skill", "Write", "AskUserQuestion"]
---

# Review Profile

Persistent review configurations. Create once, use forever.

---

## QUICK REFERENCE

| Command | Action |
|---------|--------|
| `/review-profile --setup` | Create or edit a profile |
| `/review-profile --setup security` | Create/edit named profile |
| `/review-profile --list` | Show all profiles |
| `/review-profile --use security` | Run review with profile |
| `/review-profile --delete security` | Delete a profile |
| `/review-profile` | Run with default (or setup if none) |

---

## HOW PROFILES DRIVE PARALLELIZATION

Profiles control how many parallel agents are spawned during review.

### Profile Structure

```yaml
# .code-foundations/profiles/my-profile.yaml
name: my-profile
description: "Custom review configuration"

skills:                              # Each enabled skill = 1 checking agent
  cc-defensive-programming: true     # → Agent 1
  aposd-simplifying-complexity: true # → Agent 2
  cc-quality-practices: false        # (disabled, no agent)

custom_checklists:                   # Each custom checklist = 1 checking agent
  - .code-foundations/checklists/defensive-multidimensional.md  # → Agent 3
  - .code-foundations/checklists/owasp-top-10.md               # → Agent 4
```

### Profile → Parallel Agents

| Profile Component | Parallel Agents Spawned |
|-------------------|------------------------|
| Files in diff | ceil(files / 10) extraction agents (haiku) |
| Enabled skills | 1 checking agent per skill (your model) |
| Custom checklists | 1 checking agent per checklist (your model) |
| Low-confidence findings | 1 investigation agent per finding (haiku) |

### Scaling Examples

| Profile | Skills | Custom | Checking Agents | Checks |
|---------|--------|--------|-----------------|--------|
| `quick-sanity` | 0 | 1 | 1 | ~99 |
| `defensive-only` | 2 | 1 | 3 | ~100 |
| `standard` | 7 | 0 | 7 | ~360 |
| `deep` | 9 | 0 | 9 | ~550 |
| `mega-review` | 9 | 10 | 19 | ~1000+ |

### Execution Flow

```
/review-profile --use my-profile

Profile loaded:
  skills: [cc-defensive, aposd-simplify]
  custom: [defensive-multi, owasp-top-10]

Phase 1 - EXTRACTION (parallel by file batch)
  50 files ÷ 10 per batch = 5 haiku agents

Phase 2 - CHECKING (parallel by skill/checklist)
  2 skills + 2 custom = 4 agents (your model)
  Each agent runs their checklist against all files

Phase 3 - AGGREGATION
  1 haiku agent merges all findings

Phase 4 - INVESTIGATION (parallel by finding)
  12 low-confidence findings = 12 haiku agents

Phase 5 - REPORT
  1 agent (your model) generates final report

Total: 5 + 4 + 1 + 12 + 1 = 23 agents
```

### Task Tracking

All agents are tracked via TaskCreate/TaskUpdate:

```
Profile review: my-profile
├── Extract batch 1 .............. [completed]
├── Extract batch 2 .............. [completed]
├── Extract batch 3 .............. [completed]
├── Check: cc-defensive .......... [completed]
├── Check: aposd-simplify ........ [completed]
├── Check: defensive-multi ....... [completed]
├── Check: owasp-top-10 .......... [in_progress]
├── Aggregate findings ........... [pending]
├── Investigate: DEF-MD-4 ........ [pending]
├── Investigate: SEC-2 ........... [pending]
└── Final report ................. [pending]
```

### Adding More Checks

To scale to 1000+ checks, add more skills or custom checklists:

```yaml
# .code-foundations/profiles/comprehensive.yaml
skills:
  # All 9 built-in skills (~550 checks)
  cc-defensive-programming: true
  aposd-simplifying-complexity: true
  aposd-reviewing-module-design: true
  cc-code-layout-and-style: true
  cc-control-flow-quality: true
  aposd-verifying-correctness: true
  cc-quality-practices: true
  cc-performance-tuning: true
  aposd-optimizing-critical-paths: true

custom_checklists:
  # Add domain-specific checklists
  - .code-foundations/checklists/defensive-multidimensional.md  # 25
  - .code-foundations/checklists/owasp-top-10.md               # 50
  - .code-foundations/checklists/api-contracts.md              # 40
  - .code-foundations/checklists/data-validation.md            # 35
  - .code-foundations/checklists/async-patterns.md             # 30
```

This spawns **14 parallel checking agents**, each handling ~70 checks on average.

---

## STEP 1: PARSE ARGUMENTS

```
ARGS = parse arguments
PROFILE_DIR = ".code-foundations/profiles"

if --setup:
  PROFILE_NAME = arg or "default"
  goto STEP 2: INTERACTIVE SETUP

if --list:
  goto STEP 6: LIST PROFILES

if --use <name>:
  PROFILE_NAME = <name>
  goto STEP 5: EXECUTE PROFILE

if --delete <name>:
  goto STEP 7: DELETE PROFILE

if no args:
  if exists("{PROFILE_DIR}/default.yaml"):
    PROFILE_NAME = "default"
    goto STEP 5: EXECUTE PROFILE
  else:
    PROFILE_NAME = "default"
    goto STEP 2: INTERACTIVE SETUP
```

---

## STEP 2: INTERACTIVE SETUP

### 2.1 Load Existing (if editing)

```bash
mkdir -p .code-foundations/profiles
```

If editing existing profile, read it first:
```
Read(.code-foundations/profiles/{PROFILE_NAME}.yaml)
```

### 2.2 Choose Base Preset

```
AskUserQuestion(
  questions: [
    {
      header: "Base",
      question: "Start from which preset?",
      options: [
        {label: "Quick", description: "99 checks, 3-agent pipeline. Fast pre-commit sanity."},
        {label: "Standard", description: "360 checks, 7 skills. Balanced coverage."},
        {label: "Deep", description: "550 checks, 9 skills. Comprehensive review."},
        {label: "Custom", description: "Start empty, pick everything yourself."}
      ]
    }
  ]
)
```

**Map selection:**

| Selection | Base Config |
|-----------|-------------|
| Quick | `mode: quick` |
| Standard | `categories: [defensive, quality, correctness]` |
| Deep | `categories: [defensive, quality, correctness, performance, documentation]` |
| Custom | `categories: []` |

---

## STEP 3: CATEGORY SELECTION

Skip if Quick mode (uses 3-agent pipeline, not lens system).

```
AskUserQuestion(
  questions: [
    {
      header: "Categories",
      question: "Which review categories do you want?",
      multiSelect: true,
      options: [
        {label: "Defensive", description: "Security, error handling, input validation (2 skills, 75 checks)"},
        {label: "Quality", description: "Module design, code style, control flow (3 skills, 221 checks)"},
        {label: "Correctness", description: "Tests, edge cases, verification (2 skills, 146 checks)"},
        {label: "Performance", description: "Optimization, async, loops (2 skills, 80 checks)"}
      ]
    }
  ]
)
```

**Note:** Documentation category (26 checks) shown separately:

```
AskUserQuestion(
  questions: [
    {
      header: "Docs",
      question: "Include documentation review?",
      options: [
        {label: "Yes", description: "README, comments, API docs, CLAUDE.md (26 checks)"},
        {label: "No", description: "Skip documentation checks"}
      ]
    }
  ]
)
```

---

## STEP 4: SKILL FINE-TUNING (Optional)

```
AskUserQuestion(
  questions: [
    {
      header: "Fine-tune",
      question: "Want to enable/disable individual skills?",
      options: [
        {label: "No, use category defaults (Recommended)", description: "All skills in selected categories"},
        {label: "Yes, let me pick", description: "Choose specific skills within categories"}
      ]
    }
  ]
)
```

### If "Yes, let me pick":

Show skills grouped by selected category:

```
AskUserQuestion(
  questions: [
    {
      header: "Defensive",
      question: "Which defensive skills?",
      multiSelect: true,
      options: [
        {label: "cc-defensive-programming", description: "Error handling, assertions, input validation (38 checks)"},
        {label: "aposd-simplifying-complexity", description: "Exception design, error reduction (37 checks)"}
      ]
    }
  ]
)
```

Repeat for each selected category.

**Skill Reference:**

| Category | Skill | Checks |
|----------|-------|--------|
| **defensive** | cc-defensive-programming | 38 |
| **defensive** | aposd-simplifying-complexity | 37 |
| **quality** | aposd-reviewing-module-design | 89 |
| **quality** | cc-code-layout-and-style | 72 |
| **quality** | cc-control-flow-quality | 60 |
| **correctness** | aposd-verifying-correctness | 92 |
| **correctness** | cc-quality-practices | 54 |
| **performance** | cc-performance-tuning | 45 |
| **performance** | aposd-optimizing-critical-paths | 35 |
| **documentation** | cc-documentation-quality | 26 |

---

## STEP 4.5: REVIEW & ITERATE

Show summary and offer changes:

```markdown
## Profile Summary: {PROFILE_NAME}

**Mode:** {quick|lens}
**Categories:** {list}
**Skills:** {N} skills, ~{N} checks

| Category | Skills | Checks |
|----------|--------|--------|
| defensive | 2 | 75 |
| quality | 2 | 161 |
| correctness | 2 | 146 |
| **Total** | **6** | **~382** |
```

```
AskUserQuestion(
  questions: [
    {
      header: "Action",
      question: "What would you like to do?",
      options: [
        {label: "Save Profile", description: "Save as {PROFILE_NAME} and exit"},
        {label: "Add Skills", description: "Enable more skills or categories"},
        {label: "Remove Skills", description: "Disable some skills"},
        {label: "Start Over", description: "Reset and begin again"}
      ]
    }
  ]
)
```

**Loop until "Save Profile" selected.**

If "Add Skills" → go back to STEP 3, show unselected options
If "Remove Skills" → show currently selected, let user deselect
If "Start Over" → go to STEP 2

---

## STEP 4.6: SAVE PROFILE

Write the profile file:

```yaml
# .code-foundations/profiles/{PROFILE_NAME}.yaml
name: {PROFILE_NAME}
description: "Custom review profile"
created: {DATE}
modified: {DATE}

mode: lens  # or "quick"

categories:
  defensive: true
  quality: true
  correctness: true
  performance: false
  documentation: false

skills:
  cc-defensive-programming: true
  aposd-simplifying-complexity: true
  aposd-reviewing-module-design: true
  cc-code-layout-and-style: false
  cc-control-flow-quality: true
  aposd-verifying-correctness: true
  cc-quality-practices: true
  cc-performance-tuning: false
  aposd-optimizing-critical-paths: false
  cc-documentation-quality: false
```

```
Write(.code-foundations/profiles/{PROFILE_NAME}.yaml, profile_content)
```

Confirm:
```markdown
Profile saved: `.code-foundations/profiles/{PROFILE_NAME}.yaml`

Run with: `/review-profile --use {PROFILE_NAME}`
Or set as default: `/review-profile --use {PROFILE_NAME} --set-default`
```

---

## STEP 5: EXECUTE PROFILE (Scaled Parallel Architecture)

Designed for large diffs (100+ files) and many checks (1000+).

### 5.1 Setup

```bash
RUN_ID=$(date +%Y%m%d-%H%M%S)
BASE_DIR="/tmp/profile-review-$RUN_ID"
mkdir -p "$BASE_DIR"/{extraction,checking,investigation}
```

```
Read(.code-foundations/profiles/{PROFILE_NAME}.yaml)
```

Parse:
- `ENABLED_SKILLS` = list of enabled skills
- `CUSTOM_CHECKLISTS` = list of custom checklist paths

### 5.2 Get Diff Target

```
AskUserQuestion(
  questions: [
    {
      header: "Target",
      question: "What do you want to review?",
      options: [
        {label: "Staged changes", description: "git diff --staged"},
        {label: "Unstaged changes", description: "git diff"},
        {label: "All uncommitted", description: "git diff HEAD"},
        {label: "Branch diff", description: "Diff against main/master"}
      ]
    }
  ]
)
```

Get file list:
```bash
git diff {DIFF_ARGS} --name-only > $BASE_DIR/files.txt
FILE_COUNT=$(wc -l < $BASE_DIR/files.txt)
```

### 5.3 Create Task Hierarchy

```
TaskCreate("Profile review: {PROFILE_NAME}", "Parallel review with {N} skills, {FILE_COUNT} files")

# Extraction phase tasks (one per batch of 5-10 files)
BATCH_SIZE = 10
for batch_num in range(ceil(FILE_COUNT / BATCH_SIZE)):
  TaskCreate("Extract batch {batch_num}", "Files {start}-{end}")

# Checking phase tasks (one per skill + custom checklists)
for skill in ENABLED_SKILLS:
  TaskCreate("Check: {skill}", "Run checklist against all units")
for checklist in CUSTOM_CHECKLISTS:
  TaskCreate("Check: {checklist_name}", "Run custom checklist")

# Set dependencies: checking blocked by all extraction
TaskUpdate(each checking task, addBlockedBy: [all extraction task IDs])

# Aggregation task
TaskCreate("Aggregate findings", "Merge, dedupe, identify low-confidence")
TaskUpdate(aggregation task, addBlockedBy: [all checking task IDs])

# Investigation tasks created dynamically after aggregation
# Report task created after investigation
```

---

### 5.4 Phase 1: EXTRACTION (Parallel by File Batch)

Dispatch parallel haiku agents, one per batch of 5-10 files.

```
for batch_num, file_batch in enumerate(batched(files, BATCH_SIZE)):
  TaskUpdate(extraction_task[batch_num], status: "in_progress")

  Task(
    subagent_type: "general-purpose",
    model: "haiku",
    description: "Extract batch {batch_num}",
    prompt: """
    Extract semantic units from these files in {REPO_ROOT}:

    FILES:
    {file_batch as newline-separated list}

    For each file, read it and identify:
    - Functions/methods (name, line range, characteristics)
    - Classes (name, line range)

    Characteristics: has_try_catch, has_loops, has_async, has_null_checks,
    has_validation, has_logging, nesting_depth

    Write to: {BASE_DIR}/extraction/batch-{batch_num}.json

    Format:
    {"batch": N, "files": [{"path": "...", "units": [...]}]}
    """
  )
```

**Dispatch all extraction agents in parallel (single message, multiple Task calls).**

Wait for all extraction tasks to complete, then merge:

```bash
# Merge all batch files into single units.json
jq -s '{files: map(.files) | add}' $BASE_DIR/extraction/batch-*.json > $BASE_DIR/units.json
```

Mark extraction tasks completed, unblock checking tasks.

---

### 5.5 Phase 2: CHECKING (Parallel by Skill)

Dispatch parallel agents (inherited model), one per skill.

```
for skill in ENABLED_SKILLS:
  TaskUpdate(checking_task[skill], status: "in_progress")

  Task(
    subagent_type: "general-purpose",
    # No model specified = inherits user's model
    description: "Check: {skill}",
    prompt: """
    Run {skill} checklist against extracted units.

    INPUTS:
    - Read({BASE_DIR}/units.json) for semantic units
    - Read(skills/{skill}/checklists.md) for checklist
    - git diff {DIFF_ARGS} for actual code

    For each unit, apply applicable checklist items.

    For each finding, record:
    - id: checklist item ID
    - file, line, severity (CRITICAL/IMPORTANT/SUGGESTION)
    - confidence: HIGH (clear violation) or LOW (needs context)
    - issue, evidence, recommendation
    - unknown: what context is missing (if LOW confidence)

    Write to: {BASE_DIR}/checking/{skill}.json

    Format:
    {"skill": "{skill}", "findings": [...], "summary": {...}}
    """
  )

# Also dispatch custom checklists
for checklist_path in CUSTOM_CHECKLISTS:
  checklist_name = basename(checklist_path)
  Task(
    subagent_type: "general-purpose",
    description: "Check: {checklist_name}",
    prompt: """
    Run custom checklist against extracted units.

    INPUTS:
    - Read({BASE_DIR}/units.json)
    - Read({checklist_path})
    - git diff {DIFF_ARGS}

    Write to: {BASE_DIR}/checking/{checklist_name}.json
    """
  )
```

**Dispatch all checking agents in parallel.**

Wait for all checking tasks to complete.

---

### 5.6 Phase 3: AGGREGATION

Single haiku agent merges all findings.

```
TaskUpdate(aggregation_task, status: "in_progress")

Task(
  subagent_type: "general-purpose",
  model: "haiku",
  description: "Aggregate findings",
  prompt: """
  Merge all findings from checking phase.

  INPUT: Read all files in {BASE_DIR}/checking/*.json

  TASKS:
  1. Combine all findings into single list
  2. Deduplicate (same file:line + same issue = keep higher severity)
  3. Sort by: severity (CRITICAL first), then file, then line
  4. Separate HIGH vs LOW confidence
  5. Count totals

  Write to: {BASE_DIR}/all-findings.json

  Format:
  {
    "high_confidence": [...],
    "low_confidence": [...],
    "summary": {
      "total": N, "critical": N, "important": N, "suggestion": N,
      "high_confidence_count": N, "low_confidence_count": N
    }
  }
  """
)
```

After aggregation, create investigation tasks:

```
findings = Read({BASE_DIR}/all-findings.json)
for finding in findings.low_confidence:
  TaskCreate("Investigate: {finding.id}", "Verify {finding.file}:{finding.line}")
```

---

### 5.7 Phase 4: INVESTIGATION (Parallel by Finding)

Dispatch parallel haiku investigators for each low-confidence finding.

```
for finding in low_confidence_findings:
  TaskUpdate(investigation_task[finding.id], status: "in_progress")

  Task(
    subagent_type: "general-purpose",
    model: "haiku",
    description: "Investigate: {finding.id}",
    prompt: """
    Investigate this potential issue in {REPO_ROOT}:

    **{finding.id}**: {finding.issue}
    **File:** {finding.file}:{finding.line}
    **Evidence:** {finding.evidence}
    **Unknown:** {finding.unknown}

    Read the file and surrounding context. Determine:
    1. Is this a real issue or false positive?
    2. If real, what's the impact?
    3. If false positive, why?

    Write to: {BASE_DIR}/investigation/{finding.id}.json

    Format:
    {"id": "{finding.id}", "verdict": "CONFIRMED|FALSE_POSITIVE|NEEDS_CONTEXT",
     "reason": "...", "recommendation": "..."}
    """
  )
```

**Dispatch all investigators in parallel.**

Wait for all investigation tasks to complete.

---

### 5.8 Phase 5: FINAL REPORT

Single agent (inherited model) produces the report.

```
Task(
  subagent_type: "general-purpose",
  description: "Generate final report",
  prompt: """
  Generate the final review report.

  INPUTS:
  - Read({BASE_DIR}/all-findings.json)
  - Read all {BASE_DIR}/investigation/*.json

  TASKS:
  1. Update findings based on investigation verdicts:
     - CONFIRMED → keep, upgrade to HIGH confidence
     - FALSE_POSITIVE → remove
     - NEEDS_CONTEXT → move to "Questions" section
  2. Group by action type: Findings, Questions, Suggestions
  3. Write full report with code evidence and fix recommendations

  Write to: {BASE_DIR}/REPORT.md

  NO emojis. Use labels: "Findings", "Questions", "Suggestions".

  Also return terminal summary (counts + top 3 issues only).
  """
)
```

Mark all tasks completed.

---

### 5.9 Terminal Summary

```markdown
## Profile Review Complete

**{PROFILE_NAME}** | **{N} files** | **{N} checks** | **{N} findings**

Parallel execution: {N} extraction + {N} checking + {N} investigation agents

### Results
- {N} findings
- {N} questions
- {N} suggestions
- {N} false positives removed

### Top Issues
1. **[ID]** file:line - issue
2. **[ID]** file:line - issue
3. **[ID]** file:line - issue

Full report: {BASE_DIR}/REPORT.md
```

### 5.10 Offer Actions

```
AskUserQuestion(
  questions: [
    {
      header: "Action",
      question: "What would you like to do?",
      options: [
        {label: "Fix All", description: "Create plan to fix all issues"},
        {label: "View Report", description: "Show full report"},
        {label: "Done", description: "Exit"}
      ]
    }
  ]
)
```

If "Fix All" → `Skill(code-foundations:whiteboarding, args: "Fix findings from {BASE_DIR}/REPORT.md")`

---

## Parallelization Summary

| Phase | Agents | Model | Parallelization |
|-------|--------|-------|-----------------|
| Extraction | ceil(files/10) | haiku | By file batch |
| Checking | len(skills) + len(custom) | inherited | By skill |
| Aggregation | 1 | haiku | Sequential |
| Investigation | len(low_confidence) | haiku | By finding |
| Report | 1 | inherited | Sequential |

**Example scaling:**
- 100 files, 10 skills, 20 low-confidence findings
- Extraction: 10 parallel haiku agents
- Checking: 10 parallel agents (your model)
- Investigation: 20 parallel haiku agents
- Total: 40 parallel agents (vs 3 sequential before)

---

## STEP 6: LIST PROFILES

```bash
ls -la .code-foundations/profiles/
```

For each profile, show summary:

```markdown
## Available Profiles

| Profile | Mode | Skills | Checks | Modified |
|---------|------|--------|--------|----------|
| default | lens | 6 | ~382 | 2026-01-29 |
| security | lens | 2 | 75 | 2026-01-28 |
| quick-check | quick | 3 agents | 99 | 2026-01-27 |

**Presets (built-in):**
- `quick` - 99 checks, 3-agent pipeline
- `standard` - 360 checks, 7 skills
- `deep` - 550 checks, 9 skills
```

---

## STEP 7: DELETE PROFILE

```
AskUserQuestion(
  questions: [
    {
      header: "Confirm",
      question: "Delete profile '{PROFILE_NAME}'?",
      options: [
        {label: "Yes, delete it", description: "Remove .code-foundations/profiles/{PROFILE_NAME}.yaml"},
        {label: "No, keep it", description: "Cancel deletion"}
      ]
    }
  ]
)
```

If confirmed:
```bash
rm .code-foundations/profiles/{PROFILE_NAME}.yaml
```

---

## INTEGRATION WITH /review

Use profiles with `/review`:
```
/review --profile security --staged
/review --profile fast
```
