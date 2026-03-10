# Plan: Live Review Preset for Building Pipeline

**Created:** 2026-03-10
**Status:** ready
**Complexity:** complex

---

## Context

The code review system (`/code-foundations:review`) currently offers two presets: `--sanity` (14 core checks for pre-commit) and `--pr` (614 checks for full PR review). Both operate as batch processes on already-written code. There is no way to run review checks incrementally during a `/code-foundations:building` session, meaning issues caught by review are discovered late -- after all phases complete rather than immediately after each IMPLEMENT sub-phase. A `--live` preset would surface findings in real-time during building, tightening the feedback loop and catching issues before they propagate across phases.

## Constraints

- Must not break existing `--sanity` and `--pr` presets
- Must integrate with the existing `add-finding.sh` / `add-verdict.sh` pipeline (JSONL schema)
- Must hook into building's phase transition points without requiring the user to manually invoke review
- Findings must be surfaced between IMPLEMENT and POST-GATE (not after POST-GATE, which already has its own reviewer)
- Must work with the TaskCreate/blockedBy enforcement chain in building
- Check selection must be phase-aware (only run checks relevant to what was just implemented)
- Must not duplicate work the post-gate-agent already performs
- Must not require changes to the agent dispatch protocol (subagent_type, model resolution)
- Overhead must be bounded -- live review of a single phase should add less than 30 seconds of wall-clock time beyond what the phase already takes

## Chosen Approach

**Injected Sub-Phase with Scoped Check Selection**

Insert a new sub-phase (N.2b: LIVE-REVIEW) between IMPLEMENT (N.2) and POST-GATE (N.3) in the building execution loop. This sub-phase dispatches a lightweight review agent that runs a curated subset of checks (drawn from the existing core-checklist.md and relevant skill checklists) scoped to only the files changed during IMPLEMENT. Findings are written via `add-finding.sh` to a per-phase JSONL file and surfaced inline before POST-GATE proceeds. The post-gate-agent then receives these findings as additional input, avoiding redundant checking.

**Rationale:** This approach reuses the existing review infrastructure (check IDs, finding schema, verdict schema) and slots into the building pipeline's TaskCreate chain with minimal disruption. It avoids creating a parallel review system and instead extends the one that exists.

**Fallback:** If injecting a sub-phase proves too disruptive to the building orchestrator's task chain, fall back to a simpler model where POST-GATE itself runs the live checks as an optional first pass before its existing verification, consolidating into one sub-phase rather than adding a new one.

## Rejected Approaches

- **Background Watcher (Continuous Polling):** Run checks in a background process that monitors file changes during IMPLEMENT. Rejected because Claude Code's execution model is synchronous subagent dispatch -- there is no background process capability, and polling would fight the TaskCreate enforcement model.
- **Post-Hoc Batch with Phase Tags:** Run a modified `--sanity` after all building phases complete, tagging findings by phase. Rejected because this defeats the purpose of real-time feedback -- issues from Phase 1 would not be visible until after Phase N completes.

---

## Implementation Phases

### Phase 1: Live Check Selection Engine
**Model:** sonnet

**Goal:** Create the mechanism that selects which checks to run based on what files changed in a phase, so live review only runs relevant checks rather than the full 614-check corpus.

**Scope:**
- IN: Check selection logic that maps file types, change patterns, and phase context to a subset of check IDs from existing checklists
- OUT: New checks, modifications to existing checklist files, UI/reporting

**Constraints:**
- Must read from existing checklist files (`agents/core-checklist.md`, `skills/*/checklists.md`)
- Selection output must be a list of check IDs compatible with `add-finding.sh --check-id`
- Must always include the 14 core checks from `core-checklist.md` as baseline

**Approach notes:**
- Use the core 14 checks as the always-on baseline, then layer skill-specific checks based on which skills the IMPLEMENT sub-phase loaded (e.g., if `cc-control-flow-quality` was loaded during IMPLEMENT, include its checks in live review)
- Phase metadata from the building plan (difficulty, uncertainty) should influence check depth -- HIGH difficulty phases get more checks

