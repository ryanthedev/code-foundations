---
description: "Execute an approved plan through gated phases (BUILD → REVIEW → commit) with subagent dispatch. Use when a plan exists in .code-foundations/plans/ and the user wants it implemented — phased implementation, per-phase quality gates, orchestrator commits, and a final trust report."
---

# Command: build

**Load Plan → Setup → Execute → Verify → Report**

---

## Invariants

Each of these exists because its absence has a specific failure mode:

- **Worktree isolation** — building on main/master leaves multi-phase commits with no rollback boundary
- **Load plan before coding** — no plan means no checklist, and unlisted tasks get forgotten
- **One wave at a time** — phases run in parallel only when the plan declares them independent (`Depends on` + disjoint `File scope`) and each runs in its own phase worktree; same-tree parallel execution contaminates test evidence and causes merge conflicts. The commit is the phase boundary — nothing downstream starts before it exists
- **BUILD before REVIEW** (Full and Standard gates) — REVIEW runs on every phase except Minimal; Minimal skips both REVIEW and discovery
- **Verification before commit, per gate policy** — Full/Standard: REVIEW must PASS; Minimal: tests are the gate
- **Independent verification on complex work only** — self-review is blind, but over-verifying trivial work injects noise
- **Mark complete only when gates pass** — premature completion ships unverified work
- **Update the execution log** — it debugs failed builds and anchors later phases

---

## Phase 1: LOAD (Read Plan File)

### Locate Plan

Read the provided plan path from `.code-foundations/plans/`. If no path was given, `ls .code-foundations/plans/*.md` and ask: "Which plan should I execute?"

### Worktree Gate (immediately after the plan is located — it needs the plan filename)

**Read `${CLAUDE_PLUGIN_ROOT}/references/worktree-gate.md`** and clear the gate before any other work: workspace-mode detection, worktree vs feature-branch creation, dependency setup, and record-keeping for REPORT. Never proceed on main/master — commits there have no rollback boundary. Throughout this document, "build worktree" means the build workspace this gate produced — the worktree, or the feature-branch checkout in feature-branch mode.

### Parse Plan Structure

Extract from the plan file:
1. **Context** - What we're building (used for goal anchoring in BUILD dispatch prompts)
2. **Approach** - How we're building it
3. **Phases** - Implementation sections
4. **Done-when items per phase** - Every `- [ ]` under each phase's `**Done when:**` (passed verbatim to build and review agents)
5. **Test Coverage** - What level of tests required (100%, targeted, etc.)
6. **Test Plan** - Specific verification criteria
7. **Model per phase** - `**Model:** <model>` (required on every phase)
8. **Gate per phase** - `**Gate:**` (required on every phase); optional `**Pipeline:**` override
9. **Dependencies** - `**Depends on:**` per phase (required) and optional `**File scope:**` globs — these drive wave derivation
10. **Assumptions** - Assumptions table with `Verify Before Phase` timing
11. **Security-sensitive flags** - Optional `**Security-sensitive:** yes` per phase (triggers 3-sample REVIEW majority vote)

**Required fields:** every phase must carry `**Model:**`, `**Gate:**`, and `**Depends on:**`. If any is missing, stop and tell the user to re-run `/code-foundations:plan` — plans are ephemeral per-feature artifacts and the planner always emits these fields; a plan without them wasn't produced by the pipeline. **If Test Coverage is missing:** default to "100% coverage" and inform user.

### Verify Plan is Ready

| Plan status | Action |
|-------------|--------|
| `draft` | **Stop.** The plan was never confirmed by the user — the planner flips draft → ready only after the user approves the presented plan. Tell the user to finish `/code-foundations:plan` |
| `ready` | Proceed |
| `in-progress` | Resume: derive completed phases from the execution log + commit trailers, re-run SETUP task creation for the remainder, continue from the first incomplete phase |
| `complete` | Ask: "Plan already complete. Re-execute or archive?" |
| `blocked` | Show blockers as a short bulleted list (one line each), ask how to proceed |
| missing or unrecognized | Treat as `draft` — stop and send the user back to `/code-foundations:plan` |

