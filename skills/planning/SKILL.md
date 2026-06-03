---
name: planning
description: "Standard/Full planning pipeline for plan command. Steps: discover, classify, explore, detail, save, check, confirm, handoff. Use when dispatched from plan command for Medium/Complex tasks. Triggers on 'planning pipeline', 'standard track', 'full track'."
user-invocable: false
---

# Skill: planning

Standard/Full planning pipeline: **Discover -> Classify -> Explore -> Decompose -> Detail -> Cross-cut -> Save -> Check -> Confirm -> Handoff**

The plan is written in stages, not one shot: DECOMPOSE fixes the phase shape and seams, DETAIL fills one phase at a time with a reset between each, CROSS-CUT derives the whole-plan sections. Each stage writes to the file in place.

The plan is a contract between plan and build. It specifies WHAT and WHY at the strategic level, with explicit interfaces between phases.

**Thinking effort:** Planning benefits from max effort. If not already at max, suggest the user increase it before proceeding.

### Load Design Vocabulary

Before any work: `Skill(code-foundations:aposd-designing-deep-modules)` — depth, interfaces, and design-it-twice vocabulary for shaping phases and their Produces seams.

### Create Progress Tasks

`TaskCreate` for each step, `TaskUpdate` with `blockedBy` to enforce ordering:

```
DISCOVER: Codebase search | DISCOVER: Questioning | CLASSIFY | EXPLORE | DECOMPOSE | DETAIL | CROSS-CUT | SAVE | CHECK | CONFIRM | HANDOFF
```

During DETAIL, add one sub-task per phase under it (one `TaskCreate` each), worked in DAG order.

**CHECK runs on all tracks** — never skip independent review.

---

## Step 1: DISCOVER

### 1a: Codebase Search (MANDATORY -- Do First)

**Before asking ANY questions**, load `Skill(code-foundations:code-standards)` to generate or update `docs/code-standards.md`. The skill handles staleness detection, codebase scanning, legacy migration, and writing.

**See also:** [pattern-reuse-gate.md](${CLAUDE_PLUGIN_ROOT}/references/pattern-reuse-gate.md)

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

A confirmed problem statement arrives from the shared steps in the plan command. DISCOVER refines it with deeper codebase context — don't redo clarification from scratch.

Review the existing problem statement against what deeper discovery found. If it holds, proceed. If discovery reveals the problem is different or broader than stated, update and re-confirm via `AskUserQuestion`: "Discovery found [X]. Updated problem statement: [Y]. Does this still capture what you want?"

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

### Recommendation + Decision Gate

After presenting the approach table, **name a recommendation with 1-sentence rationale** — not neutral presentation. The user wants an opinion, then picks.

**MUST use `AskUserQuestion`** with options:
- Each approach from the table (A, B, C...) as a selectable option
- "Elaborate on one" — expand trade-offs before choosing
- "Different direction" — none of the above fits

**Hard gate: Cannot proceed to DETAIL until the user picks an approach via `AskUserQuestion`.** Writing "Going with X" and moving on is a violation — the user must answer. No silent defaults, no "I'll flag it at confirm."

**Question style:** See [adaptive-questioning.md](${CLAUDE_PLUGIN_ROOT}/references/adaptive-questioning.md). Encode the recommendation in the option labels (e.g., "Use JWT (recommended)") so confirmatory mode works inside the structured tool.

Record chosen approach, rationale, and fallback.

---

## Step 4: DECOMPOSE

Get the *shape* right before investing in phase bodies. Write the skeleton only — no internals yet.

### The Plan Is a Contract

The plan specifies WHAT and WHY. Subagents determine HOW. Four readers: orchestrator (phase names, ordering, DW counts), pre-gate (goal, scope, constraints, approach notes, file hints), post-gate (goal, done-when), human (strategic intent, rationale).

**No implementation details in phases** -- pre-gate writes pseudocode after fresh discovery. **Plans must be pipeline-compatible** -- deterministic rules, not interactive user prompts between sub-phases.

### Define the Phases as a DAG

For each phase, write only:

- **Name** + **one-line goal**
- **Depends on / Unlocks** — the edges
- **Produces:** what this phase hands the phase(s) that consume it — the explicit seam. This is the interface the contract promises; designing it now is exactly what one-shotting skips.
- **Difficulty:** LOW / MEDIUM / HIGH

### YAGNI Gate + Phase Sizing

