---
description: "Comprehensive PR review with 5 parallel agents: defensive (security+errors), quality (maintainability+clarity), correctness (bugs+tests), performance, and documentation."
argument-hint: "[--parallel]"
allowed-tools: ["Bash", "Glob", "Grep", "Read", "Task", "Skill", "TodoWrite", "AskUserQuestion"]
---

# Review PR (Level 3 - Full Review)

## ⛔ MANDATORY EXECUTION PROTOCOL

This is a checklist-driven process. You MUST use TodoWrite to track progress.

**THE RULES:**

1. **Create the execution checklist FIRST** - Use TodoWrite before any other action
2. **Mark items in_progress BEFORE starting** - Never skip ahead
3. **Dispatch 5 agents** - Use Task tool, ALL 5 IN ONE MESSAGE
4. **Phase 5 is THE LAW** - Execute fixes, don't just report them
5. **DO NOT RETURN** until execution checklist is 100% complete

**FAILURE MODES TO AVOID:**

- Saying "let me dispatch agents" but not calling Task tool
- Calling Task tool with only 1-2 agents instead of 5
- Skipping Phase 5 execution
- Not using TodoWrite to track progress

---

## STEP 0: CREATE EXECUTION CHECKLIST

**DO THIS IMMEDIATELY. NO EXCEPTIONS.**

```
TodoWrite([
  {content: "Get PR diff and check size", status: "pending", activeForm: "Getting PR diff"},
  {content: "Run triage if large diff (>500 lines OR >10 files)", status: "pending", activeForm: "Running triage on large diff"},
  {content: "GATE: Dispatch ALL 5 review agents in parallel", status: "pending", activeForm: "Dispatching 5 review agents"},
  {content: "GATE: Wait for all 5 agents to complete", status: "pending", activeForm: "Waiting for agent results"},
  {content: "Aggregate results grouped by action type", status: "pending", activeForm: "Aggregating review results"},
  {content: "Execute FIX items (dispatch subagents)", status: "pending", activeForm: "Executing FIX items"},
  {content: "Execute INVESTIGATE items (dispatch subagents)", status: "pending", activeForm: "Executing INVESTIGATE items"},
  {content: "Handle PLAN items (output prompts)", status: "pending", activeForm: "Handling PLAN items"},
  {content: "Handle DECIDE items (ask user)", status: "pending", activeForm: "Handling DECIDE items"},
  {content: "Final verification - all items resolved", status: "pending", activeForm: "Verifying all items resolved"}
])
```

---

## STEP 1: GET PR METADATA (NOT FULL DIFF)

Mark todo "Get PR diff" as `in_progress`.

```bash
gh pr view --json number,title,baseRefName,headRefName 2>/dev/null || echo "No PR"
git diff --name-only $(git merge-base HEAD main)..HEAD
git diff $(git merge-base HEAD main)..HEAD | wc -l  # Count lines for size check
```

**DO NOT run `git diff` for full content.** Triage subagent will handle it.

**SIZE CHECK:**
- Lines > 500 OR files > 10 → Run triage with haiku (Step 2)
- Otherwise → Run triage with haiku (Step 2) - still needed to create JSON

**ALWAYS run triage.** This ensures consistent JSON-based workflow for all agents.

Store only file list and line count. Mark todo complete.

---

## STEP 2: TRIAGE (ALWAYS RUN)

**ALWAYS run triage** to create the JSON file that agents will read.

Mark todo "Run triage" as `in_progress`.

**Create unique run directory:**
```bash
RUN_ID=$(date +%Y%m%d-%H%M%S)
mkdir -p /tmp/pr-review-$RUN_ID
echo $RUN_ID
```

Store `RUN_ID` for use in all subsequent steps.

**IMPORTANT:** When dispatching agents, replace `[RUN_ID]` in prompts with the actual value (e.g., `20260121-121731`).

Dispatch triage agent:

```
Task(
  subagent_type: "general-purpose",
  description: "Triage PR changes",
  prompt: """
Triage this PR diff for routing to specialized reviewers.

Run this command to get the full diff:
```bash
git diff $(git merge-base HEAD main)..HEAD
```

TASK: Parse the diff and create a triage JSON with embedded diff hunks for each reviewer.

REVIEWER MAPPING:
- Input validation, auth, error handling, catch blocks → defensive
- Naming, complexity, cohesion, style → quality
- Logic, boundaries, tests, race conditions → correctness
- O(n²), loops, resources, hot paths → performance
- Comments, README, docs, CLAUDE.md → documentation

OUTPUT: Write JSON to /tmp/pr-review-[RUN_ID]/triage.json using the Write tool:

{
  "metadata": {
    "base": "main",
    "head": "[branch name]",
    "total_files": [count],
    "total_lines": [count]
  },
  "by_reviewer": {
    "defensive": [
      {
        "file": "path/to/file.ext",
        "lines": [start, end],
        "description": "what this change DOES",
        "diff": "@@ -45,10 +45,27 @@\n actual diff hunk here\n- removed line\n+ added line\n context..."
      }
    ],
    "quality": [...],
    "correctness": [...],
    "performance": [...],
    "documentation": [...]
  }
}

CRITICAL:
- Extract and embed the actual diff hunk for each chunk (not just file paths)
- A chunk may be assigned to multiple reviewers - duplicate the entry in each
- Empty array [] if no chunks for a reviewer
- Use the Write tool to save to /tmp/pr-review-[RUN_ID]/triage.json
- Return "Triage complete - /tmp/pr-review-[RUN_ID]" when done
"""
)
```

Mark todo complete when triage returns.

---

## STEP 3: DISPATCH 5 AGENTS ⛔ THIS IS A GATE

**YOU MUST DISPATCH ALL 5 AGENTS IN A SINGLE MESSAGE.**

Mark todo "GATE: Dispatch ALL 5 review agents" as `in_progress`.

### VERIFICATION CHECKPOINT

Before proceeding, verify:
- [ ] You have the file list and line count (NOT full diff in memory)
- [ ] If large diff, triage JSON is available with file paths
- [ ] You are about to call Task tool 5 times in ONE message

### THE 5 AGENT PROMPTS

Use these EXACT prompts. Call ALL 5 in a SINGLE message with the Task tool.

**INPUT:** Agents ALWAYS read from `/tmp/pr-triage.json` which contains embedded diff hunks.

**CRITICAL:** Specialized agents read ONLY the JSON file. The diff hunks are already embedded - NO git commands needed. Zero redundant diff reads.

---

### AGENT 1: defensive-reviewer

```
Task(
  subagent_type: "code-foundations:defensive-reviewer",
  description: "Defensive review",
  prompt: """
Read agents/defensive-reviewer.md for your role.

Review for security AND error handling:
- Input validation at trust boundaries
- Injection prevention (SQL, command, path traversal)
- Auth checks BEFORE action
- Empty catch blocks
- Silent failures
- Error context preservation

YOUR INPUT: Read /tmp/pr-review-[RUN_ID]/triage.json and review ONLY `by_reviewer.defensive` entries.
Each entry contains: file, lines, description, and the actual diff hunk.

⛔ DO NOT run full `git diff` - the hunks are already in the JSON.
✅ You MAY run targeted git commands (git show, git blame, git log) if you need additional context.

If `by_reviewer.defensive` is empty or missing, write "No chunks assigned - PASS" to the output file.

OUTPUT: Write your review to /tmp/pr-review-[RUN_ID]/defensive.md using the Write tool.

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
  → /whiteboarding "[topic]"

### Verdict: HARDENED / ADEQUATE / FRAGILE / VULNERABLE

Return: "/tmp/pr-review-[RUN_ID]/defensive.md"
"""
)
```

---

### AGENT 2: quality-reviewer

```
Task(
  subagent_type: "code-foundations:quality-reviewer",
  description: "Quality review",
  prompt: """
Read agents/quality-reviewer.md for your role.

Review for design AND readability:
- Complexity symptoms (change amplification, cognitive load)
- Cohesion (routine does ONE thing)
- Coupling (minimized dependencies)
- Naming clarity
- Comment quality
- Style consistency
- Trailing newlines

YOUR INPUT: Read /tmp/pr-review-[RUN_ID]/triage.json and review ONLY `by_reviewer.quality` entries.
Each entry contains: file, lines, description, and the actual diff hunk.

⛔ DO NOT run full `git diff` - the hunks are already in the JSON.
✅ You MAY run targeted git commands (git show, git blame, git log) if you need additional context.

If `by_reviewer.quality` is empty or missing, write "No chunks assigned - PASS" to the output file.

OUTPUT: Write your review to /tmp/pr-review-[RUN_ID]/quality.md using the Write tool.

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
  → /whiteboarding "[topic]"

### Verdict: EXCELLENT / GOOD / ADEQUATE / POOR

Return: "/tmp/pr-review-[RUN_ID]/quality.md"
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
Read agents/correctness-reviewer.md for your role.

Review for bugs AND test coverage:
- Boundary conditions (off-by-one, empty, null, max)
- Logic flow (all paths, early returns)
- Duplicate handling
- Race conditions
- Test gaps for new code

YOUR INPUT: Read /tmp/pr-review-[RUN_ID]/triage.json and review ONLY `by_reviewer.correctness` entries.
Each entry contains: file, lines, description, and the actual diff hunk.

⛔ DO NOT run full `git diff` - the hunks are already in the JSON.
✅ You MAY run targeted git commands (git show, git blame, git log) if you need additional context.

If `by_reviewer.correctness` is empty or missing, write "No chunks assigned - PASS" to the output file.

OUTPUT: Write your review to /tmp/pr-review-[RUN_ID]/correctness.md using the Write tool.

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
  → /whiteboarding "[topic]"

### Verdict: VERIFIED / LIKELY CORRECT / UNCERTAIN / BUGGY

Return: "/tmp/pr-review-[RUN_ID]/correctness.md"
"""
)
```

