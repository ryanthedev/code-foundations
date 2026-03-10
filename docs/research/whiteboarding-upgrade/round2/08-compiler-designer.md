# Compiler Designer Analysis (Round 2): The Plan as Intermediate Representation

## Persona Lens

A compiler transforms high-level source into executable machine code through a multi-pass pipeline. The central artifact is the IR (intermediate representation) -- it sits between the frontend (parsing, type-checking) and the backend (register allocation, instruction selection, code generation). Good IR design answers one question: **what information must be preserved from the source, and what can the backend reconstruct?**

The whiteboarding-to-building pipeline is a compiler:
- **Frontend** = whiteboarding (parse user intent, resolve ambiguity, type-check constraints)
- **IR** = plan file (the contract between planning and execution)
- **Backend** = building + subagents (pre-gate discovery, implementation, post-gate review)

Round 1 identified seven proposals. This round asks: **given what the backend actually does, which of those proposals belong in the IR, and which are redundant with backend passes?**

---

## 1. What the Building Architecture Already Handles

Mapping the building pipeline to compiler passes reveals that several round 1 proposals duplicate work the backend already performs.

| Building Sub-Phase | Compiler Analogy | What It Already Does |
|---|---|---|
| Pre-gate discovery | Semantic analysis pass | Reads codebase, finds what exists, identifies gaps between plan assumptions and reality |
| Pre-gate pseudocode | IR lowering | Translates plan-level intent into implementation-ready pseudocode with specific file/function targets |
| Implementation agent | Code generation | Translates pseudocode to code, following the pseudocode as a contract |
| Post-gate review | Verification pass | Checks spec match, dead code, correctness across 6 dimensions, defensive programming |
| Model auto-detection | Target selection | Chooses haiku/sonnet/opus based on phase complexity signals |
| TaskCreate with blockedBy | Instruction scheduling | Enforces execution order through dependency chains |

**Critical observation:** The pre-gate agent already performs discovery. It reads the codebase, checks whether files exist, identifies gaps between plan and reality, and writes pseudocode informed by what it finds. This means the plan does NOT need to contain everything the implementation agent needs -- it needs to contain everything the pre-gate agent needs to do its job well.

This changes the IR design question from "what does the implementation agent need?" to "what does the pre-gate agent need that it cannot discover on its own?"

### What the Pre-Gate Agent Can Reconstruct

The pre-gate agent has full codebase access. It can:
- Discover existing files, functions, patterns (it does this in Phase 1: Discovery)
- Resolve concrete file paths from conceptual descriptions
- Identify current implementation state
- Detect gaps between plan assumptions and reality
- Write detailed pseudocode based on discovered context

### What the Pre-Gate Agent Cannot Reconstruct

Without the plan providing it, the pre-gate agent cannot know:
- **User intent** -- why this feature exists, what problem it solves
- **Chosen approach** -- which of several possible designs was selected and why
- **Constraints** -- performance requirements, compatibility needs, things that must NOT change
- **Scope boundaries** -- what is deliberately excluded (YAGNI decisions)
- **Phase ordering rationale** -- why phase 2 comes after phase 1 (the dependency logic)
- **Test coverage expectations** -- what level of testing was agreed upon
- **Invariants** -- what existing behavior must be preserved

---

## 2. The Right Level of Detail: IR Design Principles

### Principle: Preserve Decisions, Not Discoveries

A good IR preserves the results of frontend analysis (type information, scope resolution, optimization hints) but does not embed target-specific details that the backend will determine anyway. Applied to plans:

| Preserve in Plan (Frontend Decisions) | Leave to Pre-Gate (Backend Discovery) |
|---|---|
| What to build and why | Which files currently exist |
| Which approach was chosen and why alternatives were rejected | Current implementation state of those files |
| Constraints and invariants | Specific function signatures to modify |
| Phase decomposition and ordering rationale | Detailed pseudocode for each change |
| Success criteria (testable postconditions) | How to wire new code into existing patterns |
| Scope boundaries (what is excluded) | Import paths, naming conventions, error handling patterns |

**The anti-pattern is a plan that specifies `Add function handleAuth() to auth/middleware.ts that validates JWT tokens, checks expiry, and calls next()`.** This is backend-level detail that the pre-gate agent should determine after discovering the actual codebase state. The plan should say: `Add authentication middleware that validates tokens before allowing access. Must integrate with existing request pipeline. Must not break existing unauthenticated routes.`

### Principle: Contracts at Phase Boundaries, Not Implementation Details

The IR in a compiler defines the contract between passes -- what each pass can assume about its input and what it must guarantee about its output. The plan should define contracts at phase boundaries:

- **Preconditions**: What must be true before this phase starts (output of prior phases)
- **Postconditions**: What must be true after this phase completes (testable assertions)
- **Invariants**: What must remain true throughout (regression guards)

These are NOT discoverable by the pre-gate agent. They encode user decisions about what "done" means and what must not break. This is the strongest argument from round 1 -- **Proposal 3 (Plan Contracts) belongs in the IR because contracts encode decisions, not facts.**

### Principle: Dependency Edges Are Semantic, Not Structural

