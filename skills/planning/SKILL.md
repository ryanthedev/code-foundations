---
name: planning
description: "Implements the Standard/Full planning pipeline for Medium and Complex tasks: multi-step discovery, phase decomposition with skill matching, cross-cutting concerns, and plan emission with Gate fields."
user-invocable: false
disable-model-invocation: true
---

# Skill: planning

Standard/Full planning pipeline: **Discover -> Classify -> Explore -> Decompose -> Detail -> Cross-cut -> Save -> Check -> Confirm -> Handoff**

The plan is written in stages, not one shot: DECOMPOSE fixes the phase shape and seams, DETAIL fills one phase at a time with a reset between each, CROSS-CUT derives the whole-plan sections. Each stage writes to the file in place.

The plan is a contract between plan and build. It specifies WHAT and WHY at the strategic level, with explicit interfaces between phases.

**Thinking effort:** Planning benefits from max effort. If not already at max, suggest the user increase it before proceeding.

### Create Progress Tasks

`TaskCreate` one task per pipeline step (the ten named in the header line above), `TaskUpdate` with `blockedBy` to enforce ordering:

```
DISCOVER | CLASSIFY | EXPLORE | DECOMPOSE | DETAIL | CROSS-CUT | SAVE | CHECK | CONFIRM | HANDOFF
```

During DETAIL, add one sub-task per phase under it (one `TaskCreate` each), worked in DAG order.

**CHECK runs on all tracks** — never skip independent review.

---

## Step 1: DISCOVER

DISCOVER runs **after** the plan command's shared steps (code-standards scan, clarify, confirmed problem statement). Do NOT re-run them. This step is the *delta*: deepen codebase research, and re-confirm the problem statement only if discovery contradicts it.

### 1a: Deepen Codebase Research

The code-standards scan already ran in the plan command's shared step 1 — `docs/code-standards.md` exists. Do **not** reload the code-standards skill. Deepen the research instead: how similar problems are solved here, existing libraries/patterns to reuse, and patterns intentionally omitted (check git history).

**See also:** [pattern-reuse-gate.md](${CLAUDE_PLUGIN_ROOT}/references/pattern-reuse-gate.md)

### 1b: Re-confirm Problem Statement (only on contradiction)

A confirmed problem statement already arrives from the plan command's shared step — clarification ran there, under its 5-round cap. Do **not** reload the clarify skill or re-clarify from scratch. Only if deeper research contradicts or materially broadens the stated problem do you re-confirm (see Output below).

### Questioning Gate

**STOP. Cannot proceed until ALL true:**
- [ ] Codebase research deepened (pattern reuse + prior art checked)
- [ ] Track received from dispatch (Medium/Complex)
- [ ] Problem statement holds, or was re-confirmed after a discovery contradiction

### Output: Problem Statement

A confirmed problem statement arrives from the shared steps in the plan command. DISCOVER refines it with deeper codebase context — don't redo clarification from scratch.

Review the existing problem statement against what deeper discovery found. If it holds, proceed. If discovery reveals the problem is different or broader than stated, update and re-confirm via `AskUserQuestion`: "Discovery found [X]. Updated problem statement: [Y]. Does this still capture what you want?"

---

## Step 2: CLASSIFY

Classify using signals: files touched (Medium 4-8, Complex 9+), patterns (Medium 2-3 some new, Complex multiple cross-cutting), cross-cutting concerns (Medium 1-2, Complex 3+), uncertainty (Medium approach unclear, Complex requirements uncertain), phase count (Medium 3-5, Complex 5-7).

