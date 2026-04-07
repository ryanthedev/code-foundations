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
| **Worktree isolation required** | Multi-phase commits on main = no rollback, polluted history. Worktrees enable parallel builds. |
| **Load plan before coding** | No plan = no checklist = forgotten tasks |
| **One section at a time** | Parallel sections = merge conflicts + lost context |
| **BUILD before review (Full/Standard gate)** | No design = coding without discovery = rework. Exception: Minimal gate phases skip discovery/pseudocode. |
| **Verification before commit (per gate policy)** | Full phases: REVIEW required. Standard/Minimal: tests are the gate. Catch-up review before next Full phase if 2+ phases ran ungated. |
| **Independent verification on complex work** | Self-review is blind; fresh agent catches issues. But over-verification on trivial work injects noise (CR-Bench: SNR drops 69% on small models under reflexion). |
| **Mark complete only when gates pass** | Premature completion = unverified work shipped |
| **Update execution log** | Log enables debugging failed builds |

---

## Phase 1: LOAD (Read Plan File)

### Worktree Gate (MANDATORY - First Check)

**Before anything else, determine workspace mode:**

```bash
git branch --show-current
git status
git worktree list
```

| Situation | Action |
|-----------|--------|
| Already in a worktree (`.git` is a file, not a directory) | On a feature branch — proceed |
| On `main`/`master`, clean | Ask: worktree or feature branch? |
| On feature branch, clean | Proceed (single-build mode) |
| Dirty working tree | Ask: "Uncommitted changes. Stash, commit, or abort?" |

**Ask the user:**

```
You're on [main]. Building requires an isolated workspace.

Worktree or feature branch?
- [ ] Worktree — isolated copy, main checkout stays free for other work
- [ ] Feature branch — simpler, but blocks this checkout during build
- [ ] Abort
```

**If worktree:**
```bash
# Extract plan slug from plan filename (e.g., 2026-03-17-auth-system → auth-system)
PLAN_SLUG="<extracted-slug>"

# Create worktree with feature branch
git worktree add .claude/worktrees/${PLAN_SLUG} -b feature/${PLAN_SLUG}
```

Then change working directory to the worktree:
```bash
cd .claude/worktrees/${PLAN_SLUG}
```

**If feature branch:**
```bash
git checkout -b feature/<plan-topic>
```

**Record workspace mode** for use in REPORT:
- `worktree: .claude/worktrees/<slug>` + `branch: feature/<slug>`
- OR `branch: feature/<topic>`

### Dependency Setup (Worktree Mode Only)

After creating a worktree, gitignored files (node_modules, .env, build artifacts) are absent. Detect and install dependencies:

```bash
# Auto-detect package manager and install
if [ -f pnpm-lock.yaml ]; then pnpm install --frozen-lockfile
elif [ -f package-lock.json ]; then npm ci
elif [ -f yarn.lock ]; then yarn install --frozen-lockfile
elif [ -f go.mod ]; then go mod download
elif [ -f Cargo.lock ]; then cargo fetch
elif [ -f uv.lock ]; then uv sync
fi
```

**For macOS (APFS):** If the main checkout has `node_modules`, copy-on-write is near-instant:
```bash
cp -Rc ../../../node_modules ./node_modules  # APFS CoW, no actual disk copy
```

**Skip dependency setup if:** the project has no lockfile or the plan does not involve building/testing code (e.g., documentation-only plans).

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
1. **Context** - What we're building (used for goal anchoring in all subagent prompts)
2. **Approach** - How we're building it
3. **Phases** - Implementation sections
4. **Done-when items per phase** - Every `- [ ]` under each phase's `**Done when:**` (passed verbatim to build and review agents)
5. **Test Coverage** - What level of tests required (100%, backend only, etc.)
6. **Test Plan** - Specific verification criteria
7. **Model overrides** - Optional `**Model:** <model>` per phase
8. **Pipeline overrides** - Optional `**Pipeline:** direct` per phase
9. **Assumptions** - Assumptions table with `Verify Before Phase` timing

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

### Create Phase Tasks Upfront

For each phase N, run Model Auto-Detection and Gate Policy Detection (see below), then create tasks.

**Full gate (2 tasks):**

