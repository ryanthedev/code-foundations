# UX Designer Perspective: Whiteboarding Plan Detail Level

**Role:** UX Designer specializing in developer tools and developer experience
**Core question:** How detailed should a whiteboarding plan be, given it has two readers: a human who approves it and LLM subagents who execute it?

---

## 1. What the Building Architecture Already Handles

Before recommending any change to whiteboarding output, it is critical to understand what the downstream building system already provides. The building skill does not simply execute the plan verbatim -- it wraps every phase in a discovery-design-implement-review pipeline:

**Pre-gate agent (Phase N.1):** Searches the codebase, maps what exists vs. what the plan assumes, writes discovery findings, and produces implementation-ready pseudocode. This agent loads `cc-construction-prerequisites`, `cc-pseudocode-programming`, `aposd-designing-deep-modules`, and `cc-routine-and-class-design`.

**Implementation agent (Phase N.2):** Reads the discovery file and pseudocode file, then translates pseudocode to code. It is explicitly told "implement exactly what the pseudocode specifies" and "do NOT add features not in pseudocode."

**Post-gate agent (Phase N.3):** Reviews implementation against pseudocode spec. Checks spec match, dead code, correctness across six dimensions, and defensive programming.

**TaskCreate with blockedBy chains:** Phases cannot be skipped. N.2 is blocked by N.1. N.3 is blocked by N.2. The next phase is blocked by the current phase's checkpoint.

**File-based handoff:** Discovery, pseudocode, and review files live in `docs/building/`. Each agent reads from files, not from conversational context. The main orchestrator's context stays clean.

**What this means for plan design:** The plan does not need to contain pseudocode, discovery findings, or implementation-level detail. The pre-gate agent generates all of that at execution time, with fresh codebase knowledge. The plan needs to tell the pre-gate agent *what to investigate and design*, not *how to implement it*.

---

## 2. The Right Level of Detail -- Dual-Audience Document Design

The plan file has a fundamental dual-audience problem. The human reader needs:
- Strategic clarity (what are we building and why)
- Decision transparency (what alternatives were considered)
- Scope boundaries (what is explicitly out of scope)
- Approval surface (can I say yes or no to each phase)

The LLM subagent reader needs:
- Unambiguous task boundaries (what files, what changes)
- Success criteria (how to know a phase is done)
- Dependency information (what must exist before this phase starts)
- Constraint signals (what NOT to do)

These are not the same needs. But they are not contradictory either. The mistake would be to optimize for one audience at the expense of the other. The current plan template tries to serve both but leans toward the human reader (context, approach, rationale) while underserving the subagent reader (vague task bullets, no success criteria, no constraint signals).

### The Goldilocks Principle

**Too little detail (current "- [ ] specific task with file path" bullets):**
- Human can approve but cannot judge scope accurately
- Pre-gate agent must guess at intent behind terse bullets
- Implementation agent has no constraint signals, may over-build or under-build
- Post-gate agent has no success criteria to verify against

**Too much detail (pseudocode, implementation specifics in the plan):**
- Human gets overwhelmed, skims, approves without reading
- Pre-gate agent's discovery phase becomes redundant (plan already prescribes implementation)
- Plan becomes brittle -- if codebase has changed since planning, detailed implementation instructions are wrong
- Violates the architecture's design: pre-gate exists precisely to do implementation-time discovery

**Right level of detail (intent + boundaries + criteria):**
- Human reads a phase in under 60 seconds and can approve or reject
- Pre-gate agent knows what to search for, what the phase should accomplish, and what is out of scope
- Implementation agent has clear success criteria to implement toward
- Post-gate agent has explicit criteria to verify against

### Research Framing

The H2R paper (2509.12810) demonstrates that hierarchical memory should decouple high-level planning memory from low-level execution memory. The plan file is high-level memory. The pre-gate agent's pseudocode output is low-level memory. Mixing granularities in one document degrades both retrieval accuracy and execution quality.

ReCode (2510.23564) argues that planning IS a high-level form of action, and the appropriate granularity should match the current phase. During whiteboarding, we are at the coarsest granularity -- strategic decomposition. During pre-gate, we zoom to intermediate granularity -- design decisions. During implementation, we zoom to fine granularity -- code. The plan should be written at whiteboarding granularity, not implementation granularity.

---

## 3. UX Argument -- Information Architecture for Plan Files

### Principle: Separate What from How, and Never from Always

A plan file is an information architecture problem. It must organize information so that:

1. **The human can scan the document structure and approve phase-by-phase.** This means clear headings, short phase descriptions, and explicit scope boundaries.

2. **The LLM subagent can extract actionable instructions from the phase section alone.** Each phase section must be self-contained enough that when pasted into a subagent prompt (as the building skill does), the agent has sufficient context to begin work.

3. **Neither reader needs to hold the entire document in working memory.** The human reads one phase at a time during approval. The subagent receives one phase at a time during execution.

### The Context Window as a UX Constraint

The COMPASS paper (2510.08790) identifies context management as the central bottleneck of long-horizon agent tasks. The building skill already addresses this by using file-based handoff -- but the plan file itself is injected into subagent prompts. If a phase section is 500 words of vague prose, the pre-gate agent wastes context window on ambiguity. If a phase section is 50 words of terse bullets, the pre-gate agent lacks enough signal to begin meaningful discovery.

The ReCAP paper (2510.23822) recommends maintaining the original goal as a persistent, uncompressible element. In plan terms: the Context section and Chosen Approach section serve this role. They should be concise but always present when a phase is dispatched. The per-phase sections should contain only phase-specific information.

### The Orchestrator Paper's Insight

The Manager Agent paper (2510.02557) emphasizes that task specifications sent to agents need: context, constraints, and deadlines. The current plan template provides context (phase name + task bullets) but omits constraints (what not to do, scope limits) and success criteria (when is this phase done). These omissions force the pre-gate agent into guesswork.

### The Lingxi Insight: Stage-Aware Knowledge

Lingxi (2510.11838) shows that different types of knowledge matter at different stages: design patterns matter at analysis, implementation specifics matter at fixing. The plan is consumed at analysis stage (pre-gate). It should contain analysis-appropriate information: goals, constraints, boundaries, criteria. Implementation specifics belong in the pseudocode file that the pre-gate agent produces.

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

### Problems with Current Template

| Element | Human Reader | LLM Subagent Reader |
|---------|-------------|-------------------|
| Goal | Good -- 1 sentence of intent | Good -- clear starting point for discovery |
| Files | Good -- scope visible | Partially good -- but may be wrong at execution time |
| Implementation details | Risky -- human may not understand, skims | Risky -- may conflict with pre-gate discovery findings |
| Dependencies | Good -- ordering clear | Good -- maps to blockedBy chains |
| *Missing: Success criteria* | Cannot judge when to approve | Cannot judge when phase is done |
| *Missing: Constraints/scope* | Cannot judge what is excluded | May over-build or drift |
| *Missing: Acceptance test* | Must trust blindly | Post-gate has no verification anchor |

### Recommended Template

```markdown
### Phase N: [Name]
**Model:** [haiku/sonnet/opus]

**Goal:** [1-2 sentences: what this phase accomplishes and why]

**Scope:**
- IN: [what this phase covers]
- OUT: [what is explicitly excluded or deferred]

**Tasks:**
- [ ] [Action verb] + [what changes] + [in which file/module]
- [ ] [Action verb] + [what changes] + [in which file/module]

**Acceptance criteria:**
- [ ] [Observable, verifiable condition that proves this phase is done]
- [ ] [Observable, verifiable condition that proves this phase is done]

**Constraints:**
- [Technical constraint: e.g., "must use existing auth middleware, not a new one"]
- [Design constraint: e.g., "no new public API surface beyond X"]

**Dependencies:** [Phase N-1 or specific prerequisite]

**Notes:** [edge cases, gotchas, decisions made during planning -- optional]
```

### What Changed and Why

| Change | Why (Human) | Why (Subagent) |
|--------|------------|----------------|
| Renamed "Section" to "Phase" | Matches building terminology | Reduces translation overhead in dispatch prompt |
| Added Model line | Can review/override model choice | Building skill reads this for auto-detection |
| Added Scope (IN/OUT) | Can verify scope boundaries | Pre-gate agent knows what NOT to explore |
| Replaced "Implementation details" with "Acceptance criteria" | Can judge done-ness without understanding code | Post-gate agent has verification anchors |
| Added Constraints | Can verify design intent is preserved | Implementation agent has guardrails |
| Kept Tasks as action-verb bullets | Scannable checklist | Sufficient for pre-gate discovery targeting |
| Made Notes optional | Not every phase has gotchas | Avoids empty sections cluttering context |
| Removed "Files to create/modify" as mandatory | Files may change at execution time | Pre-gate agent discovers actual files; plan files are hints at best |

### On Files: Hints, Not Mandates

