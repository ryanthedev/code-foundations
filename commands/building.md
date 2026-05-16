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
| **BUILD before review (Full/Standard gate)** | No design = coding without discovery = rework. Exception: Minimal gate phases skip discovery. |
| **Verification before commit (per gate policy)** | Full phases: REVIEW required. Standard/Minimal: tests are the gate. Catch-up review before next Full phase if 2+ phases ran ungated. |
| **Independent verification on complex work** | Self-review is blind; fresh agent catches issues. But over-verification on trivial work injects noise (CR-Bench: SNR drops 69% on small models under reflexion). |
| **Mark complete only when gates pass** | Premature completion = unverified work shipped |
| **Update execution log** | Log enables debugging failed builds |

---

## Phase 1: LOAD (Read Plan File)

### Worktree Gate (MANDATORY - First Check)

Clear the worktree gate before any other work. **Read `references/worktree-gate.md`** for the full procedure: workspace-mode detection, prompts for main/master, worktree vs feature-branch creation, dependency setup, and record-keeping for REPORT.

**Summary:** Inspect `git branch / status / worktree list`. If on main/master, ask user worktree-or-branch. Create the chosen workspace, copy the plan file in if a worktree, install deps if a lockfile is present, and record the mode for use in REPORT. **Non-negotiable — never proceed on main/master.**

---

### Locate Plan

If plan path provided:
```bash
cat .local/state/code-foundations/plans/<provided-path>.md
```

If no path, list available:
```bash
ls -la .local/state/code-foundations/plans/*.md | head -20
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

### Skill Resolution (One-Time Task)

Before creating phase tasks, resolve skills for all phases. Skills affect gate policy (phases with Skills get Full gate), so this must run first.

1. `TaskCreate(subject: "SETUP: Skill Resolution", description: "Validate and resolve skill assignments for all phases.")`
2. Scan system-reminder for all available skills (exclude workflow commands: plan, building, debug, research)
3. For each phase, check the plan's `**Skills:**` field:
   - **Specific skills listed** → validate each exists in available skills. Warn on any missing.
   - **`none -- [reason]`** → evaluate phase goal and scope against available skills. If a strong match exists, suggest adding it. Log why `none` was kept or what was added.
   - **Field missing** → flag as plan defect (plan CHECK should have caught this). Add skills based on phase goal/scope.
4. Update the plan file's `**Skills:**` fields with resolved assignments
5. `TaskUpdate(status: "completed")`

**Output:** Resolved skill map logged in the task. Phase task creation uses these resolved skills for gate policy detection.

### Create Phase Tasks Upfront

For each phase N, run Model Auto-Detection and Gate Policy Detection (see below), then create tasks.

**Full gate (2 tasks):**

1. `TaskCreate(subject: "Phase N.1: BUILD - [phase name]", description: "Discovery + design + TDD. Model: [from plan or default].", activeForm: "Building Phase N")`
2. `TaskCreate(subject: "Phase N.2: REVIEW - [phase name]", description: "Post-gate review. Model: [from plan or default]. Must return PASS.", activeForm: "Reviewing Phase N")`

**Standard gate (1 task — REVIEW skipped, tests are the gate):**

1. `TaskCreate(subject: "Phase N.1: BUILD - [phase name]", description: "Discovery + design + TDD. Model: [from plan or default].", activeForm: "Building Phase N")`

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

### Sub-Phase N.1: BUILD (Discovery + Design + TDD)

## STOP. YOU CANNOT EXPLORE CODE, WRITE TESTS, OR IMPLEMENT DIRECTLY.

**TaskUpdate → in_progress, then dispatch the build agent.**

The build agent combines discovery, design, and TDD implementation in one pass. It writes a discovery file (for post-gate review), then implements via red-green cycle.

**Dispatch templates live in `references/dispatch-templates.md`.** Read the file once per build, then substitute placeholders for each phase.

| Gate | Template | Adds discovery file |
|------|----------|--------------------|
| Full | `§ FULL_BUILD` | Yes — write `.local/state/code-foundations/building/<plan-name>-phase-N-discovery.md` |
| Standard | `§ FULL_BUILD` | Yes — same template, gate policy differs at REVIEW |
| Minimal | `§ MINIMAL_BUILD` | No — skips discovery |

Substitute these placeholders in the chosen template:
- `[paste the Context section from the plan file ...]` → plan's `## Context`
- `[For Phase 1: ...] / [For Phase N>1: ...]` → progress block (see Goal-Anchoring Progress block below)
- `[paste phase description and file list from plan]` → plan phase block
- `[paste ALL DW items from the plan phase, verbatim:]` → every `- [ ] DW-N.X:` item from plan, unchanged
- `[if plan phase has **Skills:** field, include:]` → emit the Additional Skills block only when the plan has skills
- `[if plan has Assumptions with "Verify Before Phase: N", include:]` → emit the Assumption Verification block only when the plan has matching assumptions
- `[from plan's **Model:** field, or omit if not set]` → see Model Resolution above

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

