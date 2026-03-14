---
description: "Brainstrom and plan features"
---

# Skill: whiteboarding

**Discover -> Classify -> Plan -> Contract -> Validate -> Save -> Handoff**

The plan is a contract between whiteboarding and building. It specifies WHAT and WHY at the strategic level, with explicit interfaces between phases. Subagents determine HOW through fresh codebase discovery and loaded design skills.

---

## Quick Reference

| Step | Goal | Output |
|------|------|--------|
| DISCOVER | **Search codebase** + clarify problem | Pattern summary + problem statement |
| CLASSIFY | Determine complexity track | Simple / Medium / Complex |
| EXPLORE | **Research technologies** + compare approaches (Medium/Complex) | Chosen approach with rationale |
| DETAIL | Break into phases using track-specific template | Phase specs |
| SELF-CHECK | Verify plan completeness + coherence | Validated plan ready for user review |
| VALIDATE | User confirms + test coverage decision | Approval |
| SAVE | Write to docs/plans/ | Plan file ready for /code-foundations:building |
| HANDOFF | User chooses next step | Build or manual execution |

---

## Crisis Invariants - NEVER SKIP

| Check | Why Non-Negotiable |
|-------|-------------------|
| **Search codebase BEFORE questions** | Patterns exist that user may not know about |
| **Classify complexity BEFORE detailing** | Wrong track = wrong ceremony = wasted effort or missed risks |
| **Research BEFORE proposing approaches** | Uninformed proposals waste user's decision-making |
| **One question at a time** | Multiple questions = cognitive overload = shallow answers |
| **2-3 approaches before committing (Medium/Complex)** | First idea is rarely best; comparison reveals trade-offs |
| **File paths are HINTS, not mandates** | Pre-gate agent discovers actual files; plan paths go stale |
| **No implementation details in phases** | Pre-gate writes pseudocode after fresh discovery; plan-level design is pre-discovery guesswork |
| **Plans must be pipeline-compatible** | The building pipeline dispatches subagents autonomously. Plans must not introduce interactive user prompts between sub-phases (e.g., "Fix now or proceed?"). Use deterministic rules instead (e.g., "max 2 retry iterations") |
| **Include Approach notes for non-discoverable decisions** | User decisions (JWT not sessions, event-driven not polling) cannot be rediscovered by subagents |
| **Self-check before user validation (Medium/Complex)** | Catches structural gaps before the user reviews |
| **User confirms each section** | Unvalidated plans diverge from user intent |
| **Save before executing** | Plan file enables context refresh + checklist tracking |

---

## Step 1: DISCOVER (Pattern Discovery + Questioning)

### Step 1a: Codebase Search (MANDATORY - Do First)

**Before asking ANY questions, search the codebase:**

```
SEARCH FOR:
1. Similar features/functionality (grep for keywords)
2. Same directory/module patterns (read nearby files)
3. Related components (how do similar things work?)
4. Naming conventions (what patterns exist?)
```

| Search | Action |
|--------|--------|
| Similar features | `grep -r "keyword"` across codebase |
| Module patterns | Read 2-3 files in target directory |
| Related components | Find how similar problems were solved |
| Conventions | Note naming, structure, error handling patterns |

**Output: Pattern Summary**
```markdown
## Existing Patterns Found
- [pattern 1]: [where found, how it works]
- [pattern 2]: [where found, how it works]

## Conventions to Follow
- Naming: [observed pattern]
- Structure: [observed pattern]
- Error handling: [observed pattern]

## Similar Implementations
- [file]: [what it does, relevance]
```

**If no patterns found:** State "No existing patterns found for [topic]. This will establish a new pattern."

**See:** [pattern-reuse-gate.md](references/pattern-reuse-gate.md)

---

### Step 1b: Adaptive Questioning

After pattern discovery, classify complexity using the signal table in Step 2 (CLASSIFY). State the classification, then ask questions accordingly.

### Question Sequence (Ask ONE at a time via AskUserQuestion)

**ENFORCEMENT:** Each question below MUST use `AskUserQuestion` tool. Do NOT output questions as text -- the tool forces a stop and wait. No proceeding until the user answers.

**Simple (2-3 questions):**
1. What specific outcome do you want?
2. What constraints should I know about?
3. What does "done" look like?

