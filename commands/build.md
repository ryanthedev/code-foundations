---
description: "Execute an approved plan through gated phases (BUILD → REVIEW → commit) with subagent dispatch. Use when a plan exists in .code-foundations/plans/ and the user wants it implemented — phased TDD execution, per-phase quality gates, orchestrator commits, and a final trust report."
---

# Skill: build

**Load Plan → Setup → Execute → Verify → Report**

---

## Crisis Invariants — NEVER SKIP

- **Worktree isolation** — never build on main/master; multi-phase commits there have no rollback
- **Load plan before coding** — no plan = no checklist = forgotten tasks
- **One section at a time** — parallel sections cause merge conflicts and lost context
- **BUILD before REVIEW** (Full/Standard gate) — Minimal gate phases skip discovery
- **Verification before commit, per gate policy** — Full: REVIEW must PASS; Standard/Minimal: tests are the gate
- **Independent verification on complex work only** — self-review is blind, but over-verifying trivial work injects noise
- **Mark complete only when gates pass** — premature completion ships unverified work
- **Update the execution log** — it debugs failed builds and anchors later phases

---

## Phase 1: LOAD (Read Plan File)

### Worktree Gate (MANDATORY — first check)

**Read `${CLAUDE_PLUGIN_ROOT}/references/worktree-gate.md`** and clear the gate before any other work: workspace-mode detection, worktree vs feature-branch creation, dependency setup, and record-keeping for REPORT. **Non-negotiable — never proceed on main/master.**

### Locate Plan

Read the provided plan path from `.code-foundations/plans/`. If no path was given, `ls .code-foundations/plans/*.md` and ask: "Which plan should I execute?"

### Parse Plan Structure

Extract from the plan file:
1. **Context** - What we're building (used for goal anchoring in BUILD dispatch prompts)
2. **Approach** - How we're building it
3. **Phases** - Implementation sections
4. **Done-when items per phase** - Every `- [ ]` under each phase's `**Done when:**` (passed verbatim to build and review agents)
5. **Test Coverage** - What level of tests required (100%, backend only, etc.)
6. **Test Plan** - Specific verification criteria
7. **Model overrides** - Optional `**Model:** <model>` per phase
8. **Pipeline overrides** - Optional `**Pipeline:** direct` per phase
9. **Assumptions** - Assumptions table with `Verify Before Phase` timing
10. **Security-sensitive flags** - Optional `**Security-sensitive:** yes` per phase (triggers 3-sample REVIEW majority vote)

**If Test Coverage is missing:** Default to "100% coverage" and inform user.

### Verify Plan is Ready

| Plan status | Action |
|-------------|--------|
| `ready` | Proceed |
| `in-progress` | Resume from last checkpoint |
| `complete` | Ask: "Plan already complete. Re-execute or archive?" |
| `blocked` | Show blockers, ask how to proceed |

---

## Phase 2: SETUP (Initialize Tracking)

### Update Plan Status

Set in the plan file: `**Status:** in-progress`, `**Started:** YYYY-MM-DD HH:MM`, `**Current Phase:** 1`.

### Skill Resolution (One-Time Task)

Before creating phase tasks, resolve skills for all phases. Skills affect gate policy (phases with Skills get Full gate), so this must run first.

1. `TaskCreate(subject: "SETUP: Skill Resolution", description: "Validate and resolve skill assignments for all phases.")`
2. Scan system-reminder for all available skills — read every skill's description and trigger conditions. Exclude workflow commands (plan, build, debug, research, code-standards, clarify).
3. For each phase, check the plan's `**Skills:**` field:
   - **Specific skills listed** → validate each exists in available skills. If a skill name doesn't match any available skill, STOP and ask the user before proceeding.
   - **`none -- [reason]`** → compare phase goal and scope against every available skill's description. If a skill's triggers match the phase work, add it. Every phase MUST have at least one skill — skills exist for code, documentation, design, and more.
   - **Field missing** → flag as plan defect. Add skills by matching phase goal/scope against available skill descriptions.
4. **Resolve checklist paths** for every assigned skill in one pass — use `find`, NOT shell globs (zsh aborts the whole command on an unmatched glob):
   ```bash
   find ${CLAUDE_PLUGIN_ROOT}/skills/<name-1> ${CLAUDE_PLUGIN_ROOT}/skills/<name-2> ... \( -name 'checklists.md' -o -path '*/checklists/*.md' \)
   ```
   A skill resolves to its single `checklists.md`, every `.md` under its `checklists/` directory, or nothing — some skills have no checklist files; those get only their `Skill()` line in dispatch prompts. Record the resolved path(s) per skill — dispatch prompts emit them as explicit `Read()` lines.
5. Update the plan file's `**Skills:**` fields with resolved assignments.
6. `TaskUpdate(status: "completed")`

**CRITICAL: Re-read the plan file after Skill Resolution completes.** The plan was modified in step 5. All subsequent steps (gate policy detection, phase task creation, dispatch) MUST use the updated plan state — not the version from LOAD.

