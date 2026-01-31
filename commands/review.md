---
description: "Profile-driven code review"
argument-hint: "[--sanity | --pr | --profile <name>] [--staged | files...]"
allowed-tools: ["Bash", "Glob", "Grep", "Read", "Task", "Skill", "Write", "TaskCreate", "TaskUpdate", "TaskList", "AskUserQuestion"]
---

# Profile-Driven Review

Unified review workflow. One flow, driven by profile configuration.

```
/code-foundations:review --sanity          # 99 checks, quick pre-commit
/code-foundations:review --pr              # 548 checks, full PR review
/code-foundations:review --profile <name>  # Custom profile
```

**Manage profiles:** `/code-foundations:review-profile --setup`

---

## ARCHITECTURE

```
┌──────────────┐     ┌──────────────┐     ┌───────────────┐     ┌──────────┐
│  EXTRACTION  │ ──▶ │   CHECKING   │ ──▶ │ INVESTIGATION │ ──▶ │  REPORT  │
│   (haiku)    │     │ (per checklist)│    │    (haiku)    │     │          │
└──────────────┘     └──────────────┘     └───────────────┘     └──────────┘
     ↑                      ↑
  Batch by files       Profile-driven
  (max 5 per agent)    (1 agent per checklist)
```

**Main agent orchestrates everything** - dispatches all agents directly for true parallelism.

**Main agent MUST:**
- Parse arguments, load profiles, setup directories
- Dispatch extraction, checking, investigation, and report agents
- Merge JSON outputs between phases
- Mark investigation tasks complete after STEP 7
- Display terminal summary

**Main agent MUST NOT:**
- Read the diff content (subagents do this)
- Read changed files (subagents do this)
- Create investigation tasks (checking agents create these)

---

## STEP 0: FIND PLUGIN DIRECTORY

The plugin files are installed in a plugins directory, not the user's project. Find the plugin root first:

```
# Use Glob to find a known plugin file
Glob("**/code-foundations/agents/profiles/sanity.yaml")
```

Extract `PLUGIN_ROOT` from the result (everything before `/agents/profiles/sanity.yaml`).

Example: If Glob returns `/Users/r/.claude/plugins/code-foundations/agents/profiles/sanity.yaml`
Then `PLUGIN_ROOT = /Users/r/.claude/plugins/code-foundations`

---

## STEP 1: PARSE ARGUMENTS & LOAD PROFILE

```python
# Parse flags
if "--sanity" in args:
    PROFILE_PATH = f"{PLUGIN_ROOT}/agents/profiles/sanity.yaml"
elif "--pr" in args:
    PROFILE_PATH = f"{PLUGIN_ROOT}/agents/profiles/pr.yaml"
elif "--profile" in args:
    name = args["--profile"]
    # Try user profiles first (in project), then built-in (in plugin)
    if exists(f".code-foundations/profiles/{name}.yaml"):
        PROFILE_PATH = f".code-foundations/profiles/{name}.yaml"
    elif exists(f"{PLUGIN_ROOT}/agents/profiles/{name}.yaml"):
        PROFILE_PATH = f"{PLUGIN_ROOT}/agents/profiles/{name}.yaml"
    else:
        error(f"Profile not found: {name}")
        print("Available profiles:")
        print("  Built-in: sanity, pr")
        print("  User: /code-foundations:review-profile --list")
        exit()
else:
    # No profile specified - ask user
    goto STEP 1b: ASK FOR PROFILE
```

### STEP 1b: ASK FOR PROFILE (if no flag)

```
AskUserQuestion(
  questions: [
    {
      header: "Profile",
      question: "Which review profile do you want to use?",
      options: [
        {label: "Sanity (Recommended)", description: "99 critical checks. Quick pre-commit sanity."},
        {label: "PR", description: "548 checks across 10 skills. Full PR review."},
        {label: "Custom", description: "Use a saved profile or create one."}
      ]
    }
  ]
)
```

If "Custom" → ask for profile name or offer to run `/code-foundations:review-profile --setup`

---

## STEP 2: VALIDATE PROFILE

