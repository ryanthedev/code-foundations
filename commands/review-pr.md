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

    Return: VERDICT + file:line issues with Fix and Assessment [S:_ R:_ C:_ V:_]
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

    Return: VERDICT + file:line issues with Fix and Assessment [S:_ R:_ C:_ V:_]
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

    Return: VERDICT + file:line issues with Fix and Assessment [S:_ R:_ C:_ V:_]
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

    Return: VERDICT + file:line issues with Fix and Assessment [S:_ R:_ C:_ V:_]
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

    Return: VERDICT + file:line issues with Fix and Assessment [S:_ R:_ C:_ V:_]
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

## MANDATORY

1. Dispatch ALL 5 agents in parallel
2. **Group output by ACTION** (Fix / Investigate / Plan / Decide)
3. Provide code snippets for "Fix" items
4. Provide `/whiteboarding` topics for "Plan" items
5. State **Unknown** for Investigate/Decide items
