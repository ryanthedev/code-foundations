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

### Sanity Profile (--sanity)

```
┌──────────┐   ┌─────────────┐   ┌───────────┐   ┌───────────────┐   ┌────────┐
│ GET DIFF │ → │ ORCHESTRATE │ → │ CHECKING  │ → │ INVESTIGATION │ → │ REPORT │
│  (main)  │   │  (sonnet)   │   │ (sonnet)  │   │   (sonnet)    │   │(haiku) │
└──────────┘   └─────────────┘   └───────────┘   └───────────────┘   └────────┘
                     ↓                 ↓                  ↓
              • Triage files     1 agent per      1 agent per
              • Smart batching   batch, runs      5 findings,
              • Extract units    14 core checks   provides fixes
```

- **14 core checks** distilled via 7-agent consensus
- **Intelligent batching** by directory, size, dependencies
- **Per-file evaluation** with PASS / FINDING / N/A

### PR Profile (--pr)

```
┌────────────┐   ┌─────────────┐   ┌───────────┐   ┌─────────────┐   ┌───────────────┐   ┌────────┐
│ EXTRACTION │ → │ CHECK ORCH  │ → │ CHECKING  │ → │ ORCHESTRATE │ → │ INVESTIGATION │ → │ REPORT │
│  (haiku)   │   │   (haiku)   │   │ (sonnet)  │   │   (haiku)   │   │   (sonnet)    │   │(haiku) │
└────────────┘   └─────────────┘   └───────────┘   └─────────────┘   └───────────────┘   └────────┘
      ↑                ↑                 ↑                ↑                  ↑               ↑
   Batch by        Group by         1 agent per      Dedupe &          1 agent per      Verdicts
   files (5)       ID prefix        prefix group     batch             5 findings       only
                   (GC-, EH-...)    + skills
```

- **614 checks** across 10 skill checklists
- **Prefix-based grouping** (GC-, EH-, OP-, etc.)
- **Skill loading** per check group

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
dashboard:                 # Optional - custom dashboard generation
  enabled: false           # Set true to generate custom dashboard per repo
  model: sonnet            # Needs creativity for design
checklists:
  - path: <checklist_path>
    skills: [<skill1>, <skill2>]
```

**Validation:**

```python
# Extract parallelism configuration (default: 3)
MAX_PARALLELISM = profile.get("max_parallelism", 3)  # 0 means unlimited

# Extract model configuration (with defaults)
MODELS = {
    "checking": profile.get("models", {}).get("checking", "haiku"),
    "investigation": profile.get("models", {}).get("investigation", "haiku"),
    "report": profile.get("models", {}).get("report", "haiku")
}

