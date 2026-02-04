---
description: "Profile-driven code review"
argument-hint: "[--sanity | --pr | --profile <name>] [--staged | files...]"
allowed-tools: ["Bash", "Glob", "Grep", "Read", "Task", "Skill", "Write", "TaskCreate", "TaskUpdate", "TaskList", "AskUserQuestion"]
version: "3.5.0"
---

# Profile-Driven Review

**FIRST: Output this exact line before doing anything else:**
```
code-foundations:review v3.5.0
```

Unified review workflow. One flow, driven by profile configuration.

```
/code-foundations:review --sanity          # 99 checks, quick pre-commit
/code-foundations:review --pr              # 614 checks, full PR review
/code-foundations:review --profile <name>  # Custom profile
```

**Manage profiles:** `/code-foundations:review-profile --setup`

---

## ARCHITECTURE

### Sanity Profile (--sanity)

```
┌────────────┐   ┌─────────────┐   ┌───────────┐   ┌───────────────┐
│ EXTRACTION │ → │ ORCHESTRATE │ → │ CHECKING  │ → │ INVESTIGATION │
│  (script)  │   │   (bash)    │   │ (sonnet)  │   │   (sonnet)    │
└────────────┘   └─────────────┘   └───────────┘   └───────────────┘
      ↓                 ↓                 ↓                  ↓
  tree-sitter     7-step batching  1 agent per      1 agent per
  + diff parse    (deterministic)  batch, runs      5 findings,
                                   14 core checks   provides fixes
```

- **14 core checks** distilled via 7-agent consensus
- **Intelligent batching** by directory, size, dependencies
- **Schema enforced** via add-finding.sh / add-verdict.sh

### PR Profile (--pr)

```
┌────────────┐   ┌─────────────┐   ┌───────────┐   ┌─────────────┐   ┌───────────────┐
│ EXTRACTION │ → │ CHECK ORCH  │ → │ CHECKING  │ → │ ORCHESTRATE │ → │ INVESTIGATION │
│  (haiku)   │   │   (haiku)   │   │ (sonnet)  │   │   (haiku)   │   │   (sonnet)    │
└────────────┘   └─────────────┘   └───────────┘   └─────────────┘   └───────────────┘
      ↑                ↑                 ↑                ↑                  ↑
   Batch by        Group by         1 agent per      Dedupe &          1 agent per
   files (5)       ID prefix        prefix group     batch             5 findings
                   (GC-, EH-...)    + skills
```

- **614 checks** across 10 skill checklists
- **Prefix-based grouping** (GC-, EH-, OP-, etc.)
- **Skill loading** per check group

**Main agent orchestrates everything** - dispatches all agents directly for true parallelism.

**Main agent MUST:**
- Parse arguments, load profiles, setup directories
- Dispatch extraction, checking, orchestrate, and investigation agents
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
checklists:
  - path: <checklist_path>
    skills: [<skill1>, <skill2>]
```

**Validation:**

```python
# Extract parallelism configuration (default: 5)
MAX_PARALLELISM = profile.get("max_parallelism", 5)  # 0 means unlimited