### Model Resolution

Use the `**Model:**` field from the plan if present. If not specified, omit the model parameter for both BUILD and REVIEW — the agent runs on whatever model is active.

If the plan specifies a model, downgrade REVIEW one tier (prover-verifier asymmetry — intentional):

| BUILD model | REVIEW model |
|-------------|--------------|
| opus | sonnet |
| sonnet | haiku |
| haiku | haiku (floor) |

### Gate Policy Detection

Determine the gate level for each phase. This controls which sub-phases run. Non-uniform verification beats uniform: heavy gates on risky work, tests-as-gate on the rest.

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

**State the resolved gate level when creating tasks:** "Phase N gate: [Full/Standard/Minimal] (reason: [auto/plan override])"

### Create Phase Tasks Upfront

For each phase N (using its resolved gate level and model):

- **Full gate — 2 tasks:** `Phase N.1: BUILD - [phase name]` (description: "Discovery + design + TDD. Model: [from plan or default].") and `Phase N.2: REVIEW - [phase name]` (description: "Post-gate review. Model: [REVIEW model]. Must return PASS."), N.2 blockedBy N.1.
- **Standard/Minimal gate — 1 task:** `Phase N.1: BUILD - [phase name]` (Minimal description notes "Implement from plan description (minimal gate)").
- **Chaining:** next phase's first task blockedBy this phase's last task.
- **Catch-up review tasks are NOT created upfront** — they are inserted dynamically when the catch-up trigger fires.
- **Orchestrator handles commits directly** after each phase's last task completes — no commit tasks.

Example for a 3-phase plan (Full + Minimal + Full):
```
Phase 1.1 BUILD → Phase 1.2 REVIEW (blockedBy 1.1) → Phase 2.1 BUILD (blockedBy 1.2)
  → Phase 3.1 BUILD (blockedBy 2.1, catch-up check fires here) → Phase 3.2 REVIEW (blockedBy 3.1)
```

---

## Phase 3: EXECUTE (Implement Sections)

### CRITICAL: DO NOT DO ANYTHING DIRECTLY

**You MUST dispatch subagents for ALL work. DO NOT:**
- Read/explore code files directly during build
- Edit code files directly during build
- Skip any task
- Proceed when a blockedBy dependency is not completed
- Mark a gate task completed when it returned FAIL

**Exception: You DO handle commits directly** — no subagent needed for git operations.

### Agent Types Per Sub-Phase

| Sub-Phase | Agent Type |
|-----------|-----------|
| N.1 BUILD | `code-foundations:build-agent` |
| N.2 REVIEW | `code-foundations:post-gate-agent` |
| Commit | Orchestrator (you) |

**Gates load ONLY per-phase skills.** Each agent definition carries its own protocol and works with zero skills assigned. Skills arrive exclusively via the dispatch prompt's `## Additional Skills` block — construction rules and BUILD→REVIEW skill propagation live in the dispatch-templates Substitution rules.

### Execution Loop

All tasks were created in SETUP. Execute them in order. For each task:

```
1. TaskGet(task_id) → verify blockedBy list is empty (all predecessors completed)
2. TaskUpdate(task_id, status: "in_progress")
3. Dispatch subagent (see sub-phases below)
4. Wait for completion
5. If result is FAIL → do NOT mark completed → Gate Failure Protocol
6. If success → TaskUpdate(task_id, status: "completed")
   → If this is the phase's last task (REVIEW for Full, BUILD for Standard/Minimal): commit
7. Proceed to next task
```

### Sub-Phase N.1: BUILD (Discovery + Design + TDD)

## STOP. YOU CANNOT EXPLORE CODE, WRITE TESTS, OR IMPLEMENT DIRECTLY.

TaskUpdate → in_progress, then dispatch the build agent. It combines discovery, design, and TDD implementation in one pass.

**Dispatch templates live in `${CLAUDE_PLUGIN_ROOT}/references/dispatch-templates.md`.** Read the file once per build (the Substitution rules at the top govern all placeholders), then substitute per phase:

| Gate | Template | Discovery file |
|------|----------|----------------|
| Full | `§ FULL_BUILD` | Yes — `.code-foundations/build/<plan-name>-phase-N-discovery.md` |
| Standard | `§ FULL_BUILD` | Yes — same template, gate differs at REVIEW |
| Minimal | `§ MINIMAL_BUILD` | No |

**After BUILD returns:**
1. Check status: DONE, SKIP, UPDATE_PLAN, or BLOCKED
2. If SKIP → mark task completed, skip REVIEW task if exists, proceed to next phase
3. If UPDATE_PLAN → pause and ask user
4. If BLOCKED → do NOT mark completed → debug and re-dispatch or escalate
5. If DONE → TaskUpdate → completed
6. If Standard/Minimal gate → commit now (see Commit After Phase)
7. If Full gate → proceed to REVIEW

