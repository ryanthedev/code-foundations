# Candidate C: Adaptive Whiteboarding Skill

**Philosophy:** Different tasks need different plan depths. Simple tasks get a flat checklist. Complex tasks get full contract structure. The skill classifies complexity FIRST, then follows the appropriate track.

---

## Complete SKILL.md Replacement

```markdown
---
name: whiteboarding
description: "Brainstorm and plan features through codebase search, technology research, and approach comparison before producing implementation-ready plans. Adapts ceremony to complexity: simple tasks get flat checklists, complex tasks get full contracts. Use when starting features, designing solutions, or planning complex work. Triggers on: whiteboard, let's plan, brainstorm, design this, figure out how to build. Save plans to docs/plans/ for execution via /code-foundations:building."
---

# Skill: whiteboarding

**Search -> Classify -> Plan -> Save -> Handoff**

---

## Quick Reference

| Step | Goal | Output |
|------|------|--------|
| DISCOVER | **Search codebase** before anything else | Pattern summary |
| CLASSIFY | Determine complexity track | Simple / Medium / Complex |
| UNDERSTAND | Adaptive questioning | Problem statement + constraints |
| EXPLORE | Research + compare approaches (Medium/Complex only) | Chosen approach |
| DETAIL | Break into phases using track-specific template | Implementation-ready plan |
| SAVE | Write to docs/plans/ | Plan file ready for /code-foundations:building |
| HANDOFF | User chooses next step | Build or manual execution |

---

## Crisis Invariants - NEVER SKIP

| Check | Why Non-Negotiable |
|-------|-------------------|
| **Search codebase BEFORE questions** | Patterns exist that user may not know about |
| **Classify complexity BEFORE detailing** | Wrong track = wrong ceremony = wasted effort or missed risks |
| **One question at a time** | Multiple questions = cognitive overload = shallow answers |
| **User confirms each section (Medium/Complex)** | Unvalidated plans diverge from user intent |
| **Save before executing** | Plan file enables context refresh + checklist tracking |
| **Plan specifies WHAT and WHY, never HOW** | Pre-gate agent discovers HOW with fresh codebase knowledge + loaded skills |

---

## Step 1: DISCOVER (Pattern Discovery)

### MANDATORY - Do First, Every Time

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

**See:** [pattern-reuse-gate.md](../../references/pattern-reuse-gate.md)

---

## Step 2: CLASSIFY (Complexity Assessment)

### Classify BEFORE Proceeding

After pattern discovery, classify the task using these signals:

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

| Track | Phases | Ceremony | Approach Comparison | Section Confirmation |
|-------|--------|----------|--------------------|--------------------|
| **Simple** | 1-2 | Flat checklist, ~30-50 words/phase | Skip | Skip |
| **Medium** | 3-5 | Standard contract, ~75-100 words/phase | 2 approaches | Per-section |
| **Complex** | 5-7 | Full contract with risk/uncertainty, ~100-150 words/phase | 2-3 approaches + pre-mortem | Per-section |

**Hard cap: 7 phases regardless of complexity.** If you need more than 7, the scope is too large -- split into multiple plans.

---

## Step 3: UNDERSTAND (Adaptive Questioning)

### Question Count by Track

| Track | Questions | Focus |
|-------|-----------|-------|
| Simple | 2-3 | Outcome + constraints + done-criteria |
| Medium | 4-5 | + users/consumers + failure modes |
| Complex | 6-8 | + system boundaries + rollback + testing strategy |

**ENFORCEMENT:** Each question MUST use `AskUserQuestion` tool. Do NOT output questions as text. No proceeding until the user answers.

### Question Sequence (Ask ONE at a time)

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

**STOP. You CANNOT proceed until ALL of the following are true:**
- [ ] Complexity classified (Simple/Medium/Complex)
- [ ] Minimum questions asked per track
- [ ] Each question asked via `AskUserQuestion` (not text output)
- [ ] Each answer received and recorded

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

## Step 4: EXPLORE (Research + Approaches)

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

### Generate Alternatives

**Approaches must be STRUCTURALLY different** (different technology, pattern, or architecture):
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
```

---

## Step 5: DETAIL (Track-Specific Plan)