Before accepting each phase: Is it needed for success criteria? Could we ship without it? If "not needed now" -> remove. **Granularity test:** each phase produces a deliverable meaningful to the orchestrator and verifiable by post-gate. If it's an internal component of another phase's deliverable, fold it in.

Phase counts: Medium 3-5, Complex 5-7. Prefer fewer. Express independent phases as DAG -- don't artificially linearize.

### Write the Skeleton to the File

Create the plan file now (see Step 7 schema): header + Context + Constraints + Chosen Approach, then one header per phase carrying name, goal, Depends on / Unlocks, Produces, Difficulty. The file is built **progressively** across DECOMPOSE -> DETAIL -> CROSS-CUT -> SAVE — recoverable if interrupted. Do not commit it.

### Skeleton Checkpoint

**`AskUserQuestion`** — present the phase shape and the handoffs (Produces edges). Options:
- "Looks right" -- proceed to DETAIL
- "Adjust" -- user names what's off; revise the skeleton and re-present

Lightweight react-or-pass. Catching a wrong decomposition here is far cheaper than after the bodies are written.

---

## Step 5: DETAIL

Fill in one phase at a time. **Create a task per phase** (`TaskCreate`, ordered by the DAG) and work them in order — a deliberate stop-and-reset so each phase gets fresh attention instead of degrading across one long pass.

### Per-Phase Loop

For each phase task, in DAG order:

**1. Reframe** (the reset — write it before the body):

