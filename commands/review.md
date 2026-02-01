---
description: "Profile-driven code review"
argument-hint: "[--sanity | --pr | --profile <name>] [--staged | files...]"
allowed-tools: ["Bash", "Glob", "Grep", "Read", "Task", "Skill", "Write", "TaskCreate", "TaskUpdate", "TaskList", "AskUserQuestion"]
---

# Profile-Driven Review

Unified review workflow. One flow, driven by profile configuration.

```
/code-foundations:review --sanity          # 99 checks, quick pre-commit
/code-foundations:review --pr              # 614 checks, full PR review
/code-foundations:review --profile <name>  # Custom profile
```

**Manage profiles:** `/code-foundations:review-profile --setup`

---

## ARCHITECTURE

```
┌────────────┐   ┌────────────┐   ┌─────────────┐   ┌───────────────┐   ┌────────┐
│ EXTRACTION │ → │  CHECKING  │ → │ ORCHESTRATE │ → │ INVESTIGATION │ → │ REPORT │
│  (haiku)   │   │  (haiku)   │   │   (haiku)   │   │    (haiku)    │   │(haiku) │
└────────────┘   └────────────┘   └─────────────┘   └───────────────┘   └────────┘
      ↑                ↑                 ↑                  ↑               ↑
   Batch by        1 agent per       1 agent:           1 agent per     Verdicts
   files (5)       checklist         batches &          5 findings      only
                                     creates tasks
```

**Main agent orchestrates everything** - dispatches all agents directly for true parallelism.

**Main agent MUST:**
- Parse arguments, load profiles, setup directories
- Dispatch extraction, checking, orchestrate, investigation, and report agents
- Read TaskList() after orchestrate phase to dispatch investigation agents
- Merge JSON outputs between phases
- Display terminal summary

**Main agent MUST NOT:**
- Read the diff content (subagents do this)
- Read changed files (subagents do this)

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
        {label: "PR", description: "614 checks across 10 skills. Full PR review."},
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
  report: haiku
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
    "report": profile.get("models", {}).get("report", "haiku")
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

Process the checklist **section by section**. For each section:

1. Log the section header
2. For EACH checklist item (every line starting with `- [ ]`):
   - Extract the item ID
   - Log the check message (the question being asked)
   - Apply the check to the code
   - Record and log result:
     - **PASS**: Check satisfied. One-line evidence.
     - **FINDING**: Check failed. Include file:line, evidence, confidence, recommendation.

3. After completing the section, log a section summary:
   ```
   ## {{SECTION_NAME}}

   - {{ID-1}}: "{{check message}}" → PASS (evidence)
   - {{ID-2}}: "{{check message}}" → FINDING: {{file}}:{{line}} - {{issue}}

   Section: {{pass_count}} passed, {{finding_count}} findings
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
      "check": "Is input validated before use?",
      "file": "src/auth.ts",
      "line": 42,
      "issue": "User input not validated",
      "confidence": "HIGH",
      "evidence": "...",
      "recommendation": "..."
    }}
  ],
  "passes": [
    {{
      "id": "SEC-2",
      "check": "Are all inputs sanitized?",
      "evidence": "All inputs sanitized via sanitize() at entry points"
    }}
  ]
}}
```

Return: `{BASE_DIR}/checking/{checklist_name}.json`
"""
    )
```

**Wait for all checking agents.**

---

## STEP 7: ORCHESTRATE FINDINGS (Single Haiku)

**Purpose:** Batch findings and create investigation tasks. Main agent dispatches based on these tasks.

```python
Task(
    subagent_type="general-purpose",
    model="haiku",
    description="Orchestrate findings",
    prompt=f"""
## Orchestrator Agent

Collect all findings, deduplicate, and create investigation tasks.

### Step 1: Collect Findings

Read all checking results:
```bash
ls {BASE_DIR}/checking/*.json
```
Read each file.

### Step 2: Deduplicate

Group findings by file:line. If multiple checklists flagged the same location, keep the most specific finding.

### Step 3: Batch and Create Tasks

Create one task per batch of 5 findings:

```python
BATCH_SIZE = 5
batches = chunk(findings, BATCH_SIZE)

for batch_num, batch in enumerate(batches):
    TaskCreate(
        subject=f"Investigate: batch-{{batch_num + 1}}",
        description=f"Verify {{len(batch)}} findings",
        activeForm=f"Investigating batch {{batch_num + 1}}",
        metadata={{
            "batch": batch_num + 1,
            "findings": [
                {{
                    "id": f.id,
                    "check": f.check,
                    "file": f.file,
                    "line": f.line,
                    "issue": f.issue,
                    "confidence": f.confidence,
                    "evidence": f.evidence,
                    "recommendation": f.recommendation
                }}
                for f in batch
            ]
        }}
    )
```

### Step 4: Write Summary

Write to `{BASE_DIR}/orchestrate.json`:

```json
{{
  "total_findings": N,
  "unique_findings": N,
  "duplicates_removed": N,
  "batches_created": N,
  "findings_per_batch": [5, 5, 3]
}}
```

### Output

Return the batch count and total findings.
"""
)
```

**Wait for orchestrator. Then read tasks:**

```python
tasks = TaskList()
investigate_tasks = [t for t in tasks if t.subject.startswith("Investigate:") and t.status == "pending"]
```

**If no findings:**
```python
if len(investigate_tasks) == 0:
    print("No findings to investigate. Skipping to report.")
    goto STEP 9
```

---

## STEP 8: INVESTIGATION (Parallel Haiku)

**Purpose:** Verify findings in parallel. Each agent handles one batch. Capture code context and diff for report.

**Dispatch ALL in single message:**

```python
for task in investigate_tasks:
    batch_num = task.metadata["batch"]
    findings = task.metadata["findings"]
    files = list(set(f["file"] for f in findings))

    Task(
        subagent_type="general-purpose",
        model=MODELS["investigation"],  # From profile config (default: haiku)
        description=f"Investigate batch {batch_num}",
        prompt=f"""
## Investigation Agent

Verify these findings in {REPO_ROOT}:

### Findings to Verify

{chr(10).join(f'''
**{f["id"]}** - {f["file"]}:{f["line"]}
- Check: "{f["check"]}"
- Issue: {f["issue"]}
- Evidence: {f["evidence"]}
''' for f in findings)}

### Instructions

For EACH finding:

1. Read the file around the finding line (10 lines before, 10 lines after)
2. Get the diff hunk for that file:
   ```bash
   cd {REPO_ROOT}
   git diff {DIFF_ARGS} -U5 -- <file> | grep -A20 "^@@.*{line_number}"
   ```
3. Determine verdict:
   - **CONFIRMED**: Real issue that needs fixing
   - **FALSE_POSITIVE**: Not an issue (explain why)
   - **NEEDS_CONTEXT**: Cannot determine without more information
4. For CONFIRMED: refine the recommendation if needed
5. Capture the code context and diff hunk for the report

### Output

Write to `{BASE_DIR}/investigation/batch-{batch_num}.json`:

```json
{{
  "batch": {batch_num},
  "results": [
    {{
      "id": "SEC-1",
      "verdict": "CONFIRMED",
      "reason": "User input from request.body passed directly to SQL query",
      "recommendation": "Use parameterized query",
      "code_context": {{
        "start_line": 35,
        "lines": [
          "function handleRequest(req) {{",
          "  const id = req.body.id;",
          "  db.query(`SELECT * FROM users WHERE id = ${{id}}`);",
          "  return result;",
          "}}"
        ]
      }},
      "diff_hunk": "@@ -40,6 +42,8 @@\\n function handleRequest(req) {{\\n+  const id = req.body.id;\\n+  db.query(`SELECT...`);"
    }},
    {{
      "id": "DP-3",
      "verdict": "FALSE_POSITIVE",
      "reason": "Validation occurs in middleware before this function is called",
      "code_context": {{
        "start_line": 82,
        "lines": [
          "// Called after validateInput middleware",
          "function processData(data) {{",
          "  // data is already validated",
          "  return transform(data);",
          "}}"
        ]
      }},
      "diff_hunk": null
    }}
  ]
}}
```

**Important:** Always include `code_context` with ~10 lines around the finding. Include `diff_hunk` if the finding is in changed code, otherwise null.
"""
    )
```

**Wait for all investigation agents.**

**Mark investigation tasks complete:**
```python
for task in investigate_tasks:
    TaskUpdate(taskId=task.id, status="completed")
```

---

## STEP 9: REPORT (Single Haiku)

**Purpose:** Compile investigation results into final JSON report.

```python
Task(
    subagent_type="general-purpose",
    model=MODELS["report"],  # From profile config (default: haiku)
    description="Generate final report",
    prompt=f"""
## Report Agent

Compile investigation results into the final report JSON.

### Inputs

1. Read orchestration summary:
   ```
   Read({BASE_DIR}/orchestrate.json)
   ```

2. Read all investigation results:
   ```bash
   ls {BASE_DIR}/investigation/*.json
   ```
   Read each file.

3. Read extraction summary for file/line counts:
   ```
   Read({BASE_DIR}/units.json)
   ```

### Tasks

1. **Collect** all findings from investigation results
2. **Group** by verdict (confirmed, false_positive, needs_context)
3. **Sort** confirmed findings by file, then line number
4. **Compile** into final JSON

### Output

Write to `{BASE_DIR}/report.json`:

```json
{{
  "profile": "{PROFILE_NAME}",
  "timestamp": "2024-01-15T14:30:00Z",
  "stats": {{
    "files_reviewed": 14,
    "checklists_run": 10,
    "items_checked": 614,
    "total_findings": 7,
    "confirmed": 6,
    "false_positives": 1,
    "needs_context": 0
  }},
  "findings": [
    {{
      "id": "SEC-1",
      "verdict": "confirmed",
      "file": "src/auth.ts",
      "line": 42,
      "check": "Is input validated before use?",
      "issue": "User input not validated",
      "evidence": "req.body.id passed directly to query()",
      "recommendation": "Use parameterized query",
      "reason": "User input from request.body passed directly to SQL query",
      "code_context": {{
        "start_line": 35,
        "lines": [
          "function handleRequest(req) {{",
          "  const id = req.body.id;",
          "  db.query(`SELECT * FROM users WHERE id = ${{id}}`);",
          "  return result;",
          "}}"
        ]
      }},
      "diff_hunk": "@@ -40,6 +42,8 @@\\n function handleRequest(req) {{\\n+  const id = req.body.id;"
    }},
    {{
      "id": "DP-3",
      "verdict": "false_positive",
      "file": "src/api.ts",
      "line": 89,
      "check": "Is error handling present?",
      "issue": "Missing try-catch",
      "reason": "Validation occurs in middleware before this function is called",
      "code_context": {{
        "start_line": 82,
        "lines": [
          "// Called after validateInput middleware",
          "function processData(data) {{",
          "  return transform(data);",
          "}}"
        ]
      }},
      "diff_hunk": null
    }},
    {{
      "id": "CF-7",
      "verdict": "needs_context",
      "file": "src/utils.ts",
      "line": 156,
      "check": "Is the loop termination condition correct?",
      "issue": "Potential infinite loop",
      "reason": "Cannot determine without knowing if external service guarantees termination",
      "code_context": {{
        "start_line": 150,
        "lines": [
          "while (await fetchNext()) {{",
          "  items.push(current);",
          "  if (items.length > MAX) break;",
          "}}"
        ]
      }},
      "diff_hunk": "@@ -155,4 +156,6 @@\\n+while (await fetchNext()) {{"
    }}
  ]
}}
```

Return: `{BASE_DIR}/report.json`
"""
)
```

---

## STEP 10: TERMINAL SUMMARY

```markdown
## Review Complete

**{PROFILE_NAME}** | **{FILE_COUNT} files** | **{TOTAL_CHECKLISTS} checklists** | **{FINDING_COUNT} findings**

### Phases
- Extraction: {N} batches
- Checking: {N} checklists
- Orchestrate: {N} findings → {N} batches
- Investigation: {N} confirmed, {N} false positives, {N} need context

### Top Issues
1. **[ID]** file:line - issue
2. **[ID]** file:line - issue
3. **[ID]** file:line - issue

Output: {BASE_DIR}/report.json
```

---

## STEP 11: OFFER ACTIONS

```
AskUserQuestion(
  questions: [
    {
      header: "Action",
      question: "What would you like to do?",
      options: [
        {label: "Open Dashboard", description: "View full review in browser"},
        {label: "Fix All", description: "Create a plan to fix all issues"},
        {label: "Done", description: "Exit review"}
      ]
    }
  ]
)
```

**If "Open Dashboard":**
```bash
cp {PLUGIN_ROOT}/assets/review-dashboard.html {BASE_DIR}/
cp {PLUGIN_ROOT}/assets/report-viewer.html {BASE_DIR}/
open {BASE_DIR}/review-dashboard.html
```

**If "Fix All":**
```
Skill(code-foundations:whiteboarding, args: "Fix review findings from {BASE_DIR}/report.json")
```

**If "Other":** Handle user's custom request.

---

## PRESETS (Shortcut Flags)

| Flag | Profile | Checks |
|------|---------|--------|
| `--sanity` | `agents/profiles/sanity.yaml` | 99 |
| `--pr` | `agents/profiles/pr.yaml` | 614 |
| `--profile <name>` | User or built-in profile | Varies |

---

## PARALLELIZATION SUMMARY

| Phase | Agents | Model | Scaling |
|-------|--------|-------|---------|
| Extraction | 1 per 5 files | haiku | `ceil(files / 5)` |
| Checking | 1 per checklist | `profile.models.checking` | `len(checklists)` |
| Orchestrate | 1 | haiku | Fixed |
| Investigation | 1 per 5 findings | `profile.models.investigation` | `ceil(findings / 5)` |
| Report | 1 | `profile.models.report` | Fixed |

**All dispatched by main agent** - single message with multiple Task calls = true parallelism.

## SCALING ANALYSIS (100k Line PR)

| Phase | Agents | Context per Agent | Notes |
|-------|--------|-------------------|-------|
| Extraction | ~200 | Small (5 files) | Parallel, fast |
| Checking | 10 | Medium (units.json) | Fixed by profile |
| Orchestrate | 1 | Medium (all findings) | Just batching |
| Investigation | ~40 | Small (5 findings + files) | Bounded context |
| Report | 1 | Small (verdicts only) | No raw code |
