---
description: "Execute plans through gated phases with subagent dispatch."
---

# Skill: building

**Load Plan → Setup → Execute → Verify → Report**

---

## Quick Reference

| Phase | Goal | Output |
|-------|------|--------|
| LOAD | Read plan file | Parsed implementation checklist |
| SETUP | Initialize tracking | Plan status updated |
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
| **TaskCreate sub-phases** | Prompt-only enforcement gets skipped. blockedBy chains cannot be skipped. |

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
4. **Test Coverage** - What level of tests required (100%, backend only, etc.)
5. **Test Plan** - Specific verification criteria
6. **Model overrides** - Optional `**Model:** <model>` per phase

**If Test Coverage is missing:** Default to "100% coverage" and inform user.

### Verify Plan is Ready

Check plan status:
- `Status: ready` → Proceed
- `Status: in-progress` → Resume from last checkpoint
- `Status: complete` → Ask: "Plan already complete. Re-execute or archive?"
- `Status: blocked` → Show blockers, ask how to proceed

---

## Phase 2: SETUP (Initialize Tracking)

### Update Plan Status

```markdown
**Status:** in-progress
**Started:** YYYY-MM-DD HH:MM
**Current Phase:** 1
```

### Create ALL Sub-Phase Tasks Upfront

**DO NOT create phase-level tasks like "Phase 1: [Name]". DO NOT use TodoWrite.**

Create the 4 sub-phase tasks for EVERY phase in the plan NOW, before executing anything.

For each phase N, run Model Auto-Detection (see below), then create:

1. `TaskCreate(subject: "Phase N.1: PRE-GATE - [phase name]", description: "Discovery + pseudocode via pre-gate-agent. Model: [resolved_model].", activeForm: "Running pre-gate for Phase N")`
2. `TaskCreate(subject: "Phase N.2: IMPLEMENT - [phase name]", description: "Implement from pseudocode. Model: [resolved_model].", activeForm: "Implementing Phase N")`
3. `TaskCreate(subject: "Phase N.3: POST-GATE - [phase name]", description: "Review implementation. Model: [resolved_model]. Must return PASS.", activeForm: "Running post-gate for Phase N")`
4. `TaskCreate(subject: "Phase N.4: CHECKPOINT - [phase name]", description: "Commit after all gates pass.", activeForm: "Committing Phase N")`

**Then chain ALL dependencies:**
- Within each phase: N.2 blockedBy N.1, N.3 blockedBy N.2, N.4 blockedBy N.3
- **Between phases:** Phase (N+1).1 blockedBy Phase N.4

Example for a 2-phase plan (8 tasks total):
```
Phase 1.1: PRE-GATE        → no blockedBy
Phase 1.2: IMPLEMENT       → blockedBy: [1.1]
Phase 1.3: POST-GATE       → blockedBy: [1.2]
Phase 1.4: CHECKPOINT      → blockedBy: [1.3]
Phase 2.1: PRE-GATE        → blockedBy: [1.4]  ← chains to previous phase
Phase 2.2: IMPLEMENT       → blockedBy: [2.1]
Phase 2.3: POST-GATE       → blockedBy: [2.2]
Phase 2.4: CHECKPOINT      → blockedBy: [2.3]
```

**The user sees the full pipeline immediately.**

---

## Phase 3: EXECUTE (Implement Sections)

### CRITICAL: DO NOT DO ANYTHING DIRECTLY

**You MUST dispatch subagents for ALL work. DO NOT:**
- Read/explore code files directly during building
- Edit code files directly during building
- Skip any sub-phase task
- Proceed when a blockedBy dependency is not completed
- Mark a gate task completed when it returned FAIL
- Create phase-level tasks (NO "Phase 1: [Name]" tasks)

**The ONLY tasks you create are the 4 sub-phase tasks per phase (PRE-GATE, IMPLEMENT, POST-GATE, CHECKPOINT).**

---

### Mandatory Skill Loading Per Sub-Phase

Each sub-phase dispatches a specific agent type with specific skills. **Do NOT paraphrase the prompts below. Include the skill loading instructions VERBATIM.**