**Medium (add these):**
4. Who/what will use this?
5. What could go wrong?

**Complex (add these):**
6. What other systems does this touch?
7. What's the rollback plan if it fails?
8. What's the testing strategy?

**NOTE:** Questions about "existing patterns" removed -- we searched instead of asking.

### Question Format

Use multiple-choice when possible:

```
Which authentication approach fits best?
- [ ] JWT tokens (stateless, scalable)
- [ ] Session cookies (simpler, server-state)
- [ ] OAuth2 (if external providers needed)
- [ ] Other (describe)
```

### Questioning Gate

**STOP. You CANNOT proceed to Step 2 until ALL of the following are true:**
- [ ] Codebase searched
- [ ] Complexity classified (Simple/Medium/Complex)
- [ ] Minimum questions asked: Simple=2, Medium=4, Complex=6
- [ ] Each question asked via `AskUserQuestion` (not text output)
- [ ] Each answer received and recorded

**If you catch yourself about to skip to approaches -- STOP. Count questions asked. If below minimum, ask the next one.**

### Output: Problem Statement

After ALL questions answered, summarize:

```markdown
## Problem Statement
[1-2 sentences describing what we're building]

## Constraints
- [constraint 1]
- [constraint 2]

## Success Criteria
- [criterion 1]
- [criterion 2]
```

Get user confirmation via `AskUserQuestion`: "Does this capture what you want?"

---

## Step 2: CLASSIFY (Complexity Assessment)

### Classify BEFORE Proceeding

After pattern discovery and questioning, classify the task using these signals:

| Signal | Simple | Medium | Complex |
|--------|--------|--------|---------|
| Files touched | 1-3 | 4-8 | 9+ |
| Patterns involved | 1 known pattern | 2-3 patterns, some new | Multiple new patterns, cross-cutting |
| Cross-cutting concerns | None | 1-2 (e.g., auth, logging) | 3+ (e.g., auth, caching, migration, backward compat) |
| Uncertainty | Low -- clear what to build | Medium -- approach unclear | High -- requirements or feasibility uncertain |
| Phase count | 1-2 | 3-5 | 5-7 |

**State classification explicitly:**

> "Based on pattern discovery, this is a **[Simple/Medium/Complex]** task. [1-sentence justification based on signals above]. I'll follow the [Simple/Medium/Complex] track."

**If uncertain between two tracks, choose the higher one.** Under-planning costs more than slight over-planning.

### Track Overview

| Track | Phases | Ceremony | Approach Comparison | Self-Check |
|-------|--------|----------|--------------------|----|
| **Simple** | 1-2 | Flat checklist, 50-75 words/phase | Skip (unless conflicting patterns found) | Skip |
| **Medium** | 3-5 | Contract, ~100-150 words/phase | 2 approaches | Full |
| **Complex** | 5-7 | Full contract with risk/uncertainty, ~100-150 words/phase | 2-3 approaches + pre-mortem | Full |

**Hard cap: 7 phases regardless of complexity.** If you need more than 7, the scope is too large -- split into multiple plans.

---

## Step 3: EXPLORE (Research + Approaches)

### Simple Track: SKIP This Step

For Simple tasks, the approach is usually obvious from the codebase patterns found in Step 1. Proceed directly to DETAIL.

**Exception:** If pattern discovery found conflicting patterns, do a quick 2-approach comparison even on Simple track.

### Medium Track: Compare 2 Approaches

### Complex Track: Compare 2-3 Approaches + Pre-Mortem

### Research Before Proposing (Medium/Complex Only)

#### Codebase Research
```
SEARCH FOR:
1. How similar problems are solved in this codebase
2. What libraries/patterns are already in use
3. What the codebase is NOT using (intentional omissions?)
```

| Check | Why |
|-------|-----|
| Existing dependencies | Don't propose new lib if similar exists |
| Rejected patterns | Check git history/comments for "we tried X" |
| Team conventions | Match what's already working |

#### Web Research (When technology choice is involved)

**Use WebSearch/WebFetch when:**
- Comparing libraries/frameworks
- Evaluating technology trade-offs
- Checking current best practices (your knowledge may be outdated)

```
SEARCH FOR:
1. "[technology A] vs [technology B] [current year]"
2. "[problem domain] best practices [current year]"
3. "[framework] [specific feature] implementation"
```

