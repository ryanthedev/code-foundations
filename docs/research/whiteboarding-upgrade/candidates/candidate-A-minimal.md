---
name: whiteboarding
description: "Brainstorm and plan features through codebase search and adaptive questioning, producing minimal phase-level plans for execution by /code-foundations:building. The plan is a prompt for the pre-gate agent, not a specification. Save plans to docs/plans/. Triggers on: whiteboard, let's plan, brainstorm, design this, figure out how to build."
---

# Skill: whiteboarding

**Discover intent -> Define phases -> Save -> Handoff**

---

## Quick Reference

| Phase | Goal | Output |
|-------|------|--------|
| DISCOVER | Search codebase + ask questions | Problem statement + constraints |
| SHAPE | Define phases with Goal/Scope/Constraints/Done-when | Phase list (2-7 phases) |
| CONFIRM | User approves each phase | Approved plan |
| SAVE | Write to docs/plans/ | Plan file ready for /code-foundations:building |
| HANDOFF | Clear context + start building | Execution begins |

---

## Crisis Invariants - NEVER SKIP

| Check | Why Non-Negotiable |
|-------|-------------------|
| **Search codebase BEFORE questions** | Patterns exist that user may not know about |
| **One question at a time** | Multiple questions = cognitive overload = shallow answers |
| **4 fields per phase only** | Pre-gate agent discovers everything else with fresh context + loaded skills |
| **No implementation detail in plan** | Pre-gate designs better than you can -- it has the codebase AND the skills |
| **User confirms each phase** | Unvalidated plans diverge from user intent |
| **Save before executing** | Plan file enables context refresh + subagent dispatch |

---

## Phase 1: DISCOVER

### Step 1a: Codebase Search (MANDATORY - Do First)

**Before asking ANY questions, search the codebase:**

1. Similar features/functionality (grep for keywords)
2. Same directory/module patterns (read nearby files)
3. Related components (how do similar things work?)
4. Naming conventions (what patterns exist?)

**Output a brief summary:**
```markdown
## Patterns Found
- [pattern]: [where, relevance]

## Conventions
- [naming/structure/error handling patterns observed]
```

If no patterns found: State "No existing patterns found for [topic]. This will establish a new pattern."

**See:** [pattern-reuse-gate.md](../../references/pattern-reuse-gate.md)

---

### Step 1b: Adaptive Questioning

Classify complexity from what you found:

| Signal | Complexity | Questions |
|--------|-----------|-----------|
| Single file, clear scope | Simple | 2-3 |
| Multiple files, some unknowns | Medium | 3-5 |
| Architecture changes, many unknowns | Complex | 5-7 |

State classification: "This seems [simple/medium/complex]. I have [N] questions."

**ENFORCEMENT:** Each question MUST use `AskUserQuestion` tool. Do NOT batch questions. One at a time, wait for answer.

**Core questions (ask in order, stop when you have enough):**
1. What specific outcome do you want?
2. What constraints should I know about?
3. What does "done" look like?
4. Who/what will use this?
5. What could go wrong?
6. What other systems does this touch?
7. What's the testing strategy?

Use multiple-choice format when possible.

### Questioning Gate

**STOP. You CANNOT proceed until:**
- [ ] Codebase searched
- [ ] Complexity classified
- [ ] Minimum questions asked (Simple=2, Medium=3, Complex=5)
- [ ] Each via `AskUserQuestion`, each answer received

---

### Step 1c: Problem Statement

Summarize after ALL questions answered:

```markdown
## Problem Statement
[1-2 sentences]

## Constraints
- [constraint 1]
- [constraint 2]

## Success Criteria
- [criterion 1]
- [criterion 2]
```

Confirm via `AskUserQuestion`: "Does this capture what you want?"

---

## Phase 2: SHAPE

### Approach Selection

**For simple tasks (1-2 phases, obvious approach):** State the approach in one sentence. Skip comparison.

**For medium/complex tasks:** Present 2-3 structurally different approaches.

```markdown
| Approach | Trade-off | Best when |
|----------|-----------|-----------|
| A | [pro/con] | [condition] |
| B | [pro/con] | [condition] |
```

Ask: "Which approach, or should I elaborate?"