| Sub-Phase | Agent Type | Skills (baked into agent template) |
|-----------|-----------|-------------------------------|
| N.1 PRE-GATE | `code-foundations:pre-gate-agent` | `cc-construction-prerequisites`, `cc-pseudocode-programming`, `aposd-designing-deep-modules`, `cc-routine-and-class-design` |
| N.2 IMPLEMENT | `code-foundations:implementation-agent` | `cc-control-flow-quality`, `cc-data-organization`, `aposd-improving-code-clarity`, `aposd-simplifying-complexity` |
| N.3 POST-GATE | `code-foundations:post-gate-agent` | `aposd-verifying-correctness`, `cc-quality-practices`, `aposd-reviewing-module-design`, `cc-defensive-programming` |
| N.4 CHECKPOINT | None (you do this) | N/A |

**POST-GATE uses `code-foundations:post-gate-agent`.** Skills are baked into the agent template — no skill loading needed in the dispatch prompt.

---

### Model Auto-Detection

Before creating sub-phase tasks for a phase, determine the model for PRE-GATE, IMPLEMENT, and POST-GATE agents.

**Resolution order** (first match wins):

1. **Plan override:** If phase has a `**Model:** <model>` line below the heading, use that model for all three agents.
2. **Auto-detect** from phase signals:

```
Parse the phase section from the plan:
  task_count  = number of bullet tasks (- [ ] lines)
  file_count  = number of unique file paths mentioned
  phase_text  = lowercase phase heading + all task text

OPUS_KEYWORDS  = [refactor, architect, migrate, redesign, rewrite, overhaul]
HAIKU_KEYWORDS = [config, rename, typo, bump, cleanup, delete, remove]

If task_count <= 2 AND file_count <= 2
   AND no OPUS_KEYWORDS in phase_text:
  → haiku

If task_count >= 6 OR file_count >= 6
   OR any OPUS_KEYWORD in phase_text:
  → opus

Otherwise:
  → sonnet
```

**State the resolved model when creating tasks:**
"Phase N model: [model] (reason: [auto: N tasks, M files] or [plan override])"

---

### Execution Loop - Enforced via TaskCreate

All sub-phase tasks were created in SETUP. Now execute them in order.

#### Execute Each Sub-Phase

For each sub-phase task in order:

```
1. TaskGet(task_id) → verify blockedBy list is empty (all predecessors completed)
2. TaskUpdate(task_id, status: "in_progress")
3. Dispatch subagent (see templates below)
4. Wait for completion
5. If gate task (PRE-GATE or POST-GATE) and result is FAIL:
   → Do NOT mark completed
   → Follow Gate Failure Protocol
6. If success:
   → TaskUpdate(task_id, status: "completed")
7. Proceed to next sub-phase
```

**All 4 completed → proceed to Phase N+1.**

---

### Sub-Phase N.1: PRE-GATE (Discovery + Pseudocode)

## STOP. YOU CANNOT EXPLORE CODE OR WRITE PSEUDOCODE DIRECTLY.

**TaskUpdate → in_progress, then dispatch the pre-gate agent.**

The pre-gate agent combines discovery (what exists) and design (what to build) into one step. Skills are baked into the agent template - no need to include skill loading in your prompt.

```
Agent tool:
- subagent_type: "code-foundations:pre-gate-agent"
- model: [resolved_model]
- description: "PRE-GATE for Phase N"
- prompt: |
    Run PRE-GATE for Phase N of the building plan.

    ## Phase N: [name]
    [paste phase description and file list from plan]

    ## Inputs
    - Plan file: docs/plans/<plan-name>.md
    - Phase: N - [name]

    ## Output Files
    - Discovery: docs/building/<plan-name>-phase-N-discovery.md
    - Pseudocode: docs/building/<plan-name>-phase-N-pseudocode.md
```

**After PRE-GATE returns:**
1. Check status: DONE, SKIP, or UPDATE_PLAN
2. If SKIP → mark remaining sub-phase tasks as completed, proceed to next phase
3. If UPDATE_PLAN → pause and ask user
4. If DONE → verify pseudocode file exists and covers all tasks
5. If incomplete → do NOT mark completed → re-dispatch
6. If complete → TaskUpdate → completed

