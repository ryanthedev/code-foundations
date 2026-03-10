# Plan: Live Review Preset for Building Pipeline

**Created:** 2026-03-10
**Status:** ready
**Complexity:** complex

---

## Context

The code review system (`/code-foundations:review`) currently offers two presets: `--sanity` (14 core checks, pre-commit) and `--pr` (614 checks, full PR review). Both operate as batch processes on already-written code. We need a third preset `--live` that runs incrementally during `/code-foundations:building` sessions, hooking into phase transitions to surface findings between IMPLEMENT and POST-GATE. This requires changes to the building skill's execution loop, new incremental review agents, and integration with the existing `add-finding.sh`/`add-verdict.sh` pipeline.

## Constraints

- Must not break existing `--sanity` or `--pr` presets
- Must not increase building phase duration by more than ~30 seconds per phase (review must be fast)
- Must reuse the existing `add-finding.sh` and `add-verdict.sh` schema pipeline -- no parallel output format
- Must not require changes to the post-gate-agent template (live review supplements post-gate, does not replace it)
- Findings must be actionable before POST-GATE runs, so the implementation agent can fix issues in-loop
- Must work with the existing TaskCreate/blockedBy enforcement model -- cannot break sub-phase chaining
- Live review is opt-in via `--live` flag on `/code-foundations:building`, not a default behavior change

## Chosen Approach

**Injected Sub-Phase Approach**

Add an optional `N.2b: LIVE-REVIEW` sub-phase between IMPLEMENT (N.2) and POST-GATE (N.3) in the building execution loop. When `--live` is active, the building orchestrator inserts this sub-phase into the TaskCreate chain. The live-review agent runs a targeted subset of checks (the 14 core sanity checks from `core-checklist.md`) against only the files changed in that phase, writes findings via `add-finding.sh`, and surfaces actionable issues. If findings exist, an optional fix loop dispatches back to the implementation agent before POST-GATE proceeds.

**Rationale:** This approach respects the existing TaskCreate/blockedBy enforcement model by inserting a new link in the chain rather than running review in parallel or outside the pipeline. It reuses proven infrastructure (core-checklist, add-finding.sh) rather than inventing a new review path. The 14-check subset keeps latency low while catching the highest-signal issues.

**Fallback:** If injecting a sub-phase proves too disruptive to the building skill's task creation logic, fall back to a post-IMPLEMENT hook that runs inline (same agent context) rather than as a dispatched sub-phase.

## Rejected Approaches

- **Parallel Background Review:** Run review concurrently with POST-GATE using a separate agent. Rejected because findings would arrive after POST-GATE has already started, creating race conditions in the findings pipeline and confusing the fix loop.
- **Event-Driven Watcher:** Implement a file-watcher that triggers review on every file save during IMPLEMENT. Rejected because Claude Code operates in a request-response model without persistent background processes, and the implementation agent's file saves are not observable events from the building orchestrator's perspective.

---

## Implementation Phases

### Phase 1: Live Review Agent Template
**Model:** sonnet

**Goal:** Create a new agent template (`live-review-agent.md`) that runs the 14 core sanity checks against a set of changed files and outputs findings via the existing `add-finding.sh` pipeline. This agent is the atomic unit that the building orchestrator will dispatch.

**Scope:**
- IN: Agent template file, core-checklist integration, add-finding.sh usage, output format
- OUT: Building skill modifications, command-line flag parsing, fix loop logic

**Constraints:**
- Agent must use `add-finding.sh` for all finding output -- no direct file writes for findings
- Agent must accept a file list and phase context as input (same pattern as post-gate-agent)
- Agent must complete within a single dispatch (no multi-turn interaction)

**Approach notes:**
- Use the 14 core checks from `core-checklist.md`, not the full 614-check PR set -- user chose speed over thoroughness for in-loop review
- Agent template should bake in the core-checklist content directly (same pattern as post-gate-agent bakes in its skills) rather than loading it via Skill tool

**File hints:**
- `agents/` -- where agent templates live; reference `post-gate-agent.md` for dispatch pattern
- `agents/core-checklist.md` -- the 14 checks to embed
- `agents/add-finding.sh` -- the schema-enforced output pipeline