# Extract model configuration (with defaults)
MODELS = {
    "checking": profile.get("models", {}).get("checking", "haiku"),
    "investigation": profile.get("models", {}).get("investigation", "haiku")
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

## STEP 4.5: CREATE PHASE TASKS

**Create all phase tasks upfront.** This enforces the flow - agent cannot skip phases.

```python
if PROFILE_NAME == "sanity":
    # Sanity flow phases
    TaskCreate(subject="Phase 1: Extraction", description="Extract semantic units from files", activeForm="Extracting units")
    TaskCreate(subject="Phase 2: Orchestrate", description="Build intelligent batches from units", activeForm="Orchestrating review")
    TaskCreate(subject="Phase 3: Checking", description="Run 14 core checks on each batch", activeForm="Running checks")
    TaskCreate(subject="Phase 4: Collect Findings", description="Parse checker output, count findings", activeForm="Collecting findings")
    TaskCreate(subject="Phase 5: Investigation", description="Verify findings, provide fixes", activeForm="Investigating findings")
    TaskCreate(subject="Phase 6: Summary", description="Display results, offer actions", activeForm="Generating summary")
else:
    # PR flow phases
    TaskCreate(subject="Phase 1: Extraction", description="Extract semantic units from files", activeForm="Extracting units")
    TaskCreate(subject="Phase 2: Check Orchestrate", description="Parse checklists, group by prefix", activeForm="Orchestrating checks")
    TaskCreate(subject="Phase 3: Checking", description="Run checks per prefix group", activeForm="Running checks")
    TaskCreate(subject="Phase 4: Orchestrate Findings", description="Dedupe, batch findings", activeForm="Orchestrating findings")
    TaskCreate(subject="Phase 5: Investigation", description="Verify findings, provide fixes", activeForm="Investigating findings")
    TaskCreate(subject="Phase 6: Summary", description="Display results, offer actions", activeForm="Generating summary")
```

**Each phase MUST:**
1. `TaskUpdate(taskId=phase_id, status="in_progress")` before starting
2. Do its work
3. `TaskUpdate(taskId=phase_id, status="completed")` when done
4. Check `TaskList()` to confirm next phase is ready

---

## STEP 4.6: BRANCH BY PROFILE TYPE

```python
if PROFILE_NAME == "sanity":
    goto SANITY_FLOW
else:
    goto PR_FLOW  # STEP 5
```

---

# SANITY FLOW (14 core checks, intelligent batching)

---

## SANITY STEP 1: EXTRACTION (Single Script Call)

**Purpose:** Extract semantic units from changed files using tree-sitter extraction.

**Mark phase in_progress:**

```python
tasks = TaskList()
phase1_id = next(t.id for t in tasks if "Phase 1" in t.subject)
TaskUpdate(taskId=phase1_id, status="in_progress")
```

**Execute extraction script:**

```bash
# Define script path and output location
SCRIPT_PATH="{PLUGIN_ROOT}/agents/extract-with-diff.sh"
OUTPUT_FILE="{BASE_DIR}/units.jsonl"

# Execute extraction script from repository root
cd "{REPO_ROOT}" && "{SCRIPT_PATH}" {DIFF_ARGS} > "{OUTPUT_FILE}" 2>&1
EXIT_CODE=$?

# Handle errors
if [ $EXIT_CODE -ne 0 ]; then
  echo "Extraction failed. Exit code: $EXIT_CODE"
  echo "Check that tree-sitter-cli is installed: npm install -g tree-sitter-cli"
  echo "Script output shown above"
  exit 1
fi

# Verify output exists and count units
if [ ! -f "{OUTPUT_FILE}" ] || [ ! -s "{OUTPUT_FILE}" ]; then
  FILE_COUNT=$(wc -l < "{BASE_DIR}/files.txt" | tr -d ' ')
  if [ "$FILE_COUNT" -eq 0 ]; then
    echo "No files to extract. Review target has no changes."
  else
    echo "Extraction produced no units from $FILE_COUNT files."
    echo "This may indicate unsupported file types or extraction error."
  fi
else
  UNIT_COUNT=$(wc -l < "{OUTPUT_FILE}" | tr -d ' ')
  echo "Extracted $UNIT_COUNT units from changed files."
fi
```

**Mark phase complete:**

```python
TaskUpdate(taskId=phase1_id, status="completed")
```

---

## SANITY STEP 2: ORCHESTRATE (Bash Script)

**Purpose:** Build intelligent batches from extracted units using deterministic algorithm.

**Mark phase in_progress:**

```python
tasks = TaskList()
phase2_id = next(t.id for t in tasks if "Phase 2" in t.subject)
TaskUpdate(taskId=phase2_id, status="in_progress")
```

**Execute orchestrator script:**

```bash
# Run batching algorithm (7-step: skip → test pairs → call graph → directory → layer → stragglers)
ORCH_SCRIPT="{PLUGIN_ROOT}/agents/orchestrate-batches.sh"
cat "{BASE_DIR}/units.jsonl" | "$ORCH_SCRIPT" > "{BASE_DIR}/checking-batches.json"

# Verify output
if [ ! -s "{BASE_DIR}/checking-batches.json" ]; then
  echo "Orchestration produced no batches"
  exit 1
fi

BATCH_COUNT=$(jq 'length' "{BASE_DIR}/checking-batches.json")
echo "Created $BATCH_COUNT batches"
```

**Read result and mark phase complete:**

```python
BATCHES = read_json(f"{BASE_DIR}/checking-batches.json")
NUM_BATCHES = len(BATCHES)

TaskUpdate(taskId=phase2_id, status="completed")
```

---

## SANITY STEP 3: CHECKING (1 Agent per Batch)

**Purpose:** Run 14 core checks against each unit in the batch. Diffs are provided inline.

**Mark phase in_progress:**

```python
tasks = TaskList()
phase3_id = next(t.id for t in tasks if "Phase 3" in t.subject)
TaskUpdate(taskId=phase3_id, status="in_progress")
```

**Execute (respect MAX_PARALLELISM):**

```python
# Split into waves
if MAX_PARALLELISM == 0:
    waves = [BATCHES]
else:
    waves = [BATCHES[i:i+MAX_PARALLELISM]
             for i in range(0, len(BATCHES), MAX_PARALLELISM)]

for wave in waves:
    for batch in wave:
        Task(
            subagent_type="code-foundations:checker-agent",
            description=f"Check batch {batch['id']}",
            prompt=f"""
BATCH: {batch['id']}
PLUGIN_ROOT: {PLUGIN_ROOT}
BASE_DIR: {BASE_DIR}

SKILLS:
- cc-defensive-programming
- cc-control-flow-quality
- aposd-verifying-correctness
- cc-performance-tuning

CHECKS (14 core):
- ERR-3: Are all error-return codes checked?
- ERR-8: Are partial failures handled (rollback, cleanup)?
- NULL-2: Does code check for null before use?
- NULL-4: Are array indexes within bounds?
- NULL-5: Are array references free of off-by-one errors?
- NULL-6: What happens with empty input?
- LOGIC-1: Does the loop end under all conditions?
- LOGIC-6: Does recursive code have a path to stop?
- LOGIC-11: Are all cases covered in switch/if-else?
- LOGIC-15: No accidental assignment in conditionals?
- CONC-2: Is each shared access point protected?
- CONC-3: Are there no TOCTOU race conditions?
- RES-1: Does every acquire have corresponding release?
- PERF-1: Are database queries not in loops (N+1)?

UNITS:
{chr(10).join(f'''
**{u['name']}** ({u['type']}) - {u['file']}:{u['lines'][0]}-{u['lines'][1]}
- has_loops: {u.get('has_loops', False)}, has_async: {u.get('has_async', False)}, has_try_catch: {u.get('has_try_catch', False)}
- summary: {u.get('summary', 'N/A')}
```diff
{u['diff']}
```
''' for u in batch['units'])}
"""
        )
    # WAIT for wave to complete
```

**Wait for all checker agents, then mark phase complete:**

```python
TaskUpdate(taskId=phase3_id, status="completed")
```

---

## SANITY STEP 4: COLLECT FINDINGS

**Mark phase in_progress, then read findings from JSONL:**

```python
tasks = TaskList()
phase4_id = next(t.id for t in tasks if "Phase 4" in t.subject)
TaskUpdate(taskId=phase4_id, status="in_progress")
```

```bash
# Count findings
FINDING_COUNT=$(grep -c '"verdict":"FINDING"' "$BASE_DIR/findings.jsonl" 2>/dev/null || echo "0")

# Extract just the FINDINGs for investigation
jq -c 'select(.verdict == "FINDING")' "$BASE_DIR/findings.jsonl" > "$BASE_DIR/to-investigate.jsonl"
```

```python
TaskUpdate(taskId=phase4_id, status="completed")

if FINDING_COUNT == 0:
    print("No findings. Skipping investigation.")
    goto SANITY_STEP_6
```

---

## SANITY STEP 5: INVESTIGATION (1 Agent per 5 Findings)

**Mark phase in_progress:**

```python
tasks = TaskList()
phase5_id = next(t.id for t in tasks if "Phase 5" in t.subject)
TaskUpdate(taskId=phase5_id, status="in_progress")
```

**Read findings and batch:**

```bash
# Read findings into array (one per line)
mapfile -t FINDINGS < "$BASE_DIR/to-investigate.jsonl"
FINDING_COUNT=${#FINDINGS[@]}
```

```python
# Batch into groups of 5
BATCH_SIZE = 5
finding_batches = [FINDINGS[i:i+BATCH_SIZE] for i in range(0, len(FINDINGS), BATCH_SIZE)]
```

**Dispatch investigation agents (respecting MAX_PARALLELISM):**

```python
for wave in waves:
    for batch_num, findings_batch in wave:
        Task(
            subagent_type="code-foundations:investigation-agent",
            model=MODELS["investigation"],
            description=f"Investigate batch {batch_num}",
            prompt=f"""
## Investigation Agent: Batch {batch_num}

Verify each finding and provide fixes.

### Findings to Investigate

{chr(10).join(findings_batch)}

### Instructions

For EACH finding:
1. Read the file around the finding line (20 lines context)
2. Determine verdict:
   - **CONFIRMED**: Real issue that needs fixing
   - **FALSE_POSITIVE**: Not an issue (explain why)
   - **NEEDS_CONTEXT**: Cannot determine without more info

3. For CONFIRMED findings, provide a fix

### Output via add-verdict.sh

**Use the add-verdict.sh script for EVERY finding.** This enforces the schema.

```bash
SCRIPT="{PLUGIN_ROOT}/agents/add-verdict.sh"
export BASE_DIR="{BASE_DIR}"
```

For each finding, call the script:

```bash
# CONFIRMED (requires fix fields)
$SCRIPT --finding-id "batch-1-NULL-4" --file "src/foo.ts" --line 42 --check-id "NULL-4" \\
  --verdict "CONFIRMED" --reason "Array accessed without bounds check" \\
  --explanation "Add bounds check before array access" \\
  --old-string "items[0]" --new-string "items.length > 0 ? items[0] : null"

# FALSE_POSITIVE
$SCRIPT --finding-id "batch-1-ERR-3" --file "src/foo.ts" --line 50 --check-id "ERR-3" \\
  --verdict "FALSE_POSITIVE" --reason "Error is handled in caller via Result type"

# NEEDS_CONTEXT
$SCRIPT --finding-id "batch-1-CONC-2" --file "src/foo.ts" --line 60 --check-id "CONC-2" \\
  --verdict "NEEDS_CONTEXT" --reason "Unclear if this runs in multi-threaded context" \\
  --question "Is this service accessed concurrently?"
```

**The script will error if:**
- Required fields are missing
- Verdict is not CONFIRMED, FALSE_POSITIVE, or NEEDS_CONTEXT
- CONFIRMED is missing fix fields

All results go to `{BASE_DIR}/verdicts.jsonl`.

Return: "Batch {batch_num} complete: X verdicts added"
"""
        )
```

**Wait for all investigation agents, then mark complete:**

```python
TaskUpdate(taskId=phase5_id, status="completed")
```

---

## SANITY STEP 6: TERMINAL SUMMARY

**Mark phase in_progress:**

```python
tasks = TaskList()
phase6_id = next(t.id for t in tasks if "Phase 6" in t.subject)
TaskUpdate(taskId=phase6_id, status="in_progress")
```

**Collect findings, generate dashboard, display summary:**

```python
# Read verdicts from JSONL
verdicts = []
for line in read_lines(f"{BASE_DIR}/verdicts.jsonl"):
    verdicts.append(json.loads(line))

confirmed = [v for v in verdicts if v["verdict"] == "CONFIRMED"]
false_positives = [v for v in verdicts if v["verdict"] == "FALSE_POSITIVE"]
needs_context = [v for v in verdicts if v["verdict"] == "NEEDS_CONTEXT"]
findings = verdicts  # All verdicts are findings for dashboard
```

**Generate dashboard (inline, no agent):**

```python
# Build review data
review_data = {
    "profile": PROFILE_NAME,
    "timestamp": datetime.now().isoformat(),
    "stats": {
        "files_reviewed": FILE_COUNT,
        "checks_run": 14,
        "confirmed": len(confirmed),
        "false_positives": len(false_positives),
        "needs_context": len(needs_context)
    },
    "findings": findings
}

# Read dashboard template, inject data, write to BASE_DIR
html = Read(f"{PLUGIN_ROOT}/assets/review-dashboard.html")
html = html.replace("</head>", f"<script>window.REVIEW_DATA = {json.dumps(review_data)};</script></head>")
Write(f"{BASE_DIR}/dashboard.html", html)
```

**Display summary:**

```python
print(f"""
## Review Complete

**{PROFILE_NAME}** | **{FILE_COUNT} files** | **14 checks** | **{len(verdicts)} findings**

### Results
- Confirmed: {len(confirmed)}
- False positives: {len(false_positives)}
- Needs context: {len(needs_context)}

**Dashboard:** {BASE_DIR}/dashboard.html
""")

TaskUpdate(taskId=phase6_id, status="completed")
```

**Proceed to STEP 10 (OFFER ACTIONS)** to let user open dashboard, fix all, or exit.

---

# PR FLOW (614 checks, prefix-based grouping)

---

## STEP 5: PHASE 1 - EXTRACTION (Single Script Call)

**Purpose:** Extract semantic units from changed files using tree-sitter extraction.

**Mark phase in_progress:**

```python
tasks = TaskList()
phase1_id = next(t.id for t in tasks if "Phase 1" in t.subject)
TaskUpdate(taskId=phase1_id, status="in_progress")
```

**Execute extraction script:**

```bash
# Define script path and output location
SCRIPT_PATH="{PLUGIN_ROOT}/agents/extract-with-diff.sh"
OUTPUT_FILE="{BASE_DIR}/units.jsonl"

# Execute extraction script from repository root
cd "{REPO_ROOT}" && "{SCRIPT_PATH}" {DIFF_ARGS} > "{OUTPUT_FILE}" 2>&1
EXIT_CODE=$?

# Handle errors
if [ $EXIT_CODE -ne 0 ]; then
  echo "Extraction failed. Exit code: $EXIT_CODE"
  echo "Ensure tree-sitter-cli is installed globally."
  exit 1
fi

# Count extracted units for progress display
UNIT_COUNT=$(wc -l < "{OUTPUT_FILE}" | tr -d ' ')
echo "Extracted $UNIT_COUNT units."
```

**Mark phase complete:**

```python
TaskUpdate(taskId=phase1_id, status="completed")
```

---

## STEP 6: PHASE 2a - CHECK ORCHESTRATION (Single Haiku)

**Purpose:** Parse all checklists, extract checks, and group by ID prefix (e.g., `GC-`, `EH-`, `OP-`).

**Available checker skills** (orchestrator picks per group):
- `cc-defensive-programming` - input validation, assertions, error handling
- `cc-performance-tuning` - optimization, profiling, bottlenecks
- `cc-code-layout-and-style` - formatting, readability, visual structure
- `cc-control-flow-quality` - conditionals, loops, nesting, complexity
- `cc-quality-practices` - testing, debugging, code review
- `cc-documentation-quality` - comments, docs, naming
- `aposd-reviewing-module-design` - abstraction, interfaces, dependencies
- `aposd-simplifying-complexity` - complexity symptoms, deep modules
- `aposd-verifying-correctness` - correctness, edge cases, invariants
- `aposd-optimizing-critical-paths` - performance design, critical paths

**Dispatch orchestrator:**
```python
Task(
    subagent_type="general-purpose",
    model="haiku",
    description="Orchestrate checks",
    prompt=f"""
## Check Orchestrator

Parse all checklists, extract checks, and group by ID prefix.

### Checklists to Parse

{chr(10).join(f"- {c.resolved_path}" for c in CHECKLISTS)}

### Instructions

For each checklist:
1. Read the file
2. Extract every check item (lines starting with `- [ ]` followed by an ID like `GC-1`, `EH-2`, `OP-3`)
3. Group checks by their prefix (the letters before the hyphen)

### Output

Write to `{BASE_DIR}/checks.json`:

```json
{{
  "total_checks": 614,
  "groups": {{
    "GC": {{
      "name": "General Critical",
      "prompt": "Hunt for unvalidated inputs and missing assertions. Red flags: external data trusted without validation, no precondition checks at routine entry, assertions used for normal error handling instead of impossible conditions.",
      "skills": ["cc-defensive-programming"],
      "checks": [
        {{
          "id": "GC-1",
          "check": "Does the routine protect itself from bad input data?",
          "section": "General",
          "source_checklist": "skills/cc-defensive-programming/checklists.md"
        }}
      ]
    }},
    "EH": {{
      "name": "Exceptions High",
      "prompt": "Focus on exception hygiene. Red flags: exceptions for control flow, empty catch blocks, implementation details leaking through exception types, exceptions in constructors/destructors.",
      "skills": ["cc-defensive-programming", "aposd-simplifying-complexity"],
      "checks": [...]
    }},
    "OP": {{
      "name": "Overall Program Performance",
      "prompt": "Look for optimization anti-patterns. Red flags: micro-optimizing before measuring, I/O in tight loops, ignoring algorithmic improvements in favor of code tuning.",
      "skills": ["cc-performance-tuning", "aposd-optimizing-critical-paths"],
      "checks": [...]
    }}
  }}
}}
```

**For each group:**

1. **`prompt`**: Write a focused hunting prompt:
   - Summarizes what this group is hunting for (1 sentence)
   - Lists 2-3 specific red flags to watch for
   - Is actionable and specific to the checks in that group

2. **`skills`**: Pick 1-3 most relevant skills from this list:
   - `cc-defensive-programming` - input validation, assertions, error handling
   - `cc-performance-tuning` - optimization, profiling, bottlenecks
   - `cc-code-layout-and-style` - formatting, readability, visual structure
   - `cc-control-flow-quality` - conditionals, loops, nesting, complexity
   - `cc-quality-practices` - testing, debugging, code review
   - `cc-documentation-quality` - comments, docs, naming
   - `aposd-reviewing-module-design` - abstraction, interfaces, dependencies
   - `aposd-simplifying-complexity` - complexity symptoms, deep modules
   - `aposd-verifying-correctness` - correctness, edge cases, invariants
   - `aposd-optimizing-critical-paths` - performance design, critical paths

   Pick based on what the checks are actually examining. Don't load unrelated skills.

The `name` field should be inferred from the section header where these checks appear.

Return the total check count and number of groups.
"""
)
```

**Wait for orchestrator. Then read checks:**
```python
checks_data = read_json(f"{BASE_DIR}/checks.json")
TOTAL_CHECKS = checks_data["total_checks"]
CHECK_GROUPS = checks_data["groups"]  # Dict of prefix -> {name, checks}
```

---

## STEP 6b: PHASE 2b - CHECKING (Parallel, 1 Agent per Prefix Group)

**Purpose:** Run checks against the code. Each agent handles one prefix group and loads ALL checker skills.

**Create tasks:**
```python
for prefix, group in CHECK_GROUPS.items():
    TaskCreate(
        subject=f"Check: {prefix}",
        description=f"Run {len(group['checks'])} {group['name']} checks",
        activeForm=f"Checking {prefix}"
    )
```

**Execute (respect MAX_PARALLELISM):**

```python
indexed_groups = list(CHECK_GROUPS.items())

# Split into waves based on MAX_PARALLELISM
if MAX_PARALLELISM == 0:
    waves = [indexed_groups]
else:
    waves = [indexed_groups[i:i+MAX_PARALLELISM]
             for i in range(0, len(indexed_groups), MAX_PARALLELISM)]

for wave in waves:
    # Dispatch all agents in this wave in a SINGLE MESSAGE
    for prefix, group in wave:
        checks = group["checks"]
        group_name = group["name"]
        group_prompt = group["prompt"]
        group_skills = group["skills"]

        Task(
            subagent_type="code-foundations:checker-agent",
            model=MODELS["checking"],  # From profile config
            description=f"Check: {prefix}",
            prompt=f"""
BATCH: {prefix}
PLUGIN_ROOT: {PLUGIN_ROOT}
BASE_DIR: {BASE_DIR}

FOCUS: {group_prompt}

SKILLS:
{chr(10).join(f'- {skill}' for skill in group_skills)}

CHECKS ({prefix} - {group_name}):
{chr(10).join(f'- {c["id"]}: {c["check"]}' for c in checks)}

UNITS: Read from {BASE_DIR}/units.jsonl
DIFF_CMD: {DIFF_CMD}
REPO_ROOT: {REPO_ROOT}
"""
        )
    # WAIT for this wave to complete before starting next wave
```

**Wait for all checker agents.**

---

## STEP 7: ORCHESTRATE FINDINGS (Single Haiku)

**Purpose:** Batch findings, pick implementation skills, and create investigation tasks with tailored prompts.

**Available implementation skills** (orchestrator picks per batch):
- `cc-defensive-programming` - input validation, error handling, assertions
- `cc-refactoring-guidance` - safe code changes, small steps
- `cc-routine-and-class-design` - function/class structure, cohesion
- `cc-control-flow-quality` - conditionals, loops, complexity
- `aposd-designing-deep-modules` - interface design, abstraction
- `aposd-simplifying-complexity` - reducing cognitive load
- `aposd-improving-code-clarity` - naming, comments, readability

```python
Task(
    subagent_type="general-purpose",
    model="haiku",
    description="Orchestrate findings",
    prompt=f"""
## Orchestrator Agent

Collect findings, deduplicate, batch, and prepare investigation tasks with skills and prompts.

### Step 1: Collect Findings

Read all findings from JSONL:
```bash
cat {BASE_DIR}/findings.jsonl
```
Each line is a JSON object with: batch, unit, file, check_id, verdict, line, issue, confidence.

### Step 2: Deduplicate

Group findings by file:line. If multiple checks flagged the same location, keep the most specific finding.

### Step 3: Batch and Create Tasks

Create one task per batch of 5 findings. For each batch:
1. Analyze what the findings are about
2. Write a focused prompt for the investigator
3. Pick 1-3 implementation skills relevant to FIXING these issues

```python
BATCH_SIZE = 5
batches = chunk(findings, BATCH_SIZE)

for batch_num, batch in enumerate(batches):
    # Analyze batch to pick skills and write prompt
    # e.g., if findings are about validation → cc-defensive-programming
    # e.g., if findings are about complexity → aposd-simplifying-complexity

    TaskCreate(
        subject=f"Investigate: batch-{{batch_num + 1}}",
        description=f"Verify {{len(batch)}} findings",
        activeForm=f"Investigating batch {{batch_num + 1}}",
        metadata={{
            "batch": batch_num + 1,
            "prompt": "Focus on validation gaps. For each confirmed issue, provide a complete fix with proper input sanitization.",
            "skills": ["cc-defensive-programming", "cc-refactoring-guidance"],
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

**Skill selection guide:**
- Validation/security issues → `cc-defensive-programming`
- Complexity/nesting issues → `aposd-simplifying-complexity`, `cc-control-flow-quality`
- Interface/abstraction issues → `aposd-designing-deep-modules`
- Naming/clarity issues → `aposd-improving-code-clarity`
- Structure issues → `cc-routine-and-class-design`
- Always include `cc-refactoring-guidance` for safe changes

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

## STEP 8: INVESTIGATION (Parallel Sonnet)

**Purpose:** Verify findings and provide comprehensive fixes. Each agent loads implementation skills and produces ready-to-apply code.

**Execute (respect MAX_PARALLELISM):**

```python
# Split into waves based on MAX_PARALLELISM
if MAX_PARALLELISM == 0:
    waves = [investigate_tasks]
else:
    waves = [investigate_tasks[i:i+MAX_PARALLELISM]
             for i in range(0, len(investigate_tasks), MAX_PARALLELISM)]

for wave in waves:
    # Dispatch all agents in this wave in a SINGLE MESSAGE
    for task in wave:
        batch_num = task.metadata["batch"]
        findings = task.metadata["findings"]
        batch_prompt = task.metadata["prompt"]
        batch_skills = task.metadata["skills"]
        files = list(set(f["file"] for f in findings))

        Task(
            subagent_type="code-foundations:investigation-agent",
            model=MODELS["investigation"],  # From profile config
            description=f"Investigate batch {batch_num}",
            prompt=f"""
## Investigation Agent

Verify findings and provide comprehensive, ready-to-apply fixes.

### YOUR FOCUS

{batch_prompt}

### PHASE 1: LOAD IMPLEMENTATION SKILLS

{chr(10).join(f'''```
Skill(code-foundations:{skill})
```''' for skill in batch_skills)}

### PHASE 2: VERIFY FINDINGS

{chr(10).join(f'''
**{f["id"]}** - {f["file"]}:{f["line"]}
- Check: "{f["check"]}"
- Issue: {f["issue"]}
- Evidence: {f["evidence"]}
''' for f in findings)}

For EACH finding:

1. Read the file around the finding line (20 lines before, 20 lines after)
2. Get the diff hunk:
   ```bash
   cd {REPO_ROOT}
   git diff {DIFF_ARGS} -U5 -- <file>
   ```
3. Determine verdict:
   - **CONFIRMED**: Real issue that needs fixing
   - **FALSE_POSITIVE**: Not an issue (explain why)
   - **NEEDS_CONTEXT**: Cannot determine without more information

### PHASE 3: WRITE COMPREHENSIVE FIXES

For each CONFIRMED finding, provide a **complete fix**:
- Show the exact code to replace (old_string)
- Show the fixed code (new_string)
- Explain WHY this fix works
- Follow patterns from the loaded skills

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
      "code_context": {{
        "start_line": 35,
        "end_line": 45,
        "lines": ["..."]
      }},
      "diff_hunk": "@@ -40,6 +42,8 @@...",
      "fix": {{
        "explanation": "Added input validation and switched to parameterized query to prevent SQL injection",
        "edits": [
          {{
            "file": "src/auth.ts",
            "old_string": "  const id = req.body.id;\\n  db.query(`SELECT * FROM users WHERE id = ${{id}}`);",
            "new_string": "  const id = req.body.id;\\n  if (!id || typeof id !== 'string') {{\\n    throw new ValidationError('Invalid user ID');\\n  }}\\n  db.query('SELECT * FROM users WHERE id = ?', [id]);"
          }}
        ]
      }}
    }},
    {{
      "id": "API-2",
      "verdict": "CONFIRMED",
      "reason": "Function renamed but callers not updated",
      "code_context": {{...}},
      "diff_hunk": "...",
      "fix": {{
        "explanation": "Renamed function and updated all call sites",
        "edits": [
          {{
            "file": "src/utils.ts",
            "old_string": "export function oldName(",
            "new_string": "export function newName("
          }},
          {{
            "file": "src/api.ts",
            "old_string": "import {{ oldName }} from './utils'",
            "new_string": "import {{ newName }} from './utils'"
          }},
          {{
            "file": "src/api.ts",
            "old_string": "oldName(data)",
            "new_string": "newName(data)"
          }}
        ]
      }}
    }},
    {{
      "id": "DP-3",
      "verdict": "FALSE_POSITIVE",
      "reason": "Validation occurs in middleware before this function is called",
      "code_context": {{
        "start_line": 82,
        "end_line": 92,
        "lines": ["..."]
      }},
      "diff_hunk": null,
      "fix": null
    }},
    {{
      "id": "CF-7",
      "verdict": "NEEDS_CONTEXT",
      "reason": "Cannot determine loop termination without knowing external API behavior",
      "code_context": {{...}},
      "diff_hunk": "...",
      "fix": null,
      "question": "Does fetchNext() guarantee eventual termination?"
    }}
  ]
}}
```

**Fix requirements:**
- `fix.edits` is an array - one finding can require multiple file edits
- `old_string` must match exactly what's in the file
- `new_string` should be a complete, working replacement
- Order edits logically (definition before usages)
- Include enough context to make each edit unambiguous
- Follow the coding style of the existing file
"""
        )
    # WAIT for this wave to complete before starting next wave
```

**Wait for all investigation agents.**

**Mark investigation tasks complete:**
```python
for task in investigate_tasks:
    TaskUpdate(taskId=task.id, status="completed")
```

---

## STEP 9: TERMINAL SUMMARY

**Collect findings from investigation results:**

```python
findings = []
for batch_file in glob(f"{BASE_DIR}/investigation/batch-*.json"):
    batch = read_json(batch_file)
    for result in batch["results"]:
        findings.append(result)

confirmed = [f for f in findings if f["verdict"] == "CONFIRMED"]
false_positives = [f for f in findings if f["verdict"] == "FALSE_POSITIVE"]
needs_context = [f for f in findings if f["verdict"] == "NEEDS_CONTEXT"]
```

**Generate dashboard (inline, no agent):**

```python
# Build review data
review_data = {
    "profile": PROFILE_NAME,
    "timestamp": datetime.now().isoformat(),
    "stats": {
        "files_reviewed": FILE_COUNT,
        "checklists_run": TOTAL_CHECKLISTS,
        "confirmed": len(confirmed),
        "false_positives": len(false_positives),
        "needs_context": len(needs_context)
    },
    "findings": findings
}

# Read dashboard template, inject data, write to BASE_DIR
html = Read(f"{PLUGIN_ROOT}/assets/review-dashboard.html")
html = html.replace("</head>", f"<script>window.REVIEW_DATA = {json.dumps(review_data)};</script></head>")
Write(f"{BASE_DIR}/dashboard.html", html)
```

**Display summary:**

```markdown
## Review Complete

**{PROFILE_NAME}** | **{FILE_COUNT} files** | **{TOTAL_CHECKLISTS} checklists** | **{len(findings)} findings**

### Phases
- Extraction: {N} batches
- Checking: {N} checklists
- Orchestrate: {N} findings → {N} batches
- Investigation: {len(confirmed)} confirmed, {len(false_positives)} false positives, {len(needs_context)} need context

### Top Issues
1. **[ID]** file:line - issue
2. **[ID]** file:line - issue
3. **[ID]** file:line - issue

**Dashboard:** {BASE_DIR}/dashboard.html
```

---

## STEP 10: OFFER ACTIONS

```
AskUserQuestion(
  questions: [
    {
      header: "Action",
      question: "What would you like to do?",
      options: [
        {label: "Open Dashboard", description: "View full review in browser"},
        {label: "Fix All", description: "Apply all fixes from confirmed findings"},
        {label: "Done", description: "Exit review"}
      ]
    }
  ]
)
```

**If "Open Dashboard":**

Dashboard was already generated in STEP 9. Just open it:

```bash
open {BASE_DIR}/dashboard.html
```

**If "Fix All":**

Apply fixes directly from investigation results:

```python
confirmed_with_fixes = [f for f in confirmed if f.get("fix")]

if not confirmed_with_fixes:
    print("No confirmed findings with fixes to apply.")
else:
    print(f"Applying {len(confirmed_with_fixes)} fixes...")

    for finding in confirmed_with_fixes:
        fix = finding["fix"]
        print(f"\n**{finding.get('check_id', finding.get('id', 'unknown'))}**: {fix['explanation']}")

        # Apply each edit in the fix
        for edit in fix["edits"]:
            print(f"  → {edit['file']}")
            Edit(
                file_path=edit["file"],
                old_string=edit["old_string"],
                new_string=edit["new_string"]
            )

    print(f"\n✓ Applied {len(confirmed_with_fixes)} fixes")
    print("Run tests to verify changes.")
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
| Extraction | 1 (script) | bash | Single script call |
| Orchestrate (sanity) | 1 (script) | bash | Single script call |
| Check Orchestrate (PR) | 1 | haiku | Fixed |
| Checking | 1 per batch/prefix | `profile.models.checking` | `len(batches)` |
| Orchestrate Findings | 1 | haiku | Fixed |
| Investigation | 1 per 5 findings | `profile.models.investigation` | `ceil(findings / 5)` |

**All dispatched by main agent** - single message with multiple Task calls = true parallelism.

**Checker agents load group-specific skills** - orchestrator picks 1-3 relevant skills per prefix group.

**Prefix groups** - checks are grouped by ID prefix (e.g., `GC-`, `EH-`, `OP-`, `CT-`). Each prefix = 1 agent.

### max_parallelism

Control concurrent agents per phase via profile config:

```yaml
max_parallelism: 5  # Max concurrent agents (default: 5)
```

| Setting | Behavior |
|---------|----------|
| `0` | Unlimited - dispatch all agents at once |
| `1` | Sequential - one agent at a time |
| `N` | Dispatch in waves of N agents, wait between waves |

**Example:** PR profile with ~30 prefix groups, `max_parallelism: 5`:
- Wave 1: GC, GH, GS, EH, EC (wait)
- Wave 2: SC, OP, CT, SS, MD (wait)
- ...

## SCALING ANALYSIS (100k Line PR)

| Phase | Agents | Context per Agent | Notes |
|-------|--------|-------------------|-------|
| Extraction | ~200 | Small (5 files) | Parallel, fast |
| Check Orchestrate | 1 | Small (parse checklists) | Just text parsing |
| Checking | ~30 | Medium (prefix group + all skills + code) | Semantic grouping |
| Orchestrate | 1 | Medium (all findings) | Just batching |
| Investigation | ~40 | Small (5 findings + files) | Bounded context |
