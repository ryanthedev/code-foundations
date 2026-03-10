# Cognitive Scientist Analysis (Round 2): How Detailed Should a Whiteboarding Plan Be?

**Persona:** Cognitive scientist specializing in human problem decomposition, cognitive load theory, and chunking
**Core question:** Given that subagents do their own discovery and write their own pseudocode, what does the whiteboarding plan actually need to contain?

---

## 1. What the Building Architecture Already Handles

Round 1 identified seven gaps. Several of these are substantially addressed by the building architecture's subagent design -- a fact that was invisible without reading the agent templates. Here is a gap-by-gap assessment:

### Gaps Already Solved by Architecture

**Gap 7 (Executability Grounding):** The pre-gate agent's Phase 1 (Discovery) explicitly checks whether plan-referenced files exist, identifies gaps between plan assumptions and reality, and can return SKIP or UPDATE_PLAN when the plan is wrong. The pre-gate agent does its OWN codebase search before writing pseudocode. This means grounding happens at execution time with fresh information, which is strictly better than grounding at planning time with potentially stale information.

**Verdict: Solved. The plan does NOT need to verify file existence -- the pre-gate agent will do this with current data.**

**Gap 4 (Dependency Modeling):** The building skill creates ALL sub-phase tasks upfront with explicit `blockedBy` chains. The architecture enforces sequential phase execution via TaskCreate/TaskUpdate -- a phase literally cannot start until its predecessor completes. The dependency enforcement is structural, not advisory.

**Verdict: Partially solved. The architecture enforces linear ordering. What it does NOT do is identify parallelizable phases -- that still requires the plan to specify which phases are independent. But the Round 1 proposal for DAG-based dependency graphs is less urgent than it appeared, because the building skill already prevents the worst failure mode (skipping prerequisites).**

**Gap 6 (No Plan Review Loop):** The building architecture implements a review loop at the EXECUTION level: pre-gate discovery catches plan-reality mismatches, post-gate catches implementation errors, and the gate failure protocol loops back for fixes. This is more valuable than a review loop at the PLANNING level because it operates on concrete code rather than abstract plans.

**Verdict: Partially solved. Execution-time review catches more than planning-time review. But the CogWriter research (2502.12568) still shows that planning-time review catches a different class of errors (structural completeness, constraint coverage). Both are needed, but the execution-level review reduces the stakes of planning-time review failures.**

### Gaps NOT Solved by Architecture

**Gap 1 (No Plan Quality Verification):** The building skill trusts the plan. If the plan is structurally incomplete -- missing a phase, forgetting a constraint, having circular logic -- the building skill will faithfully execute a broken plan. The pre-gate agent checks plan-vs-reality for ONE phase at a time; it cannot assess whole-plan coherence.

**Gap 2 (No Constraint Pre-Allocation):** Neither the building skill nor any subagent tracks whether constraints from the problem statement map to specific phases. A constraint that appears in the whiteboarding session but is never allocated to a phase will simply be forgotten.

**Gap 3 (Missing Expected Outcomes):** The building skill's post-gate agent verifies implementation against PSEUDOCODE, not against expected outcomes defined in the plan. If the pseudocode faithfully implements a wrong approach (one that doesn't achieve the user's actual goal), the post-gate will pass it. Expected outcomes in the plan serve a different function: they let the ORCHESTRATOR (building skill) detect strategic drift, not just tactical errors.

**Gap 5 (Fixed Ceremony):** The building skill applies uniform ceremony to all phases. Model auto-detection is a partial solution (haiku for simple, opus for complex), but the planning process itself does not adapt.

### The Critical Insight

The building architecture creates a system where **tactical execution is robust but strategic direction is brittle**. Subagents are excellent at: discovering what exists, writing pseudocode for what's specified, implementing what's designed, and reviewing what's implemented. What they cannot do is: assess whether the overall plan makes sense, detect missing phases, verify constraint coverage, or recognize strategic drift.

