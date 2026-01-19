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
   Assessment: `[S:L R:H C:H V:T]` - Localized fix, high risk (DoS), high confidence, needs test
   **Unknown**: What's the expected max input size in production?

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

## Positive Patterns
- [good things observed]

---

## Action Plan

| Priority | Count | High Risk | Low Confidence | Needs Review |
|----------|-------|-----------|----------------|--------------|
| 🔴 Critical | [n] | [count R:H] | [count C:L] | [count V:R] |
| 🟡 Important | [n] | [count R:H] | [count C:L] | [count V:R] |
| 🟢 Suggestions | [n] | [count R:H] | [count C:L] | [count V:R] |

**Assessment Legend**: `[S:Scope R:Risk C:Confidence V:Verification]`
- Scope: L=Localized, B=Bounded, S=Systemic
- Risk: L=Low, M=Medium, H=High
- Confidence: L=Low (speculative), M=Medium, H=High (pattern-matched)
- Verification: C=Compile, T=Test, R=Review (human required)

1. Fix critical issues first (especially `R:H` high-risk)
2. Human review required for any `C:L` or `V:R` items
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
3. Include 4-dimension assessment `[S:_ R:_ C:_ V:_]` for each issue
4. Include code fix snippets where possible
5. State unknowns for critical issues (epistemic humility)
6. Flag any `C:L` (low confidence) items for human review
