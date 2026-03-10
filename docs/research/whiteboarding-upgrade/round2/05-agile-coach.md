# Agile Coach Analysis (Round 2): Just-Enough Planning for LLM Executors

## Persona Lens

The core agile question: how detailed should a plan be? The classic answer -- "just enough" -- needs recalibration when the executor is not a human teammate with persistent memory and implicit organizational knowledge, but an LLM subagent with fresh context and no memory of the planning conversation.

This analysis examines what the building architecture already handles, what research says about specification granularity for agentic executors, and where the whiteboarding plan template should land.

---

## 1. What the Building Architecture Already Handles

Before adding detail to the plan, recognize what the downstream machinery does for free:

| Concern | Where It Is Handled | What It Does |
|---------|-------------------|-------------|
| Discovery of current state | Pre-gate agent (Phase N.1) | Searches codebase, maps files, identifies gaps between plan assumptions and reality |
| Design translation | Pre-gate agent (pseudocode) | Converts plan tasks into implementation-ready pseudocode with cc-construction-prerequisites and aposd-designing-deep-modules |
| Implementation quality | Implementation agent (Phase N.2) | Applies cc-control-flow-quality, cc-data-organization, aposd-improving-code-clarity, aposd-simplifying-complexity |
| Verification | Post-gate agent (Phase N.3) | Reviews against pseudocode spec, checks correctness across 6 dimensions, catches dead code and defensive violations |
| Sequencing enforcement | TaskCreate with blockedBy chains | Cannot skip gates, cannot proceed without predecessor completion |
| Model selection | Auto-detection from task/file counts + OPUS/HAIKU keywords | Allocates reasoning capacity proportional to phase complexity |
| Scope control | Implementation agent anti-patterns | "Not in pseudocode = not in scope" -- strictly enforced |
| Failure recovery | Gate Failure Protocol | FAIL stays in_progress, re-dispatch until PASS |

**The pre-gate agent is the key insight.** It performs discovery (what exists) and design (pseudocode) with fresh eyes and loaded skills. This means the plan does NOT need to specify how to implement -- the pre-gate agent will figure that out by searching the codebase. The plan needs to specify what to implement and why.

**What the plan IS:**
- A contract between the human and the building orchestrator
- A routing document that determines phase boundaries, sequencing, and model allocation
- A set of acceptance criteria the post-gate agent verifies against

**What the plan is NOT:**
- A pseudocode specification (pre-gate agent writes that)
- A codebase map (pre-gate agent discovers that)
- An implementation guide (implementation agent follows pseudocode, not the plan)

---

## 2. The Right Level of Detail -- Just-Enough Planning for LLM Executors

### The Specification Paradox

Human executors benefit from ambiguity -- they fill gaps with organizational knowledge, ask clarifying questions, and use judgment. LLM subagents do the opposite: they fill gaps with hallucination, plausible-sounding fabrication, and scope creep.

But over-specifying creates a different problem. Research on hierarchical planning (STEP Planner, 2506.21030) shows that flat, over-detailed plans actually degrade performance. When planners receive too much context, success rates drop -- the contextual gap overwhelms the logical structure. STEP achieved 40% success rate vs 6% for flat methods specifically by giving each decomposition level only parent + sibling context, not the full history.

The right level is therefore: **enough structure that the pre-gate agent knows what to discover and the post-gate agent knows what to verify, but not so much that it constrains discovery or crowds the context window.**

### What Needs to Be Explicit vs What Can Be Discovered

| Explicit in the Plan | Discovered by Pre-Gate Agent |
|---------------------|----------------------------|
| WHAT to build (goal per phase) | HOW it currently works (codebase state) |
| WHY this phase exists (user intent) | WHAT files to modify (discovery) |
| Acceptance criteria (testable outcomes) | HOW to implement (pseudocode) |
| Phase ordering and dependencies | WHETHER prerequisites are met |
| Constraints and non-goals | WHETHER assumptions hold |
| Test coverage level | Specific test cases |

The current Section Template includes "Implementation details" and "specific function/class/pattern" -- these are pre-gate agent territory. The plan should specify the goal and constraints; the pre-gate agent should figure out the implementation path.

### The Three-Sentence Phase Test

A well-sized plan phase should be expressible in three sentences:
1. **Goal:** What this phase delivers (user-observable outcome)
2. **Constraint:** What must be true about the implementation (non-functional requirements, patterns to follow, things to avoid)
3. **Done-when:** How the post-gate agent knows this phase is complete (testable acceptance criteria)

If a phase cannot be expressed in three sentences, it is either too large (split it) or too vague (clarify the goal). If it needs five paragraphs of implementation detail, that detail belongs in the pre-gate agent's pseudocode output, not the plan.

---

## 3. Agile Argument -- Story Sizing, INVEST, and Specification Granularity

### INVEST Criteria Applied to Plan Phases