**Output: Research Summary**
```markdown
## Codebase Findings
- Already using: [libraries, patterns]
- Similar solutions: [where, how]

## Web Research (if applicable)
- [Technology A]: [pros, cons, current status]
- [Technology B]: [pros, cons, current status]
- Recommendation: [based on research]
```

### Generate Alternatives

**Approaches must be STRUCTURALLY different** (different technology, pattern, or architecture). Variations of the same approach do NOT count:
- Bad: "JWT with refresh tokens" vs "JWT without refresh tokens" = same approach
- Good: "JWT tokens" vs "Session cookies" vs "OAuth2" = different approaches

**Approaches must be informed by research.** Don't propose technologies you didn't research.

**If user mentioned a solution in their initial request** (e.g., "I'm thinking JWT"), this is exploratory input, NOT a decision. Still present structurally different alternatives.

| Approach | Trade-offs | Best When | Research Source |
|----------|-----------|-----------|-----------------|
| Option A | [pros/cons] | [conditions] | [codebase/web] |
| Option B | [pros/cons] | [conditions] | [codebase/web] |

### Pre-Mortem (Complex Track Only)

After presenting approaches, before the user chooses, run a pre-mortem:

```markdown
## Pre-Mortem: What Could Kill This Plan?

| Failure Mode | Probability | Impact | Which Approach Survives? |
|-------------|-------------|--------|-------------------------|
| [failure 1] | LOW/MED/HIGH | LOW/MED/HIGH | [approach] |
| [failure 2] | LOW/MED/HIGH | LOW/MED/HIGH | [approach] |
```

### Decision

Ask: "Which approach do you prefer, or should I elaborate on any?"

Record chosen approach and rationale:
```markdown
## Chosen Approach: [Name]
**Rationale:** [why this over others]
**Fallback:** [1 sentence: what to try if the chosen approach hits a wall]
```

---

## Step 4: DETAIL (Track-Specific Phase Specs)

### The Plan Is a Contract

The plan specifies WHAT and WHY. Subagents determine HOW. Each phase is a contract between the planning session and the building pipeline's independent subagents.

**The plan has four readers with different needs:**

| Reader | Needs from Plan | Ignores |
|--------|----------------|---------|
| **Building orchestrator** | Phase names, ordering, model hints, Done-when item counts | Implementation details |
| **Pre-gate agent** | Goal, scope, constraints, approach notes, file hints | Other phases' internals |
| **Post-gate agent** | Goal, done-when criteria | How it was implemented |
| **Human (user)** | Strategic intent, approach rationale, constraint coverage | Pseudocode-level detail |

---

### Simple Track Template (1-2 phases, 50-75 words each)

**No approach comparison. No self-check. Present the full plan at once.**

Each phase is a flat checklist. No contract structure, no risk analysis.

```markdown
### Phase N: [Name]
**Model:** [recommended model]

**Goal:** [One sentence: what this phase delivers]

**Scope:**
- IN: [what this phase covers]
- OUT: [what is explicitly excluded]

**Constraints:** [non-discoverable requirements -- omit if none]

**Done when:**
- [ ] [Verifiable criterion]
- [ ] [Verifiable criterion]
```

---

### Medium/Complex Track Template (~100-150 words per phase)

**Present each section and get user confirmation before proceeding to the next.**

```markdown
### Phase N: [Name]
**Model:** [recommended model]

**Goal:** [What this phase accomplishes and why -- 1-2 sentences]

**Scope:**
- IN: [what this phase covers]
- OUT: [what is explicitly excluded]

**Constraints:**
- [non-discoverable requirement the pre-gate agent must respect]

**Approach notes:** [ONLY non-discoverable user decisions -- omit if none]
- [decision + rationale]

**File hints:**
- `path/to/area/` -- [why relevant]

**Depends on:** [Phase X] | **Unlocks:** [Phase Y]

**Done when:**
- [ ] [Observable, verifiable condition]
- [ ] [Observable, verifiable condition]

**Difficulty:** LOW / MEDIUM / HIGH
**Uncertainty:** [what could change -- or "None"]
```

### What This Template Includes and Why

