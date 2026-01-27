---
description: "Medium-depth review with 3 parallel agents: defensive (security+errors), quality (maintainability+clarity), and correctness (bugs+tests)."
argument-hint: "[--lens] [--staged | files...]"
allowed-tools: ["Bash", "Glob", "Grep", "Read", "Task", "Skill", "TodoWrite", "AskUserQuestion"]
---

# Review Changes (Level 2 - Medium Review)

## ⛔ MANDATORY EXECUTION PROTOCOL

This is a checklist-driven process. You MUST use TodoWrite to track progress.

**THE RULES:**

1. **Create the execution checklist FIRST** - Use TodoWrite before any other action
2. **Mark items in_progress BEFORE starting** - Never skip ahead
3. **Dispatch 3 agents** - Use Task tool, ALL 3 IN ONE MESSAGE
4. **Phase 5 is THE LAW** - Execute fixes, don't just report them
5. **DO NOT RETURN** until execution checklist is 100% complete

**FAILURE MODES TO AVOID:**

- Saying "let me dispatch agents" but not calling Task tool
- Calling Task tool with only 1-2 agents instead of 3
- Skipping Phase 5 execution
- Not using TodoWrite to track progress

---

## STEP 0: CREATE EXECUTION CHECKLIST

**DO THIS IMMEDIATELY. NO EXCEPTIONS.**

```
TodoWrite([
  {content: "Get diff and check size", status: "pending", activeForm: "Getting diff"},
  {content: "Run triage to create JSON for review agents", status: "pending", activeForm: "Running triage"},
  {content: "GATE: Dispatch ALL 3 review agents in parallel", status: "pending", activeForm: "Dispatching 3 review agents"},
  {content: "GATE: Wait for all 3 agents to complete", status: "pending", activeForm: "Waiting for agent results"},
  {content: "Aggregate results grouped by action type", status: "pending", activeForm: "Aggregating review results"},
  {content: "GATE: Get user decision on execution", status: "pending", activeForm: "Getting user decision"}
])
```

---

## ARGUMENT PARSING

Parse `--lens` flag from arguments:

```
LENS_MODE=false
DIFF_ARGS=""

for arg in $ARGUMENTS; do
  if [[ "$arg" == "--lens" ]]; then
    LENS_MODE=true
  else
    DIFF_ARGS="$DIFF_ARGS $arg"
  fi
done
```

### LENS MODE REDIRECT

**If `LENS_MODE=true`, use the lens orchestrator instead:**

```
If LENS_MODE=true:
  → Use lens-review command: /lens-review review-changes $DIFF_ARGS
  → This dispatches 7 agents (one per skill) with full checklist execution
  → STOP processing this command - lens-review handles everything
```

The lens orchestrator (`commands/lens-review.md`) provides:
- One agent per skill (7 total for review-changes)
- Every checklist item executed with evidence
- Full audit trail in `/tmp/lens-review-{RUN_ID}/`

**If `LENS_MODE=false`, continue with standard review below.**

---

## STEP 1: GET DIFF METADATA (NOT FULL DIFF)

Mark todo "Get diff" as `in_progress`.

```bash
# Get file list and line count only
if [[ "$ARGUMENTS" == "--staged" ]]; then
  git diff --cached --name-only
  git diff --cached | wc -l
elif [[ -n "$ARGUMENTS" ]]; then
  git diff --name-only $ARGUMENTS
  git diff $ARGUMENTS | wc -l
else
  git diff --name-only
  git diff | wc -l
fi
```

**DO NOT run full `git diff` for content.** Triage subagent will handle it.

**ALWAYS run triage (Step 2)** to create the JSON file that agents will read.

Store only file list and line count. Mark todo complete.

---

## STEP 2: TRIAGE (ALWAYS RUN)

**ALWAYS run triage** to create the JSON files that agents will read.

Mark todo "Run triage" as `in_progress`.

**Determine diff command based on arguments:**
```bash
RUN_ID=$(date +%Y%m%d-%H%M%S)

if [[ "$ARGUMENTS" == "--staged" ]]; then
  DIFF_CMD="git diff --cached"
elif [[ -n "$ARGUMENTS" ]]; then
  DIFF_CMD="git diff $ARGUMENTS"
else
  DIFF_CMD="git diff"
fi

./scripts/triage-diff.sh "$RUN_ID" "$DIFF_CMD"
```

