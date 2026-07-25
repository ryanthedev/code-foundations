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
- **Every phase gets reviewed, but not every phase blocks on it** — Full-gate and security-sensitive phases review immediately, before their commit; Standard and Minimal phases commit on green tests and are covered by a later batch REVIEW. Nothing ships unreviewed; the review just arrives after the commit instead of before it
- **The batch never goes stale** — it fires at the cadence, before any Full phase, and once before VERIFY. An un-reviewed phase cannot reach the trust report
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
11. **Security-sensitive flags** - Optional `**Security-sensitive:** yes` per phase (forces an immediate 3-sample REVIEW majority vote — never deferred into a batch)
12. **Review cadence** - `**Review cadence:** N` in the plan header (how many un-reviewed phases may accumulate before a batch REVIEW fires). Missing or unparseable → default to 3 and say so once

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

Determine the gate level for each phase. The gate controls two things: how much rigor the BUILD gets, and **whether REVIEW blocks the commit or is deferred into a batch**. Every phase is still reviewed — the question is only when.

| Level | Sub-Phases | Review timing | When |
|---|---|---|---|
| **Full** | BUILD → REVIEW → commit | **Blocking** — commit waits for PASS | High-risk work where errors cascade; the heavyweight tier, and the home of security 3-sample REVIEW |
| **Standard** | BUILD → commit | **Deferred** — covered by the next batch REVIEW | Medium work; tests gate the commit, the batch catches what tests can't (missed edge cases, gaps, gotchas) |
| **Minimal** | BUILD (minimal) → commit | **Deferred** — same batch | Trivial docs/config work; no discovery phase |
| **Batch** | REVIEW over all un-reviewed committed phases | — | Fires at the cadence, before any Full phase, and once before VERIFY |

**Security-sensitive overrides the gate's timing.** A phase carrying `**Security-sensitive:** yes` reviews immediately (3-sample, before its commit) whatever its gate says. Security defects that sit un-reviewed across three more phases are exactly the ones that get expensive.

**Why deferral is safe and blocking is not free.** The commit is a rollback boundary, not a correctness claim — a green suite is enough to earn one. Batching trades a small window of un-reviewed HEAD for reviewer context: a reviewer seeing three related phases at once catches cross-phase incoherence that three isolated per-phase reviews structurally cannot. The cost is real and worth naming: a batch FAIL means fixing forward on committed code instead of gating before commit (see Gate Failure Protocol → Batch Failures).

**Resolution order** (first match wins):

1. **Pipeline override (topmost):** `**Pipeline:** full` forces Full. `**Pipeline:** direct` forces Minimal.
2. **Plan-declared gate:** use the phase's `**Gate:**` field verbatim — `Full`, `Standard`, or `Minimal`. The planner sets this at SAVE with the risk context in hand; the decision is visible and reviewable in the plan file. The field is required — a phase without it stops the build at LOAD.

Skill presence does NOT affect the gate — every phase carries skills (see Skill Resolution), so skills cannot discriminate gate level.

**State the resolved gate level when creating tasks:** "Phase N gate: [Full/Standard/Minimal] (reason: plan `**Gate:**` field | pipeline override)"

### Review Cadence

Gate is per phase; cadence is per plan. Read `**Review cadence:** N` from the plan header — how many deferred-review phases may accumulate before a batch REVIEW fires. **Default 3** when absent.

| N | Behavior |
|---|---|
| 1 | Every Standard/Minimal phase reviews right after its commit — closest to blocking, one phase per batch |
| 2–3 | The intended range. 3 is the default |
| 4–5 | Looser. The ceiling is reviewer recall, not policy: a batch review must run the suite and verify every DW item across every covered phase, and per-item recall degrades as the item count climbs |
| >5 or unparseable | Clamp to 5, say so once, continue |

**State the cadence once at SETUP:** "Review cadence: N (batch REVIEW every N un-reviewed phases, before each Full phase, and before VERIFY)."

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
| **fable / opus + Minimal gate** | heavyweight effort on work trivial enough to skip discovery | "Phase N is [fable/opus] (judgment-heavy) but Minimal gate (no discovery, deferred review). Lower the model, raise the gate, or proceed as-is?" |