**File hints:**
- `agents/core-checklist.md` -- the 14 core checks to always include
- `skills/*/checklists.md` -- skill-specific checks to selectively include
- `references/checker-dispatch.md` -- existing check dispatch patterns

**Depends on:** None | **Unlocks:** Phase 2

**Done when:**
- [ ] Given a list of changed files and phase metadata, produces a scoped check list
- [ ] Core 14 checks are always included
- [ ] Skill-specific checks are included only when the corresponding skill was active during IMPLEMENT
- [ ] Output format is consumable by a checker agent

**Difficulty:** MEDIUM
**Uncertainty:** The right granularity for skill-to-check mapping -- may need iteration to find the balance between too few checks (misses issues) and too many (defeats the speed goal)

---

### Phase 2: Live Review Agent
**Model:** sonnet

**Goal:** Create the agent template that executes the scoped checks against files changed during a single IMPLEMENT sub-phase, producing findings via the existing `add-finding.sh` pipeline.

**Scope:**
- IN: Agent template (`agents/live-review-agent.md`), integration with `add-finding.sh` for output
- OUT: Verdict/investigation logic (that stays in the investigation phase of `--sanity`/`--pr`), modifications to existing agents

**Constraints:**
- Must follow the existing agent template pattern (frontmatter with name/description, skill loading section, input/output format)
- Must use `add-finding.sh` for all findings -- no custom output format
- Must accept a check list (from Phase 1) and a file list as inputs
- Must return structured output: finding count, check IDs with findings, phase-scoped JSONL path

**Approach notes:**
- Model this after the existing checker agents in the review pipeline, but scoped to single-phase incremental review rather than full-codebase batch review
- Agent should be dispatchable as a subagent from the building orchestrator using the standard Agent tool

**File hints:**
- `agents/core-checklist.md` -- pattern for check execution
- `agents/add-finding.sh` -- output mechanism
- `agents/post-gate-agent.md` -- existing review agent to complement (not duplicate)
- `commands/review.md` -- existing review dispatch patterns

**Depends on:** Phase 1 | **Unlocks:** Phase 3

**Done when:**
- [ ] Agent template exists at `agents/live-review-agent.md`
- [ ] Agent accepts check list and changed-file list as input
- [ ] Agent writes findings via `add-finding.sh` to a phase-scoped JSONL file
- [ ] Agent returns a structured summary (finding count, severity breakdown)
- [ ] Agent completes within the 30-second overhead budget for a typical 3-file phase

**Difficulty:** MEDIUM
**Uncertainty:** None -- this follows established agent template patterns

---

### Phase 3: Building Pipeline Integration
**Model:** opus

**Goal:** Modify the building skill's execution loop to inject the LIVE-REVIEW sub-phase between IMPLEMENT and POST-GATE, wiring it into the TaskCreate/blockedBy chain so it cannot be skipped.

**Scope:**
- IN: Building skill's SETUP (task creation), EXECUTE loop, and sub-phase dispatch templates
- OUT: Review command (`commands/review.md`), existing preset behavior, VERIFY/REPORT phases

**Constraints:**
- The new sub-phase must be optional -- only injected when the plan or user specifies `--live` review
- When `--live` is not active, the building pipeline must behave identically to today (no regression)
- Task chain must go: N.1 PRE-GATE -> N.2 IMPLEMENT -> N.2b LIVE-REVIEW -> N.3 POST-GATE -> N.4 CHECKPOINT
- Model auto-detection for LIVE-REVIEW should default to sonnet (review work, not implementation)

**Approach notes:**
- The `--live` flag is a plan-level setting, not a per-phase setting -- user decides at whiteboarding/plan time whether the building session uses live review
- The building orchestrator reads a `**Live Review:** enabled` field from the plan file header to know whether to inject N.2b tasks

**File hints:**
- `skills/building/SKILL.md` -- the execution loop and task creation logic to modify
- `commands/building.md` -- the command entry point
- `references/plan-schema.md` -- plan file format (needs new field)