---

### AGENT 4: performance-reviewer

```
Task(
  subagent_type: "code-foundations:performance-reviewer",
  description: "Performance review",
  prompt: """
Read agents/performance-reviewer.md for your role.

Review for performance:
- O(n²) or worse algorithms
- I/O in loops
- Resource allocation patterns
- Hot path efficiency
- Memory amplification

YOUR INPUT: Read /tmp/pr-review-[RUN_ID]/triage.json and review ONLY `by_reviewer.performance` entries.
Each entry contains: file, lines, description, and the actual diff hunk.

⛔ DO NOT run full `git diff` - the hunks are already in the JSON.
✅ You MAY run targeted git commands (git show, git blame, git log) if you need additional context.

If `by_reviewer.performance` is empty or missing, write "No chunks assigned - PASS" to the output file.

OUTPUT: Write your review to /tmp/pr-review-[RUN_ID]/performance.md using the Write tool.

FORMAT:
## Performance Review

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
  → /whiteboarding "[topic]"

### Verdict: OPTIMIZED / ACCEPTABLE / NEEDS ATTENTION / PROBLEMATIC

Return: "/tmp/pr-review-[RUN_ID]/performance.md"
"""
)
```

---

### AGENT 5: documentation-reviewer

```
Task(
  subagent_type: "code-foundations:documentation-reviewer",
  description: "Documentation review",
  prompt: """
Read agents/documentation-reviewer.md for your role.

Review documentation:
- README accuracy after changes
- Comment freshness (do comments match code?)
- API doc updates needed
- Changelog entries for user-facing changes
- CLAUDE.md / AI documentation updates

YOUR INPUT: Read /tmp/pr-review-[RUN_ID]/triage.json and review ONLY `by_reviewer.documentation` entries.
Each entry contains: file, lines, description, and the actual diff hunk.

⛔ DO NOT run full `git diff` - the hunks are already in the JSON.
✅ You MAY run targeted git commands (git show, git blame, git log) if you need additional context.

If `by_reviewer.documentation` is empty or missing, write "No chunks assigned - PASS" to the output file.

OUTPUT: Write your review to /tmp/pr-review-[RUN_ID]/documentation.md using the Write tool.

FORMAT:
## Documentation Review

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
  → /whiteboarding "[topic]"

### Verdict: COMPLETE / ADEQUATE / INCOMPLETE / MISSING

Return: "/tmp/pr-review-[RUN_ID]/documentation.md"
"""
)
```

---

### POST-DISPATCH VERIFICATION

After calling Task tool 5 times, mark todo "GATE: Dispatch ALL 5 review agents" as complete.

Mark todo "GATE: Wait for all 5 agents" as `in_progress`.

Wait for all 5 agents to return results.

Mark todo "GATE: Wait for all 5 agents" as complete.

---

## STEP 4: AGGREGATE RESULTS

Mark todo "Aggregate results" as `in_progress`.

**Collect file paths returned by agents**, then read all review files:
```bash
cat /tmp/pr-review-[RUN_ID]/defensive.md
cat /tmp/pr-review-[RUN_ID]/quality.md
cat /tmp/pr-review-[RUN_ID]/correctness.md
cat /tmp/pr-review-[RUN_ID]/performance.md
cat /tmp/pr-review-[RUN_ID]/documentation.md
```

**Synthesize into human-readable report** grouped by action type.
Write the final report to `/tmp/pr-review-[RUN_ID]/REPORT.md` AND output to user.