This means the whiteboarding plan's job is NOT to specify HOW to implement (the pre-gate agent handles that). Its job is to specify WHAT to implement and WHY, with enough structure that multiple independent agents can each verify their piece contributes to the whole.

---

## 2. The Right Level of Detail

### What the Plan Needs to Contain (the minimum viable contract)

The plan is consumed by three distinct readers, each with different needs:

| Reader | What They Need | What They Ignore |
|--------|---------------|-----------------|
| **Building orchestrator** | Phase names, ordering, model hints, task counts for auto-detection | Implementation details |
| **Pre-gate agent** | Phase goal, file list, constraints relevant to this phase | Other phases' details |
| **Post-gate agent** | Phase goal, success criteria, pseudocode (produced by pre-gate) | Original plan details beyond the phase |
| **Human (user)** | Strategic intent, approach rationale, constraint coverage | Pseudocode-level detail |

From this table, the required detail level crystallizes:

**Per phase, the plan needs:**
1. **Goal** (1-2 sentences) -- what this phase accomplishes strategically
2. **File list** (paths) -- scoping what the pre-gate agent should discover
3. **Task checklist** (bullet points) -- what to implement, not how
4. **Success criteria** (binary) -- how the orchestrator knows the phase succeeded
5. **Dependencies** -- what must come before
6. **Constraints** -- which global/local constraints apply to this phase

**Per phase, the plan should NOT contain:**
1. **Pseudocode** -- the pre-gate agent writes this after fresh codebase discovery
2. **Function signatures** -- the pre-gate agent designs these using its cc-routine-and-class-design skill
3. **Error handling specifics** -- the implementation agent applies cc-defensive-programming
4. **Detailed algorithms** -- the implementation agent translates pseudocode, which the pre-gate agent writes
5. **Edge case enumeration** -- the post-gate agent checks these with aposd-verifying-correctness

### What Is Too Much Detail

The current Section Template asks for "Implementation details: specific function/class/pattern, key decisions, edge cases to handle." This is too much. Here is why:

**Cognitive science argument:** When a plan over-specifies implementation, it creates what Sweller calls "extraneous cognitive load" -- information that the learner (subagent) must process but that does not contribute to schema formation. The pre-gate agent must reconcile the plan's implementation details with what it discovers in the codebase. If they conflict (and they often will, because the plan was written without fresh codebase discovery), the agent faces a judgment call: follow the plan or follow what it found? This ambiguity is the worst kind of cognitive load -- it creates unknown unknowns about which source of truth to trust.

**Architecture argument:** The pre-gate agent loads four skills (cc-construction-prerequisites, cc-pseudocode-programming, aposd-designing-deep-modules, cc-routine-and-class-design) and uses them to make design decisions. Over-specifying in the plan means the whiteboarding session is doing design work WITHOUT those skills loaded, producing lower-quality design decisions than the pre-gate agent would make on its own.

**Research argument:** Division-of-Thoughts (2502.04392) found that plan granularity should adapt to executor capability. The pre-gate agent is a specialized agent with design skills -- it is a strong executor. Coarse plans suffice for strong executors. Fine-grained plans are needed only for weak executors that cannot fill in details.

### What Is Too Little Detail

A plan that says only "Phase 1: Build the authentication system" is too little. Without file paths, the pre-gate agent's discovery phase is unfocused -- it has to search the entire codebase rather than examining specific areas. Without success criteria, the orchestrator cannot detect strategic drift. Without constraints, per-phase verification has nothing to verify against.

The minimum viable information for a phase to be actionable by a subagent is: **what** (goal + tasks), **where** (files), and **when done** (success criteria).

---

## 3. Cognitive Science Argument

### Chunking Theory Applied to Plan Consumption