1. `TaskCreate(subject: "Phase N.1: BUILD - [phase name]", description: "Discovery + pseudocode + implement. Model: [from plan or default].", activeForm: "Building Phase N")`
2. `TaskCreate(subject: "Phase N.2: REVIEW - [phase name]", description: "Post-gate review. Model: [from plan or default]. Must return PASS.", activeForm: "Reviewing Phase N")`

**Standard gate (1 task — REVIEW skipped, tests are the gate):**

1. `TaskCreate(subject: "Phase N.1: BUILD - [phase name]", description: "Discovery + pseudocode + implement. Model: [from plan or default].", activeForm: "Building Phase N")`

**Minimal gate (1 task — no discovery/pseudocode):**

1. `TaskCreate(subject: "Phase N.1: BUILD - [phase name]", description: "Implement from plan description (minimal gate). Model: [from plan or default].", activeForm: "Building Phase N")`

**Chain dependencies:**
- Full gate: N.2 blockedBy N.1. Next phase blockedBy N.2.
- Standard/Minimal: Next phase blockedBy N.1.

**Orchestrator handles commits** directly after each phase completes (after REVIEW passes for Full gate, or after BUILD completes for Standard/Minimal gate).

**Catch-up review tasks** are NOT created upfront. They are inserted dynamically when the catch-up rule triggers (2+ phases since last REVIEW, before a Full phase).

Example for a 3-phase plan (Full + Minimal + Full):
```
Phase 1.1: BUILD          → no blockedBy (Full gate)
Phase 1.2: REVIEW         → blockedBy: [1.1]
Phase 2.1: BUILD          → blockedBy: [1.2] (Minimal gate)
Phase 3.1: BUILD          → blockedBy: [2.1] (Full gate — catch-up check happens here)
Phase 3.2: REVIEW         → blockedBy: [3.1]
```

---

## Phase 3: EXECUTE (Implement Sections)

### CRITICAL: DO NOT DO ANYTHING DIRECTLY

**You MUST dispatch subagents for ALL work. DO NOT:**
- Read/explore code files directly during building
- Edit code files directly during building
- Skip any task
- Proceed when a blockedBy dependency is not completed
- Mark a gate task completed when it returned FAIL

**Exception: You DO handle commits directly** — no subagent needed for git operations.

---

### Agent Types Per Sub-Phase

| Sub-Phase | Agent Type | Standards Loaded (baked into agent template) |
|-----------|-----------|-------------------------------|
| N.1 BUILD | `code-foundations:build-agent` | `references/pre-gate-standards.md` + `references/implement-standards.md` |
| N.2 REVIEW | `code-foundations:post-gate-agent` | `references/post-gate-standards.md` |
| Commit | Orchestrator (you) | N/A |

**Standards files are combined references** distilled from individual skills. Agents Read() one file instead of loading 3-4 separate Skill() calls. Individual skills remain available for standalone invocation and code review.

### Skills from Plan

If the plan's phase has a `**Skills:**` field, include those skills in the agent dispatch prompt. The build-agent also does its own skill discovery if no skills are passed — but explicit skills from the plan take precedence.

**Add this block to the dispatch prompt when `**Skills:**` is present:**
```
## Additional Skills
Before starting work, load the following skills using the Skill tool:
- Skill([skill-1])
- Skill([skill-2])
```

---

### Model Resolution

Use the `**Model:**` field from the plan if present. If not specified, omit the model parameter — the agent runs on whatever model is active.

**REVIEW model downgrade (Prover-Verifier):**

If the plan specifies a model, downgrade REVIEW one tier:

| BUILD model | REVIEW model |
|-------------|--------------|
| opus | sonnet |
| sonnet | haiku |
| haiku | haiku (floor) |

If no model specified, omit for both BUILD and REVIEW.

Research basis: prover-verifier gap (2407.13692). The asymmetry is intentional.

---

### Gate Policy Detection

After resolving the model, determine the gate level for each phase. This controls which sub-phases run.

**Research basis:** Non-uniform verification is strictly better than uniform (Plan and Budget: 193.8% efficiency gain). Over-verification on easy tasks injects noise and wastes budget (Thinkless: 86.7% of easy queries harmed by deep reasoning; CR-Bench: reflexion on small models collapses SNR 69%). Simpler pipelines with fewer verification loops produce better results at lower cost (Agentless: $0.70/32% vs SWE-agent $2.53/18%).

**Gate levels:**

