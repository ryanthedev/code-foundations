---
name: building
description: "Execute whiteboard plans with checklist-based tracking. Use after /whiteboarding to implement saved plans. Triggers on: build it, execute plan, implement the whiteboard, run the plan. Loads plan from docs/plans/, tracks progress, produces working code with tests."
---

# Skill: building

**Load Plan → Checklist → Execute → Verify → Report**

---

## Quick Reference

| Phase | Goal | Output |
|-------|------|--------|
| LOAD | Read plan file | Parsed implementation checklist |
| SETUP | Initialize tracking | TodoWrite populated |
| EXECUTE | Implement each section | Working code |
| VERIFY | Run tests, confirm completion | All tests pass |
| REPORT | Update plan, summarize | Execution log |

---

## Crisis Invariants - NEVER SKIP

| Check | Why Non-Negotiable |
|-------|-------------------|
| **Feature branch required** | Multi-phase commits on main = no rollback, polluted history |
| **Load plan before coding** | No plan = no checklist = forgotten tasks |
| **One section at a time** | Parallel sections = merge conflicts + lost context |
| **PRE-GATE before implementation** | No pseudocode = coding without design = rework |
| **POST-GATE before checkpoint** | No verification = bugs escape to next phase |
| **Reviewer agent per phase** | Self-review is blind; fresh agent catches issues |
| **Mark complete only when gates pass** | Premature completion = unverified work shipped |
| **Update execution log** | Log enables debugging failed builds |

---

## Phase 1: LOAD (Read Plan File)

### Branch Gate (MANDATORY - First Check)

**Before anything else, verify branch status:**

```bash
git branch --show-current
git status
```

| Current Branch | Action |
|----------------|--------|
| `main` or `master` | **STOP.** Create feature branch first. |
| Feature branch, clean | Proceed |
| Feature branch, dirty | Ask: "Uncommitted changes. Stash, commit, or abort?" |

**If on main/master:**
```
You're on [main]. Building requires a feature branch for safe multi-phase commits.

Create branch now?
- [ ] Yes, create: feature/<plan-topic>
- [ ] Yes, create: <custom-name>
- [ ] No, abort building
```

```bash
git checkout -b feature/<plan-topic>
```

**This gate is NON-NEGOTIABLE.** Do not proceed on main/master under any circumstances.

---

### Locate Plan

If plan path provided:
```bash
cat docs/plans/<provided-path>.md
```

If no path, list available:
```bash
ls -la docs/plans/*.md | head -20
```

Ask user: "Which plan should I execute?"

### Parse Plan Structure

Extract from plan file:
1. **Context** - What we're building
2. **Approach** - How we're building it
3. **Phases** - Implementation sections
4. **Test Plan** - Verification criteria

### Verify Plan is Ready

Check plan status:
- `Status: ready` → Proceed
- `Status: in-progress` → Resume from last checkpoint
- `Status: complete` → Ask: "Plan already complete. Re-execute or archive?"
- `Status: blocked` → Show blockers, ask how to proceed

---

## Phase 2: SETUP (Initialize Tracking)

### Convert Plan to TodoWrite

Transform each plan phase into todos:

```
Plan Phase 1: Database Schema
- [ ] Create migration file
- [ ] Define User table
- [ ] Define Session table

↓ Becomes ↓

TodoWrite([
  {content: "Create migration file", status: "pending", activeForm: "Creating migration file"},
  {content: "Define User table", status: "pending", activeForm: "Defining User table"},
  {content: "Define Session table", status: "pending", activeForm: "Defining Session table"}
])
```

### Update Plan Status

```markdown
**Status:** in-progress
**Started:** YYYY-MM-DD HH:MM
**Current Phase:** 1
```

---

## Phase 3: EXECUTE (Implement Sections)

### CRITICAL: DO NOT IMPLEMENT DIRECTLY

**You MUST dispatch subagents for implementation. DO NOT:**
- Edit code files directly during building
- Skip PRE-GATE pseudocode
- Skip POST-GATE reviewer agent
- Proceed after reviewer returns FAIL

**The gates are BLOCKING, not advisory.**

### Execution Loop - Gated

For each phase, execute this **mandatory** sequence:

```
┌──────────────────────────────────────────────────────────┐
│  PRE-GATE (BLOCKS IMPLEMENTATION)                        │
│  ├─ Skill(cc-pseudocode-programming) → pseudocode        │
│  ├─ Skill(aposd-designing-deep-modules) → design review  │
│  └─ CONFIRM: Pseudocode exists? Design passed?           │
│                                                          │
│  ⛔ STOP: Cannot proceed until PRE-GATE checklist TRUE   │
├──────────────────────────────────────────────────────────┤
│  IMPLEMENT (via subagent - DO NOT code directly)         │
│  ├─ Task tool → dispatch implementation subagent         │
│  ├─ Wait for subagent DONE                               │
│  └─ Run tests to verify                                  │
├──────────────────────────────────────────────────────────┤
│  POST-GATE (BLOCKS CHECKPOINT)                           │
│  ├─ Skill(aposd-verifying-correctness)                   │
│  ├─ Skill(cc-defensive-programming)                      │
│  ├─ Task tool → dispatch reviewer agent                  │
│  └─ Wait for PASS                                        │
│                                                          │
│  ⛔ STOP: Cannot proceed until reviewer returns PASS     │
├──────────────────────────────────────────────────────────┤
│  CHECKPOINT (Only after PASS)                            │
│  ├─ Commit with phase summary                            │
│  └─ Update execution log                                 │
└──────────────────────────────────────────────────────────┘
```

---

### PRE-GATE (MANDATORY - BLOCKS IMPLEMENTATION)

## STOP. YOU CANNOT WRITE CODE UNTIL THIS GATE PASSES.

**Before writing ANY code for a phase, complete this checklist:**

- [ ] Pseudocode written via `cc-pseudocode-programming`
- [ ] Design reviewed via `aposd-designing-deep-modules` (if new modules)
- [ ] PRE-GATE checklist saved to execution log

**Step 1: Write Pseudocode**

```
Skill(code-foundations:cc-pseudocode-programming)
```

Provide the skill with:
- Phase description from plan
- Files to be created/modified
- Expected behavior

**DO NOT PROCEED** until pseudocode output is captured.

**Step 2: Design Review** (if phase creates new modules/classes)

```
Skill(code-foundations:aposd-designing-deep-modules)
```

Verify:
- Interface is simpler than implementation
- Information hiding applied
- "Design it twice" principle considered

**PRE-GATE CHECKLIST (Must be TRUE before IMPLEMENT):**

| Check | Status |
|-------|--------|
| Pseudocode exists for this phase | [ ] |
| Pseudocode covers all tasks in phase | [ ] |
| Design review passed (if applicable) | [ ] |

**If any check is FALSE, you CANNOT proceed to IMPLEMENT.**

---

### IMPLEMENT (ONLY AFTER PRE-GATE PASSES)

## STOP. Confirm PRE-GATE passed before proceeding.

**Dispatch implementation subagent** - DO NOT implement directly:

```
Task tool:
- subagent_type: "general-purpose"
- description: "Implement Phase N"
- prompt: |
    You are implementing Phase N of a building plan.

    INVOKE code-foundations skill first.

    ## Pseudocode to Implement
    [paste pseudocode from PRE-GATE]

    ## Files to Create/Modify
    [list from plan]

    ## Tasks
    [task list from plan phase]

    ## Requirements
    1. Translate pseudocode to code exactly
    2. Run tests after each file change
    3. Return: DONE with files changed, or BLOCKED with issue

    DO NOT add features not in pseudocode.
    DO NOT refactor unrelated code.
```

**Wait for subagent to complete before proceeding.**

**After subagent returns:**

1. Verify subagent returned DONE (not BLOCKED)
2. Run tests to confirm implementation works
3. If BLOCKED, debug and re-dispatch or escalate

**During implementation, subagent should invoke:**

| Situation | Skill |
|-----------|-------|
| Error handling code | `Skill(code-foundations:cc-defensive-programming)` |
| Complex control flow | `Skill(code-foundations:cc-control-flow-quality)` |
| Data structures | `Skill(code-foundations:cc-data-organization)` |

---

### POST-GATE (MANDATORY - BLOCKS CHECKPOINT)

## STOP. YOU CANNOT COMMIT UNTIL THIS GATE PASSES.

**Before marking phase complete, ALL of these must pass:**

- [ ] Verification via `aposd-verifying-correctness`
- [ ] Defensive check via `cc-defensive-programming`
- [ ] Reviewer agent returns PASS

**Step 1: Verification**

```
Skill(code-foundations:aposd-verifying-correctness)
```

