---
description: "Medium-depth review of staged or unstaged changes. Dispatches parallel agents for maintainability, error handling, and correctness. Use before committing or creating PR."
argument-hint: "[--staged | files...]"
allowed-tools: ["Bash", "Glob", "Grep", "Read", "Task"]
---

# Review Changes (Level 2 - Medium Review)

**MANDATORY:** This command MUST dispatch specialized review agents using the Task tool. DO NOT perform the review yourself. DO NOT skip agent dispatch.

## Phase 1: Get Changes

First, get the diff content that will be passed to agents:

```bash
# Determine scope based on arguments
if [[ "$ARGUMENTS" == "--staged" ]]; then
  # Staged changes only
  git diff --cached
elif [[ -n "$ARGUMENTS" ]]; then
  # Specific files
  git diff $ARGUMENTS
else
  # Default: unstaged changes
  git diff
fi
```

Store the diff output - you will pass it to each agent.

---

## Phase 2: Dispatch Review Agents

**YOU MUST USE THE TASK TOOL TO DISPATCH THESE AGENTS IN PARALLEL.**

Launch ALL 3 agents simultaneously in a SINGLE message with multiple Task tool calls:

### Agent 1: maintainability-reviewer

```
Task tool call:
- subagent_type: "general-purpose"
- description: "Maintainability review"
- prompt: |
    You are a maintainability reviewer. Review this git diff for design quality.

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

### Agent 2: error-handling-reviewer

```
Task tool call:
- subagent_type: "general-purpose"
- description: "Error handling review"
- prompt: |
    You are an error handling reviewer. Review this git diff for error handling issues.

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

### Agent 3: correctness-reviewer

```
Task tool call:
- subagent_type: "general-purpose"
- description: "Correctness review"
- prompt: |
    You are a correctness reviewer. Review this git diff for bugs and logic errors.

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

## Phase 3: Quick Local Checks (While Agents Run)

While waiting for agents, do a quick scan for:
- Variable names unclear?
- Comments present for complex code?
- Formatting consistent?

---

## Phase 4: Aggregate Results

After ALL agents complete, combine their findings:

```markdown
# Review Changes Report

## Scope
[files reviewed]

## Overall Verdict: [READY / NEEDS WORK / BLOCKED]

---

## Critical Issues - Must Fix
[Combine all CRITICAL findings]

## Important Issues - Should Fix
[Combine all IMPORTANT findings]

## Suggestions
[Combine all SUGGESTIONS]

## Positive Patterns
[Note good patterns]

---

## Action Plan
1. Fix critical issues
2. Address important issues
3. Re-run: `/review-changes` to verify
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

## REMINDER

**DO NOT:**
- Skip agent dispatch and review the code yourself
- Launch agents sequentially - use parallel dispatch
- Summarize without actually running agents

**YOU MUST:**
- Use the Task tool to dispatch all 3 agents
- Pass the actual git diff content to each agent
- Wait for all agents to complete
- Aggregate their findings into the unified report

---

## Usage Examples

```bash
# Review unstaged changes (default)
/review-changes

# Review staged changes only
/review-changes --staged

# Review specific files
/review-changes src/api/handler.ts src/utils/validate.ts
```