Load and validate the profile before executing:

```
Read({PROFILE_PATH})
```

Parse profile:
```yaml
name: <profile_name>
description: <description>
models:                    # Optional - defaults if not specified
  checking: haiku
  investigation: haiku
  report: sonnet
checklists:
  - path: <checklist_path>
    skills: [<skill1>, <skill2>]
```

**Validation:**

```python
# Extract model configuration (with defaults)
MODELS = {
    "checking": profile.get("models", {}).get("checking", "haiku"),
    "investigation": profile.get("models", {}).get("investigation", "haiku"),
    "report": profile.get("models", {}).get("report", "sonnet")
}

CHECKLISTS = []
for checklist in profile.checklists:
    # Resolve path: user paths (.code-foundations/) stay as-is, plugin paths get PLUGIN_ROOT
    if checklist.path.startswith(".code-foundations/"):
        resolved_path = checklist.path
    else:
        resolved_path = f"{PLUGIN_ROOT}/{checklist.path}"

    # Validate checklist exists
    if not file_exists(resolved_path):
        error(f"Checklist not found: {resolved_path}")
        exit()

    # Store resolved path
    checklist.resolved_path = resolved_path
    CHECKLISTS.append(checklist)

TOTAL_CHECKLISTS = len(CHECKLISTS)
```

---

## STEP 3: GET DIFF TARGET

```
AskUserQuestion(
  questions: [
    {
      header: "Target",
      question: "What do you want to review?",
      options: [
        {label: "Staged changes (Recommended)", description: "git diff --staged"},
        {label: "Unstaged changes", description: "git diff"},
        {label: "All uncommitted", description: "git diff HEAD"},
        {label: "Branch diff", description: "Your changes only (excludes merged/rebased)"}
      ]
    }
  ]
)
```

Map selection to diff command:
- Staged → `git diff --staged`
- Unstaged → `git diff`
- All uncommitted → `git diff HEAD`
- Branch diff → Uses merge-base to exclude merged/rebased changes (see below)

**Branch diff handling:**
```bash
# Detect base branch
if git rev-parse --verify main >/dev/null 2>&1; then
  BASE_BRANCH="main"
elif git rev-parse --verify master >/dev/null 2>&1; then
  BASE_BRANCH="master"
else
  BASE_BRANCH="origin/main"
fi

# Get merge-base (common ancestor) - this excludes merged-in and rebased changes
MERGE_BASE=$(git merge-base $BASE_BRANCH HEAD)

# Diff from merge-base to HEAD (your changes only)
DIFF_CMD="git diff $MERGE_BASE HEAD"
```

This ensures:
- Merge commits from upstream are excluded
- Rebased-in changes are excluded
- Only YOUR changes since branching are reviewed

---

## STEP 4: SETUP

```bash
# Generate descriptive folder name
REPO_ROOT=$(git rev-parse --show-toplevel)
REPO_NAME=$(basename "$REPO_ROOT")
BRANCH=$(git branch --show-current)
SHORT_ID=$(date +%H%M)
# Extract last component of branch name (feature/foo -> foo)
BRANCH_SHORT=$(echo "$BRANCH" | sed 's:.*/::')
FOLDER_NAME="${REPO_NAME}-${BRANCH_SHORT}-${SHORT_ID}"

# Cross-platform temp directory (works on Unix, macOS, Windows Git Bash)
if [ -n "$TMPDIR" ]; then
  TEMP_BASE="$TMPDIR"
elif [ -n "$TEMP" ]; then
  TEMP_BASE="$TEMP"
elif [ -n "$TMP" ]; then
  TEMP_BASE="$TMP"
else
  TEMP_BASE="/tmp"
fi

BASE_DIR="$TEMP_BASE/$FOLDER_NAME"
mkdir -p "$BASE_DIR/extraction"
mkdir -p "$BASE_DIR/checking"
mkdir -p "$BASE_DIR/investigation"

# Get file list (using DIFF_CMD from STEP 3)
${DIFF_CMD} --name-only > "$BASE_DIR/files.txt"
FILE_COUNT=$(wc -l < "$BASE_DIR/files.txt" | tr -d ' ')
```

