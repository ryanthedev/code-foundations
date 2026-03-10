# Evaluation: FINAL-SKILL.md Whiteboarding Upgrade

**Evaluator context:** Blind evaluation of 6 plans (3 scenarios x 2 agents) produced by the same FINAL-SKILL.md, assessed against how well the building pipeline (pre-gate-agent, implementation-agent, post-gate-agent) can consume them.

---

## Scores by Scenario

### Simple (rename command)

| Criterion | A | B |
|-----------|---|---|
| Track routing | 10 | 10 |
| Pre-gate clarity | 9 | 9 |
| Scope discipline | 9 | 8 |
| Done-when quality | 9 | 9 |
| Signal-to-noise | 8 | 9 |
| Non-discoverable preservation | 9 | 8 |
| Ceremony appropriateness | 9 | 9 |
| **TOTAL** | **63** | **62** |

### Medium (estimation skill)

| Criterion | A | B |
|-----------|---|---|
| Track routing | 10 | 10 |
| Pre-gate clarity | 9 | 8 |
| Scope discipline | 9 | 8 |
| Done-when quality | 9 | 8 |
| Signal-to-noise | 8 | 7 |
| Non-discoverable preservation | 9 | 8 |
| Ceremony appropriateness | 9 | 8 |
| **TOTAL** | **63** | **57** |

### Complex (live review system)

| Criterion | A | B |
|-----------|---|---|
| Track routing | 10 | 10 |
| Pre-gate clarity | 9 | 8 |
| Scope discipline | 9 | 7 |
| Done-when quality | 9 | 8 |
| Signal-to-noise | 8 | 7 |
| Non-discoverable preservation | 9 | 8 |
| Ceremony appropriateness | 9 | 8 |
| **TOTAL** | **63** | **56** |

---

## Consistency Analysis

**Overall consistency: HIGH.** Both agents consistently produce the same track classification for every scenario. The skill's signal table is unambiguous enough that neither agent hesitates or misclassifies. This is the strongest signal that the skill is well-designed -- routing is deterministic.

**Where they converge:**
- Track selection (100% agreement across all 3 scenarios)
- Phase count (Simple: both 1-2 phases; Medium: both 3-4 phases; Complex: both 6 phases)
- Template adherence (both follow the correct template for their track)
- Model recommendations (both use haiku for Simple, sonnet/haiku mix for Medium, opus for high-risk Complex phases)
- Test coverage integration (both ask and record the answer)

**Where they diverge:**

1. **Simple scenario: Scope boundaries.** A splits into 2 phases (rename file, then update references). B does 1 phase (rename only) and defers reference updates to a "follow-up pass." Both are defensible, but A's plan is more complete -- it finishes the job. B's plan leaves a known gap (9 stale references) that the user would need to remember. The skill does not prescribe whether to include follow-up work, so both are valid outputs. However, A's interpretation serves the building pipeline better because the pipeline produces a finished state.

2. **Medium scenario: Phase granularity and detail density.** A produces 3 focused phases (core skill, research backing, integration). B produces 4 phases (adds a Phase 4 for CLAUDE.md docs). A's Phase 2 (hard-data) is cleanly scoped with haiku model recommendation. B's Phase 4 (docs) is arguably YAGNI -- CLAUDE.md updates could be folded into Phase 3's integration work. More notably, B's phases are slightly denser with more approach notes per phase, some of which edge toward implementation detail (e.g., specifying the PERT formula and Fibonacci sequence in approach notes). A keeps approach notes at the decision level.

3. **Complex scenario: Architectural decomposition.** A decomposes into 6 phases with a clear dependency DAG (Phase 1 unlocks both 2 and 3; Phases 3+4 unlock 5; 5 unlocks 6). B decomposes into 6 phases with a strictly linear chain (1->2->3->4->5->6). A's DAG better models the actual dependency structure -- the command flag (Phase 3) and fix loop (Phase 4) are independent work streams that only converge at reporting (Phase 5). B's linear chain artificially serializes independent work. More significantly, B introduces a Phase 1 ("Live Check Selection Engine") that is arguably implementation detail -- deciding which checks to run is a decision the live-review agent should make internally, not a separate buildable phase. A correctly treats check selection as part of the agent template (Phase 1).

   B also includes a Phase 6 that registers `--live` as a review command preset that returns an error message. This is an odd design choice -- building a feature that only exists to tell users not to use it. A does not include this and is cleaner for it.

   B's Phase 5 (Inline Finding Presentation) introduces a "Fix now / Proceed to POST-GATE" user interaction that A handles more cleanly as an automated fix loop (Phase 4) with a bounded iteration cap. A's approach is more aligned with the building pipeline's autonomous execution model.

