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

Combine findings **grouped by action type** (what to do next), then by file within each group.

See `references/assessment-framework.md` for action type definitions.

```markdown
# PR Review Report

## Summary
- **PR:** [title]
- **Branch:** [head] → [base]
- **Files Changed:** [count]
- **Agents:** defensive, quality, correctness, performance, documentation

## Verdict: [APPROVE / REQUEST CHANGES / BLOCKED]

---

## Fix Now
Ready-to-apply fixes with high confidence. Apply these in current session.

### src/middleware/FeatureHeader.cs

1. 🔴 [CRITICAL] Line 84 - Base64 memory amplification (defensive)
   ```csharp
   if (encoded.Length > MaxDecodedSize / 1.34) return null;
   ```
   Assessment: `[S:L R:H C:H V:T]`

2. 🟡 [IMPORTANT] Line 58 - Silent JSON failure (defensive)
   Fix: Add telemetry logging
   Assessment: `[S:L R:M C:H V:C]`

3. 🟡 [IMPORTANT] Line 134 - Missing trailing newline (quality)
   Fix: Add newline at EOF
   Assessment: `[S:L R:L C:H V:C]`

### src/services/FeatureToggle.cs

1. 🟡 [IMPORTANT] Line 45 - New public API undocumented (documentation)
   Fix: Add XML doc comment
   Assessment: `[S:L R:L C:H V:C]`

---

## Investigate
Low confidence or unclear root cause. Need more context before fixing.

### src/services/UserService.cs

1. 🟡 [IMPORTANT] Line 200 - Possible race condition (correctness)
   Assessment: `[S:B R:M C:L V:R]`
   Check: Is this method called concurrently? Check callers.
   **Unknown**: Thread safety requirements for this service.

---

## Plan
Systemic changes requiring dedicated planning session.

### src/api/*.cs (multiple files)

1. 🔴 [CRITICAL] Auth middleware missing from 5 endpoints (defensive)
   Assessment: `[S:S R:H C:H V:R]`
   Topic: "add consistent auth middleware to all API endpoints"
   → Invoke: `/whiteboarding "auth middleware pattern"`

---

## Decide
Trade-offs or business logic requiring human judgment.

### src/config/Settings.cs

1. 🟡 [IMPORTANT] Line 30 - Cache TTL seems too long (performance)
   Assessment: `[S:L R:M C:L V:R]`
   Options:
   - Option A: Reduce to 5 min - fresher data, more load
   - Option B: Keep 1 hour - stale data, less load
   **Unknown**: Acceptable staleness for this data?

---

## Positive Patterns
- [good things observed]

---

## Summary

| Action | Count | Breakdown |
|--------|-------|-----------|
| Fix Now | [n] | [n] critical, [n] important |
| Investigate | [n] | Need context before fixing |
| Plan | [n] | → `/whiteboarding` sessions |
| Decide | [n] | Needs human judgment |

**Next Steps:**
1. Apply "Fix Now" items in this session
2. Spin off "Investigate" as separate tasks
3. Run `/whiteboarding` for each "Plan" item
4. Discuss "Decide" items with stakeholders
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
2. **Group output by ACTION TYPE** (Fix Now / Investigate / Plan / Decide)
3. Within each action group, organize by file
4. Include 4-dimension assessment `[S:_ R:_ C:_ V:_]` for each issue
5. Provide code snippets ONLY for "Fix Now" items
6. Provide `/whiteboarding` topics for "Plan" items
7. State unknowns for Investigate/Decide items (epistemic humility)
