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
| `/code-foundations:review-profile --setup` | Create or edit a profile |
| `/code-foundations:review-profile --setup security` | Create/edit named profile |
| `/code-foundations:review-profile --list` | Show all profiles |
| `/code-foundations:review-profile --use security` | Run review with profile |
| `/code-foundations:review-profile --delete security` | Delete a profile |
| `/code-foundations:review-profile` | Run with default (or setup if none) |

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
/code-foundations:review-profile --use my-profile

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

Run with: `/code-foundations:review-profile --use {PROFILE_NAME}`
Or set as default: `/code-foundations:review-profile --use {PROFILE_NAME} --set-default`
```

---

## STEP 5: EXECUTE PROFILE (Task-Driven Workflow)

Task-driven execution ensures no phases are skipped. The workflow:
1. Creates ALL tasks upfront with dependencies
2. Loops: check TaskList → execute unblocked → mark completed
3. Completes when all tasks done

### 5.1 Setup

**Generate descriptive folder name:**

First, gather context:
```bash
REPO_NAME=$(basename $(git rev-parse --show-toplevel))
BRANCH=$(git branch --show-current)
SHORT_ID=$(date +%H%M)  # Just HHMM for uniqueness
```

Then generate a descriptive name based on the changes:
```
# Look at the changed files and branch name to create a meaningful folder name
# Examples:
#   booking-trip-creation reviewing linked-pnr-validation → "booking-linked-pnr-validation-1423"
#   my-app reviewing auth changes on feature/oauth → "myapp-oauth-feature-0915"
#   api-service reviewing staged controller changes → "api-controller-updates-2201"

FOLDER_NAME = generate_name(
    repo: REPO_NAME,
    branch: BRANCH,
    changed_files: git diff --name-only,
    profile: PROFILE_NAME
)
# Format: "{repo-short}-{feature-summary}-{HHMM}"
# Keep it under 40 chars, lowercase, hyphens only
```

Create directory:
```bash
BASE_DIR="/tmp/$FOLDER_NAME"
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

### 5.3 Task-Driven Execution Loop

**Principle:** Create tasks per phase, execute, verify complete before next phase.

```python
# Main execution loop
while not all_phases_complete:
    tasks = TaskList()

    # Find unblocked pending tasks
    ready = [t for t in tasks if t.status == 'pending' and not has_incomplete_blockers(t)]

    if ready:
        # Execute all ready tasks in parallel
        for task in ready:
            TaskUpdate(task.id, status='in_progress')
        dispatch_parallel(ready)
        for task in ready:
            TaskUpdate(task.id, status='completed')

    # Check if phase complete, create next phase tasks
    check_phase_transitions()
```

---

### 5.4 Phase 1: EXTRACTION (Parallel by File Batch)

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

**Execute (parallel haiku agents):**
```
# Dispatch ALL extraction tasks in single message
# Use balanced batching to distribute work evenly
batches = split_evenly(files, NUM_BATCHES)
for batch_num, file_batch in enumerate(batches):
    Task(
        subagent_type: "general-purpose",
        model: "haiku",
        description: "Extract batch {batch_num}",
        prompt: """
        Extract semantic units from these files in {REPO_ROOT}:

        FILES: {file_batch}

        Identify functions/methods/classes with characteristics:
        has_try_catch, has_async, has_null_checks, has_validation, nesting_depth

        WRITE TO: {BASE_DIR}/extraction/batch-{batch_num}.json
        """
    )
```

**Verify & transition:**
```bash
# Confirm all batch files exist
ls $BASE_DIR/extraction/batch-*.json

# Merge into units.json
jq -s '{files: map(.files) | add}' $BASE_DIR/extraction/batch-*.json > $BASE_DIR/units.json
```

Mark all extraction tasks completed. Proceed to dependency detection.

---

### 5.4.5 Phase 1b: DEPENDENCY DETECTION

After extraction, detect project type and prepare dependency resolution for investigation.

**Create task:**
```
TaskCreate(
    subject: "Detect project dependencies",
    description: "Detect project type and prepare for external symbol resolution",
    activeForm: "Detecting dependencies"
)
```

**Execute (direct, no agent needed):**
```bash
# Detect project type
SCRIPT_DIR=$(dirname $(realpath agents/resolve-dependencies.sh))
PROJECT_TYPE=$($SCRIPT_DIR/resolve-dependencies.sh --detect {REPO_ROOT} | jq -r '.type')

# Write detection result for investigation phase
echo "{\"project_type\": \"$PROJECT_TYPE\", \"repo_root\": \"{REPO_ROOT}\"}" > $BASE_DIR/project-context.json

# Optional: Restore dependencies if not already present
# This ensures external symbols can be resolved during investigation
if [[ "$PROJECT_TYPE" != "unknown" ]]; then
    $SCRIPT_DIR/resolve-dependencies.sh --restore {REPO_ROOT} 2>/dev/null || true
fi
```

**Project types detected:**
| Type | Markers | Resolution Method |
|------|---------|-------------------|
| dotnet | `*.csproj`, `*.sln` | NuGet + ilspycmd decompile |
| java-maven | `pom.xml` | Source JARs + CFR decompile |
| java-gradle | `build.gradle` | Gradle cache + CFR decompile |
| typescript | `tsconfig.json` | node_modules (direct read) |
| python | `pyproject.toml` | site-packages |
| go | `go.mod` | GOMODCACHE |