Store `RUN_ID` for use in all subsequent steps.

**IMPORTANT:** When dispatching agents, replace `[RUN_ID]` in prompts with the actual value (e.g., `20260121-121731`).

The script outputs to `/tmp/review-$RUN_ID/` with:
- `defensive.json` - error handling, validation, auth patterns
- `quality.json` - code structure (catch-all)
- `correctness.json` - test files
- `performance.json` - loops, I/O patterns (ignored for review-changes)
- `documentation.json` - .md files, docs/ (ignored for review-changes)
- `metadata.json` - run info

**Note:** review-changes uses only 3 reviewers (defensive, quality, correctness). The script generates all 5, but only 3 are dispatched.

Mark todo complete when script returns.

---

## STEP 3: DISPATCH 3 AGENTS ⛔ THIS IS A GATE

**YOU MUST DISPATCH ALL 3 AGENTS IN A SINGLE MESSAGE.**

Mark todo "GATE: Dispatch ALL 3 review agents" as `in_progress`.

### VERIFICATION CHECKPOINT

Before proceeding, verify:
- [ ] You have the file list and line count (NOT full diff in memory)
- [ ] If large diff, triage JSON is at /tmp/changes-triage.json
- [ ] You are about to call Task tool 3 times in ONE message

### THE 3 AGENT PROMPTS

Use these EXACT prompts. Call ALL 3 in a SINGLE message with the Task tool.

**INPUT:** Each agent reads from their own JSON file (e.g., `/tmp/review-[RUN_ID]/defensive.json`).

**CRITICAL:** Each agent reads ONLY their assigned chunks file. The diff hunks are already embedded - NO full git diff needed. Zero redundant diff reads.

---

### AGENT 1: defensive-reviewer

```
Task(
  subagent_type: "code-foundations:defensive-reviewer",
  description: "Defensive review",
  prompt: """
FIRST: Load your skills using the Skill tool:
1. Skill(code-foundations:cc-defensive-programming)
2. Skill(code-foundations:aposd-simplifying-complexity)

THEN: Read agents/defensive-reviewer.md for your role.

Review for security AND error handling:
- Input validation at trust boundaries
- Injection prevention (SQL, command, path traversal)
- Auth checks BEFORE action
- Empty catch blocks
- Silent failures
- Error context preservation

YOUR INPUT: Read /tmp/review-[RUN_ID]/defensive.json for your assigned chunks.
Each entry contains: file, lines, description, and the actual diff hunk.

⛔ DO NOT run full `git diff` - the hunks are already in the JSON.
✅ You MAY run targeted git commands (git show, git blame, git log) if you need additional context.

If the JSON array is empty [], write "No chunks assigned - PASS" to the output file.

OUTPUT: Write your review to /tmp/review-[RUN_ID]/defensive.md using the Write tool.

FORMAT:
## Defensive Review

### Fix (high confidence)
- [CRITICAL/IMPORTANT] file:line - issue
  ```lang
  code fix
  ```

### Investigate (low confidence)
- [IMPORTANT] file:line - issue
  Check: [what to investigate]
  **Unknown**: [missing context]

### Plan (systemic)
- [CRITICAL] description
  → /code-foundations:whiteboarding "[topic]"

### Verdict: HARDENED / ADEQUATE / FRAGILE / VULNERABLE

Return: "/tmp/review-[RUN_ID]/defensive.md"
"""
)
```

---

### AGENT 2: quality-reviewer

**CONDITIONAL DISPATCH**: If `LENS_MODE=true`, use the lens-based agent.

#### Standard Mode (LENS_MODE=false)