| Field | Purpose | Who Consumes It |
|-------|---------|----------------|
| **Goal** | Strategic anchor -- WHAT and WHY | All readers |
| **Scope (IN/OUT)** | Prevents scope creep and scope gaps | Pre-gate agent, user |
| **Constraints** | Non-discoverable requirements the codebase cannot reveal | Pre-gate agent |
| **Approach notes** | User design decisions that subagents cannot reconstruct | Pre-gate agent |
| **File hints** | Focuses pre-gate discovery without mandating specific paths | Pre-gate agent |
| **Depends on / Unlocks** | Explicit phase relationships for orchestrator | Building orchestrator |
| **Done when** | Verifiable postconditions for post-gate and VERIFY | Post-gate agent, orchestrator |
| **Difficulty** | Informs model auto-detection | Building orchestrator |
| **Uncertainty** | Directs pre-gate to investigate critical unknowns first | Pre-gate agent |

### What This Template Deliberately Excludes

| Excluded | Why | Who Handles It Instead |
|----------|-----|----------------------|
| Pseudocode | Pre-gate writes this after fresh codebase discovery | Pre-gate agent + `cc-pseudocode-programming` |
| Function signatures | Pre-gate designs these using actual codebase patterns | Pre-gate agent + `cc-routine-and-class-design` |
| Class hierarchies | Pre-gate designs these using APOSD deep-module principles | Pre-gate agent + `aposd-designing-deep-modules` |
| Error handling specifics | Implementation agent applies defensive programming | Implementation agent + `cc-defensive-programming` |
| Edge case enumeration | Post-gate checks 6-dimension correctness | Post-gate agent + `aposd-verifying-correctness` |
| Exact file paths as mandates | Pre-gate discovers actual file state; plan paths go stale | Pre-gate agent discovery phase |
| Task lists (HOW) | Pre-gate decomposes the Goal into tasks after discovery | Pre-gate agent + loaded skills |

### Approach Notes: The Non-Discoverable Exception

**Approach notes exist ONLY for decisions the user made during planning that subagents cannot rediscover from the codebase.** These are design choices, not implementation details.

Good approach notes:
- "Use JWT not sessions -- user chose stateless for horizontal scaling"
- "Event-driven architecture, not polling -- latency budget is <100ms"
- "Rejected: direct DB access from handlers. Use repository pattern per existing convention."

Bad approach notes (these belong in pseudocode, not the plan):
- "Create a UserService class with getUser(), createUser(), deleteUser() methods"
- "Use bcrypt with 12 rounds for password hashing"
- "Add try-catch around the database call on line 47"
- "Use PERT formula: E = (O + 4M + P) / 6" (the decision to use three-point estimation is non-discoverable; the formula itself is discoverable from any estimation reference)

**Test:** If the pre-gate agent could arrive at this decision by searching the codebase, it does NOT belong in approach notes. If only the user knows why this choice was made, it belongs.

### YAGNI Gate

Before each phase, ask:
- Is this phase actually needed for the stated success criteria?
- Could we ship without it?
- Are we building for hypothetical future needs?

If answer is "not needed now" -> Remove from plan.

**Phase granularity test:** Each phase should produce a deliverable that is meaningful to the building orchestrator and verifiable by the post-gate agent. If a "phase" describes an internal component of another phase's deliverable (e.g., "selection logic" inside a "review agent"), it belongs in that phase's scope, not as a separate phase. Phases are contracts for WHAT to deliver, not a task breakdown of HOW to build.

### Phase Count Guidance

| Complexity | Phase Count | Rationale |
|-----------|-------------|-----------|
| Simple | 1-2 phases | More phases than tasks = overhead exceeds value |
| Medium | 3-5 phases | Standard decomposition |
| Complex | 5-7 phases | If >7, the feature should be split into multiple plans |

**Prefer fewer phases within the range.** A 3-phase Medium plan is usually better than a 5-phase Medium plan -- fewer phases mean less pre-gate/post-gate overhead per phase and more substantial work per phase. Add phases only when scope boundaries genuinely require separate pre-gate discovery or when different model recommendations apply.

**If a phase exceeds 200 words, it is too large.** Split it into two phases.

### Dependency Structure Guidance

Use the simplest dependency chain that accurately models reality. If Phase 3 and Phase 4 can both start after Phase 2 completes (and they do not depend on each other), express this as a DAG: both depend on Phase 2, and a later phase depends on both. Do not artificially linearize independent work -- it forces sequential execution in the building pipeline when parallel execution would be safe.