**Depends on:** None | **Unlocks:** Phase 2, Phase 3

**Done when:**
- [ ] `agents/live-review-agent.md` exists with frontmatter, skill loading, input format, and output format
- [ ] Agent template references all 14 core checks
- [ ] Agent template uses `add-finding.sh` for finding output
- [ ] Output format includes phase context (phase number, changed files) for downstream consumption

**Difficulty:** MEDIUM
**Uncertainty:** Whether baking core-checklist content into the agent template (vs. referencing it) is the right pattern -- pre-gate should evaluate both during discovery

---

### Phase 2: Building Skill Live-Review Injection
**Model:** opus

**Goal:** Modify the building skill's execution loop to optionally inject a LIVE-REVIEW sub-phase (N.2b) between IMPLEMENT and POST-GATE when the `--live` flag is active. This is the core architectural change that threads live review into the building pipeline.

**Scope:**
- IN: Building skill execution loop modification, TaskCreate chain modification, sub-phase injection logic, model auto-detection for live-review sub-phase
- OUT: Command-line flag parsing (Phase 3), fix loop (Phase 4), live-review agent internals (Phase 1)

**Constraints:**
- When `--live` is not active, the execution loop must be identical to current behavior -- zero behavioral change for existing users
- The injected sub-phase must participate in the blockedBy chain: N.2b blockedBy N.2, N.3 blockedBy N.2b
- Must not change the 4-sub-phase naming convention for non-live builds (N.1 through N.4)
- Live-review sub-phase should use haiku model by default (14 checks on small file set = lightweight work)

**Approach notes:**
- Inject as "Phase N.2b: LIVE-REVIEW" rather than renumbering existing sub-phases -- user chose to avoid renumbering to maintain backward compatibility with existing execution logs and plan references
- The building skill's SETUP phase (Phase 2 in SKILL.md) creates all tasks upfront -- the injection must happen during task creation, not during execution

**File hints:**
- `skills/building/SKILL.md` -- the execution loop that needs modification (Phase 2: SETUP and Phase 3: EXECUTE sections)
- `commands/building.md` -- the command entry point that passes flags to the skill

**Depends on:** Phase 1 | **Unlocks:** Phase 3, Phase 4

**Done when:**
- [ ] Building skill SETUP creates 5 sub-phase tasks per phase when `--live` is active (N.1, N.2, N.2b, N.3, N.4)
- [ ] blockedBy chains include N.2b in the correct position
- [ ] Execution loop dispatches `live-review-agent` for N.2b sub-phases
- [ ] Non-live builds produce identical TaskCreate output to current behavior
- [ ] Model auto-detection documented for the new sub-phase

**Difficulty:** HIGH
**Uncertainty:** Whether the TaskCreate API supports "N.2b" naming or requires integer-only identifiers -- pre-gate must discover TaskCreate constraints

---

### Phase 3: Command Interface and Flag Routing
**Model:** sonnet

**Goal:** Add the `--live` flag to `/code-foundations:building` and route it through to the building skill's execution loop so users can opt in to live review.

**Scope:**
- IN: Command argument parsing, flag validation, flag propagation to the building skill
- OUT: Review command changes (live is building-only, not a review preset), UI/reporting changes

**Constraints:**
- `--live` is a building command flag, not a review command flag -- it modifies building behavior
- Flag must be compatible with existing plan path argument: `/code-foundations:building --live docs/plans/my-plan.md`
- Invalid flag combinations should produce clear error messages

**Approach notes:**
- `--live` flag goes on the building command only -- user explicitly chose to NOT add it as a review preset, even though the original request mentioned "third preset." The integration point is building, not review.

**File hints:**
- `commands/building.md` -- command definition with argument-hint and allowed-tools
- `skills/building/SKILL.md` -- where the flag is consumed

**Depends on:** Phase 2 | **Unlocks:** Phase 5

**Done when:**
- [ ] `commands/building.md` argument-hint includes `--live` option
- [ ] Building skill reads and validates the `--live` flag
- [ ] Flag is propagated to SETUP phase for conditional task creation
- [ ] Error message shown if `--live` used without a plan file

**Difficulty:** LOW
**Uncertainty:** None

