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

## STEP 1: GET PR DIFF

Mark todo "Get PR diff" as `in_progress`.

```bash
gh pr view --json number,title,baseRefName,headRefName 2>/dev/null || echo "No PR"
git diff --name-only $(git merge-base HEAD main)..HEAD
git diff $(git merge-base HEAD main)..HEAD | wc -l  # Count lines for size check
git diff $(git merge-base HEAD main)..HEAD  # Full diff
```

**SIZE CHECK:**
- Lines > 500 OR files > 10 → Must run triage (Step 2)
- Otherwise → Skip to Step 3

Store the full diff in memory. Mark todo complete.

---

## STEP 2: TRIAGE (LARGE DIFFS ONLY)

**GATE CONDITION:** Only run if diff > 500 lines OR > 10 files.

Mark todo "Run triage" as `in_progress`.

Dispatch triage agent:

```
Task(
  subagent_type: "general-purpose",
  model: "haiku",
  description: "Triage PR changes",
  prompt: """
Triage this PR diff for routing to specialized reviewers.

GIT DIFF:
<diff>
[PASTE FULL DIFF HERE]
</diff>

TASK: For each logical change chunk, output JSON:

{
  "chunks": [
    {
      "file": "path/to/file.ext",
      "lines": [start, end],
      "description": "what this change DOES",
      "reviewers": ["defensive", "quality", "correctness", "performance", "documentation"]
    }
  ]
}

REVIEWER MAPPING:
- Input validation, auth, error handling → defensive
- Naming, complexity, cohesion → quality
- Logic, boundaries, tests → correctness
- O(n²), loops, resources → performance
- Comments, README, docs → documentation

OUTPUT: JSON only, no explanation.
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
- [ ] You have the diff stored in memory
- [ ] If large diff, triage JSON is available
- [ ] You are about to call Task tool 5 times in ONE message

### THE 5 AGENT PROMPTS

Use these EXACT prompts. Call ALL 5 in a SINGLE message with the Task tool.

**INPUT SELECTION:**
- Small diff (< 500 lines, < 10 files): Pass entire diff to all agents
- Large diff (triage ran): Pass only chunks routed to each reviewer

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

GIT DIFF:
<diff>
[PASTE DIFF OR TRIAGED CHUNKS HERE]
</diff>

OUTPUT FORMAT:
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

GIT DIFF:
<diff>
[PASTE DIFF OR TRIAGED CHUNKS HERE]
</diff>

OUTPUT FORMAT:
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

GIT DIFF:
<diff>
[PASTE DIFF OR TRIAGED CHUNKS HERE]
</diff>

OUTPUT FORMAT:
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

GIT DIFF:
<diff>
[PASTE DIFF OR TRIAGED CHUNKS HERE]
</diff>

OUTPUT FORMAT:
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

GIT DIFF:
<diff>
[PASTE DIFF OR TRIAGED CHUNKS HERE]
</diff>

OUTPUT FORMAT:
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

Combine findings from all 5 agents **grouped by action type**.

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
