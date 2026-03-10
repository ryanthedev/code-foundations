# Military Strategist Analysis: Whiteboarding Skill Improvements

## Persona Lens

Military planning doctrine -- particularly the Military Decision Making Process (MDMP) and the OODA loop (Observe, Orient, Decide, Act) -- shares deep structural parallels with software feature planning. Both operate under uncertainty, both require decomposition of complex objectives into executable phases, and both must anticipate adversarial conditions (in software: changing requirements, integration failures, environment drift). The core military planning principles that translate directly to better software implementation plans are:

1. **Commander's Intent** -- a clear, concise statement of the desired end-state that allows subordinates to adapt when the plan breaks down. Software plans lack this; they describe *what* to build but not *why it matters* at a level that enables autonomous course-correction during implementation.

2. **Branches and Sequels** -- pre-planned contingencies (branches = what to do if conditions change; sequels = what to do after success/failure). Current whiteboarding produces a single linear plan with no fallback positions.

3. **Intelligence Preparation of the Battlefield (IPB)** -- systematic analysis of the operating environment before planning. The whiteboarding skill's Phase 1 pattern discovery is a form of IPB, but it lacks the structured threat/risk assessment that IPB demands.

4. **Phased Operations with Decision Points** -- military operations define explicit decision points where commanders assess whether to continue, shift to a branch, or abort. The current skill has phases but no decision points within the plan output itself.

5. **Running Estimate** -- a continuously updated assessment that tracks assumptions, facts, and open questions throughout planning. The whiteboarding skill captures a snapshot (problem statement, constraints) but does not maintain a living estimate.

---

## Key Research Findings

### 2508.19076 - HiPlan: Hierarchical Planning with Adaptive Global-Local Guidance
**Core finding:** Plans need both macro-level milestone guides (global direction) and micro-level step-wise hints (local adaptation). High-level planning alone "exhibits limited flexibility when encountering unexpected execution errors or adapting to dynamic environmental changes." Step-wise planning alone "frequently leads the agent to lose sight of the overall task structure, making it prone to inefficient or locally optimal behaviors."

**Key mechanism:** A milestone library built from prior successful demonstrations enables structured experience reuse at the *milestone level* -- not full-task level (too noisy) and not action-level (too context-dependent). Each milestone includes: description, trajectory fragment, and insights.

**Quantitative result:** 4-23% absolute success rate improvement on ALFWorld by combining global milestone guides with local step-wise hints versus either alone.

**Relevance to whiteboarding:** The current skill produces a flat checklist of implementation phases. It lacks the dual-scale structure (milestones + adaptive hints) that HiPlan shows is critical for long-horizon task completion. Plans should explicitly separate the "roadmap" (milestones with success criteria) from the "implementation details" (step-wise specifics that may change).

### 2508.00083 - Survey on Code Generation with LLM-based Agents
**Core finding on planning strategies:**
- Self-Planning (plan-then-implement) works for linear tasks but fails for multi-path problems.
- Tree-structured planning (CodeTree/DARS) branches at decision points and prunes based on execution results -- directly applicable to plans with technical uncertainty.
- Hierarchical workflows (PairCoder pattern: Navigator proposes strategy, Driver implements, Navigator reviews feedback) outperform flat pipelines for complex tasks.

**Core finding on reflection:** "The gap between code LLMs and code agents is primarily the ability to reflect on and fix outputs." Plans that do not build in reflection points produce worse outcomes.

**Core finding on context management:** "For multi-agent systems, the limiting factor is not individual agent intelligence but shared context management." Plans must specify what context each implementation phase needs and how it flows between phases.

**Relevance to whiteboarding:** The current skill produces implementation checklists without decision points, reflection gates, or context flow specifications. The research shows these are not optional niceties -- they are the primary differentiators between successful and failed complex implementations.

### 2509.08222 - ExRAP: Exploratory Retrieval-Augmented Planning
**Core finding:** Plans for multi-task environments must integrate exploration (gathering information) with exploitation (executing tasks). Planning each task independently produces 31% more wasted steps (9.2 pending steps vs 7 for integrated planning).

**Key mechanism:** Decompose conditional instructions into query (condition to check) and execution (task to perform). This separation enables efficient evaluation without full task planning for unmet conditions.

**Core finding on knowledge decay:** Environmental observations become less reliable over time. Plans must account for information staleness -- assumptions made during planning may not hold during implementation.

