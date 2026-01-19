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

Store the diff - pass it to each agent.

---

## Phase 3: Dispatch 3 Agents in Parallel

**USE TASK TOOL - ALL 3 AGENTS IN SINGLE MESSAGE**

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

    GIT DIFF:
    [paste diff]

    Return: VERDICT + file:line issues with Fix and Assessment [S:_ R:_ C:_ V:_]
```

---

## Phase 4: Aggregate Results (GROUP BY FILE)

```markdown
# Review Changes Report

## Scope
[files reviewed]

## Verdict: [READY / NEEDS WORK / BLOCKED]

---

## Issues by File

### [filename]

1. 🔴 [CRITICAL] Line X - [issue] (agent)
   Fix: [specific fix]
   Assessment: `[S:_ R:_ C:_ V:_]`
   **Unknown**: [what would change this assessment?]

2. 🟡 [IMPORTANT] Line Y - [issue] (agent)
   Fix: [suggestion]
   Assessment: `[S:_ R:_ C:_ V:_]`

---

## Action Plan

| Priority | Count | High Risk | Low Confidence | Needs Review |
|----------|-------|-----------|----------------|--------------|
| 🔴 Critical | [n] | [count R:H] | [count C:L] | [count V:R] |
| 🟡 Important | [n] | [count R:H] | [count C:L] | [count V:R] |
| 🟢 Suggestions | [n] | [count R:H] | [count C:L] | [count V:R] |

**Assessment Legend**: `[S:Scope R:Risk C:Confidence V:Verification]`
See `references/assessment-framework.md` for full definitions.

1. Fix critical issues (especially `R:H` high-risk)
2. Human review required for any `C:L` or `V:R` items
3. Re-run: `/review-changes`
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

## Phase 5: Debugging Guidance (Optional)

If correctness-reviewer reports CRITICAL bugs:

1. Suggest: "For systematic debugging, invoke cc-debugging skill"
2. Add to Action Plan:
   ```
   ## Debugging Resources
   For systematic investigation of bugs found above, consider:
   - `/skill cc-debugging` - Scientific debugging methodology
   ```

---

## Usage

```bash
/review-changes           # Unstaged changes
/review-changes --staged  # Staged only
/review-changes file.ts   # Specific files
```
