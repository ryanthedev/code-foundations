---
description: "Comprehensive PR review with 5 parallel agents: defensive (security+errors), quality (maintainability+clarity), correctness (bugs+tests), performance, and documentation."
argument-hint: "[--parallel]"
allowed-tools: ["Bash", "Glob", "Grep", "Read", "Task", "Skill"]
---

# Review PR (Level 3 - Full Review)

**MANDATORY:** Dispatch 5 specialized review agents. DO NOT review code yourself.

---

## Phase 1: Invoke oberagent (if available)

```
Skill(oberskills:oberagent)
```

Skip if oberskills not installed.

---

## Phase 2: Get PR Diff

```bash
gh pr view --json number,title,baseRefName,headRefName 2>/dev/null || echo "No PR"
git diff --name-only $(git merge-base HEAD main)..HEAD
git diff $(git merge-base HEAD main)..HEAD
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
- description: "Triage PR changes"
- prompt: |
    Triage this PR diff for routing to specialized reviewers.

    REFERENCE: Read references/triage-tags.md for tag vocabulary and mapping.

    GIT DIFF:
    [paste diff]

    TASK:
    Go file by file, method by method. For each logical chunk of change, write ONE line:

    FORMAT:
    file:start-end | description | [tags] | reviewers

    RULES:
    1. One line per method/function/logical block changed
    2. Description: what the change DOES (not what it IS), max 10 words
    3. Tags: max 3, pick most specific from triage-tags.md
    4. Reviewers: derive from tags using the mapping in triage-tags.md
    5. If a chunk touches multiple concerns, list all relevant reviewers

    EXAMPLE OUTPUT:
    src/auth/login.ts:15-42 | validates user input before DB query | [validation, injection] | defensive
    src/auth/login.ts:44-60 | adds session timeout handling | [auth, error-handling] | defensive
    src/services/user.ts:88-95 | retries failed API calls with backoff | [retry, async] | defensive, correctness
    src/services/user.ts:100-120 | caches user preferences | [cache, state] | performance, correctness
    src/components/List.tsx:20-45 | renders filtered user list | [loop, interface] | performance, quality
    src/utils/format.ts:5-15 | extracts date formatting helper | [structure] | quality
    README.md:1-50 | updates installation instructions | [readme] | documentation

    OUTPUT: Write all lines to a single code block. No headers, no explanations.
```

### Parse Triage Output

The triage output becomes `changes.txt`. Use it to route chunks to reviewers:

```
For each reviewer:
  1. Filter changes.txt for lines containing that reviewer
  2. For each matching line, extract file:start-end
  3. Get the actual diff chunk for those lines
  4. Pass only relevant chunks to that reviewer
```

**Skip triage for small diffs** - pass entire diff to all reviewers (existing behavior).

---

## Phase 3: Dispatch 5 Agents in Parallel

**USE TASK TOOL - ALL 5 AGENTS IN SINGLE MESSAGE**

### Input Selection

| Diff Size | Input to Each Agent |
|-----------|---------------------|
| Small (< 500 lines, < 10 files) | Entire diff |
| Large (triage ran) | Only chunks routed to that reviewer |

If triage ran, include the relevant `changes.txt` lines so reviewer has context:

```
TRIAGE CONTEXT (your assigned chunks):
src/auth/login.ts:15-42 | validates user input before DB query | [validation, injection]
src/auth/login.ts:44-60 | adds session timeout handling | [auth, error-handling]

DIFF CHUNKS:
[only the diff for lines 15-60 of src/auth/login.ts]
```

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
    For bug-fix PRs, reference cc-debugging skill for debugging methodology verification.

    [If triage ran: TRIAGE CONTEXT + DIFF CHUNKS]
    [If small diff: GIT DIFF: full diff]

    Return: VERDICT + issues grouped by action (Fix/Investigate/Plan)
```

### Agent 4: performance-reviewer

```
Task tool:
- subagent_type: "general-purpose"
- description: "Performance review"
- prompt: |
    First invoke code-foundations skill, then read agents/performance-reviewer.md.

    Review for performance: O(n²), I/O in loops, resource usage, hot paths.

    [If triage ran: TRIAGE CONTEXT + DIFF CHUNKS]
    [If small diff: GIT DIFF: full diff]

    Return: VERDICT + issues grouped by action (Fix/Investigate/Plan)