---

### Phase 4: Fix Loop Integration
**Model:** opus

**Goal:** When live-review surfaces findings during a building phase, give the implementation agent a chance to fix them before POST-GATE runs. This closes the feedback loop that makes live review actionable rather than merely informational.

**Scope:**
- IN: Fix loop logic between LIVE-REVIEW and POST-GATE, re-dispatch to implementation agent, finding consumption, loop termination
- OUT: Findings reporting/dashboard, post-gate-agent changes

**Constraints:**
- Fix loop must terminate: maximum 2 iterations (review -> fix -> review -> proceed regardless)
- Fix loop must not re-dispatch implementation agent if zero findings from live-review
- Findings from `add-finding.sh` must be readable by the building orchestrator to decide whether to enter fix loop
- Fix loop iterations must be visible in the execution log

**Approach notes:**
- Two-iteration cap is a hard constraint -- user chose bounded iteration over convergence-based termination to prevent infinite loops
- The fix re-dispatch should provide the implementation agent with the specific findings (file, line, check-id, issue) rather than asking it to re-read the full findings file

**File hints:**
- `skills/building/SKILL.md` -- execution loop where fix logic lives
- `agents/implementation-agent.md` -- reference for re-dispatch format
- `agents/add-finding.sh` -- output format the orchestrator must parse

**Depends on:** Phase 2 | **Unlocks:** Phase 5

**Done when:**
- [ ] Building orchestrator reads findings after LIVE-REVIEW sub-phase
- [ ] If findings exist, implementation agent is re-dispatched with finding details
- [ ] After fix, live-review runs again (iteration 2 maximum)
- [ ] Fix loop iterations logged in execution log with finding counts
- [ ] Zero-finding case skips fix loop entirely and proceeds to POST-GATE

**Difficulty:** HIGH
**Uncertainty:** How to parse findings.jsonl from the orchestrator level -- the building skill currently does not read finding output; pre-gate must determine whether bash parsing or a helper script is needed

---

### Phase 5: Execution Log and Reporting
**Model:** sonnet

**Goal:** Update the building skill's execution log format and trust report to include live-review data so engineers can see what was caught and fixed in-loop versus what POST-GATE found after.

**Scope:**
- IN: Execution log format updates, trust report format updates, per-phase live-review summary
- OUT: Dashboard UI, findings file format changes, review command reporting

**Constraints:**
- Execution log must distinguish between live-review findings (caught in-loop) and post-gate findings (caught by reviewer)
- Trust report must show live-review statistics without drowning out the existing gate summary
- Must be backward-compatible: execution logs from non-live builds should render identically to current format

**Approach notes:**
- Add a `LIVE-REVIEW` row to the gate summary table rather than a separate section -- user prefers integrated reporting over separate live-review reports

**File hints:**
- `skills/building/SKILL.md` -- Phase 5: REPORT section and execution log format
- `commands/building.md` -- trust report template

**Depends on:** Phase 3, Phase 4 | **Unlocks:** Phase 6

**Done when:**
- [ ] Execution log per-phase section includes LIVE-REVIEW status (findings count, fix iterations, final state)
- [ ] Trust report gate summary table includes LIVE-REVIEW column
- [ ] Non-live builds omit LIVE-REVIEW from execution log and trust report
- [ ] Per-phase artifacts section references live-review findings file when applicable

**Difficulty:** MEDIUM
**Uncertainty:** None

---

### Phase 6: Documentation and CLAUDE.md Sync
**Model:** haiku

**Goal:** Update all documentation references to reflect the new `--live` capability so that CLAUDE.md, skill descriptions, and command help text accurately describe the system.

**Scope:**
- IN: CLAUDE.md updates, building skill description update, command help text
- OUT: Tutorial/guide content, marketing materials

**Constraints:**
- CLAUDE.md architecture diagrams must show the optional LIVE-REVIEW sub-phase
- Building skill description must mention `--live` as an option
- Do not update review system documentation (live review is a building feature, not a review feature)

**File hints:**
- `CLAUDE.md` -- project documentation that describes building workflow and review system
- `skills/building/SKILL.md` -- frontmatter description field
- `commands/building.md` -- frontmatter description field