**Show configuration:**

```markdown
## Review Configuration

**Profile:** {PROFILE_NAME} - {PROFILE_DESCRIPTION}
**Checklists:** {TOTAL_CHECKLISTS}
**Target:** {DIFF_ARGS} ({FILE_COUNT} files)
**Output:** {BASE_DIR}

Proceed? [Y/n]
```

---

## STEP 5: PHASE 1 - EXTRACTION (Parallel Haiku)

**Purpose:** Extract semantic units from changed files for targeted checking.

**Create tasks:**
```python
MAX_PER_AGENT = 5
NUM_BATCHES = max(1, ceil(FILE_COUNT / MAX_PER_AGENT))

for batch_num in range(NUM_BATCHES):
    TaskCreate(
        subject=f"Extract batch {batch_num + 1}",
        description=f"Extract semantic units from files",
        activeForm=f"Extracting batch {batch_num + 1}"
    )
```

**Execute (dispatch ALL in single message):**

```python
files = read_lines(f"{BASE_DIR}/files.txt")
batches = split_evenly(files, NUM_BATCHES)

# Single message with multiple Task calls = true parallelism
for batch_num, file_batch in enumerate(batches):
    Task(
        subagent_type="general-purpose",
        model="haiku",
        description=f"Extract batch {batch_num + 1}",
        prompt=f"""
## Extraction Agent

Extract semantic units from these files in {REPO_ROOT}:

FILES:
{chr(10).join(file_batch)}

### Instructions

For each file:
1. Read the file
2. Identify functions/methods/classes
3. Record characteristics:
   - has_try_catch: boolean
   - has_loops: boolean
   - has_async: boolean
   - has_io_calls: boolean
   - nesting_depth: number

### Output

Write to `{BASE_DIR}/extraction/batch-{batch_num + 1}.json`:

```json
{{
  "batch": {batch_num + 1},
  "files": [
    {{
      "path": "src/auth.ts",
      "units": [
        {{"name": "validateInput", "type": "function", "lines": [10, 25], "chars": {{...}}}}
      ]
    }}
  ]
}}
```
"""
    )
```

**Wait for all extraction agents, then merge:**

```bash
# Verify all batches completed
ls $BASE_DIR/extraction/batch-*.json | wc -l

# Merge into units.json
jq -s '{files: map(.files) | add}' $BASE_DIR/extraction/batch-*.json > $BASE_DIR/units.json
```

Mark all extraction tasks completed.

---

## STEP 6: PHASE 2 - CHECKING (Parallel per Checklist)

**Purpose:** Run each checklist against the code. One agent per checklist.

**Create tasks:**
```python
for checklist in CHECKLISTS:
    checklist_name = basename(checklist.path, ".md")
    TaskCreate(
        subject=f"Check: {checklist_name}",
        description=f"Run {checklist.path} checklist",
        activeForm=f"Running {checklist_name}"
    )
```

**Execute (dispatch ALL in single message):**

