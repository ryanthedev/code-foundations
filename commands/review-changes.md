---
description: "Medium-depth review with 3 parallel agents: defensive (security+errors), quality (maintainability+clarity), and correctness (bugs+tests)."
argument-hint: "[--staged | files...]"
allowed-tools: ["Bash", "Glob", "Grep", "Read", "Task", "Skill"]
---

# Review Changes (Level 2 - Medium Review)

**MANDATORY:** Dispatch 3 specialized review agents. DO NOT review code yourself.

---

## Phase 1: Invoke oberagent (if available)

```
Skill(oberskills:oberagent)
```

Skip if oberskills not installed.

---

## Phase 2: Get Changes

```bash
# Staged, specific files, or unstaged (default)
if [[ "$ARGUMENTS" == "--staged" ]]; then
  git diff --cached
elif [[ -n "$ARGUMENTS" ]]; then
  git diff $ARGUMENTS
else
  git diff
fi
```

Store the diff. Check size to determine if triage is needed.

---

## Phase 2.5: Triage (Large Diffs Only)

**Threshold:** If diff > 500 lines OR > 10 files, run triage first.

### Dispatch Triage Agent

```
Task tool:
- subagent_type: "general-purpose"
- model: "sonnet"
- description: "Triage changes"
- prompt: |
    Triage this diff for routing to specialized reviewers.

    REFERENCE: Read references/triage-tags.md for tag vocabulary and mapping.

    GIT DIFF:
    [paste diff]

    TASK:
    Go file by file, method by method. For each logical chunk of change, create a JSON object.

    CHECKLIST (complete for EACH chunk):
    - [ ] Identify file path and line range
    - [ ] Write concise description (what the change DOES, not what it IS)
    - [ ] Apply 1-3 tags from triage-tags.md (max 3 per cognitive research)
    - [ ] Derive reviewers from tag mapping (only: defensive, quality, correctness)
    - [ ] Add to chunks array

    OUTPUT FORMAT (JSON):
    ```json
    {
      "chunks": [
        {
          "file": "src/auth/login.ts",
          "lines": [15, 42],
          "description": "validates user input before DB query",
          "tags": ["validation", "injection"],
          "reviewers": ["defensive"]
        },
        {
          "file": "src/services/user.ts",
          "lines": [88, 95],
          "description": "retries failed API calls with backoff",
          "tags": ["retry", "async"],
          "reviewers": ["defensive", "correctness"]
        }
      ]
    }
    ```

    STOP CONDITIONS:
    - Do NOT skip any changed method/function
    - Do NOT invent tags outside triage-tags.md
    - Do NOT include explanations outside the JSON
```

### Parse Triage Output

The triage output is JSON. Filter chunks array by reviewer and pass only relevant chunks to each agent.

```
For each reviewer:
  1. Filter chunks where reviewers[] contains that reviewer
  2. Extract file and lines for each matching chunk
  3. Get actual diff for those line ranges
  4. Pass to reviewer as JSON context + diff chunks
```

**Skip triage for small diffs** - pass entire diff to all reviewers (existing behavior).

---

## Phase 3: Dispatch 3 Agents in Parallel

**USE TASK TOOL - ALL 3 AGENTS IN SINGLE MESSAGE**

### Input Selection

| Diff Size | Input to Each Agent |
|-----------|---------------------|
| Small (< 500 lines, < 10 files) | Entire diff |
| Large (triage ran) | Only chunks routed to that reviewer |

If triage ran, include relevant `changes.txt` lines for context.

### Agent 1: defensive-reviewer

```
Task tool:
- subagent_type: "general-purpose"
- description: "Defensive review"
- prompt: |
    First invoke code-foundations skill, then read agents/defensive-reviewer.md.

    Review for security AND error handling: input validation, injection, auth, catch blocks, silent failures.

    [If triage ran: TRIAGE CONTEXT + DIFF CHUNKS]
    [If small diff: GIT DIFF: full diff]

    Return: VERDICT + issues grouped by action (Fix/Investigate/Plan)
```

### Agent 2: quality-reviewer

```
Task tool:
- subagent_type: "general-purpose"
- description: "Quality review"
- prompt: |
    First invoke code-foundations skill, then read agents/quality-reviewer.md.

    Review for design AND readability: complexity, cohesion, naming, comments, style, trailing newlines.

    [If triage ran: TRIAGE CONTEXT + DIFF CHUNKS]
    [If small diff: GIT DIFF: full diff]

    Return: VERDICT + issues grouped by action (Fix/Investigate/Plan)
```

### Agent 3: correctness-reviewer