```
Task(
  subagent_type: "code-foundations:quality-reviewer",
  description: "Quality review",
  prompt: """
FIRST: Load your skills using the Skill tool:
1. Skill(code-foundations:aposd-reviewing-module-design)
2. Skill(code-foundations:cc-code-layout-and-style)

THEN: Read agents/quality-reviewer.md for your role.

Review for design AND readability:
- Complexity symptoms (change amplification, cognitive load)
- Cohesion (routine does ONE thing)
- Coupling (minimized dependencies)
- Naming clarity
- Comment quality
- Style consistency
- Trailing newlines

YOUR INPUT: Read /tmp/review-[RUN_ID]/quality.json for your assigned chunks.
Each entry contains: file, lines, description, and the actual diff hunk.

⛔ DO NOT run full `git diff` - the hunks are already in the JSON.
✅ You MAY run targeted git commands (git show, git blame, git log) if you need additional context.

If the JSON array is empty [], write "No chunks assigned - PASS" to the output file.

OUTPUT: Write your review to /tmp/review-[RUN_ID]/quality.md using the Write tool.

FORMAT:
## Quality Review

### Fix (high confidence)
- [CRITICAL/IMPORTANT] file:line - issue
  ```lang
  code fix
  ```

### Investigate (low confidence)
- [IMPORTANT] file:line - issue
  Check: [what to investigate]
  **Unknown**: [missing context]

### Plan (systemic)
- [CRITICAL] description
  → /code-foundations:whiteboarding "[topic]"

### Verdict: EXCELLENT / GOOD / ADEQUATE / POOR

Return: "/tmp/review-[RUN_ID]/quality.md"
"""
)
```

---

### AGENT 3: correctness-reviewer

```
Task(
  subagent_type: "code-foundations:correctness-reviewer",
  description: "Correctness review",
  prompt: """
FIRST: Load your skills using the Skill tool:
1. Skill(code-foundations:aposd-verifying-correctness)
2. Skill(code-foundations:cc-quality-practices)

THEN: Read agents/correctness-reviewer.md for your role.

Review for bugs AND test coverage:
- Boundary conditions (off-by-one, empty, null, max)
- Logic flow (all paths, early returns)
- Duplicate handling
- Race conditions
- Test gaps for new code

YOUR INPUT: Read /tmp/review-[RUN_ID]/correctness.json for your assigned chunks.
Each entry contains: file, lines, description, and the actual diff hunk.

⛔ DO NOT run full `git diff` - the hunks are already in the JSON.
✅ You MAY run targeted git commands (git show, git blame, git log) if you need additional context.

If the JSON array is empty [], write "No chunks assigned - PASS" to the output file.

OUTPUT: Write your review to /tmp/review-[RUN_ID]/correctness.md using the Write tool.

FORMAT:
## Correctness Review

### Fix (high confidence)
- [CRITICAL/IMPORTANT] file:line - issue
  ```lang
  code fix
  ```

### Investigate (low confidence)
- [IMPORTANT] file:line - issue
  Check: [what to investigate]
  **Unknown**: [missing context]

### Plan (systemic)
- [CRITICAL] description
  → /code-foundations:whiteboarding "[topic]"

### Verdict: VERIFIED / LIKELY CORRECT / UNCERTAIN / BUGGY

Return: "/tmp/review-[RUN_ID]/correctness.md"
"""
)
```

---

### POST-DISPATCH VERIFICATION

After calling Task tool 3 times, mark todo "GATE: Dispatch ALL 3 review agents" as complete.

Mark todo "GATE: Wait for all 3 agents" as `in_progress`.

Wait for all 3 agents to return results.

Mark todo "GATE: Wait for all 3 agents" as complete.

---

## STEP 4: AGGREGATE RESULTS

Mark todo "Aggregate results" as `in_progress`.

**Collect file paths returned by agents**, then read all review files:
```bash
cat /tmp/review-[RUN_ID]/defensive.md
cat /tmp/review-[RUN_ID]/quality.md
cat /tmp/review-[RUN_ID]/correctness.md
```

**Synthesize into human-readable report** grouped by action type.
Write the final report to `/tmp/review-[RUN_ID]/REPORT.md` AND output to user.

```markdown
# Review Changes Report

## Scope
[files reviewed]

## Verdict: [READY / NEEDS WORK / BLOCKED]

---

## Fix
High confidence. Apply now.

### [filename]
1. [SEVERITY] Line X - [issue] ([agent])
   ```lang
   [code to apply]
   ```

---

## Investigate
Low confidence. Need context.

1. [SEVERITY] file:line - [issue] ([agent])
   Check: [what to investigate]
   **Unknown**: [what we don't know]

---

## Plan
Systemic. Spin off to /code-foundations:whiteboarding.

1. [SEVERITY] [description]
   → /code-foundations:whiteboarding "[topic]"

---

## Summary Table

| Action | Count |
|--------|-------|
| Fix | [n] |
| Investigate | [n] |
| Plan | [n] |
```