**Consistency verdict:** The skill produces structurally similar plans from both agents, but Agent A consistently makes better judgment calls about scope boundaries, phase granularity, and the WHAT-vs-HOW line. This suggests the skill provides good guardrails but does not fully prevent an agent from drifting toward over-specification or questionable decomposition choices.

---

## Per-Scenario Commentary

### Simple: Rename Command

**Strengths (both plans):**
- Correct track routing with zero hesitation
- Clean, flat checklist format with appropriate word counts
- Both correctly identify the trap: do not change `Skill(code-foundations:whiteboarding)` invocation
- Model recommendation (haiku) is correct and justified
- Test plan is appropriate (grep for old name, verify new file exists)

**Weaknesses:**
- A includes a Notes section flagging specific files the pre-gate agent should discover. This is helpful but borders on doing the pre-gate agent's job. The file hints in each phase are sufficient.
- B's decision to defer reference updates is a scope judgment the user made, not the skill. The skill does not guide the agent on whether to include "everything related" or "minimum viable change." This is arguably fine -- it is a user decision -- but it means the plan's completeness depends entirely on the user's answer to Q1.

**Net assessment:** Both plans would execute successfully in the building pipeline. A is slightly more complete. The Simple track is working well.

### Medium: Estimation Skill

**Strengths (both plans):**
- Correct Medium classification with clear signal-table justification
- Both produce the same approach decision (standalone skill with file output)
- Both identify the right rejected approach (inline in whiteboarding)
- Approach notes correctly capture non-discoverable decisions (technique ordering, output directory, solo-dev constraint)
- Assumptions tables are well-structured with confidence levels and fallbacks

**Weaknesses:**
- A's approach notes are cleaner: "Use reference class forecasting as PRIMARY technique" is a decision. B's approach notes include "PERT formula: E = (O + 4M + P) / 6" -- this is an implementation detail that the pre-gate agent should derive from the hard-data research, not a user decision. The formula itself is well-established; the decision to USE three-point estimation was already captured elsewhere.
- B assigns sonnet to Phase 2 (checklists + hard-data). A assigns haiku. Given Phase 2 has 2 done-when items, references 2-3 files, and is LOW difficulty, A's haiku recommendation is more aligned with the model auto-detection rules. B is slightly wasteful.
- B's Phase 4 (docs sync) is borderline YAGNI for a medium-complexity plan. CLAUDE.md updates are 2 lines in a table and a sentence in a workflow section -- this could be folded into Phase 3's scope without creating a separate phase with its own pre-gate/implement/post-gate cycle.
- Both plans would benefit from explicitly noting that `cc-estimation` is a new prefix that needs to be added to the master dispatcher's skill reference, but neither makes this a Phase 1 constraint (A mentions it in Notes, B in Phase 3 scope).

**Net assessment:** A is the stronger plan. It is tighter, has better model recommendations, and keeps approach notes at the right abstraction level. B is adequate but slightly bloated. The Medium track is working well overall.

### Complex: Live Review System