```python
for checklist in CHECKLISTS:
    checklist_name = basename(checklist.path, ".md")
    skills_to_load = checklist.skills

    Task(
        subagent_type="general-purpose",
        model=MODELS["checking"],  # From profile config (default: haiku)
        description=f"Check: {checklist_name}",
        prompt=f"""
## Checklist Agent: {checklist_name}

You are a checklist agent. Execute EVERY item in the checklist against the code.

### PHASE 1: LOAD CONTEXT

1. Load skills for persona and mental models:
{"".join(f'''
   ```
   Skill(code-foundations:{skill})
   ```
''' for skill in skills_to_load) if skills_to_load else "   (No skills - self-contained checklist)"}

2. Read the checklist:
   ```
   Read({checklist.resolved_path})
   ```

3. Read extracted units:
   ```
   Read({BASE_DIR}/units.json)
   ```

4. Get the diff:
   ```bash
   cd {REPO_ROOT}
   {DIFF_CMD}
   ```

5. Read changed files for full context.

### PHASE 2: EXECUTE CHECKLIST

For EACH checklist item (every line starting with `- [ ]`):

1. Extract the item ID and check
2. Apply the check to the code
3. Record result:
   - **PASS**: Check satisfied. One-line evidence.
   - **FINDING**: Check failed. Include file:line, evidence, confidence.

4. For EVERY finding, create an investigation task:
   ```
   TaskCreate(
     subject="Investigate: {{finding.id}}",
     description="{{finding.file}}:{{finding.line}} - {{finding.issue}}",
     activeForm="Investigating {{finding.id}}",
     metadata={{
       "finding_id": "{{finding.id}}",
       "file": "{{finding.file}}",
       "line": "{{finding.line}}",
       "issue": "{{finding.issue}}",
       "confidence": "{{finding.confidence}}",
       "checklist": "{checklist_name}"
     }}
   )
   ```

### PHASE 3: OUTPUT

Write to `{BASE_DIR}/checking/{checklist_name}.json`:

```json
{{
  "checklist": "{checklist.path}",
  "skills_loaded": {json.dumps(skills_to_load)},
  "items_checked": <count>,
  "findings": [
    {{
      "id": "SEC-1",
      "file": "src/auth.ts",
      "line": 42,
      "issue": "User input not validated",
      "confidence": "HIGH",
      "evidence": "...",
      "recommendation": "..."
    }}
  ],
  "passes": [
    {{"id": "SEC-2", "evidence": "All inputs sanitized"}}
  ]
}}
```

Return: `{BASE_DIR}/checking/{checklist_name}.json`
"""
    )
```

**Wait for all checking agents.**

Mark all checking tasks completed. Proceed directly to STEP 7 - investigation tasks were already created by checkers.

---

## STEP 7: PHASE 3 - INVESTIGATION (Parallel Haiku)

**Purpose:** Verify all findings. Reduce false positives.

**Get pending investigation tasks:**
```python
tasks = TaskList()
investigate_tasks = [t for t in tasks if t.subject.startswith("Investigate:") and t.status == "pending"]

# Deduplicate by finding_id (in case of duplicates)
seen_ids = set()
unique_tasks = []
for task in investigate_tasks:
    finding_id = task.metadata.get("finding_id")
    if finding_id and finding_id not in seen_ids:
        seen_ids.add(finding_id)
        unique_tasks.append(task)
investigate_tasks = unique_tasks
```

**Skip if no findings:**
```python
if len(investigate_tasks) == 0:
    print("No findings to investigate. Skipping to report.")
    goto STEP 8
```

**Batch and dispatch:**
```python
MAX_PER_AGENT = 5
NUM_BATCHES = max(1, ceil(len(investigate_tasks) / MAX_PER_AGENT))
batches = split_evenly(investigate_tasks, NUM_BATCHES)

# Single message with multiple Task calls = true parallelism
for batch_num, batch in enumerate(batches):
    Task(
        subagent_type="general-purpose",
        model=MODELS["investigation"],  # From profile config (default: haiku)
        description=f"Investigate batch {batch_num + 1}",
        prompt=f"""
## Investigation Agent

Investigate these findings in {REPO_ROOT}:

{chr(10).join(f'''
- **{task.metadata.finding_id}**
  Issue: {task.metadata.issue}
  File: {task.metadata.file}:{task.metadata.line}
''' for task in batch)}

### Instructions

For EACH finding:
1. Read the file and surrounding context (50 lines before/after)
2. Determine verdict:
   - **CONFIRMED**: Real issue, needs fixing
   - **FALSE_POSITIVE**: Not an issue (explain why)
   - **NEEDS_CONTEXT**: Can't determine without more info
3. Explain reasoning

### Output

Write to `{BASE_DIR}/investigation/batch-{batch_num + 1}.json`:

```json
{{
  "batch": {batch_num + 1},
  "findings": [
    {{
      "id": "SEC-1",
      "verdict": "CONFIRMED",
      "reason": "User input from request.body passed directly to SQL query without sanitization",
      "recommendation": "Use parameterized query"
    }}
  ]
}}
```
"""
    )
```