Miller's chunking research and Chase & Simon's expert-novice studies established that experts process information by recognizing meaningful patterns (chunks) rather than individual elements. A chess master sees "kingside castling position" where a novice sees 6 individual pieces. The chunking advantage depends on the chunks being meaningful to the processor.

For the building architecture, each subagent is a specialized processor. The pre-gate agent "thinks in" codebase patterns, file structures, and design principles. The implementation agent "thinks in" pseudocode translations. The post-gate agent "thinks in" correctness dimensions.

**A plan that is chunked along implementation lines (function signatures, algorithms) forces subagents to de-chunk and re-chunk along their own cognitive lines.** A plan chunked along strategic lines (goals, constraints, success criteria) provides chunks that each subagent can directly incorporate into its own processing.

This is the chunking argument for strategic-level plans: the plan should be chunked at the level of the orchestrator's cognition (phases, goals, constraints), not at the level of the implementer's cognition (functions, algorithms, patterns). The implementer does its own chunking during pre-gate discovery.

### Cognitive Load Theory: Intrinsic vs. Extraneous Load

Sweller's cognitive load theory distinguishes three types:
- **Intrinsic load:** inherent to the task (irreducible complexity)
- **Extraneous load:** caused by poor presentation (reducible)
- **Germane load:** effort spent building schemas (productive)

For a subagent consuming a plan:
- **Intrinsic:** understanding what to build and the constraints
- **Extraneous:** reconciling plan-specified implementation details with actual codebase state
- **Germane:** forming a mental model of the phase's purpose and success criteria

Over-detailed plans increase extraneous load (reconciliation work) at the expense of germane load (understanding purpose). Under-detailed plans increase intrinsic load (the task becomes ambiguous). The optimal detail level minimizes extraneous load while keeping intrinsic load manageable -- which means specifying WHAT and WHY at a strategic level while leaving HOW to the agent that has the tools and skills to determine it.

### Information Processing: The Contract Metaphor

Research on plan-then-execute architectures (2502.01390, N=248) found that plan quality is the single strongest predictor of both trust and task performance. But "quality" in this context means clarity of intent and completeness of constraints, not implementation specificity.

The plan functions as a contract. Contract theory from cognitive science tells us that effective contracts specify:
1. **Obligations** (what must be delivered) -- goals and success criteria
2. **Constraints** (what must be respected) -- global and per-phase constraints
3. **Boundaries** (what is out of scope) -- YAGNI enforcement
4. **Verification** (how to confirm compliance) -- binary done-when criteria

Effective contracts do NOT specify:
1. **Methods** (how to fulfill obligations) -- that is the contractor's expertise
2. **Internal processes** (how the contractor organizes work) -- pre-gate handles this
3. **Tool choices** (which tools to use) -- the agent has skills for this

This maps precisely to the whiteboarding plan's role: it is a contract between the planning session and multiple independent subagent "contractors."

### The 4-Chunk Working Memory Constraint

Cowan's updated estimate of working memory capacity is approximately 4 chunks. When the building orchestrator dispatches a subagent, the dispatch prompt includes: the phase description from the plan, file paths, and pointers to input/output files. If each phase section contains 10+ detail items, the dispatch prompt becomes a cognitive overload problem for the subagent -- it cannot hold all the details in working memory while simultaneously exploring the codebase.

The current building skill's dispatch prompts are deliberately lean (plan section + input/output file paths). This design is correct. The plan sections should be equally lean to match.

**Recommended per-phase information budget:** 4 chunks maximum in the dispatch context:
1. Goal + reasoning (1 chunk)
2. File scope (1 chunk -- list of paths)
3. Task list (1 chunk -- what to do, 3-5 bullets)
4. Success criteria (1 chunk -- how to verify)

Everything else (constraints, dependencies, risk) is consumed by the orchestrator, not the subagent.

---

## 4. Concrete Recommendation: Updated Section Template

### The Two-Audience Template

The key insight is that the plan has two audiences with different needs. The template should visually separate them.

