---
name: code-foundations
description: Use when doing ANY code task - writing, debugging, reviewing, fixing,
  implementing, optimizing, or refactoring. Symptoms that trigger this skill include
  seeing code, being asked to implement something, fix a bug, review code, or improve
  performance. This skill dispatches to specific skills based on task type.
---

## First Action

**Execute immediately:**
```bash
python3 ~/.claude/bin/log-skill-load.py code-foundations
```

# Code Foundations

## STOP - Classify Before Acting

**You MUST classify the task before ANY other action.**

Do NOT:
- Start analyzing the code
- Start writing a solution
- Say "Let me look at this"
- Skip to a specific skill you "already know" is right

**Classification is mandatory. No exceptions.**

### Task Classification

| User Intent Signals | Task Type | INVOKE NEXT |
|---------------------|-----------|-------------|
| "implement", "write", "build", "add", "create" | WRITE | cc-developer-character → cc-construction-prerequisites |
| "debug", "fix bug", "failing", "broken", "error" | DEBUG | cc-developer-character → cc-quality-practices |
| "review", "check", "audit", "evaluate quality" | REVIEW | cc-quality-practices (CHECKER mode) |
| "optimize", "slow", "performance", "faster" | OPTIMIZE | cc-performance-tuning |
| "refactor", "clean up", "improve structure" | REFACTOR | cc-developer-character → cc-refactoring-guidance |
| "secure", "vulnerability", "validate input" | SECURE | cc-defensive-programming (CHECKER mode) |

**After classifying:** State the task type, then INVOKE the indicated skill(s).

## cc-developer-character is NON-NEGOTIABLE

For WRITE, DEBUG, and REFACTOR tasks, you MUST invoke cc-developer-character FIRST.

**Why:** Baseline testing showed agents skip mindset checks and rationalize "I already know how to do this." The skill exists because knowing and doing are different.

**No exceptions for:**
- "Simple" tasks
- Tasks you've "done before"
- Time pressure
- Small codebases

## Red Flags - STOP If You Think This

These are the EXACT rationalizations observed in baseline testing. If you think any of these, you are about to violate the skill:

| If you think... | Reality |
|-----------------|---------|
| "I can already see the issue" | Seeing ≠ systematic verification. Load the skill anyway. |
| "This is simple enough / overkill" | Simple tasks have HIGHEST error rates (Weinberg 1983). |
| "Skills would add overhead/latency" | 30 seconds of checklist prevents 30 minutes of debugging. |
| "I already know how to do this" | Knowing ≠ executing checklist. Experts make errors too. |
| "Not worth loading for a 5-line function" | 5-line functions have bugs. Load the skill. |
| "I'll just fix it directly" | Direct fixes without process have >50% error rate (Yourdon). |

**All of these mean:** Load the skill anyway. Your confidence is the problem, not the solution.

## Crisis Minimum (Time Pressure)

Production down? Urgent fix needed? You STILL must:

1. **Classify the task** (5 seconds)
2. **State what you're skipping and why** (explicit, not implicit)
3. **After crisis:** Return within 24 hours to apply full skill chain

**What you may NOT skip even in crisis:**
- Input validation on external data
- Verifying fix actually works (not just "looks right")
- One sentence explaining WHY the fix works

**Baseline testing showed:** Under time pressure, agents skipped ALL skills and later admitted "skills would have prompted me to think about the actual problem." Crisis makes process MORE important, not less.

## Phase Skills (Chain After Classification)

| Task Type | Primary Skills | Follow-up Skills |
|-----------|----------------|------------------|
| WRITE | cc-construction-prerequisites → cc-pseudocode-programming | cc-routine-and-class-design (CHECKER), cc-defensive-programming (CHECKER) |
| DEBUG | cc-quality-practices (Scientific Method) | cc-refactoring-guidance (for the fix) |
| REVIEW | cc-quality-practices, cc-routine-and-class-design | cc-refactoring-guidance (if issues found) |
| OPTIMIZE | cc-performance-tuning | cc-refactoring-guidance (if structure degraded) |
| REFACTOR | cc-refactoring-guidance | cc-control-flow-quality (CHECKER), cc-routine-and-class-design (CHECKER) |
| SECURE | cc-defensive-programming | cc-data-organization (input validation) |

## Chain Completion

After completing primary skill work, invoke follow-up skills as CHECKER gates:

- **WRITE:** Before claiming "done", run cc-routine-and-class-design CHECKER and cc-defensive-programming CHECKER on your code
- **DEBUG:** After identifying fix, invoke cc-refactoring-guidance for safe fix process
- **REVIEW:** If violations found, invoke cc-refactoring-guidance for fix recommendations
- **OPTIMIZE:** After changes, verify with cc-control-flow-quality that structure wasn't degraded

**Do not claim task complete until CHECKER gates pass.**