**Relevance to whiteboarding:** The current skill gathers information in Phase 1 (UNDERSTAND) and Phase 2 (EXPLORE) but treats this information as permanently valid through implementation. Plans should explicitly tag assumptions with confidence levels and identify which assumptions need re-verification before dependent phases execute.

### 2509.00189 - HiVA: Self-Organized Hierarchical Variable Agent
**Core finding:** Starting from the simplest possible configuration and evolving complexity through feedback outperforms starting with a complex predefined structure. "Singleton-to-Complex Evolution" avoids premature architectural commitments.

**Relevance to whiteboarding:** The current skill always produces a full multi-phase plan. For simpler features, this is overhead. For complex features, the initial plan may commit to the wrong structure. Plans should identify which structural decisions can be deferred until implementation feedback is available.

### 2509.02547 - The Landscape of Agentic RL for LLMs
**Core finding on planning as capability:** Planning is one of six core agentic capabilities (alongside tool use, memory, reasoning, self-improvement, perception). Effective planning requires: (a) combining sparse task-completion rewards with dense step-level progress signals, and (b) distinguishing between text outputs and action outputs.

**Core finding on credit assignment:** Long horizons with sparse rewards cause credit assignment failure -- agents "ignore early actions that enable late success." This directly maps to implementation plans where foundational work in Phase 1 enables success in Phase 4, but the connection is invisible in flat checklists.

**Relevance to whiteboarding:** Plans should explicitly trace dependencies between phases so that foundational work is understood as enabling later success, not just as ceremony.

### 2508.10428 - SC2Arena and StarEvolve
**Core finding:** Self-improvement through structured reflection on outcomes -- specifically, extracting successful patterns from wins and generating failure analysis from losses -- improves strategic planning. "Reflection analyses correctly identify failure causes" is a quality gate.

**Relevance to whiteboarding:** The current skill has no mechanism for incorporating lessons from previous plan executions. Plans should reference prior plan outcomes when available.

### 2508.05606 - Uni-CoT (Low relevance, rating 2)
Primarily about multimodal reasoning. Not directly applicable to whiteboarding.

### 2508.07642 - Mixture of Skills VLN (Low relevance, rating 2)
The skill decomposition pattern (breaking complex capability into specialized sub-skills with mixture routing) is interesting but applies more to the building execution than to the planning phase.

### 2508.09444 - DAgger Diffusion Navigation (Low relevance, rating 2)
Distribution shift concept (learned policies encounter unfamiliar states at execution time) has a loose analogy to plans encountering unforeseen implementation states, but the paper's contributions are too domain-specific to inform concrete proposals.

---

## Current Skill Gaps

Analyzing the whiteboarding skill (SKILL.md, 533 lines) through the lens of both military planning doctrine and the research findings, I identify seven gaps:

### Gap 1: No Commander's Intent
The plan output schema (Phase 5) has `Context`, `Constraints`, `Chosen Approach`, and `Implementation Checklist` -- but no explicit statement of desired end-state that enables autonomous adaptation. If the implementer hits an obstacle, the plan gives no guidance on which constraints are flexible vs. rigid.

### Gap 2: No Decision Points or Branch Plans
The implementation checklist is a linear sequence of phases. There is no mechanism for: "If X fails, do Y instead" or "Before starting Phase 3, verify that assumption Z still holds." HiPlan (2508.19076) shows that plans without adaptive checkpoints fail significantly more often on long-horizon tasks.

### Gap 3: No Assumption Tracking
The skill captures constraints and success criteria but does not track *assumptions* -- things believed to be true that the plan depends on. ExRAP (2509.08222) demonstrates that assumptions decay over time and must be explicitly tracked with confidence levels.

### Gap 4: No Context Flow Between Phases
The plan schema lists phases with tasks and files, but does not specify what information each phase produces that subsequent phases need. The code agent survey (2508.00083) identifies context management as "the limiting factor" for complex multi-step work.

### Gap 5: No Reflection/Retrospective Integration
The skill does not reference prior plan outcomes. SC2Arena (2508.10428) shows that structured reflection on prior successes and failures materially improves future planning quality. The skill has no mechanism to learn from previous whiteboarding sessions.

### Gap 6: No Risk Assessment
Military planning's IPB requires identifying threats and risks. The current skill asks "What could go wrong?" as question 5 (Medium complexity only), but this answer is not structured into the plan output. It should be a first-class section with mitigations.

