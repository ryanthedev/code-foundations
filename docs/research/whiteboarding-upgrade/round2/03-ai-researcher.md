# Whiteboarding Plan Detail: AI Research Analysis

**Question:** How detailed should a whiteboarding plan be, given that it is consumed by LLM subagents (not humans)?

---

## 1. What the Building Architecture Already Handles

The building system has significant built-in intelligence that makes certain plan details redundant. Understanding what the architecture provides "for free" is essential to avoiding context pollution.

### Fresh Context Windows Per Phase

Each sub-phase (PRE-GATE, IMPLEMENT, POST-GATE) dispatches a **fresh subagent** with no prior conversation history. The subagent receives only:
- The plan file (phase section)
- Discovery/pseudocode artifact files (written by pre-gate)
- A skill-loaded agent template with baked-in checklists

This means the plan does not need to carry implementation-level detail forward. The pre-gate agent does its own codebase discovery -- it searches for files, reads current state, identifies gaps between plan assumptions and reality, and writes both a discovery document and implementation-ready pseudocode. The plan's job is to tell the pre-gate agent *what to investigate*, not *what it will find*.

### TaskCreate Enforcement

The building orchestrator creates all sub-phase tasks upfront with `blockedBy` chains. This is mechanical enforcement -- the orchestrator cannot skip PRE-GATE, cannot proceed without POST-GATE PASS, cannot commit without all gates passing. The plan does not need to describe this process. It only needs to describe the *work*.

### Model Auto-Detection

The building skill auto-detects model tier (haiku/sonnet/opus) from task count, file count, and keyword signals in the plan text. Plans only need an explicit `**Model:**` override when the auto-detection would be wrong.

### Skill Loading Per Phase

Each agent type loads 4 specific skills that provide checklists and mental models:
- Pre-gate: construction prerequisites, pseudocode programming, deep module design, routine/class design
- Implementation: control flow, data organization, code clarity, simplifying complexity
- Post-gate: verifying correctness, quality practices, module review, defensive programming

These skills are baked into the agent templates. The plan does not need to specify quality criteria -- the agents carry their own.

### What This Means for Plan Detail

The architecture handles: execution ordering, quality verification, codebase discovery, pseudocode generation, model selection, and skill-based review. The plan needs to handle: *intent*, *scope*, *constraints*, and *structural decisions the agents cannot infer*.

---

## 2. The Right Level of Detail

### The Goldilocks Problem

Plans consumed by LLM subagents face a different optimization problem than plans consumed by humans.

**Too much detail causes:**
- **Context pollution.** Fresh subagent context windows are finite. Every word of plan detail competes with codebase discovery, pseudocode, and skill checklists for attention. The pre-gate agent reads the plan, then searches the codebase, then writes pseudocode -- plan verbosity directly reduces the attention budget available for discovery.
- **Stale specificity.** Detailed file paths, function signatures, and implementation patterns written during whiteboarding become wrong when the pre-gate agent discovers the actual codebase state. The agent then faces a conflict between plan specificity and reality, which burns reasoning tokens on reconciliation.
- **Constraint on agent reasoning.** Over-specified plans reduce the pre-gate agent to a transcription task rather than a design task. The pre-gate agent has `aposd-designing-deep-modules` and `cc-routine-and-class-design` loaded -- it is better equipped to make design decisions *after* codebase discovery than the whiteboarding phase is *before* discovery.

**Too little detail causes:**
- **Hallucinated scope.** Without clear boundaries, the pre-gate agent may discover more than needed and design more than required. The implementation agent may add features not in scope.
- **Ambiguous intent.** The pre-gate agent can discover *what exists* but cannot infer *what the user wants*. Intent must come from the plan.
- **Missing constraints.** Non-obvious constraints (performance requirements, API compatibility, migration concerns) that are not discoverable from the codebase must be stated explicitly.

### The Optimal Information Density

Based on the architecture analysis, a plan phase should contain:

| Include | Exclude |
|---------|---------|
| **Goal:** what this phase accomplishes (1-2 sentences) | How to accomplish it (agent decides) |
| **Scope boundary:** what files/modules are in play | Exact function signatures or implementations |
| **Constraints:** non-discoverable requirements | Patterns the agent will discover via search |
| **Dependencies:** what must exist before this phase | Execution ordering (TaskCreate handles this) |
| **Success criteria:** how to know this phase is done | Quality criteria (skills handle this) |
| **Key decisions already made:** chosen approach, trade-offs | Design decisions the agent should make post-discovery |