---

## Step 5: SELF-CHECK (Plan Integrity Verification)

### Simple Track: SKIP This Step

Simple plans are short enough that structural issues are visible on inspection. Proceed to VALIDATE.

### Medium/Complex Track: Full Self-Check

**Before showing the plan to the user, verify it yourself.**

### Structural Completeness Check

Run through this checklist silently. Fix any failures before presenting to the user.

| Check | What to Verify | Fix If Failing |
|-------|---------------|----------------|
| **Constraint coverage** | Every constraint from Step 1 maps to at least one phase's Constraints field | Add missing constraints to relevant phases |
| **Success criteria chain** | Done-when criteria across all phases collectively satisfy the Problem Statement's success criteria | Add missing criteria or phases |
| **Scope coherence** | No phase's IN scope overlaps with another phase's IN scope | Merge overlapping phases or clarify boundaries |
| **Scope completeness** | The union of all phases' IN scopes covers the full feature | Add missing phases or expand scope |
| **Dependency chain** | Every phase's Depends-on references an existing phase | Fix references |
| **No orphan phases** | Every phase either Depends-on something or is Phase 1; every phase Unlocks something or is the final phase | Fix chains |
| **Approach notes audit** | Approach notes contain ONLY non-discoverable user decisions, not implementation details | Move implementation details out; they belong in pre-gate |
| **File hints present** | Every phase has at least one file hint to focus pre-gate discovery | Add directory-level hints |
| **Done-when verifiable** | Every done-when criterion is externally observable (test command, behavior, output) | Rewrite vague criteria |
| **YAGNI pass (global)** | No phase exists solely for hypothetical future needs | Remove or merge |

### Cross-Phase Coherence Check

| Check | What to Verify |
|-------|---------------|
| **No contradictions** | Phase N's constraints do not contradict Phase M's constraints |
| **Interface alignment** | What Phase N produces (per Done-when) matches what Phase N+1 assumes (per Depends-on) |
| **Progressive delivery** | At least one phase produces user-observable output (not just infrastructure) |
| **Risk front-loading** | Highest-uncertainty phases appear early, not late |

**If self-check reveals issues:** Fix them before proceeding to user validation. Do not present a plan you know has gaps.

---

## Step 6: VALIDATE (Confirmation Loop)

### Test Coverage Question (MANDATORY)

Before finalizing the plan, ask about test coverage:

```
How much test coverage do you want for this implementation?

1. 100% coverage (Recommended)
   Unit tests for all new code + integration tests for critical paths

2. Backend only
   Tests for server-side/API changes only

3. Backend + frontend
   Tests for both server and client layers

4. None
   Skip tests (not recommended - technical debt)

5. Ask at each phase
   Decide test scope when building each phase
```

**Record the answer in the plan file** under `## Test Coverage`.

**Inform building:** This choice affects POST-GATE behavior -- reviewers will check for tests matching the chosen coverage level.

---

### Full Plan Review

**Simple track:** Present full plan. Ask: "Does this plan look right? Anything to add or change?"

**Medium/Complex track:** After all sections confirmed individually, present the full plan structure:

```markdown
# Plan: [Topic]

## Phases
1. [Phase 1 name] -- [1 sentence goal]
2. [Phase 2 name] -- [1 sentence goal]
3. ...

## Constraint Coverage
- [constraint] -> Phase [N]
- [constraint] -> Phase [N]

## Test Plan
- [test 1]
- [test 2]

## Questions/Concerns
- [any remaining uncertainties]
```

Ask: "Does this plan look complete? Any phases to add, remove, or modify?"

---

## Step 7: SAVE (Write Plan File)

### File Location

```
docs/plans/YYYY-MM-DD-<topic-slug>.md
```

### Model Recommendations (Apply Per Phase)

When writing each phase, recommend a model based on the phase's content:

```
OPUS_KEYWORDS  = [refactor, architect, migrate, redesign, rewrite, overhaul]
HAIKU_KEYWORDS = [config, rename, typo, bump, cleanup, delete, remove]

If Done-when items <= 2 AND file hints reference <= 2 areas AND no OPUS_KEYWORDS:
  -> haiku (simple, mechanical work)

If Done-when items >= 6 OR file hints reference >= 6 areas OR any OPUS_KEYWORD:
  -> opus (complex, architectural work)

Otherwise:
  -> sonnet (default)
```