Round 1 proposed a formal dependency graph (Proposal 1). But the building command already enforces sequential phase execution via TaskCreate with blockedBy chains. The question is whether the plan needs to express richer dependency semantics than "phase N+1 depends on phase N."

The answer: **only when phases can run in parallel or have non-linear dependencies.** For the common case of sequential phases, the building command's linear chain is sufficient. The plan should annotate exceptions, not the default case.

---

## 3. Compiler Theory Argument: Information Preservation in Multi-Pass Compilation

### The Phase-Ordering Problem

In compiler design, the phase-ordering problem asks: in what order should optimization passes run, given that each pass can enable or disable opportunities for other passes? The solution is to design the IR so that it preserves enough information for passes to run in any order without losing optimization opportunities.

The analogous problem in the building pipeline: **the plan must preserve enough information that the pre-gate agent can make correct decisions regardless of what it discovers during codebase exploration.** If the plan says "add authentication" but does not say "we chose JWT over sessions because of the stateless constraint," the pre-gate agent might design a session-based solution that satisfies the surface requirement but violates the unstated constraint.

**Information that prevents wrong-direction pre-gate decisions:**
1. **Approach rationale** -- why this approach, not alternatives (prevents re-litigating decisions)
2. **Constraints with priorities** -- which constraints are hard vs. soft (prevents violating hard constraints to satisfy soft ones)
3. **Scope boundaries** -- what is deliberately out of scope (prevents scope creep during discovery)
4. **Cross-phase invariants** -- what phase N must not break that phase N-1 established

### The Constant Propagation Analogy

In compilers, constant propagation replaces variables with their known values as early as possible, enabling downstream passes to make better decisions. The planning analogy: **propagate user decisions into the plan as early as possible so the pre-gate agent does not need to re-derive or guess them.**

The current plan schema already does this for some decisions (chosen approach, test coverage level). But it does not propagate:
- **Rejected approaches** -- knowing what was rejected and why prevents the pre-gate agent from accidentally rediscovering and proposing rejected ideas
- **Constraint priorities** -- knowing "latency matters more than throughput" changes pseudocode design
- **Integration points** -- knowing "this must work with the existing event bus" constrains the solution space

### The Dead Code Elimination Analogy

Dead code elimination removes code that cannot be reached. The planning analogy is YAGNI -- removing plan elements that will never be needed. The current skill has a YAGNI gate per section. But it does not have a **global YAGNI pass** that examines the entire plan and asks: "given all sections together, are any sections redundant or subsumable?"

This is the difference between local optimization (per-section YAGNI) and global optimization (cross-section YAGNI). A compiler that only does local dead code elimination misses opportunities that are visible only at the whole-program level.

---

## 4. Concrete Recommendation: Updated Section Template

Based on the IR analysis, the plan section template should be restructured to separate **decisions** (which the plan must preserve) from **details** (which the pre-gate agent will discover).

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
**Model:** [recommended model]

**Intent:** [what this phase accomplishes and why -- 1-2 sentences]

**Constraints:**
- [hard constraint -- MUST be satisfied]
- [soft constraint -- SHOULD be satisfied, with priority]

**Contract:**
- **Requires:** [what prior phases must have established]
- **Produces:** [testable postcondition -- what is true after this phase]
- **Preserves:** [invariant -- what existing behavior must not break]

**Scope:**
- **In:** [what this phase covers]
- **Out:** [what this phase deliberately excludes, and why]

**Approach notes:** [key design decisions the pre-gate agent must respect]
- [decision 1 -- e.g., "Use event-driven pattern, not polling, because of latency constraint"]
- [decision 2 -- e.g., "Rejected: direct DB access from handler. Reason: violates existing repository pattern"]

**Files (approximate):**
- `path/to/area/` - [conceptual description of changes]

**Tasks:**
- [ ] [task description at intent level, not implementation level]
```

### What Changed and Why

| Element | Old | New | Rationale |
|---|---|---|---|
| Goal | Single line | **Intent** with "and why" | Pre-gate needs motivation, not just action |
| Files | Specific paths with changes | **Approximate** paths with conceptual descriptions | Pre-gate discovers actual state; rigid paths become stale |
| Implementation details | Mixed decisions and details | Split into **Constraints**, **Approach notes**, **Scope** | Decisions preserved; details left to pre-gate |
| Dependencies | Freeform text | **Contract** with requires/produces/preserves | Testable, machine-parseable boundary conditions |
| (missing) | -- | **Scope.Out** | Prevents scope creep during pre-gate discovery |
| (missing) | -- | **Approach notes with rejected alternatives** | Prevents re-litigating settled decisions |

### What Was NOT Added

| Round 1 Proposal | Verdict | Rationale |
|---|---|---|
| P1: Dependency Graph | **Defer** | Building already enforces linear chains. Add only when parallel execution is implemented in building. Premature IR enrichment. |
| P2: Control Flow Types | **Defer** | Same reasoning. The backend does not support parallel dispatch yet. Adding annotations the backend ignores is dead code in the IR. |
| P4: Goal-Conflict Detection | **Absorb into Constraints** | Rather than a separate step, make constraints explicit with priorities. Conflicts become visible when two "MUST" constraints contradict. Simpler than formal MUS/MCS analysis. |
| P5: Fallback Preservation | **Keep (simplified)** | Preserve in `## Chosen Approach` section as 1-2 sentence fallback notes, not full fallback plan schemas. The pre-gate agent can expand if needed. |
| P6: Complexity Budget | **Absorb into Model auto-detection** | Building already does this via task/file count heuristics. Adding it to the plan duplicates backend logic. |
| P7: Structured Question Types | **Keep** | Belongs in the frontend (whiteboarding), not the IR (plan). Improves question quality during planning without changing plan schema. |