| Level | Sub-Phases | When |
|---|---|---|
| **Full** | BUILD → REVIEW → commit | High-risk work where errors cascade |
| **Standard** | BUILD → commit | Medium work; tests are the verification gate |
| **Minimal** | BUILD (minimal) → commit | Trivial work; tests are the gate, no design phase needed |
| **Catch-up** | Batch REVIEW inserted before next Full phase | Prevents drift across accumulated ungated phases |

**Resolution order** (first match wins):

1. **Plan override:** `**Pipeline:** full` forces Full. `**Pipeline:** direct` forces Minimal.
2. **Always Full** if ANY of these are true:
   - First phase in the plan (errors here cascade to everything)
   - Final phase in the plan (last chance before merge)
   - Model is set to opus
   - Phase has `**Uncertainty:**` that is NOT "None"
   - Phase has assumptions to verify (from Assumptions table)
   - Phase has a `**Skills:**` field
3. **Minimal** if ALL of these are true:
   - Model is set to haiku
   - No Skills, no assumptions, no uncertainty
   - Done-when items <= 2
4. **Standard** — everything else

**Catch-up rule:** Before executing any Full phase, check: have 2 or more phases run since the last REVIEW? If yes, insert a catch-up REVIEW covering the accumulated phases before proceeding. This prevents drift without per-phase overhead.

**State the resolved gate level when creating tasks:**
"Phase N gate: [Full/Standard/Minimal] (reason: [auto/plan override])"

---

### Execution Loop

All tasks were created in SETUP. Execute them in order.

For each task:

```
1. TaskGet(task_id) → verify blockedBy list is empty (all predecessors completed)
2. TaskUpdate(task_id, status: "in_progress")
3. Dispatch subagent (see templates below)
4. Wait for completion
5. If result is FAIL:
   → Do NOT mark completed
   → Follow Gate Failure Protocol
6. If success:
   → TaskUpdate(task_id, status: "completed")
   → If this is the last task for the phase (REVIEW for Full, BUILD for Standard/Minimal):
     commit (see Commit After Phase below)
7. Proceed to next task
```

---

### Sub-Phase N.1: BUILD (Discovery + Design + Implementation)

## STOP. YOU CANNOT EXPLORE CODE, WRITE PSEUDOCODE, OR IMPLEMENT DIRECTLY.

**TaskUpdate → in_progress, then dispatch the build agent.**

The build agent combines discovery, pseudocode, and implementation in one pass. It writes discovery and pseudocode files (for post-gate review), then implements.

**Full/Standard gate dispatch:**

```
Agent tool:
- subagent_type: "code-foundations:build-agent"
- model: [from plan's **Model:** field, or omit if not set]
- description: "BUILD Phase N"
- prompt: |
    Build Phase N of the building plan. This is a three-part task:
    1. Discovery — explore codebase, map what exists, identify gaps
    2. Design — write pseudocode referencing DW items, verify coverage
    3. Implementation — translate pseudocode to code, run tests

    Write discovery and pseudocode files before implementing.

    ## Plan Context
    [paste the Context section from the plan file — the 2-3 sentence problem statement]

    ## Progress
    [For Phase 1: "This is the first phase."]
    [For Phase N>1: "Completed: Phase 1: [name] — [1 sentence summary from execution log]. Phase 2: ..."]
    Current: Phase N of M

    ## Phase N: [name]
    [paste phase description and file list from plan]

    ## Done-When Items (DW-IDs)
    These are the acceptance criteria from the plan. Your pseudocode must
    reference which DW items each section addresses (e.g., "## Setup [DW-1.1, DW-1.3]").
    Any DW item not referenced in any section is a visible gap.
    If any item cannot be met, return UPDATE_PLAN.
    [paste ALL DW items from the plan phase, verbatim:]
    - [ ] DW-N.1: [done-when item 1]
    - [ ] DW-N.2: [done-when item 2]
    - [ ] DW-N.X: [done-when item N...]

    [if plan phase has **Skills:** field, include:]
    ## Additional Skills
    Before starting work, load the following skills using the Skill tool:
    - Skill([skill-from-plan])

    [if plan has Assumptions with "Verify Before Phase: N", include:]
    ## Assumption Verification
    Before proceeding with discovery, verify these assumptions from the plan:
    - [assumption text] (Confidence: [level])
    If any assumption is wrong, return UPDATE_PLAN with the invalidated assumption
    and what you found instead.

    ## Inputs
    - Plan file: docs/plans/<plan-name>.md
    - Phase: N - [name]

    ## Output Files
    - Discovery: docs/building/<plan-name>-phase-N-discovery.md
    - Pseudocode: docs/building/<plan-name>-phase-N-pseudocode.md
```