```markdown
### Phase N: [Name]

**Model:** [recommended model]
**Difficulty:** LOW / MEDIUM / HIGH
**Depends on:** [Phase IDs] | **Unlocks:** [Phase IDs]

<!-- ORCHESTRATOR CONTEXT (consumed by building skill) -->

**Goal:** [1-2 sentences: what this phase accomplishes and WHY]

**Constraints:**
- [constraints from global list that apply to this phase]

**Done when:**
- [ ] [Binary, testable condition -- e.g., "POST /api/users returns 201"]
- [ ] [Binary, testable condition -- e.g., "Unit tests pass for auth module"]

**If this fails:** [Fallback: what to try, or escalation path]

<!-- SUBAGENT CONTEXT (passed to pre-gate agent in dispatch) -->

**Scope:**
- `path/to/file.ts` - [what changes: create / modify / delete]
- `path/to/other.ts` - [what changes]

**Tasks:**
- [ ] [WHAT to do, not HOW -- e.g., "Add user validation endpoint"]
- [ ] [WHAT to do -- e.g., "Write unit tests for validation logic"]
- [ ] [WHAT to do -- e.g., "Update API route table"]

**Context forward:** _[filled during building]_
```

### What Changed from the Current Template

| Current Template Element | New Status | Rationale |
|-------------------------|-----------|-----------|
| Goal | KEPT | Strategic anchor for all agents |
| Files to create/modify | KEPT as "Scope" | Focuses pre-gate discovery |
| Implementation details | REMOVED | Pre-gate agent designs this; plan-level detail creates reconciliation load |
| Key decisions | MOVED to plan-level Decision Log | Decisions are strategic, not per-phase |
| Edge cases to handle | REMOVED | Post-gate agent checks these with aposd-verifying-correctness |
| Dependencies | RESTRUCTURED as Depends on / Unlocks | Structured for orchestrator consumption |
| (new) Done when | ADDED | Binary success criteria for drift detection |
| (new) Constraints | ADDED | Per-phase constraint allocation |
| (new) If this fails | ADDED | Fallback path for gate failure protocol |
| (new) Difficulty | ADDED | Informs model auto-detection and effort front-loading |
| (new) Context forward | ADDED | Filled during building to combat inter-phase context loss |

### What Changed from the Round 1 Synthesis Template

The Round 1 synthesis proposed a template with: Goal, Reasoning, Difficulty, Uncertainty, Files, Implementation details, Depends on / Unlocks, Requires from prior phases / Produces for later phases, Done when, If this fails. My recommendation differs:

1. **Remove "Implementation details"** -- This is the single most important change. The pre-gate agent writes implementation-ready pseudocode after fresh discovery. Plan-level implementation details are either redundant (if they match what the pre-gate finds) or harmful (if they conflict). The pre-gate agent's `cc-pseudocode-programming` and `aposd-designing-deep-modules` skills produce higher-quality implementation design than the whiteboarding session can.

2. **Remove "Uncertainty" as a per-phase field** -- Uncertainty is better captured in the plan-level Assumptions table (Round 1 proposal 1.3). Per-phase uncertainty text is vague and unactionable. An assumption with a confidence level and a "verify before phase N" instruction is concrete and actionable.

3. **Simplify "Requires/Produces" to "Context forward"** -- The Requires/Produces formalism is too heavy for most plans. The building architecture already handles artifact handoff through file-based contracts (discovery.md, pseudocode.md, review.md). What is genuinely needed is a free-form "Context forward" field that captures unexpected findings during execution -- the information that the file-based handoff does NOT capture.

4. **Merge "Reasoning" into "Goal"** -- A good goal statement includes WHY. Separating them creates redundancy and increases template bulk. "Add user validation to prevent malformed data from reaching the database" is both goal and reasoning. A separate reasoning field invites padding.

5. **Keep "Difficulty"** -- This directly informs model auto-detection (the building skill already uses task/file counts; difficulty is a useful additional signal) and effort front-loading.

