---
name: whiteboarding
description: "Discovery-oriented brainstorming to produce implementation-ready plans. Use when starting features, designing solutions, or planning complex work. Triggers on: whiteboard, let's plan, brainstorm, design this, figure out how to build. Saves plans to docs/plans/ for execution via /building command."
---

# Skill: whiteboarding

**Brainstorm → Design → Save → Handoff**

---

## Quick Reference

| Phase | Goal | Output |
|-------|------|--------|
| UNDERSTAND | Clarify the problem | Problem statement |
| EXPLORE | Compare 2-3 approaches | Chosen approach + rationale |
| DETAIL | Break into implementation steps | Checklist with files/functions |
| VALIDATE | User confirms each section | Approval |
| SAVE | Write to docs/plans/ | Plan file ready for /building |

---

## Crisis Invariants - NEVER SKIP

| Check | Why Non-Negotiable |
|-------|-------------------|
| **One question at a time** | Multiple questions = cognitive overload = shallow answers |
| **2-3 approaches before committing** | First idea is rarely best; comparison reveals trade-offs |
| **User confirms each section** | Unvalidated plans diverge from user intent |
| **Save before executing** | Plan file enables context refresh + checklist tracking |

---

## Phase 1: UNDERSTAND (Discovery-Oriented Questioning)

### Adaptive Depth Decision

First, classify complexity:

| Signal | Complexity | Question Count |
|--------|-----------|----------------|
| Single file, clear scope | Simple | 3-4 questions |
| Multiple files, some unknowns | Medium | 5-7 questions |
| Architecture changes, many unknowns | Complex | 8-12 questions |

**State classification:** "This seems [simple/medium/complex]. I'll ask [N] questions to understand it."

### Question Sequence (Ask ONE at a time)

**Simple (3-4 questions):**
1. What specific outcome do you want?
2. What constraints should I know about?
3. Any existing patterns I should follow?
4. What does "done" look like?

**Medium (add these):**
5. Who/what will use this?
6. What could go wrong?
7. Any performance considerations?

**Complex (add these):**
8. What's the current architecture?
9. What other systems does this touch?
10. What's the rollback plan if it fails?
11. Are there similar patterns elsewhere in the codebase?
12. What's the testing strategy?

### Question Format

Use multiple-choice when possible:

```
Which authentication approach fits best?
- [ ] JWT tokens (stateless, scalable)
- [ ] Session cookies (simpler, server-state)
- [ ] OAuth2 (if external providers needed)
- [ ] Other (describe)
```

**IMPORTANT:** Wait for answer before next question. No question batching.

### Output: Problem Statement

After questions, summarize:

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

Get user confirmation: "Does this capture what you want?"

---

## Phase 2: EXPLORE (2-3 Approaches)

### Mandatory: Generate Alternatives

**You MUST present 2-3 approaches before proceeding.**

**CRITICAL:** Approaches must be STRUCTURALLY different (different technology, pattern, or architecture). Variations of the same approach do NOT count:
- ❌ "JWT with refresh tokens" vs "JWT without refresh tokens" = same approach
- ✅ "JWT tokens" vs "Session cookies" vs "OAuth2" = different approaches

**If user mentioned a solution in their initial request** (e.g., "I'm thinking JWT"), this is exploratory input, NOT a decision. Still present 2-3 structurally different alternatives in this phase.

| Approach | Trade-offs | Best When |
|----------|-----------|-----------|
| Option A | [pros/cons] | [conditions] |
| Option B | [pros/cons] | [conditions] |
| Option C | [pros/cons] | [conditions] |

### Presentation Format

```markdown
## Approach A: [Name] (Recommended)
**Idea:** [1-2 sentences]
**Pros:** [list]
**Cons:** [list]
**Effort:** [relative estimate]

## Approach B: [Name]
**Idea:** [1-2 sentences]
**Pros:** [list]
**Cons:** [list]
**Effort:** [relative estimate]

## Approach C: [Name] (if applicable)
...
```

### Decision

Ask: "Which approach do you prefer, or should I elaborate on any?"

Record chosen approach and rationale:
```markdown
## Chosen Approach: [Name]
**Rationale:** [why this over others]
```

---

## Phase 3: DETAIL (Implementation-Ready Plan)