**Minimal gate dispatch:**

```
Agent tool:
- subagent_type: "code-foundations:build-agent"
- model: [from plan's **Model:** field, or omit if not set]
- description: "BUILD Phase N (minimal)"
- prompt: |
    Build Phase N of the building plan. This phase uses minimal gate
    policy — skip discovery and pseudocode, implement directly from
    the plan description.

    ## Plan Context
    [paste the Context section from the plan file]

    ## Progress
    [For Phase N>1: "Completed: Phase 1: [name] — [1 sentence summary]. Phase 2: ..."]
    Current: Phase N of M

    [if plan phase has **Skills:** field, include:]
    ## Additional Skills
    Before starting work, load the following skills using the Skill tool:
    - Skill([skill-from-plan])

    ## Phase N: [name]
    [paste the full phase description from the plan]

    ## Inputs
    - Plan file: docs/plans/<plan-name>.md
    - Phase: N - [name]
```

**After BUILD returns:**
1. Check status: DONE, SKIP, UPDATE_PLAN, or BLOCKED
2. If SKIP → mark task completed, skip REVIEW task if exists, proceed to next phase
3. If UPDATE_PLAN → pause and ask user
4. If BLOCKED → do NOT mark completed → debug and re-dispatch or escalate
5. If DONE → TaskUpdate → completed
6. If Standard/Minimal gate → commit now (see Commit After Phase)
7. If Full gate → proceed to REVIEW

---

### Sub-Phase N.2: REVIEW (Post-Gate)

## STOP. Verify BUILD task is completed before proceeding.

**TaskUpdate → in_progress, then dispatch.**

**Always use `code-foundations:post-gate-agent`.** Skills are baked into the agent template.

```
Agent tool:
- subagent_type: "code-foundations:post-gate-agent"
- model: [from plan's **Model:** field, or omit if not set]
- description: "REVIEW Phase N"
- prompt: |
    Review Phase N implementation.

    ## Plan Context
    [paste the Context section from the plan file]

    ## Progress
    [For Phase N>1: "Completed: Phase 1: [name] — [1 sentence summary]. Phase 2: ..."]
    Current: Phase N of M

    ## Done-When Items (DW-IDs) — Requirement Verification
    For EACH item below, mark SATISFIED or NOT_SATISFIED with evidence
    (file:line, test name, or observable behavior). Any NOT_SATISFIED → FAIL.
    Do NOT skip items. Do NOT check against pseudocode only — these come
    from the original plan and may include items the build agent missed.
    [paste ALL DW items from the plan phase, verbatim:]
    - DW-N.1: [done-when item 1] → Status: ___ Evidence: ___
    - DW-N.2: [done-when item 2] → Status: ___ Evidence: ___
    - DW-N.X: [done-when item N...] → Status: ___ Evidence: ___

    [if plan phase has **Skills:** field, include:]
    ## Additional Skills
    Before starting work, load the following skills using the Skill tool:
    - Skill([skill-from-plan])

    ## Inputs
    - Plan: docs/plans/<plan-name>.md (Phase N section)
    [Full/Standard gate only:]
    - Discovery: docs/building/<plan-name>-phase-N-discovery.md
    - Pseudocode: docs/building/<plan-name>-phase-N-pseudocode.md
    [Minimal gate: no discovery/pseudocode files exist]

    ## Files Changed
    [list files from BUILD subagent]

    ## Output
    Write review to: docs/building/<plan-name>-phase-N-review.md
```

**After REVIEW:**
1. Read the review file
2. If PASS → TaskUpdate → completed → commit (see Commit After Phase)
3. If FAIL → do NOT mark completed → follow Gate Failure Protocol

---

### Catch-Up REVIEW (inserted dynamically)

**Trigger:** Before executing any Full gate phase, check: have 2+ phases completed since the last REVIEW ran? If yes, insert a catch-up review before proceeding to the Full phase's BUILD.

This prevents drift across accumulated Standard/Minimal phases without per-phase overhead.