```

### Agent 5: documentation-reviewer

```
Task tool:
- subagent_type: "general-purpose"
- description: "Documentation review"
- prompt: |
    First invoke code-foundations skill, then read agents/documentation-reviewer.md.

    Review documentation: README accuracy, comment freshness, API docs, changelog.

    [If triage ran: TRIAGE CONTEXT + DIFF CHUNKS]
    [If small diff: GIT DIFF: full diff]

    Return: VERDICT + issues grouped by action (Fix/Investigate/Plan)
```

---

## Phase 4: Aggregate Results (GROUP BY ACTION)

Combine findings **grouped by action type** (what to do next).

```markdown
# PR Review Report

## Summary
- **PR:** [title]
- **Branch:** [head] → [base]
- **Files Changed:** [count]

## Verdict: [APPROVE / REQUEST CHANGES / BLOCKED]

---

## Fix
High confidence. Apply these now.

### src/middleware/FeatureHeader.cs

1. 🔴 [CRITICAL] Line 84 - Base64 memory amplification (defensive)
   ```csharp
   if (encoded.Length > MaxDecodedSize / 1.34) return null;
   ```

2. 🟡 [IMPORTANT] Line 58 - Silent JSON failure (defensive)
   Fix: Add telemetry logging

3. 🟡 [IMPORTANT] Line 134 - Missing trailing newline (quality)
   Fix: Add newline at EOF

---

## Investigate
Low confidence. Need more context.

### src/services/UserService.cs

1. 🟡 [IMPORTANT] Line 200 - Possible race condition (correctness)
   Check: Is this method called concurrently?
   **Unknown**: Thread safety requirements for this service.

---

## Plan
Systemic. Spin off to `/whiteboarding`.

1. 🔴 [CRITICAL] Auth middleware missing from 5 endpoints (defensive)
   → `/whiteboarding "auth middleware pattern"`

---

## Decide
Trade-offs needing human judgment.

1. 🟡 [IMPORTANT] Settings.cs:30 - Cache TTL seems too long (performance)
   Options:
   - A: 5 min TTL - fresher data, more load
   - B: 1 hour TTL - stale data, less load
   **Unknown**: Acceptable staleness?

---

## Summary

| Action | Count |
|--------|-------|
| Fix | [n] |
| Investigate | [n] |
| Plan | [n] |
| Decide | [n] |

**Next Steps:**
1. Apply "Fix" items now
2. Spin off "Investigate" as tasks
3. Run `/whiteboarding` for "Plan" items
4. Discuss "Decide" with stakeholders
```

---

## Verdict Logic

| Condition | Verdict |
|-----------|---------|
| Any CRITICAL | **BLOCKED** |
| IMPORTANT only | **REQUEST CHANGES** |
| SUGGESTIONS only | **APPROVE** with comments |
| No issues | **APPROVE** |

---

## Agent Summary Table

| Agent | Combines | Skills |
|-------|----------|--------|
| defensive-reviewer | security + errors | cc-defensive-programming, aposd-simplifying-complexity |
| quality-reviewer | maintainability + clarity | aposd-reviewing-module-design, cc-code-layout-and-style |
| correctness-reviewer | bugs + tests | aposd-verifying-correctness, cc-quality-practices |
| performance-reviewer | algorithms + hot paths | cc-performance-tuning, aposd-optimizing-critical-paths |
| documentation-reviewer | docs + comments | cc-documentation-quality |

---

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

### 5.4 Handle DECIDE Items

For EACH item in the "Decide" section, **ask the user**:

```
AskUserQuestion tool:
- question: "[Issue description]. Which approach?"
- options:
  - A: [option A description]
  - B: [option B description]
```

Based on user response, either:
- Execute as FIX if user chooses an option
- Move to INVESTIGATE if user says "need more info"
- Move to PLAN if user says "needs broader discussion"

---

## Execution Checklist

- [ ] All FIX items implemented and verified
- [ ] All INVESTIGATE items resolved (fixed, planned, or dismissed)
- [ ] All PLAN items have ready-to-copy prompts
- [ ] All DECIDE items have user responses and are executed
- [ ] Final `git status` shows clean or expected state

**DO NOT STOP until this checklist is complete.**

---

## MANDATORY

1. **Large diffs (> 500 lines OR > 10 files):** Run triage first (Phase 2.5)
2. Dispatch ALL 5 review agents in parallel (with routed chunks if triaged)
3. **Group output by ACTION** (Fix / Investigate / Plan / Decide)
4. **EXECUTE Phase 5** - this is THE LAW
5. FIX items → subagents with code-foundations → implement → verify
6. INVESTIGATE items → subagents with cc-debugging → resolve
7. PLAN items → output ready-to-copy prompts for new sessions
8. DECIDE items → ask user → execute based on response
9. **Iterate until execution checklist is complete**