### Verdict Logic

| Condition | Verdict |
|-----------|---------|
| Any CRITICAL | **BLOCKED** |
| IMPORTANT only | **NEEDS WORK** |
| SUGGESTIONS only | **READY** |
| No issues | **READY** |

Mark todo "Aggregate results" as complete.

---

## STEP 5: USER DECISION GATE ⛔ MANDATORY

**STOP. Present full report and let user decide what to execute.**

Mark todo "GATE: Get user decision on execution" as `in_progress`.

### 5.1 Present Full Report to User

**ALWAYS output the complete report** with all sections (Fix, Investigate, Plan) as formatted in Step 4.

Then show the summary:

```markdown
## Review Complete

| Action | Count |
|--------|-------|
| Fix | [n] |
| Investigate | [n] |
| Plan | [n] |

**Verdict:** [READY / NEEDS WORK / BLOCKED]
```

### 5.2 Ask User What to Execute

```
AskUserQuestion(
  questions: [
    {
      question: "Execute Fix items? ([n] high-confidence issues with code fixes)",
      header: "Fix",
      options: [
        {label: "All (Recommended)", description: "Apply all [n] fixes"},
        {label: "CRITICAL only", description: "Apply only critical severity fixes"},
        {label: "None", description: "Skip all fixes"}
      ],
      multiSelect: false
    },
    {
      question: "Execute Investigate items? ([n] low-confidence issues needing context)",
      header: "Investigate",
      options: [
        {label: "All (Recommended)", description: "Investigate all [n] uncertain items"},
        {label: "None", description: "Skip investigations"}
      ],
      multiSelect: false
    },
    {
      question: "Generate Plan prompts? ([n] systemic issues for /code-foundations:whiteboarding)",
      header: "Plan",
      options: [
        {label: "All (Recommended)", description: "Generate all [n] /code-foundations:whiteboarding prompts"},
        {label: "None", description: "Skip plan generation"}
      ],
      multiSelect: false
    }
  ]
)
```

**Note:** Replace `[n]` with actual counts from the report.

### 5.3 Build Execution Checklist

Based on user selections, create todos ONLY for the selected categories:

```
todos = []

if Fix != "None":
  todos.push({content: "Execute FIX items", status: "pending", activeForm: "Executing FIX items"})

if Investigate != "None":
  todos.push({content: "Execute INVESTIGATE items", status: "pending", activeForm: "Executing INVESTIGATE items"})

if Plan != "None":
  todos.push({content: "Handle PLAN items", status: "pending", activeForm: "Handling PLAN items"})

if todos.length > 0:
  todos.push({content: "Final verification", status: "pending", activeForm: "Verifying completion"})
  TodoWrite(todos)
else:
  # User selected "None" for everything - we're done
  STOP HERE
```

**Filter logic for Fix items:**
- "All" → Execute all Fix items
- "CRITICAL only" → Execute only items marked 🔴 CRITICAL
- "None" → Skip

Mark todo "GATE: Get user decision on execution" as complete.

---

## STEP 6: EXECUTE

**Execute based on user's selection from Step 5.**

### 6.1 Execute FIX Items

Mark todo "Execute FIX items" as `in_progress`.

For EACH item in the "Fix" section, dispatch a subagent:

```
Task(
  subagent_type: "code-foundations:implementation-agent",
  description: "Fix: [brief description]",
  prompt: """
FIRST: Load your skills using the Skill tool:
1. Skill(code-foundations:cc-pseudocode-programming)
2. Skill(code-foundations:cc-defensive-programming)
3. Skill(code-foundations:aposd-designing-deep-modules)

THEN: Implement this fix.

TASK: Implement this fix.

FILE: [file path]
LINE: [line number]
ISSUE: [issue description]
FIX:
```lang
[the code/fix from review]
```

CHECKLIST:
- [ ] Read the file to understand context
- [ ] Apply the fix exactly as specified
- [ ] Run tests if available
- [ ] Verify the fix compiles/passes

CHECKPOINT: Do not return until fix is verified working.
"""
)
```

