# Military Strategist Analysis (Round 2): Mission Orders vs. Detailed Orders

## The Core Question

How detailed should a whiteboarding plan be, given that the building skill dispatches subagents (pre-gate, implementation, post-gate) with their own intelligence-gathering capabilities?

Military doctrine has a precise answer to this: **Auftragstaktik** (mission-type tactics). The question is not "how much detail" but "what kind of detail." The building architecture already embeds a command structure that maps cleanly onto military operations. The whiteboarding plan should be written as a **mission order**, not a **detailed order**.

---

## 1. What the Building Architecture Already Handles

The building skill is not a flat executor. It is a hierarchical command structure with organic intelligence capability at each echelon. Mapping to military analogy:

| Building Component | Military Equivalent | Function |
|---|---|---|
| Whiteboarding plan | **Operations Order (OPORD)** | Commander's concept of the operation -- what to achieve, in what sequence, under what constraints |
| `TaskCreate` with `blockedBy` chains | **Synchronization matrix** | Enforces phase sequencing; no unit moves until prerequisites are met |
| Pre-gate agent (N.1) | **Reconnaissance-in-force** | Deploys into the codebase, maps terrain (discovery), develops scheme of maneuver (pseudocode) |
| Implementation agent (N.2) | **Assault element** | Executes the scheme of maneuver developed by recon, with its own tactical judgment |
| Post-gate agent (N.3) | **After-Action Review (AAR) board** | Independent assessment of whether the objective was actually taken |
| Checkpoint (N.4) | **Consolidation** | Secure gains (commit), update higher HQ (execution log) |
| Gate failure protocol | **Fragmentary Order (FRAGO)** | Modify the plan without rewriting it; retry with adjusted approach |
| Model auto-detection | **Force allocation** | Match capability to task complexity (haiku=light infantry, sonnet=mechanized, opus=heavy armor) |

The pre-gate agent is the critical element. It loads four skills (`cc-construction-prerequisites`, `cc-pseudocode-programming`, `aposd-designing-deep-modules`, `cc-routine-and-class-design`), conducts its own codebase reconnaissance, identifies gaps between plan assumptions and reality, and writes implementation-ready pseudocode. This is not a dumb executor -- it is a subordinate commander with reconnaissance capability and delegated design authority.

**The implication is profound:** The pre-gate agent will independently discover what the whiteboarding plan could never predict -- the actual state of the codebase at execution time, integration points that shifted since planning, patterns that emerged from earlier phases. Detailed implementation instructions in the plan will either be redundant (pre-gate discovers the same thing) or wrong (codebase changed since planning).

---

## 2. The Right Level of Detail: Mission Orders

### Detailed Orders vs. Mission Orders

| Aspect | Detailed Order | Mission Order |
|---|---|---|
| **Specifies** | WHAT + HOW + WHEN + WHERE | WHAT + WHY + constraints |
| **Leaves to subordinate** | Almost nothing | HOW to accomplish the mission |
| **Works when** | Situation is fully known, subordinates lack initiative | Situation is uncertain, subordinates are competent |
| **Fails when** | Reality diverges from plan (which it always does) | Subordinates lack capability to adapt (not our case) |
| **Military example** | "Move 2nd Platoon along Route Alpha at 0600, establish blocking position at grid reference XY123456" | "Prevent enemy reinforcement of Hill 203 by 0800. Priority: deny the northern approach" |

### Why Mission Orders Fit LLM Subagents

The building subagents are not shell scripts. They are LLM agents with:

1. **Organic intelligence capability** -- Pre-gate conducts its own reconnaissance via codebase search, file reading, and pattern analysis. It does not need the plan to tell it what files exist.

2. **Loaded doctrinal knowledge** -- Each agent loads 4 skills that provide checklists, heuristics, and quality criteria. The implementation agent knows `cc-control-flow-quality` and `aposd-simplifying-complexity` -- it does not need the plan to tell it how to write clean code.

3. **Adaptive judgment** -- Pre-gate can return SKIP (unnecessary phase), UPDATE_PLAN (assumptions wrong), or BUILD (proceed). It makes command decisions, not just executes instructions.