```
Agent tool:
- subagent_type: "code-foundations:post-gate-agent"
- model: [REVIEW model for the upcoming Full phase]
- description: "Catch-up REVIEW for Phases X-Y"
- prompt: |
    Batch review of Phases X through Y. These phases ran with Standard
    or Minimal gate policy (tests-only verification). Review them now
    before proceeding to Phase Z (Full gate).

    ## Plan Context
    [paste the Context section from the plan file]

    ## Phases to Review
    [For each accumulated phase:]
    ### Phase X: [name]
    Done-When Items:
    - DW-X.1: [item] → Status: ___ Evidence: ___
    Files changed: [list]

    ### Phase Y: [name]
    Done-When Items:
    - DW-Y.1: [item] → Status: ___ Evidence: ___
    Files changed: [list]

    ## Cross-Phase Coherence
    Check that the accumulated phases work together:
    - No contradictions between phase outputs
    - No regressions introduced by later phases
    - Tests still pass for earlier phases' functionality

    ## Output
    Write review to: docs/building/<plan-name>-catchup-phases-X-Y-review.md
```

**After catch-up REVIEW:**
- If PASS → proceed to the Full phase's BUILD
- If FAIL → fix issues before proceeding. Same Gate Failure Protocol applies.

**Do NOT create catch-up tasks upfront.** Insert them dynamically when the trigger fires. This keeps the initial task list clean.

---

### Commit After Phase (Orchestrator Handles Directly)

After the last task for a phase completes (REVIEW for Full, BUILD for Standard/Minimal), **you commit directly** — no subagent, no task.

```bash
git add .
git commit -m "[prefix]([scope]): [description]

[WHY this phase exists — goal, key decisions, constraints that shaped implementation]

Phase: N/M \"[phase name]\"
Plan: docs/plans/[plan-file].md
AI-Model: [model used]
AI-Epistemic-Status: [tested|assumed|provisional]
Gate-Policy: [Full|Standard|Minimal]
Review: [pass|fail->pass (N attempts)|skipped (Standard/Minimal)|catch-up (batch)]"
```

**Commit message rules:**
- **Subject**: Conventional Commits prefix (`feat`, `fix`, `refactor`, `chore`, etc.) + scope + description
- **Body**: WHY — goal, key decisions, constraints. Not operational telemetry.
- **Trailers**: Machine-parseable metadata via git trailer format
- **AI-Epistemic-Status**: `tested` (verified by tests), `assumed` (believed correct, not proven), `provisional` (expected to change)
- **AI-Temporal-Validity**: Add only when a decision has a known expiry (e.g., `until-v2-migration`)

Update plan file execution log:
```markdown
### Phase N: [Name] (Gate: [Full/Standard/Minimal])
- [x] BUILD: Discovery + pseudocode + implementation complete
- [x] REVIEW: Verification passed [or "SKIPPED — tests are gate" or "Covered by catch-up review"]
- [x] Committed
Commit: [hash]
Summary: [1 sentence — what this phase delivered and what state it left the codebase in]
```

**The Summary line is critical for goal anchoring.** It feeds into the `## Progress` block of subsequent subagent dispatch prompts, giving later phases context about what earlier phases accomplished.

**State:** "Phase N complete. Committed. Proceeding to Phase N+1."

---

### Gate Failure Protocol

If any gate fails:

| Gate | Failure | Action |
|------|---------|--------|
| BUILD | Discovery finds gaps | Re-dispatch build agent with updated context |
| BUILD | Design issues | Re-dispatch build agent |
| REVIEW | Verification fails | Fix code, re-dispatch REVIEW agent |
| REVIEW | Reviewer finds issues | Fix issues, re-dispatch REVIEW agent |

**The failed task stays `in_progress` until it passes. You CANNOT mark it completed on FAIL.**
**You CANNOT proceed to next sub-phase until the current task is completed.**
**blockedBy enforcement prevents skipping - the next task's blockedBy list is not empty until the predecessor is completed.**

### Retry Cap (max 3 failures per gate)

Track the number of times each gate has returned FAIL for the current phase.

| Attempt | Action |
|---------|--------|
| 1st FAIL | Fix issues, re-dispatch |
| 2nd FAIL | Fix issues, re-dispatch. Note: if the same issues recur, the fix approach is wrong. |
| 3rd FAIL | **STOP.** Do not re-dispatch. Present findings to user: |