Check:
- Requirements: Each requirement mapped to code?
- Concurrency: Shared state protected?
- Errors: All failure points handled?
- Resources: All acquired resources released?
- Boundaries: Edge cases handled?

**Step 2: Defensive Programming Check**

```
Skill(code-foundations:cc-defensive-programming)
```

Check:
- External input validated?
- No empty catch blocks?
- Error handling consistent?

**Step 3: Dispatch Phase Reviewer Agent (MANDATORY)**

```
Task tool:
- subagent_type: "general-purpose"
- description: "Phase N review"
- prompt: |
    You are reviewing Phase N of a building plan.

    INVOKE code-foundations skill first.

    ## Files Changed This Phase
    [list files from implementation subagent]

    ## Plan Requirements
    [paste phase requirements from plan]

    ## Review Checklist
    1. Does implementation match plan exactly?
    2. Any bugs, security issues, or missing error handling?
    3. Code quality issues?
    4. Tests cover the implementation?

    ## Output Format
    Return EXACTLY one of:
    - PASS: [brief summary]
    - FAIL: [specific issues that must be fixed]

    Be strict. If anything is wrong, return FAIL.
```

**WAIT for reviewer agent response.**

**POST-GATE CHECKLIST (Must ALL be TRUE before CHECKPOINT):**

| Check | Status |
|-------|--------|
| Verification skill passed | [ ] |
| Defensive programming check passed | [ ] |
| Reviewer agent returned PASS | [ ] |
| All tests pass | [ ] |

**If reviewer returns FAIL:**
1. Fix the issues identified
2. Re-run tests
3. Re-dispatch reviewer agent
4. Repeat until PASS

**You CANNOT proceed to CHECKPOINT until reviewer returns PASS.**

---

### CHECKPOINT (Only After Gates Pass)

```bash
git add .
git commit -m "Phase N: [name]

- [summary of what was implemented]
- PRE-GATE: pseudocode reviewed
- POST-GATE: verification passed, reviewer approved

Co-Authored-By: Claude Code <noreply@anthropic.com>"
```

Update plan file execution log:
```markdown
### Phase N: [Name]
- [x] PRE-GATE: Pseudocode complete
- [x] Task 1 - Completed
- [x] Task 2 - Completed
- [x] POST-GATE: Verification passed
- [x] POST-GATE: Reviewer approved
Commit: [hash]
```

**State:** "Phase N complete. All gates passed. Proceeding to Phase N+1."

---

### Gate Failure Protocol

If any gate fails:

| Gate | Failure | Action |
|------|---------|--------|
| PRE-GATE | Pseudocode unclear | Refine pseudocode, re-run gate |
| PRE-GATE | Design issues | Redesign, re-run gate |
| POST-GATE | Verification fails | Fix code, re-run POST-GATE |
| POST-GATE | Reviewer finds issues | Fix issues, re-run reviewer |

**You CANNOT proceed to next phase until current phase passes all gates.**

---

## Phase 4: VERIFY (Full Test Suite)

### Pre-Completion Checks

- [ ] All plan phases marked complete
- [ ] All tests pass (unit + integration)
- [ ] No skipped tasks
- [ ] Code compiles without warnings

### Run Test Plan

Execute each item from plan's Test Plan section:

```bash
# Unit tests
npm test  # or equivalent

# Integration tests (if specified)
npm run test:integration

# Manual verification (prompt user)
```

### Verification Gate

| Condition | Action |
|-----------|--------|
| All tests pass | Proceed to REPORT |
| Tests fail | Debug, fix, re-verify |
| Tests missing | Write tests, then re-verify |

---

## Phase 5: REPORT (Update Plan + Summarize)

### Update Plan File

```markdown
**Status:** complete
**Completed:** YYYY-MM-DD HH:MM
**Duration:** [time from start to complete]

---

## Execution Log

### Phase 1: [Name]
- [x] Task 1 - Completed YYYY-MM-DD HH:MM
- [x] Task 2 - Completed YYYY-MM-DD HH:MM
Commit: [hash]
Notes: [any issues encountered]

### Phase 2: [Name]
...
```

### Summary Output

```markdown
# Build Complete

**Plan:** [plan name]
**Phases Completed:** N/N
**Tests:** All passing

## What Was Built
- [summary of implemented features]

## Files Changed
- `path/to/file.ts` - [what changed]
- ...

## Commits
- [hash] Phase 1: [name]
- [hash] Phase 2: [name]
- ...

## Next Steps
- [any follow-up tasks identified]
- [documentation to update]
```