4. **Fresh context** -- Each subagent starts with a clean context window. Detailed instructions from planning are not "remembered" -- they must be written to files. The file-based handoff (discovery.md, pseudocode.md) is the communication channel, and the pre-gate agent writes these files based on current reality, not stale planning assumptions.

**A detailed order to a pre-gate agent is counterproductive.** If the plan says "Create a UserService class with methods getUser(), createUser(), and deleteUser(), using the Repository pattern from src/repos/," the pre-gate agent will either:
- Discover this is correct and produce identical pseudocode (redundant detail in the plan)
- Discover the codebase already uses a different pattern and be forced to reconcile conflicting instructions (harmful detail in the plan)

A mission order says: "Enable CRUD operations for users. Must integrate with existing auth system. Prioritize consistency with existing data access patterns." The pre-gate agent then discovers what those patterns actually are and designs accordingly.

### The Auftragstaktik Principle

Auftragstaktik -- the German doctrine of mission-type tactics that dominated 20th century military thinking -- rests on two pillars:

1. **Commander's intent must be crystal clear.** The subordinate must understand not just WHAT to do but WHY, so they can adapt when circumstances change. A platoon leader who knows "prevent enemy reinforcement" can improvise when Route Alpha is blocked. One who only knows "move along Route Alpha" is paralyzed.

2. **Subordinates must have freedom to determine HOW.** Prescribing methods assumes the commander has better situational awareness than the subordinate. In military operations, the soldier on the ground sees things the general cannot. In our architecture, the pre-gate agent sees the actual codebase state -- the whiteboarding planner saw a snapshot that may already be stale.

The whiteboarding plan is the commander. The building subagents are subordinate units. The plan should specify intent, constraints, and success criteria -- not implementation procedures.

---

## 3. The Military Argument

### What Goes Wrong with Detailed Orders

Military history is littered with failures caused by over-specification:

**The Schlieffen Plan (1914):** Prescribed every division's route, timetable, and objective for a 6-week campaign. When the French did not behave as predicted (they never do), the plan had no adaptation mechanism. Subordinate commanders who deviated to exploit opportunities were recalled to maintain the schedule. Result: the plan failed precisely because it was too detailed to survive contact with reality.

**Contrast: German Blitzkrieg (1940):** Guderian's panzer divisions received mission orders -- "Cross the Meuse at Sedan, exploit success toward the Channel coast." HOW to cross, where to exploit, what routes to take -- left to division and regiment commanders. When opportunities appeared that higher HQ could not have predicted, subordinate commanders seized them without waiting for orders.

**The lesson for whiteboarding plans:** A plan that specifies "Create UserService with these exact methods in this exact file using this exact pattern" is a Schlieffen Plan. It will work only if reality matches every assumption. A plan that specifies "Enable user CRUD operations, must integrate with existing auth, prioritize consistency with data access patterns, done when all endpoints return 200 for happy-path requests" is a mission order. It gives the pre-gate agent freedom to discover the right approach.

### Commander's Intent as the Bridge

The critical insight from Auftragstaktik is that mission orders are NOT vague orders. They are precise about the things that matter (intent, constraints, success criteria) and deliberately silent about the things that don't (implementation procedures).

Commander's intent has three components:
1. **Purpose** -- WHY this phase exists in the larger plan
2. **End state** -- WHAT the system looks like when this phase succeeds
3. **Key tasks** -- the minimum set of actions that MUST happen (not all actions, just the non-negotiable ones)

This maps exactly to what the pre-gate agent needs:
- Purpose tells it why this work matters (so it can make trade-off decisions)
- End state tells it what to verify (so it can write meaningful pseudocode)
- Key tasks tell it what cannot be skipped (so it maintains alignment with the plan)

### Subordinate Initiative and the Pre-Gate Agent

The pre-gate agent already exhibits subordinate initiative. It can:
- Return SKIP if the phase is unnecessary (a subordinate commander reporting "objective already secured")
- Return UPDATE_PLAN if assumptions are wrong (a subordinate commander reporting "enemy not where expected, recommend change of plan")
- Write pseudocode that deviates from the plan's literal task list based on discovery (a subordinate commander adapting the scheme of maneuver to actual terrain)

