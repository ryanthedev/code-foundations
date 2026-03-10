# Failure Analyst (Round 2): The Detail Calibration Problem

## Persona Lens
What level of plan detail CAUSES failures vs. PREVENTS them? The building architecture already mitigates many failure modes -- where does the plan itself still need to carry the load?

---

## 1. What the Building Architecture Already Handles

Before arguing about plan detail, I need to be honest about what the existing system already protects against. The building skill has significant structural defenses that reduce the burden on plan quality.

### Mitigations Already in Place

| Failure Mode | Architecture Defense | How It Works |
|---|---|---|
| **Stale plan assumptions** | Pre-gate discovery | Pre-gate agent searches the codebase BEFORE writing pseudocode. If the plan says "modify auth.ts" but auth.ts was refactored into three files, discovery catches this. |
| **Implementation drift from spec** | Pseudocode as contract | Implementation agent is explicitly told: "implement exactly what the pseudocode specifies." Deviations must be flagged, not silently introduced. |
| **Self-review blindness** | Post-gate agent (fresh context) | A separate agent with fresh context reviews each phase's output. It loads its own skill lenses (correctness verification, defensive programming) and checks spec match, dead code, and 6-dimension correctness. |
| **Phase skipping** | TaskCreate with blockedBy chains | Phase N.2 literally cannot start until N.1 is completed. Phase N+1.1 cannot start until N.4 is committed. This is structural, not prompt-based. |
| **Scope creep during implementation** | Implementation agent anti-patterns | "If not in pseudocode, flag it as deviation." The agent is told not to add features, refactor unrelated code, or "improve" the design. |
| **Context loss between phases** | File-based handoff | Discovery, pseudocode, and review artifacts persist as files. Each subagent reads its inputs from disk, not from conversation history. |
| **Plan-reality divergence** | Pre-gate SKIP/UPDATE_PLAN signals | Pre-gate agent can return UPDATE_PLAN if reality does not match plan assumptions. Building skill then pauses and asks the user. |

### What This Means for Plan Detail

These defenses create a **floor of competence** that the system reaches even with mediocre plans. A plan that says "Phase 1: Add authentication" will not produce total garbage because:
1. Pre-gate will discover what exists, find patterns, and write specific pseudocode
2. Implementation agent will follow that pseudocode
3. Post-gate will verify the implementation

This is the critical insight: **the pre-gate agent is itself a discovery-and-design step**. It compensates for plan vagueness by doing its own research. The plan does not need to be the final word on implementation details -- it needs to give the pre-gate agent the right problem to investigate.

---

## 2. The Right Level of Detail: The Failure Curve

Plan detail exists on a spectrum. Both extremes cause failures, but they cause *different* failures with *different severities*.

### The Under-Specification Failure Zone

When plans are too vague, the pre-gate agent must make unsupervised decisions about scope, approach, and constraints. The building architecture mitigates some of this (discovery catches missing files, post-gate catches bugs), but it cannot compensate for:

| What Goes Wrong | Example | Why Architecture Cannot Save It |
|---|---|---|
| **Wrong scope** | Plan says "add search." Pre-gate interprets this as full-text search when user meant filter-by-name. | Pre-gate agent has no way to know user intent. It will build something plausible but wrong. Post-gate checks correctness against pseudocode, not against user intent. |
| **Wrong approach** | Plan says "improve performance." Pre-gate chooses caching when the real bottleneck is N+1 queries. | Discovery can find what exists but cannot benchmark. The approach decision is made without the data needed to make it well. |
| **Missing constraints** | Plan does not mention backward compatibility. Pre-gate redesigns the API. Post-gate sees a clean implementation and passes. | No constraint = no check. Post-gate verifies what the pseudocode specified, not what the user assumed was obvious. |
| **Cross-phase incoherence** | Phases 1-3 each look fine individually, but phase 3 creates a type that conflicts with phase 1's interface. | Each pre-gate agent operates independently. No agent holds the full cross-phase picture. TaskCreate chains enforce ordering but not coherence. |

**Root cause:** Under-specified plans transfer decision authority to subagents that lack the context to decide well. The pre-gate agent is competent at *how* but blind to *what* and *why*.

### The Over-Specification Failure Zone

When plans contain too much implementation detail, a different class of failures emerges:

| What Goes Wrong | Example | Why Architecture Cannot Save It |
|---|---|---|
| **Plan locks in stale details** | Plan specifies "use `createUser(name, email)` from users.ts." But since planning, the function was renamed to `registerUser` with different params. Pre-gate discovery finds the mismatch -- but what does it do? | Pre-gate can flag UPDATE_PLAN, which pauses everything and asks the user. If the plan has 30 specific function signatures, half of them may be stale. Each one triggers a pause. The plan becomes an obstacle course. |
| **Pre-gate ignores its own discovery** | Plan says "modify `handleAuth` on line 47 of auth.ts to add JWT validation." Pre-gate dutifully writes pseudocode for exactly that, even though its discovery found that auth.ts was refactored and the right place is now middleware.ts. | The implementation agent is told to follow pseudocode exactly. If the pre-gate agent writes pseudocode that matches the (stale) plan rather than its own discovery, the implementation will target the wrong file. |
| **Pseudocode becomes redundant transcription** | Plan contains detailed pseudocode-level implementation notes. Pre-gate agent copies them into the pseudocode file with minor reformatting. The "design" step becomes clerical. | The pre-gate agent's value is in DISCOVERING what exists and DESIGNING based on reality. If the plan already contains the design, pre-gate becomes a copy operation that adds no value and no error-checking. |
| **Implementation agent fights the spec** | Plan specifies a class hierarchy. Pre-gate dutifully designs it. But the implementation agent's `aposd-simplifying-complexity` skill identifies it as unnecessary complexity. The agent is stuck: follow the pseudocode (skill says: yes) or simplify (skill says: yes). | The agent's anti-pattern table says "implement the pseudocode, suggest improvements separately." But it cannot suggest improvements to an orchestrator that only checks DONE/BLOCKED. The improvement signal is lost. |

**Root cause:** Over-specified plans collapse the discovery-design-implement pipeline into a transcription pipeline. The pre-gate agent, which is the system's strongest defense against plan-reality mismatch, is neutered by a plan that already made all the decisions.

### The Failure-Minimizing Sweet Spot

The sweet spot is where the plan specifies *enough* to prevent scope/approach/constraint ambiguity, but *not so much* that it preempts the pre-gate agent's discovery and design work.

```
         Failure Rate
              |
  High   *    |                                    *
              |  *                              *
              |     *                        *
              |        *                  *
  Low         |           *    ****    *
              |              **    **
              +----------------------------------------→
              Vague                              Detailed

              ← Under-spec        Over-spec →
                failures          failures

        [scope wrong]     [sweet spot]    [stale details]
        [approach wrong]                  [discovery neutered]
        [constraints missing]             [transcription not design]
```

**The sweet spot plan specifies:**
- WHAT to build (goal, scope boundary, success criteria)
- WHY constraints exist (performance budget, backward compat, security)
- WHICH files/areas are involved (scoping, not implementation)
- WHAT DONE LOOKS LIKE (externally verifiable)

**The sweet spot plan does NOT specify:**
- HOW to implement (function signatures, class hierarchies, algorithms)
- EXACT code changes (line numbers, specific edits)
- DESIGN DECISIONS that depend on codebase state (which pattern to use, how to structure modules)

---

## 3. Failure Analysis Argument: Concrete Failure Modes at Each Detail Level

### Level 1: Skeleton Plan (Too Vague)
```markdown
### Phase 1: Authentication
- [ ] Add auth to the app
```

**Failure modes:**
- Pre-gate agent invents scope: adds OAuth, JWT, session management, RBAC -- when user wanted a simple API key check
- No constraint awareness: pre-gate might redesign the entire auth flow when backward compatibility was assumed
- Cross-phase incoherence: later phases reference auth patterns that phase 1's agent chose differently

**Failure probability: HIGH.** The building architecture's pre-gate discovery helps with *how* but cannot compensate for missing *what* and *why*.

### Level 2: Goal + Constraints Plan (The Sweet Spot)
```markdown
### Phase 1: API Key Authentication
**Goal:** Add API key validation to all /api/v2/* routes

**Constraints:**
- Must not break existing /api/v1/* routes (backward compat)
- API keys stored in environment variables, not database
- Return 401 with JSON error body on invalid key

**Files likely involved:**
- `src/middleware/` - new middleware
- `src/routes/api-v2/` - apply middleware
- `tests/` - auth tests

**Done when:**
- [ ] `npm test -- --grep "api-key"` passes
- [ ] Existing /api/v1/ tests still pass
- [ ] Manual: `curl -H "X-API-Key: invalid" /api/v2/data` returns 401
```

**Why this works:**
- Pre-gate agent knows WHAT to build (API key auth, not OAuth) and WHERE to look
- Constraints are explicit: backward compat, env vars, error format
- "Files likely involved" guides discovery without dictating implementation
- Success criteria are externally verifiable -- post-gate and VERIFY phases can check them
- Pre-gate is free to discover the actual file structure and design the middleware however makes sense

**Failure probability: LOW.** The plan constrains scope and defines success without constraining implementation. Pre-gate discovery adds the implementation detail that the plan deliberately omits.

