---
description: "Profile-driven code review"
argument-hint: "[--sanity | --pr | --profile <name>] [diff-target]"
allowed-tools: ["Bash", "Glob", "Grep", "Read", "Task", "Write", "AskUserQuestion"]
version: "3.6.10"
---

# Code Review

```bash
echo "code-foundations:review v3.6.10"
```

---

## Step 1: Find Plugin Root

```bash
# Use PLUGIN_DIR if set (local dev via ccf alias), otherwise search cache
if [[ -n "$PLUGIN_DIR" ]]; then
  PLUGIN_ROOT="$PLUGIN_DIR"
else
  PLUGIN_ROOT=$(dirname "$(dirname "$(find ~/.claude/plugins -name 'generate-checklists.ts' -path '*/code-foundations/*' 2>/dev/null | head -1)")")
fi
echo "PLUGIN_ROOT: $PLUGIN_ROOT"
```

---

## Step 2: Parse Arguments

| Argument | Meaning |
|----------|---------|
| `--sanity` | 14 core checks (default) |
| `--pr` | Full PR review (614 checks) |
| `--profile <name>` | Custom profile |
| `main`, `--staged`, etc. | Diff target |

If no diff target specified, ask:

```
AskUserQuestion(
  questions: [{
    header: "Target",
    question: "What do you want to review?",
    options: [
      {label: "Branch diff (Recommended)", description: "Changes since branching from main"},
      {label: "Staged changes", description: "git diff --staged"},
      {label: "Unstaged changes", description: "git diff"},
      {label: "All uncommitted", description: "git diff HEAD"}
    ]
  }]
)
```

Map to diff command:
- Branch diff → `git diff $(git merge-base main HEAD) HEAD`
- Staged → `git diff --staged`
- Unstaged → `git diff`
- All uncommitted → `git diff HEAD`

---

## Step 3: Setup

```bash
REPO_ROOT=$(git rev-parse --show-toplevel)
REPO_NAME=$(basename "$REPO_ROOT")
BRANCH=$(git branch --show-current | sed 's:.*/::')
BASE_DIR="${TMPDIR:-/tmp}/${REPO_NAME}-${BRANCH}-$(date +%H%M)"

mkdir -p "$BASE_DIR/checklists"
echo "BASE_DIR: $BASE_DIR"
```

Show configuration:

```markdown
## Review Configuration

**Profile:** sanity - 14 core checks
**Target:** [diff description] ([N] files)
**Output:** $BASE_DIR
```

---

## Step 4: Extract Units

```bash
cd "$REPO_ROOT"
bun "$PLUGIN_ROOT/agents/extract-units.ts" $DIFF_ARGS > "$BASE_DIR/units.jsonl" 2>&1
UNIT_COUNT=$(wc -l < "$BASE_DIR/units.jsonl" | tr -d ' ')
echo "Extracted $UNIT_COUNT units"
```

If 0 units, stop: "No code units found in diff. Nothing to review."

---

## Step 5: Create Batches & Generate Checklists

Run batching and checklist generation together. **Replace {PLUGIN_ROOT} and {BASE_DIR} with actual paths from previous steps:**

```bash
PLUGIN_ROOT="{PLUGIN_ROOT}"
BASE_DIR="{BASE_DIR}"

# Create batches
tail -n +2 "$BASE_DIR/units.jsonl" | "$PLUGIN_ROOT/agents/orchestrate-batches.sh" > "$BASE_DIR/batches.json" 2>/dev/null
BATCH_COUNT=$(jq 'length' "$BASE_DIR/batches.json")
echo "Created $BATCH_COUNT batches"

# Generate checklists
cat "$BASE_DIR/batches.json" | bun "$PLUGIN_ROOT/agents/generate-checklists.ts" "$BASE_DIR"
echo "Generated $BATCH_COUNT checklists"
```

**Example with real paths:**
```bash
PLUGIN_ROOT="/Users/r/repos/code-foundations"
BASE_DIR="/tmp/PricingAPI-feature-2107"
# ... rest of commands
```

---

## Step 7: Dispatch Checker Agents

Dispatch ALL checker agents in parallel as background tasks:

```python
checklist_files = Glob("$BASE_DIR/checklists/batch-*.md")

# Dispatch all at once in a SINGLE message with multiple Task calls
for checklist_file in checklist_files:
    Task(
        subagent_type="code-foundations:checker-agent",
        description=f"Check {basename(checklist_file)}",
        run_in_background=True,
        prompt=f"""
CHECKLIST_FILE: {checklist_file}
REPO_ROOT: {REPO_ROOT}

Read the checklist, read each unit's source code, and fill in every checkbox.
"""
    )
```

**IMPORTANT:** Send ALL Task calls in a single message to dispatch them simultaneously.

After dispatching, inform the user:
```
Dispatched {N} checker agents in background.
Checklists will be filled in: $BASE_DIR/checklists/

You can continue working. Check results with:
  ls $BASE_DIR/checklists/
  grep '\[!\]' $BASE_DIR/checklists/*.md
```

Then proceed to Step 8 to monitor/summarize when ready.

---

## Step 8: Summarize Results

Wait for background agents to complete, then read all checklists and count verdicts:

```bash
cd "$BASE_DIR/checklists"
FINDINGS=$(grep -c '\[!\]' *.md 2>/dev/null | awk -F: '{sum+=$2} END {print sum+0}')
PASSES=$(grep -c '\[x\]' *.md 2>/dev/null | awk -F: '{sum+=$2} END {print sum+0}')
NA=$(grep -c '\[~\]' *.md 2>/dev/null | awk -F: '{sum+=$2} END {print sum+0}')
UNCHECKED=$(grep -c '\[ \]' *.md 2>/dev/null | awk -F: '{sum+=$2} END {print sum+0}')

echo "Findings: $FINDINGS"
echo "Passes: $PASSES"
echo "N/A: $NA"
echo "Unchecked: $UNCHECKED"
```

Display summary:

```markdown
## Review Complete

**$BATCH_COUNT batches** | **$UNIT_COUNT units** | **14 checks each**

### Results
- 🔴 Findings: $FINDINGS
- ✅ Passes: $PASSES
- ⚪ N/A: $NA

### Checklists
$BASE_DIR/checklists/
```

If findings > 0, extract and display them:

```bash
grep -h '\[!\]' "$BASE_DIR/checklists"/*.md | head -20
```

---

## Step 9: Offer Actions

```
AskUserQuestion(
  questions: [{
    header: "Action",
    question: "What next?",
    options: [
      {label: "Show findings", description: "Display all findings with details"},
      {label: "Open checklists", description: "Open checklist folder"},
      {label: "Done", description: "Exit review"}
    ]
  }]
)
```

**Show findings**: `grep -B2 '\[!\]' "$BASE_DIR/checklists"/*.md`

**Open checklists**: `open "$BASE_DIR/checklists"` (macOS) or show path