Each phase in the plan is analogous to a user story. The INVEST criteria reveal whether phases are well-sized:

| Criterion | What It Means for a Plan Phase | Current Template | Gap |
|-----------|-------------------------------|-----------------|-----|
| **Independent** | Phase can be implemented without understanding other phases' internals | Partially met -- dependencies listed but no context scoping | Phase context bleeds across boundaries |
| **Negotiable** | Phase goal can be achieved multiple ways | Not addressed -- template implies specific implementation | Pre-gate agent provides negotiability by discovering alternatives |
| **Valuable** | Phase delivers something the user can verify | Not validated -- no vertical slice check | Infrastructure phases may deliver no observable value |
| **Estimable** | Phase scope is clear enough to predict effort | Met via task count + file count for model auto-detection | Works well |
| **Small** | Phase is completable in one building sub-cycle | Loosely enforced via 200-300 word limit | Word count is a poor proxy for scope |
| **Testable** | Phase has clear pass/fail criteria | Weakly met -- "Implementation details" listed but no acceptance criteria | Post-gate agent needs explicit criteria to verify against |

The largest gaps are **Valuable** (vertical slice) and **Testable** (acceptance criteria). These are also the two criteria that matter most for LLM execution, because:
- Without testability, the post-gate agent has no standard to verify against and defaults to generic quality checks
- Without value delivery, intermediate phases cannot be validated even by a human reviewing the execution log

### Story Sizing for LLM Context Windows

Traditional story sizing uses relative points or t-shirt sizes. For LLM executors, the relevant dimension is **context budget**: how much context does the pre-gate agent need to load to understand this phase?

| Size Signal | Phase Characteristic | Recommendation |
|-------------|---------------------|----------------|
| **Small** (1-2 files, mechanical change) | Config update, rename, add field | Haiku model, minimal plan detail, 2-level decomposition |
| **Medium** (3-5 files, moderate logic) | New endpoint, refactor module, add feature | Sonnet model, standard plan detail, 3-level decomposition |
| **Large** (6+ files, architectural change) | New subsystem, migration, cross-cutting concern | Opus model, detailed plan with explicit constraints, feasibility gate required |

This maps directly to the existing model auto-detection logic. The plan detail level should scale with the same signals.

### Vertical Slicing for Phased Delivery

The most common anti-pattern in plans is horizontal slicing: "Phase 1: all the data models, Phase 2: all the business logic, Phase 3: all the UI." This creates phases that cannot be independently verified and that accumulate risk toward the end.

Vertical slicing means each phase delivers an end-to-end slice: "Phase 1: user can create a widget (model + logic + UI for create), Phase 2: user can edit a widget (model + logic + UI for edit)."

For LLM execution, vertical slicing is even more important than for human teams because:
- Each phase gets a fresh subagent context -- there is no "I remember what I built in Phase 1" carryover
- Post-gate verification is meaningful only when the phase produces observable output
- Gate failures are recoverable when the phase is self-contained (replan this slice without affecting others)

---

## 4. Concrete Recommendation -- Updated Section Template

### Current Template (from whiteboarding SKILL.md)

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

### Proposed Template

```markdown
### Phase N: [Name]
**Model:** [auto-detect or override]

**Goal:** [One sentence: what user-observable outcome this phase delivers]

**Constraints:**
- [Non-functional requirement or pattern to follow]
- [What NOT to do -- explicit non-goals for this phase]

**Done-when:**
- [ ] [Testable acceptance criterion 1]
- [ ] [Testable acceptance criterion 2]

**Depends-on:** [Phase N-1 output, or "None"]

**Context for implementer:** [1-2 sentences maximum: what the pre-gate
agent needs to know that it cannot discover by searching the codebase.
User intent, business rules, or decisions made during planning.]
```

### What Changed and Why

| Removed | Why |
|---------|-----|
| "Files to create/modify" | Pre-gate agent discovers this via codebase search. Plan assumptions about file paths are often wrong. |
| "Implementation details" | Pre-gate agent writes pseudocode for this. Plan-level implementation details constrain discovery and are frequently stale by execution time. |
| "specific function/class/pattern" | This is pseudocode territory. Including it in the plan creates a contract the pre-gate agent cannot renegotiate when reality differs. |
| "edge cases to handle" | Post-gate agent catches these via aposd-verifying-correctness checklist. Listing them in the plan is redundant with the gate. |

| Added | Why |
|-------|-----|
| "Constraints" with explicit non-goals | LLM subagents scope-creep. Stating what NOT to build is as important as stating what to build. Implementation agent anti-pattern table says "Not in pseudocode = not in scope" but the pre-gate agent needs to know the boundaries too. |
| "Done-when" with testable criteria | Post-gate agent needs concrete verification targets, not just "check quality." These become the spec-match checklist items. |
| "Context for implementer" (capped at 1-2 sentences) | Only information the pre-gate agent cannot discover by searching. User intent, business rules, or planning decisions. Everything else is discoverable. |
| "Model" field | Already exists in building SKILL.md but not in the plan template. Making it visible during planning lets the user adjust before execution. |

