---
name: whiteboarding-planning
description: "Standard/Full planning pipeline for whiteboarding. Steps: discover, classify, explore, detail, save, check, confirm, handoff. Use when dispatched from whiteboarding command for Medium/Complex tasks. Triggers on 'planning pipeline', 'standard track', 'full track'."
---

# Skill: whiteboarding-planning

Standard/Full planning pipeline: **Discover -> Classify -> Explore -> Detail -> Save -> Check -> Confirm -> Handoff**

The plan is a contract between whiteboarding and building. It specifies WHAT and WHY at the strategic level, with explicit interfaces between phases.

**Thinking effort:** Planning benefits from max effort. If not already at max, suggest the user increase it before proceeding.

### Load Design Standards

Before any work: `Read($CLAUDE_PLUGIN_ROOT/references/pre-gate-standards.md)`

### Create Progress Tasks

`TaskCreate` for each step, `TaskUpdate` with `blockedBy` to enforce ordering:

```
DISCOVER: Codebase search | DISCOVER: Questioning | CLASSIFY | EXPLORE | DETAIL | SAVE | CHECK | CONFIRM | HANDOFF
```

**CHECK runs on all tracks** — never skip independent review.

---

## Step 1: DISCOVER

### 1a: Codebase Search (MANDATORY -- Do First)

**Before asking ANY questions**, check for existing code patterns:

1. Look for `docs/code-standards.md` (or legacy `docs/code-patterns.md`)
2. **If exists:** Read it, check staleness via `git rev-list <commit-ref>..HEAD --count`
   - 0 commits since -> trust it, skip search
   - 1-20 -> spot-check recent diffs, update if changed
   - 20+ -> full re-scan, regenerate
3. **If missing:** Run full codebase search, generate `docs/code-standards.md`

**Full search:** Similar features, module patterns, related components, conventions.

**`docs/code-standards.md` sections:** Architecture, Naming, Imports, Error Handling, File Organization, Testing, Technology Decisions, Forbidden Patterns, Similar Implementations. Each: observed pattern + where used + examples. Include `<!-- base-commit: [HEAD] -->` and `<!-- generated: [date] -->` at top.

Legacy: migrate `docs/code-patterns.md` -> `docs/code-standards.md` if found. **See:** [pattern-reuse-gate.md]($CLAUDE_PLUGIN_ROOT/references/pattern-reuse-gate.md)

### 1b: Clarify Intent

**Load the clarify skill:** `Skill(code-foundations:clarify)`

Use its framework to classify what's unclear (fault type + ambiguity direction) and generate targeted questions. Do not duplicate the questioning protocol here -- the skill has it.

**Enforcement:** Each question MUST use `AskUserQuestion` tool. No proceeding until answered. Short-circuit: zero questions if already clear.

### Questioning Gate

**STOP. Cannot proceed until ALL true:**
- [ ] Codebase searched
- [ ] Complexity classified (Medium/Complex)
- [ ] Hypotheses converged (or request was already unambiguous)
- [ ] Each question asked via `AskUserQuestion`, each answer received

### Output: Problem Statement

Summarize: Problem Statement (1-2 sentences) + Constraints + Success Criteria. Confirm via `AskUserQuestion`: "Does this capture what you want?"

---

## Step 2: CLASSIFY

Classify using signals: files touched (Medium 4-8, Complex 9+), patterns (Medium 2-3 some new, Complex multiple cross-cutting), cross-cutting concerns (Medium 1-2, Complex 3+), uncertainty (Medium approach unclear, Complex requirements uncertain), phase count (Medium 3-5, Complex 5-7).

State explicitly: "This is a **[Medium/Complex]** task. [1-sentence justification]." **If uncertain, choose higher.**

| Track | Phases | Approach Comparison |
|-------|--------|---------------------|
| **Medium** | 3-5, ~100-150 words/phase | 2 approaches |
| **Complex** | 5-7, ~100-150 words/phase | 2-3 + pre-mortem |