> Phase N: [name]. Consumes: [upstream Produces, or "nothing -- entry phase"]. Must produce: [this phase's Produces]. Difficulty: [X].

**2. Write the body** using the phase template below.

**3. Complete the task**, then move to the next phase.

### Phase Template

```markdown
### Phase N: [Name]
**Model:** [assigned at SAVE]
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
**Produces:** [what downstream consumes -- carried from skeleton]
**Security-sensitive:** [yes -- ONLY if the phase touches auth, crypto, secrets, deserialization, or untrusted input; omit otherwise. Triggers 3-sample majority-vote REVIEW during build.]
[/Medium/Complex only]

**Done when:**
- [ ] DW-N.1: [verifiable criterion]

[Medium/Complex only]
**Difficulty:** LOW / MEDIUM / HIGH  [carried from skeleton]
**Uncertainty:** [what could change, or "None"]
[/Medium/Complex only]
```

**DW-ID format:** `DW-{phase}.{item}` -- every done-when item gets a stable ID. **200-word cap per phase body.**

### Approach Notes

Only non-discoverable user decisions. **Test:** could codebase search find it? If yes, it does NOT belong.
- Good: "Use JWT not sessions -- user chose stateless for horizontal scaling"
- Bad: "Create a UserService class with getUser(), createUser()" (implementation detail)

---

## Step 6: CROSS-CUT

Derive the whole-plan sections now that every phase body exists — they fall out of the full phase set.

### Test Coverage (MANDATORY -- ask first)

`AskUserQuestion`: "How much test coverage?" Options: 100% (recommended), Backend only, Backend + frontend, None, Per-phase. Record under `## Test Coverage`. The level gates how much you derive next.

### Test Plan

Derive test items **from the done-when items** across all phases, to the chosen coverage level: Unit + Integration + Manual.

### Assumptions + Decision Log (Medium/Complex)

Fill from the choices made during EXPLORE and DETAIL:
- **Assumptions** table: assumption, confidence, verify-before-phase, fallback-if-wrong.
- **Decision Log:** decision, alternatives, rationale, phase.

### Notes

Edge cases, gotchas, and open questions surfaced while detailing.

---

## Step 7: SAVE

The file already exists from DECOMPOSE, with bodies and cross-cut sections filled. SAVE annotates each phase with model + skill, then validates the whole file against the schema.

### File Location

`.code-foundations/plans/YYYY-MM-DD-<topic-slug>.md`

### Model Detection + Skill Assignment

**Model detection per phase (MANDATORY -- every phase MUST have `**Model:**` populated):**

```
OPUS_KEYWORDS  = [refactor, architect, migrate, redesign, rewrite, overhaul,
                  new abstraction, novel pattern, system design]
HAIKU_KEYWORDS = [config, rename, typo, bump, cleanup, delete, remove,
                  backfill, data fix, sql update, doc update]

DW items <= 2 AND file hints <= 1 area AND any HAIKU_KEYWORD   -> haiku
Any OPUS_KEYWORD OR (DW items >= 6 AND file hints >= 4 areas)  -> opus
Otherwise                                                       -> sonnet
```

**Why Sonnet is the default, not omit:** Omit means inherit the user's session model -- and plan tells the user to crank to max effort, so Opus propagates to every subagent. Most code-touching phases (test, fix, validate, implement, wire, helper, hook, integration) are mechanical translation work that runs faster and cheaper on Sonnet without measurable quality loss. Reserve Opus for the keyword-flagged design-heavy phases.

**Skill assignment (EVERY phase MUST have `**Skills:**` field):**

**STOP. Before writing any `**Skills:**` field, do this:**
1. Read the system-reminder in this conversation — find every line with a skill name (format: `plugin:skill-name` or `skill-name`)
2. For each skill, read its description (shown next to its name in the system-reminder)
3. For each phase, compare the phase's goal and scope against every skill's description and trigger conditions
4. Assign skills whose triggers match the phase work. Most phases match 1-3 skills.
5. Exclude workflow commands (plan, build, debug, research, code-standards, clarify)
6. Write `**Skills:**` on every phase — `none -- [reason]` valid, omission NOT valid

**`none` is the exception, not the default.** If a phase writes code, designs an API, refactors, handles errors, touches control flow, or modifies existing untested code — there is almost certainly a matching skill. Writing `none` for a code-writing phase without checking every available skill description is a plan defect.

Skills affect gate policy: phases WITH skills get Full gate. This is intentional — skills mean the work is complex enough to warrant review.

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
(Use phase template from Step 5)
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
_To be filled during /code-foundations:build_
```

### Save (MANDATORY)

The file was created at DECOMPOSE (`mkdir -p .code-foundations/plans` already done). Ensure every phase has `**Model:**` and `**Skills:**` populated and the schema is complete. **Do NOT commit** -- the plan is a working document, not a deliverable. Building handles worktree visibility by copying the plan file after worktree creation.

---

## Step 8: CHECK

**ALL tracks:** Dispatch subagent to review saved plan with fresh eyes. Never skip — independent review catches blind spots regardless of task size.

```
Agent: sonnet, "Review plan"
Prompt: Review .code-foundations/plans/<plan>.md for structural issues.

Checklist:
- Structural: every constraint maps to a phase, done-when items cover problem statement,
  no scope overlap, union covers full feature, depends-on references exist, no orphan phases,
  every phase has a Produces (handoff), phases touching auth/crypto/secrets/deserialization/
  untrusted input are marked Security-sensitive, approach notes only non-discoverable,
  file hints present, done-when observable + has DW-ID, YAGNI
- Coherence: no contradictions, each phase's Produces matches what its dependents consume,
  user-observable output exists, high-uncertainty phases early
- Skills: every phase has Skills field (not omitted), skills match work type,
  each skill name matches an available skill in system-reminder (reject typos/nonexistent names),
  code-writing phases with `none` justify why no skill's triggers match
- Models: every phase has Model field populated (haiku/sonnet/opus -- never omitted)

Output: PASS or FINDINGS with specific fix recommendations.
```

After return: PASS -> proceed. FINDINGS -> fix issues, then proceed.

---

## Step 9: CONFIRM

**Present to user:** phases, goals, skill assignments, constraint coverage, test coverage level (chosen at CROSS-CUT), review results.

**Simple:** "Does this look right? Anything to add or change?"

**Medium/Complex:** Structured summary with phases, constraint -> phase mapping, review results, remaining questions.

**Question style:** See [adaptive-questioning.md](${CLAUDE_PLUGIN_ROOT}/references/adaptive-questioning.md). If the user has been terse during planning, present the plan with assumptions stated rather than asking open-ended "thoughts?"

### Corrections

If changes requested: update plan. Structural changes -> re-run CHECK. Minor changes -> update and re-present.

---

## Step 10: HANDOFF

`AskUserQuestion`: "Plan saved. How would you like to proceed?"

1. **Build now** (Recommended) -- Suggest default thinking effort, run `/code-foundations:build .code-foundations/plans/<plan>.md`
2. **Tell me what to do** -- Numbered manual steps

**Question style:** See [adaptive-questioning.md](${CLAUDE_PLUGIN_ROOT}/references/adaptive-questioning.md). The "Recommended" tag on Build now is the confirmatory cue — keep it there.

---

## Chain

- **Receives from:** plan command (router dispatch)
- **Chains to:** build (via saved plan file)
