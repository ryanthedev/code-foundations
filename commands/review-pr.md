---
description: "Comprehensive multi-dimensional PR review. Dispatches parallel agents for security, performance, maintainability, error handling, clarity, and correctness. Use before merging."
argument-hint: "[aspects...] [--parallel]"
allowed-tools: ["Bash", "Glob", "Grep", "Read", "Task", "Skill"]
---

# Review PR (Level 3 - Full Review)

**MANDATORY:** This command MUST invoke oberagent and dispatch specialized review agents. DO NOT perform the review yourself. DO NOT skip these steps.

---

## Phase 1: Invoke oberagent

**YOU MUST INVOKE THE OBERAGENT SKILL FIRST.**

```
Skill(oberskills:oberagent)
```

This ensures proper agent dispatch with validated prompts.

---

## Phase 2: Get PR Diff

Get the diff content that will be passed to agents:

```bash
# Get PR info
gh pr view --json number,title,baseRefName,headRefName 2>/dev/null || echo "No PR - reviewing branch changes"

# Get changed files list
git diff --name-only $(git merge-base HEAD main)..HEAD

# Get full diff for agents
git diff $(git merge-base HEAD main)..HEAD
```

Store the diff output - you will pass it to each agent.

---

## Phase 3: Validate Agent Prompts (oberagent checklist)

Before dispatching, validate each agent prompt against oberagent checklist:

| # | Check | Requirement |
|---|-------|-------------|
| 1 | Purpose is OUTCOME | What to find, not how to find it |
| 2 | Agent type matches | general-purpose for code review |
| 3 | Skills specified | "First invoke [skill]" in prompt |
| 4 | Prompt ≤3 sentences | Or justified if longer |
| 5 | No step-by-step HOW | Trust agent capability |
| 6 | Scope provided | Diff content included |

---

## Phase 4: Dispatch Review Agents

**YOU MUST USE THE TASK TOOL TO DISPATCH ALL 6 AGENTS IN PARALLEL (single message, multiple Task calls).**

### Agent 1: security-reviewer

```
Task tool call:
- subagent_type: "general-purpose"
- description: "Security review"
- prompt: |
    First invoke the code-foundations skill, then read agents/security-reviewer.md for your review checklist.

    Review this PR diff for security vulnerabilities. Focus on: input validation, injection flaws, auth bypasses, secrets exposure, path traversal.

    GIT DIFF:
    [paste diff here]

    Return: VERDICT (SECURE/CONCERNS/VULNERABLE) with specific file:line references for any issues.
```

### Agent 2: performance-reviewer

```
Task tool call:
- subagent_type: "general-purpose"
- description: "Performance review"
- prompt: |
    First invoke the code-foundations skill, then read agents/performance-reviewer.md for your review checklist.

    Review this PR diff for performance issues. Focus on: O(n²)+ algorithms, nested loops, I/O in loops, missing caching, hot path inefficiencies.

    GIT DIFF:
    [paste diff here]

    Return: VERDICT (OPTIMAL/ACCEPTABLE/CONCERNING/SLOW) with specific file:line references for any issues.
```

### Agent 3: maintainability-reviewer

```
Task tool call:
- subagent_type: "general-purpose"
- description: "Maintainability review"
- prompt: |
    First invoke the code-foundations skill, then read agents/maintainability-reviewer.md for your review checklist.

    Review this PR diff for design quality. Focus on: complexity symptoms, shallow modules, information leakage, cohesion/coupling, parameters >7.

    GIT DIFF:
    [paste diff here]

    Return: VERDICT (EXCELLENT/GOOD/CONCERNING/POOR) with specific file:line references for any issues.
```

### Agent 4: error-handling-reviewer

```
Task tool call:
- subagent_type: "general-purpose"
- description: "Error handling review"
- prompt: |
    First invoke the code-foundations skill, then read agents/error-handling-reviewer.md for your review checklist.

    Review this PR diff for error handling issues. Focus on: empty catch blocks, silent failures, broad exception catching, missing error context.

    GIT DIFF:
    [paste diff here]

    Return: VERDICT (ROBUST/ADEQUATE/FRAGILE/BROKEN) with specific file:line references for any issues.
```

### Agent 5: clarity-reviewer

```
Task tool call:
- subagent_type: "general-purpose"
- description: "Clarity review"
- prompt: |
    First invoke the code-foundations skill, then read agents/clarity-reviewer.md for your review checklist.

    Review this PR diff for readability. Focus on: unclear naming, missing/stale comments, inconsistent formatting, complex unexplained expressions.

    GIT DIFF:
    [paste diff here]

    Return: VERDICT (CLEAR/READABLE/CONFUSING/OBSCURE) with specific file:line references for any issues.
```

### Agent 6: correctness-reviewer

```
Task tool call:
- subagent_type: "general-purpose"
- description: "Correctness review"
- prompt: |
    First invoke the code-foundations skill, then read agents/correctness-reviewer.md for your review checklist.

    Review this PR diff for bugs. Focus on: boundary conditions, off-by-one errors, race conditions, resource leaks, null safety.

    GIT DIFF:
    [paste diff here]

    Return: VERDICT (VERIFIED/LIKELY CORRECT/UNCERTAIN/BUGGY) with specific file:line references for any issues.
```

---

## Phase 5: Aggregate Results

After ALL agents complete, combine their findings:

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

## MANDATORY STEPS (DO NOT SKIP)

1. **Invoke oberagent skill** - Validates agent dispatch
2. **Get PR diff** - Content for agents to review
3. **Validate prompts** - Check against oberagent checklist
4. **Dispatch ALL 6 agents in parallel** - Use Task tool
5. **Aggregate results** - Combine into unified report

**DO NOT:**
- Skip oberagent invocation
- Skip agent dispatch and review code yourself
- Launch agents sequentially
- Omit skill invocation from agent prompts