---

## 5. Research Backing

### Plans Should Preserve Decisions, Not Prescribe Implementation

**SWE-Adept (2603.01327)** demonstrates that structured to-do lists with semantic checkpointing outperform free-form approaches, but the to-do list must be *dynamic* -- expandable when feedback reveals missing steps. This directly supports the principle that plans should specify intent and constraints while leaving implementation details to discovery. SWE-Adept's resolution agent formulates hypotheses and expands its to-do list based on what it finds -- exactly what the pre-gate agent does when it discovers gaps between plan and reality.

**Key number:** Resolution improvement alone (+3.3pp) outweighs localization improvement (+1.3pp). The backend pass (resolution/implementation) contributes more than the frontend pass (localization/planning) when given adequate constraints. This argues for leaner plans with stronger contracts rather than detailed plans with weak contracts.

### Intermediate Representations Must Be Human-Reviewable

**ViviDoc (2603.01912)** shows that structured intermediate representations between planning and execution create a "contract" that constrains error-prone translation. The DocSpec decomposes into State, Render, Transition, Constraint -- four typed components that are both human-readable and machine-parseable. The parallel to the proposed Contract section (Requires, Produces, Preserves) is direct: both decompose a phase boundary into typed, verifiable components.

**Key insight:** Human review should be placed at maximum leverage points -- after planning (before code) and after output (final review). The plan file IS the maximum leverage point. Making it more precise (via contracts) increases the leverage of human review.

### Static Decomposition Fails When Complexity Is Revealed at Runtime

**ReAcTree (2511.02424)** shows that dynamic decomposition at runtime outperforms static up-front decomposition (31% to 61% success rate). The building pipeline already handles this -- the pre-gate agent can recommend SKIP or UPDATE_PLAN when it discovers that a phase is more or less complex than expected. But this only works if the plan preserves enough context for the pre-gate agent to make that judgment. A plan that says "implement authentication" gives the pre-gate agent nothing to evaluate against. A plan that says "implement JWT-based authentication; must integrate with existing Express middleware chain; must not require database changes" gives the pre-gate agent concrete criteria for assessing feasibility and scope.

**HTAM (2511.17198)** reinforces that the most effective architecture mirrors the domain's intrinsic task-dependency graph. For software engineering, the intrinsic dependency is: understand intent -> discover current state -> design changes -> implement -> verify. The building pipeline already mirrors this. The plan's job is to provide the "understand intent" layer so completely that the pre-gate agent can do "discover current state" effectively.

### LLMs Should Translate, Not Plan

**Plan Space Exploration (2603.02070)** argues that LLMs excel at translation between natural language and formal representations but should not perform actual planning computation. Applied to whiteboarding: the LLM's job during planning is to translate user intent into a structured plan (the IR), not to solve the implementation problem. The pre-gate agent solves the implementation problem. This further supports lean plans -- the whiteboarding skill should focus on capturing intent precisely, not on pre-solving implementation challenges.

### Anchor Points Preserve Intent Through Refinement

**AnchorDrive (2603.02542)** introduces anchor points -- sparse key points extracted from an initial generation that guide a more capable generator while preserving high-level intent. The Contract section (Requires/Produces/Preserves) serves exactly this function: these are the anchor points that the pre-gate and implementation agents must respect, even as they make their own decisions about the details.

### Complementary Strengths: Human Decisions, Agent Discovery

**Human-Agent Collaboration (2603.02050)** finds that routine/mechanical sub-tasks should be handed off to AI entirely, while subjective/taste-dependent decisions should remain with the human. The proposed template operationalizes this: the human makes decisions during whiteboarding (approach, constraints, scope boundaries, priorities), and the agents handle mechanical work during building (file discovery, pseudocode generation, implementation, verification). The plan is the handoff contract.

---

## Summary

The plan file is an intermediate representation. Like any good IR, it should preserve the results of analysis that cannot be cheaply reconstructed (user decisions, constraint priorities, scope boundaries, approach rationale) while omitting details that downstream passes will determine more accurately from fresh information (current file state, specific function signatures, import paths, naming conventions).

The strongest single change from round 1 is **Plan Contracts** (Proposal 3), reframed here as the Requires/Produces/Preserves structure. This is the information the backend cannot reconstruct because it encodes user intent about what "done" means and what must not break. Everything else in the template reorganization follows from the principle: preserve decisions, leave discoveries to the agents that have the tools to make them.