### Level 3: Prescriptive Plan (Too Detailed)
```markdown
### Phase 1: API Key Authentication
**Model:** haiku
- [ ] Create `src/middleware/apiKeyAuth.ts`:
  ```typescript
  export function apiKeyAuth(req: Request, res: Response, next: NextFunction) {
    const key = req.headers['x-api-key'];
    if (key !== process.env.API_KEY) {
      return res.status(401).json({ error: 'Invalid API key' });
    }
    next();
  }
  ```
- [ ] In `src/routes/api-v2/index.ts`, add `router.use(apiKeyAuth)` after line 12
- [ ] Add test in `tests/middleware/apiKeyAuth.test.ts` with cases:
  - valid key returns 200
  - missing key returns 401
  - invalid key returns 401
```

**Failure modes:**
- If `src/routes/api-v2/index.ts` does not exist or has a different structure, pre-gate flags UPDATE_PLAN, pausing execution for user intervention on a trivial discovery
- The code snippet locks in a single-key design. If the pre-gate agent discovers the codebase already has a key-rotation pattern, it cannot use it without conflicting with the plan
- "After line 12" is maximally brittle. Any prior change to the file invalidates this
- Pre-gate agent's job is reduced to transcription: copy the plan into pseudocode.md, losing the discovery-design value
- Model override to haiku may be wrong if the middleware directory has complex patterns the agent needs to understand

**Failure probability: MEDIUM-HIGH.** The plan is likely to be partially stale by execution time. Each stale detail triggers an UPDATE_PLAN pause or, worse, a pre-gate agent that follows stale instructions over its own discovery.

### Level 4: Pseudo-Implementation Plan (Way Too Detailed)

Plans that contain full pseudocode, complete type definitions, database schemas with column types, and step-by-step algorithms. These are effectively implementation specs masquerading as plans.

**Failure modes:** All of Level 3, plus:
- The plan file itself becomes the longest document in context, crowding out the actual codebase
- Any change to any detail cascades across the plan (change amplification -- the exact symptom APOSD warns about)
- The whiteboarding phase takes so long that the codebase changes before building starts

**Failure probability: HIGH.** These plans create the illusion of thoroughness while actually increasing fragility. Every additional detail is a potential point of staleness.

---

## 4. Concrete Recommendation: Updated Section Template

Based on the failure curve analysis, the section template should enforce the sweet spot: goals, constraints, scope, and verifiable success criteria. It should explicitly prohibit implementation-level detail.

### Proposed Section Template

```markdown
### Section N: [Name]

**Goal:** [What this section accomplishes -- one sentence, outcome-focused]

**Scope boundary:**
- IN: [what this section covers]
- OUT: [what this section explicitly does NOT cover]

**Constraints:**
- [Hard constraint with rationale -- e.g., "Must not break /api/v1/ (backward compat)"]
- [Performance/security/compatibility constraints]

**Files likely involved:**
- `path/to/area/` - [why this area, not what to change]

**Depends on:** [Phase X output: specific artifact or decision]
**Produces for later phases:** [What downstream phases need from this one]

**Done when:**
- [ ] [Externally verifiable criterion -- test command, build check, or observable behavior]
- [ ] [At least one criterion must be machine-runnable]

**Risk:** [Low/Medium/High]
**If blocked:** [One-sentence fallback strategy -- only required for Medium/High risk]
```

### What This Template Deliberately Excludes

| Excluded Element | Why |
|---|---|
| Function signatures | Pre-gate agent discovers the actual codebase API and designs to match |
| Code snippets | Implementation agent writes code; plan writes intent |
| Line numbers | Maximally brittle; invalidated by any prior change |
| Algorithm choices | Pre-gate agent designs based on what patterns exist in the codebase |
| Specific file names (when uncertain) | "Files likely involved" + directory hints let pre-gate discover the actual structure |
| Class/module design | This is the pre-gate agent's core job via `aposd-designing-deep-modules` |

### What This Template Enforces

| Required Element | Why |
|---|---|
| Goal (outcome-focused) | Prevents scope ambiguity -- the #1 cause of under-specification failures |
| Scope boundary (IN/OUT) | Prevents both scope creep and scope gaps |
| Constraints with rationale | Prevents constraint drift; rationale helps pre-gate agent make judgment calls |
| "Done when" with runnable criterion | Prevents self-assessed completion; enables post-gate and VERIFY to check objectively |
| Cross-phase dependencies | Prevents the 42% context-loss failure mode (VulnBot) |
| Risk + fallback for non-trivial phases | Prevents plan stalls without over-engineering low-risk phases |

---

## 5. Research Backing