**Hard cap: 7 phases.** More than 7 -> split into multiple plans.

---

## Step 3: EXPLORE

**Research BEFORE proposing** -- uninformed proposals waste the user's decision-making.

### Research (Medium/Complex)

**Codebase:** How similar problems are solved, existing libraries/patterns, intentionally omitted patterns (check git history).

**Web (when technology choice is involved):** Compare libraries/frameworks, check current best practices. Search for "[tech A] vs [tech B] [year]", "[domain] best practices [year]".

### Generate Alternatives

Approaches must be **structurally different** (different technology, pattern, or architecture):
- Good: "JWT tokens" vs "Session cookies" vs "OAuth2"
- Bad: "JWT with refresh" vs "JWT without refresh" (same approach)

| Approach | Trade-offs | Best When | Research Source |
|----------|-----------|-----------|-----------------|
| Option A | [pros/cons] | [conditions] | [codebase/web] |
| Option B | [pros/cons] | [conditions] | [codebase/web] |

### Pre-Mortem (Complex Only)

| Failure Mode | Probability | Impact | Which Approach Survives? |
|-------------|-------------|--------|-------------------------|
| [failure] | LOW/MED/HIGH | LOW/MED/HIGH | [approach] |

### Decision

Ask: "Which approach, or should I elaborate?" Record chosen approach, rationale, and fallback.

---

## Step 4: DETAIL

### The Plan Is a Contract

The plan specifies WHAT and WHY. Subagents determine HOW. Four readers: orchestrator (phase names, ordering, DW counts), pre-gate (goal, scope, constraints, approach notes, file hints), post-gate (goal, done-when), human (strategic intent, rationale).

**No implementation details in phases** -- pre-gate writes pseudocode after fresh discovery. **Plans must be pipeline-compatible** -- deterministic rules, not interactive user prompts between sub-phases.

### Phase Template

```markdown
### Phase N: [Name]
**Model:** [recommended model]
**Skills:** [assigned at SAVE -- skills or `none -- [reason]`]

**Goal:** [One sentence (Simple) | 1-2 sentences (Medium/Complex)]

**Scope:**
- IN: [covered]
- OUT: [excluded]

**Constraints:** [non-discoverable requirements -- omit if none]

[Medium/Complex only]
**Approach notes:** [non-discoverable user decisions -- omit if none]
**File hints:** `path/` -- [why relevant]
**Depends on:** [Phase X] | **Unlocks:** [Phase Y]
[/Medium/Complex only]

**Done when:**
- [ ] DW-N.1: [verifiable criterion]

[Medium/Complex only]
**Difficulty:** LOW / MEDIUM / HIGH
**Uncertainty:** [what could change, or "None"]
[/Medium/Complex only]
```

**DW-ID format:** `DW-{phase}.{item}` -- every done-when item gets a stable ID.

### Approach Notes

Only non-discoverable user decisions. **Test:** could codebase search find it? If yes, it does NOT belong.
- Good: "Use JWT not sessions -- user chose stateless for horizontal scaling"
- Bad: "Create a UserService class with getUser(), createUser()" (implementation detail)

### YAGNI Gate + Phase Sizing

Before each phase: Is it needed for success criteria? Could we ship without it? If "not needed now" -> remove. **Phase granularity test:** each phase produces a deliverable meaningful to the orchestrator and verifiable by post-gate. If it's an internal component of another phase's deliverable, fold it in.

Phase counts: Medium 3-5, Complex 5-7. Prefer fewer. 200-word cap per phase. Express independent phases as DAG -- don't artificially linearize.

---

## Step 5: SAVE

### File Location

`docs/plans/YYYY-MM-DD-<topic-slug>.md`

### Model Detection + Skill Assignment

**Model detection per phase:**

