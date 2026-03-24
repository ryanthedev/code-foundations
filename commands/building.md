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
| **PRE-GATE before implementation (full pipeline)** | No pseudocode = coding without design = rework. Exception: simplified pipeline phases skip PRE-GATE. |
| **POST-GATE before checkpoint** | No verification = bugs escape to next phase |
| **Reviewer agent per phase** | Self-review is blind; fresh agent catches issues |
| **Mark complete only when gates pass** | Premature completion = unverified work shipped |
| **Update execution log** | Log enables debugging failed builds |
| **TaskCreate sub-phases** | Prompt-only enforcement gets skipped. blockedBy chains cannot be skipped. |

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
| On `main`/`master`, clean | Create worktree (recommended) or feature branch |
| On feature branch, clean | Proceed (single-build mode) |
| Dirty working tree | Ask: "Uncommitted changes. Stash, commit, or abort?" |

**Worktree mode (recommended for parallel builds):**

```
You're on [main]. Building requires an isolated workspace.

How would you like to proceed?
- [ ] Create worktree (recommended) — enables parallel builds
- [ ] Create feature branch — single build, blocks this checkout
- [ ] Abort building
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

**If feature branch (legacy mode):**
```bash
git checkout -b feature/<plan-topic>
```

**Record workspace mode** for use in REPORT:
- `worktree: .claude/worktrees/<slug>` + `branch: feature/<slug>`
- OR `branch: feature/<topic>` (legacy)

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
4. **Done-when items per phase** - Every `- [ ]` under each phase's `**Done when:**` (passed verbatim to pre-gate and post-gate agents)
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

### Create ALL Sub-Phase Tasks Upfront

**DO NOT create phase-level tasks like "Phase 1: [Name]". DO NOT use TodoWrite.**

Create sub-phase tasks for EVERY phase in the plan NOW, before executing anything.

For each phase N, run Model Auto-Detection and Pipeline Detection (see below), then create tasks.

**Full pipeline (4 tasks):**

1. `TaskCreate(subject: "Phase N.1: PRE-GATE - [phase name]", description: "Discovery + pseudocode via pre-gate-agent. Model: [resolved_model].", activeForm: "Running pre-gate for Phase N")`
2. `TaskCreate(subject: "Phase N.2: IMPLEMENT - [phase name]", description: "Implement from pseudocode. Model: [resolved_model].", activeForm: "Implementing Phase N")`
3. `TaskCreate(subject: "Phase N.3: POST-GATE - [phase name]", description: "Review implementation. Model: [resolved_model]. Must return PASS.", activeForm: "Running post-gate for Phase N")`
4. `TaskCreate(subject: "Phase N.4: CHECKPOINT - [phase name]", description: "Commit after all gates pass.", activeForm: "Committing Phase N")`

**Simplified pipeline (3 tasks — PRE-GATE skipped):**

1. `TaskCreate(subject: "Phase N.1: PRE-GATE - [phase name]", description: "SKIPPED — simplified pipeline.", status: "completed")`
2. `TaskCreate(subject: "Phase N.2: IMPLEMENT - [phase name]", description: "Implement from plan description (no pseudocode). Model: [resolved_model].", activeForm: "Implementing Phase N")`
3. `TaskCreate(subject: "Phase N.3: POST-GATE - [phase name]", description: "Review implementation. Model: [resolved_model]. Must return PASS.", activeForm: "Running post-gate for Phase N")`
4. `TaskCreate(subject: "Phase N.4: CHECKPOINT - [phase name]", description: "Commit after all gates pass.", activeForm: "Committing Phase N")`

Note: simplified pipeline still creates the PRE-GATE task but marks it completed immediately. This keeps the N.1-N.4 numbering consistent and the blockedBy chain intact.

**Then chain ALL dependencies:**
- Within each phase: N.2 blockedBy N.1, N.3 blockedBy N.2, N.4 blockedBy N.3
- **Between phases:** Phase (N+1).1 blockedBy Phase N.4

Example for a 2-phase plan (full + simplified):
```
Phase 1.1: PRE-GATE        → no blockedBy (full pipeline)
Phase 1.2: IMPLEMENT       → blockedBy: [1.1]
Phase 1.3: POST-GATE       → blockedBy: [1.2]
Phase 1.4: CHECKPOINT      → blockedBy: [1.3]
Phase 2.1: PRE-GATE        → blockedBy: [1.4], pre-completed (simplified pipeline)
Phase 2.2: IMPLEMENT       → blockedBy: [2.1] (reads plan directly, no pseudocode)
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

