# Game Designer Analysis: How Detailed Should a Whiteboarding Plan Be?

## Persona Lens

I have shipped AAA titles. The question of how much detail goes into a quest description versus what the player discovers during gameplay is one I have answered hundreds of times, and gotten wrong enough times to know what "wrong" costs. The building architecture maps cleanly onto quest systems, and the answer to "how much detail?" is neither "more" nor "less" -- it is "the right kind, in the right place."

---

## 1. What the Building Architecture Already Handles

The building system is already a well-designed quest chain. Mapping it to game systems reveals what is already solved and what is missing.

| Building Concept | Game System Equivalent | What It Provides |
|-----------------|----------------------|------------------|
| TaskCreate with blockedBy chains | Quest prerequisites | Structural ordering. Player cannot start quest B until quest A is complete. |
| Subagent dispatch with fresh context | Player starts each quest fresh | No contamination from previous quest state. Forces the quest description to carry all necessary context. |
| PRE-GATE (discovery + pseudocode) | Exploration phase before combat | Player scouts the dungeon before fighting. Discovers what the plan assumed versus what is real. |
| IMPLEMENT | Combat / core gameplay | The player executes. Success depends on how well the quest description prepared them. |
| POST-GATE | Quest completion verification | Did the player actually kill the boss, or just clear trash mobs? Checks the real objective, not just "did you do stuff." |
| Plan file as persistent artifact | Quest journal / codex | Survives context death. Player can resume from checkpoint. |
| Model auto-detection (haiku/sonnet/opus) | Difficulty scaling | Sends a harder party to harder content. Smart resource allocation. |

**What this means:** The *execution infrastructure* is strong. The blockedBy chains enforce ordering. The gate system catches bad work. The subagent pattern provides fresh eyes. The question is not about execution -- it is about what goes INTO the quest description that the orchestrator passes to each subagent.

**The gap is at the seam.** The whiteboarding skill produces the plan. The building skill consumes it. The subagent receives a prompt containing the phase description from the plan. That prompt is the quest description. Its quality determines whether the subagent succeeds or wanders.

---

## 2. The Right Level of Detail

### The Quest Description Spectrum

In game design, quest descriptions fall on a spectrum:

| Level | Quest Description | Player Experience | Completion Rate |
|-------|------------------|-------------------|-----------------|
| **Over-specified** | "Go to coordinates (47, 82). Kill the red goblin. Pick up the key. Walk to door. Use key on door." | Player feels like a robot. No agency. Brittle to any world-state change (what if the goblin moved?). | HIGH for trivial quests. CRASHES on any deviation. |
| **Well-specified** | "Clear the goblin camp to recover the dungeon key. The camp is in the eastern valley. Watch for archers on the ridge." | Player knows WHAT to do and WHERE to go. HOW they fight is their choice. Key threats are flagged. | HIGHEST across all difficulty levels. |
| **Under-specified** | "Something is wrong in the eastern region. Investigate." | Player wanders. May solve the wrong problem. May never find the camp. Creative players love it; most players abandon. | LOW. High variance. |

The current whiteboarding Section Template sits between over-specified and well-specified, but inconsistently. It specifies files to modify (coordinates) and "implementation details" (which often become step-by-step instructions) but does not consistently specify the GOAL of the phase in terms the subagent can verify, or flag the KEY RISKS that could derail it.

### What the Subagent Actually Needs

The subagent (player) starts each quest with:
1. No memory of previous quests (fresh context)
2. The prompt from the orchestrator (quest description)
3. The discovery/pseudocode files (quest journal entries from the previous phase)
4. Access to the codebase (the game world)

Given these constraints, the quest description must contain:

| Element | Why Required | Current Status |
|---------|-------------|----------------|
| **Clear objective** (what "done" looks like) | Subagent must know when to stop | PARTIAL -- "Goal" field exists but is often vague |
| **Scope boundary** (what NOT to do) | Prevents scope creep, the #1 subagent failure | MISSING -- no explicit exclusions |
| **Key threats** (what could go wrong) | Prevents the subagent from walking into known traps | MISSING -- no risk information in phase descriptions |
| **Interface contract** (what this phase produces for the next) | Subagent must know what shape its output needs to take | MISSING -- "Dependencies" only looks backward |
| **Verification criteria** (how the POST-GATE will judge) | Subagent builds to the test, not past it | MISSING -- POST-GATE criteria are implicit |
| **Files to touch** | Grounds the phase in reality | PRESENT -- but sometimes stale by build time |
| **Implementation details** | Specific patterns, algorithms, approaches | PRESENT -- but over-specified when it becomes step-by-step |

### The Over-Specification Trap

The current template encourages listing "implementation details" as bullet points:

```
**Implementation details:**
- Create UserService class with create/read/update methods
- Use repository pattern for database access
- Add validation middleware for input checking
- Handle duplicate email error case
```

This is the equivalent of "go to coordinates (47, 82)." It works when the plan author's assumptions are correct. It fails catastrophically when reality differs, because the subagent follows the instructions instead of pursuing the goal. The pre-gate agent is supposed to catch this via discovery, but the implementation agent receives the pseudocode (derived from these details) as a contract to follow exactly. Its anti-pattern table literally says: "Not in pseudocode = not in scope."

This creates a rigidity cascade: whiteboarding over-specifies details, pre-gate converts them to pseudocode, implementation agent treats pseudocode as sacred contract, and any mismatch between plan assumptions and reality becomes a BLOCKED return rather than an adaptive solution.

### The Under-Specification Trap

The opposite failure is equally real. A phase that says:

```
**Goal:** Set up authentication
**Files to create/modify:** TBD during discovery
**Implementation details:** Use whatever auth pattern fits best
```

This gives the pre-gate agent nothing to work with. Discovery becomes open-ended exploration. Pseudocode becomes invention. The implementation agent is now designing, not implementing. The quality gates cannot verify against a spec that does not exist.

---

## 3. Game Design Argument

### Information Revelation and Player Agency

The best quest design follows a principle I call **guided freedom**: tell the player WHAT they need to accomplish and WHY it matters, flag the known dangers, then let them figure out HOW.

In Elden Ring, a quest might say: "Seek the medallion halves to operate the Grand Lift. One half is held by the commander of Castle Sol. The castle is guarded by spectral knights." This gives you:
- **Objective:** Get the medallion half
- **Location:** Castle Sol
- **Key threat:** Spectral knights
- **Context:** Why you need it (the Grand Lift)

It does NOT tell you:
- Which route through the castle to take
- Which weapons to use against spectral knights
- Whether to fight the commander head-on or use a strategy
- What order to clear the rooms in

The player discovers these things through gameplay. That discovery is the point. Over-specifying it would remove the gameplay entirely and make the player a script executor.

### Applying This to Plan Phases

Each plan phase should function like a well-designed quest:

**Tell the subagent:**
- WHAT the phase accomplishes (the objective, stated as a verifiable outcome)
- WHY this phase exists (its role in the larger plan, what depends on it)
- WHERE to look (files, modules, areas of the codebase)
- WHAT to watch out for (known risks, constraints, edge cases that the planner identified)
- WHAT "done" looks like (verification criteria the POST-GATE will use)

**Let the subagent discover:**
- HOW to implement (the pre-gate agent maps the territory; the implementation agent writes the code)
- The exact code structure (pseudocode provides the design, but the implementation agent adapts to reality)
- Integration details (discovered during pre-gate, not prescribed during planning)

### The Discovery Budget

Game designers talk about "discovery budget" -- how much of the player's time should be spent figuring things out versus executing on known tasks. Too much discovery and the player feels lost. Too little and the player feels railroaded.