**This initiative is a feature, not a bug.** The round 1 analysis identified that pre-gate discovery catches gaps between plan assumptions and reality. Detailed orders suppress this initiative -- if the plan says exactly what to build, the pre-gate agent becomes a rubber stamp rather than an independent assessor.

---

## 4. Concrete Recommendation: Updated Section Template

The current whiteboarding section template (Phase 3: DETAIL) is:

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

This is a detailed order. It prescribes files, functions, classes, and patterns -- information the pre-gate agent will independently discover (or discover is wrong).

**Proposed mission-order template:**

```markdown
### Phase N: [Name]

**Commander's Intent:**
- **Purpose:** [WHY this phase exists -- what it enables for the overall mission]
- **End state:** [WHAT the system looks like when this phase succeeds]
- **Key tasks:** [minimum non-negotiable actions -- not all tasks, just the critical ones]

**Constraints:**
- [Must integrate with X]
- [Must not break Y]
- [Performance requirement Z]

**Done when:**
- [ ] [Verifiable criterion 1]
- [ ] [Verifiable criterion 2]

**Assumptions to verify:**
- [ ] [Assumption the pre-gate agent should confirm before committing to pseudocode]

**Context for subordinate agents:**
- [Information the pre-gate agent cannot discover independently -- user preferences, business rules, non-obvious requirements]
```

### What Changed and Why

| Removed | Why |
|---|---|
| `Files to create/modify` | Pre-gate agent discovers actual files via codebase reconnaissance. Plan-specified files become stale. |
| `Implementation details` (functions, classes, patterns) | Pre-gate agent designs these based on discovered patterns + loaded skills. Plan-specified designs conflict with discovery. |
| `Edge cases to handle` | Post-gate agent verifies edge cases via `aposd-verifying-correctness`. Listing them in the plan is redundant with the post-gate checklist. |

| Added | Why |
|---|---|
| `Commander's Intent` (purpose + end state + key tasks) | Enables subordinate initiative. Pre-gate agent can adapt HOW while maintaining alignment with WHY. |
| `Constraints` (explicit, separate from intent) | Defines the boundaries within which subordinate agents have freedom. Military: "you may maneuver freely west of the river" -- tells the subordinate where NOT to go. |
| `Done when` (verifiable criteria) | From round 1's Proposal 6. Milestones, not task completion, define success. |
| `Assumptions to verify` | From round 1's Proposal 3. Directs pre-gate reconnaissance toward the critical unknowns. |
| `Context for subordinate agents` | Information that CANNOT be discovered via codebase search -- business rules, user preferences, stakeholder decisions. This is the "intelligence briefing" that supplements organic reconnaissance. |

| Kept (restructured) | Why |
|---|---|
| `Dependencies` becomes implicit in `blockedBy` chains | The building skill already enforces sequencing via TaskCreate. Restating it in the plan is redundant. |

### The Key Distinction: What to Specify vs. What to Leave Open

| Specify in the Plan (Commander's Domain) | Leave to Subagents (Subordinate's Domain) |
|---|---|
| WHY this phase exists | WHAT files to create/modify |
| WHAT success looks like | HOW to structure the code |
| WHAT constraints apply | WHAT patterns to use |
| WHAT assumptions need verification | WHAT edge cases exist (post-gate discovers these) |
| WHAT the user/business requires (non-discoverable) | HOW to integrate with existing code (discoverable) |

---

## 5. Research Backing

### HiPlan (2508.19076) -- Milestone-Level is the Right Abstraction

HiPlan's central finding supports mission orders directly: the optimal granularity for plan reuse and adaptation is the **milestone level** -- between full-task (too noisy, too rigid) and individual-action (too context-dependent, too brittle).

The current whiteboarding template operates at the action level ("create function X in file Y"). The proposed template operates at the milestone level ("system reaches state X, verified by criteria Y"). HiPlan demonstrates 4-23% absolute improvement in long-horizon task success when using milestone-level guidance over action-level guidance.