### YAGNI Gate (Apply to Every Phase)

Before each phase, ask:
- Is this phase actually needed to ship?
- Could we deliver value without it?
- Are we building for hypothetical future needs?

If answer is "not needed now" -> Remove from plan.

---

### Simple Track Template (1-2 phases, ~30-50 words each)

**No section-by-section confirmation. Present the full plan at once.**

Each phase is a flat checklist. No approach comparison, no contract structure, no risk analysis.

```markdown
### Phase N: [Name]

**Goal:** [One sentence: what this phase delivers]

- [ ] [Task with file/module reference]
- [ ] [Task with file/module reference]

**Done when:**
- [ ] [Verifiable criterion]
```

**Simple track plan-level structure:**
```markdown
# Plan: [Topic]

**Created:** YYYY-MM-DD
**Status:** ready
**Complexity:** simple

---

## Context
[Problem statement from Step 3 -- 2-3 sentences]

## Constraints
- [constraint 1]
- [constraint 2]

---

## Implementation Checklist

### Phase 1: [Name]
**Model:** [recommended model]

**Goal:** [One sentence]

- [ ] [Task]
- [ ] [Task]

**Done when:**
- [ ] [Verifiable criterion]

---

### Phase 2: [Name] (if needed)
**Model:** [recommended model]

**Goal:** [One sentence]

- [ ] [Task]
- [ ] [Task]

**Done when:**
- [ ] [Verifiable criterion]

---

## Test Coverage

**Level:** [100% / Backend only / Backend + frontend / None / Per-phase]

## Test Plan

- [ ] [specific tests]

---

## Execution Log

_To be filled during /code-foundations:building_
```

---

### Medium Track Template (3-5 phases, ~75-100 words each)

**Present each section and get user confirmation before proceeding to the next.**

```markdown
### Phase N: [Name]
**Model:** [recommended model]

**Goal:** [1-2 sentences: what this phase accomplishes and why]

**Scope:**
- IN: [what this phase covers]
- OUT: [what is explicitly excluded]

**Tasks:**
- [ ] [WHAT to do, not HOW -- e.g., "Add user validation endpoint"]
- [ ] [WHAT to do -- e.g., "Write unit tests for validation logic"]

**Constraints:**
- [Non-discoverable requirement or pattern to honor]

**Depends-on:** [Phase N-1 output] | **Unlocks:** [Phase N+1]

**Done when:**
- [ ] [Observable, verifiable condition]
- [ ] [Observable, verifiable condition]
```

**Medium track plan-level structure:**
```markdown
# Plan: [Topic]

**Created:** YYYY-MM-DD
**Status:** ready
**Complexity:** medium

---

## Context
[Problem statement from Step 3]

## Constraints
- [constraint 1]
- [constraint 2]

## Chosen Approach

**[Approach name]**

[Rationale from Step 4]

**Rejected:** [Other approach] -- [why rejected in 1 sentence]

---

## Implementation Checklist

### Phase 1: [Name]
**Model:** [recommended model]

**Goal:** [1-2 sentences]

**Scope:**
- IN: [covered]
- OUT: [excluded]

**Tasks:**
- [ ] [task]
- [ ] [task]

**Constraints:**
- [constraint]

**Depends-on:** None | **Unlocks:** Phase 2

**Done when:**
- [ ] [criterion]
- [ ] [criterion]

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

---

## Notes

- [decisions made during planning]
- [gotchas discovered during research]

---

## Execution Log

_To be filled during /code-foundations:building_
```

---

### Complex Track Template (5-7 phases, ~100-150 words each)

**Present each section and get user confirmation before proceeding to the next.**