---

### Sub-Phase N.2: IMPLEMENT

## STOP. Verify PRE-GATE task is completed before proceeding.

**TaskGet → confirm blockedBy is empty. TaskUpdate → in_progress, then dispatch:**

```
Agent tool:
- subagent_type: "code-foundations:implementation-agent"
- model: [resolved_model]
- description: "Implement Phase N"
- prompt: |
    Implement Phase N of the building plan.

    ## Input Files (READ THESE FIRST)
    - Discovery: docs/building/<plan-name>-phase-N-discovery.md
    - Pseudocode: docs/building/<plan-name>-phase-N-pseudocode.md
    - Plan: docs/plans/<plan-name>.md (Phase N section)

    ## Your Tasks
    1. Read the discovery file - understand current state
    2. Read the pseudocode file - this is your implementation spec
    3. Implement exactly what the pseudocode specifies
    4. Run tests after each file change

    Return: DONE with files changed, or BLOCKED with issue.
```

**Why file-based handoff:**
- Main context stays clean (no pseudocode bloat)
- Implementation agent has full context via files
- Artifacts are persistent and reviewable
- Enables resume if interrupted

**After subagent returns:**
1. Verify subagent returned DONE (not BLOCKED)
2. Run tests to confirm implementation works
3. If BLOCKED → do NOT mark completed → debug and re-dispatch or escalate
4. If DONE → TaskUpdate → completed

---

### Sub-Phase N.3: POST-GATE

## STOP. Verify IMPLEMENT task is completed before proceeding.

**TaskGet → confirm blockedBy is empty. TaskUpdate → in_progress, then dispatch.**

**Always use `code-foundations:post-gate-agent`.** Skills are baked into the agent template.

```
Agent tool:
- subagent_type: "code-foundations:post-gate-agent"
- model: [resolved_model]
- description: "POST-GATE for Phase N"
- prompt: |
    Review Phase N implementation.

    ## Inputs
    - Plan: docs/plans/<plan-name>.md (Phase N section)
    - Discovery: docs/building/<plan-name>-phase-N-discovery.md
    - Pseudocode: docs/building/<plan-name>-phase-N-pseudocode.md

    ## Files Changed
    [list files from implementation subagent]

    ## Output
    Write review to: docs/building/<plan-name>-phase-N-review.md
```

**After POST-GATE:**
1. Read the review file
2. If PASS → TaskUpdate → completed
3. If FAIL → do NOT mark completed → follow Gate Failure Protocol

---

### Sub-Phase N.4: CHECKPOINT

## STOP. Verify POST-GATE task is completed before proceeding.

**TaskGet → confirm blockedBy is empty. TaskUpdate → in_progress, then:**

```bash
git add .
git commit -m "Phase N: [name]

- [summary of what was implemented]
- Model: [resolved_model] ([reason])
- PRE-GATE: pseudocode reviewed
- POST-GATE: verification passed, reviewer approved"
```

Update plan file execution log:
```markdown
### Phase N: [Name]
- [x] PRE-GATE: Discovery + pseudocode complete
- [x] IMPLEMENT: Code written, tests pass
- [x] POST-GATE: Verification passed, reviewer approved
- [x] CHECKPOINT: Committed
Model: [resolved_model] ([reason])
Commit: [hash]
```

**TaskUpdate → completed.**

**State:** "Phase N complete. All sub-phases passed. Proceeding to Phase N+1."

---

### Gate Failure Protocol

If any gate fails:

| Gate | Failure | Action |
|------|---------|--------|
| PRE-GATE | Pseudocode unclear | Refine pseudocode, re-dispatch PRE-GATE agent |
| PRE-GATE | Design issues | Redesign, re-dispatch PRE-GATE agent |
| POST-GATE | Verification fails | Fix code, re-dispatch POST-GATE agent |
| POST-GATE | Reviewer finds issues | Fix issues, re-dispatch POST-GATE agent |

