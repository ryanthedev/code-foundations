# Systems Architect Analysis (Round 2): Plan as API Contract

## Persona Lens

I design API contracts for a living. The question "how detailed should a whiteboarding plan be?" is isomorphic to "what goes in the API spec vs. what does the implementation decide?" Every over-specified API becomes a maintenance burden that constrains the implementer needlessly. Every under-specified API becomes a source of integration bugs when consumers make incompatible assumptions. The plan is a contract between whiteboarding (the producer) and N independent subagents (the consumers). The architecture of the building system -- TaskCreate chains, fresh-context subagents, file-based handoffs -- determines what the contract *must* specify and what it *must not*.

---

## 1. What the Building Architecture Already Handles

Before arguing about what plans should contain, a contract designer must understand what the consumer already provides. The building system is not a dumb executor -- it has substantial built-in intelligence that the plan should not duplicate.

### Pre-Gate Agent: Discovery + Design

The pre-gate agent already does:
- **Codebase discovery** -- searches for existing files, checks plan assumptions against reality, identifies gaps
- **Pseudocode generation** -- translates plan requirements into implementation-ready pseudocode using `cc-pseudocode-programming` and `aposd-designing-deep-modules` skills
- **Prerequisite verification** -- confirms dependencies are met before proceeding
- **Recommendation authority** -- can return SKIP or UPDATE_PLAN if conditions warrant

**Contract implication:** The plan does NOT need to contain pseudocode, detailed function signatures, or exact implementation patterns. The pre-gate agent discovers these. Specifying them in the plan creates a rigidity hazard -- the plan locks in assumptions before discovery.

### Implementation Agent: Faithful Translation

The implementation agent already does:
- **Exact pseudocode translation** -- implements what pre-gate designed, nothing more
- **Defensive programming** -- applies validation, error handling, resource cleanup where pseudocode indicates
- **Interface design** -- enforces deep modules, information hiding for new modules
- **Test-after-each-file** discipline

**Contract implication:** The plan does NOT need to specify error handling strategies, validation approaches, or coding patterns. These are implementation details the agent handles via loaded skills.

### Post-Gate Agent: Quality Verification

The post-gate agent already does:
- **Spec match verification** -- maps pseudocode to implementation line by line
- **Dead code detection**
- **Six-dimension correctness verification** (requirements, concurrency, errors, resources, boundaries, security)
- **Defensive programming audit**
- **Test coverage verification** against the plan's coverage level

**Contract implication:** The plan does NOT need to specify quality criteria in detail. The post-gate agent has its own comprehensive checklist. What the plan *does* need is a `Test Coverage` field (which it already has) and verifiable exit criteria per phase (which it lacks).

### Model Auto-Detection

Building already resolves model selection via:
- Plan `**Model:**` override (first priority)
- Heuristic: task count, file count, keyword matching for opus/haiku triggers
- Default: sonnet

**Contract implication:** The plan's model recommendation is an *override*, not a requirement. The auto-detection system is the default. Plans should only set `**Model:**` when they have information the heuristic cannot infer (e.g., "this phase is mechanically simple but architecturally critical -- use opus").

### TaskCreate Dependency Chains

Building creates all sub-phase tasks upfront with blockedBy chains:
```
Phase N.1 PRE-GATE -> N.2 IMPLEMENT -> N.3 POST-GATE -> N.4 CHECKPOINT
Phase (N+1).1 -> blockedBy N.4
```

**Contract implication:** The plan's phase ordering is the *only* sequencing signal the building system uses. If phases must be sequential, the plan expresses this implicitly by ordering. If phases could be parallel, the current system cannot express this. The plan format is the bottleneck.

### Summary: What the Plan Gets for Free

| Capability | Provider | Plan Should NOT Specify |
|-----------|----------|------------------------|
| Codebase discovery | Pre-gate agent | Exact current state of files |
| Pseudocode design | Pre-gate agent | Function signatures, algorithms |
| Implementation patterns | Implementation agent + skills | Error handling, validation, coding style |
| Quality verification | Post-gate agent + skills | Correctness criteria, dead code rules |
| Model selection | Auto-detection heuristic | Model choice (unless overriding) |
| Phase sequencing enforcement | TaskCreate + blockedBy | Execution order (it follows plan order) |