### Complexity-Scaled Detail

| Complexity | Phase Template Additions |
|------------|------------------------|
| **Simple** | Use base template as-is. 1-2 done-when criteria. Skip constraints if obvious. |
| **Medium** | Add constraints. 2-4 done-when criteria. Add context-for-implementer if non-obvious intent exists. |
| **Complex** | Add constraints with explicit non-goals. 3-5 done-when criteria. Add context-for-implementer. Add feasibility note if approach depends on unverified assumptions. |

### Plan-Level Additions

Beyond the per-phase template, the plan file should include:

```markdown
## Vertical Slice Validation

| Phase | User-Observable Output | Independently Testable? |
|-------|----------------------|------------------------|
| 1     | [what user sees]     | YES / NO               |
| 2     | [what user sees]     | YES / NO               |

Red flags:
- Phase with no user-observable output -> merge with adjacent phase
- Phase not independently testable -> too coupled, restructure
- First testable output in Phase 3+ -> reorder for earlier value delivery
```

---

## 5. Research Backing

### Directly Applicable

**STEP Planner (2506.21030)** -- The most relevant paper. Demonstrates that:
- Flat plans fail at >5 steps (1-6% success rate vs 40% for hierarchical decomposition)
- Context pruning (each node sees only parent + siblings, not full history) accounts for +32 percentage points of improvement
- Dual termination criteria (mappability + consistency) prevent both premature and infeasible actions
- "Additional/Missing Steps" is the primary error mode (27%) -- directly addressed by explicit done-when criteria

Applied: The proposed template reduces context per phase (context-for-implementer is capped), removes implementation details that belong in pseudocode (context pruning), and adds done-when criteria (termination validation).

**ContextMatters (2506.15828)** -- Goal relaxation framework:
- When a plan step is infeasible, relax along functionality (what) or feasibility (how) axes
- +52.45% success rate from systematic relaxation vs retry

Applied: The "Constraints" field with explicit non-goals gives the pre-gate agent room to relax approach while preserving intent. If discovery reveals the planned approach is infeasible, the agent has the goal + constraints to find alternatives, rather than rigid file paths that cannot be adapted.

**RoboCerebra (2506.06677)** -- Long-horizon evaluation:
- Planning, reflection, and memory are three independent dimensions of planning quality
- Short-horizon benchmarks hide failures that emerge at scale

Applied: The vertical slice validation adds a reflection step (do all phases together satisfy the problem statement?). The done-when criteria provide per-phase reflection targets.

### Indirectly Applicable

**HRM (2506.21734)** -- Adaptive computational time:
- Allocating more compute to harder problems and less to easy ones saves ~50% on easy problems
- Minimal advantage on simple tasks; massive advantage on complex ones

Applied: Complexity-scaled detail levels in the template. Simple phases get minimal ceremony; complex phases get constraints, non-goals, and feasibility notes.

**ECON (2506.08292)** -- Multi-agent coordination:
- Belief-based coordination (each agent reasons about others' strategies) outperforms direct communication by 11.2% while using 21.4% fewer tokens

Applied: The proposed template treats each phase as an independent agent's contract. Rather than communicating implementation details across phases (expensive, context-polluting), each phase states its goal and depends-on relationship. The pre-gate agent forms its own "beliefs" about codebase state via discovery rather than inheriting stale context from planning.

**ThinkAct (2507.16815)** -- Think-then-act architecture:
- Decoupling slow reasoning (every N steps) from fast control (every step) improves embodied task success
- Latent plan compression enables efficient conditioning without inflating context windows

Applied: The whiteboarding/building split already implements this pattern. Whiteboarding is the slow reasoning phase; building is the fast execution phase. The proposed template change makes the "latent plan" (what building receives) more compressed and action-aligned by removing implementation details that inflate context without improving execution.

### Low Relevance

**VLN-R1 (2506.17221), Math Reasoning Transfer (2507.00432), RoboBrain (2507.02029)** -- These address embodied navigation training, reasoning transfer methodology, and robotic vision-language models respectively. No directly applicable findings for plan specification granularity.

---

## Summary

The building architecture already handles discovery, design, implementation quality, and verification through specialized subagents with loaded skills. The whiteboarding plan should therefore specify **what and why**, not **how**. The proposed template removes implementation details (pre-gate agent territory), adds testable acceptance criteria (post-gate agent needs), caps context to what cannot be discovered (respects context window budgets), and scales ceremony to complexity (adaptive compute). Research consistently shows that giving executors focused context with clear termination criteria outperforms giving them exhaustive but unfocused specifications.