**The failed task stays `in_progress` until it passes. You CANNOT mark it completed on FAIL.**
**You CANNOT proceed to next sub-phase until the current task is completed.**
**blockedBy enforcement prevents skipping - the next task's blockedBy list is not empty until the predecessor is completed.**

---

## Phase 4: VERIFY (Full Test Suite)

### Load Skill

1. `Skill(code-foundations:cc-code-layout-and-style)` — formatting and layout consistency
2. `Skill(code-foundations:cc-documentation-quality)` — comments, docs, and API documentation match the code
3. `Skill(code-foundations:cc-performance-tuning)` — catch obvious performance regressions (O(n²), N+1 queries, unnecessary allocations)
4. `Skill(code-foundations:aposd-optimizing-critical-paths)` — simpler code runs faster; flag unnecessary complexity in hot paths

### Test Coverage Check

Read the **Test Coverage** field from the plan:

| Level | Verification |
|-------|--------------|
| **100%** | Unit tests for ALL new code + integration tests |
| **Backend only** | Server-side tests only, skip frontend |
| **Backend + frontend** | Tests for both layers |
| **None** | Skip test verification (warn: technical debt) |
| **Per-phase** | Check each phase's test notes |

**If coverage falls short:** FAIL verification, require tests before proceeding.

### Pre-Completion Checks

- [ ] All plan phases marked complete
- [ ] **Test coverage matches plan level**
- [ ] All tests pass (unit + integration as required)
- [ ] No skipped tasks
- [ ] Code compiles without warnings

### Run Test Plan

Execute each item from plan's Test Plan section:

```bash
# Unit tests
npm test  # or equivalent

# Integration tests (if specified)
npm run test:integration
```

### Build Verification

Run a clean build and capture output:

```bash
# Build the project (detect build system)
npm run build  # or equivalent: cargo build, go build, make, tsc, etc.
```

**Check for regressions:**
1. **Build succeeds** — if build fails, fix before proceeding
2. **No new warnings** — build output should be clean. Any warnings in output = fix them or verify they are pre-existing (`git stash && build && git stash pop` if uncertain)
3. **No new lint errors** — run linter if configured (`npm run lint`, `cargo clippy`, etc.)

If new warnings or errors are found:
- Fix them before proceeding
- Re-run build to confirm clean
- Only proceed when build is clean

### Verification Gate

| Condition | Action |
|-----------|--------|
| All tests pass, coverage met, build clean | Proceed to REPORT |
| Tests fail | Debug, fix, re-verify |
| Build warnings/errors introduced | Fix, rebuild, re-verify |
| Tests missing (but required by coverage level) | Write tests, then re-verify |
| Coverage = None | Warn "Skipping tests per plan. Technical debt noted." and proceed |

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

### Summary Output (Trust Report)

The summary is a **trust report**, not a status dashboard. Engineers need to verify what the AI built.

```markdown
# Build Complete: [plan name]

## Pipeline: N/N phases, M/M sub-phases

### Phase 1: [name] ([resolved_model])
- PRE-GATE: Pseudocode covered N tasks, M files
- POST-GATE: [PASS|FAIL] (attempt N)
  - [What reviewer found or verified]
  - [Any notes or observations]
- Commit: [hash]
- Artifacts: docs/building/<plan>-phase-1-*.md

### Phase 2: [name] ([resolved_model])
...

## Gate Summary
| Phase | PRE-GATE | POST-GATE | Retries |
|-------|----------|-----------|---------|
| 1     | PASS     | PASS      | 0       |
| 2     | PASS     | FAIL→PASS | 1       |

## Files Changed
- `path/to/file` - [what changed]

## Build & Test Summary
- **Build:** PASS (no new warnings or errors)
- **Unit tests:** X passed, Y failed, Z skipped
- **Integration tests:** [results or N/A]
- **Lint:** PASS (no new issues)

## Manual Testing Steps
[If the plan includes manual testing steps, or if the feature involves UI/UX,
user-facing behavior, or interactions that automated tests cannot fully cover:]
1. [Step-by-step instructions to manually verify the feature]
2. [Expected behavior for each step]
3. [Edge cases worth checking manually]

[If no manual testing needed: "All behavior covered by automated tests."]

## Follow-up
- [Issues flagged by reviewers for future work]
- [Or: "None identified"]
```