---

## 2. The Right Level of Detail -- Contract Theory

### The Inversion of Control Principle

In API design, the best contracts specify *what* (behavior) not *how* (implementation). The caller says "give me a sorted list" not "use quicksort with median-of-three pivot selection." Applied to plans:

| Specify (the "what") | Do NOT Specify (the "how") |
|----------------------|---------------------------|
| What each phase must accomplish (goal) | How to accomplish it (algorithms, patterns) |
| What each phase produces for downstream (interface) | Internal structure of the output (implementation) |
| What must be true when the phase is done (postcondition) | How to verify it (the post-gate agent knows) |
| What external constraints apply (invariants) | How to satisfy them (the implementation agent decides) |
| Where the hard problems are (risk) | How to solve them (pre-gate discovers this) |

### The Liskov Substitution Test for Plans

A well-designed plan passes this test: *Could you swap in a different implementation agent (with different skills, different language expertise) and still have the plan be executable?* If yes, the plan is at the right abstraction level. If no, the plan has leaked implementation details into the contract.

Current plan sections mostly pass this test. They specify files and goals, not algorithms. But they fail in one key area: **they do not specify what each phase produces for the next phase.** A substitute agent would have to guess what upstream produced.

### Postel's Law Applied to Plans

"Be conservative in what you send, liberal in what you accept." For plans:
- **Conservative in specification:** Specify only what the subagent cannot discover on its own. The pre-gate agent discovers codebase state; don't pre-specify it.
- **Liberal in acceptance:** The plan should tolerate phases producing *more* than specified (the implementation agent might add tests the plan didn't mention). It should only fail when phases produce *less* than required.

### The Semantic Versioning Analogy

Plan phases are like API versions. Each phase has:
- **Public interface** -- what downstream phases depend on (MUST be stable)
- **Internal implementation** -- how this phase achieves its goal (CAN change freely)
- **Breaking changes** -- anything that would invalidate a downstream phase's assumptions (MUST be flagged)

The current plan format conflates public interface and internal implementation. The `**Implementation details:**` section mixes "what this phase produces" with "how this phase works internally." These need separation.

---

## 3. Architecture Argument -- Interface Design Principles Applied to Plan Granularity

### Principle 1: Specify Interfaces, Not Implementations

The plan is consumed by subagents that start with *fresh context*. They have never seen the whiteboarding conversation. They read three things: the plan file, the discovery file (written by a previous pre-gate agent), and the pseudocode file (also from pre-gate). The plan is their only window into the user's intent.

This means the plan must specify intent clearly but must not over-constrain implementation, because the pre-gate agent will discover reality and may need to deviate.

**Current failure mode:** The `**Implementation details:**` field in the section template encourages specifying "specific function/class/pattern" -- implementation details that the pre-gate agent should discover. If the plan says "use a BTreeMap" but the pre-gate agent discovers the codebase uses HashMap everywhere, there is a conflict with no resolution protocol.

**Fix:** Rename `**Implementation details:**` to `**Approach notes:**` and change the instruction from "specific function/class/pattern" to "key decisions and constraints the implementer must honor." This shifts from prescribing implementation to declaring constraints.

### Principle 2: Make Dependencies Explicit (Dependency Inversion)

The current section template has a `**Dependencies:**` field with the instruction "what must be done first." This is a sequencing dependency (Phase 2 runs after Phase 1), but it does not express a *data* dependency (Phase 2 needs the User model that Phase 1 creates).

In API design, this is the difference between temporal coupling ("call init() before process()") and interface coupling ("process() requires a valid Config object"). The building system enforces temporal coupling via blockedBy chains. But data coupling is invisible -- the pre-gate agent has to discover it.

**Fix:** Add a `**Receives from:**` field that names the specific artifacts or capabilities a phase depends on. This makes data dependencies explicit without over-specifying the format of those artifacts.

### Principle 3: Define Exit Criteria as Postconditions

In contract-based design (Design by Contract, Eiffel-style), every method has preconditions, postconditions, and invariants. Plan phases currently have implicit preconditions (the `Dependencies` field) but no postconditions. The post-gate agent checks generic quality, but it does not know what *this specific phase* was supposed to produce.

**Fix:** Add `**Done when:**` as a required field -- a list of verifiable postconditions. "Verifiable" means the post-gate agent or a bash command can check it. "The API feels good" is not verifiable. "All endpoints return 200 on happy path" is verifiable.

### Principle 4: Separate Stable from Volatile Information

Some plan information is stable across the entire execution (constraints, chosen approach, test coverage level). Other information is volatile -- it will be refined or replaced by pre-gate discovery (exact file contents, current implementation state, available functions).

The plan should clearly separate these:
- **Stable contract elements:** goal, constraints, chosen approach, test coverage, phase ordering, exit criteria, risk register
- **Volatile guidance elements:** implementation suggestions, file state assumptions, pattern recommendations

Volatile elements should be marked as advisory ("consider using X" not "use X"), so the pre-gate agent knows it can override them.

### Principle 5: Progressive Disclosure (Information Hiding for Plans)

APOSD's core principle -- deep modules with simple interfaces -- applies to plan phases. Each phase should present a simple interface to the building orchestrator (goal, inputs, outputs, exit criteria) while hiding the complexity of *how* it will be accomplished. The pre-gate agent is responsible for expanding the simple interface into detailed pseudocode.

The current plan format violates this by putting implementation details at the same level as interface elements. A phase that says:

```
Goal: Add authentication
Implementation details: Create AuthService with bcrypt hashing, JWT token generation using jsonwebtoken library, refresh token rotation with 7-day expiry...
```

...has collapsed the interface/implementation distinction. The goal is the interface. The implementation details belong in the pre-gate agent's pseudocode output.

---

## 4. Concrete Recommendation -- Updated Section Template

### Current Template (Problematic)

```markdown
### Section N: [Name]

**Goal:** [what this section accomplishes]

**Files to create/modify:**
- `path/to/file.ts` - [what changes]

**Implementation details:**
- [specific function/class/pattern]
- [key decisions]
- [edge cases to handle]

**Dependencies:** [what must be done first]
```

### Proposed Template (Contract-Oriented)

```markdown
### Phase N: [Name]

**Goal:** [what this phase accomplishes -- the "what", not the "how"]

**Difficulty:** [LOW | MEDIUM | HIGH]
**Uncertainty:** [what we don't know that could change this plan]

**Files to create/modify:**
- `path/to/file.ts` - [what changes]

**Approach notes:** [constraints and decisions the implementer must honor -- NOT algorithms or patterns]

**Receives from:** [what this phase needs from prior phases -- data dependencies]
**Produces:** [what this phase outputs that downstream phases or the user consume]

**Done when:** [verifiable postconditions -- things a command or code review can check]

**Dependencies:** [which phases must complete first]
```

### What Changed and Why

| Field | Change | Rationale |
|-------|--------|-----------|
| `Implementation details` | Renamed to `Approach notes`, scope narrowed | Prevents plan from prescribing implementation; shifts to constraints |
| `Difficulty` | Added | Drives model selection and effort allocation (research: 193.8% efficiency gain) |
| `Uncertainty` | Added | Identifies where pre-gate discovery is most critical |
| `Receives from` | Added | Makes data dependencies explicit; prevents interface gaps |
| `Produces` | Added | Defines the phase's public interface for downstream consumers |
| `Done when` | Added | Postconditions enable plan-specific quality gates |

### What Was NOT Added

| Omitted | Why |
|---------|-----|
| Pseudocode | Pre-gate agent generates this from discovery |
| Function signatures | Implementation agent decides based on pseudocode |
| Error handling strategy | Implementation agent applies via `cc-defensive-programming` |
| Quality checklist | Post-gate agent has comprehensive built-in checklists |
| Exact test cases | Test plan section covers high-level; implementation agent writes specific tests |

### Progressive Detail by Phase Position

The template applies uniformly, but the *depth of content* should vary:

| Phase Position | `Goal` | `Approach notes` | `Done when` |
|---------------|--------|-------------------|-------------|
| Phase 1 (first) | Full clarity | Detailed constraints, edge cases, known patterns | 3-5 verifiable criteria |
| Phase 2-3 | Clear | Key constraints only | 2-3 verifiable criteria |
| Phase 4+ | Directional | "TBD during pre-gate discovery" is acceptable | 1-2 high-level criteria |

This is not a new field -- it is guidance for the whiteboarding agent on how much to write per phase. Later phases will be re-planned by pre-gate agents that have the benefit of seeing what earlier phases actually produced.

### Plan-Level Additions

Beyond the section template, add two plan-level sections:

**Dependency Graph** (after `## Chosen Approach`):
```markdown
## Dependency Graph

Phase 1 -> Phase 2 -> Phase 4
Phase 1 -> Phase 3 -> Phase 4

Critical path: 1 -> 2 -> 4
Parallelizable: Phase 2, Phase 3
```

**Risk Register** (after `## Test Plan`):
```markdown
## Risk Register

| Risk | Impact | Phase | Mitigation |
|------|--------|-------|------------|
| [risk description] | HIGH/MED/LOW | N | [how to handle] |
```

---

## 5. Research Backing

### Plans Should Front-Load Uncertainty (2505.16122 -- Plan and Budget)

The "Plan and Budget" framework demonstrates that decomposing problems into sub-questions with difficulty-aware token budgets yields up to 193.8% efficiency improvement. The key mechanism is *front-loading* -- cosine and polynomial decay schedules allocate more compute to early sub-questions where epistemic uncertainty is highest. For whiteboarding plans, this translates directly: Phase 1 should tackle the highest-uncertainty work, and the plan template should make uncertainty visible via the `**Uncertainty:**` field so the building system can calibrate effort.

The paper also validates the "weak planner, strong reasoner" pattern: the decomposition planner (whiteboarding) should be deliberately less capable at *execution* than the executor (building subagents). The planner identifies sub-questions and their difficulty; it does not solve them. This is exactly the contract boundary: whiteboarding specifies *what* and *how hard*; building subagents determine *how*.

### Over-Specification Causes Edge-Level Defects (2505.18286 -- Single-Agent or Multi-Agent?)

The MAS defect taxonomy identifies edge-level defects as the failure mode where "downstream agents are overwhelmed by upstream context." In the building pipeline, each subagent starts with fresh context and reads the plan + discovery + pseudocode files. An over-specified plan adds noise to this context -- the implementation agent has to distinguish between the plan's prescriptive implementation details and the pre-gate agent's pseudocode, which may conflict.

The paper's finding that MAS advantages diminish as LLMs improve has a direct architectural implication: as models get better, the value of detailed decomposition decreases. Plans should specify less, not more, because stronger subagents can fill in gaps better than they can resolve conflicts between the plan and reality.

The hybrid cascade pattern (SAS first, escalate to MAS on low confidence) maps to progressive detail: give the pre-gate agent a simple phase specification first. If it returns UPDATE_PLAN, that is the confidence signal to provide more detail.

### Adaptive Compute Allocation per Phase (2505.13379 -- Thinkless)

The Thinkless framework trains models to self-select reasoning depth, achieving 50-90% token reduction on easy tasks. The core insight is that *the executor is better at judging difficulty than an external classifier.* Applied to plans: the whiteboarding agent's difficulty estimate is useful guidance, but the pre-gate agent (which actually reads the code) will form a more accurate assessment. The plan's `**Difficulty:**` field is a prior; the pre-gate agent updates it to a posterior.

This argues against making difficulty a hard constraint (e.g., "this phase MUST use opus"). Instead, it should be advisory input to the model auto-detection heuristic -- a signal that can be overridden by actual discovery.

### Credit Assignment Requires Per-Phase Progress Criteria (2505.20732 -- SPA-RL)

The SPA framework decomposes final task-completion rewards into per-step progress contributions. The key constraint: per-step scores must sum to the final reward. Applied to plans: each phase should have a `**Done when:**` that constitutes a measurable fraction of the overall goal. Without this, the building system has no way to detect when a phase succeeded but contributed nothing (e.g., the code compiles and tests pass, but the feature does not actually work).

The fused reward concept (progress + grounding) maps to the plan's dual obligation: each phase must both *advance the goal* (progress) and *produce executable artifacts* (grounding). The `**Produces:**` field captures the grounding dimension; the `**Done when:**` field captures the progress dimension.

### Hierarchical Planning: Global Topology + Local Density (2505.06131 -- LOG-Nav)

The LOG-Nav architecture maintains two representations: a sparse global topology (for efficient inter-room routing) and dense local plans (for intra-room navigation). The global plan prevents unnecessary detours; the local plan handles dynamic changes.

Applied to whiteboarding: the plan file is the global topology -- sparse waypoints between phases with dependency edges. The pre-gate agent's pseudocode is the dense local plan -- detailed implementation instructions generated just-in-time from actual codebase state. The current plan format tries to be both global and local, which is why it over-specifies later phases. The proposed template separates these layers: the plan provides topology (goal, dependencies, constraints); the pre-gate agent provides density (pseudocode, discovery).

The "incremental local planning" principle -- computing dense waypoints for the next segment only as the robot approaches -- validates progressive detail resolution. Do not plan all local details upfront. Phase 4's detailed pseudocode should be generated by Phase 4's pre-gate agent, not by the whiteboarding agent that has never seen Phase 1's output.

### Capability-Typed Task Assignment (2506.05020 -- Hierarchical Multi-Robot)

The multi-robot paper demonstrates that heterogeneous agents must have tasks assigned based on capability type, not treated as interchangeable. In the building pipeline, the three agent types (pre-gate, implementation, post-gate) are heterogeneous with different skill loadouts and different roles. The plan's job is to give each agent type the information it needs:

| Agent Type | Needs from Plan | Does NOT Need |
|-----------|----------------|---------------|
| Pre-gate | Goal, files, constraints, uncertainty | Implementation details (it discovers these) |
| Implementation | (reads pseudocode, not plan directly) | Plan-level context (it works from pseudocode) |
| Post-gate | Exit criteria, test coverage level | Implementation details (it reads the code) |

The proposed template's field set is designed to serve these three consumers. `Goal` and `Uncertainty` serve pre-gate. `Done when` and test coverage serve post-gate. `Approach notes` serve pre-gate's pseudocode design. No field serves the implementation agent directly, because the implementation agent's contract is with the pseudocode, not the plan.

### Situational Risk Detection (2505.19933 -- SAFEL)

The SAFEL framework reveals that LLMs are far better at rejecting obviously unsafe commands than at anticipating subtle situational risks. Applied to planning: whiteboarding agents easily identify obvious risks ("this requires database migration") but miss subtle ones ("the existing auth middleware silently swallows 403 errors, so our new permission check will appear to succeed"). The `**Uncertainty:**` field forces the whiteboarding agent to state what it does not know, creating a signal for the pre-gate agent to investigate. This is modular safety evaluation applied to planning: decompose risk assessment into "what I know is risky" (Risk Register) and "what I don't know" (Uncertainty field).

---

## Summary

The plan is a contract. Like any good API contract, it should specify:

1. **What** each phase accomplishes (Goal) -- not how
2. **What** each phase consumes and produces (Receives from, Produces) -- the interface
3. **When** each phase is done (Done when) -- the postcondition
4. **How hard** each phase is (Difficulty, Uncertainty) -- effort calibration signal
5. **What could go wrong** (Risk Register) -- adversarial thinking

It should NOT specify:
1. Pseudocode, algorithms, or implementation patterns (pre-gate agent's job)
2. Quality criteria or verification steps (post-gate agent has built-in checklists)
3. Detailed implementation for later phases (will be invalidated by earlier phase outcomes)
4. Model selection (auto-detection handles this; plan overrides only when necessary)

The building system's three-agent architecture (pre-gate/implement/post-gate) with fresh-context dispatch and file-based handoffs is already well-designed. The plan's job is to be the right kind of input to this system: enough structure to prevent wrong work, enough freedom to allow right work.