**Strengths (both plans):**
- Correct Complex classification with thorough signal-table justification
- Both identify the same core approach (injected sub-phase)
- Both reject the same alternatives for the right reasons (background watcher is architecturally impossible in Claude Code's model)
- Both correctly use opus for the highest-risk phase (building pipeline modification)
- Constraints are comprehensive and correctly identify backward compatibility as the top priority
- Both capture the "30-second latency budget" constraint, which is non-discoverable

**Weaknesses:**
- A's dependency DAG is more accurate than B's linear chain. The live-review agent template (Phase 1) unlocks both the building integration (Phase 2) AND the fix loop (Phase 4) -- these are independent streams. B serializes them unnecessarily, which means the building pipeline would execute them sequentially even though they could theoretically be parallelized in a future multi-track building mode.
- B's Phase 1 ("Live Check Selection Engine") creates a separate buildable artifact for check selection logic. This is problematic because check selection is an internal concern of the live-review agent -- it is HOW the agent works, not WHAT it produces. The pre-gate agent for Phase 2 (the agent template) should design the check selection as part of the agent's internals. B is over-decomposing.
- B's Phase 5 introduces a "Fix now / Proceed?" user prompt. This contradicts the building pipeline's autonomous execution model -- the building orchestrator dispatches subagents without interactive pauses. A's fix loop (Phase 4) with a 2-iteration cap is architecturally aligned with how building actually works.
- B's Phase 6 (register `--live` as a review preset that errors) is technically scope creep. The user framed this as a "third preset" but both plans correctly identified it as a building feature. A stops there. B adds a phase to register it in the review command just to produce an error message -- this is over-engineering.
- A's approach notes are more disciplined. "N.2b naming not renumbering -- user chose backward compatibility" is a clean non-discoverable decision. B's "plan-level setting, not per-phase" is similarly good. But B also includes "Use the core 14 checks as the always-on baseline, then layer skill-specific checks based on which skills the IMPLEMENT sub-phase loaded" -- this is getting into HOW territory. The decision is "use core 14 checks for speed." How to layer additional checks is pre-gate's job.

**Net assessment:** A is meaningfully stronger for Complex. It makes better architectural decomposition choices, keeps approach notes at the right level, and does not introduce anti-patterns (user prompts in autonomous pipelines, error-only features, HOW-level decomposition). B is a functional plan but would cause friction in the building pipeline due to the interactive pause in Phase 5 and the arguably unnecessary Phase 1 and Phase 6.

---

## Cross-Scenario Patterns

### Does the skill scale ceremony appropriately?

**Yes.** This is the skill's strongest feature. The ceremony gradient is clear and well-calibrated:

| Scenario | Track | Phases | Words/Phase | Approach Comparison | Self-Check |
|----------|-------|--------|-------------|--------------------|----|
| Simple | Simple | 1-2 | 50-75 | Skipped | Skipped |
| Medium | Medium | 3-4 | 100-150 | 2 approaches | Full |
| Complex | Complex | 6 | 100-150 | 2-3 approaches + rejected | Full |

The Simple track genuinely feels lightweight. The Complex track genuinely adds structural value (assumptions table, decision log, pre-mortem-style rejected approaches). No plan at any complexity level feels over- or under-planned relative to its task.

### Systematic strengths

1. **Track routing is bulletproof.** 6/6 plans classified correctly. The signal table leaves no ambiguity. This is the most important thing for the skill to get right, and it does.

2. **Template adherence is strong.** Both agents follow the correct template for their track. Simple plans do not have approach notes or file hints. Medium/Complex plans do. The templates are well-structured enough that agents fill them consistently.

3. **Non-discoverable preservation is good.** Both agents understand the concept and apply it. Approach notes consistently capture user decisions rather than implementation details, with minor exceptions in Agent B.

4. **Done-when criteria are verifiable across all plans.** No plan uses vague language like "well-designed" or "properly structured." Every criterion can be checked by a post-gate agent reading files and running commands.

5. **Model recommendations are consistent and defensible.** Both agents apply the keyword-based auto-detection correctly.

### Systematic weaknesses

1. **The WHAT-vs-HOW boundary is the skill's weakest point.** Agent B consistently drifts closer to implementation detail than Agent A. The skill's anti-rationalization table addresses this ("I should add implementation details so the subagent knows what to do"), but the guidance is negative (don't do X) rather than positive (here is the exact test for whether something belongs). The "Test: If the pre-gate agent could arrive at this decision by searching the codebase, it does NOT belong in approach notes" is good but only applies to approach notes, not to other fields like Constraints or phase decomposition itself.

2. **Phase decomposition discipline varies.** Agent B creates more phases than Agent A in both Medium and Complex scenarios. Some of B's extra phases are YAGNI (Medium Phase 4: docs) or HOW-level (Complex Phase 1: check selection engine). The skill's YAGNI Gate instruction exists but is not specific enough to prevent an agent from creating phases for internal implementation concerns rather than user-visible deliverables.

3. **The skill does not explicitly guide dependency structure.** A produces DAGs; B produces linear chains. For Complex tasks, the dependency structure matters because it informs the building orchestrator's scheduling. The skill's template has "Depends on / Unlocks" fields but no guidance on when to use DAGs vs. linear chains. This is a missed opportunity.

4. **The fix loop / user interaction pattern is not addressed.** B's Complex plan introduces an interactive "Fix now / Proceed?" prompt that would break the building pipeline's autonomous execution model. The skill does not explicitly state that plans should respect the building pipeline's non-interactive dispatch model. This is a gap because the plan is consumed by an automated pipeline, not a human.

---

## Skill Verdict

**FINAL-SKILL.md is ready to ship with minor fixes.** The core architecture is sound:

- Track routing is deterministic and correct
- Templates scale ceremony appropriately
- The contract model (WHAT/WHY vs HOW) is well-articulated
- Non-discoverable decision preservation works
- Done-when criteria are consistently verifiable
- Integration with the building pipeline (pre-gate, implementation, post-gate agents) is well-designed

The skill produces usable plans at all complexity levels from both agents. Agent A's plans are consistently better, but Agent B's plans are functional -- they would execute in the building pipeline without failures, just with some wasted work (unnecessary phases, slightly over-specified approach notes).

The gap between A and B is the skill's growth edge. A tighter skill would narrow this gap by adding specific guardrails for the weaknesses identified above.

---

## Specific Fixes Needed

### Fix 1: Strengthen the WHAT-vs-HOW boundary for phase decomposition

**Issue:** Agent B creates phases for internal implementation concerns (e.g., "Check Selection Engine" as a separate phase). The YAGNI Gate asks "Is this phase needed?" but does not distinguish between user-visible deliverables and internal implementation details.

**Proposed addition to YAGNI Gate section:**

> **Phase granularity test:** Each phase should produce a deliverable that is meaningful to the building orchestrator and verifiable by the post-gate agent. If a "phase" describes an internal component of another phase's deliverable (e.g., "selection logic" inside a "review agent"), it belongs in that phase's scope, not as a separate phase. Phases are contracts for WHAT to deliver, not a task breakdown of HOW to build.

### Fix 2: Add dependency structure guidance

**Issue:** No guidance on when to use DAGs vs. linear chains in "Depends on / Unlocks" fields.

**Proposed addition to Medium/Complex Track Template section:**

> **Dependency structure:** Use the simplest dependency chain that accurately models reality. If Phase 3 and Phase 4 can both start after Phase 2 completes (they do not depend on each other), express this as a DAG: both depend on Phase 2, and a later phase depends on both. Do not artificially linearize independent work -- it forces sequential execution in the building pipeline when parallel execution would be safe.

### Fix 3: Add pipeline compatibility note

**Issue:** Agent B's Complex plan introduces an interactive user prompt between sub-phases, which is incompatible with the building pipeline's autonomous dispatch model.

**Proposed addition to Crisis Invariants or the "What the Plan Specifies" section:**

> **Pipeline compatibility:** The building pipeline dispatches subagents autonomously. Plans must not introduce interactive user prompts between sub-phases (e.g., "Fix now or proceed?"). If a phase needs conditional behavior, express it as a constraint with a deterministic rule (e.g., "If findings > 0, re-dispatch implementation agent; max 2 iterations") rather than a user decision point.

### Fix 4: Tighten approach notes guidance for formulas and algorithms

**Issue:** Agent B includes specific formulas (PERT: E = (O + 4M + P) / 6) in approach notes. This is borderline -- the decision to USE three-point estimation is non-discoverable, but the formula itself is well-established and the pre-gate agent would find it through standard research.

**Proposed addition to "Approach Notes: The Non-Discoverable Exception" section, in the "Bad approach notes" list:**

> - "Use PERT formula: E = (O + 4M + P) / 6" (the decision to use three-point estimation is non-discoverable; the formula itself is discoverable from any estimation reference)

This reinforces the principle that approach notes capture the DECISION, not the DETAILS of how to execute it.

### Fix 5 (Optional): Add a note about phase count expectations per track

**Issue:** Agent B consistently creates more phases than Agent A. The skill states ranges (Simple: 1-2, Medium: 3-5, Complex: 5-7) but does not provide guidance on preferring fewer phases within the range.

**Proposed addition to Phase Count Guidance section:**

> **Prefer fewer phases within the range.** A 3-phase Medium plan is usually better than a 5-phase Medium plan -- fewer phases mean less pre-gate/post-gate overhead per phase and more substantial work per phase. Add phases only when scope boundaries genuinely require separate pre-gate discovery or when different model recommendations apply.