**Key elements:**
- **Per-phase reviewer findings** - not just PASS/FAIL, but what was verified and any notes
- **Retry count** - shows if gates caught issues (retries > 0 = the system worked)
- **Artifact links** - engineer can read the discovery, pseudocode, and review files
- **Model used** - shows which model was auto-detected per phase
- **Build & test summary** - concrete proof the build is clean and tests pass
- **Manual testing steps** - what the engineer should verify by hand (or confirmation that automated tests cover everything)
- **Follow-up** - anything the reviewer flagged that wasn't a blocker

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
| "I'll just quickly read the files myself" | Direct exploration pollutes your context. Pre-gate agent returns only what's relevant. |
| "Discovery is overkill for a simple phase" | Plan assumptions often mismatch reality. Pre-gate agent catches this before wasted work. |
| "I already know this codebase" | Your context is stale. Pre-gate agent has fresh eyes and finds what changed. |
| "I'll dispatch an Explore agent for discovery" | Explore agents are read-only and can't write files. Use `code-foundations:pre-gate-agent` which handles discovery + pseudocode together. |
| "I'll tell the subagent to invoke a skill" | Subagents can't invoke skills (fresh context). Use specialized agent types instead. |
| "general-purpose is fine for review" | post-gate-agent has skills built-in. Use `code-foundations:post-gate-agent`. |
| "I'll skip TaskCreate, it's overhead" | TaskCreate with blockedBy is the enforcement mechanism. Without it, gates are just suggestions. |
| "I'll just mark the blocker completed manually" | Marking a gate completed without PASS is lying. The next sub-phase will inherit false confidence. |
| "Haiku is fine for this complex phase" | Auto-detection chose opus for a reason. Override down only with explicit `**Model:**` in the plan. |
| "The subagent doesn't need those skills" | Skills provide checklists and mental models. Without them, the subagent improvises. Include the skill loading block VERBATIM. |
| "I'll summarize the prompt instead" | Paraphrased prompts drop skill loading, output formats, and file paths. Use the templates AS WRITTEN. |
| "quick-checklist is fine for POST-GATE" | Quick-checklist has no reviewer skills. Use `code-foundations:post-gate-agent`. |
| "Those warnings are pre-existing, not mine" | Verify it. `git stash && build && git stash pop` — if warnings disappear, they're yours. |
| "Lint is cosmetic, the build passed" | Lint warnings become bugs. Clean build = clean lint. Fix before proceeding. |
| "Manual testing isn't needed, tests cover it" | If the feature has UI or user-facing behavior, automated tests can't catch what humans see. State it explicitly either way. |

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

## Integration with /code-foundations:whiteboarding

### Expected Flow

```
/code-foundations:whiteboarding "user story"
  ↓
[Socratic questions]
[2-3 approaches]
[Detailed sections]
[Save to docs/plans/YYYY-MM-DD-topic.md]
  ↓
[Optional: Refresh context window]
  ↓
/code-foundations:building docs/plans/YYYY-MM-DD-topic.md
  ↓
[Checklist execution]
[Tests pass]
[Summary report]
```

### Plan File Model Override Syntax

Plans can optionally specify model per phase:

```markdown
### Phase 1: Simple Config
- [ ] Update config file

### Phase 2: Complex Engine
**Model:** opus
- [ ] Build query parser
- [ ] Implement optimizer
```

If `**Model:**` is omitted, auto-detection applies.

### Context Refresh Benefits

Starting fresh session before /code-foundations:building:
- Full context window for implementation
- No planning discussion cluttering context
- Plan file contains all necessary information

---

## Chaining

- **RECEIVES FROM:** whiteboarding (via plan file), user with plan path
- **CHAINS TO:** code-foundations skills during execution
- **RELATED:** oberexec, aposd-verifying-correctness, cc-quality-practices