**The ONLY tasks you create are the sub-phase tasks per phase (PRE-GATE, IMPLEMENT, POST-GATE, CHECKPOINT). Full pipeline = 4 active tasks. Simplified pipeline = 3 active + 1 pre-completed.**

---

### Mandatory Skill Loading Per Sub-Phase

Each sub-phase dispatches a specific agent type with specific skills. **Do NOT paraphrase the prompts below. Include the skill loading instructions VERBATIM.**

| Sub-Phase | Agent Type | Standards Loaded (baked into agent template) |
|-----------|-----------|-------------------------------|
| N.1 PRE-GATE | `code-foundations:pre-gate-agent` | `references/pre-gate-standards.md` |
| N.2 IMPLEMENT | `code-foundations:implementation-agent` | `references/implement-standards.md` |
| N.3 POST-GATE | `code-foundations:post-gate-agent` | `references/post-gate-standards.md` |
| N.4 CHECKPOINT | None (you do this) | N/A |

**Standards files are combined references** distilled from individual skills. Agents Read() one file instead of loading 3-4 separate Skill() calls. Individual skills remain available for standalone invocation and code review.

### Additional Skills from Plan

If the plan's phase has a `**Skills:**` field, include those skills in the agent dispatch prompt as additional skill loading instructions. These come from whiteboarding's skill audit and may include skills from any installed plugin (e.g., `react-native-foundations:coding`, `design-for-ai:a11y`, `svelte-foundations:coding`).

**Add this block to the dispatch prompt when `**Skills:**` is present:**
```
## Additional Skills
Before starting work, load the following skills using the Skill tool:
- Skill([skill-1])
- Skill([skill-2])
```

These are loaded IN ADDITION to the agent's default skills, not as replacements.

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

### Pipeline Detection

After resolving the model, determine the pipeline type for each phase: **full** or **simplified**.

**Resolution order** (first match wins):

1. **Plan override:** If phase has `**Pipeline:** direct`, use simplified pipeline.
2. **Plan override:** If phase has `**Pipeline:** full`, use full pipeline.
3. **Force full** if ANY of these are true:
   - Model resolves to opus
   - Phase has a `**Skills:**` field
   - Phase has assumptions to verify (from Assumptions table with `Verify Before Phase: N`)
   - Phase has `**Uncertainty:**` that is NOT "None"
4. **Auto-detect simplified** if ALL of these are true:
   - Model resolves to haiku
   - No Skills, no assumptions, no uncertainty
   - Done-when items <= 2
5. **Default:** full pipeline

| Pipeline | Sub-Phases | When |
|----------|-----------|------|
| **Full** | PRE-GATE → IMPLEMENT → POST-GATE → CHECKPOINT | Default for sonnet/opus phases |
| **Simplified** | IMPLEMENT → POST-GATE → CHECKPOINT | Haiku phases with trivial scope |

**State the resolved pipeline when creating tasks:**
"Phase N pipeline: [full/simplified] (reason: [auto/plan override])"

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

**Full pipeline dispatch:**