Dispatch FIX agents in parallel where files don't overlap.

**ITERATE until all FIX items are complete.**

Mark todo "Execute FIX items" as complete when ALL fixes are done.

---

### 6.2 Execute INVESTIGATE Items

Mark todo "Execute INVESTIGATE items" as `in_progress`.

For EACH item in the "Investigate" section, dispatch a subagent:

```
Task(
  subagent_type: "general-purpose",
  description: "Investigate: [brief description]",
  prompt: """
Invoke cc-debugging skill for scientific debugging method.

TASK: Investigate this issue and report findings.

FILE: [file path]
LINE: [line number]
ISSUE: [issue description]
CHECK: [what to investigate from review]
UNKNOWN: [the unknown from review]

DEBUGGING METHOD (cc-debugging):
1. STABILIZE - Can you reproduce the concern?
2. LOCATE - Find all relevant code paths
3. HYPOTHESIZE - Form hypothesis about the issue
4. EXPERIMENT - Test the hypothesis
5. CONCLUDE - What did you find?

RETURN:
- Finding: [what you discovered]
- Confidence: [High/Medium/Low]
- Recommendation: [FIX with code | PLAN needed | FALSE ALARM]
"""
)
```

If investigation returns "FIX with code" → Add to FIX queue and execute.
If investigation returns "PLAN needed" → Add to PLAN section.
If investigation returns "FALSE ALARM" → Document and move on.

Mark todo "Execute INVESTIGATE items" as complete when ALL investigations are resolved.

---

### 6.3 Handle PLAN Items

Mark todo "Handle PLAN items" as `in_progress`.

For EACH item in the "Plan" section, output a ready-to-use prompt:

```markdown
## New Session Required

The following items require dedicated planning sessions.
Copy the prompt and start a new Claude session.

### Plan 1: [topic]

**Issue:** [description]
**Files affected:** [list]
**Severity:** [CRITICAL/IMPORTANT]

**Prompt to copy:**
```
/code-foundations:whiteboarding "[topic]"

Context from code review:
- Issue: [description]
- Files: [affected files]
- Severity: [CRITICAL/IMPORTANT]
- Unknown: [what we don't know]
```
```

Mark todo "Handle PLAN items" as complete when all prompts are generated.

---

## STEP 7: FINAL VERIFICATION

Mark todo "Final verification" as `in_progress`.

**Verify ALL items are resolved:**

- [ ] All FIX items implemented and verified
- [ ] All INVESTIGATE items resolved (fixed, planned, or dismissed)
- [ ] All PLAN items have ready-to-copy prompts
- [ ] `git status` shows expected state

```bash
git status
git diff --stat
```

Mark todo "Final verification" as complete.

**ONLY NOW MAY YOU STOP.**

---

## QUICK REFERENCE

### Agent Summary Table (3 agents for review-changes)

| Agent | Combines | Skills |
|-------|----------|--------|
| defensive-reviewer | security + errors | cc-defensive-programming, aposd-simplifying-complexity |
| quality-reviewer | maintainability + clarity | aposd-reviewing-module-design, cc-code-layout-and-style |
| correctness-reviewer | bugs + tests | aposd-verifying-correctness, cc-quality-practices |

### Severity Levels

| Severity | Meaning | Verdict Impact |
|----------|---------|----------------|
| **CRITICAL** | Blocks merge | BLOCKED |
| **IMPORTANT** | Should fix | NEEDS WORK |
| **SUGGESTION** | Consider | READY |

---

## Usage

```bash
/review-changes           # Unstaged changes
/review-changes --staged  # Staged only
/review-changes file.ts   # Specific files
/review-changes --lens    # Lens mode: explicit checklist execution
/review-changes --lens --staged  # Lens mode on staged changes
```

### Lens Mode

When `--lens` is specified, the quality-reviewer uses lens-based execution:
- Executes every checklist item explicitly (175+ items)
- Records PASS/FINDING for each item with evidence
- Creates full audit trail in output

Use lens mode when:
- Standard review isn't catching issues
- You need traceable evidence of what was checked
- Testing the review system itself
