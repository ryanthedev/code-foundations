# Systems Architect Analysis: Whiteboarding Skill Improvements

## Persona Lens

As a systems architect, I evaluate plans by asking: **Can an implementer take this plan and build the system without coming back to ask clarifying questions about boundaries, contracts, or sequencing?** The best implementation plans specify three things precisely: (1) what each module's interface contract is, (2) what the dependency graph between modules looks like, and (3) how effort should be allocated across sub-tasks based on their uncertainty and complexity. The current whiteboarding skill produces plans that are adequate for simple features but lack the structural rigor needed for systems with multiple interacting components.

## Key Research Findings

### 2505.16122 - Plan and Budget (ICLR 2026)
- **Reasoning miscalibration** is a pervasive failure mode: LLMs either *overthink* (verbose tangential reasoning on simple sub-tasks) or *underthink* (premature termination on hard sub-tasks). This directly applies to planning -- some plan sections get over-specified while critical hard sections get hand-waved.
- **Decomposition + difficulty-weighted budgeting** improves efficiency by up to 193.8%. A lightweight planner decomposes problems into sub-questions with complexity scores, then allocates reasoning effort proportionally.
- **Front-loading uncertainty reduction** is critical: early sub-questions (problem interpretation, strategy formation) have highest epistemic uncertainty. Cosine/polynomial decay schedules allocate more effort to early steps.
- **A weak planner + strong reasoner** pattern works: the decomposition planner should be deliberately weaker than the executor. It only needs to identify sub-questions and their difficulty, not solve them.
- **E3 metric (A^2/T)** penalizes accuracy loss quadratically while rewarding token reduction linearly -- correctness matters more than efficiency.

### 2505.18286 - Single-agent or Multi-agent? Why Not Both?
- **MAS advantages diminish as LLMs improve.** MetaGPT's HumanEval improvement dropped from 10.7% (ChatGPT) to 3.0% (Gemini-2.0-Flash). This means over-decomposing plans into many small agent-sized chunks may actually hurt execution.
- **Node/Edge/Path defect taxonomy** for diagnosing multi-agent failures: Node-level (bottleneck agent on hardest subtask), Edge-level (downstream overwhelmed by upstream context -- "overthinking"), Path-level (error propagation through agent chain).
- **Edge-level defects are the planning-relevant finding:** when a plan phase sends too much context to the next phase, the executing agent gets confused. Plans should specify minimal, precise handoff contracts between phases.
- **Hybrid cascade** (simple first, escalate on low confidence) reduces cost by up to 88.1% while improving accuracy 1.1-12%.

### 2505.13379 - Thinkless: LLM Learns When to Think
- **Adaptive compute allocation** per sub-task: models trained to self-select reasoning depth achieve 50-90% token reduction on easy tasks while preserving full reasoning on hard tasks.
- **Self-aware difficulty assessment** beats external routing: the model solving the problem is better at judging difficulty than an external classifier.
- Key insight for whiteboarding: **plan phases should be tagged with expected difficulty** so the executing model (during `/building`) can calibrate its effort per phase.

### 2505.19443 - Vibe Coding vs. Agentic Coding
- **Strategic Problem Formulation** hierarchy: logical thinking -> analytical thinking -> computational thinking -> procedural thinking -> PRD. This is a more rigorous version of the whiteboarding UNDERSTAND phase.
- **Five developer cognitive skills** for AI-assisted development: Thinking, Framework, Checkpoints, Debugging, Context. Plans should address which of these are exercised in each phase.
- **Hybrid architecture** combining human creative direction with autonomous execution is the recommended pattern -- directly maps to whiteboarding (creative) -> building (autonomous).

### 2505.20732 - SPA-RL: Stepwise Progress Attribution
- **Credit assignment in long-horizon tasks:** per-step progress scores that sum to the final reward. Applicable to plan design: each plan phase should have a measurable progress contribution toward the overall goal.
- **Fused rewards (progress + grounding):** combining "did this advance the goal?" with "was this action executable?" For plans: each phase should specify both its *value delivery* and its *executability preconditions*.

### 2505.06131 - LOG-Nav: Hierarchical Planning
- **Global-local planning hierarchy:** lightweight global topology plan for inter-module routing + dense local plans for intra-module execution. For whiteboarding: plans should have a high-level architecture sketch (global) plus detailed per-phase instructions (local).
- **Incremental local planning:** don't plan all local details upfront. Compute dense instructions for the next phase only as the agent approaches it. Current whiteboarding over-specifies all phases upfront.
- **Dual-level representation:** maintain both a topology graph (for routing) and a detailed representation (for execution). Plans need both a dependency DAG and per-phase detail.