### Gap 7: Flat Phase Structure (No Milestone Hierarchy)
HiPlan (2508.19076) demonstrates that milestone-level abstraction (between task-level and action-level) is the optimal granularity for plan reuse and adaptation. The current plan format uses phases with flat task lists but does not distinguish milestones (success-criteria-bearing waypoints) from implementation steps (specific actions).

---

## Specific Proposals

### Proposal 1: Add Commander's Intent to Plan Schema

- **Research basis:** HiPlan (2508.19076) -- milestone action guides provide "clear overall direction" that prevents agents from "losing sight of the overall task structure." Code agent survey (2508.00083) -- hierarchical Navigator/Driver pattern succeeds because the Navigator maintains strategic direction while the Driver executes.
- **Current gap:** Gap 1 -- No statement of desired end-state or priority hierarchy for constraints.
- **Proposed change:** Add a `## Commander's Intent` section to the plan file schema in Phase 5, between `## Context` and `## Constraints`:

```markdown
## Commander's Intent

**End-state:** [1 sentence: what does the system look like when this is done?]

**Priority of constraints:**
1. [Most important -- never sacrifice this]
2. [Important -- sacrifice only if #1 requires it]
3. [Desirable -- sacrifice if needed for #1 or #2]

**Key judgment:** [The single most important decision the implementer will face, and how to decide]
```

Also add to Phase 3 (DETAIL) a mandatory question: "What is the single most important thing the implementer must not compromise on?"

- **Expected impact:** When the implementer encounters an obstacle during `/code-foundations:building`, they can consult Commander's Intent to make autonomous decisions about trade-offs rather than stalling or making arbitrary choices. This directly addresses the "unknown unknowns" problem from APOSD.

### Proposal 2: Add Decision Points and Branch Plans to Phase Structure

- **Research basis:** HiPlan (2508.19076) -- "High-level planning methods often exhibit limited flexibility when encountering unexpected execution errors." Code agent survey (2508.00083) -- tree-structured planning "branches at decision points; prunes based on execution results." ExRAP (2509.08222) -- integrated planning with condition checking reduces wasted steps by 24%.
- **Current gap:** Gap 2 -- Linear phase structure with no contingency mechanism.
- **Proposed change:** Add a `Decision Points` subsection to each implementation phase in the plan schema:

```markdown
### Phase N: [Name]
**Model:** [recommended model]
- [ ] [Specific task with file path]
- [ ] [Specific task with file path]

**Files:**
- `path/to/file.ts`

**Decision point before Phase N+1:**
- **Verify:** [What must be true to proceed]
- **If false:** [Branch action -- alternative approach, reduced scope, or abort criteria]

**Details:**
[Implementation specifics]
```

Also add to Phase 3 (DETAIL), after the YAGNI gate, a new gate:

```
### Contingency Gate

For each phase, ask:
- What could prevent this phase from succeeding?
- If it fails, is there a fallback approach?
- What would we verify before committing to the next phase?

If no contingency identified → State "No contingency needed; phase is low-risk."
```

- **Expected impact:** Plans become resilient to implementation surprises. The building command can check decision points between phases rather than blindly proceeding. This is the software equivalent of branches and sequels in military planning.

### Proposal 3: Add Assumption Register to Plan Output

- **Research basis:** ExRAP (2509.08222) -- environmental observations become less reliable over time; temporal consistency refinement needed. HiPlan (2508.19076) -- plans fail when "the environment changes" between planning and execution. Agentic RL survey (2509.02547) -- partial observability (POMDP) means the agent never has complete state information.
- **Current gap:** Gap 3 -- Assumptions are implicit, not tracked.
- **Proposed change:** Add an `## Assumptions` section to the plan schema, and add a step to Phase 2 (EXPLORE) that requires explicitly listing assumptions:

```markdown
## Assumptions

| # | Assumption | Confidence | Verify Before Phase | If Wrong |
|---|-----------|------------|--------------------|---------|
| A1 | [e.g., "API X supports batch operations"] | High/Med/Low | Phase 2 | [fallback] |
| A2 | [e.g., "Database can handle 10k concurrent writes"] | Med | Phase 3 | [fallback] |
```

Add to Phase 2 (EXPLORE), after the research summary:

```
### Assumption Extraction (MANDATORY)

After research, explicitly list every assumption the plan depends on:
- Technology assumptions (API capabilities, library features)
- Environment assumptions (infrastructure, dependencies)
- Scope assumptions (user behavior, data volumes)
- Integration assumptions (other systems, interfaces)

Each assumption must have: confidence level and phase where it should be verified.
```