**Depends on:** Phase 5 | **Unlocks:** None

**Done when:**
- [ ] CLAUDE.md building workflow section includes `--live` option
- [ ] CLAUDE.md quality gates section shows optional LIVE-REVIEW between IMPLEMENT and POST-GATE
- [ ] Building skill and command descriptions updated

**Difficulty:** LOW
**Uncertainty:** None

---

## Test Coverage

**Level:** 100%

## Test Plan

- [ ] Unit: Live-review agent template produces valid `add-finding.sh` calls for each of the 14 core checks
- [ ] Unit: Building skill SETUP creates correct TaskCreate chain with 5 sub-phases when `--live` active
- [ ] Unit: Building skill SETUP creates correct TaskCreate chain with 4 sub-phases when `--live` not active (regression)
- [ ] Unit: Fix loop terminates after 2 iterations regardless of finding state
- [ ] Unit: Fix loop skips entirely when live-review produces zero findings
- [ ] Integration: Full building session with `--live` on a 2-phase plan completes with correct execution log
- [ ] Integration: Full building session without `--live` produces identical output to current behavior (regression)
- [ ] Manual: Verify trust report readability with live-review data included

---

## Assumptions

| Assumption | Confidence | Verify Before Phase | Fallback If Wrong |
|-----------|-----------|--------------------|--------------------|
| TaskCreate supports non-integer sub-phase identifiers (N.2b) | MEDIUM | Phase 2 | Use integer numbering (N.1 through N.5) and adjust all references |
| `add-finding.sh` output (findings.jsonl) is readable by the building orchestrator via bash | HIGH | Phase 4 | Write a small helper script to parse JSONL |
| 14 core checks can complete on a typical phase's changed files in <30 seconds | HIGH | Phase 1 | Reduce check count or parallelize |
| Building skill's SETUP phase can conditionally branch based on a flag | HIGH | Phase 2 | Pass flag as plan metadata instead |

## Decision Log

| Decision | Alternatives Considered | Rationale | Phase |
|----------|------------------------|-----------|-------|
| Injected sub-phase over parallel review | Parallel background review, event-driven watcher | Respects TaskCreate chain model; avoids race conditions | 2 |
| 14 core checks over full 614 | Full PR set, custom subset | Speed constraint (<30s); core checks have 7/7 consensus signal | 1 |
| Building flag over review preset | `--live` on review command, auto-detect | Live review is building-specific behavior; review command operates on existing code | 3 |
| 2-iteration fix cap over convergence | Unlimited iteration, single-pass | Bounded termination prevents infinite loops while allowing one fix attempt | 4 |
| Integrated gate summary over separate report | Separate live-review report section | Reduces cognitive load; engineers already read the gate summary table | 5 |

---

## Notes

- The live-review agent intentionally runs only the 14 core sanity checks, not the full skill-based POST-GATE review. POST-GATE still runs after live-review, providing the full correctness/defensive-programming/module-design review. Live-review catches the low-hanging fruit (null safety, error handling, bounds) before POST-GATE does the deep review.
- If live-review becomes popular, a future enhancement could allow configuring which checks to run (e.g., `--live=core` vs `--live=defensive` vs `--live=full`). This is explicitly out of scope for this plan.
- The fix loop creates a feedback cycle that could theoretically surface new issues on each fix. The 2-iteration cap prevents this from becoming unbounded. Issues not fixed in 2 iterations will be caught by POST-GATE.
- Phase 2 is the highest-risk phase because it modifies the building skill's core execution loop. Front-loading it (after agent template) ensures we discover architectural constraints early.

---

## Execution Log

_To be filled during /code-foundations:building_

---
---

## Meta-Commentary

### Did the skill correctly route to the Complex track?

Yes. The signal table clearly indicates Complex:

- **Files touched:** 9+ (building SKILL.md, building command, CLAUDE.md, new agent template, add-finding.sh integration, execution log format, trust report format, potentially a helper script)
- **Patterns involved:** Multiple new patterns (injected sub-phase, fix loop, conditional task chain creation) plus cross-cutting integration with existing patterns (agent dispatch, finding pipeline, execution logging)
- **Cross-cutting concerns:** 3+ (TaskCreate chain modification, finding pipeline integration, execution log format, backward compatibility, command flag routing)
- **Uncertainty:** High -- whether TaskCreate supports N.2b naming, whether the building orchestrator can parse findings.jsonl, whether 14 checks fit in the latency budget
- **Phase count:** 6 (within the 5-7 range for Complex)