```markdown
### Phase N: [Name]
**Model:** [recommended model]
**Difficulty:** LOW / MEDIUM / HIGH
**Uncertainty:** [What we don't know that could change this phase]

**Goal:** [1-2 sentences: what this phase accomplishes and why it matters to the overall plan]

**Scope:**
- IN: [what this phase covers]
- OUT: [what is explicitly excluded and why]

**Tasks:**
- [ ] [WHAT to do -- intent level, not implementation level]
- [ ] [WHAT to do]
- [ ] [WHAT to do]

**Constraints:**
- [Hard constraint with rationale]
- [Soft constraint with priority]

**Approach notes:** [Key design decisions the pre-gate agent must respect -- NOT pseudocode]
- [decision -- e.g., "Use event-driven pattern, not polling, because of latency constraint"]
- [rejected alternative -- e.g., "Rejected: direct DB access. Reason: violates repository pattern"]

**Depends-on:** [Phase X: specific artifact or capability] | **Unlocks:** [Phase Y]

**Done when:**
- [ ] [Externally verifiable criterion -- test command, observable behavior]
- [ ] [Externally verifiable criterion]
- [ ] [At least one machine-runnable criterion]

**If blocked:** [Fallback strategy -- what to try if primary approach fails]
```

**Complex track plan-level structure:**
```markdown
# Plan: [Topic]

**Created:** YYYY-MM-DD
**Status:** ready
**Complexity:** complex

---

## Context
[Problem statement from Step 3]

## Commander's Intent
[2-3 sentences: the strategic outcome. If everything goes sideways and subagents must improvise, what is the ONE thing that must be true when this plan is done?]

## Constraints
- [constraint 1]
- [constraint 2]

## Chosen Approach

**[Approach name]**

[Rationale from Step 4]

**Rejected alternatives:**
- [Alternative A] -- [why rejected]
- [Alternative B] -- [why rejected]

**Fallback:** If the chosen approach fails fundamentally, [1-sentence fallback direction].

## Assumptions

| Assumption | Confidence | Verify Before Phase |
|-----------|------------|-------------------|
| [assumption 1] | HIGH/MED/LOW | [phase number] |
| [assumption 2] | HIGH/MED/LOW | [phase number] |

## Risk Register

| Risk | Impact | Phase | Mitigation |
|------|--------|-------|------------|
| [risk 1] | HIGH/MED/LOW | N | [mitigation] |
| [risk 2] | HIGH/MED/LOW | N | [mitigation] |

## Pre-Mortem Summary
[Key failure modes identified during approach comparison]

---

## Implementation Checklist

### Phase 1: [Name]
**Model:** [recommended model]
**Difficulty:** [LOW/MEDIUM/HIGH]
**Uncertainty:** [what could change]

**Goal:** [1-2 sentences with why]

**Scope:**
- IN: [covered]
- OUT: [excluded and why]

**Tasks:**
- [ ] [task]
- [ ] [task]

**Constraints:**
- [constraint with rationale]

**Approach notes:**
- [design decision]

**Depends-on:** None | **Unlocks:** Phase 2

**Done when:**
- [ ] [criterion]
- [ ] [criterion]

**If blocked:** [fallback]

---

### Phase 2: [Name]
**Model:** [recommended model]
**Difficulty:** [LOW/MEDIUM/HIGH]
**Uncertainty:** [what could change]
...

---

## Test Coverage

**Level:** [100% / Backend only / Backend + frontend / None / Per-phase]

## Test Plan

- [ ] Unit: [specific tests]
- [ ] Integration: [specific tests]
- [ ] Manual: [verification steps]

---

## Decision Log

| Decision | Rationale | Alternatives Considered |
|----------|-----------|------------------------|
| [decision 1] | [why] | [what else was considered] |

## Notes

- [edge cases]
- [gotchas]
- [discoveries during planning]

---

## Execution Log

_To be filled during /code-foundations:building_
```

---

## Step 6: VALIDATE

### Test Coverage Question (MANDATORY -- All Tracks)

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
   Skip tests (not recommended -- technical debt)

5. Ask at each phase
   Decide test scope when building each phase
```

**Record the answer in the plan file** under `## Test Coverage`.

### Plan Review

**Simple track:** Present full plan. Ask: "Does this plan look right? Anything to add or change?"

**Medium/Complex track:** After all sections confirmed individually, present the full plan structure:

```markdown
## Plan Summary
1. [Phase 1 name] -- [1 sentence]
2. [Phase 2 name] -- [1 sentence]
3. ...

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

If tasks <= 2 AND files <= 2 AND no OPUS_KEYWORDS:
  -> haiku (simple, mechanical work)

If tasks >= 6 OR files >= 6 OR any OPUS_KEYWORD:
  -> opus (complex, architectural work)

Otherwise:
  -> sonnet (default)
```