**Write `**Model:** [model]` into each phase heading.** This is not optional -- the plan should make the model choice visible so the user can adjust before building begins.

### Plan File Schema: Simple Track

```markdown
# Plan: [Topic]

**Created:** YYYY-MM-DD
**Status:** ready
**Complexity:** simple

---

## Context

[Problem statement from Step 1 -- 2-3 sentences]

## Constraints

- [constraint 1]
- [constraint 2]

---

## Implementation Phases

### Phase 1: [Name]
**Model:** [recommended model]

**Goal:** [One sentence]

**Scope:**
- IN: [covered]
- OUT: [excluded]

**Constraints:** [non-discoverable requirements -- omit if none]

**Done when:**
- [ ] [Verifiable criterion]

---

### Phase 2: [Name] (if needed)
**Model:** [recommended model]

**Goal:** [One sentence]

**Scope:**
- IN: [covered]
- OUT: [excluded]

**Constraints:** [non-discoverable requirements -- omit if none]

**Done when:**
- [ ] [Verifiable criterion]

---

## Test Coverage

**Level:** [100% / Backend only / Backend + frontend / None / Per-phase]

## Test Plan

- [ ] [specific tests]

---

## Notes

- [anything pre-gate agents should know that does not fit in phase constraints]

---

## Execution Log

_To be filled during /code-foundations:building_
```

### Plan File Schema: Medium/Complex Track

```markdown
# Plan: [Topic]

**Created:** YYYY-MM-DD
**Status:** ready
**Complexity:** [medium/complex]

---

## Context

[Problem statement from Step 1]

## Constraints

- [constraint 1]
- [constraint 2]

## Chosen Approach

**[Approach name]**

[Rationale from Step 3]

**Fallback:** [1 sentence: what to try if the chosen approach hits a wall]

## Rejected Approaches

- **[Approach B name]:** [1 sentence why rejected]
- **[Approach C name]:** [1 sentence why rejected]

---

## Implementation Phases

### Phase 1: [Name]
**Model:** [recommended model]

**Goal:** [1-2 sentences: what and why]

**Scope:**
- IN: [what this covers]
- OUT: [what is excluded]

**Constraints:**
- [constraint]

**Approach notes:**
- [non-discoverable user decision, if any]

**File hints:**
- `path/to/area/` -- [why relevant]

**Depends on:** None | **Unlocks:** Phase 2

**Done when:**
- [ ] [verifiable criterion]
- [ ] [verifiable criterion]

**Difficulty:** [LOW/MEDIUM/HIGH]
**Uncertainty:** [what we don't know, or "None"]

---

### Phase 2: [Name]
**Model:** [recommended model]
...

---

## Test Coverage

**Level:** [100% / Backend only / Backend + frontend / None / Per-phase]

## Test Plan

- [ ] Unit: [specific tests]
- [ ] Integration: [specific tests]
- [ ] Manual: [verification steps]

---

## Assumptions

| Assumption | Confidence | Verify Before Phase | Fallback If Wrong |
|-----------|-----------|--------------------|--------------------|
| [assumption] | HIGH/MED/LOW | [phase N] | [what to do instead] |

## Decision Log

| Decision | Alternatives Considered | Rationale | Phase |
|----------|------------------------|-----------|-------|
| [decision] | [alternatives] | [why this one] | [N] |

---

## Notes

- [edge cases identified during planning]
- [gotchas discovered during codebase search]
- [open questions for future consideration]

---

## Execution Log

_To be filled during /code-foundations:building_
```

### Save Command

```bash
mkdir -p docs/plans
# Write plan file
```

---

## Step 8: HANDOFF

### Ask User How to Proceed

After saving the plan, use `AskUserQuestion` with these options:

**Question:** "Plan saved to docs/plans/YYYY-MM-DD-<topic>.md. How would you like to proceed?"

**Options:**
1. **Clear conversation and build** (Recommended) - Fresh context for better execution
2. **Tell me what to do** - Get step-by-step instructions to execute manually

**If user selects option 1:**
Execute `/clear` command, then immediately run `/code-foundations:building docs/plans/YYYY-MM-DD-<topic>.md`