---

## Phase 2: SETUP (Initialize Tracking)

### Update Plan Status

Set in the plan file: `**Status:** in-progress`, `**Started:** YYYY-MM-DD HH:MM`, `**Current Phase:** 1`.

### Skill Resolution (One-Time Task)

Before creating phase tasks, resolve skills for all phases. Skills do NOT affect gate policy — every phase carries at least one skill, so skill presence cannot discriminate gate level (gate is keyed off the plan's `**Gate:**` field). Resolving skills first still matters: every phase needs a validated, invocable skill set before dispatch.

1. `TaskCreate(subject: "SETUP: Skill Resolution", description: "Validate and resolve skill assignments for all phases.")`
2. Scan your available-skills register — every skill in context: the internal code-foundations skills (now `user-invocable: false`, so model-discoverable) plus any external plugin skills. Read each candidate's description and trigger conditions. Exclude workflow commands and pipeline skills (plan, build, debug, research, code-standards, clarify, planning).
3. For each phase, check the plan's `**Skills:**` field:
   - **Specific skills listed** → validate each is a real available skill (internal or external). If a name doesn't match any available skill, STOP and ask the user before proceeding.
   - **`none -- [reason]`** → compare phase goal and scope against every available skill's description. If a skill's triggers match the phase work, add it. Every phase MUST have at least one skill — skills exist for code, documentation, design, and more.
   - **Field missing** → flag as plan defect. Add skills by matching phase goal/scope against available skill descriptions.
4. Update the plan file's `**Skills:**` fields with the validated set, each recorded by its **invocable name**: internal skills may stay bare (`cc-debugging`) or qualified (`code-foundations:cc-debugging`); external skills MUST keep their plugin prefix (`oberskills:skill-craft`). Dispatch emits one `Skill(<plugin:name>)` per skill (bare internal names get the `code-foundations:` prefix), and each skill self-loads its own checklists when invoked — so there are no checklist paths to resolve here.
5. `TaskUpdate(status: "completed")`

**Re-read the plan file after Skill Resolution completes** — step 4 modified it, and every subsequent step (gate policy detection, wave derivation, phase task creation, dispatch) must use the updated plan state, not the stale version from LOAD. Skipping this re-read is how dispatches go out with the pre-resolution skill set.

### Model Resolution

Every phase's `**Model:**` field is required (see LOAD). BUILD uses it directly; REVIEW runs one tier below, **floored at sonnet** (prover-verifier asymmetry — intentional):

| BUILD model | REVIEW model |
|-------------|--------------|
| fable | sonnet |
| opus | sonnet |
| sonnet | sonnet (floor) |
| haiku | sonnet (floor) |

**Why the sonnet floor (never haiku):** the model-tier benchmark (round 2, 2026-07) found haiku's planted-defect recall unreliable on REVIEW-shaped tasks — it missed *every* planted defect (0/5) on one review task where higher tiers caught them. A reviewer that misses defects is false insurance, so REVIEW never runs below sonnet even when BUILD does. For a sonnet-built phase the reviewer is the same tier; independence is preserved the way it always has been here — by the intent-stripped dispatch (no plan context, no progress narrative; see § REVIEW debiasing), not by the tier gap.

**Exception:** security-sensitive phases run their 3-sample REVIEW on **fable** regardless of the BUILD model — for security, verification rigor beats cost asymmetry.

### Gate Policy Detection

Determine the gate level for each phase. This controls which sub-phases run. REVIEW runs on every phase except Minimal — tests passing is not sufficient grounds to skip it, because tests don't catch missed edge cases, gaps, or gotchas; REVIEW does. Rigor is non-uniform: Full adds the heavyweight extras (catch-up anchoring, security 3-sample) on top of REVIEW; Standard runs a single-sample REVIEW; only trivial Minimal work rides on tests alone.

| Level | Sub-Phases | When |
|---|---|---|
| **Full** | BUILD → REVIEW → commit | High-risk work where errors cascade; the heavyweight tier — adds catch-up anchoring and is the home of security 3-sample REVIEW |
| **Standard** | BUILD → REVIEW → commit | Medium work; a single-sample REVIEW still runs — tests alone don't surface missed edge cases or gaps |
| **Minimal** | BUILD (minimal) → commit | Trivial docs/config work only; tests are the gate, no REVIEW, no design phase |
| **Catch-up** | Batch REVIEW inserted before next Full phase | Prevents drift across accumulated Minimal phases (the only un-reviewed tier) |

**Resolution order** (first match wins):

1. **Pipeline override (topmost):** `**Pipeline:** full` forces Full. `**Pipeline:** direct` forces Minimal.
2. **Plan-declared gate:** use the phase's `**Gate:**` field verbatim — `Full`, `Standard`, or `Minimal`. The planner sets this at SAVE with the risk context in hand; the decision is visible and reviewable in the plan file. The field is required — a phase without it stops the build at LOAD.

Skill presence does NOT affect the gate — every phase carries skills (see Skill Resolution), so skills cannot discriminate gate level.

**State the resolved gate level when creating tasks:** "Phase N gate: [Full/Standard/Minimal] (reason: plan `**Gate:**` field | pipeline override)"

### Effort Alignment

BUILD-agent depth is derived from the phase's `**Model:**` — the same field that already encodes how much thinking the work needs — and applied through the dispatch's depth-steering wording (the Agent tool has no `effort` parameter; see § FULL_BUILD / § MINIMAL_BUILD / § REVIEW and `references/plan-integration.md`):

| Phase Model | BUILD depth | REVIEW depth |
|---|---|---|
| fable / opus / sonnet | Think carefully | Think carefully |
| haiku | Answer directly | Think carefully — REVIEW never drops below (mirrors Model Resolution's sonnet floor; a reviewer that skims misses defects) |

**Mismatch stop — ask the user (only when Model and Gate disagree).** Normally a phase's `**Model:**` (effort) and `**Gate:**` (rigor) agree, and build proceeds silently with the depth above. When they *don't*, the phase's effort doesn't match its risk — STOP and ask the user to reconcile before dispatching that phase, the same way an unknown skill stops at Skill Resolution. Only these two combinations trigger it:

| Mismatch | Reads as | Ask |
|---|---|---|
| **haiku + Full gate** | mechanical effort on high-risk work | "Phase N is haiku (mechanical) but Full gate (high-risk). Raise the model, lower the gate, or proceed as-is?" |
| **fable / opus + Minimal gate** | heavyweight effort on trivial, un-reviewed work | "Phase N is [fable/opus] (judgment-heavy) but Minimal gate (no REVIEW). Lower the model, raise the gate, or proceed as-is?" |

`sonnet` matches any gate and `Standard` matches any model — neither ever triggers the stop. **Proceed-as-is is always a valid answer** (the plan is the user's); the stop only surfaces the tension so it's a conscious choice, never silent. If the user adjusts the model or gate, apply it as a one-run override (announced like the gate/model resolutions) — a gate change re-enters Wave Derivation below with the new value. Run this check per phase; batch the questions if several phases mismatch.

### Wave Derivation

Derive the execution order from the plan's dependency DAG, not from file order:

1. **Topological layers:** group phases by `**Depends on:**` — a phase's layer is one past its deepest dependency.
2. **Co-scheduling rule** — two phases in the same layer share a wave only when ALL hold:
   - neither transitively depends on the other,
   - both declare `**File scope:**` and the globs are pairwise disjoint,
   - **both gates are Standard or Minimal** (Full-gate phases always run alone — they're high-risk by definition, and serial execution keeps catch-up accounting well-defined),
   - the test suite does not use shared mutable resources (fixed ports, docker services, global test DBs, on-disk fixtures — evident from the test command or the plan's Notes). If it does, serialize: correct beats concurrent.

   (Seam consumption needs no separate check — a phase consuming another's Produces depends on it, which the dependency check already covers; the planner's CHECK enforces that invariant.)
3. **Wave width cap: 3** (foreground fan-out + orchestrator context budget). Wider layers split into consecutive waves in plan order. A Full-gate phase inside a layer forms its own single-phase wave, placed in plan order relative to the grouped waves.
4. Any doubt about independence → serialize within the layer in plan order. A phase without `File scope` never shares a wave.

**State the derived waves aloud before creating tasks:** "Wave 1: Phase 1. Wave 2: Phases 2, 3 in parallel (disjoint scopes). Wave 3: Phase 4." Waves are derived here, never stored in the plan — plan edits would leave stored wave numbers stale.

### Create Phase Tasks Upfront

For each phase N (using its resolved gate level and model):

- **Full / Standard gate — 2 tasks:** `Phase N.1: BUILD - [phase name]` (description: "Discovery + design + implementation. Model: [from plan].") and `Phase N.2: REVIEW - [phase name]` (description: "Post-gate review. Model: [REVIEW model]. Must return PASS."), N.2 blockedBy N.1.
- **Minimal gate — 1 task:** `Phase N.1: BUILD - [phase name]` (description notes "Implement from plan description (minimal gate)").
- **Chaining follows the DAG:** each phase's BUILD task is blockedBy the last task of every phase it depends on — not the previous phase in file order. Same-wave phases share predecessors and no edges between each other.
- **Catch-up review tasks are NOT created upfront** — they are inserted dynamically when the catch-up trigger fires (evaluated at wave boundaries, where the completed-phase order is total).
- **Orchestrator handles commits directly** after each phase's last task completes — no commit tasks.

Example for a 4-phase plan (Full + two independent Standards + Full):
```
Wave 1: Phase 1.1 BUILD → 1.2 REVIEW → commit
Wave 2: Phase 2.1 BUILD ∥ Phase 3.1 BUILD (both blockedBy 1.2; disjoint File scopes)
        → 2.2 REVIEW / 3.2 REVIEW as each BUILD finishes → integrate + commit in plan order
Wave 3: Phase 4.1 BUILD (blockedBy 2.2 AND 3.2; catch-up check fires here) → 4.2 REVIEW → commit
```

---

## Phase 3: EXECUTE (Implement Sections)

### The Orchestrator Dispatches; Agents Do the Work

You are the dispatcher. All exploration, implementation, and review happens in subagents — direct edits bypass the gates that make the trust report honest, and direct exploration fills the orchestration context with code the agents will re-read anyway. Concretely, during EXECUTE:

- Code reading, editing, and test-writing happen only inside dispatched agents
- Every task runs; a task is skipped only via a BUILD agent's SKIP status
- A task starts only when its blockedBy list is empty
- A gate task that returned FAIL is never marked completed

**Exception: you handle git directly** — worktree management, cherry-pick integration, commits, and the wave-integration test run need no subagent.

### Agent Types Per Sub-Phase

| Sub-Phase | Agent Type |
|-----------|-----------|
| N.1 BUILD | `code-foundations:build-agent` |
| N.2 REVIEW | `code-foundations:post-gate-agent` |
| Commit | Orchestrator (you) |

**Gates load ONLY per-phase skills.** Each agent definition carries its own protocol and works with zero skills assigned. Skills arrive exclusively via the dispatch prompt's `## Additional Skills` block — construction rules and BUILD→REVIEW skill propagation live in the dispatch-templates Substitution rules.

### Execution Loop

All tasks were created in SETUP. Execute wave by wave. **Single-phase waves run exactly the serial flow below; parallel waves add the worktree steps in the next section.**

Serial flow, per task:

```
1. TaskGet(task_id) → verify blockedBy list is empty (all predecessors completed)
2. TaskUpdate(task_id, status: "in_progress")
3. Dispatch subagent (see sub-phases below)
4. Wait for completion
5. If result is FAIL → do NOT mark completed → Gate Failure Protocol
6. If success → TaskUpdate(task_id, status: "completed")
   → If this is the phase's last task (REVIEW for Full/Standard, BUILD for Minimal): commit
7. Proceed to next task
```

### Parallel Waves (2-3 phases)

When a wave holds multiple phases, isolation is what makes it sound: BUILD and REVIEW agents run the test suite as their evidence, and two agents sharing a tree would each see the other's half-written code. **This procedure replaces serial-flow steps 3-7 for the wave's members** — in particular, commits are deferred to integration (step 5), never made immediately after a REVIEW.

```
1. For each member phase: git worktree add --detach .code-foundations/wave-worktrees/phase-N HEAD
   (run from the build worktree), then copy in what a fresh checkout lacks: the plan file,
   docs/code-standards.md if untracked, and run the dependency setup from worktree-gate.md
2. ONE message, one BUILD Agent call per phase (its plan **Model:**). Prompt additions to the
   template: "Work ONLY inside <worktree-root>; run all commands from there. End with exactly ONE
   commit: wip(phase-N): <name> — squash if you made more. Report the worktree path and wip sha."
3. Handle each BUILD status:
   - DONE → step 4.
   - SKIP → mark the task completed, append the SKIP execution-log entry, git worktree remove
     that phase's worktree. A SKIPped member counts as settled for step 8.
   - UPDATE_PLAN or BLOCKED from one member → let in-flight siblings finish, hold their
     worktrees uncommitted, then pause for the user.
4. As each BUILD returns DONE: Standard members get their REVIEW dispatched into that phase's
   worktree — same § REVIEW template with paths and commands rooted at the worktree, plus "run
   all commands from <worktree-root>" (debiasing is unchanged: a different directory is not
   intent-framing). Minimal members have no REVIEW — DONE with passing tests counts as PASSED.
5. Integrate PASSED phases strictly in plan order — a plan-order-earlier phase that is still
   failing holds later passers (the barrier applies to commits, not just wave opening; held
   passers' worktrees simply wait unchanged — the step-7 integration run covers combined
   behavior):
     git cherry-pick -n <latest reported wip-sha> in the build worktree → real commit per
     commit-format.md → execution-log entry → copy the phase's discovery/review artifacts into
     the build worktree's .code-foundations/build/ → git worktree remove
   A cherry-pick conflict means the File scope declaration was violated: treat as a gate
   failure — drop that phase's WIP, re-dispatch its BUILD serially on top of current HEAD.
6. FAILED phases: Gate Failure Protocol in their own worktree (see gate-failure-protocol.md
   Wave Failures); sync the worktree with build HEAD before each retry REVIEW; fixes are
   squashed into a fresh wip(phase-N) commit whose sha supersedes the old one.
7. Wave integration: after the last member commits, run the full test suite once in the build
   worktree — members were green in isolation but never tested together. Red → gate failure
   attributed to the last-integrated member, fix forward.
8. The next wave opens only when every member is committed, SKIPped, or escalated.
```

### Sub-Phase N.1: BUILD (Discovery + Design + Implementation)

BUILD work happens only inside the dispatched agent — the dispatcher rule above applies with full force here, where the temptation to "just fix it directly" is strongest.

TaskUpdate → in_progress, then dispatch the build agent. It combines discovery, design, and implementation (stub → implement → validate) in one pass.

**Dispatch templates live in `${CLAUDE_PLUGIN_ROOT}/references/dispatch-templates.md`.** Read the file once per build (the Substitution rules at the top govern all placeholders), then substitute per phase:

| Gate | Template | Discovery file |
|------|----------|----------------|
| Full | `§ FULL_BUILD` | Yes — `.code-foundations/build/<plan-name>-phase-N-discovery.md` |
| Standard | `§ FULL_BUILD` | Yes — same template; both Full and Standard proceed to REVIEW |
| Minimal | `§ MINIMAL_BUILD` | No |

**After BUILD returns:**
1. Check status: DONE, SKIP, UPDATE_PLAN, or BLOCKED
2. If SKIP → mark task completed, skip REVIEW task if exists, **append a SKIP execution-log entry** to the plan file (the `### Phase N` entry from `commit-format.md` with BUILD/REVIEW/Committed lines replaced by a single `- [x] SKIPPED — [reason from build agent]` and no commit hash), then proceed to next phase
3. If UPDATE_PLAN → pause and ask user: the phase's requested change plus the build agent's one-sentence reason, not its raw report
4. If BLOCKED → do NOT mark completed → Gate Failure Protocol (BLOCKED is BUILD's failure status; the 3-retry cap applies)
5. If DONE → TaskUpdate → completed
6. If Minimal gate → commit now (see Commit After Phase)
7. If Full or Standard gate → proceed to REVIEW

### Sub-Phase N.2: REVIEW (Post-Gate)

REVIEW dispatches only after the phase's BUILD task is completed — reviewing a moving target produces evidence against code that no longer exists.

TaskUpdate → in_progress, then dispatch `code-foundations:post-gate-agent` with `§ REVIEW`.

**The reviewer is a debiased independent critic — give it NO intent-framing.** Do NOT include the plan's Context, any Progress block, the discovery file, or any account of what the BUILD agent did or intended — intent-framing collapses defect detection. Requirements + files + commands only (the template enforces this).

**Security-sensitive phases** (`**Security-sensitive:** yes` in the plan): dispatch THREE independent REVIEW agents on **fable** as three Agent calls in a single message — they run concurrently; independence is contextual (separate contexts, zero intent-framing), not temporal. The prompts are identical EXCEPT for the per-sample review path: substitute `K`=1,2,3 into the `§ REVIEW` review-path placeholder so each sample writes a distinct `<plan>-phase-N-review-sample-K.md` (otherwise the samples race and overwrite each other). Each sample writes any artifacts it creates (coverage output, temp files) under a sample-unique scratch dir and never runs mutating commands. **Fallback:** if the suite uses shared mutable resources (DB, ports, docker services, on-disk fixtures), run the three samples sequentially instead — a correct slow vote beats a flaky fast one. Take the majority verdict; all three sample files are the record. On a majority PASS, the phase commit records `Review: pass (3-sample)` (not plain `pass`) so the heavier verification is auditable in the trailer history.

**After REVIEW:**
1. Read the review file
2. If PASS (or 2-of-3 for security-sensitive) → TaskUpdate → completed → commit
3. If FAIL → do NOT mark completed → Gate Failure Protocol

### Catch-Up REVIEW (inserted dynamically)

**Trigger:** evaluated at wave boundaries (where the completed-phase order is total, since Full phases always run alone): before a Full gate phase's BUILD — and once more before VERIFY, so trailing un-reviewed phases don't slip through — check whether 2+ committed phases carry the `Review: skipped (Minimal)` trailer since the last REVIEW. If yes, insert a catch-up review first using `§ CATCHUP_REVIEW` (model rule is in the template header). This prevents drift across accumulated Minimal phases — the only tier without per-phase REVIEW — without extra overhead. On PASS, append a dated `Covered by catch-up review` addendum line to each covered phase's execution-log entry.

- PASS → proceed to the Full phase's BUILD
- FAIL → Gate Failure Protocol before proceeding

### Commit After Phase (Orchestrator Handles Directly)

After the phase's last task completes, **you commit directly** — no subagent, no task.

**Commit per `${CLAUDE_PLUGIN_ROOT}/references/commit-format.md`** (read once per build — it holds the recipe, message rules, the wave-member cherry-pick variant, and the execution-log entry format). Required trailers: `Phase:`, `Plan:`, `AI-Model:`, `AI-Epistemic-Status:`, `Gate-Policy:`, `Review:`. Wave members commit in plan order via the cherry-pick recipe; serial phases use the standard recipe.

Then append the phase's execution-log entry to the plan file. **Its Summary line feeds the `## Progress` block of later dispatch prompts** — write it as goal anchoring for subsequent phases, not as telemetry.

**State:** "Phase N complete. Committed. Proceeding to Phase N+1."

### Gate Failure Protocol

When a REVIEW task returns FAIL or a BUILD task returns BLOCKED, **read `${CLAUDE_PLUGIN_ROOT}/references/gate-failure-protocol.md`** for the per-failure action table and user-escalation template. The failed task stays `in_progress`; re-dispatch at most 3 times, then stop and escalate — never silently retry a 4th time.

---

## Phase 4: VERIFY (Full Test Suite)

### Load Skills

1. `Skill(code-foundations:performance-optimization)` — catch obvious performance regressions (O(n²), N+1 queries, unnecessary allocations)
2. `Skill(code-foundations:cc-refactoring-guidance)` — identify refactoring opportunities introduced during implementation

### Test Coverage Check

Verify against the plan's **Test Coverage** level: **100%** (unit tests for all new code + integration), **Targeted** (the layers the user named), **None** (skip, warn: technical debt), or **Per-phase** (check each phase's test notes). **If coverage falls short:** FAIL verification, require tests before proceeding.

### Run Test Plan + Clean Build

Execute each item from the plan's Test Plan section, then run a clean build and linter. No new warnings or lint errors — if uncertain whether a warning is pre-existing, disambiguate with `git stash && build && git stash pop`. Fix everything new before proceeding.

**Suite re-run delta rule:** skip the redundant full-suite re-run iff a full-suite run already executed **in the build worktree** after the last integration (the final phase's REVIEW for serial builds, or the wave-integration run) AND no source has changed since — `git status` clean apart from the plan file and `.code-foundations/` artifacts (execution-log appends don't invalidate test evidence). Cite that run's output as the trust-report evidence. Anything else (final phase was Minimal, post-review fixes touched source) → run the suite once now. The Test Plan items, coverage check, and clean-build warning delta always run — no earlier step disambiguates pre-existing vs new warnings.

### Verification Gate

| Condition | Action |
|-----------|--------|
| All tests pass, coverage met, build clean, no unsanctioned skips (SKIPs via BUILD status are fine when their log entries exist) | Proceed to REPORT |
| Tests fail | Debug, fix, re-verify |
| Build warnings/errors introduced | Fix, rebuild, re-verify |
| Tests missing (but required by coverage level) | Write tests, then re-verify |
| Coverage = None | Warn "Skipping tests per plan. Technical debt noted." and proceed |

---

## Phase 5: REPORT (Update Plan + Summarize)

### Update Plan File

Set `**Status:** complete`, `**Completed:** YYYY-MM-DD HH:MM`, `**Duration:** [start → complete]`. The execution log is already populated per-phase at commit time.

### Final Commit

If VERIFY made any changes (debug fixes, added tests) or the plan file changed, commit them now: `chore(build): verification fixes + plan completion` with the standard trailers — otherwise the branch handed to the user is missing the fixes VERIFY made.

### Summary Output (Trust Report)

The summary is a **trust report**, not a status dashboard — engineers need to verify what the AI built. Gate metadata lives in commit trailers; **use `${CLAUDE_PLUGIN_ROOT}/references/trust-report.md`** for the trailer-dump commands and report template (Build & Test Summary, Manual Testing Steps, Follow-up, Merge Instructions).

---

## Error Handling

For blockers beyond the per-phase Gate Failure Protocol, and for resuming a `blocked` plan, **read `${CLAUDE_PLUGIN_ROOT}/references/build-failure-resume.md`**: stop-and-document procedure, plan status update, user options on failure, resume checkpoint flow.

---

## Integration with /code-foundations:plan

For the chained plan→build flow, parallel-build pattern, plan-file model-override syntax, and thinking-effort guidance, **read `${CLAUDE_PLUGIN_ROOT}/references/plan-integration.md`**.

**Key constraint (always applies):** parallel builds must target different plan files. Never run two build instances against the same plan.