For subagents, the discovery budget is the PRE-GATE phase. The whiteboarding plan should be detailed enough that PRE-GATE is verification ("yes, these files exist, yes, this pattern works"), not exploration ("what files exist? what pattern should we use?"). If PRE-GATE becomes a mini-whiteboarding session, the plan was under-specified. If PRE-GATE has nothing to discover because the plan prescribes everything, the plan was over-specified and any reality mismatch will cause a BLOCKED state.

**The sweet spot:** PRE-GATE should spend 80% of its time confirming plan assumptions and 20% adapting to surprises. If surprises dominate, the plan needs more detail. If there are zero surprises, the plan has detail that could have been left to the subagent.

---

## 4. Concrete Recommendation: Updated Section Template

Replace the current Section Template (whiteboarding SKILL.md, Phase 3):

**Current:**
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

**Proposed:**
```markdown
### Phase N: [Name] — Risk: [LOW/MEDIUM/HIGH]
**Model:** [recommended model]

**Objective:** [what "done" looks like, stated as a verifiable outcome]
  Example: "Users can authenticate via JWT. Login endpoint returns token. Protected routes reject invalid tokens."

**Why this phase exists:** [1 sentence on what depends on this phase's output]
  Example: "Phase 3 (authorization) consumes the auth middleware produced here."

**Produces:** [concrete output — the interface contract for downstream phases]
  Example: "authMiddleware function exported from src/middleware/auth.ts; POST /login endpoint; User model with password hashing"

**Scope boundary:**
- IN: [what this phase covers]
- OUT: [what this phase explicitly does NOT cover — prevents scope creep]

**Files:**
- `path/to/file.ts` - [what changes]

**Approach guidance:** [design-level direction, NOT step-by-step instructions]
  Example: "Use bcrypt for password hashing. Store JWT secret in environment config. Middleware should extract token from Authorization header."
  NOT: "Step 1: Install bcrypt. Step 2: Create hashPassword function. Step 3: ..."

**Key risks:**
- [risk 1] — Mitigation: [what the subagent should watch for]
- [risk 2] — Mitigation: [fallback approach if primary fails]

**Verification criteria:** [how POST-GATE will judge this phase]
- [ ] [criterion 1 — something the reviewer can check]
- [ ] [criterion 2]

**Depends on:** [Phase numbers] | **Parallel with:** [Phase numbers, if any]
```

### Why Each Field Exists

| Field | Game Design Principle | What It Prevents |
|-------|----------------------|-----------------|
| **Objective** (verifiable) | Quest completion criteria must be unambiguous | Subagent doing work that does not satisfy the actual goal |
| **Why this phase exists** | Quest context (why this quest matters to the story) | Subagent making locally optimal but globally wrong decisions |
| **Produces** | Quest reward item that next quest requires | Integration failures between phases (DEVS semantic drift) |
| **Scope boundary** | Quest area boundaries | Scope creep -- the #1 subagent failure mode |
| **Approach guidance** (not steps) | Difficulty hints, not walkthrough | Over-specification rigidity; subagent follows dead instructions instead of adapting |
| **Key risks** | "Watch for archers on the ridge" | Subagent walks into known traps that the planner already identified |
| **Verification criteria** | Quest completion checklist | POST-GATE inventing criteria that do not match the plan's intent |

### What This Template Removes

The `**Implementation details:**` field is gone. Replaced by `**Approach guidance:**` which is explicitly design-level, not step-level. The difference:

- **Implementation details** (old): "Create UserService class with create/read/update methods. Use repository pattern." -- This is pseudocode. It belongs in the PRE-GATE output, not the plan.
- **Approach guidance** (new): "Use repository pattern for data access. Keep service layer thin -- business logic in domain models." -- This is a design constraint that guides the pre-gate agent's pseudocode writing without prescribing the exact output.

The pre-gate agent's job is to translate approach guidance into pseudocode. The plan should not do the pre-gate agent's job for it.

---

## 5. Research Backing

### HiMAP-Travel (2603.04750) -- Coordinator Knows Global, Executors Handle Local