---

## Error Handling

### Build Failure Protocol

If implementation fails:

1. **Stop immediately** - Don't proceed to next task
2. **Document failure** in execution log:
   ```markdown
   ### Phase N: [Name]
   - [x] Task 1 - Complete
   - [ ] Task 2 - **FAILED**
     Error: [description]
     Attempted: [what was tried]
   ```
3. **Update plan status:** `Status: blocked`
4. **Ask user:**
   - "Task failed. Options: (A) Debug now, (B) Skip and continue, (C) Pause build"

### Resume Protocol

When resuming blocked plan:

1. Read execution log
2. Find last successful checkpoint
3. Show: "Resuming from Phase N, Task M. Last failure: [description]"
4. Ask: "Ready to retry, or should we discuss the blocker first?"

---

## Anti-Rationalization Table

| Rationalization | Reality |
|-----------------|---------|
| "I'll mark it complete and fix later" | Incomplete = incomplete. Fix now or don't mark done. |
| "Tests are slow, skip for now" | Untested code = unknown bugs shipped |
| "This task is done enough" | Either done or not done. No partial credit. |
| "I'll commit all phases at once" | Per-phase commits enable rollback |
| "The plan is outdated, I'll improvise" | Update the plan, don't abandon it |
| "User said ship it, skip verification" | Broken code shipped = worse than delay |
| "I remember what the plan said" | Read the plan file. Memory is unreliable. |
| "This extra feature fits naturally" | Not in plan = not in this build. Add to backlog. |
| "PRE-GATE is overkill for simple code" | Simple code has highest error rates. PRE-GATE catches design issues before they're coded. |
| "I can review my own code" | Self-review is blind to your own assumptions. Dispatch reviewer agent. |
| "POST-GATE is slowing me down" | POST-GATE catches issues BEFORE they propagate. Fix now = faster than fix later. |
| "Reviewer agent is redundant" | You implemented the code; reviewer agent has fresh perspective. Different context = different bugs caught. |
| "Gates passed last phase, skip this one" | Each phase is independent. Past gates don't predict current quality. |
| "I'll just commit to main, it's faster" | Multi-phase builds on main = no rollback. Feature branch is mandatory. |
| "It's a small change, main is fine" | Small changes grow. Branch now or regret later. |
| "I can implement faster than dispatching" | Direct implementation skips quality gates. Subagent ensures fresh context. |
| "Pseudocode is overkill, I know what to do" | You know NOW. The subagent doesn't. Pseudocode is the contract. |
| "The subagent will figure it out" | Subagent needs explicit pseudocode. No pseudocode = garbage implementation. |

---

## Pressure Testing Scenarios

### Scenario 1: Plan and Reality Diverge

**Situation:** During implementation, you discover the plan is wrong or incomplete.

**Response:**
1. Stop current task
2. Update plan file with discovery
3. Ask user: "Plan says X, but I found Y. Should I: (A) Update plan and continue, (B) Continue with current plan, (C) Pause for re-planning?"

### Scenario 2: Tests Fail After Implementation

**Situation:** Code is written, but tests fail.

**Response:**
1. Do NOT mark phase complete
2. Debug test failure
3. Fix code (not tests, unless tests are wrong)
4. Re-run tests
5. Only proceed when tests pass

### Scenario 3: Scope Creep

**Situation:** You see an opportunity to add a "quick improvement" not in the plan.

**Response:** "I noticed [opportunity]. This isn't in the current plan. Should I:
- Add to this plan (extends timeline)
- Add to backlog (future work)
- Skip entirely"

---

## Integration with /whiteboarding

### Expected Flow

```
/whiteboarding "user story"
  ↓
[Socratic questions]
[2-3 approaches]
[Detailed sections]
[Save to docs/plans/YYYY-MM-DD-topic.md]
  ↓
[Optional: Refresh context window]
  ↓
/building docs/plans/YYYY-MM-DD-topic.md
  ↓
[Checklist execution]
[Tests pass]
[Summary report]
```

### Context Refresh Benefits

Starting fresh session before /building:
- Full context window for implementation
- No planning discussion cluttering context
- Plan file contains all necessary information

---

## Chaining

- **RECEIVES FROM:** whiteboarding (via plan file), user with plan path
- **CHAINS TO:** code-foundations skills during execution
- **RELATED:** oberexec, aposd-verifying-correctness, cc-quality-practices
