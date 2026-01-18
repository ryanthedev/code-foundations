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

Store the diff - pass it to each agent.

---

## Phase 3: Dispatch 5 Agents in Parallel

**USE TASK TOOL - ALL 5 AGENTS IN SINGLE MESSAGE**

### Agent 1: defensive-reviewer

```
Task tool:
- subagent_type: "general-purpose"
- description: "Defensive review"
- prompt: |
    First invoke code-foundations skill, then read agents/defensive-reviewer.md.

    Review for security AND error handling: input validation, injection, auth, catch blocks, silent failures.

    GIT DIFF:
    [paste diff]

    Return: VERDICT + file:line issues with Fix and Effort (🟢/🟡/🔴)
```

### Agent 2: quality-reviewer

```
Task tool:
- subagent_type: "general-purpose"
- description: "Quality review"
- prompt: |
    First invoke code-foundations skill, then read agents/quality-reviewer.md.

    Review for design AND readability: complexity, cohesion, naming, comments, style, trailing newlines.

    GIT DIFF:
    [paste diff]

    Return: VERDICT + file:line issues with Fix and Effort (🟢/🟡/🔴)
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

    GIT DIFF:
    [paste diff]

    Return: VERDICT + file:line issues with Fix and Effort (🟢/🟡/🔴)
```

### Agent 4: performance-reviewer

```
Task tool:
- subagent_type: "general-purpose"
- description: "Performance review"
- prompt: |
    First invoke code-foundations skill, then read agents/performance-reviewer.md.

    Review for performance: O(n²), I/O in loops, resource usage, hot paths.

    GIT DIFF:
    [paste diff]

    Return: VERDICT + file:line issues with Fix and Effort (🟢/🟡/🔴)
```

### Agent 5: documentation-reviewer

```
Task tool:
- subagent_type: "general-purpose"
- description: "Documentation review"
- prompt: |
    First invoke code-foundations skill, then read agents/documentation-reviewer.md.

    Review documentation: README accuracy, comment freshness, API docs, changelog.

    GIT DIFF:
    [paste diff]

    Return: VERDICT + file:line issues with Fix and Effort (🟢/🟡/🔴)
```

---

## Phase 4: Aggregate Results (GROUP BY FILE)

Combine findings **grouped by file**, not by dimension:

```markdown
# PR Review Report

## Summary
- **PR:** [title]
- **Branch:** [head] → [base]
- **Files Changed:** [count]
- **Agents:** defensive, quality, correctness, performance, documentation

## Verdict: [APPROVE / REQUEST CHANGES / BLOCKED]

---

## Issues by File

### src/middleware/FeatureHeader.cs

1. 🔴 [CRITICAL] Line 84 - Base64 memory amplification (defensive)
   Fix: Add max expansion check
   ```csharp
   if (encoded.Length > MaxDecodedSize / 1.34) return null;
   ```
   Effort: 🟢 Quick

2. 🟡 [IMPORTANT] Line 58 - Silent JSON failure (defensive)
   Fix: Add telemetry logging
   Effort: 🟢 Quick

3. 🟡 [IMPORTANT] Line 134 - Missing trailing newline (quality)
   Fix: Add newline at EOF
   Effort: 🟢 Quick

### src/services/FeatureToggle.cs

1. 🟡 [IMPORTANT] Line 45 - New public API undocumented (documentation)
   Fix: Add XML doc comment
   Effort: 🟢 Quick

---

## Positive Patterns
- [good things observed]

---

## Action Plan

| Priority | Count | Effort |
|----------|-------|--------|
| 🔴 Critical | [n] | [total] |
| 🟡 Important | [n] | [total] |
| 🟢 Suggestions | [n] | [total] |

1. Fix critical issues first
2. Address important issues
3. Re-run: `/review-pr` to verify
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

## MANDATORY

1. Dispatch ALL 5 agents in parallel
2. Group output by FILE, not dimension
3. Include effort estimates (🟢/🟡/🔴)
4. Include code fix snippets where possible