# Extract dashboard configuration
DASHBOARD = {
    "enabled": profile.get("dashboard", {}).get("enabled", False),
    "model": profile.get("dashboard", {}).get("model", "sonnet")
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

## STEP 4.5: BRANCH BY PROFILE TYPE

```python
if PROFILE_NAME == "sanity":
    goto SANITY_FLOW
else:
    goto PR_FLOW  # STEP 5
```

---

# SANITY FLOW (14 core checks, intelligent batching)

---

## SANITY STEP 1: ORCHESTRATE (Single Sonnet)

**Purpose:** Triage files, build intelligent batches, extract units. One agent does all pre-work.

```python
Task(
    subagent_type="general-purpose",
    model="sonnet",
    description="Orchestrate review",
    prompt=f"""
## Review Orchestrator

Analyze the diff, triage files, build intelligent batches, and extract units.

### Step 1: Get Files

```bash
cd {REPO_ROOT}
{DIFF_CMD} --name-only
```

Also get line counts:
```bash
{DIFF_CMD} --stat
```

### Step 2: Triage Files

Categorize each file:

**SKIP** (don't review):
- `*.lock`, `*-lock.json` → lockfiles
- `*.generated.*`, `*.pb.*`, `*_generated.*` → generated code
- `*.min.js`, `*.bundle.js` → bundled/minified
- `__snapshots__/*` → test snapshots
- `vendor/*`, `node_modules/*` → dependencies

**REVIEW** (everything else):
- Application code
- Tests
- Documentation (*.md)
- Config files
- Migrations

### Step 3: Extract Units & Get Diffs

For each file to REVIEW:
1. Read the file
2. Get the diff:
   ```bash
   {DIFF_CMD} -- <file>
   ```
3. Identify units (functions/methods/classes) with:
   - name, type, lines
   - has_loops, has_async, has_try_catch
   - The actual diff hunks that touch this unit

### Step 4: Build Intelligent Batches

Group **units** (not just files) for checking. Each batch goes to one checker agent.

**Hybrid batching strategy:**

1. **By directory** - units from same dir share context (imports, types)
2. **By size** - combine small units until ~4k tokens of diff, large units alone
3. **By relationship** - keep `foo.ts` units + `foo.test.ts` units together
4. **By imports** - units that call each other → same batch

**Each batch contains:**
- List of units to check
- The diff hunks for those units
- Shared context description

Target: ~4k tokens of diff per batch

### Output

Write to `{BASE_DIR}/orchestrate.json`:

```json
{{
  "stats": {{
    "total_files": 147,
    "review": 45,
    "skip": 102
  }},
  "skip": [
    {{"file": "package-lock.json", "reason": "lockfile"}},
    {{"file": "src/generated/client.ts", "reason": "generated"}}
  ],
  "batches": [
    {{
      "id": 1,
      "shared_context": "User module - files import from each other",
      "units": [
        {{
          "file": "src/user/api.ts",
          "name": "createUser",
          "type": "function",
          "lines": [10, 45],
          "has_loops": false,
          "has_async": true,
          "diff": "@@ -10,6 +10,15 @@\n function createUser(data) {\n+  const validated = validate(data);\n+  if (!validated) return null;\n   ..."
        }},
        {{
          "file": "src/user/api.ts",
          "name": "getUser",
          "type": "function",
          "lines": [47, 72],
          "has_loops": false,
          "has_async": true,
          "diff": "@@ -50,3 +50,8 @@\n async function getUser(id) {\n+  const user = await db.find(id);\n   ..."
        }},
        {{
          "file": "src/user/service.ts",
          "name": "UserService",
          "type": "class",
          "lines": [5, 120],
          "diff": "@@ -20,4 +20,10 @@\n class UserService {\n+  async save(user) {\n   ..."
        }}
      ],
      "total_diff_tokens": 850
    }},
    {{
      "id": 2,
      "shared_context": null,
      "units": [...],
      "total_diff_tokens": 1200
    }}
  ]
}}
```

Return batch count and file counts.
"""
)
```

**Wait for orchestrator. Read result:**
```python
orch = read_json(f"{BASE_DIR}/orchestrate.json")
BATCHES = orch["batches"]
NUM_BATCHES = len(BATCHES)
```

---

## SANITY STEP 2: CHECKING (1 Agent per Batch)

**Purpose:** Run 14 core checks against each unit in the batch. Diffs are provided inline.

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
            subagent_type="general-purpose",
            model="sonnet",
            description=f"Check batch {batch['id']}",
            prompt=f"""
## Checker Agent: Batch {batch['id']}

Review these units using the 14 core checks. Diffs are provided inline.

### Context

**Shared context:** {batch['shared_context'] or 'None'}

### Units to Check

{chr(10).join(f'''
**{u['name']}** ({u['type']}) - {u['file']}:{u['lines'][0]}-{u['lines'][1]}
- has_loops: {u.get('has_loops', False)}
- has_async: {u.get('has_async', False)}
- has_try_catch: {u.get('has_try_catch', False)}

```diff
{u['diff']}
```
''' for u in batch['units'])}

### Instructions

For EACH unit above, evaluate ALL 14 checks.

If you need more context around a diff, read the file:
```
Read({u['file']})
```

For EACH unit, evaluate:

**Error Handling:**
- ERR-3: Are all error-return codes checked?
- ERR-8: Are partial failures handled (rollback, cleanup)?

**Null Safety & Boundaries:**
- NULL-2: Does code check for null before use?
- NULL-4: Are array indexes within bounds?
- NULL-5: Are array references free of off-by-one errors?
- NULL-6: What happens with empty input?

**Logic & Control Flow:**
- LOGIC-1: Does the loop end under all conditions?
- LOGIC-6: Does recursive code have a path to stop?
- LOGIC-11: Are all cases covered in switch/if-else?
- LOGIC-15: No accidental assignment in conditionals?

**Concurrency:**
- CONC-2: Is each shared access point protected?
- CONC-3: Are there no TOCTOU race conditions?

**Resources & Performance:**
- RES-1: Does every acquire have corresponding release?
- PERF-1: Are database queries not in loops (N+1)?

### Evaluation Format

For each unit, for each check:
- **PASS**: Check satisfied
- **FINDING**: Check failed - include line numbers and issue
- **N/A**: Check doesn't apply (use unit metadata: has_loops=false → LOGIC-1 is N/A)

### Output

Write to `{BASE_DIR}/checking/batch-{batch['id']}.json`:

```json
{{
  "batch": {batch['id']},
  "results": [
    {{
      "unit": "createUser",
      "file": "src/user/api.ts",
      "lines": [10, 45],
      "checks": {{
        "ERR-3": {{"verdict": "FINDING", "locations": [{{"line": 42, "issue": "ignores db.insert error"}}]}},
        "ERR-8": {{"verdict": "PASS"}},
        "NULL-2": {{"verdict": "FINDING", "locations": [{{"line": 23, "issue": "userId not checked"}}]}},
        "NULL-4": {{"verdict": "N/A", "reason": "no array access"}},
        "LOGIC-1": {{"verdict": "N/A", "reason": "has_loops: false"}}
      }}
    }},
    {{
      "unit": "getUser",
      "file": "src/user/api.ts",
      "lines": [47, 72],
      "checks": {{...}}
    }}
  ],
  "summary": {{
    "units_checked": 3,
    "total_checks": 42,
    "pass": 30,
    "findings": 8,
    "na": 4
  }}
}}
```
"""
        )
    # WAIT for wave to complete
```

**Wait for all checker agents.**

---

## SANITY STEP 3: COLLECT FINDINGS

**Main agent collects all findings from checking results:**

```python
findings = []
for batch in BATCHES:
    result = read_json(f"{BASE_DIR}/checking/batch-{batch['id']}.json")
    for unit_result in result["results"]:
        for check_id, check_result in unit_result["checks"].items():
            if check_result["verdict"] == "FINDING":
                for loc in check_result["locations"]:
                    findings.append({
                        "id": check_id,
                        "unit": unit_result["unit"],
                        "file": unit_result["file"],
                        "line": loc["line"],
                        "issue": loc["issue"]
                    })

if not findings:
    print("No findings. Skipping investigation.")
    goto SANITY_STEP_5
```

---

## SANITY STEP 4: INVESTIGATION (1 Agent per 5 Findings)

Same as PR flow - verify findings and provide comprehensive fixes.

```python
# Batch findings into groups of 5
BATCH_SIZE = 5
finding_batches = [findings[i:i+BATCH_SIZE] for i in range(0, len(findings), BATCH_SIZE)]

# Dispatch investigation agents (respecting MAX_PARALLELISM)
# ... same pattern as PR flow STEP 8 ...
```

Each investigation agent:
1. Loads implementation skills picked by orchestrator
2. Verifies each finding (CONFIRMED / FALSE_POSITIVE / NEEDS_CONTEXT)
3. Provides comprehensive fix with `old_string` / `new_string` / `explanation`

---

## SANITY STEP 5: REPORT

Same as PR flow - compile results into final JSON.

**Then goto STEP 10 (Terminal Summary)**

---

# PR FLOW (614 checks, prefix-based grouping)

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

**Execute (respect MAX_PARALLELISM):**

```python
files = read_lines(f"{BASE_DIR}/files.txt")
batches = split_evenly(files, NUM_BATCHES)
indexed_batches = list(enumerate(batches))  # [(0, files), (1, files), ...]

# Split into waves based on MAX_PARALLELISM
if MAX_PARALLELISM == 0:
    # Unlimited: all in one wave
    waves = [indexed_batches]
else:
    # Limited: chunk into waves
    waves = [indexed_batches[i:i+MAX_PARALLELISM]
             for i in range(0, len(indexed_batches), MAX_PARALLELISM)]

for wave in waves:
    # Dispatch all agents in this wave in a SINGLE MESSAGE (true parallelism)
    for batch_num, file_batch in wave:
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
    # WAIT for this wave to complete before starting next wave
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
            subagent_type="general-purpose",
            model=MODELS["checking"],  # From profile config
            description=f"Check: {prefix}",
            prompt=f"""
## Checker Agent: {prefix} ({group_name})

You are a checker agent. Execute all {len(checks)} checks in the {prefix} group.

### YOUR FOCUS

{group_prompt}

### PHASE 1: LOAD SKILLS

Load skills for this group's expertise:

{chr(10).join(f'''```
Skill(code-foundations:{skill})
```''' for skill in group_skills)}

### PHASE 2: LOAD CODE CONTEXT

1. Read extracted units:
   ```
   Read({BASE_DIR}/units.json)
   ```

2. Get the diff:
   ```bash
   cd {REPO_ROOT}
   {DIFF_CMD}
   ```

3. Read changed files for full context.

### PHASE 3: EXECUTE CHECKS

Your assigned checks ({prefix} group - {group_name}):

{chr(10).join(f'''**{c["id"]}**: {c["check"]}''' for c in checks)}

For EACH check:
1. Apply the check to the changed code
2. Record result:
   - **PASS**: Check satisfied. One-line evidence.
   - **FINDING**: Check failed. Include file:line, evidence, confidence, recommendation.

### PHASE 4: OUTPUT

Write to `{BASE_DIR}/checking/{prefix}.json`:

```json
{{
  "prefix": "{prefix}",
  "group_name": "{group_name}",
  "checks_run": {len(checks)},
  "findings": [
    {{
      "id": "{prefix}-1",
      "check": "...",
      "file": "src/auth.ts",
      "line": 42,
      "issue": "...",
      "confidence": "HIGH",
      "evidence": "...",
      "recommendation": "..."
    }}
  ],
  "passes": [
    {{
      "id": "{prefix}-2",
      "check": "...",
      "evidence": "..."
    }}
  ]
}}
```

Return: `{BASE_DIR}/checking/{prefix}.json`
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

Read all checking results:
```bash
ls {BASE_DIR}/checking/*.json
```
Read each file.

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
            subagent_type="general-purpose",
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
      "reason": "User input from request.body passed directly to SQL query",
      "code_context": {{
        "start_line": 35,
        "lines": [...]
      }},
      "diff_hunk": "@@ -40,6 +42,8 @@...",
      "fix": {{
        "explanation": "Added input validation and switched to parameterized query",
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

## STEP 9.5: DASHBOARD DESIGNER (Optional)

**Purpose:** Generate a customized HTML dashboard tailored to the specific repo.

**CRITICAL: Check `dashboard.enabled` in the profile FIRST.**
- If `dashboard.enabled: false` → SKIP this entire step, go directly to STEP 10
- If `dashboard.enabled: true` → Run the Task below

```python
# CHECK THIS FIRST - most profiles have dashboard disabled
if not DASHBOARD["enabled"]:
    print("Dashboard generation disabled (dashboard.enabled: false). Skipping to STEP 10.")
    # DO NOT dispatch any Task - go directly to STEP 10
    goto STEP 10

# Only reach here if dashboard.enabled: true
Task(
    subagent_type="general-purpose",
    model=DASHBOARD["model"],  # From profile config (default: sonnet)
    description="Design custom dashboard",
    prompt=f"""
## Dashboard Designer Agent

Create a customized HTML review dashboard for this specific project.

### Load Skill

```
Skill(frontend-design:frontend-design)
```

### Gather Context

1. Read the report:
   ```
   Read({BASE_DIR}/report.json)
   ```

2. Read project metadata (if exists):
   ```
   Read({REPO_ROOT}/package.json)      # or Cargo.toml, pyproject.toml, etc.
   Read({REPO_ROOT}/README.md)
   ```

3. Get repo info:
   ```bash
   cd {REPO_ROOT}
   basename $(git rev-parse --show-toplevel)  # Repo name
   git remote get-url origin 2>/dev/null      # Remote URL (if any)
   ```

### Design Guidelines

Create a **unique, project-specific** dashboard that:

1. **Reflects the project identity**
   - Use project name prominently
   - Infer color scheme from project type (e.g., blue for TypeScript, green for Node, rust for Rust)
   - Match the project's aesthetic if it has branding

2. **Shows review results clearly**
   - Stats summary (files, checklists, findings)
   - Findings grouped by verdict (confirmed, false positive, needs context)
   - Code context and diff for each finding
   - Expandable details

3. **Is self-contained**
   - Single HTML file with embedded CSS/JS
   - Works offline
   - Loads report.json from same directory

4. **Has personality**
   - Don't use generic templates
   - Add subtle design touches that make it memorable
   - Consider the project type (CLI tool? Web app? Library?)

### Output

Write to `{BASE_DIR}/dashboard.html`

The dashboard should load `{BASE_DIR}/report.json` for data.

Return: `{BASE_DIR}/dashboard.html`
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
- Dashboard: {custom | default}

### Top Issues
1. **[ID]** file:line - issue
2. **[ID]** file:line - issue
3. **[ID]** file:line - issue

Output: {BASE_DIR}/report.json
Dashboard: {BASE_DIR}/dashboard.html
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
        {label: "Fix All", description: "Apply all fixes from confirmed findings"},
        {label: "Done", description: "Exit review"}
      ]
    }
  ]
)
```

**If "Open Dashboard":**

**IMPORTANT: Do NOT dispatch a Task agent for this. Execute these steps directly.**

The dashboard needs data injected inline because `fetch()` doesn't work with `file://` protocol due to CORS.

1. Read `{BASE_DIR}/report.json` using the Read tool
2. Read the default dashboard HTML from `{PLUGIN_ROOT}/assets/review-dashboard.html`
3. Inject the report data as a script tag before `</head>`:
   ```html
   <script>window.REVIEW_DATA = { "report": <report.json contents> };</script>
   ```
4. Write the modified HTML to `{BASE_DIR}/dashboard.html` using the Write tool
5. Open the dashboard:
   ```bash
   open {BASE_DIR}/dashboard.html
   ```

This is simple string manipulation - just read the HTML, insert the JSON, write it back.

**If "Fix All":**

Apply fixes directly from the report:

```python
report = read_json(f"{BASE_DIR}/report.json")
confirmed = [f for f in report["findings"] if f["verdict"] == "confirmed" and f.get("fix")]

if not confirmed:
    print("No confirmed findings with fixes to apply.")
else:
    total_edits = sum(len(f["fix"]["edits"]) for f in confirmed)
    print(f"Applying {len(confirmed)} fixes ({total_edits} edits)...")

    for finding in confirmed:
        fix = finding["fix"]
        print(f"\n**{finding['id']}**: {fix['explanation']}")

        for edit in fix["edits"]:
            print(f"  → {edit['file']}")
            Edit(
                file_path=edit["file"],
                old_string=edit["old_string"],
                new_string=edit["new_string"]
            )

    print(f"\n✓ Applied {len(confirmed)} fixes ({total_edits} edits)")
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
| Extraction | 1 per 5 files | haiku | `ceil(files / 5)` |
| Check Orchestrate | 1 | haiku | Fixed |
| Checking | 1 per prefix group | `profile.models.checking` | `len(unique_prefixes)` |
| Orchestrate | 1 | haiku | Fixed |
| Investigation | 1 per 5 findings | `profile.models.investigation` | `ceil(findings / 5)` |
| Report | 1 | `profile.models.report` | Fixed |

**All dispatched by main agent** - single message with multiple Task calls = true parallelism.

**Checker agents load group-specific skills** - orchestrator picks 1-3 relevant skills per prefix group.

**Prefix groups** - checks are grouped by ID prefix (e.g., `GC-`, `EH-`, `OP-`, `CT-`). Each prefix = 1 agent.

### max_parallelism

Control concurrent agents per phase via profile config:

```yaml
max_parallelism: 5  # Max concurrent agents (default: 3)
```

| Setting | Behavior |
|---------|----------|
| `0` | Unlimited - dispatch all agents at once |
| `1` | Sequential - one agent at a time |
| `N` | Dispatch in waves of N agents, wait between waves |

**Example:** PR profile with ~30 prefix groups, `max_parallelism: 3`:
- Wave 1: GC, GH, GS (wait)
- Wave 2: EH, EC, SC (wait)
- Wave 3: OP, CT, SS (wait)
- ...

## SCALING ANALYSIS (100k Line PR)

| Phase | Agents | Context per Agent | Notes |
|-------|--------|-------------------|-------|
| Extraction | ~200 | Small (5 files) | Parallel, fast |
| Check Orchestrate | 1 | Small (parse checklists) | Just text parsing |
| Checking | ~30 | Medium (prefix group + all skills + code) | Semantic grouping |
| Orchestrate | 1 | Medium (all findings) | Just batching |
| Investigation | ~40 | Small (5 findings + files) | Bounded context |
| Report | 1 | Small (verdicts only) | No raw code |
