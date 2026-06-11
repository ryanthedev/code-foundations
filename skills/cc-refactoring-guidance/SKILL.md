---
name: cc-refactoring-guidance
description: "Guides safe refactoring using Code Complete's fix-first-then-refactor discipline: decides between refactor, rewrite, and fix-first; enforces separate commits; applies small-change rigor to high-error-rate one-liners."
disable-model-invocation: true
---

# Skill: cc-refactoring-guidance

## STOP - Refactoring Rules

- **Fix first, then refactor** - Never simultaneously (separate commits)
- **Small changes need MORE rigor, not less** - 1-line changes have HIGHEST error rate
- **>50% of changes fail first attempt** - Review and test even "trivial" changes

---

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

**Critical:** Each change has >50% first-attempt error rate regardless of prior results. Error rates are per change, not cumulative.

**Definitions:**
- **small** = ONE structural change (one rename, one extract, one inline). If you describe it with "and", it's not small.
- **review** = distinct person examining diff. Self-review does NOT satisfy this. AI review is acceptable but less effective.
- **working code** = all tests pass AND no known behavior bugs. Code that compiles but has failing tests is NOT working.
- **then** (as in "fix first, then refactor") = with COMMIT BOUNDARY between activities. Not same session, same commit.

---

## Pattern Reuse Gate

**BEFORE starting any refactoring, identify target patterns:**

| Search For | Why |
|------------|-----|
| Best examples of this pattern | What does "good" look like in this codebase? |
| Similar refactorings done before | How were they structured? |
| Module/directory conventions | What patterns dominate this area? |
| Recent improvements | What direction is the code evolving? |

**Questions to answer:**
1. What pattern am I refactoring TOWARD? (Not just away from bad code)
2. Does this target pattern exist elsewhere in the codebase?
3. Am I aligning with the codebase's direction, or fighting it?
4. Will this make surrounding code look inconsistent?

**If target pattern exists:** Match it exactly. Copy naming, structure, style.

**If no target pattern exists:** You're establishing one. Consider:
- Is this the right time to set a new precedent?
- Should you refactor MORE code to establish the pattern consistently?
- Document the new pattern for future reference.

**See:** [pattern-reuse-gate.md](${CLAUDE_PLUGIN_ROOT}/references/pattern-reuse-gate.md) for full gate protocol.

---

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

Combining fix and refactor in one change increases complexity and error likelihood. Split them.

#### When Prerequisites Are Missing

**No automated tests:**
1. Invoke `Skill(code-foundations:welc-legacy-code)` — follow the Legacy Code Change Algorithm
2. Write characterization tests first (capture current behavior, not intended behavior)
3. If impossible: document expected behavior, manual test script, increase review rigor
4. Minimum: at least one verification path must exist

**No version control:**
1. Create physical backup copy of files before starting
2. STRONGLY recommend: set up VCS first. This is almost always the right choice.

**No reviewer available:**
1. Perform systematic checklist-based self-review
2. Smaller changes, more commits, more testing to compensate

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

**Refactoring Sequencing (Fowler):**
- Move Field BEFORE Move Method (data first)
- Extract Method BEFORE Replace Temp with Query
- Self Encapsulate Field BEFORE Replace Data Value with Object
- Replace Constructor with Factory Method BEFORE Replace Type Code with Subclasses

**Recovery if Tests Fail After Refactoring:**
1. Don't debug extensively
2. Back out the change
3. Take a smaller step
4. Consider if you understood the code correctly

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

## Already Violated? Here's What To Do

If you mixed fix and refactor in one commit:
- **Before push:** `git reset --soft HEAD~1`, separate changes, re-commit properly. Takes ~15 minutes.
- **After push:** Document the violation, split in follow-up PR. Don't force-push shared branches.
- **Never:** Leave it because "it's already done."

If you skipped review on a small change:
- **Before merge:** Get the review now. It's not too late.
- **After merge:** Note it, move on, don't skip next time.

**Fixing violations post-commit is still worthwhile** — the cost of fixing now is less than the debugging cost of bugs they cause.

---

## Chain

| After | Next |
|-------|------|
| Refactoring complete | cc-control-flow-quality (CHECKER) |
| Structure changed | cc-routine-and-class-design (CHECKER) |
