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

### Ambiguous Requests

When the task type is unclear (e.g., "take a look at this code"):

1. **Load code-foundations FIRST** (you already did - you're reading this)
2. **Then ask clarifying questions** - "Are you looking for a review, debugging help, or something else?"
3. **After clarification, classify and continue the chain**

**WRONG order:** Ask questions → then load skills
**RIGHT order:** Load code-foundations → ask questions → classify → invoke chain

The skill comes BEFORE clarification because the skill tells you HOW to clarify.

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
| "This is genuinely trivial" | **NEW:** You don't get to decide triviality. Load the skill. It decides. |
| "The CRITICAL language is aspirational" | **NEW:** It's literal. "ANY code activity" means ANY. No interpretation. |
| "I'm following the spirit without the letter" | **NEW:** Violating the letter IS violating the spirit. Load the skill. |
| "Loading skills for this is cargo culting" | **NEW:** Process exists for edge cases you can't predict. Load anyway. |
| "I've done this exact thing 1000 times" | **NEW:** Expertise creates blind spots. The 1001st time can fail. |
| "The code already works / is battle-tested" | **NEW:** Your CHANGE can break what worked. 2 years of success doesn't protect today's edit. |
| "Skills are for new/broken code, not working code" | **NEW:** You're MODIFYING it. The modification is new code. Load the skill. |
| "Production validates correctness" | **NEW:** Production validates PAST code. Your change is FUTURE code. Load the skill. |
| "It's config, not code" | **NEW:** Config that affects runtime behavior IS code activity. Feature flags, deps, env vars need verification. |
| "Dependency version bump is just a number" | **NEW:** Version changes can introduce breaking changes, security patches, or behavior changes. Review it. |

**All of these mean:** Load the skill anyway. Your confidence is the problem, not the solution.

**The "Trivial Task" Trap (Observed in Testing):**
Agents rationalized skipping skills for "trivial" tasks like getters and variable renames. They said:
- "The task is genuinely trivial"
- "The 'CRITICAL' language is aspirational, not practical"
- "Loading skills for every keystroke would be cargo-culting"

These are the EXACT thoughts that precede bugs. A 2-line getter can have bugs. A variable rename can break tests. **You are not the judge of triviality - the skill is.**

**The "Working Code" Trap (Observed in Testing):**
Agents rationalized skipping skills when modifying production code. They said:
- "The code has empirical validation - two years of production use"
- "Working production code has already passed the ultimate review: reality"
- "Skills are for NEW code or BROKEN code. This is neither."

**These rationalizations are dangerous because they're half-true.** Yes, the EXISTING code works. But you're not evaluating the existing code - you're ADDING to it. Your addition is new code. The 2 years of production success doesn't validate your new logging statement, your new parameter, your new error handler. **Every modification is new code that needs the skill chain.**

**The "It's Just Config" Trap (Observed in Testing):**
Agents rationalized skipping skills for configuration file changes. They said:
- "It's a configuration file, not code"
- "A version bump is just changing a number"
- "Environment variables are data entry, not programming"

**Configuration that affects runtime behavior IS a code activity:**
- **Feature flags** enable/disable code paths - wrong value = production bug
- **Dependency versions** can introduce breaking changes or security issues
- **Environment variables** control database connections, API endpoints, secrets
- **Build configs** affect what code gets compiled/bundled

If a configuration change can cause your application to behave differently, it needs the same verification as a code change. At minimum, verify: What behavior changes? What could break? How will you test?

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