The dual-scale guidance principle (macro milestones + micro step-wise hints) maps precisely to the mission-order architecture: the plan provides macro milestones (commander's intent + done-when criteria), and the pre-gate agent provides micro step-wise guidance (pseudocode based on actual codebase discovery).

### Code Agent Survey (2508.00083) -- Hierarchical Navigator/Driver Pattern

The survey identifies that the most effective multi-agent code generation pattern is **hierarchical**: a Navigator proposes strategy while a Driver implements. The Navigator reviews execution feedback and guides the next iteration.

This is exactly the whiteboarding-plan / pre-gate-agent relationship. The whiteboarding plan is the Navigator (strategy). The pre-gate agent is the first Driver echelon (translates strategy to tactics). The implementation agent is the second Driver echelon (executes tactics).

The survey warns against "role-playing prompts that don't constrain behavior" -- agents drift from assigned responsibilities. Mission orders prevent this drift not through detailed instructions but through clear intent: the subordinate knows WHAT to accomplish and can self-correct when they drift.

### ExRAP (2509.08222) -- Assumptions Decay, Plans Must Account for It

ExRAP demonstrates that environmental observations become unreliable over time. In the building context, the "environment" is the codebase. Between whiteboarding (planning time) and building phase N (execution time), the codebase may have changed -- especially if earlier building phases modified shared code.

The proposed `Assumptions to verify` field directs the pre-gate agent to check critical assumptions before committing to a design. This is the military equivalent of ordering reconnaissance to confirm that the enemy is still in the expected position before launching the attack.

### HiVA (2509.00189) -- Start Simple, Evolve Complexity

HiVA's "singleton-to-complex evolution" principle argues against premature structural commitment. Over-detailed plans commit to a structure before execution feedback is available.

Mission orders enable the building system to evolve complexity through the pre-gate agent's discovery. Phase 1's pre-gate might discover that the planned approach is simpler than expected (return a simpler pseudocode) or more complex (split into sub-components). This organic adaptation is suppressed by detailed orders that prescribe the structure upfront.

### Agentic RL Survey (2509.02547) -- Credit Assignment Across Long Horizons

The survey identifies that long-horizon tasks with sparse rewards cause credit assignment failure: agents "ignore early actions that enable late success." The `Purpose` field in commander's intent addresses this directly -- it tells the pre-gate agent WHY this phase matters to the overall mission, making the connection between foundational work and eventual success explicit.

Without purpose, Phase 1 ("set up data models") looks like boring scaffolding. With purpose ("data models enable the query engine in Phase 3 -- schema decisions here determine query performance"), the pre-gate agent understands the stakes and designs accordingly.

### SC2Arena (2508.10428) -- Structured Reflection Improves Planning

The StarEvolve framework shows that extracting patterns from successes and analyzing failures improves future strategic planning. This reinforces the round 1 proposal for prior plan reference (Proposal 7) and supports the mission-order approach: if previous plans with detailed orders failed when reality diverged, that is evidence for switching to mission orders that accommodate divergence.

---

## Summary

The whiteboarding plan should be written as a **mission order**, not a detailed order. The building architecture already embeds a hierarchical command structure where subagents have organic intelligence capability (pre-gate discovery), loaded doctrinal knowledge (skills), and delegated authority (SKIP/UPDATE_PLAN/BUILD decisions). Detailed implementation instructions in the plan are either redundant with pre-gate discovery or harmful when they conflict with actual codebase state.

The proposed section template replaces file lists and implementation details with commander's intent (purpose + end state + key tasks), constraints, verifiable completion criteria, assumptions to verify, and non-discoverable context. This gives the pre-gate agent the freedom to adapt HOW while maintaining alignment with WHY -- the essence of Auftragstaktik.

The research consistently supports this approach: milestone-level abstraction outperforms action-level detail (HiPlan), hierarchical strategy/execution separation works better than flat instruction (Code Agent Survey), assumptions decay between planning and execution (ExRAP), premature structural commitment is harmful (HiVA), and purpose-linkage across phases prevents credit assignment failure (Agentic RL Survey).

**The single most important change:** Replace `Implementation details` (functions, classes, patterns) with `Commander's Intent` (purpose, end state, key tasks). Everything else follows from this shift in what the plan is trying to communicate.