### 2506.05020 - Hierarchical LLM for Multi-Robot Systems
- **Capability-typed task assignment:** when orchestrating heterogeneous agents, model each agent's capability type explicitly and assign tasks based on type matching. For plans: each phase should declare what capability it requires (haiku-level mechanical work vs. opus-level architectural reasoning).

## Current Skill Gaps

### Gap 1: No Dependency Graph Between Plan Phases
The current DETAIL phase (Phase 3) produces sequential sections with a `Dependencies` field, but there is no explicit dependency DAG. Phases are implicitly sequential. This means:
- Parallel-executable phases are serialized unnecessarily
- The building skill cannot reason about which phases are safe to reorder
- No way to identify the critical path

### Gap 2: No Complexity/Difficulty Assessment Per Phase
The current plan template assigns a `**Model:**` recommendation (haiku/sonnet/opus) based on task/file count heuristics, but does not estimate *difficulty* or *uncertainty*. Research (2505.16122, 2505.13379) shows that difficulty-aware allocation dramatically improves execution quality. The model heuristic is a weak proxy for actual difficulty.

### Gap 3: No Interface Contracts Between Phases
The current section template specifies `Files to create/modify` and `Dependencies` but not *what the output of this phase must look like for the next phase to succeed*. This leads to edge-level defects (2505.18286): downstream phases get overwhelmed or confused by upstream output that doesn't match expectations.

### Gap 4: No Explicit Risk/Uncertainty Identification
The current skill has a YAGNI gate (good) but no mechanism for identifying *where the hard problems are* in the plan. Research (2505.16122) shows that front-loading effort on high-uncertainty sub-tasks is the single highest-impact improvement for plan execution quality.

### Gap 5: Over-Specification of Later Phases
The current skill requires equal detail for all phases upfront. Research (2505.06131, 2505.16122) shows that later phases should be planned at lower resolution because: (a) earlier phases will produce information that changes later plans, and (b) detailed planning of low-uncertainty phases wastes planning effort.

### Gap 6: No Progress Metrics Per Phase
The current plan has no way to measure whether a phase succeeded beyond "files were modified." Research (2505.20732) shows that per-step progress attribution (measurable criteria that sum to overall success) dramatically improves execution.

### Gap 7: No Handoff Contract to Building
The plan file schema has no explicit section specifying *what the building skill should verify at each phase boundary*. The building skill's POST-GATE is generic, not plan-specific.

## Specific Proposals

### Proposal 1: Add Dependency DAG to Plan Output

- **Research basis:** 2505.06131 (hierarchical global-local planning -- global topology for inter-module routing), 2505.18286 (modeling MAS execution as directed graph G=(V,E) to diagnose defects)
- **Current gap:** Phases are implicitly sequential. No explicit dependency graph. Parallel opportunities are invisible.
- **Proposed change:** Add a `## Dependency Graph` section to the plan file schema (Phase 5 in SKILL.md), between `## Chosen Approach` and `## Implementation Checklist`:

```markdown
## Dependency Graph

```
Phase 1: Core data model
  |
  +---> Phase 2: API endpoints (depends on: Phase 1)
  |
  +---> Phase 3: UI components (depends on: Phase 1)
  |
  +-----+---> Phase 4: Integration tests (depends on: Phase 2, Phase 3)
```

**Critical path:** Phase 1 -> Phase 2 -> Phase 4
**Parallelizable:** Phase 2 and Phase 3
```

Also add to the DETAIL phase (Phase 3) instructions: "After defining all sections, draw the dependency graph. Identify the critical path (longest sequential chain) and any phases that can execute in parallel."

- **Expected impact:** Building skill can parallelize independent phases. Plans become explicit about sequencing constraints vs. arbitrary ordering. Critical path visibility helps the user understand where delays will propagate.

### Proposal 2: Add Difficulty/Uncertainty Rating Per Phase

- **Research basis:** 2505.16122 (complexity scores per sub-question drive budget allocation; front-loading uncertainty reduction yields up to 193.8% efficiency improvement), 2505.13379 (adaptive compute allocation reduces token usage 50-90% on easy tasks)
- **Current gap:** Model recommendation uses task/file count heuristics only. No difficulty or uncertainty assessment.
- **Proposed change:** Modify the Section Template in Phase 3 of SKILL.md to add difficulty assessment:

Replace the current section template with:
```markdown
### Section N: [Name]

**Goal:** [what this section accomplishes]
**Difficulty:** [LOW / MEDIUM / HIGH]
**Uncertainty:** [what we don't know that could change this plan]

**Files to create/modify:**
- `path/to/file.ts` - [what changes]

**Implementation details:**
- [specific function/class/pattern]

**Done when:** [measurable exit criteria]

**Dependencies:** [what must be done first]
```

Also add a new instruction after all sections are defined: "Review difficulty ratings. If the first phase is not the highest-difficulty phase, consider reordering: front-load the hardest, most uncertain work to reduce risk of late-stage replanning."

Modify the Model Recommendations logic to incorporate difficulty:
```
If difficulty == HIGH or uncertainty is significant:
  -> opus (regardless of task/file count)

If difficulty == LOW and tasks <= 2 AND files <= 2:
  -> haiku

Otherwise:
  -> sonnet
```

- **Expected impact:** Plans explicitly identify where the hard problems are. Model selection becomes difficulty-driven rather than size-driven. Building skill can allocate more effort (review cycles, test coverage) to HIGH-difficulty phases.

### Proposal 3: Add Interface Contracts Between Phases

- **Research basis:** 2505.18286 (edge-level defects occur when downstream agents are overwhelmed by upstream context; inter-agent communication needs explicit contracts), 2506.05020 (inter-agent information sharing requires explicit channels)
- **Current gap:** Phases specify what files they modify but not what they *produce* for downstream phases. The handoff between phases is implicit.
- **Proposed change:** Add to the Section Template in Phase 3:

```markdown
**Produces for downstream:** [what this phase outputs that later phases consume]
- [artifact 1]: [description, format, location]
```

Add a new validation step to the DETAIL phase: "For each dependency edge in the dependency graph, verify that the upstream phase's `Produces for downstream` includes everything the downstream phase needs. If there is a mismatch, the plan has an interface gap -- resolve it before proceeding."

- **Expected impact:** Prevents the most common plan execution failure: a later phase discovers it needs something the earlier phase didn't produce. Forces the planner to think about data flow, not just task ordering.

### Proposal 4: Add Progressive Detail Resolution

- **Research basis:** 2505.06131 (incremental local planning -- compute dense waypoints for the next segment only as the robot approaches it), 2505.16122 (front-loading compute budget on early sub-questions with highest uncertainty)
- **Current gap:** All phases receive equal detail in the plan. This wastes planning effort on later phases that will likely change based on earlier phase outcomes.
- **Proposed change:** Add a new instruction to Phase 3 (DETAIL):

```
### Detail Resolution by Phase Position

| Phase Position | Detail Level | What to Specify |
|---------------|-------------|-----------------|
| Phase 1 (first) | FULL | Complete implementation details, exact functions, edge cases, tests |
| Phase 2-3 | STANDARD | Files, key decisions, patterns to follow, exit criteria |
| Phase 4+ | SKETCH | Goal, approach direction, key constraints. Details TBD during building. |

**Rationale:** Earlier phases have the highest uncertainty. Investing planning effort there yields the highest return. Later phases will be re-planned during building based on what earlier phases actually produced.
```

- **Expected impact:** Reduces planning time by ~30% (less detail on later phases). Improves plan accuracy because later phases aren't locked into assumptions that earlier phases may invalidate. Aligns with the building skill's phased execution model.

### Proposal 5: Add Measurable Progress Criteria Per Phase

- **Research basis:** 2505.20732 (per-step progress attribution -- scores that sum to final reward enable credit assignment; fused progress + grounding rewards improve execution), 2505.16122 (E3 metric penalizes accuracy loss quadratically)
- **Current gap:** The current section template has no exit criteria. The only implicit check is whether files were modified. No way to measure partial progress.
- **Proposed change:** The `**Done when:**` field proposed in Proposal 2 addresses this partially. Strengthen it by adding a progress contribution estimate to the plan summary:

Add to the VALIDATE phase (Phase 4), after the full plan review:

```markdown
## Progress Breakdown

| Phase | Progress Contribution | Cumulative |
|-------|----------------------|------------|
| Phase 1: Core data model | 30% | 30% |
| Phase 2: API endpoints | 25% | 55% |
| Phase 3: UI components | 25% | 80% |
| Phase 4: Integration tests | 20% | 100% |

**Checkpoint rule:** If cumulative progress falls below expected at any phase boundary, STOP and reassess remaining phases before continuing.
```

- **Expected impact:** Enables the building skill to detect when execution is off-track (e.g., Phase 1 took 60% of total effort, suggesting the plan underestimated complexity). Provides a natural escalation signal for when to invoke the user.

### Proposal 6: Add Risk Register to Plan Output