**Write `**Model:** [model]` into each phase heading.** This is not optional.

### Write the Plan

Use the track-specific plan-level structure from Step 5. Ensure:
- All fields from the track template are present
- Complexity field matches the classified track
- Model recommendation per phase
- Test coverage recorded
- Execution log section (empty, for building to fill)

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
1. **Clear conversation and build** (Recommended) -- Fresh context for better execution
2. **Tell me what to do** -- Get step-by-step instructions to execute manually

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

**The plan does NOT contain:**
- Pseudocode (pre-gate agent writes this after fresh discovery)
- Function signatures (pre-gate designs these with cc-routine-and-class-design)
- Error handling specifics (implementation agent applies cc-defensive-programming)
- Detailed algorithms (pre-gate translates goals into pseudocode)
- Edge case enumeration (post-gate checks these with aposd-verifying-correctness)

---

## Anti-Rationalization Table

| Rationalization | Reality |
|-----------------|---------|
| "I already know what to build" | Planning reveals unknowns you don't know you don't know |
| "This is too simple for planning" | Simple tasks get the Simple track -- 5 minutes, not 30 |
| "Let's just start coding" | Code without plan = rework later |
| "One approach is obviously right" | Simple track skips comparison. If it's not Simple, compare. |
| "User is waiting, skip questions" | Wrong solution fast < right solution slightly slower |
| "I'll figure out details during implementation" | Details in plan = checklist during execution |
| "Plan will be outdated by implementation" | Plan specifies WHAT, pre-gate discovers HOW -- WHAT doesn't go stale |
| "Multiple choice is slower" | MC gets precise answers; open questions get vague ones |
| "I'll just plan in my head" | Mental plans don't persist. File = resumable artifact. |
| "I'll batch questions to save time" | Batched questions get shallow, incomplete answers. |
| "User mentioned X, so that's decided" | User-mentioned solutions are exploratory. Still compare on Medium/Complex. |
| "I'll ask user about patterns" | **Search instead.** User may not know all patterns. |
| "No need to search, I know this tech" | Your knowledge may be outdated. Search confirms current best practices. |
| "I should add implementation details to the plan" | Pre-gate agent discovers HOW with fresh codebase knowledge + 4 loaded skills. Your plan-time design decisions will be stale or wrong. Specify WHAT and WHY. |
| "The plan needs function signatures" | Pre-gate designs these after discovery. Plan-level signatures create reconciliation conflicts when reality differs. |
| "I'll specify edge cases in the plan" | Post-gate checks these with aposd-verifying-correctness. Listing them in the plan is redundant with the gate. |
| "This Complex task only needs a Simple plan" | Under-planning costs more than slight over-planning. When uncertain, choose the higher track. |
| "Every task needs the Complex track" | Over-planning wastes time and creates brittle, over-specified plans. Classify honestly. |
| "I can infer what they want from context" | Inference != confirmation. Ask via `AskUserQuestion` or you'll plan the wrong thing. |
| "Searching takes too long" | 2 min search prevents 20 min wrong-approach rework. |
| "I'll research during implementation" | Research informs approach CHOICE. After choosing, it's too late. |

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

### Scenario 4: Complexity Classification Disagreement

**Situation:** User says "this is simple" but signals indicate Complex.

**Response:** "I see [signal 1] and [signal 2] that suggest this is more complex than it appears. The Complex track adds [specific value: risk register, pre-mortem, fallback strategies]. Want to use Medium as a compromise, or go with Simple and accept the risk of missing something?"

### Scenario 5: Plan Exceeds 7 Phases

**Situation:** During DETAIL, you identify more than 7 phases.

**Response:** "This plan has [N] phases, which exceeds the 7-phase cap. Options:
- Split into two sequential plans (recommended)
- Merge related phases to fit within 7
- Remove lower-priority phases to a follow-up plan"

---

## Chaining

- **RECEIVES FROM:** User request, feature description, user story
- **CHAINS TO:** building (via saved plan file)
- **RELATED:** oberplan, aposd-designing-deep-modules, cc-construction-prerequisites
```