```
Agent tool:
- subagent_type: "code-foundations:implementation-agent"
- model: [resolved_model]
- description: "Implement Phase N"
- prompt: |
    Implement Phase N of the building plan.

    ## Plan Context
    [paste the Context section from the plan file]

    ## Progress
    [For Phase 1: "This is the first phase."]
    [For Phase N>1: "Completed: Phase 1: [name] — [1 sentence summary]. Phase 2: ..."]
    Current: Phase N of M

    [if plan phase has **Skills:** field, include:]
    ## Additional Skills
    Before starting work, load the following skills using the Skill tool:
    - Skill([skill-from-plan])

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

**Simplified pipeline dispatch (no PRE-GATE, no pseudocode):**

```
Agent tool:
- subagent_type: "code-foundations:implementation-agent"
- model: [resolved_model]
- description: "Implement Phase N (simplified)"
- prompt: |
    Implement Phase N of the building plan. This is a simplified pipeline
    phase — no pseudocode file exists. Work directly from the plan description.

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

    ## Your Tasks
    1. Read the plan phase description above - this is your implementation spec
    2. Read the plan file for full context: docs/plans/<plan-name>.md
    3. Implement what the phase describes
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

    ## Plan Context
    [paste the Context section from the plan file]

    ## Progress
    [For Phase N>1: "Completed: Phase 1: [name] — [1 sentence summary]. Phase 2: ..."]
    Current: Phase N of M

    ## Done-When Items (DW-IDs) — Requirement Verification
    For EACH item below, mark SATISFIED or NOT_SATISFIED with evidence
    (file:line, test name, or observable behavior). Any NOT_SATISFIED → FAIL.
    Do NOT skip items. Do NOT check against pseudocode only — these come
    from the original plan and may include items the pre-gate agent missed.
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
    [full pipeline only:]
    - Discovery: docs/building/<plan-name>-phase-N-discovery.md
    - Pseudocode: docs/building/<plan-name>-phase-N-pseudocode.md
    [simplified pipeline: no discovery/pseudocode files exist]

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
git commit -m "[prefix]([scope]): [description]

[WHY this phase exists — goal, key decisions, constraints that shaped implementation]

Phase: N/M \"[phase name]\"
Plan: docs/plans/[plan-file].md
AI-Model: [resolved_model]
AI-Epistemic-Status: [tested|assumed|provisional]
Pre-Gate: [pass|fail->pass (N attempts)|skipped]
Post-Gate: [pass|fail->pass (N attempts)]
Reviewed-by: post-gate-agent"
```

**Commit message rules (from ADR):**
- **Subject**: Conventional Commits prefix (`feat`, `fix`, `refactor`, `chore`, etc.) + scope + description
- **Body**: WHY — goal, key decisions, constraints. Not operational telemetry.
- **Trailers**: Machine-parseable metadata via git trailer format
- **AI-Epistemic-Status**: `tested` (verified by tests), `assumed` (believed correct, not proven), `provisional` (expected to change)
- **AI-Temporal-Validity**: Add only when a decision has a known expiry (e.g., `until-v2-migration`)

Update plan file execution log:
```markdown
### Phase N: [Name]
- [x] PRE-GATE: Discovery + pseudocode complete [or "SKIPPED — simplified pipeline"]
- [x] IMPLEMENT: Code written, tests pass
- [x] POST-GATE: Verification passed, reviewer approved
- [x] CHECKPOINT: Committed
Commit: [hash]
Summary: [1 sentence — what this phase delivered and what state it left the codebase in]
```

**The Summary line is critical for goal anchoring.** It feeds into the `## Progress` block of subsequent subagent dispatch prompts, giving later phases context about what earlier phases accomplished.

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

Gate metadata (model, pre-gate/post-gate results, epistemic status) now lives in commit trailers. The trust report is derived from `git log`:

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

To merge:
  cd /path/to/main/checkout
  git merge --no-ff feature/<slug>
  git worktree remove .claude/worktrees/<slug>
  git branch -d feature/<slug>
  git worktree prune

[If legacy branch mode:]
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
[Refresh context window]
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

### Context Refresh Benefits

Starting fresh session before /code-foundations:building:
- Full context window for implementation
- No planning discussion cluttering context
- Plan file contains all necessary information
- Worktree provides filesystem isolation from other builds

---

## Chaining

- **RECEIVES FROM:** whiteboarding (via plan file), user with plan path
- **CHAINS TO:** code-foundations skills during execution
- **RELATED:** oberexec, aposd-verifying-correctness, cc-quality-practices