### Plan-Level Structure (What Surrounds the Phases)

The Round 1 synthesis's plan-level additions are mostly correct. I endorse:

- **Commander's Intent** -- provides strategic anchor that subagents can check against
- **Assumptions table** -- concrete, verifiable, with fallbacks (replaces vague "uncertainty")
- **Risks table** -- paired with mitigations and phase assignments
- **Decision Log** -- captures WHY so subagents facing ambiguity can reference rationale
- **Dependency Graph** -- identifies critical path and parallel phases
- **Global Constraints** -- separated from per-phase constraints for clarity
- **Replanning Triggers** -- defines when to stop building and return to whiteboarding

I recommend AGAINST:
- **Fallback Approaches section** -- Too heavy for most plans. The per-phase "If this fails" field is sufficient for tactical fallbacks. Strategic fallbacks (switching the entire approach) are rare enough that they should trigger a return to whiteboarding rather than being pre-planned.

---

## 5. Research Backing

### Primary Citations

**Plan quality dominates execution quality:**
- He et al. (2502.01390), Plan-Then-Execute study (N=248): Plan quality is the single strongest predictor of both user trust and task performance. Poor plans cannot be saved by good execution. This supports investing in plan-level structure (constraints, success criteria, assumptions) rather than plan-level implementation detail.

**Plan granularity should match executor capability:**
- Shao et al. (2502.04392), Division-of-Thoughts: "Generate coarse plans (3-5 high-level steps)" for capable executors (7B+ models). The pre-gate agent with four loaded skills is a highly capable executor. Coarse strategic plans suffice. Fine-grained implementation plans are needed only for executors that cannot design their own solutions.

**Constraint pre-allocation prevents accumulating violations:**
- Wan et al. (2502.12568), CogWriter: Pre-allocating constraints to sections before generation improved constraint satisfaction by +0.16 average accuracy. Removing the PlanRevise step dropped range accuracy from 0.61 to 0.45. This supports the constraint allocation step and the plan integrity check.

**Context loss is the dominant failure mode in multi-agent systems:**
- Kong et al. (2501.13411), VulnBot: 42.36% of failures attributed to context loss between phases. Phase specialization with inter-phase summarization reduces this. This supports the "Context forward" field and the file-based artifact handoff that the building architecture already implements.

**Structured communication outperforms free-form:**
- Yang et al. (2502.05453), DAMCS: Structured message schemas "drastically reduce communication overhead and parsing errors compared to free-form natural language between agents." This supports a structured plan template with named fields rather than prose-heavy implementation descriptions.

**LLMs generate unnecessarily long plans:**
- Wei et al. (2502.11221), PlanGenLLMs survey: LLMs exhibit length bias in plan generation. Plans need conciseness pressure. This supports removing "Implementation details" from the phase template and enforcing the 2-7 phase count constraint.

**Query-dependent compute allocation reduces waste:**
- Zhang et al. (2502.04180), MaAS: Same pipeline for all queries wastes 55-94% of compute budget. Easy queries need simple processing. This supports the adaptive ceremony system where Simple plans get minimal structure and Complex plans get full structure.

### The Overarching Principle

The research converges on a single principle that directly answers the core question:

**Plans should specify WHAT and WHY at the strategic level, not HOW at the implementation level, when the executor has the capability to determine HOW on its own.**

The building architecture's pre-gate agent has four design skills, performs fresh codebase discovery, and writes implementation-ready pseudocode. It is a capable executor. The whiteboarding plan should be a strategic contract -- goals, constraints, success criteria, assumptions, risks -- not an implementation specification. The pre-gate agent will produce a better implementation specification than the whiteboarding session can, because it operates with current codebase knowledge and specialized design skills.

The right level of detail is: **enough for the orchestrator to detect strategic drift, enough for the pre-gate agent to scope its discovery, and no more.**