**CRITICAL:** Approaches must be STRUCTURALLY different. "JWT with refresh" vs "JWT without refresh" is NOT different. "JWT" vs "Session cookies" vs "OAuth2" IS different.

**If user mentioned a solution:** Still present alternatives. User input is exploratory, not a decision.

---

### Phase Template

Each phase gets EXACTLY 4 fields. 50-75 words total per phase. No more.

```markdown
### Phase N: [Name]

**Goal:** [What this phase accomplishes and why -- 1-2 sentences max]

**Scope:**
- IN: [what this phase covers]
- OUT: [what is explicitly excluded]

**Constraints:** [non-discoverable requirements only -- things pre-gate cannot find by searching]

**Done-when:** [observable, verifiable conditions that prove this phase is complete]
```

**What these fields do:**
- **Goal** tells pre-gate WHAT to investigate and WHY
- **Scope IN/OUT** prevents scope creep (the #1 subagent failure)
- **Constraints** carry information pre-gate cannot discover (user intent, business rules, compatibility requirements)
- **Done-when** gives post-gate verification anchors and the orchestrator drift-detection criteria

**What is deliberately excluded from phases:**

| Excluded | Why |
|----------|-----|
| File paths | Pre-gate discovers actual files with fresh codebase state |
| Function signatures | Pre-gate designs these via cc-routine-and-class-design skill |
| Implementation details | Pre-gate writes pseudocode via cc-pseudocode-programming skill |
| Edge cases | Post-gate checks these via aposd-verifying-correctness skill |
| Error handling | Implementation agent applies cc-defensive-programming skill |
| Algorithms/patterns | Pre-gate discovers existing patterns and designs to match |

The plan is a prompt for the pre-gate agent. The pre-gate agent has four design skills, performs fresh codebase discovery, and writes implementation-ready pseudocode. It will produce a better implementation specification than this planning session can.

---

### Phase Count

- **2-7 phases.** Below 2, you are not decomposing. Above 7, you are over-planning.
- Each phase should deliver a vertically-sliced, independently testable outcome.
- If a phase cannot be expressed in 50-75 words across the 4 fields, split it.

### YAGNI Gate

Before each phase: Is this phase actually needed? Could we ship without it? Are we building for hypothetical future needs? If "not needed now" -- remove it.

---

## Phase 3: CONFIRM

### Test Coverage Question (MANDATORY)

Before finalizing, ask via `AskUserQuestion`:

```
How much test coverage?
1. 100% (Recommended) -- unit + integration
2. Backend only
3. Backend + frontend
4. None (not recommended)
5. Decide per phase
```

Record the answer.

### Phase-by-Phase Approval

Present each phase. User confirms or requests changes. Then present the full plan summary:

```markdown
# Plan: [Topic]

## Phases
1. [Phase 1 name] -- [1 sentence]
2. [Phase 2 name] -- [1 sentence]
...

## Test Coverage: [level]
```

Ask: "Plan complete? Any phases to add, remove, or modify?"

---

## Phase 4: SAVE

### File Location

```
docs/plans/YYYY-MM-DD-<topic-slug>.md
```

### Model Recommendations

When writing each phase, recommend a model:

```
OPUS_KEYWORDS  = [refactor, architect, migrate, redesign, rewrite, overhaul]
HAIKU_KEYWORDS = [config, rename, typo, bump, cleanup, delete, remove]

If tasks <= 2 AND scope is narrow AND no OPUS_KEYWORDS:
  -> haiku

If scope is broad OR any OPUS_KEYWORD:
  -> opus

Otherwise:
  -> sonnet
```

Write `**Model:** [model]` into each phase heading.

### Plan File Schema

```markdown
# Plan: [Topic]

**Created:** YYYY-MM-DD
**Status:** ready

---

## Context

[Problem statement from Phase 1]

## Constraints

- [constraint 1]
- [constraint 2]

## Chosen Approach

**[Approach name]**

[1-2 sentence rationale]

---

## Phases

### Phase 1: [Name]
**Model:** [recommended model]

**Goal:** [1-2 sentences]

**Scope:**
- IN: [covered]
- OUT: [excluded]

**Constraints:** [non-discoverable requirements]

**Done-when:** [verifiable conditions]

---

### Phase 2: [Name]
**Model:** [recommended model]

**Goal:** [1-2 sentences]

**Scope:**
- IN: [covered]
- OUT: [excluded]

**Constraints:** [non-discoverable requirements]

**Done-when:** [verifiable conditions]

---

## Test Coverage

**Level:** [100% / Backend only / Backend + frontend / None / Per-phase]

---

## Notes

- [decisions made during planning]
- [anything pre-gate agents should know that does not fit in phase constraints]

---

## Execution Log

_To be filled during /code-foundations:building_
```

---

## Phase 5: HANDOFF

After saving, ask via `AskUserQuestion`:

**"Plan saved to docs/plans/YYYY-MM-DD-<topic>.md. How would you like to proceed?"**

1. **Clear conversation and build** (Recommended) -- Fresh context for better execution
2. **Tell me what to do** -- Step-by-step manual instructions

**If option 1:** Execute `/clear`, then run `/code-foundations:building docs/plans/YYYY-MM-DD-<topic>.md`

**If option 2:** Provide numbered steps for manual implementation.

---

## Anti-Rationalization Table

| Rationalization | Reality |
|-----------------|---------|
| "I already know what to build" | Planning reveals unknowns you don't know you don't know |
| "This is too simple for planning" | Simple tasks have highest error rates |
| "Let's just start coding" | Code without plan = rework later |
| "One approach is obviously right" | If it's obvious, comparing takes 2 minutes |
| "User is waiting, skip questions" | Wrong solution fast < right solution slightly slower |
| "I'll figure out details during implementation" | That is literally the pre-gate agent's job. Let it do its job with fresh context and loaded skills. |
| "Plan will be outdated by implementation" | Plan captures INTENT and CONSTRAINTS. Those don't go stale. Implementation details do -- which is why we don't put them in the plan. |
| "I should specify file paths so pre-gate knows where to look" | Pre-gate searches the codebase with fresh state. Your file paths may already be wrong. Scope IN/OUT gives it enough to search effectively. |
| "I should add implementation details to help the subagent" | You are helping it LESS. Over-specified plans make pre-gate a transcriber instead of a designer. It has 4 design skills loaded. Let it use them. |
| "The phase needs more than 4 fields" | If it needs more, the phase is too big. Split it. |
| "75 words isn't enough for this phase" | If you can't express it in 75 words, you're specifying HOW, not WHAT. Remove the HOW. |
| "I'll batch questions to save time" | Batched questions get shallow, incomplete answers. One question = focused, complete answer. |
| "User mentioned X, so that's decided" | User-mentioned solutions are exploratory. Still compare alternatives. |
| "I'll ask user about patterns" | Search instead. User may not know all patterns. You have tools to find them. |
| "I need to add function signatures so the agent knows what to build" | The pre-gate agent designs function signatures using cc-routine-and-class-design after discovering the actual codebase. Your signatures are guesses made without that context. |
| "I should add edge cases to the plan" | Post-gate checks edge cases via aposd-verifying-correctness with a 40-item checklist. Your enumeration will be incomplete AND redundant. |
| "Multiple choice is slower" | MC gets precise answers; open questions get vague ones |
| "I'll just plan in my head" | Mental plans don't persist. File = resumable artifact. Skip file = lose all planning work on context refresh. |

---

## Pressure Testing Scenarios

### Scenario 1: User Wants to Skip Planning

"I can build without planning, but plans catch issues before code exists and enable fresh-context execution. Quick plan: 3 questions, 5 minutes?"

### Scenario 2: Vague Requirements

Ask clarifying questions ONE AT A TIME via `AskUserQuestion`. Do NOT guess or assume.

### Scenario 3: User Rejects All Approaches

"What's missing from these approaches? I'll generate alternatives that address [specific concern]."

### Scenario 4: Phase Feels Too Big

If a phase exceeds 75 words across its 4 fields, it is too big. Split into two phases with narrower scope. Each phase should be independently testable.

### Scenario 5: Temptation to Add Implementation Detail

If you catch yourself writing function names, file paths, class hierarchies, or algorithms in a phase -- STOP. Delete it. Write what the phase ACCOMPLISHES, not how. The pre-gate agent will figure out how with better information than you have right now.

---

## Chaining

- **RECEIVES FROM:** User request, feature description, user story
- **CHAINS TO:** building (via saved plan file)
- **RELATED:** oberplan, aposd-designing-deep-modules, cc-construction-prerequisites