State explicitly: "This is a **[Medium/Complex]** task. [1-sentence justification]." **If uncertain between Medium and Complex, choose higher** (this tie-breaker refines Medium-vs-Complex only; the plan command's "Default to Quick" already routed the task here).

**Demotion path — discovery reveals the task is actually Simple:** if the signals now read Simple (one focused change, 1-2 phases, no approach comparison needed), stop the pipeline and hand back to the Quick track in `commands/plan.md`. Do not force a 3-phase plan onto a one-thing change. Say so explicitly: "Discovery shows this is a Simple task — switching to the Quick track."

| Track | Phases | Approach Comparison |
|-------|--------|---------------------|
| **Medium** | 3-5, ~100-150 words/phase | 2 approaches |
| **Complex** | 5-7, ~100-150 words/phase | 2-3 + pre-mortem |

**Hard cap: 7 phases.** More than 7 -> split into multiple plans.

---

## Step 3: EXPLORE

**Research BEFORE proposing** -- uninformed proposals waste the user's decision-making.

### Load Design Vocabulary

`Skill(code-foundations:ca-architecture-boundaries)` — system-level vocabulary (boundaries, dependency direction, SRP-by-actor) for generating structurally different approaches here and shaping phase seams at DECOMPOSE. Module-level design skills (e.g. aposd-designing-deep-modules) are NOT loaded here — they get matched per phase at DECOMPOSE and loaded during DETAIL.

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

Print the approach table in conversation, then **name a recommendation with 1-sentence rationale** — not neutral presentation. The user wants an opinion, then picks.

**MUST use `AskUserQuestion`** with options:
- Each approach from the table (A, B, C...) as a selectable option — **`preview` REQUIRED on each**: that approach's trade-offs, best-when, and research source as markdown. The preview pane is the guaranteed-visible surface; the user compares approaches side-by-side there even if the table print was skipped.
- "Different direction" — none of the above fits

**Hard gate: Cannot proceed to DETAIL until the user picks an approach via `AskUserQuestion`.** Writing "Going with X" and moving on is a violation — the user must answer. No silent defaults, no "I'll flag it at confirm."

**Question style:** See [adaptive-questioning.md](${CLAUDE_PLUGIN_ROOT}/references/adaptive-questioning.md). Encode the recommendation in the option labels (e.g., "Use JWT (recommended)") so confirmatory mode works inside the structured tool.

Record chosen approach, rationale, and fallback.

---

## Step 4: DECOMPOSE

Get the *shape* right before investing in phase bodies. Write the skeleton only — no internals yet.

### The Plan Is a Contract

The plan specifies WHAT and WHY. Subagents determine HOW. Four readers: orchestrator (phase names, ordering, DW counts), build-agent (goal, scope, constraints, approach notes, file hints), post-gate-agent (goal, done-when), human (strategic intent, rationale).

**No implementation details in phases** -- the build-agent writes pseudocode after fresh discovery. Cross-phase seams are the one exception: the Produces contract pins the interface; internals stay the build agent's latitude. **Plans must be pipeline-compatible** -- deterministic rules, not interactive user prompts between sub-phases.

### Define the Phases as a DAG

For each phase, write only:

- **Name** + **one-line goal**
- **Depends on / Unlocks** — the edges
- **Produces:** what this phase hands the phase(s) that consume it — the explicit seam. This is the interface the contract promises; designing it now is exactly what one-shotting skips.
- **Skills:** matched now so DETAIL can load them (see below)
- **Difficulty:** LOW / MEDIUM / HIGH

### Match Skills per Phase

Skills are matched HERE so DETAIL can load them while writing phase bodies — a phase body written without domain knowledge is the planner guessing.

1. Match against your **available-skills register** — every skill whose description is in context. That includes the 19 internal code-foundations skills (`user-invocable: false`: model-discoverable, hidden from the slash menu) AND skills from other installed plugins (e.g. skill-craft, mcp-builder, security-guidance). Each description carries its own when-to-match and sibling-disambiguation (the "not for X (use Y)" clauses) — match on the descriptions directly.
2. For each phase, compare the phase's goal against every candidate skill's when-to-match conditions (register descriptions for external skills; catalog entries plus their disambiguation notes for the internal sibling pairs)
3. Assign skills whose triggers match the phase work. Most phases match 1-3 skills.
4. Exclude workflow commands (plan, build, debug, research, code-standards, clarify)
5. Write `**Skills:**` on every skeleton header — `none -- [reason]` valid, omission NOT valid

**`none` is the exception, not the default.** If a phase writes code, designs an API, refactors, handles errors, touches control flow, or modifies existing untested code — there is almost certainly a matching skill. DETAIL may add skills it discovers while writing bodies; SAVE validates the final set.

### YAGNI Gate + Phase Sizing

Before accepting each phase: Is it needed for success criteria? Could we ship without it? If "not needed now" -> remove. **Granularity test:** each phase produces a deliverable meaningful to the orchestrator and verifiable by the post-gate-agent. If it's an internal component of another phase's deliverable, fold it in.

Phase counts: Medium 3-5, Complex 5-7. Prefer fewer. Express independent phases as DAG -- don't artificially linearize.

### Skeleton Checkpoint

Catching a wrong decomposition here is far cheaper than after the bodies are written. The user can only review what the dialog itself shows them — Write tool results render collapsed, and conversation prose is routinely skipped under tool-chaining. **The skeleton travels INSIDE the `AskUserQuestion` call, in the `preview` field.** Do NOT write the plan file first; the file is written after approval.

`AskUserQuestion` — "Does the N-phase decomposition look right? Review the skeleton in the preview." Options — **the `preview` field on BOTH options is REQUIRED and carries the identical full skeleton**:

- "Looks right" — description: "Write the skeleton to the plan file and proceed to detailing each phase." — `preview`: the skeleton
- "Adjust" — description: "Name what's off — phase boundaries, ordering, scope, or missing work." — `preview`: the skeleton

An option without the skeleton preview asks the user to confirm something they cannot see — the question is invalid without it. On "Adjust": revise, re-ask with the updated skeleton in the previews.

Preview content shape (markdown):

```markdown
## Skeleton: N phases
1. **[Name]** — [one-line goal] (LOW/MED/HIGH)
   produces: [seam] → Phase 2
2. ...
DAG: 1 → 2 → {3, 4} → 5
```

Printing the skeleton in conversation before the call is good practice too — but the preview is the mandatory channel, not the print.

### Write the Skeleton to the File

After "Looks right": create the plan file (see Step 7 schema): header + Context + Constraints + Chosen Approach, then one header per phase carrying name, goal, Depends on / Unlocks, Produces, Skills, Difficulty. The file is built **progressively** across DECOMPOSE -> DETAIL -> CROSS-CUT -> SAVE — recoverable if interrupted. Do not commit it.

---

## Step 5: DETAIL

Fill in one phase at a time. **Create a task per phase** (`TaskCreate`, ordered by the DAG) and work them in order — a deliberate stop-and-reset so each phase gets fresh attention instead of degrading across one long pass.

### Per-Phase Loop

For each phase task, in DAG order:

**1. Reframe** (the reset — write it before the body):

> Phase N: [name]. Consumes: [upstream Produces, or "nothing -- entry phase"]. Must produce: [this phase's Produces]. Difficulty: [X].

**2. Load the phase's skills** (matched at DECOMPOSE). For each skill not already loaded this conversation, invoke it with the Skill tool — `Skill(code-foundations:<name>)` for this plugin's own skills, `Skill(<plugin>:<name>)` for external ones; each self-loads its own checklists. Skills load once — later phases reuse them. Apply them while writing Constraints, Edge cases, and Done-when. If the work reveals a skill the skeleton missed, add it to the field.

**3. Write the body** using the phase template below.

**4. Complete the task**, then move to the next phase.

### Phase Template

```markdown
### Phase N: [Name]
**Model:** [assigned at SAVE]
**Skills:** [matched at DECOMPOSE, loaded during DETAIL -- skills or `none -- [reason]`]
**Gate:** [Full | Standard | Minimal -- assigned at SAVE]

**Goal:** [One sentence (Simple) | 1-2 sentences (Medium/Complex)]

**Scope:**
- IN: [covered]
- OUT: [excluded]

**Constraints:** [non-discoverable requirements -- omit if none]
**Edge cases:** [boundaries + error paths this phase must handle -- skill-informed; omit if none]

[Medium/Complex only]
**Approach notes:** [non-discoverable user decisions -- omit if none]
**File hints:** `path/` -- [why relevant]
**Depends on:** [Phase X] | **Unlocks:** [Phase Y]
**Produces:** [what downstream consumes -- carried from skeleton. If the seam is code, state the contract: signature / type / route / schema -- not prose]
**Security-sensitive:** [yes -- ONLY if the phase touches auth, crypto, secrets, deserialization, or untrusted input; omit otherwise. Triggers 3-sample majority-vote REVIEW during build.]
**Rollback:** [REQUIRED if the phase performs destructive or irreversible actions (data deletion, prod deploy, migration): the compensating action, or "point of no return -- [mitigation]"; omit otherwise]
[/Medium/Complex only]

**Done when:**
- [ ] DW-N.1: [verifiable criterion]

[Medium/Complex only]
**Difficulty:** LOW / MEDIUM / HIGH  [carried from skeleton]
**Uncertainty:** [what could change, or "None"]
[/Medium/Complex only]
```

**DW-ID format:** `DW-{phase}.{item}` -- every done-when item gets a stable ID. **250-word cap per phase body.**

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

Load `Skill(code-foundations:cc-quality-practices)` (skip if already loaded; it self-loads its checklists). Apply its Test Case Generation to derive test items, to the chosen coverage level:

- **Per-DW:** one test item per done-when item across all phases (Unit + Integration + Manual)
- **Boundary:** below / at / above each boundary named in the phases' Edge cases
- **Dirty:** error paths, bad data, wrong size -- aim toward the 5:1 dirty:clean ratio; every code-touching phase contributes at least one dirty test

### Assumptions + Decision Log (Medium/Complex)

Fill from the choices made during EXPLORE and DETAIL:
- **Assumptions** table: assumption, confidence, verify-before-phase, fallback-if-wrong.
- **Decision Log:** decision, alternatives, rationale, phase.

### Notes

Gotchas and open questions surfaced while detailing. Per-phase edge cases live in the phase bodies, not here.

---

## Step 7: SAVE

The file already exists from DECOMPOSE, with bodies and cross-cut sections filled. SAVE annotates each phase with a model, validates the skill assignments made upstream, then validates the whole file against the schema.

### File Location

`.code-foundations/plans/YYYY-MM-DD-<topic-slug>.md`

### Model Detection + Gate Assignment + Skill Validation

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

**Gate assignment per phase (MANDATORY -- every phase MUST have `**Gate:**` populated):**

Build consumes the `**Gate:**` field verbatim — `Full`, `Standard`, or `Minimal` (see `commands/build.md` resolution order, rule 2). The planner sets it here with the risk context in hand. Mirror build.md's risk rules:

| Risk signal in the phase | Gate |
|---|---|
| Security / auth / payment work (matches `**Security-sensitive:**`) | Full |
| Multi-file change introducing new cross-phase seams | Full |
| Docs-only or config-only change | Minimal |
| (none of the above) | Standard |

Skill presence does NOT decide the gate — every phase carries skills, so skills cannot discriminate gate level. Gate is keyed off the risk of the work itself, exactly as build resolves it.

**Skill validation (EVERY phase MUST have `**Skills:**` field):**

Skills were matched at DECOMPOSE and refined during DETAIL. Validate the final set:

1. Every phase has `**Skills:**` populated — `none -- [reason]` valid, omission NOT valid
2. Every skill name matches a real available skill present in your available-skills register — internal (code-foundations) or external (another plugin) (reject typos/nonexistent names)
3. No workflow commands (plan, build, debug, research, code-standards, clarify)
4. Code-writing phases with `none` justify why no skill's triggers match — on any gap, re-run the DECOMPOSE matching procedure for that phase

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

The file was created at DECOMPOSE (`mkdir -p .code-foundations/plans` already done). Ensure every phase has `**Model:**`, `**Gate:**`, and `**Skills:**` populated and the schema is complete. **Do NOT commit** -- the plan is a working document, not a deliverable. Building handles worktree visibility by copying the plan file after worktree creation.

---

## Step 8: CHECK

**ALL tracks:** Dispatch subagent to review saved plan with fresh eyes. Never skip — independent review catches blind spots regardless of task size.

```
Agent: sonnet, "Review plan"
Prompt: Review .code-foundations/plans/<plan>.md for structural issues.

Checklist:
- Structural: every constraint maps to a phase, done-when items cover problem statement,
  no scope overlap, union covers full feature, depends-on references exist, no orphan phases,
  every phase has a Produces (handoff) -- code seams stated as contracts (signature/type/
  route/schema, not prose), phases with destructive/irreversible actions carry Rollback,
  phases touching auth/crypto/secrets/deserialization/untrusted input are marked
  Security-sensitive, approach notes only non-discoverable, file hints present,
  done-when observable + has DW-ID, YAGNI
- Coherence: no contradictions, each phase's Produces matches what its dependents consume,
  user-observable output exists, high-uncertainty phases early
- Tests: test plan covers every DW item; boundary + dirty tests derived from phase Edge cases
- Skills: every phase has Skills field (not omitted), skills match work type,
  each skill name matches a real available skill in the available-skills register — internal or external (reject typos/nonexistent names),
  code-writing phases with `none` justify why no skill's triggers match
- Gates: every phase has a Gate field populated (Full/Standard/Minimal), matching its risk
  (Full for security/auth/payment or new cross-phase seams; Minimal for docs/config-only; Standard otherwise)
- Models: every phase has Model field populated (haiku/sonnet/opus -- never omitted)

Output: PASS or FINDINGS with specific fix recommendations.
```

After return: PASS -> proceed. FINDINGS -> fix; **structural fixes (phase boundaries, DW set, Produces seams, Gate/Model/Skills assignments) -> re-run CHECK**; minor fixes -> proceed (mirrors CONFIRM's rule).

---

## Step 9: CONFIRM

**Present to user:** phases, goals, skill assignments, constraint coverage, test coverage level (chosen at CROSS-CUT), review results. Print this summary as markdown in conversation, then `AskUserQuestion` with options carrying it — **`preview` REQUIRED on both** (the identical summary), so the user can review the plan inside the dialog even if the print was skipped. The user won't open the saved file, and Write/Edit tool results render collapsed.

Summary content: phases with goals, constraint -> phase mapping, review results, remaining questions.

Question: "Does this look right? Anything to add or change?" Options:
- "Approve" — `preview`: the plan summary
- "Request changes" — `preview`: the plan summary

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