```
Phase N REVIEW has failed 3 times.

Recurring issues:
- [list findings that appeared in multiple reviews]

Options:
1. I fix the remaining issues and retry (explain what you'd do differently)
2. You provide guidance on the recurring issues
3. We revisit the plan for this phase (UPDATE_PLAN)
```

**Do NOT silently retry a 4th time.** Three failures indicate a structural problem — either the plan is wrong, the pseudocode is wrong, or the fix approach isn't addressing root causes. Escalate to the user.

---

## Phase 4: VERIFY (Full Test Suite)

### Load Skill

1. `Skill(code-foundations:performance-optimization)` — catch obvious performance regressions (O(n²), N+1 queries, unnecessary allocations) and flag unnecessary complexity in hot paths
2. `Skill(code-foundations:cc-refactoring-guidance)` — identify refactoring opportunities introduced during implementation

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

Gate metadata (model, review results, epistemic status) now lives in commit trailers. The trust report is derived from `git log`:

```bash
# Full trailer dump for the build
git log --format="%(trailers)" first-commit..HEAD

# Find all provisional decisions
git log --format="%(trailers:key=AI-Epistemic-Status)" first-commit..HEAD

# One-line summary
git log --oneline first-commit..HEAD
```

The trust report text output focuses on what commit trailers can't capture:

```markdown
# Build Complete: [plan name]

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

## Merge Instructions
[If worktree mode:]
Worktree: .claude/worktrees/<slug>/
Branch: feature/<slug>

To merge and clean up (run from main checkout, not the worktree):
  cd /path/to/main/checkout
  git worktree remove .claude/worktrees/<slug>   # remove worktree FIRST
  git merge --no-ff feature/<slug>                # then merge
  git branch -d feature/<slug>                    # then delete branch
  git worktree prune                              # clean up stale entries

If using GitHub PR instead of local merge:
  cd /path/to/main/checkout
  git push -u origin feature/<slug>               # push from main checkout
  gh pr create ...                                # create PR
  gh pr merge <number> --merge --delete-branch    # merge + remote delete
  git worktree remove .claude/worktrees/<slug>    # remove worktree
  git branch -D feature/<slug>                    # force-delete local branch
  git pull --ff-only                              # update main

NOTE: gh pr merge will fail if run from inside the worktree
(git can't resolve main). Always run from the main checkout.
If git pull diverges (plan commits on main not on remote),
rebase: git rebase origin/main

[If feature branch mode:]
Branch: feature/<topic>
To merge: git merge --no-ff feature/<topic>
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

## Integration with /code-foundations:whiteboarding

### Expected Flow (Single Build)

```
/code-foundations:whiteboarding "user story"
  ↓
[Socratic questions]
[2-3 approaches]
[Detailed sections]
[Save + commit to docs/plans/YYYY-MM-DD-topic.md]
  ↓
[Set thinking effort to default — plan has the reasoning, orchestration doesn't need max effort]
  ↓
/code-foundations:building docs/plans/YYYY-MM-DD-topic.md
  ↓
[Worktree Gate → creates .claude/worktrees/<slug>/]
[Checklist execution in worktree]
[Tests pass]
[Summary report with merge instructions]
```

### Expected Flow (Parallel Builds)

```
Claude Instance 1                        Claude Instance 2
────────────────                        ────────────────
/whiteboarding "auth system"            /whiteboarding "notifications"
  → saves + commits plan                  → saves + commits plan
  → clear + build                         → clear + build

/building (worktree: auth-system)       /building (worktree: notifications)
  → .claude/worktrees/auth-system/        → .claude/worktrees/notifications/
  → feature/auth-system branch            → feature/notifications branch
  → all phases run isolated               → all phases run isolated
  → report: "merge when ready"            → report: "merge when ready"

                    User merges both to main when ready
```

**Key constraint:** Each parallel build must target a different plan file. Never run two building instances against the same plan.

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

### Thinking Effort for Building

Set thinking effort to default before building. The plan already contains the strategic reasoning — max effort during orchestration is wasted overhead. The subagents do the heavy thinking in their own contexts. Default effort on the orchestrator saves tokens without losing quality.

For whiteboarding/planning, use max effort. For building/execution, use default.

Worktree provides filesystem isolation from other builds.

---

## Chaining

- **RECEIVES FROM:** whiteboarding (via plan file), user with plan path
- **CHAINS TO:** code-foundations skills during execution
- **RELATED:** aposd-verifying-correctness, cc-quality-practices