This maps to roughly **50-100 words per phase**, not the current template's 200-300 words per section.

---

## 3. AI Research Argument

### PaperBench: The Plan-Execution Gap (2504.01848)

The most directly relevant finding comes from PaperBench. The paper demonstrates that "agents fail not at reasoning or code-writing, but at long-horizon task execution -- they quit early, fail to strategize about time allocation, and cannot execute multi-step plans they themselves formulate."

Critical insight: **the bottleneck is not plan quality but execution scaffolding.** The building architecture already addresses this with forced continuation (TaskCreate chains prevent early termination), piecemeal execution (sub-phases break work into micro-steps), and fresh context per phase (prevents context window exhaustion).

The PaperBench finding that "forced continuation" (IterativeAgent) can triple scores (o3-mini: 2.6% to 8.5%) validates the building architecture's `blockedBy` enforcement. But it also implies that plan detail is not the lever -- execution scaffolding is.

However, PaperBench also shows scaffolding sensitivity is model-specific: IterativeAgent improved o1 by +11.2pp but degraded Claude 3.5 Sonnet by -4.9pp. This suggests that **plan format should be model-aware**, but the current whiteboarding skill does not consider this.

### PaperCoder: Top-Down Decomposition (2504.17192)

PaperCoder achieves 88% best-ranking in human evaluations and 45.14% on PaperBench Code-Dev using a three-stage pipeline: **plan -> analyze -> code**. This maps directly to building's **plan -> pre-gate -> implement** pipeline.

The key finding: PaperCoder's planning stage produces an "overall plan" with architecture diagrams, file dependencies, and configuration -- but the *analysis stage* (equivalent to pre-gate) is where per-file implementation specs are generated. The planning stage does NOT produce implementation-level detail. It produces structural decisions.

This validates the current architecture: whiteboarding should produce structural decisions (approach, file organization, phase decomposition), and pre-gate should produce implementation specs. The current whiteboarding template's "Implementation details" section (specific function/class/pattern, key decisions, edge cases) is doing work that belongs in pre-gate.

### Test-Time Scaling Survey: Verification as Bottleneck (2503.24235)

The survey's key pattern: "the quality of the verifier is the primary limiter of search-based scaling. Invest in verifier quality before increasing search budget."

Applied to building: POST-GATE (the verifier) matters more than plan detail (the search input). The building architecture already invests heavily in verification -- post-gate-agent loads 4 skills and does 6-dimension correctness checking. This further supports the argument that plan detail beyond what is needed for correct scoping is wasted effort.

### Multi-SWE-bench: Description Length Correlates with Success (2504.02605)

"Richer issue descriptions help agents succeed." This might seem to argue for more plan detail, but the key word is "richer" -- not "longer." The study measures *information content* relevant to the task, not verbosity.

Applied to whiteboarding: plans should be informationally rich (clear intent, explicit constraints, unambiguous scope) without being verbose (implementation patterns, pseudocode-level detail, discoverable information).

### Hierarchical Semantic Decomposition (2505.05622)

CityNavAgent decomposes navigation into landmark -> object -> motion levels. The principle: "for any long-horizon task, decompose into progressively finer sub-goals with decreasing planning frequency at higher levels."

Applied to building: whiteboarding operates at the "landmark" level (what phases, what goals), pre-gate operates at the "object" level (what files, what designs), and implementation operates at the "motion" level (what code). The current whiteboarding template blurs these levels by including file-level implementation details in what should be a landmark-level document.

### Autonomous Agent Survey: Coordination Degradation (2504.19678)

"Multi-agent performance drops at >7 iterations" due to communication overhead. While building uses fresh contexts (avoiding this specific failure mode), the principle applies to plan density: every additional detail in the plan is a communication signal that must be processed, verified against reality, and either followed or reconciled. Lean plans reduce coordination overhead.

### SWEET-RL: Credit Assignment (2503.15478)

SWEET-RL demonstrates that effective multi-turn agent training requires step-wise credit assignment rather than trajectory-level rewards. Applied to building: each phase should have independently evaluable success criteria so that POST-GATE can perform meaningful verification. Plans that define success at the trajectory level ("the feature works") rather than the phase level ("this module exposes interface X") make verification harder.

---

## 4. Concrete Recommendation: Updated Section Template

### Current Template (200-300 words per section)