**If user selects option 2:**
Provide numbered steps the user can follow to implement the plan manually

---

## What the Plan Specifies vs. What Subagents Discover

The plan is a contract between whiteboarding and multiple independent subagents that start with fresh context. The pre-gate agent loads four design skills, searches the codebase, and writes implementation-ready pseudocode. The plan should give it the right problem, not prescribe the solution.

| Plan Specifies (WHAT + WHY) | Subagents Discover (HOW) |
|----------------------------|--------------------------|
| Goal per phase | Current codebase state |
| Constraints and non-goals | Specific file paths and function signatures |
| Scope boundaries (IN/OUT) | Implementation patterns and algorithms |
| Success criteria (Done when) | Pseudocode and design decisions |
| Approach rationale and rejected alternatives | Edge cases and error handling |
| Cross-phase dependencies | Integration details |
| Test coverage level | Specific test cases |
| File hints (directional, not mandates) | Actual files to create/modify |
| Difficulty + Uncertainty signals | Task decomposition within phases |

**The plan does NOT contain:**
- Pseudocode (pre-gate agent writes this after fresh discovery)
- Function signatures (pre-gate designs these with `cc-routine-and-class-design`)
- Error handling specifics (implementation agent applies `cc-defensive-programming`)
- Detailed algorithms (pre-gate translates goals into pseudocode)
- Edge case enumeration (post-gate checks these with `aposd-verifying-correctness`)
- Task lists prescribing HOW (pre-gate decomposes the Goal after discovery)

---

## Anti-Rationalization Table

| Rationalization | Reality |
|-----------------|---------|
| "I already know what to build" | Planning reveals unknowns you don't know you don't know |
| "This is too simple for planning" | Simple tasks get the Simple track -- 5 minutes, not 30 |
| "Let's just start coding" | Code without plan = rework later |
| "One approach is obviously right" | Simple track skips comparison. If it's not Simple, compare. |
| "User is waiting, skip questions" | Wrong solution fast < right solution slightly slower |
| "Plan will be outdated by implementation" | Plan specifies WHAT and WHY. Those don't go stale. Implementation details do -- which is why we don't put them in the plan. |
| "Multiple choice is slower" | MC gets precise answers; open questions get vague ones |
| "I'll just plan in my head" | Mental plans don't persist. File = resumable artifact. Skip file = lose all planning work on context refresh. |
| "I'll batch questions to save time" | Batched questions get shallow, incomplete answers. One question = focused, complete answer. |
| "User mentioned X, so that's decided" | User-mentioned solutions are exploratory. Still compare on Medium/Complex. |
| "I'll ask user about patterns" | **Search instead.** User may not know all patterns. You have tools to find them. |
| "No need to search, I know this tech" | Your knowledge may be outdated. Search confirms current best practices. |
| "Searching takes too long" | 2 min search prevents 20 min wrong-approach rework. |
| "I'll research during implementation" | Research informs approach CHOICE. After choosing, it's too late. |
| "This codebase is new to me" | That's exactly why you search. Don't guess conventions -- find them. |
| "I can infer what they want from context" | Inference is not confirmation. Ask via `AskUserQuestion` or you'll plan the wrong thing. |
| "I should add implementation details so the subagent knows what to do" | The pre-gate agent writes pseudocode after fresh codebase discovery. Your implementation details are pre-discovery guesswork that will conflict with reality. Specify WHAT and WHY, not HOW. |
| "I'll include function signatures to be helpful" | Function signatures go stale between planning and building. The pre-gate agent designs these using `cc-routine-and-class-design` with current codebase knowledge. |
| "This phase needs more detail to be safe" | Over-specified plans neuter pre-gate discovery. The agent follows stale instructions instead of adapting to reality. Trust the pipeline: pre-gate has 4 design skills loaded and fresh codebase access. |
| "I should specify edge cases in the plan" | Post-gate checks 6-dimension correctness with `aposd-verifying-correctness`. Your edge case list will be incomplete; the skill's checklist will not. |
| "File paths need to be exact" | File paths are hints for pre-gate discovery, not mandates. Use directory-level hints. Pre-gate finds the actual files. |
| "Approach notes should explain how to implement" | Approach notes capture user DECISIONS (JWT not sessions). If the pre-gate agent could arrive at the decision by searching the codebase, it does not belong in approach notes. |
| "The plan self-check is overkill" | Self-check catches constraint gaps, scope overlaps, and orphan phases. 2 minutes of checking prevents UPDATE_PLAN pauses during building. |
| "I'll skip the self-check, the user will catch issues" | Users skim plans. They catch intent errors, not structural gaps. Self-check catches structural gaps. Both are needed. |
| "I should add a task list so the agent knows what to do" | Task lists prescribe HOW. The pre-gate agent decomposes the Goal into tasks after discovering the actual codebase state. Your task list is a guess made without that context and it constrains pre-gate from finding a better decomposition. |
| "This Complex task only needs a Simple plan" | Under-planning costs more than slight over-planning. When uncertain, choose the higher track. |
| "Every task needs the Complex track" | Over-planning wastes time and creates brittle, over-specified plans. Classify honestly using the signal table. |
| "75 words is enough for this Medium phase" | Simple track is 50-75 words. Medium/Complex phases need 100-150 words to carry approach notes, file hints, difficulty, and uncertainty signals that pre-gate needs. |