### Sub-Phase N.2: REVIEW (Post-Gate)

## STOP. Verify BUILD task is completed before proceeding.

TaskUpdate → in_progress, then dispatch `code-foundations:post-gate-agent` with `§ REVIEW`.

**The reviewer is a debiased independent critic — give it NO intent-framing.** Do NOT include the plan's Context, any Progress block, the discovery file, or any account of what the BUILD agent did or intended — intent-framing collapses defect detection. Requirements + files + commands only (the template enforces this).

**Security-sensitive phases** (`**Security-sensitive:** yes` in the plan): dispatch THREE independent REVIEW agents with the identical prompt (separate Agent calls — independence is the point), take the majority verdict, record all three in the execution log.

**After REVIEW:**
1. Read the review file
2. If PASS (or 2-of-3 for security-sensitive) → TaskUpdate → completed → commit
3. If FAIL → do NOT mark completed → Gate Failure Protocol

### Catch-Up REVIEW (inserted dynamically)

**Trigger:** before any Full gate phase's BUILD, check: have 2+ phases run since the last REVIEW? If yes, insert a catch-up review first using `§ CATCHUP_REVIEW` (model rule is in the template header). This prevents drift across accumulated Standard/Minimal phases without per-phase overhead.

- PASS → proceed to the Full phase's BUILD
- FAIL → Gate Failure Protocol before proceeding

### Commit After Phase (Orchestrator Handles Directly)

After the phase's last task completes, **you commit directly** — no subagent, no task.

**Commit per `${CLAUDE_PLUGIN_ROOT}/references/commit-format.md`** (read once per build — it holds the recipe, message rules, and execution-log entry format). Required trailers: `Phase:`, `Plan:`, `AI-Model:`, `AI-Epistemic-Status:`, `Gate-Policy:`, `Review:`.

Then append the phase's execution-log entry to the plan file. **Its Summary line feeds the `## Progress` block of later dispatch prompts** — write it as goal anchoring for subsequent phases, not as telemetry.

**State:** "Phase N complete. Committed. Proceeding to Phase N+1."

### Gate Failure Protocol

When a BUILD or REVIEW task returns FAIL, **read `${CLAUDE_PLUGIN_ROOT}/references/gate-failure-protocol.md`** for the per-failure action table and user-escalation template. The failed task stays `in_progress`; re-dispatch at most 3 times, then STOP and escalate — never silently retry a 4th time.

---

## Phase 4: VERIFY (Full Test Suite)

### Load Skills

1. `Skill(code-foundations:performance-optimization)` — catch obvious performance regressions (O(n²), N+1 queries, unnecessary allocations)
2. `Skill(code-foundations:cc-refactoring-guidance)` — identify refactoring opportunities introduced during implementation

### Test Coverage Check

Verify against the plan's **Test Coverage** level: **100%** (unit tests for all new code + integration), **Backend only**, **Backend + frontend**, **None** (skip, warn: technical debt), or **Per-phase** (check each phase's test notes). **If coverage falls short:** FAIL verification, require tests before proceeding.

### Run Test Plan + Clean Build

Execute each item from the plan's Test Plan section, then run a clean build and linter. No new warnings or lint errors — if uncertain whether a warning is pre-existing, disambiguate with `git stash && build && git stash pop`. Fix everything new before proceeding.

### Verification Gate

| Condition | Action |
|-----------|--------|
| All tests pass, coverage met, build clean, no skipped tasks | Proceed to REPORT |
| Tests fail | Debug, fix, re-verify |
| Build warnings/errors introduced | Fix, rebuild, re-verify |
| Tests missing (but required by coverage level) | Write tests, then re-verify |
| Coverage = None | Warn "Skipping tests per plan. Technical debt noted." and proceed |

---

## Phase 5: REPORT (Update Plan + Summarize)

### Update Plan File

Set `**Status:** complete`, `**Completed:** YYYY-MM-DD HH:MM`, `**Duration:** [start → complete]`. The execution log is already populated per-phase at commit time.

### Summary Output (Trust Report)

The summary is a **trust report**, not a status dashboard — engineers need to verify what the AI built. Gate metadata lives in commit trailers; **use `${CLAUDE_PLUGIN_ROOT}/references/trust-report.md`** for the trailer-dump commands and report template (Build & Test Summary, Manual Testing Steps, Follow-up, Merge Instructions).

---

## Error Handling

For blockers beyond the per-phase Gate Failure Protocol, and for resuming a `blocked` plan, **read `${CLAUDE_PLUGIN_ROOT}/references/build-failure-resume.md`**: stop-and-document procedure, plan status update, user options on failure, resume checkpoint flow.

---

## Integration with /code-foundations:plan

For the chained plan→build flow, parallel-build pattern, plan-file model-override syntax, and thinking-effort guidance, **read `${CLAUDE_PLUGIN_ROOT}/references/plan-integration.md`**.

**Key constraint (always applies):** parallel builds must target different plan files. Never run two build instances against the same plan.