### Primary Evidence

**Compartmentalized context prevents degradation (ALAS, 2505.12501).** Each subagent should receive only task-relevant facts. The plan template supports this by specifying goal, scope, and constraints -- not the entire implementation design. The pre-gate agent builds its own context through discovery rather than inheriting a bloated plan.

**Self-assessed progress is unreliable at 67% error rate (Gobel et al., 2603.06064).** The "Done when" field with externally verifiable criteria directly addresses this. Agentic iteration only helps when feedback is externally grounded (compiler errors, test results), not when it is self-assessed. The template forces each phase to define what "grounded feedback" means for that phase.

**Context loss causes 42% of multi-phase failures (VulnBot, 2501.13411).** The "Depends on" and "Produces for later phases" fields create an explicit dependency chain that survives context resets. When building resumes after `/clear`, these fields tell the pre-gate agent what to look for from prior phases.

**Domain-specific details lost in high-level plans cause 33.9% accuracy drops (VerilogCoder, AAAI 2025).** The template handles this through "Constraints" rather than implementation detail. A database migration plan should have constraints like "must be reversible" and "zero-downtime required" rather than detailed SQL. These constraints guide the pre-gate agent to discover and design for the right properties without prescribing the mechanism.

**Schema-gated execution prevents intent-action drift (Strickland et al., 2603.06394).** The "Done when" criteria function as lightweight schemas -- machine-checkable specifications that gate phase completion. They separate conversational intent ("add auth") from execution verification ("test passes, 401 returned").

**Front-loading effort on high-uncertainty work improves efficiency by 193.8% (Plan and Budget, 2505.16122).** The Risk field enables this at the building level: high-risk phases should get more capable models and deeper pre-gate discovery, while low-risk phases can use haiku with minimal ceremony.

### The Architectural Argument

The building system is a **three-stage pipeline per phase**: discover (pre-gate) -> implement -> verify (post-gate). The plan is the **input to the first stage**, not a specification for all three.

When the plan contains implementation details, it short-circuits the pipeline:
- Discovery becomes validation-of-plan rather than exploration-of-reality
- Design becomes transcription rather than engineering
- Verification checks implementation against a possibly-stale plan rather than against actual requirements

When the plan contains only goals, constraints, and success criteria, the pipeline operates as designed:
- Discovery explores the codebase and finds the real state
- Design creates pseudocode based on discovered reality + plan constraints
- Verification checks implementation against externally grounded criteria

The research converges on one principle: **separate the authority to define WHAT from the authority to decide HOW.** The plan holds WHAT authority. The pre-gate agent holds HOW authority. The post-gate agent holds DONE authority. Mixing these authorities is the root cause of failures at both extremes of the detail spectrum.

### What the Research Says About the Middle Ground

The MaAS framework (2502.04180) found that query-dependent compute allocation -- giving easy tasks simple processing and hard tasks complex processing -- reduced costs by 55-94% while maintaining quality. Applied to planning: easy phases need skeletal plans (goal + done-when), hard phases need the full template (goal + constraints + scope + risk + fallback + dependencies). The template should scale with uncertainty, not be uniformly applied.

The ReMA framework (2503.09501) found that separating strategic thinking (what approach to take) from detailed reasoning (how to execute) improved out-of-distribution performance by up to 20%. This maps directly to the plan/pre-gate separation: the plan is strategic (goals, constraints, approach), and the pre-gate agent does the detailed reasoning (discovery, design, pseudocode).

The FLARE framework (AAAI 2025, 32455) found that plans must be validated against actual environment state before execution, and that replanning from current state (not full replan) is more efficient when things go wrong. The building architecture already does this via pre-gate discovery (validate plan against reality) and UPDATE_PLAN signals (replan from current state). The plan template's "If blocked" field supports efficient local recovery rather than full replanning.

---

## Summary

The failure-minimizing sweet spot for plan detail is:

**Specify WHAT (goals, scope, constraints, success criteria). Do NOT specify HOW (implementation details, code, algorithms).**

This is not a philosophical preference. It is the configuration that lets the building architecture's three-stage pipeline operate as designed, with each stage contributing its unique value: discovery maps reality, design responds to reality, and verification checks against externally grounded criteria rather than potentially stale plan details.

The current section template in the whiteboarding skill is close but needs two changes:
1. **Add** the missing fields: scope boundary, cross-phase dependencies, externally verifiable "done when" criteria, and risk-conditional fallbacks
2. **Remove** the implicit invitation to include "specific function/class/pattern" and "key decisions" in implementation details, which pulls the plan toward the over-specification zone

The updated template in Section 4 above represents the failure-minimizing sweet spot backed by the research evidence.