The whiteboarding plan is the coordinator's output. Each phase description is the allocation given to an executor. HiMAP shows that the coordinator should specify WHAT each executor must achieve and WHAT CONSTRAINTS apply, but not HOW to achieve it. When coordinators over-specify execution strategy, executors cannot adapt to local conditions, and when local conditions differ from the coordinator's assumptions, the entire plan fails.

The "Produces" and "Scope boundary" fields directly implement the coordinator-executor contract pattern. The coordinator (plan) owns global constraints and inter-phase interfaces. The executor (subagent) owns local implementation decisions.

### StructuredAgent (2603.05294) -- Separate Structure from Reasoning

The framework maintains the planning tree; the LLM handles local decisions. This is exactly the relationship between the plan file and the subagent. The plan file IS the planning tree. The subagent IS the local reasoner. Putting implementation details (local reasoning) into the plan file (planning tree) conflates these two roles. The "Approach guidance" field preserves this separation by giving design direction without local reasoning.

### DEVS (2603.03784) -- Adaptive Interface Resolution

The "Produces" field is directly inspired by DEVS's finding that integration failures come from semantic drift between what a component is planned to produce and what it actually produces. Making the interface contract explicit in the plan means the POST-GATE can verify not just "did this phase work?" but "did this phase produce what the next phase expects?"

### MA-CoNav (2603.03024) -- Reflection Depth Proportional to Risk

The "Key risks" field and the risk rating (LOW/MEDIUM/HIGH) implement the dual-level reflection finding. LOW-risk phases get quick self-checks. HIGH-risk phases get full reviews with rollback plans. This is the game design principle of scaling encounter difficulty: trash mobs get quick fights, bosses get full preparation and a save point before the encounter.

The 8.4 percentage point improvement from reflection in MA-CoNav suggests that even acknowledging "what could go wrong" before starting significantly improves outcomes. The key risks field forces the planner to do this thinking during whiteboarding, when the cost of thinking is low, rather than during building, when the cost of discovering a risk is high.

### Human-Agentic AI Teaming (2603.04746) -- Continuous Alignment via Checkpoints

The "Verification criteria" field implements checkpoint alignment. The paper's finding that alignment must be continuously maintained maps to: the plan should tell the POST-GATE what to check, so that alignment between plan intent and implementation reality is verified at every phase boundary, not just at the end.

The 10-20% overhead estimate for meaningful review aligns with the building skill's gate structure. The issue is not whether to check (the gates exist) but what to check (currently left to the POST-GATE agent to invent). Explicit verification criteria close this gap.

### GIANT (2603.04659) -- Plan Globally, Act Locally

The separation of "Objective" (global direction) from "Approach guidance" (local tactics) directly implements the plan-globally-act-locally pattern. The plan provides waypoints; the subagent navigates between them. When deviation from the planned approach exceeds what "Approach guidance" covers, the subagent should escalate (BLOCKED) rather than improvise -- just as GIANT replans when a robot deviates more than 2x from its global path.

### RAG for Robots (2603.02688) -- The Grounding Gap

The grounding gap finding (0.448 F1 loss from grounding vs 0.091 from retrieval) explains why implementation details in plans often fail: the bottleneck is not having the right plan, but mapping the plan's abstractions to codebase reality. The "Files" field with actual paths, combined with PRE-GATE discovery, addresses this. But the key insight is that the plan should provide enough grounding cues (file paths, module names, pattern references) for PRE-GATE to verify quickly, without providing so much detail that the plan becomes brittle to grounding mismatches.

---

## Summary

The right level of detail for a whiteboarding plan phase is the level of a well-designed quest description: tell the player WHAT to accomplish, WHY it matters, WHERE to look, and WHAT to watch out for. Let the player (subagent) discover HOW through the PRE-GATE exploration phase. The updated Section Template removes step-by-step implementation details (which belong in pseudocode, not in plans) and adds objective clarity, interface contracts, scope boundaries, risk flags, and verification criteria. These additions cost little planning time but provide the information subagents actually need to succeed on first attempt.