No reasonable argument for Medium exists. This touches the core execution loop of a multi-agent pipeline.

### Was the ceremony appropriate for this architectural change?

Yes. The Complex track's full ceremony is justified here:

- **Approach comparison** was essential. The three approaches (injected sub-phase, parallel background, event-driven watcher) are structurally different and have meaningfully different failure modes. The pre-mortem would have revealed that the parallel approach creates race conditions and the watcher approach is architecturally impossible in Claude Code's execution model.
- **Self-check** would have caught that the original user request framed this as a "third review preset" but the design correctly routes it as a building feature. That reframing needs to be explicit.
- **Assumptions table** is load-bearing. The TaskCreate naming constraint (N.2b vs integer) could force a significant redesign if the assumption is wrong. Documenting it with a fallback prevents a blocked build.

### Do phases stay at WHAT/WHY level without prescribing HOW?

Yes, with appropriate discipline:

- No phase contains pseudocode, function signatures, class hierarchies, or specific algorithms.
- Approach notes contain only non-discoverable user decisions: "14 core checks not 614" (user chose speed), "N.2b naming not renumbering" (user chose backward compatibility), "2-iteration cap" (user chose bounded termination).
- File hints are directory-level or reference existing files for pattern discovery, not mandated file paths to create.
- Done-when criteria are observable conditions ("file exists," "chain includes N.2b," "non-live builds produce identical output"), not implementation steps.

One area that could be criticized: the constraint "Agent must use add-finding.sh for all finding output" could be seen as prescribing HOW. But this is legitimately a constraint (schema enforcement is a non-negotiable architectural decision), not an implementation detail. The pre-gate agent still decides how to invoke it.

### Are dependencies and scope boundaries clear?

Yes. The dependency graph is:

```
Phase 1 (agent template) ──┬──> Phase 2 (building loop)──┬──> Phase 3 (command flag)──┐
                            │                              │                            │
                            │                              └──> Phase 4 (fix loop)──────┤
                            │                                                           │
                            └──────────────────────────────────────> Phase 5 (reporting)─┤
                                                                                        │
                                                                              Phase 6 (docs)
```

Scope boundaries are explicit via IN/OUT on every phase. No phase's IN scope overlaps with another's. The union covers the full feature. Phase 1's OUT explicitly excludes building skill modifications; Phase 2's OUT explicitly excludes command-line parsing.

### Does the plan respect the 7-phase cap?

Yes, 6 phases. A 7th phase for "testing infrastructure" was considered but correctly rejected by YAGNI -- the test plan covers verification within existing phases, and a dedicated testing phase would be over-planning.

### Would you trust a pre-gate agent to execute from this plan?

Yes, for each phase:

- **Phase 1:** Pre-gate has clear goal (create agent template), clear patterns to reference (post-gate-agent.md), clear constraints (must use add-finding.sh). It will discover the agent template pattern by reading existing agents and produce appropriate pseudocode.
- **Phase 2:** This is the highest-risk phase. The pre-gate agent has the right file hints (building SKILL.md), the right constraints (zero behavioral change for non-live builds), and the right uncertainty signal (TaskCreate naming). It will discover the actual TaskCreate API constraints before designing.
- **Phase 3:** Straightforward flag routing. Pre-gate will read the existing command format and extend it.
- **Phase 4:** Pre-gate has the fix loop goal, the iteration cap constraint, and the finding pipeline reference. It will discover the findings.jsonl format and design parsing.
- **Phase 5:** Pre-gate has clear format requirements and backward compatibility constraint. Mechanical work.
- **Phase 6:** Documentation sync. Pre-gate reads current docs and updates them.

The plan gives each pre-gate agent enough strategic context to make good tactical decisions without constraining its discovery. The approach notes preserve user decisions (14 checks, N.2b naming, 2-iteration cap) that cannot be rediscovered from the codebase.