```markdown
# PR Review Report

## Summary
- **PR:** [title or branch name]
- **Branch:** [head] → [base]
- **Files Changed:** [count]

## Verdict: [APPROVE / REQUEST CHANGES / BLOCKED]

---

## Fix
High confidence. Apply these now.

### [file path]

1. [SEVERITY] Line [n] - [issue] ([agent])
   ```lang
   [code to apply]
   ```

---

## Investigate
Low confidence. Need more context.

### [file path]

1. [SEVERITY] Line [n] - [issue] ([agent])
   Check: [what to investigate]
   **Unknown**: [missing context]

---

## Plan
Systemic. Spin off to /whiteboarding.

1. [SEVERITY] [description] ([agent])
   → /whiteboarding "[topic]"

---

## Decide
Trade-offs needing human judgment.

1. [SEVERITY] [file:line] - [issue] ([agent])
   Options:
   - A: [option description]
   - B: [option description]
   **Unknown**: [what would inform decision]

---

## Summary Table

| Action | Count |
|--------|-------|
| Fix | [n] |
| Investigate | [n] |
| Plan | [n] |
| Decide | [n] |
```

### Verdict Logic

| Condition | Verdict |
|-----------|---------|
| Any CRITICAL | **BLOCKED** |
| IMPORTANT only | **REQUEST CHANGES** |
| SUGGESTIONS only | **APPROVE** with comments |
| No issues | **APPROVE** |

Mark todo "Aggregate results" as complete.

---

## STEP 5: EXECUTE ⛔ THIS IS THE LAW

**DO NOT SKIP THIS STEP. EXECUTION IS MANDATORY.**

### 5.1 Execute FIX Items

Mark todo "Execute FIX items" as `in_progress`.

For EACH item in the "Fix" section, dispatch a subagent:

```
Task(
  subagent_type: "code-foundations:implementation-agent",
  description: "Fix: [brief description]",
  prompt: """
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

### 5.2 Execute INVESTIGATE Items

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

### 5.3 Handle PLAN Items

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
/whiteboarding "[topic]"

Context from code review:
- Issue: [description]
- Files: [affected files]
- Severity: [CRITICAL/IMPORTANT]
- Unknown: [what we don't know]
```
```

Mark todo "Handle PLAN items" as complete when all prompts are generated.

---

### 5.4 Handle DECIDE Items

Mark todo "Handle DECIDE items" as `in_progress`.

For EACH item in the "Decide" section, ask the user:

```
AskUserQuestion(
  questions: [{
    question: "[Issue description]. Which approach?",
    header: "Decision",
    options: [
      {label: "[Option A]", description: "[description]"},
      {label: "[Option B]", description: "[description]"},
      {label: "Need more info", description: "Investigate further before deciding"},
      {label: "Needs planning", description: "Spin off to /whiteboarding"}
    ],
    multiSelect: false
  }]
)
```

Based on user response:
- User chooses an option → Execute as FIX
- "Need more info" → Move to INVESTIGATE queue and execute
- "Needs planning" → Move to PLAN section and output prompt

Mark todo "Handle DECIDE items" as complete when all decisions are resolved.

---

## STEP 6: FINAL VERIFICATION

Mark todo "Final verification" as `in_progress`.

**Verify ALL items are resolved:**

- [ ] All FIX items implemented and verified
- [ ] All INVESTIGATE items resolved (fixed, planned, or dismissed)
- [ ] All PLAN items have ready-to-copy prompts
- [ ] All DECIDE items have user responses and are executed
- [ ] `git status` shows expected state

```bash
git status
git diff --stat
```

Mark todo "Final verification" as complete.

**ONLY NOW MAY YOU STOP.**

---

## QUICK REFERENCE

### Agent Summary Table

| Agent | Combines | Skills |
|-------|----------|--------|
| defensive-reviewer | security + errors | cc-defensive-programming, aposd-simplifying-complexity |
| quality-reviewer | maintainability + clarity | aposd-reviewing-module-design, cc-code-layout-and-style |
| correctness-reviewer | bugs + tests | aposd-verifying-correctness, cc-quality-practices |
| performance-reviewer | algorithms + hot paths | cc-performance-tuning, aposd-optimizing-critical-paths |
| documentation-reviewer | docs + comments | cc-documentation-quality |

### Severity Levels

| Severity | Meaning | Verdict Impact |
|----------|---------|----------------|
| **CRITICAL** | Blocks merge | BLOCKED |
| **IMPORTANT** | Should fix | REQUEST CHANGES |
| **SUGGESTION** | Consider | APPROVE with comments |