```
OPUS_KEYWORDS  = [refactor, architect, migrate, redesign, rewrite, overhaul]
HAIKU_KEYWORDS = [config, rename, typo, bump, cleanup, delete, remove]

DW items <= 2 AND file hints <= 2 areas AND no OPUS_KEYWORDS -> haiku
DW items >= 6 OR file hints >= 6 areas OR any OPUS_KEYWORD  -> opus
Otherwise -> omit (building uses default)
```

**Skill assignment (EVERY phase MUST have `**Skills:**` field):**
1. Scan system-reminder for all available skills (`plugin:skill-name` lines)
2. Match to phase goal, scope, and work type (tech stack, task type, domain)
3. Exclude workflow commands (whiteboarding, building, code, review, debug, prototype, setup-ast)
4. Write `**Skills:**` on every phase -- `none -- [reason]` valid, omission NOT valid

### Plan File Schema

```markdown
# Plan: [Topic]
**Created:** YYYY-MM-DD
**Status:** ready
**Complexity:** [simple/medium/complex]
---
## Context
[Problem statement from Step 1]
## Constraints
- [constraints]

[Medium/Complex only]
## Chosen Approach
**[Name]** -- [Rationale]. **Fallback:** [1 sentence]
## Rejected Approaches
- **[Name]:** [1 sentence why rejected]
[/Medium/Complex only]

---
## Implementation Phases
(Use phase template from Step 4)
---
## Test Coverage
**Level:** [100% / Backend only / Backend + frontend / None / Per-phase]
## Test Plan
- [ ] [tests] [Medium/Complex only] + Integration + Manual [/Medium/Complex only]

[Medium/Complex only]
## Assumptions
| Assumption | Confidence | Verify Before Phase | Fallback If Wrong |

## Decision Log
| Decision | Alternatives Considered | Rationale | Phase |
[/Medium/Complex only]

---
## Notes
- [edge cases, gotchas, open questions]
---
## Execution Log
_To be filled during /code-foundations:building_
```

### Save (MANDATORY)

`mkdir -p docs/plans`, write plan file. **Do NOT commit** -- the plan is a working document, not a deliverable. Building handles worktree visibility by copying the plan file after worktree creation.

---

## Step 6: CHECK

**ALL tracks:** Dispatch subagent to review saved plan with fresh eyes. Never skip — independent review catches blind spots regardless of task size.

```
Agent: sonnet, "Review whiteboarding plan"
Prompt: Review docs/plans/<plan>.md for structural issues.

Checklist:
- Structural: every constraint maps to a phase, done-when items cover problem statement,
  no scope overlap, union covers full feature, depends-on references exist, no orphan phases,
  approach notes only non-discoverable, file hints present, done-when observable + has DW-ID, YAGNI
- Coherence: no contradictions, Phase N output matches N+1 input,
  user-observable output exists, high-uncertainty phases early
- Skills: every phase has Skills field, skills match work type, skills actually available

Output: PASS or FINDINGS with specific fix recommendations.
```

After return: PASS -> proceed. FINDINGS -> fix issues, then proceed.

---

## Step 7: CONFIRM

**Present to user:** phases, goals, skill assignments, constraint coverage, review results.

**Simple:** "Does this look right? Anything to add or change?"

**Medium/Complex:** Structured summary with phases, constraint -> phase mapping, review results, remaining questions.

### Test Coverage (MANDATORY)

Ask: "How much test coverage?" Options: 100% (recommended), Backend only, Backend + frontend, None, Per-phase. Record in plan file under `## Test Coverage`.

### Corrections

If changes requested: update plan. Structural changes -> re-run CHECK. Minor changes -> update and re-present.

---

## Step 8: HANDOFF

`AskUserQuestion`: "Plan saved. How would you like to proceed?"

1. **Build now** (Recommended) -- Suggest default thinking effort, run `/code-foundations:building docs/plans/<plan>.md`
2. **Tell me what to do** -- Numbered manual steps

---

## Chain

- **Receives from:** whiteboarding command (router dispatch)
- **Chains to:** building (via saved plan file)