```
Task tool:
- subagent_type: "general-purpose"
- description: "Correctness review"
- prompt: |
    First invoke code-foundations skill, then read agents/correctness-reviewer.md.

    Review for bugs AND test coverage: boundaries, logic flow, duplicates, test gaps.

    [If triage ran: TRIAGE CONTEXT + DIFF CHUNKS]
    [If small diff: GIT DIFF: full diff]

    Return: VERDICT + issues grouped by action (Fix/Investigate/Plan)
```

---

## Phase 4: Aggregate Results (GROUP BY ACTION)

Group findings by **action type** (what to do next).

```markdown
# Review Changes Report

## Scope
[files reviewed]

## Verdict: [READY / NEEDS WORK / BLOCKED]

---

## Fix
High confidence. Apply now.

### [filename]
1. 🔴 [CRITICAL] Line X - [issue] (agent)
   ```lang
   [code to apply]
   ```

2. 🟡 [IMPORTANT] Line Y - [issue] (agent)
   Fix: [description]

---

## Investigate
Low confidence. Need context.

1. 🟡 [IMPORTANT] file:line - [issue] (agent)
   Check: [what to investigate]
   **Unknown**: [what we don't know]

---

## Plan
Systemic. Spin off to `/whiteboarding`.

1. 🔴 [CRITICAL] [description]
   → `/whiteboarding "[topic]"`

---

## Summary

| Action | Count |
|--------|-------|
| Fix | [n] |
| Investigate | [n] |
| Plan | [n] |
```

---

## Verdict Logic

| Condition | Verdict |
|-----------|---------|
| Any CRITICAL | **BLOCKED** |
| IMPORTANT only | **NEEDS WORK** |
| SUGGESTIONS only | **READY** |
| No issues | **READY** |

---

## Phase 5: Execute (THE LAW)

After presenting the review report, **execute to completion**. This is mandatory.

### 5.1 Execute FIX Items

For EACH item in the "Fix" section, dispatch a subagent:

```
Task tool:
- subagent_type: "general-purpose"
- description: "Fix: [brief description]"
- prompt: |
    Invoke code-foundations skill.

    TASK: Implement this fix.

    FILE: [file path]
    LINE: [line number]
    ISSUE: [issue description]
    FIX: [the code/fix from review]

    CHECKLIST:
    - [ ] Read the file to understand context
    - [ ] Apply the fix exactly as specified
    - [ ] Run tests if available
    - [ ] Verify the fix compiles/passes

    CHECKPOINT: Do not return until fix is verified working.
```

Dispatch FIX agents in parallel where files don't overlap.

**Iterate until all FIX items are complete.**

---

### 5.2 Execute INVESTIGATE Items

For EACH item in the "Investigate" section, dispatch a subagent:

```
Task tool:
- subagent_type: "general-purpose"
- description: "Investigate: [brief description]"
- prompt: |
    Invoke code-foundations skill.
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
```

If investigation returns "FIX with code", add to FIX queue and execute.
If investigation returns "PLAN needed", add to PLAN section.

---

### 5.3 Handle PLAN Items

For EACH item in the "Plan" section, **output a ready-to-use prompt** for a new session:

```markdown
## New Session Required

The following items require dedicated planning sessions.
Copy the prompt and start a new Claude session.

### Plan 1: [topic]

**Issue:** [description]
**Files affected:** [list]

**Prompt to copy:**
\`\`\`
/whiteboarding "[topic]"

Context from code review:
- Issue: [description]
- Files: [affected files]
- Severity: [CRITICAL/IMPORTANT]
- Unknown: [what we don't know]
\`\`\`
```

---

## Execution Checklist

- [ ] All FIX items implemented and verified
- [ ] All INVESTIGATE items resolved (fixed, planned, or dismissed)
- [ ] All PLAN items have ready-to-copy prompts
- [ ] Final `git status` shows clean or expected state

**DO NOT STOP until this checklist is complete.**

---

## MANDATORY

1. **Large diffs (> 500 lines OR > 10 files):** Run triage first (Phase 2.5)
2. Dispatch ALL 3 review agents in parallel (with routed chunks if triaged)
3. **Group output by ACTION** (Fix / Investigate / Plan)
4. **EXECUTE Phase 5** - this is THE LAW
5. FIX items → subagents with code-foundations → implement → verify
6. INVESTIGATE items → subagents with cc-debugging → resolve
7. PLAN items → output ready-to-copy prompts for new sessions
8. **Iterate until execution checklist is complete**

---

## Usage

```bash
/review-changes           # Unstaged changes
/review-changes --staged  # Staged only
/review-changes file.ts   # Specific files
```
