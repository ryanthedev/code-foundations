---
description: "Medium-depth review of staged or unstaged changes. Dispatches parallel agents for maintainability, error handling, and correctness. Use before committing or creating PR."
argument-hint: "[--staged | files...]"
allowed-tools: ["Bash", "Glob", "Grep", "Read", "Task", "Skill"]
---

# Review Changes (Level 2 - Medium Review)

**MANDATORY:** This command MUST invoke oberagent and dispatch specialized review agents. DO NOT perform the review yourself. DO NOT skip these steps.

---

## Phase 1: Invoke oberagent

**YOU MUST INVOKE THE OBERAGENT SKILL FIRST.**

```
Skill(oberskills:oberagent)
```

This ensures proper agent dispatch with validated prompts.

---

## Phase 2: Get Changes

Get the diff content that will be passed to agents:

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

**YOU MUST USE THE TASK TOOL TO DISPATCH ALL 3 AGENTS IN PARALLEL (single message, multiple Task calls).**

### Agent 1: maintainability-reviewer

```
Task tool call:
- subagent_type: "general-purpose"
- description: "Maintainability review"
- prompt: |
    First invoke the code-foundations skill, then read agents/maintainability-reviewer.md for your review checklist.

    Review this diff for design quality. Focus on: complexity symptoms, shallow modules, information leakage, cohesion/coupling, parameters >7.

    GIT DIFF:
    [paste diff here]

    Return: VERDICT (EXCELLENT/GOOD/CONCERNING/POOR) with specific file:line references for any issues.
```

### Agent 2: error-handling-reviewer

```
Task tool call:
- subagent_type: "general-purpose"
- description: "Error handling review"
- prompt: |
    First invoke the code-foundations skill, then read agents/error-handling-reviewer.md for your review checklist.

    Review this diff for error handling issues. Focus on: empty catch blocks, silent failures, broad exception catching, missing error context.

    GIT DIFF:
    [paste diff here]

    Return: VERDICT (ROBUST/ADEQUATE/FRAGILE/BROKEN) with specific file:line references for any issues.
```

### Agent 3: correctness-reviewer

```
Task tool call:
- subagent_type: "general-purpose"
- description: "Correctness review"
- prompt: |
    First invoke the code-foundations skill, then read agents/correctness-reviewer.md for your review checklist.

    Review this diff for bugs. Focus on: boundary conditions, off-by-one errors, race conditions, resource leaks, null safety.

    GIT DIFF:
    [paste diff here]

    Return: VERDICT (VERIFIED/LIKELY CORRECT/UNCERTAIN/BUGGY) with specific file:line references for any issues.
```

---

## Phase 5: Aggregate Results

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

## MANDATORY STEPS (DO NOT SKIP)

1. **Invoke oberagent skill** - Validates agent dispatch
2. **Get diff content** - Content for agents to review
3. **Validate prompts** - Check against oberagent checklist
4. **Dispatch ALL 3 agents in parallel** - Use Task tool
5. **Aggregate results** - Combine into unified report

**DO NOT:**
- Skip oberagent invocation
- Skip agent dispatch and review code yourself
- Launch agents sequentially
- Omit skill invocation from agent prompts

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