### Break into Sections (200-300 words each)

For each section:
1. Present the section
2. Wait for user confirmation
3. Proceed to next section

### Section Template

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

### YAGNI Gate

Before each section, ask:
- Is this section actually needed?
- Could we ship without it?
- Are we building for hypothetical future needs?

If answer is "not needed now" → Remove from plan.

---

## Phase 4: VALIDATE (Confirmation Loop)

### Full Plan Review

Present complete plan structure:

```markdown
# Plan: [Topic]

## Sections
1. [Section 1 name] - [1 sentence]
2. [Section 2 name] - [1 sentence]
3. ...

## Test Plan
- [test 1]
- [test 2]

## Questions/Concerns
- [any remaining uncertainties]
```

Ask: "Does this plan look complete? Any sections to add, remove, or modify?"

---

## Phase 5: SAVE (Write Plan File)

### File Location

```
docs/plans/YYYY-MM-DD-<topic-slug>.md
```

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

[Rationale from Phase 2]

---

## Implementation Checklist

### Phase 1: [Name]
- [ ] [Specific task with file path]
- [ ] [Specific task with file path]

**Files:**
- `path/to/file.ts`

**Details:**
[Implementation specifics]

---

### Phase 2: [Name]
...

---

## Test Plan

- [ ] Unit: [specific tests]
- [ ] Integration: [specific tests]
- [ ] Manual: [verification steps]

---

## Notes

- [edge cases]
- [gotchas]
- [decisions made during planning]

---

## Execution Log

_To be filled during /building_
```

### Save Command

```bash
mkdir -p docs/plans
# Write plan file
```

---

## Phase 6: HANDOFF

### Context Refresh Recommendation

After saving, offer:

```
Plan saved to: docs/plans/YYYY-MM-DD-<topic>.md

**Recommended next steps:**
1. **Refresh context** - Start new session, run `/building docs/plans/YYYY-MM-DD-<topic>.md`
   - Best for complex plans (fresh context = better execution)

2. **Continue now** - Run `/building` in this session
   - OK for simple plans

Which do you prefer?
```

---

## Anti-Rationalization Table

| Rationalization | Reality |
|-----------------|---------|
| "I already know what to build" | Planning reveals unknowns you don't know you don't know |
| "This is too simple for planning" | Simple tasks have highest error rates |
| "Let's just start coding" | Code without plan = rework later |
| "One approach is obviously right" | If it's obvious, comparing takes 2 minutes |
| "User is waiting, skip questions" | Wrong solution fast < right solution slightly slower |
| "I'll figure out details during implementation" | Details in plan = checklist during execution |
| "Plan will be outdated by implementation" | Plan file tracks changes; no plan = no tracking |
| "Multiple choice is slower" | MC gets precise answers; open questions get vague ones |
| "I'll just plan in my head" | Mental plans don't persist. File = resumable artifact. Skip file = lose all planning work on context refresh. |
| "I'll batch questions to save time" | Batched questions get shallow, incomplete answers. One question = focused, complete answer. |
| "User mentioned X, so that's decided" | User-mentioned solutions are exploratory. Still compare 2-3 structurally different approaches. |

---

## Pressure Testing Scenarios

### Scenario 1: User Wants to Skip Planning

**Situation:** User says "just build it" or "we don't need a plan."

**Response:** "I can build without planning, but past experience shows:
- Plans catch issues before code exists
- Plan files enable context refresh for better execution
- Checklist tracking reduces forgotten edge cases

How about a quick plan (3-4 questions, 5 minutes)? Or should I proceed without?"

### Scenario 2: Vague Requirements

**Situation:** User gives unclear or incomplete requirements.

**Response:** Ask clarifying questions ONE AT A TIME. Do NOT guess or assume. Each question should narrow scope until requirements are concrete.

### Scenario 3: User Rejects All Approaches

**Situation:** User doesn't like any of the 2-3 approaches presented.

**Response:** "What's missing from these approaches? I'll generate alternatives that address [specific concern]."

---

## Chaining

- **RECEIVES FROM:** User request, feature description, user story
- **CHAINS TO:** building (via saved plan file)
- **RELATED:** oberplan, aposd-designing-deep-modules, cc-construction-prerequisites
