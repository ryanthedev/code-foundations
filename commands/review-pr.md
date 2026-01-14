---
description: "Comprehensive multi-dimensional PR review. Dispatches parallel agents for security, performance, maintainability, error handling, clarity, and correctness. Use before merging."
argument-hint: "[aspects...] [--parallel]"
allowed-tools: ["Bash", "Glob", "Grep", "Read", "Task"]
---

# Review PR (Level 3 - Full Review)

**MANDATORY:** This command MUST dispatch specialized review agents using the Task tool. DO NOT perform the review yourself. DO NOT skip agent dispatch.

## Phase 1: Get PR Diff

First, get the diff content that will be passed to agents:

```bash
# Get PR info
gh pr view --json number,title,baseRefName,headRefName 2>/dev/null || echo "No PR - reviewing branch changes"

# Get changed files
git diff --name-only $(git merge-base HEAD main)..HEAD

# Save diff to variable for agents
DIFF=$(git diff $(git merge-base HEAD main)..HEAD)
```

Store the diff output - you will pass it to each agent.

---

## Phase 2: Dispatch Review Agents

**YOU MUST USE THE TASK TOOL TO DISPATCH THESE AGENTS IN PARALLEL.**

Launch ALL of the following agents simultaneously in a SINGLE message with multiple Task tool calls:

### Agent 1: security-reviewer

```
Task tool call:
- subagent_type: "general-purpose"
- description: "Security review"
- prompt: |
    You are a security reviewer. Review this git diff for security vulnerabilities.

    Use the security-reviewer agent prompt from agents/security-reviewer.md as your guide.

    Check for:
    - Input validation issues
    - Injection vulnerabilities (SQL, command, XSS)
    - Auth/authz bypasses
    - Secrets exposure
    - Path traversal

    GIT DIFF TO REVIEW:
    [paste the diff here]

    Output format:
    ## Security Review
    ### Critical: [list or "None"]
    ### Important: [list or "None"]
    ### Suggestions: [list or "None"]
    ### Verdict: SECURE / CONCERNS / VULNERABLE
```

### Agent 2: performance-reviewer

```
Task tool call:
- subagent_type: "general-purpose"
- description: "Performance review"
- prompt: |
    You are a performance reviewer. Review this git diff for performance issues.

    Use the performance-reviewer agent prompt from agents/performance-reviewer.md as your guide.

    Check for:
    - O(n²) or worse algorithms
    - Nested loops
    - Database/API calls inside loops
    - Missing caching opportunities
    - Resource-intensive operations in hot paths

    GIT DIFF TO REVIEW:
    [paste the diff here]

    Output format:
    ## Performance Review
    ### Critical: [list or "None"]
    ### Important: [list or "None"]
    ### Suggestions: [list or "None"]
    ### Verdict: OPTIMAL / ACCEPTABLE / CONCERNING / SLOW
```

### Agent 3: maintainability-reviewer

```
Task tool call:
- subagent_type: "general-purpose"
- description: "Maintainability review"
- prompt: |
    You are a maintainability reviewer. Review this git diff for design quality.

    Use the maintainability-reviewer agent prompt from agents/maintainability-reviewer.md as your guide.

    Check for:
    - Complexity symptoms (change amplification, cognitive load, unknown unknowns)
    - Shallow modules (interface ≈ implementation)
    - Information leakage
    - Cohesion/coupling issues
    - Parameters > 7
    - Inheritance depth > 3

    GIT DIFF TO REVIEW:
    [paste the diff here]

    Output format:
    ## Maintainability Review
    ### Critical: [list or "None"]
    ### Important: [list or "None"]
    ### Suggestions: [list or "None"]
    ### Verdict: EXCELLENT / GOOD / CONCERNING / POOR
```

### Agent 4: error-handling-reviewer

```
Task tool call:
- subagent_type: "general-purpose"
- description: "Error handling review"
- prompt: |
    You are an error handling reviewer. Review this git diff for error handling issues.

    Use the error-handling-reviewer agent prompt from agents/error-handling-reviewer.md as your guide.

    Check for:
    - Empty catch blocks
    - Silent failures (errors swallowed)
    - Broad exception catching
    - Missing error context
    - Inconsistent error strategies

    GIT DIFF TO REVIEW:
    [paste the diff here]

    Output format:
    ## Error Handling Review
    ### Critical: [list or "None"]
    ### Important: [list or "None"]
    ### Suggestions: [list or "None"]
    ### Verdict: ROBUST / ADEQUATE / FRAGILE / BROKEN
```

### Agent 5: clarity-reviewer

```
Task tool call:
- subagent_type: "general-purpose"
- description: "Clarity review"
- prompt: |
    You are a clarity reviewer. Review this git diff for readability issues.

    Use the clarity-reviewer agent prompt from agents/clarity-reviewer.md as your guide.

    Check for:
    - Unclear variable/function names
    - Missing or stale comments
    - Inconsistent formatting
    - Complex expressions needing explanation

    GIT DIFF TO REVIEW:
    [paste the diff here]

    Output format:
    ## Clarity Review
    ### Critical: [list or "None"]
    ### Important: [list or "None"]
    ### Suggestions: [list or "None"]
    ### Verdict: CLEAR / READABLE / CONFUSING / OBSCURE
```

### Agent 6: correctness-reviewer

```
Task tool call:
- subagent_type: "general-purpose"
- description: "Correctness review"
- prompt: |
    You are a correctness reviewer. Review this git diff for bugs and logic errors.

    Use the correctness-reviewer agent prompt from agents/correctness-reviewer.md as your guide.

    Check for:
    - Boundary conditions (empty, null, max size)
    - Off-by-one errors
    - Race conditions
    - Resource leaks
    - Null/undefined safety

    GIT DIFF TO REVIEW:
    [paste the diff here]

    Output format:
    ## Correctness Review
    ### Critical: [list or "None"]
    ### Important: [list or "None"]
    ### Suggestions: [list or "None"]
    ### Verdict: VERIFIED / LIKELY CORRECT / UNCERTAIN / BUGGY
```

---

## Phase 3: Aggregate Results

After ALL agents complete, combine their findings into a unified report:

```markdown
# PR Review Report

## Summary
- **PR:** [title]
- **Branch:** [head] → [base]
- **Files Changed:** [count]
- **Agents Run:** security, performance, maintainability, errors, clarity, correctness

## Overall Verdict: [APPROVE / REQUEST CHANGES / BLOCKED]

---

## Critical Issues - Must Fix Before Merge
[Combine all CRITICAL findings from all agents]

## Important Issues - Should Fix
[Combine all IMPORTANT findings from all agents]

## Suggestions - Consider
[Combine all SUGGESTIONS from all agents]

## Positive Patterns
[Note good patterns observed]

---

## Action Plan
1. Fix critical issues
2. Address important issues
3. Re-run: `/review-pr` to verify fixes
```

---

## Verdict Logic

| Condition | Verdict |
|-----------|---------|
| Any CRITICAL from any agent | **BLOCKED** |
| IMPORTANT only, no CRITICAL | **REQUEST CHANGES** |
| SUGGESTIONS only | **APPROVE** with comments |
| No issues | **APPROVE** |

---

## REMINDER

**DO NOT:**
- Skip agent dispatch and review the code yourself
- Launch agents sequentially - use parallel dispatch
- Summarize without actually running agents

**YOU MUST:**
- Use the Task tool to dispatch all 6 agents
- Pass the actual git diff content to each agent
- Wait for all agents to complete
- Aggregate their findings into the unified report