**Use `references/dispatch-templates.md § REVIEW`.** Substitute the same placeholders as BUILD plus:
- `[list files from BUILD subagent]` → file list returned by the BUILD task
- `[Full/Standard gate only:] - Discovery + Design: ...` → include only when a discovery file exists; omit for Minimal gate

**After REVIEW:**
1. Read the review file
2. If PASS → TaskUpdate → completed → commit (see Commit After Phase)
3. If FAIL → do NOT mark completed → follow Gate Failure Protocol

---

### Catch-Up REVIEW (inserted dynamically)

**Trigger:** Before executing any Full gate phase, check: have 2+ phases completed since the last REVIEW ran? If yes, insert a catch-up review before proceeding to the Full phase's BUILD.

This prevents drift across accumulated Standard/Minimal phases without per-phase overhead.

**Use `references/dispatch-templates.md § CATCHUP_REVIEW`.** Substitute placeholders:
- `[REVIEW model for the upcoming Full phase]` → resolved from the upcoming Full phase's model (see Model Resolution above)
- `[For each accumulated phase:]` → emit one block per phase since the last REVIEW, with that phase's DW items and files changed

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
Plan: .local/state/code-foundations/plans/[plan-file].md
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
- [x] BUILD: Discovery + design + TDD implementation complete
- [x] REVIEW: Verification passed [or "SKIPPED — tests are gate" or "Covered by catch-up review"]
- [x] Committed
Commit: [hash]
Summary: [1 sentence — what this phase delivered and what state it left the codebase in]
```

**The Summary line is critical for goal anchoring.** It feeds into the `## Progress` block of subsequent subagent dispatch prompts, giving later phases context about what earlier phases accomplished.

**State:** "Phase N complete. Committed. Proceeding to Phase N+1."

---

### Gate Failure Protocol

When a BUILD or REVIEW task returns FAIL, **read `references/gate-failure-protocol.md`** for the per-failure action table, retry-cap policy (max 3 failures per gate), and the user-escalation template.

**Hot-path summary:** failed task stays `in_progress`, never mark completed on FAIL, `blockedBy` prevents skipping. Re-dispatch up to 3 times. On the 3rd FAIL, STOP and escalate to the user — never silently retry a 4th time.

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

The summary is a **trust report**, not a status dashboard. Engineers need to verify what the AI built. Gate metadata (model, review results, epistemic status) lives in commit trailers; the trust report is derived from `git log`.

**Use `references/trust-report.md`** — it contains the trailer-dump commands and the report template (Build & Test Summary, Manual Testing Steps, Follow-up, Merge Instructions).

---

## Error Handling

For blockers beyond the per-phase Gate Failure Protocol, and for resuming a `blocked` plan, **read `references/build-failure-resume.md`**. It covers stop-and-document procedure, plan status update, user options on failure, and the resume checkpoint flow.

---

## Integration with /code-foundations:plan

For the chained plan→building flow, parallel-build pattern, plan-file model-override syntax, and thinking-effort guidance, **read `references/plan-integration.md`**.

**Key constraint (always applies):** parallel builds must target different plan files. Never run two building instances against the same plan.

---

## Chaining

- **RECEIVES FROM:** plan (via plan file), user with plan path
- **CHAINS TO:** code-foundations skills during execution
- **RELATED:** aposd-verifying-correctness, cc-quality-practices