Mark dependency detection task completed. Proceed to Phase 2.

---

### 5.5 Phase 2: CHECKING (Parallel by Skill)

**Create tasks:**
```
for skill in ENABLED_SKILLS:
    TaskCreate(
        subject: "Check: {skill}",
        description: "Run {skill} checklist",
        activeForm: "Running {skill}"
    )

for checklist in CUSTOM_CHECKLISTS:
    TaskCreate(
        subject: "Check: {checklist_name}",
        description: "Run custom checklist",
        activeForm: "Running {checklist_name}"
    )
```

**Execute (parallel, inherited model):**
```
# Dispatch ALL checking tasks in single message
for skill in ENABLED_SKILLS + CUSTOM_CHECKLISTS:
    Task(
        subagent_type: "general-purpose",
        # No model = inherits user's model
        description: "Check: {skill}",
        prompt: """
        Run {skill} checklist against extracted units.

        INPUTS:
        - Read({BASE_DIR}/units.json)
        - Read(skills/{skill}/checklists.md)  # or custom path
        - git diff {DIFF_ARGS}

        For each finding record:
        - id, file, line, severity, confidence (HIGH/LOW)
        - issue, evidence, recommendation
        - unknown (if LOW confidence)

        WRITE TO: {BASE_DIR}/checking/{skill}.json

        **IMPORTANT: For EVERY finding, create an investigation task:**
        ```
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
        ```

        All findings get investigated - confidence level informs priority, not whether to verify.
        """
    )
```

**Verify & transition:**
```bash
# Confirm all checking files exist
ls $BASE_DIR/checking/*.json
```

Mark all checking tasks completed. Investigation tasks already created by checkers.

---

### 5.6 Phase 3: INVESTIGATION (Main Agent Dispatches Directly)

**Why main agent, not orchestrator**: Main agent can dispatch multiple Task calls in a single message = true parallelism. An orchestrator subagent dispatches sequentially, creating a bottleneck.

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

**Dispatch ALL investigation agents in ONE message (true parallel):**
```
# Single message with multiple Task calls = parallel execution
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

        For EACH:
        1. Read the file and surrounding context
        2. Determine: CONFIRMED, FALSE_POSITIVE, or NEEDS_CONTEXT
        3. Explain why

        WRITE TO: {BASE_DIR}/investigation/batch-{batch_num + 1}.json
        Format: {"batch":N,"findings":[{"id":"...","verdict":"...","reason":"..."}]}
        """
    )
```

Mark all investigation tasks completed.

---

### 5.7 Phase 4: REPORT (Main Agent Dispatches Directly)

**Dispatch report agent:**
```
Task(
    subagent_type: "general-purpose",
    description: "Generate final report",
    prompt: """
    Generate the final review report.

    INPUTS:
    - Read all {BASE_DIR}/extraction/*.json for changes summary
    - Read all {BASE_DIR}/checking/*.json for findings
    - Read all {BASE_DIR}/investigation/*.json for verdicts

    TASKS:
    1. Summarize what changed (2-3 sentences + file table)
    2. Apply verdicts: CONFIRMED→Findings, FALSE_POSITIVE→remove, NEEDS_CONTEXT→Questions
    3. Group by severity (CRITICAL, IMPORTANT, SUGGESTION)
    4. Add Positive Observations section

    WRITE TO: {BASE_DIR}/REPORT.md
    """
)
)
```

Mark orchestrator task completed when done.

---

### 5.7 Terminal Summary

```markdown
## Profile Review Complete

**{PROFILE_NAME}** | **{N} files** | **{N} checks** | **{N} findings**

### Changes Summary
{Brief 2-3 sentence description of what changed and the apparent intent}

### Phases Completed
- Extraction: {N} batches
- Checking: {N} skills
- Investigation: {N} batches ({N} findings)
- Report: generated

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

### 5.9 Offer Actions

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

| Phase | Agents | Model | Distribution |
|-------|--------|-------|--------------|
| Extraction | 1 per 5 files | haiku | Scales with file count |
| Checking | 1 per skill | inherited | Creates investigation tasks |
| Investigation | 1 per 5 findings | haiku | Scales with finding count |
| Report | 1 | inherited | - |

**Main agent dispatches everything directly** - no orchestrator bottleneck. Single message with multiple Task calls = true parallelism. All findings get verified.

**Balanced batching**: Files/findings distributed evenly, not fixed sizes. Example: 13 files with 2 agents = 7 + 6, not 10 + 3.

**Example: 100 files, 10 skills, 50 total findings**
```
Main Agent
  ├─ Extraction: 1 haiku agent per 5 files
  ├─ [wait]
  ├─ Checking: 1 agent per skill (creates investigation tasks)
  ├─ [wait, then TaskList() to get investigation tasks]
  ├─ Investigation: 1 haiku agent per 5 findings
  ├─ [wait]
  └─ Report: 1 agent
```
- All dispatched by main agent (true parallelism)
- Haiku agents scale with workload - no artificial caps

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

## INTEGRATION WITH /code-foundations:review

Use profiles with `/code-foundations:review`:
```
/code-foundations:review --profile security --staged
/code-foundations:review --profile fast
```
