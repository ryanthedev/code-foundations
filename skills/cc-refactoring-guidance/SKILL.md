---
name: cc-refactoring-guidance
description: "Use when modifying existing code, improving code quality without changing behavior, or deciding between refactoring and rewriting. Symptoms: code smells, technical debt, just cleaning while I fix, small change treated casually, regression from trivial change, one-line change errors."
---

# Skill: cc-refactoring-guidance

## Metadata
Source: Code Complete 2nd Edition
Chapters:
  - Ch 24: Refactoring
Page Range: pp. 563-585
Key Point Anchor: "Evolution should improve the internal quality of the program."
Skill Type: APPLIER + TRANSFORMER
CC Foundation: maintainability, quality

## Overview
Guides safe refactoring decisions and execution following McConnell's empirically-grounded process. Implements Code Complete foundation: maintainability through behavior-preserving changes, quality through rigorous small-change discipline.

## Quick Reference

| Rule | Value | Source |
|------|-------|--------|
| Small change error rate | Peaks at 1-5 lines | Weinberg 1983 |
| First attempt success rate | <50% for any change | Yourdon 1986b |
| Review effect on 1-line changes | 55% -> 2% error rate | Freedman and Weinberg 1982 |
| Big refactoring | "Recipe for disaster" | Kent Beck |

**Key Principles:**
- Refactoring = behavior-preserving changes to WORKING code
- Fix first, then refactor (never simultaneously)
- Small changes need MORE rigor, not less
- Sometimes rewrite is better than big refactoring

**Critical:** Error rates are PER CHANGE, not per person. Your 10-change success streak does not reduce probability on change 11. Each change is an independent event with >50% first-attempt error rate.

**Definitions:**
- **small** = ONE structural change (one rename, one extract, one inline). If you describe it with "and", it's not small.
- **review** = distinct person examining diff. Self-review does NOT satisfy this. AI review is acceptable but less effective.
- **working code** = all tests pass AND no known behavior bugs. Code that compiles but has failing tests is NOT working.
- **then** (as in "fix first, then refactor") = with COMMIT BOUNDARY between activities. Not same session, same commit.

## Core Patterns

### Pattern 1: Mixing Fix and Refactor -> Separate Commits
```
// BEFORE: Mixing concerns [ANTI-PATTERN]
// "I'm just cleaning while I fix the bug"
- Modified broken code
- Added refactoring changes
- Single commit with mixed purposes

// AFTER: Separated activities
1. Fix the bug (verify working)
2. Commit fix
3. Refactor working code
4. Commit refactoring
```

### Pattern 2: Casual Small Change -> Rigorous Small Change
```
// BEFORE: Treating 1-line change casually [ANTI-PATTERN]
- Skip desk-check ("it's just one line")
- Skip review ("overkill for this")
- Skip testing ("obviously correct")

// AFTER: Small change rigor
- Desk-check even 1-line changes
- Get review (55% -> 2% error rate)
- Run regression tests
- Apply same rigor as large changes
```

### Pattern 3: Documenting Bad Code -> Rewriting It
```
// BEFORE: Adding comment to explain confusion [ANTI-PATTERN]
// Note: This calculates X by doing Y because of Z edge case
// which happens when A and B are both true and C is false
complicated_obscure_code();

// AFTER: Self-explanatory rewrite
clear_function_that_explains_itself();
```

## Modes

### APPLIER
Purpose: Guide refactoring decisions and safe refactoring process
Triggers:
  - "should I refactor or rewrite this?"
  - "how should I approach improving this code?"
  - "is this safe to refactor?"
Non-Triggers:
  - "fix this bug" -> Fix first, then come back for refactoring
  - "review this refactoring" -> Use code review skill
  - "check my code style" -> cc-control-flow-quality

#### Emergency Response (Production Down)
When production is down:
1. **Fix ONLY** - No refactoring. No cleanup. Just fix the bug.
2. **Deploy the fix** - Get production up.
3. **THEN refactor** - As separate activity when stable.

Emergency pressure doesn't change error statistics—it makes them WORSE due to stress. "Fix AND clean up" requests during outages: split them. Fix first, deploy, clean up later.

#### When Prerequisites Are Missing

**No automated tests:**
1. Write characterization tests first (capture current behavior)
2. If impossible: document expected behavior, manual test script, increase review rigor
3. Minimum: at least one verification path must exist

**No version control:**
1. Create physical backup copy of files before starting
2. STRONGLY recommend: set up VCS first. This is almost always the right choice.

**No reviewer available:**
1. Self-review with 24h delay (review your own changes after sleeping on it)
2. Rubber duck review (explain changes out loud, document the "conversation")
3. AI-assisted review (note: not equivalent to human review, but better than nothing)
4. Accept higher risk: smaller changes, more commits, more testing

#### Refactoring vs Rewriting Decision
```
1. Does code currently work?
   NO  -> This is FIXING, not refactoring. Fix first.
   YES -> Continue

2. Is the design fundamentally sound?
   NO  -> Consider REWRITING from scratch
   YES -> Continue

3. Would changes touch >30% of module?
   YES -> "Big refactoring" - consider rewrite
   NO  -> Proceed with incremental refactoring
```