- **Research basis:** 2505.16122 (epistemic vs. aleatoric uncertainty decomposition -- reducible vs. irreducible uncertainty require different handling), 2505.19933 (situational risks are harder to detect than obvious risks -- LLMs fail at subtle hazard anticipation)
- **Current gap:** The plan has a `Notes` section for "edge cases" and "gotchas" but no structured risk identification. The YAGNI gate filters out unnecessary work but doesn't identify necessary-but-risky work.
- **Proposed change:** Add a `## Risk Register` section to the plan file schema, after `## Test Plan`:

```markdown
## Risk Register

| Risk | Likelihood | Impact | Mitigation | Phase Affected |
|------|-----------|--------|------------|---------------|
| [external API rate limits may block batch processing] | Medium | High | Implement retry with backoff; add queue | Phase 2 |
| [unclear if existing auth system supports OAuth2 scopes] | High | Medium | Spike in Phase 1 to verify; fallback to custom scopes | Phase 1 |
```

Add instruction to the EXPLORE phase: "After choosing an approach, identify 2-5 risks. For each risk, classify as reducible (can be resolved with more investigation) or irreducible (must be mitigated). Reducible risks should be assigned to early phases as spikes."

- **Expected impact:** Forces the planner to think adversarially about what could go wrong. Reducible risks become Phase 1 investigation tasks (front-loading uncertainty reduction). Irreducible risks get explicit mitigations. Building skill can check mitigations were implemented.

### Proposal 7: Add Phase Handoff Contracts for Building Skill

- **Research basis:** 2505.18286 (hybrid cascade paradigm -- explicit confidence thresholds for escalation between system tiers), 2505.19443 (explicit handoff protocols prevent duplicated or conflicting work between human and agent)
- **Current gap:** The plan file has an `Execution Log` section but no specification of what the building skill should verify at each phase boundary.
- **Proposed change:** Add a `## Phase Gate Criteria` section to the plan file schema:

```markdown
## Phase Gate Criteria

### After Phase 1: Core Data Model
- [ ] All model types compile/pass type checking
- [ ] Migration runs successfully on empty database
- [ ] Downstream phases can import the types they need

### After Phase 2: API Endpoints
- [ ] All endpoints return correct status codes for happy path
- [ ] Error responses match API contract
- [ ] Phase 3 can call endpoints from UI layer
```

Add to DETAIL phase: "For each phase, define 2-4 gate criteria that must be true before the next phase begins. Gate criteria should be *verifiable* (can be checked by running a command or reading code), not subjective."

- **Expected impact:** Building skill gets plan-specific quality gates instead of relying only on generic checklist-based gates. Prevents the common failure where Phase 2 starts with broken Phase 1 output. Makes the plan-to-building handoff contract explicit.

## Priority Ranking

| Rank | Proposal | Impact | Effort to Implement |
|------|----------|--------|-------------------|
| 1 | **Proposal 2: Difficulty/Uncertainty Rating** | Highest. Directly enables better model selection and effort allocation. Research shows this is the single highest-impact improvement (193.8% efficiency gain in 2505.16122). | Low -- add fields to template |
| 2 | **Proposal 1: Dependency DAG** | High. Unlocks parallelization and critical path visibility. Every systems architect draws this first. | Low -- add section to schema |
| 3 | **Proposal 7: Phase Gate Criteria** | High. Bridges the gap between planning and execution. Without this, plans are aspirational documents rather than executable contracts. | Medium -- requires coordination with building skill |
| 4 | **Proposal 3: Interface Contracts** | High. Prevents the most common execution failure (missing handoff artifacts). | Low -- add field to template |
| 5 | **Proposal 6: Risk Register** | Medium-High. Front-loads uncertainty reduction. Changes planning from optimistic to realistic. | Low -- add section to schema |
| 6 | **Proposal 4: Progressive Detail Resolution** | Medium. Reduces planning overhead and prevents premature commitment. | Low -- add instruction table |
| 7 | **Proposal 5: Progress Metrics** | Medium. Enables runtime progress tracking during building. | Low -- add table to schema |

**Implementation strategy:** Proposals 1, 2, 4, and 6 can be implemented independently (no cross-skill changes). Proposals 3 and 7 are most valuable when the building skill also reads and enforces them. Proposal 5 requires the building skill to check cumulative progress.

**Recommended first batch:** Proposals 2, 1, and 6 (difficulty rating, dependency DAG, risk register). These three changes transform the plan from a linear task list into a structured execution blueprint with explicit uncertainty handling. They require no changes to the building skill and immediately improve plan quality.