```markdown
### Section N: [Name]

**Goal:** [what this section accomplishes]

**Files to create/modify:**
- `path/to/file.ts` - [what changes]
- `path/to/other.ts` - [what changes]

**Implementation details:**
- [specific function/class/pattern]
- [key decisions]
- [edge cases to handle]

**Dependencies:** [what must be done first]
```

### Proposed Template (50-100 words per section)

```markdown
### Phase N: [Name]

**Goal:** [1-2 sentences: what this phase accomplishes and why]

**Scope:** [which modules/areas are in play -- NOT specific file paths unless critical]

**Constraints:** [non-discoverable requirements: perf targets, API compat, migration rules]

**Done when:** [observable success criteria the post-gate agent can verify]
```

### What Changed and Why

| Removed | Reason |
|---------|--------|
| `Files to create/modify` with specific paths | Pre-gate agent discovers these via codebase search. Plan paths become stale. |
| `Implementation details` (function/class/pattern) | Pre-gate agent designs these post-discovery with loaded skills. Plan-level design is pre-discovery guesswork. |
| `Edge cases to handle` | Post-gate agent's 6-dimension correctness check catches these. Listing them in the plan is redundant with skill checklists. |

| Added | Reason |
|-------|--------|
| `Done when` (success criteria) | Enables POST-GATE to verify phase completion independently. Per-phase credit assignment (SWEET-RL principle). |
| `Constraints` (non-discoverable) | The only information the pre-gate agent cannot find on its own. This is the plan's unique value. |

| Kept | Reason |
|------|--------|
| `Goal` | Intent cannot be inferred from codebase discovery. |
| `Scope` | Boundary definition prevents scope creep. Changed from specific paths to module areas. |

### The "Scope" Field Deserves Special Attention

The current template lists specific file paths. The proposed template describes module areas. This is deliberate:

- **Specific paths** are discoverable and frequently wrong (files get renamed, moved, or don't exist yet). They force the pre-gate agent to reconcile plan vs reality.
- **Module areas** ("the authentication module", "the API layer", "the test suite for X") give the pre-gate agent a search target without over-constraining what it finds.

If a plan *must* reference specific files (e.g., "modify the existing migration at `db/migrations/003.sql`"), that belongs in `Constraints`, not `Scope`, because it is a non-discoverable decision.

---

## 5. Research Backing

| Claim | Source | Finding |
|-------|--------|---------|
| Execution scaffolding matters more than plan detail | PaperBench (2504.01848) | "Agents fail not at reasoning but at long-horizon task execution." Forced continuation tripled scores. |
| Planning stage should produce structure, not implementation specs | PaperCoder (2504.17192) | Three-stage pipeline: plan produces architecture, analysis produces per-file specs. 88% best-ranking. |
| Richer (not longer) descriptions improve agent success | Multi-SWE-bench (2504.02605) | "Description length correlates with success" -- information density, not verbosity. |
| Verification quality limits more than input quality | TTS Survey (2503.24235) | "Verifier quality is the primary limiter of search-based scaling." |
| Hierarchical decomposition should match abstraction levels | CityNavAgent (2505.05622) | Landmark -> object -> motion decomposition. Each level operates at appropriate granularity. |
| Per-step success criteria enable meaningful evaluation | SWEET-RL (2503.15478) | Step-wise credit assignment outperforms trajectory-level rewards by +6% absolute. |
| Communication overhead degrades multi-agent performance | Agent Survey (2504.19678) | Performance drops after >7 iterations. Lean communication reduces coordination cost. |
| Scaffolding sensitivity is model-specific | PaperBench (2504.01848) | Same scaffolding change: o1 +11.2pp, Claude -4.9pp. Plan format may need model awareness. |

### Summary Position

The whiteboarding plan is not a specification -- it is a **prompt for the pre-gate agent**. The pre-gate agent's job is to produce the specification (pseudocode) after codebase discovery. The plan's job is to communicate *intent*, *scope*, *constraints*, and *success criteria* -- exactly the information that cannot be discovered from the codebase and cannot be inferred by the agent.

The current 200-300 word section template includes implementation details that are either discoverable (file paths, patterns), redundant with loaded skills (edge cases, quality criteria), or premature (function signatures designed before codebase discovery). Reducing to 50-100 words of high-signal content per phase should improve downstream agent performance by reducing context pollution and eliminating plan-reality reconciliation overhead.