**Depends on:** Phase 2 | **Unlocks:** Phase 4

**Done when:**
- [ ] Building SETUP creates N.2b tasks when live review is enabled
- [ ] N.2b is chained: blockedBy N.2, blocks N.3
- [ ] Building EXECUTE dispatches live-review-agent for N.2b with correct inputs
- [ ] When `--live` is not enabled, no N.2b tasks are created (zero regression)
- [ ] Plan file schema supports `**Live Review:** enabled/disabled` field

**Difficulty:** HIGH
**Uncertainty:** Whether the existing TaskCreate documentation in building SKILL.md can accommodate a conditional sub-phase cleanly, or whether the task numbering scheme needs revision

---

### Phase 4: Finding Handoff to POST-GATE
**Model:** sonnet

**Goal:** Ensure live review findings flow into the POST-GATE sub-phase so the post-gate-agent can skip re-checking what live review already verified, and can focus its deeper skill-based verification on areas live review flagged.

**Scope:**
- IN: Post-gate-agent input format, live review finding output, handoff protocol
- OUT: Post-gate-agent's internal verification logic, existing review presets

**Constraints:**
- Post-gate-agent must remain functional when no live review findings exist (backward compatibility)
- Live review findings are informational input, not a gate -- POST-GATE still makes its own PASS/FAIL decision
- Finding JSONL file path must be passed via the dispatch prompt, not hardcoded

**Approach notes:**
- Use an optional `## Live Review Findings` section in the POST-GATE dispatch prompt -- when present, post-gate-agent reads the JSONL and factors it into its review; when absent, it runs as before

**File hints:**
- `agents/post-gate-agent.md` -- agent template to extend with optional live review input
- `skills/building/SKILL.md` -- POST-GATE dispatch template to modify

**Depends on:** Phase 3 | **Unlocks:** Phase 5

**Done when:**
- [ ] POST-GATE dispatch prompt includes live review JSONL path when available
- [ ] Post-gate-agent reads live review findings and skips re-checking those check IDs on those files
- [ ] Post-gate-agent works identically when no live review findings are provided
- [ ] No duplicate findings between live review and POST-GATE output

**Difficulty:** MEDIUM
**Uncertainty:** None -- this is additive input to an existing agent

---

### Phase 5: Inline Finding Presentation
**Model:** sonnet

**Goal:** Surface live review findings to the building orchestrator (and by extension the user) in a format that is immediately actionable between IMPLEMENT and POST-GATE, so the user can decide whether to fix issues before POST-GATE runs.

**Scope:**
- IN: Finding presentation format, orchestrator's handling of N.2b results, user interaction pattern
- OUT: Dashboard rendering, `--sanity`/`--pr` output format, investigation agents

**Constraints:**
- Presentation must be concise -- the building orchestrator's context window is shared across all phases
- Must clearly distinguish between "fix now" (high-confidence findings) and "review later" (low-confidence)
- Must offer the user a choice: fix findings before POST-GATE, or proceed and let POST-GATE catch them

**Approach notes:**
- Adopt the existing review output format (grouped by action type: Findings vs Questions) but scoped to a single phase
- The building orchestrator should pause after LIVE-REVIEW and present a brief summary with an explicit "Fix now or proceed?" prompt

**File hints:**
- `skills/building/SKILL.md` -- where the orchestrator handles sub-phase results
- `commands/review.md` -- existing output format patterns to follow

**Depends on:** Phase 4 | **Unlocks:** Phase 6

**Done when:**
- [ ] Building orchestrator presents a summary of live review findings after N.2b completes
- [ ] Summary groups findings by severity (high-confidence vs low-confidence)
- [ ] User is offered "Fix now / Proceed to POST-GATE" choice
- [ ] If user chooses "fix now," orchestrator allows edits before POST-GATE starts
- [ ] Summary adds fewer than 20 lines to the orchestrator's output per phase

**Difficulty:** MEDIUM
**Uncertainty:** The right UX for pausing the pipeline -- too intrusive slows down building, too subtle means findings get ignored