---

## Pressure Testing Scenarios

### Scenario 1: User Wants to Skip Planning

**Situation:** User says "just build it" or "we don't need a plan."

**Response:** "I can build without planning, but past experience shows:
- Plans catch issues before code exists
- Plan files enable context refresh for better execution
- Checklist tracking reduces forgotten edge cases

This looks like a [Simple/Medium/Complex] task. The [track] takes about [5/15/30] minutes. Want to do a quick plan, or proceed without?"

### Scenario 2: Vague Requirements

**Situation:** User gives unclear or incomplete requirements.

**Response:** Ask clarifying questions ONE AT A TIME. Do NOT guess or assume. Each question should narrow scope until requirements are concrete.

### Scenario 3: User Rejects All Approaches

**Situation:** User doesn't like any of the 2-3 approaches presented.

**Response:** "What's missing from these approaches? I'll generate alternatives that address [specific concern]."

### Scenario 4: User Wants Implementation Details in the Plan

**Situation:** User says "be more specific" or "add more detail about how to implement this."

**Response:** "The building pipeline's pre-gate agent will write detailed pseudocode after searching the codebase. Implementation details I write now would be guesswork that could conflict with what it discovers.

What I CAN add to help:
- More specific constraints (e.g., 'must use existing middleware pattern')
- Approach notes for design decisions (e.g., 'use event-driven, not polling')
- More precise done-when criteria
- File hints pointing to relevant areas

Which of these would help?"

### Scenario 5: Self-Check Reveals Major Gap

**Situation:** During self-check, you discover a constraint from Step 1 that no phase addresses.

**Response:** Add a phase or expand an existing phase's scope to cover the constraint. Then present the fix to the user: "During plan review, I noticed [constraint] wasn't covered by any phase. I added it to Phase N. Does that look right?"

### Scenario 6: Complexity Classification Disagreement

**Situation:** User says "this is simple" but signals indicate Complex.

**Response:** "I see [signal 1] and [signal 2] that suggest this is more complex than it appears. The Complex track adds [specific value: approach notes, file hints, uncertainty signals, self-check]. Want to use Medium as a compromise, or go with Simple and accept the risk of missing something?"

### Scenario 7: Plan Exceeds 7 Phases

**Situation:** During DETAIL, you identify more than 7 phases.

**Response:** "This plan has [N] phases, which exceeds the 7-phase cap. Options:
- Split into two sequential plans (recommended)
- Merge related phases to fit within 7
- Remove lower-priority phases to a follow-up plan"

### Scenario 8: Temptation to Add Implementation Detail

**Situation:** You catch yourself writing function names, file paths, class hierarchies, or algorithms in a phase.

**Response:** STOP. Delete it. Write what the phase ACCOMPLISHES, not how. The pre-gate agent will figure out how with better information than you have right now. It has 4 design skills loaded, fresh codebase access, and writes pseudocode as its core job.

---

## Chaining

- **RECEIVES FROM:** User request, feature description, user story
- **CHAINS TO:** building (via saved plan file)
- **RELATED:** oberplan, aposd-designing-deep-modules, cc-construction-prerequisites