The current template asks for specific file paths. This is useful as a scope signal but dangerous as a mandate. The pre-gate agent's discovery phase may find that the plan's file list is wrong -- a file was renamed, a module was reorganized, or the planned approach requires different files than anticipated.

Recommendation: Include file paths in the Tasks bullets as context (e.g., "Add validation to `src/auth/middleware.ts`") but do not list them in a separate "Files" section that implies they are the complete and correct set. The pre-gate agent should treat plan file paths as starting points for discovery, not as the discovery itself.

### On Acceptance Criteria: The Verification Anchor

This is the single most important addition. Currently, the post-gate agent verifies implementation against pseudocode -- but the pseudocode is produced by the pre-gate agent, not by the human. There is no human-authored verification anchor in the pipeline. Acceptance criteria in the plan file create that anchor:

1. Human writes criteria during whiteboarding (forces them to think about done-ness)
2. Pre-gate agent reads criteria to scope discovery appropriately
3. Implementation agent reads criteria to know when to stop
4. Post-gate agent verifies criteria are met (not just that pseudocode was followed)

This closes a gap in the current architecture where the human approves a plan but has no say in what "done" means at the phase level.

---

## 5. Research Backing

| Paper | Key Insight | Application to Plan Design |
|-------|------------|---------------------------|
| H2R (2509.12810) | Decouple high-level planning memory from low-level execution memory | Plan stays at strategic level; pseudocode (low-level) generated at execution time by pre-gate agent |
| COMPASS (2510.08790) | Context management is the central bottleneck; separate static from dynamic context | Plan is static context (goal, scope, criteria). Discovery and pseudocode are dynamic context generated per-phase. |
| ReCAP (2510.23822) | Maintain original goal as persistent, uncompressible context element; compress completed work | Plan's Context + Approach sections are the goal anchor. Per-phase sections should be concise -- the pre-gate agent expands them. |
| ReCode (2510.23564) | Planning is a high-level action; granularity should match the current phase | Whiteboarding operates at coarse granularity (goals, scope, criteria). Pre-gate zooms to intermediate (pseudocode). Implementation zooms to fine (code). |
| Manager Agent (2510.02557) | Task specifications need context, constraints, and deadlines | Current template provides context but omits constraints and success criteria. Recommended template adds both. |
| Lingxi (2510.11838) | Different knowledge types matter at different stages; design patterns at analysis, implementation at fixing | Plan consumed at analysis stage should contain analysis-appropriate knowledge (goals, constraints, boundaries), not implementation-appropriate knowledge (pseudocode, specific patterns). |
| Gemini Robotics (2510.03342) | Orchestrator/executor separation; thinking before acting improves multi-step success | Building already implements this separation. Plan should support the orchestrator (building skill) by providing clear phase boundaries, not the executor (implementation agent) by providing code-level detail. |
| CWM (2510.02387) | Procedural knowledge (how and why) transfers better than declarative knowledge (what) | Plan should capture rationale (why this approach, why these constraints) not just structure (what files to change). Rationale enables pre-gate agent to make better design decisions when reality differs from plan. |

### The Dual-System Argument

Multiple papers converge on a dual-system architecture: a slow deliberative system (planning, strategy) paired with a fast reactive system (execution, adaptation). The building architecture already implements this -- whiteboarding is the slow system, building with its subagents is the fast system.

The plan file is the interface between these two systems. Like any good interface (per APOSD's deep module principle), it should be simple relative to the complexity it mediates. The plan should hide the complexity of the human's decision-making process (approaches considered, research done, trade-offs weighed) behind a simple interface of goals, scopes, criteria, and constraints per phase.

The plan currently exposes too much of the "how" (implementation details) and too little of the "what" and "why" (acceptance criteria, constraints, rationale). Inverting this ratio serves both audiences better.

---

## Summary

The whiteboarding plan should be a **strategic document, not an implementation document**. It should contain enough detail for a human to approve scope and intent, and enough structure for an LLM subagent to begin targeted discovery -- but not so much implementation detail that it either overwhelms the human or conflicts with the pre-gate agent's execution-time findings.

The key additions are: explicit scope boundaries (IN/OUT), acceptance criteria per phase, and constraints. The key removal is: implementation details that belong in the pre-gate agent's pseudocode output, not in the plan. File paths become hints within task bullets rather than mandated lists.

This aligns with the building architecture's design: the plan is the *what* and *why*; the pre-gate agent produces the *how*; the implementation agent produces the *code*; the post-gate agent verifies all three against each other.