**Wait for all investigation agents.**

**Mark investigation tasks complete (main agent responsibility):**
```python
for task in investigate_tasks:
    TaskUpdate(taskId=task.id, status="completed")
```

---

## STEP 8: PHASE 4 - REPORT

**Purpose:** Generate final report merging all results.

```python
Task(
    subagent_type="general-purpose",
    model=MODELS["report"],  # From profile config (default: sonnet)
    description="Generate final report",
    prompt=f"""
## Report Agent

Generate the final review report.

### Inputs

1. Read extraction summary:
   ```
   Read({BASE_DIR}/units.json)
   ```

2. Read all checking results:
   ```bash
   ls {BASE_DIR}/checking/*.json
   ```
   Read each file.

3. Read all investigation verdicts:
   ```bash
   ls {BASE_DIR}/investigation/*.json
   ```
   Read each file.

### Tasks

1. **Changes Summary**: 2-3 sentences describing what changed and apparent intent.

2. **Apply Verdicts**:
   - CONFIRMED → Include in Findings
   - FALSE_POSITIVE → Remove (note count)
   - NEEDS_CONTEXT → Include in Questions

3. **Format Report**:

```markdown
# Review Report

**Profile:** {PROFILE_NAME}
**Files:** N files, N lines changed
**Checklists:** N checklists, N items checked
**Results:** N findings, N questions, N false positives removed

## Changes Summary

[2-3 sentences]

## Findings

1. **[ID]** file:line - Issue
   Evidence: ...
   Fix: ...

2. **[ID]** file:line - Issue
   Evidence: ...
   Fix: ...

## Questions (Need Context)

1. **[ID]** file:line - Issue
   Unknown: ...

## Positive Observations

- [Things done well]
```

### Output

Write to `{BASE_DIR}/REPORT.md`

Return: `{BASE_DIR}/REPORT.md`
"""
)
```

---

## STEP 9: TERMINAL SUMMARY

```markdown
## Review Complete

**{PROFILE_NAME}** | **{FILE_COUNT} files** | **{TOTAL_CHECKLISTS} checklists** | **{FINDING_COUNT} findings**

### Phases
- Extraction: {N} batches
- Checking: {N} checklists
- Investigation: {N} batches ({N} confirmed, {N} false positives)
- Report: generated

### Top Issues
1. **[ID]** file:line - issue
2. **[ID]** file:line - issue
3. **[ID]** file:line - issue

Full report: {BASE_DIR}/REPORT.md
```

---

## STEP 10: OFFER ACTIONS

```
AskUserQuestion(
  questions: [
    {
      header: "Action",
      question: "What would you like to do with these findings?",
      options: [
        {label: "Fix All", description: "Create a plan to fix all issues"},
        {label: "View Report", description: "Show the full report"},
        {label: "Done", description: "Exit"}
      ]
    }
  ]
)
```

**If "Fix All":**
```
Skill(code-foundations:whiteboarding, args: "Fix review findings from {BASE_DIR}/REPORT.md")
```

**If "View Report":**
```bash
cat {BASE_DIR}/REPORT.md
```

---

## PRESETS (Shortcut Flags)

| Flag | Profile | Checks |
|------|---------|--------|
| `--sanity` | `agents/profiles/sanity.yaml` | 99 |
| `--pr` | `agents/profiles/pr.yaml` | 548 |
| `--profile <name>` | User or built-in profile | Varies |

---

## PARALLELIZATION SUMMARY

| Phase | Agents | Model | Scaling |
|-------|--------|-------|---------|
| Extraction | 1 per 5 files | haiku | `ceil(files / 5)` |
| Checking | 1 per checklist | `profile.models.checking` (default: haiku) | `len(profile.checklists)` |
| Investigation | 1 per 5 findings | `profile.models.investigation` (default: haiku) | `ceil(findings / 5)` |
| Report | 1 | `profile.models.report` (default: sonnet) | Fixed |

**All dispatched by main agent** - single message with multiple Task calls = true parallelism.