---

### Phase 6: Review Command Registration
**Model:** sonnet

**Goal:** Register `--live` as a recognized preset in the review command so it can be invoked standalone (outside building) and so the review system's documentation and validation recognize it as a valid option.

**Scope:**
- IN: Review command preset registration, validation, help text
- OUT: Review pipeline execution (live review during building does NOT go through the review command -- it is dispatched directly by the building orchestrator)

**Constraints:**
- `--live` standalone must produce a clear error: "The --live preset is designed for use during /code-foundations:building sessions. Use --sanity for quick checks or --pr for full review."
- Preset validation in review.md must recognize `--live` without crashing
- Documentation in CLAUDE.md must be updated to reflect the third preset

**Approach notes:**
- The `--live` preset is not independently executable like `--sanity` and `--pr` -- it is a building-pipeline integration. The review command should acknowledge it exists but redirect users to the building workflow.

**File hints:**
- `commands/review.md` -- preset parsing and validation
- `CLAUDE.md` -- top-level documentation to update

**Depends on:** Phase 5 | **Unlocks:** None

**Done when:**
- [ ] `--live` is listed in review command help text
- [ ] `--live` standalone produces a helpful redirect message
- [ ] CLAUDE.md documents the three presets and their use cases
- [ ] No validation errors when `--live` is encountered

**Difficulty:** LOW
**Uncertainty:** None

---

## Test Coverage

**Level:** 100%

## Test Plan

- [ ] Unit: Check selection engine returns correct check subset for various file/phase inputs
- [ ] Unit: Live review agent produces valid JSONL via `add-finding.sh`
- [ ] Integration: Full building session with `--live` enabled completes all sub-phases in correct order
- [ ] Integration: Building session without `--live` has zero behavioral changes (regression test)
- [ ] Integration: POST-GATE receives and correctly processes live review findings
- [ ] Integration: POST-GATE works normally when no live review findings exist
- [ ] Manual: Run `/code-foundations:building` with a 2-phase plan with `**Live Review:** enabled` and verify findings appear between IMPLEMENT and POST-GATE
- [ ] Manual: Run `/code-foundations:review --live` standalone and verify redirect message

---

## Assumptions

| Assumption | Confidence | Verify Before Phase | Fallback If Wrong |
|-----------|-----------|--------------------|--------------------|
| TaskCreate chain supports conditional sub-phases (N.2b) without breaking N.3 numbering | HIGH | Phase 3 | Renumber all sub-phases to accommodate (N.1, N.2, N.3, N.4, N.5) |
| `add-finding.sh` works correctly with per-phase JSONL paths (not just $BASE_DIR default) | HIGH | Phase 2 | Use `--output` flag which already exists |
| Post-gate-agent can accept optional additional input sections without disruption | HIGH | Phase 4 | Wrap in a conditional block in the dispatch prompt |
| 14 core checks can complete on 3 typical files within 30 seconds | MEDIUM | Phase 2 | Reduce to top 8 checks if timing budget exceeded |

## Decision Log

| Decision | Alternatives Considered | Rationale | Phase |
|----------|------------------------|-----------|-------|
| Injected sub-phase vs background watcher | Background polling, post-hoc batch | Fits Claude Code's synchronous model, uses existing TaskCreate enforcement | 3 |
| Core 14 as baseline + skill-specific extras | Full 614 checks, custom live-only list | Reuses consensus-distilled checks, scales with phase skills, stays fast | 1 |
| Plan-level `--live` flag vs per-phase toggle | Per-phase, always-on, command-line flag | Plan-level is simplest UX, decided at planning time, no per-phase overhead | 3 |
| POST-GATE receives findings as input vs separate dedup step | Dedup agent, shared state file | Direct input is simpler, post-gate-agent already reads context files | 4 |
| `--live` not standalone-executable | Full standalone mode | Live review without building context is meaningless -- checks need phase/file scope | 6 |

---

## Notes