`sonnet` matches any gate and `Standard` matches any model — neither ever triggers the stop. **Proceed-as-is is always a valid answer** (the plan is the user's); the stop only surfaces the tension so it's a conscious choice, never silent. If the user adjusts the model or gate, apply it as a one-run override (announced like the gate/model resolutions) — a gate change re-enters Wave Derivation below with the new value. Run this check per phase; batch the questions if several phases mismatch.

### Wave Derivation

Derive the execution order from the plan's dependency DAG, not from file order:

1. **Topological layers:** group phases by `**Depends on:**` — a phase's layer is one past its deepest dependency.
2. **Co-scheduling rule** — two phases in the same layer share a wave only when ALL hold:
   - neither transitively depends on the other,
   - both declare `**File scope:**` and the globs are pairwise disjoint,
   - **both gates are Standard or Minimal, and neither phase is security-sensitive** (both of those review immediately and always run alone — high-risk by definition, and serial execution keeps the un-reviewed-set accounting well-defined),
   - the test suite does not use shared mutable resources (fixed ports, docker services, global test DBs, on-disk fixtures — evident from the test command or the plan's Notes). If it does, serialize: correct beats concurrent.

   (Seam consumption needs no separate check — a phase consuming another's Produces depends on it, which the dependency check already covers; the planner's CHECK enforces that invariant.)
3. **Wave width cap: 3** (foreground fan-out + orchestrator context budget). Wider layers split into consecutive waves in plan order. A Full-gate phase inside a layer forms its own single-phase wave, placed in plan order relative to the grouped waves.
4. Any doubt about independence → serialize within the layer in plan order. A phase without `File scope` never shares a wave.

**State the derived waves aloud before creating tasks:** "Wave 1: Phase 1. Wave 2: Phases 2, 3 in parallel (disjoint scopes). Wave 3: Phase 4." Waves are derived here, never stored in the plan — plan edits would leave stored wave numbers stale.

### Create Phase Tasks Upfront

For each phase N (using its resolved gate level and model):

- **Blocking-review phases — 2 tasks.** A phase reviews immediately when its gate is **Full** OR it carries `**Security-sensitive:** yes`. Create `Phase N.1: BUILD - [phase name]` (description: "Discovery + design + implementation. Model: [from plan].") and `Phase N.2: REVIEW - [phase name]` (description: "Blocking post-gate review. Model: [REVIEW model]. Must return PASS."), N.2 blockedBy N.1.
- **Deferred-review phases — 1 task.** Standard and Minimal gates (absent a security flag) get only `Phase N.1: BUILD - [phase name]` (description notes the gate and "review deferred to batch"). The commit follows a green suite; the batch covers it later.
- **Chaining follows the DAG:** each phase's BUILD task is blockedBy the last task of every phase it depends on — not the previous phase in file order. Same-wave phases share predecessors and no edges between each other.
- **Batch review tasks are NOT created upfront** — they are inserted dynamically when a batch trigger fires (evaluated at wave boundaries, where the completed-phase order is total).
- **Orchestrator handles commits directly** after each phase's last task completes — no commit tasks.

Example for a 5-phase plan at cadence 3 (Standard, two independent Standards, Minimal, Full):
```
Wave 1: Phase 1.1 BUILD → commit                        (1 un-reviewed)
Wave 2: Phase 2.1 BUILD ∥ Phase 3.1 BUILD (both blockedBy 1.1; disjoint File scopes)
        → integrate + commit in plan order              (3 un-reviewed → cadence hit)
        → BATCH REVIEW Phases 1-3 → PASS                (0 un-reviewed)
Wave 3: Phase 4.1 BUILD (Minimal) → commit              (1 un-reviewed)
Wave 4: batch check fires before the Full phase → BATCH REVIEW Phase 4 → PASS
        → Phase 5.1 BUILD → 5.2 REVIEW (blocking) → commit
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
   → If this is the phase's last task (REVIEW for blocking-review phases, BUILD for deferred ones): commit
   → If the phase's review was deferred, add it to the un-reviewed set
7. At the wave boundary, evaluate the batch trigger (see Batch REVIEW) before opening the next wave
8. Proceed to next task
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
4. Every wave member is a deferred-review phase by construction — Full gates and
   security-sensitive phases run alone, never in a wave. So DONE with a green suite is the
   integration signal; no REVIEW is dispatched into a phase worktree.
5. Integrate DONE phases strictly in plan order — a plan-order-earlier phase still working
   holds later finishers (the barrier applies to commits, not just wave opening; held
   finishers' worktrees simply wait unchanged — the step-7 integration run covers combined
   behavior):
     git cherry-pick -n <latest reported wip-sha> in the build worktree → real commit per
     commit-format.md → execution-log entry → copy the phase's discovery artifacts into
     the build worktree's .code-foundations/build/ → git worktree remove
   A cherry-pick conflict means the File scope declaration was violated: treat as a gate
   failure — drop that phase's WIP, re-dispatch its BUILD serially on top of current HEAD.
6. Every integrated member joins the un-reviewed set together (they landed in one wave), so
   a wave can trip the cadence on its own. Evaluate the batch trigger at step 8, once the
   wave has settled — never mid-integration, where the phase order isn't yet total.
7. Wave integration: after the last member commits, run the full test suite once in the build
   worktree — members were green in isolation but never tested together. Red → gate failure
   attributed to the last-integrated member, fix forward.
8. The next wave opens only when every member is committed, SKIPped, or escalated — then
   evaluate the batch trigger before opening it.
```

### Sub-Phase N.1: BUILD (Discovery + Design + Implementation)

BUILD work happens only inside the dispatched agent — the dispatcher rule above applies with full force here, where the temptation to "just fix it directly" is strongest.

TaskUpdate → in_progress, then dispatch the build agent. It combines discovery, design, and implementation (stub → implement → validate) in one pass.

**Dispatch templates live in `${CLAUDE_PLUGIN_ROOT}/references/dispatch-templates.md`.** Read the file once per build (the Substitution rules at the top govern all placeholders), then substitute per phase:

| Gate | Template | Discovery file |
|------|----------|----------------|
| Full | `§ FULL_BUILD` | Yes — `.code-foundations/build/<plan-name>-phase-N-discovery.md` |
| Standard | `§ FULL_BUILD` | Yes — same template and same discovery rigor; only the review timing differs |
| Minimal | `§ MINIMAL_BUILD` | No |

**After BUILD returns:**
1. Check status: DONE, SKIP, UPDATE_PLAN, or BLOCKED
2. If SKIP → mark task completed, skip REVIEW task if exists, **append a SKIP execution-log entry** to the plan file (the `### Phase N` entry from `commit-format.md` with BUILD/REVIEW/Committed lines replaced by a single `- [x] SKIPPED — [reason from build agent]` and no commit hash), then proceed to next phase
3. If UPDATE_PLAN → pause and ask user: the phase's requested change plus the build agent's one-sentence reason, not its raw report
4. If BLOCKED → do NOT mark completed → Gate Failure Protocol (BLOCKED is BUILD's failure status; the 3-retry cap applies)
5. If DONE → TaskUpdate → completed
6. If the phase's review is deferred (Standard or Minimal gate, no security flag) → commit now (see Commit After Phase) and add the phase to the un-reviewed set
7. If the phase's review is blocking (Full gate, or `**Security-sensitive:** yes` at any gate) → proceed to REVIEW

### Sub-Phase N.2: REVIEW (Blocking — Full gate and security-sensitive phases only)

This sub-phase exists only for phases whose review blocks the commit: **Full** gate, or any gate with `**Security-sensitive:** yes`. Standard and Minimal phases have no N.2 task — they are covered by Batch REVIEW below.

REVIEW dispatches only after the phase's BUILD task is completed — reviewing a moving target produces evidence against code that no longer exists.

TaskUpdate → in_progress, then dispatch `code-foundations:post-gate-agent` with `§ REVIEW`.

**The reviewer is a debiased independent critic — give it NO intent-framing.** Do NOT include the plan's Context, any Progress block, the discovery file, or any account of what the BUILD agent did or intended — intent-framing collapses defect detection. Requirements + files + commands only (the template enforces this).

**Security-sensitive phases** (`**Security-sensitive:** yes` in the plan): dispatch THREE independent REVIEW agents on **fable** as three Agent calls in a single message — they run concurrently; independence is contextual (separate contexts, zero intent-framing), not temporal. The prompts are identical EXCEPT for the per-sample review path: substitute `K`=1,2,3 into the `§ REVIEW` review-path placeholder so each sample writes a distinct `<plan>-phase-N-review-sample-K.md` (otherwise the samples race and overwrite each other). Each sample writes any artifacts it creates (coverage output, temp files) under a sample-unique scratch dir and never runs mutating commands. **Fallback:** if the suite uses shared mutable resources (DB, ports, docker services, on-disk fixtures), run the three samples sequentially instead — a correct slow vote beats a flaky fast one. Take the majority verdict; all three sample files are the record. On a majority PASS, the phase commit records `Review: pass (3-sample)` (not plain `pass`) so the heavier verification is auditable in the trailer history.

**After REVIEW:**
1. Read the review file
2. If PASS (or 2-of-3 for security-sensitive) → TaskUpdate → completed → commit
3. If FAIL → do NOT mark completed → Gate Failure Protocol

### Batch REVIEW (inserted dynamically)

The primary review path for Standard and Minimal phases. It runs against **committed** code, so it is a fix-forward gate rather than a commit gate — that is the trade the cadence buys.

**The un-reviewed set.** Track it across the build: every phase that commits with a deferred review joins it; a batch PASS empties it. Phases reviewed at their own gate (Full, security-sensitive) never enter it.

**Triggers** — evaluated at wave boundaries, where the completed-phase order is total (Full phases always run alone, so no boundary splits a Full phase). Fire a batch REVIEW when any holds:

| Trigger | Why |
|---|---|
| The un-reviewed set has reached the cadence N | The routine case |
| The next phase to open has a **Full** gate | Full phases are high-risk; they should build on reviewed ground rather than on an un-reviewed stack |
| VERIFY is next and the set is non-empty | The trailing sweep — no phase reaches the trust report unreviewed |

Dispatch with `§ BATCH_REVIEW` from the dispatch templates (model rule is in the template header). Cover **every** phase in the un-reviewed set in one dispatch — the cross-phase coherence check is the point, and splitting it forfeits that.

**After the batch:**

- **PASS** → empty the un-reviewed set, append a dated `Covered by batch review (phases X–Y)` addendum line to each covered phase's execution-log entry, then proceed.
- **FAIL** → Gate Failure Protocol → Batch Failures. The offending phases are already committed, so the fix lands as a forward commit, not a re-gated one. The set stays non-empty until a batch PASS clears it.

### Commit After Phase (Orchestrator Handles Directly)

After the phase's last task completes, **you commit directly** — no subagent, no task.

**Commit per `${CLAUDE_PLUGIN_ROOT}/references/commit-format.md`** (read once per build — it holds the recipe, message rules, the wave-member cherry-pick variant, and the execution-log entry format). Required trailers: `Phase:`, `Plan:`, `AI-Model:`, `AI-Epistemic-Status:`, `Gate-Policy:`, `Review:`. Wave members commit in plan order via the cherry-pick recipe; serial phases use the standard recipe.

Then append the phase's execution-log entry to the plan file. **Its Summary line feeds the `## Progress` block of later dispatch prompts** — write it as goal anchoring for subsequent phases, not as telemetry.

**State:** "Phase N complete. Committed. Proceeding to Phase N+1."

### Gate Failure Protocol

When a REVIEW task returns FAIL or a BUILD task returns BLOCKED, **read `${CLAUDE_PLUGIN_ROOT}/references/gate-failure-protocol.md`** for the per-failure action table and user-escalation template. The failed task stays `in_progress`; re-dispatch at most 3 times, then stop and escalate — never silently retry a 4th time.

---

## Phase 4: VERIFY (Full Test Suite)

### Trailing Batch REVIEW (first — before anything else in VERIFY)

If the un-reviewed set is non-empty, fire the trailing batch REVIEW now (see Batch REVIEW). VERIFY runs the suite; it does not review. An un-reviewed phase must not reach the trust report, because the report's whole claim is that a human can trust what the trailers say was verified.

### Load Skills

1. `Skill(code-foundations:performance-optimization)` — catch obvious performance regressions (O(n²), N+1 queries, unnecessary allocations)
2. `Skill(code-foundations:cc-refactoring-guidance)` — identify refactoring opportunities introduced during implementation

### Test Coverage Check

Verify against the plan's **Test Coverage** level: **100%** (unit tests for all new code + integration), **Targeted** (the layers the user named), **None** (skip, warn: technical debt), or **Per-phase** (check each phase's test notes). **If coverage falls short:** FAIL verification, require tests before proceeding.

### Run Test Plan + Clean Build

Execute each item from the plan's Test Plan section, then run a clean build and linter. No new warnings or lint errors — if uncertain whether a warning is pre-existing, disambiguate with `git stash && build && git stash pop`. Fix everything new before proceeding.

**Suite re-run delta rule:** skip the redundant full-suite re-run iff a full-suite run already executed **in the build worktree** after the last integration (the trailing batch REVIEW, a final blocking REVIEW, or the wave-integration run) AND no source has changed since — `git status` clean apart from the plan file and `.code-foundations/` artifacts (execution-log appends don't invalidate test evidence). Cite that run's output as the trust-report evidence. Anything else (final phase was Minimal, post-review fixes touched source) → run the suite once now. The Test Plan items, coverage check, and clean-build warning delta always run — no earlier step disambiguates pre-existing vs new warnings.

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