- **Expected impact:** Assumptions become visible and actionable. The building command can verify assumptions before dependent phases execute, preventing late-stage plan failures. This directly addresses the "unknown unknowns" problem -- by forcing explicit assumption listing, unknowns become known.

### Proposal 4: Add Context Flow Specification Between Phases

- **Research basis:** Code agent survey (2508.00083) -- "Context management determines scalability. For multi-agent systems, the limiting factor is not individual agent intelligence but shared context management." Agentic RL survey (2509.02547) -- credit assignment failure occurs when "agents ignore early actions that enable late success."
- **Current gap:** Gap 4 -- Phases are listed as independent checklists with no specification of what each phase produces or consumes.
- **Proposed change:** Add `Produces` and `Requires` fields to each phase in the plan schema:

```markdown
### Phase N: [Name]
**Model:** [recommended model]
**Requires:** [What must exist from previous phases -- specific files, interfaces, test fixtures]
**Produces:** [What this phase creates that later phases need]

- [ ] [Specific task with file path]
...
```

Add to Phase 3 (DETAIL), in the Section Template:

```markdown
### Section N: [Name]

**Requires from previous sections:**
- [specific artifact, interface, or decision from Section N-1]

**Produces for later sections:**
- [specific artifact, interface, or test fixture]

**Goal:** [what this section accomplishes]
...
```

- **Expected impact:** Dependency chains become explicit. If Phase 2 fails to produce an expected artifact, the plan immediately reveals which downstream phases are affected. This enables the building command to detect broken dependency chains early rather than discovering them during Phase 4 implementation.

### Proposal 5: Add Risk Register with Mitigations

- **Research basis:** HiPlan (2508.19076) -- failure catalog identifies specific failure modes and recovery actions. ExRAP (2509.08222) -- failure recovery is a first-class concern in the planning framework. SC2Arena (2508.10428) -- "Reflection analyses correctly identify failure causes" is a quality gate for strategic planning.
- **Current gap:** Gap 6 -- "What could go wrong?" is asked only for Medium+ complexity, and the answer is not structured into the plan output.
- **Proposed change:** Add `## Risks` section to the plan schema, and promote risk identification from an optional question to a mandatory phase activity:

```markdown
## Risks

| # | Risk | Likelihood | Impact | Mitigation | Owner Phase |
|---|------|-----------|--------|-----------|-------------|
| R1 | [e.g., "Third-party API rate limits hit during batch processing"] | Med | High | [e.g., "Implement exponential backoff + circuit breaker"] | Phase 2 |
| R2 | [e.g., "Schema migration breaks existing data"] | Low | Critical | [e.g., "Reversible migration + data backup before Phase 3"] | Phase 3 |
```

Move the risk question from "Medium complexity question 5" to Phase 2 (EXPLORE) as a mandatory step after approach selection:

```
### Risk Identification (MANDATORY)

After choosing approach, identify risks in these categories:
- Technical risks (technology limitations, integration failures)
- Scope risks (requirements ambiguity, scope creep)
- Dependency risks (external systems, API changes, library bugs)
- Data risks (migration, corruption, volume)

Each risk must have: likelihood, impact, mitigation strategy, and which phase owns the mitigation.
```

- **Expected impact:** Risk mitigations are planned before implementation begins, not improvised during execution. This is the IPB (Intelligence Preparation of the Battlefield) principle applied to software planning.

### Proposal 6: Add Milestone Success Criteria to Phases

- **Research basis:** HiPlan (2508.19076) -- milestone-level abstraction is the optimal granularity for plan execution. Each milestone has a clear description and success criteria that enable the agent to know when to advance. Agentic RL survey (2509.02547) -- dense step-level progress signals (not just sparse task-completion) are critical for long-horizon success.
- **Current gap:** Gap 7 -- Phases have tasks but no explicit success criteria. The implementer cannot objectively determine when a phase is "done."
- **Proposed change:** Add `**Milestone:**` and `**Done when:**` fields to each phase:

```markdown
### Phase N: [Name]
**Model:** [recommended model]
**Milestone:** [1 sentence: what state does the system reach after this phase?]
**Done when:** [Specific, verifiable criteria]
- [ ] [criterion 1 -- e.g., "All API endpoints return 200 for happy-path requests"]
- [ ] [criterion 2 -- e.g., "Unit tests pass for new module"]

**Requires:** [from Proposal 4]
**Produces:** [from Proposal 4]
- [ ] [Specific task with file path]
...
```

Add to Phase 3 (DETAIL), in the section creation loop:

```
For each section, define:
1. The milestone (what state the system reaches)
2. Done-when criteria (how to verify objectively)
3. Implementation tasks (specific work items)

The milestone and done-when criteria are MORE important than the task list.
Tasks may change during implementation; milestones should not.
```

- **Expected impact:** The building command can verify phase completion objectively rather than relying on checklist completion. This maps directly to HiPlan's finding that milestone-level guidance improves long-horizon task success by 4-23%.

### Proposal 7: Add Prior Plan Reference Mechanism

- **Research basis:** HiPlan (2508.19076) -- milestone library built from prior successful demonstrations enables "structured experience reuse." SC2Arena (2508.10428) -- "extracting successful patterns from wins and generating reflection analysis of what went wrong" improves future strategic planning.
- **Current gap:** Gap 5 -- No mechanism to learn from previous whiteboarding sessions.
- **Proposed change:** Add to Phase 1 (UNDERSTAND), after Pattern Discovery, a new step:

```
### Step 1a.5: Prior Plan Review (If applicable)

Search for existing plans in docs/plans/:
1. Read plan files related to the current topic
2. Check their Execution Log for lessons learned
3. Note what worked and what didn't

If prior plans exist:
- Reference successful patterns in approach selection
- Avoid previously identified risks that materialized
- Reuse milestone structures that proved effective

If no prior plans exist: State "No prior plans found for related work."
```

Also add to the plan file schema, in the `## Notes` section:

```markdown
## Notes

- [edge cases]
- [gotchas]
- [decisions made during planning]

### Prior Art
- [Related plan file, if any]: [what we learned from it]
```

- **Expected impact:** Whiteboarding sessions accumulate organizational knowledge over time. Plans improve as the docs/plans/ directory grows, creating a milestone library analogous to HiPlan's offline construction phase.

---

## Priority Ranking

Ranked by impact on plan quality and implementation success rate:

| Rank | Proposal | Impact | Effort | Rationale |
|------|----------|--------|--------|-----------|
| 1 | **P6: Milestone Success Criteria** | Critical | Low | Without verifiable milestones, the building command cannot objectively assess phase completion. HiPlan shows 4-23% absolute improvement from milestone guidance. This is the single highest-leverage change. |
| 2 | **P2: Decision Points and Branch Plans** | Critical | Medium | Linear plans fail on complex features. This is the difference between a plan that survives contact with reality and one that does not. Addresses the most dangerous failure mode: the plan breaks and the implementer has no fallback. |
| 3 | **P3: Assumption Register** | High | Low | Low effort, high yield. Forcing explicit assumption listing converts unknown unknowns into known unknowns -- the single most valuable transformation in planning (per both APOSD and military doctrine). |
| 4 | **P1: Commander's Intent** | High | Low | Small addition to the schema with outsized impact on implementer autonomy. When plans break (and they will), intent guides adaptation. |
| 5 | **P5: Risk Register** | High | Medium | Complements the assumption register. Assumptions track what we believe; risks track what we fear. Together they provide comprehensive uncertainty management. |
| 6 | **P4: Context Flow** | Medium | Low | Small schema addition that prevents a common failure: Phase N fails because Phase N-1 did not produce the expected artifact. Makes dependency chains visible. |
| 7 | **P7: Prior Plan Reference** | Medium | Low | Value scales with repository maturity. Low cost to add now; payoff increases over time as the plan library grows. Analogous to HiPlan's milestone library concept. |

### Implementation Recommendation

**Immediate (add to next version):** P6 + P3 + P1 -- three low-effort, high-impact schema changes that can be added to the plan file template and Phase 3 without restructuring the skill.

**Next iteration:** P2 + P5 -- these require adding new mandatory gates (Contingency Gate, Risk Identification) and modifying the Phase 3 workflow more substantially.

**After validation:** P4 + P7 -- these are refinements that provide incremental improvement once the core changes are validated.

---

## Summary

The current whiteboarding skill is strong on process discipline (search before ask, compare approaches, YAGNI gate) but weak on plan resilience. It produces plans optimized for the happy path -- linear checklists that assume everything goes as expected. The research consistently shows that the differentiator between successful and failed long-horizon execution is not the quality of the initial plan but the plan's ability to *adapt* when reality diverges from expectations.

The seven proposals above transform the plan output from a static checklist into a resilient operational order: one with milestones, decision points, assumption tracking, risk mitigations, and context flow -- the same elements that distinguish a military operations order from a to-do list.
