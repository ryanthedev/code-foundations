# Agile Coach Analysis: Whiteboarding Skill Improvements

## Persona Lens

As an Agile coach, the principles most relevant to producing plans that lead to successful incremental delivery are:

1. **Vertical slicing** -- every planned phase should deliver observable, testable value, not just set up scaffolding for later phases.
2. **INVEST criteria for work items** -- each task in a plan should be Independent, Negotiable, Valuable, Estimable, Small, and Testable.
3. **Progressive refinement** -- plans should decompose coarse goals into fine-grained actions through intermediate abstraction levels, not in a single leap.
4. **Fail fast and adapt** -- when a plan encounters infeasibility, the response should be goal relaxation (adjust what "done" means) rather than silent failure.
5. **Context scoping** -- planners (human or AI) perform worse when overwhelmed with irrelevant context; each phase should see only what it needs.
6. **Dual-track validation** -- every planned action needs two checks: "can this be done?" (feasibility) and "should this be done?" (consistency with the goal).

These principles map directly onto findings from the research papers reviewed below.

## Key Research Findings

### Paper 2506.21030 (STEP Planner) -- Hierarchical Subgoal Decomposition
**Relevance: HIGH**

The core finding is that LLMs fail at long-horizon planning due to two gaps:
- **Contextual gap**: Too much irrelevant history in context degrades reasoning. Flat action sequences for >5-step tasks drop success rates to 1-6%.
- **Logical gap**: Jumping directly from abstract instruction to primitive action is too large a leap for reliable planning.

The solution -- a hierarchical subgoal tree where each node only sees its parent and siblings -- achieved 40% success rate vs 6% for flat methods. The tree structure excludes cross-branch history, keeping the planner focused.

Key mechanism: **dual termination criteria** at each leaf node:
1. **Mappability** -- can this subgoal be mapped to exactly one action?
2. **Consistency** -- does the action satisfy constraints and align with prior subgoals?

When consistency fails, the system backtracks to the parent and replans, rather than forcing through a bad decomposition.

### Paper 2506.15828 (ContextMatters) -- Goal Relaxation
**Relevance: HIGH**

When a plan is infeasible, this paper introduces **bidimensional goal relaxation**:
- **Functionality axis**: relax *what* to achieve (semantic equivalents -- "fork unavailable, try spoon")
- **Feasibility axis**: relax *where/how* to achieve it (alternative locations/methods)

The key insight for whiteboarding: **treat plan failure as a signal to modify the goal, not just retry**. This achieved +52.45% success rate over baselines. The relaxation is progressive and minimal -- find the smallest change that preserves user intent while making the plan executable.

### Paper 2506.06677 (RoboCerebra) -- Long-Horizon Planning Evaluation
**Relevance: MEDIUM**

Demonstrates that benchmarks with short horizons (~500 steps) do not reveal the failures that emerge at longer horizons (~3000 steps). The three critical dimensions for evaluating planning quality are:
1. **Planning** -- ability to decompose high-level goals into subtask sequences
2. **Reflection** -- ability to assess completion status
3. **Memory** -- ability to retain and use long-term context

Applied to whiteboarding: plans need explicit reflection checkpoints and memory management (what context carries forward vs what gets pruned).

### Paper 2506.08292 (ECON) -- Multi-Agent Coordination
**Relevance: MEDIUM**