- The existing review pipeline's `extract-units.sh` is not needed for live review because the building pipeline already knows exactly which files changed (the implementation agent reports them)
- The `resolve-dependencies.sh` script is also not needed since live review operates on a known, bounded file set per phase
- The quick-checklist.md agent is not reused here because it lacks the skill-based check selection that live review needs
- Future enhancement: live review could learn from POST-GATE verdicts over time, adjusting which checks it runs based on historical false positive rates per check ID

---

## Execution Log

_To be filled during /code-foundations:building_

---
---

## Meta-Commentary

### Did the skill correctly route to the Complex track?

Yes. The signal table clearly indicates Complex:
- **Files touched:** 9+ (building SKILL.md, review command, post-gate-agent, new live-review-agent, core-checklist integration, plan-schema, CLAUDE.md, plus test files)
- **Patterns involved:** Multiple new patterns (conditional sub-phase injection, incremental review, finding handoff) plus cross-cutting modification of existing patterns (TaskCreate chain, agent dispatch, review pipeline)
- **Cross-cutting concerns:** 3+ (review pipeline integration, building pipeline modification, agent dispatch protocol, plan file schema, finding deduplication)
- **Uncertainty:** High -- whether the TaskCreate chain can handle conditional sub-phases, whether timing budgets hold
- **Phase count:** 6 (within the 5-7 range for Complex)

### Was the ceremony appropriate for this architectural change?

Yes. This is a cross-system modification that touches the two most complex subsystems in the codebase (building pipeline and review pipeline). The Complex track's full contract template with approach comparison, pre-mortem (implicit in the rejected approaches), dependency chains, difficulty/uncertainty signals, and self-check is warranted. A Medium track would have missed the handoff complexity between live review and POST-GATE, and the conditional sub-phase insertion problem.

### Do phases stay at WHAT/WHY level without prescribing HOW?

Yes. Each phase specifies:
- **What** to build (check selection engine, agent template, pipeline integration, handoff, presentation, registration)
- **Why** it matters (scoped checks, reuse existing pipeline, cannot skip via TaskCreate, avoid duplicate work, actionable feedback, discoverability)
- **No pseudocode, function signatures, class hierarchies, or algorithms.** The approach notes contain only non-discoverable user decisions (e.g., "plan-level setting not per-phase," "core 14 as baseline").

The file hints are directory/file-level, not line-level. Done-when criteria are observable conditions, not implementation steps.

### Are dependencies and scope boundaries clear?

Yes. The dependency chain is linear (1 -> 2 -> 3 -> 4 -> 5 -> 6), which is appropriate because each phase builds on the previous. Scope boundaries are explicit:
- Phase 1 creates the selection logic but not the agent
- Phase 2 creates the agent but does not integrate it into building
- Phase 3 integrates into building but does not handle finding handoff
- Phase 4 handles handoff but not presentation
- Phase 5 handles presentation but not command registration
- Phase 6 handles registration and documentation

No scope overlaps. The OUT sections prevent creep (e.g., Phase 2 explicitly excludes verdict/investigation logic).

### Does the plan respect the 7-phase cap?

Yes. 6 phases, under the cap. Each phase is within the 100-150 word target for Medium/Complex track. No phase exceeds 200 words. The YAGNI gate was applied -- no phase exists for hypothetical future needs (the "learning from POST-GATE verdicts" idea is noted as a future enhancement, not a phase).

### Would you trust a pre-gate agent to execute from this plan?

Yes. Each phase gives the pre-gate agent:
- A clear **Goal** that anchors discovery (what to search for)
- **File hints** that focus discovery without mandating paths
- **Constraints** that prevent wrong turns (backward compatibility, schema compliance, timing budget)
- **Approach notes** that convey decisions the agent could not rediscover (plan-level vs per-phase, core 14 as baseline)
- **Uncertainty** signals that tell the agent where to investigate first
- **Done-when** criteria that are verifiable without subjective judgment

The pre-gate agent would load its four design skills, search the hinted files, discover the actual implementation state, and write pseudocode that respects the constraints and approach notes. It would not be constrained by stale implementation details because the plan contains none.