#### Safe Refactoring Process (Priority Order)
1. **Save starting code** - Version control checkpoint
2. **Keep refactorings small** - One change at a time
3. **Make a list of steps** - Plan before executing
4. **Do one at a time** - Recompile and retest after each; STATE: "Tests pass after [change]"
5. **Use frequent checkpoints** - Commit working states
6. **Enable all compiler warnings** - Pickiest level
7. **Retest after each change** - Run tests, report results (not just "tests pass")
8. **Review changes** - Required even for 1-line changes
9. **Adjust for risk** - Extra caution for high-risk changes

Produces: Refactoring approach, step sequence, risk assessment
Constraints:
  - [p.565] Refactoring requires WORKING code as starting point
  - [p.571] Treat small changes as if they were complicated
  - [p.579] "A big refactoring is a recipe for disaster" - Beck

### TRANSFORMER
Purpose: Transform code smells into clean code
Triggers:
  - Code smell identified during review
  - "clean up this setup/takedown pattern"
  - "eliminate this tramp data"
Non-Triggers:
  - Behavior changes needed -> Fix first
  - New feature addition -> Not refactoring

Input -> Output:
  - Setup/takedown smell -> Encapsulated interface
  - Tramp data (passed just to pass again) -> Direct access or restructure
  - Duplicated code -> Extracted shared routine
  - Speculative "design ahead" code -> Remove it
Preserves: All observable behavior
Verification: Same tests pass before and after

## Red Flags - STOP If You Think:
- "This is too simple to test"
- "I've already verified this mentally"
- "One commit is cleaner than two"
- "This change is isolated, can't affect anything"
- "The tests pass, so I'm done"
- "This is an emergency, I can skip steps"
- "My last N changes all worked perfectly"
- "I already did it differently but it works"

**All of these mean:** You're rationalizing. Follow the full rigor anyway.

## Already Violated? Here's What To Do

If you mixed fix and refactor in one commit:
- **Before push:** `git reset --soft HEAD~1`, separate changes, re-commit properly. Takes ~15 minutes.
- **After push:** Document the violation, split in follow-up PR. Don't force-push shared branches.
- **Never:** Leave it because "it's already done."

If you skipped review on a small change:
- **Before merge:** Get the review now. It's not too late.
- **After merge:** Note it, move on, don't skip next time.

**"It's too late" is almost never true.** The discomfort of fixing violations is smaller than the debugging cost of bugs they cause.

## Rationalization Counters
| Excuse | Reality |
|--------|---------|
| "I'm just cleaning while I fix" | Fix first, then refactor. Separate commits. |
| "It's basically the same thing" | Refactoring = behavior-preserving. Fixing = behavior-changing. Different activities. |
| "It's just one line" | One-line changes have HIGHEST error rate. Apply full rigor. |
| "I don't need to test this" | >50% chance of error on first attempt at ANY change. |
| "Review would be overkill" | Reviews dropped 1-line change errors from 55% to 2%. |
| "I'll refactor it later" | Refactoring requires working code. Complete feature first, THEN refactor immediately. |
| "I can salvage this with refactoring" | Some code needs rewrite. Big refactoring is recipe for disaster. |
| "It'll save time to add this for later" | Speculative code usually wrong; slows current project. |
| "I already verified this manually" | Manual verification doesn't prevent >50% first-attempt error rate. Run automated tests. |
| "The tests pass, that's enough" | Tests verify behavior; review verifies the change itself. Both required. |
| "This change is isolated" | Even isolated 1-line changes have highest error rate. Isolation doesn't reduce rigor. |
| "It's an emergency" | Emergencies make errors MORE likely (stress). Fix only, deploy, refactor later. |
| "My last 5 changes worked" | Each change has INDEPENDENT >50% error rate. Past success doesn't reduce current odds. |
| "I already did it wrong but it works" | Working code doesn't validate process. Retroactively fix: soft-reset, separate, re-commit. |
| "No one's available to review" | Use 24h self-delay, rubber duck, or AI review. Something > nothing. |
| "We don't have tests" | Write characterization tests first, or document manual verification. Can't verify "behavior-preserving" blind. |

## Chain Decision (Execute After Refactoring Complete)

**This skill guides safe changes; CHECKER skills verify quality wasn't degraded.** After completing refactoring, INVOKE verification skills.

| Situation | INVOKE NEXT |
|-----------|-------------|
| Refactoring complete | cc-control-flow-quality (CHECKER) + cc-routine-and-class-design (CHECKER) |
| Bug fix applied | cc-quality-practices (verify fix, then SEARCH for similar) |
| Structure significantly changed | cc-data-organization (CHECKER) as well |

**Do NOT claim refactoring done without CHECKER gates.** Behavior-preserving changes can still degrade design quality. Verify.

**Both CHECKERs are mandatory for REFACTOR tasks:**
1. cc-control-flow-quality - verify nesting, complexity, loop structure
2. cc-routine-and-class-design - verify cohesion, coupling, abstraction levels

## Chaining
- Prerequisites: `cc-quality-practices` (Ch 21-23 defect fixing context)
- Follow-ons: `cc-control-flow-quality`, `cc-routine-and-class-design`
- Cross-refs: Ch 5 (design), Ch 21 (collaborative construction), Ch 22 (developer testing), Ch 23 (debugging)

## References
- Foundation: [cc-foundations.md](../../references/cc-foundations.md)
- Checklist: [checklists.md](./checklists.md)
- Evidence: [hard-data.md](./hard-data.md)