Demonstrates that belief-based coordination (each agent reasons about others' likely strategies) outperforms expensive direct communication by 11.2% while using 21.4% fewer tokens. The relevant principle: when generating alternative approaches in Phase 2 of whiteboarding, the skill should model trade-offs as beliefs about how constraints interact, rather than just listing pros/cons.

### Paper 2506.21734 (HRM) -- Adaptive Compute for Reasoning
**Relevance: LOW-MEDIUM**

The key transferable insight is **adaptive computational time** -- allocating more thinking effort to harder problems and less to easy ones. The whiteboarding skill already has complexity classification (simple/medium/complex) but does not adjust the *depth* of plan decomposition accordingly.

### Papers 2506.17221, 2507.00432, 2507.02029, 2507.16815
**Relevance: LOW** -- These focus on embodied navigation, training methodology, and robotic vision-language models. No directly applicable findings for whiteboarding skill design.

## Current Skill Gaps

Analyzing the whiteboarding SKILL.md through the lens of these research findings:

### Gap 1: Flat Phase Structure (No Hierarchical Decomposition)
Phase 3 (DETAIL) asks the planner to "break into sections" with 200-300 words each, but provides no guidance on decomposition depth. The Section Template jumps from "Goal" directly to "Implementation details" -- a single logical leap. STEP Planner (2506.21030) shows this is exactly the pattern that fails at scale: success rates drop to 1-6% when going from abstract instruction to primitive actions in one step.

### Gap 2: No Feasibility Validation of Plan Steps
The current skill validates user *intent* (Phase 4: VALIDATE) but never validates whether planned steps are actually *feasible* given the codebase. There is no equivalent of ContextMatters' (2506.15828) consistency check or STEP's dual termination criteria. A plan phase might specify "modify `path/to/file.ts`" for a file that does not exist, or propose an approach that conflicts with codebase constraints.

### Gap 3: No Goal Relaxation Mechanism
When the user's goal turns out to be partially infeasible (e.g., "add real-time notifications" when the codebase has no WebSocket infrastructure), the skill has no structured way to relax the goal. It either builds the whole stack or asks the user open-ended questions. ContextMatters (2506.15828) shows that systematic bidimensional relaxation dramatically improves planning success.

### Gap 4: No Context Pruning Between Phases
The skill accumulates all context from Phase 1 through Phase 5. STEP Planner (2506.21030) demonstrates that pruning irrelevant context at each decomposition level improves success rates by 32 percentage points. The whiteboarding skill should explicitly define what context each phase needs and what should be excluded.

### Gap 5: No Reflection or Completion Checking
RoboCerebra (2506.06677) identifies reflection (assessing completion status) as a critical planning dimension. The current whiteboarding skill has no mechanism for checking whether a section's goal is actually achievable by its listed tasks, or whether the cumulative sections actually satisfy the original problem statement.

### Gap 6: Complexity Does Not Affect Decomposition Depth
The skill classifies complexity (simple/medium/complex) but only adjusts *question count*. HRM (2506.21734) and STEP (2506.21030) both show that harder tasks need deeper decomposition hierarchies, not just more questions. A complex feature plan should have sub-phases within phases, while a simple one should stay flat.

## Specific Proposals

### Proposal 1: Hierarchical Section Decomposition with Dual Validation

- **Research basis:** 2506.21030 -- STEP achieves 40% success rate vs 6% for flat methods by decomposing through intermediate abstraction levels; dual termination criteria (mappability + consistency) prevent premature or infeasible actions.
- **Current gap:** Phase 3 (DETAIL) uses a flat section template that jumps from "Goal" to "Implementation details" in one logical step. No validation that each task maps to exactly one implementable change.
- **Proposed change:** Replace the Section Template in Phase 3 with a hierarchical decomposition protocol:

```markdown
### Section Decomposition Protocol

For each section, apply coarse-to-fine decomposition:

**Level 1 (Goal):** What does this section accomplish?
**Level 2 (Subgoals):** What 2-4 subgoals compose this section?
**Level 3 (Tasks):** For each subgoal, what specific file changes are needed?

Before finalizing each task, apply dual validation:
1. **Mappability:** Can this task be completed in a single coding action?
   - If NO: decompose further (add sub-tasks)
   - If YES: proceed to consistency check
2. **Consistency:** Does this task align with codebase patterns, dependencies, and constraints?
   - If NO: replan the parent subgoal
   - If YES: include in plan

**Decomposition depth by complexity:**
| Complexity | Max Levels | Tasks per Section |
|-----------|-----------|------------------|
| Simple    | 2 (Goal → Tasks) | 1-3 |
| Medium    | 3 (Goal → Subgoals → Tasks) | 3-6 |
| Complex   | 3-4 (Goal → Subgoals → Sub-subgoals → Tasks) | 5-10 |
```

- **Expected impact:** Plans produce tasks that are each independently implementable and verified against codebase constraints, reducing rework during building. Mirrors STEP's 34-percentage-point improvement over flat decomposition.

### Proposal 2: Feasibility Gate with Goal Relaxation

- **Research basis:** 2506.15828 -- ContextMatters achieves +52.45% success rate by relaxing infeasible goals along two axes (functionality and feasibility) rather than failing outright.
- **Current gap:** No mechanism for handling infeasible requirements. The YAGNI Gate asks "is this needed?" but never asks "is this achievable given the codebase?"
- **Proposed change:** Add a Feasibility Gate after approach selection in Phase 2, and a structured relaxation protocol:

```markdown
### Step 2c: Feasibility Gate (After Approach Selection)

For the chosen approach, verify feasibility against the codebase:

**Check each requirement against reality:**
| Requirement | Codebase Support | Status |
|------------|-----------------|--------|
| [requirement] | [what exists] | FEASIBLE / PARTIAL / INFEASIBLE |

**If any requirement is INFEASIBLE, apply goal relaxation:**

1. **Functionality relaxation** (adjust WHAT):
   - Can a simpler version achieve the core intent?
   - "Real-time notifications" → "Polling-based notifications" (preserves intent, removes WebSocket dependency)

2. **Feasibility relaxation** (adjust HOW):
   - Can existing infrastructure achieve a partial version?
   - "New auth system" → "Extend existing auth with new role" (preserves intent, reuses existing code)

**Relaxation rule:** Find the MINIMAL modification that preserves user intent while making the plan executable. Present relaxed alternatives to user for approval.

**Anti-pattern:** Do NOT silently scope-cut. Present the trade-off explicitly:
"[Original goal] requires [missing infrastructure]. Alternatives:
- A: [relaxed goal] using [existing infrastructure] — delivers [X% of value]
- B: [full goal] requiring [additional work] — adds [N] phases"
```

- **Expected impact:** Plans become executable on first attempt rather than stalling during building when infeasible steps are discovered. Users make informed decisions about scope early.

### Proposal 3: Context Scoping Per Phase

- **Research basis:** 2506.21030 -- Tree structure that excludes cross-branch history improved success rate by 32 percentage points. Context pruning is as important as logical decomposition.
- **Current gap:** All phases accumulate context. Phase 5 (SAVE) includes everything from Phase 1 through Phase 4. When the building command loads this plan, it gets the full blob.
- **Proposed change:** Add explicit context scoping to the Plan File Schema:

```markdown
### Context Scoping

Each phase in the plan file should include a **Context** block specifying what the implementer needs to know:

**Phase context template:**
```
### Phase N: [Name]
**Context:** [1-2 sentences: what this phase needs to know from prior phases]
**Excludes:** [what context from other phases is NOT relevant here]
```

**Rule:** Each phase's context block should reference ONLY:
- Its own goal and tasks
- Direct dependencies from prior phases (parent context)
- Relevant constraints

**Exclude:** Implementation details of sibling phases, rejected approaches, discovery questions and answers (unless directly relevant).
```

- **Expected impact:** When the building command executes each phase, the agent starts with focused context rather than the entire planning history. Mirrors STEP's finding that context pruning alone is worth +32 percentage points.

### Proposal 4: Vertical Slice Validation

- **Research basis:** 2506.06677 -- RoboCerebra identifies that planning, reflection, and memory are three distinct dimensions of planning quality. Current skill only addresses planning. Also informed by 2506.21030's finding that "Additional/Missing Steps" (27% of errors) is the primary failure mode.
- **Current gap:** No mechanism to verify that planned sections form a vertical slice (end-to-end deliverable) rather than horizontal layers (all backend, then all frontend). No reflection step to check section completeness against the original goal.
- **Proposed change:** Add a Vertical Slice Check and Reflection Gate to Phase 4 (VALIDATE):

```markdown
### Vertical Slice Check (Before Full Plan Review)

For each section, verify it delivers observable value:

| Section | User-Observable Output | Can Be Tested Independently? |
|---------|----------------------|----------------------------|
| [name]  | [what the user sees/can verify] | YES/NO |

**Red flags:**
- Section has no testable output → Split or merge with adjacent section
- Section depends on 3+ other sections before it's testable → Too horizontal, restructure as vertical slice
- First testable output appears in Section 3+ → Reorder to deliver value earlier

### Reflection Gate

After listing all sections, verify completeness:

**Forward check:** Do all sections together satisfy the original problem statement?
- List each success criterion from Phase 1
- Map each to the section(s) that deliver it
- Any unmapped criterion = missing section

**Backward check:** Does each section contribute to at least one success criterion?
- Any section that maps to zero criteria = candidate for YAGNI removal
```

- **Expected impact:** Plans produce incrementally deliverable value. Each phase of the building command produces something the user can see and verify, rather than accumulating invisible infrastructure. Reduces "Additional/Missing Steps" errors.

### Proposal 5: Backtrack-on-Failure Protocol for Building Handoff

- **Research basis:** 2506.21030 -- STEP's backtrack-on-failure architecture re-plans parent nodes when child decompositions fail, preventing cascading errors. 2506.15828 -- ContextMatters treats failure as a relaxation cue, not a dead end.
- **Current gap:** The plan file has no guidance for what to do when a phase fails during building. The Execution Log section is blank. There is no structured recovery protocol.
- **Proposed change:** Add a Failure Recovery section to the Plan File Schema:

```markdown
## Failure Recovery

For each phase, define the recovery action if implementation fails:

| Phase | Failure Signal | Recovery Action |
|-------|---------------|-----------------|
| Phase 1 | [what would indicate failure] | [replan/relax/skip] |
| Phase 2 | [what would indicate failure] | [replan/relax/skip] |

**Recovery protocol:**
1. If a task within a phase fails: re-examine the parent subgoal, not the task
2. If a phase fails entirely: relax the phase's goal (apply Proposal 2 relaxation)
3. If relaxation is insufficient: escalate to user with options

**Anti-pattern:** Do NOT retry the same approach. If it failed, the decomposition was wrong -- replan at a higher level.
```

- **Expected impact:** Building becomes resilient to mid-execution failures. Instead of stalling on infeasible steps, the agent has a structured protocol for adaptation that preserves the plan's overall intent.

### Proposal 6: Adaptive Decomposition Depth Signal

- **Research basis:** 2506.21734 -- HRM demonstrates that adaptive computational time (allocating more compute to harder problems) improves efficiency by ~50% on easy problems while maintaining quality on hard ones. 2506.21030 -- STEP shows minimal advantage on short-simple tasks (10/10 vs 8-10/10) but massive advantage on long-complex ones (6/10 vs 1/10).
- **Current gap:** Complexity classification only affects question count (2-3 for simple, 6-8 for complex). It does not affect decomposition depth, section detail, or plan structure.
- **Proposed change:** Extend the complexity classification to control plan structure:

```markdown
### Complexity-Driven Plan Structure

| Complexity | Questions | Decomposition Depth | Section Detail | Approach Count |
|-----------|----------|-------------------|---------------|---------------|
| Simple    | 2-3      | 2 levels (Goal → Tasks) | 100-150 words | 2 approaches |
| Medium    | 4-5      | 3 levels (Goal → Subgoals → Tasks) | 200-300 words | 2-3 approaches |
| Complex   | 6-8      | 3-4 levels (Goal → Subgoals → Sub-subgoals → Tasks) | 250-400 words | 3 approaches + feasibility gate |

**Simple plans:** Skip feasibility gate, skip context scoping, use flat sections.
**Complex plans:** Require feasibility gate, require context scoping per phase, require vertical slice check, require failure recovery protocol.
```

- **Expected impact:** Simple tasks get planned quickly without unnecessary ceremony. Complex tasks get the deeper decomposition and validation they need. Mirrors HRM's finding that adaptive compute allocation saves ~50% on easy problems.

## Priority Ranking

Ranked by expected impact on plan quality and downstream building success:

1. **Proposal 1: Hierarchical Section Decomposition** -- Addresses the root cause of plan failure (flat decomposition). Research shows 34pp improvement. This is the single highest-leverage change.

2. **Proposal 2: Feasibility Gate with Goal Relaxation** -- Catches infeasible plans before they reach building. Research shows +52.45% success rate. High impact because infeasible plans waste the most time.

3. **Proposal 4: Vertical Slice Validation** -- Ensures plans deliver incrementally. Without this, plans often front-load infrastructure and back-load value, making early phases impossible to verify.

4. **Proposal 6: Adaptive Decomposition Depth** -- Right-sizes ceremony to task complexity. Prevents over-planning simple tasks and under-planning complex ones. Easy to implement alongside Proposal 1.

5. **Proposal 3: Context Scoping Per Phase** -- Improves building execution quality. Research shows 32pp from context pruning alone. Lower priority because it primarily affects the downstream building command, not the plan itself.

6. **Proposal 5: Backtrack-on-Failure Protocol** -- Important for resilience but has less impact than getting the initial plan right. This is a safety net; proposals 1-2 reduce the need for it.
