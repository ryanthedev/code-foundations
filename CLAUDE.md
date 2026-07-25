# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Code-foundations is a Claude Code plugin providing software engineering skills based on *Code Complete* (McConnell) and *A Philosophy of Software Design* (Ousterhout). It includes a build workflow with gated phases (BUILD, REVIEW, orchestrator commit) and an experimental code review system.

## Architecture

### Skill Families

| Family | Prefix | Focus |
|--------|--------|-------|
| Code Complete | `cc-*` | Process rigor, metrics, checklists |
| APOSD | `aposd-*` | Design philosophy, complexity reduction |
| GoF Design Patterns | `gof-*` | 23 Gang of Four patterns, decision trees, structural recipes |
| Clean Architecture | `ca-*` | System-level boundaries, SRP-by-actor, dependency direction |
| Legacy Code | `welc-*` | Safely modifying untested code (conditional, invoked from cc-refactoring-guidance) |

### Directory Structure

- `skills/` - Individual skill definitions (SKILL.md; checklists.md where build's checklist-resolution step consumes it)
- `commands/` - User-invocable commands (slash commands)
- `agents/` - Agent templates (build-agent, post-gate-agent)
- `references/` - Shared reference materials (cc-foundations.md, dispatch-templates.md, etc.)
- `docs/` - `code-standards.md` (this repo's own authoring standards, consumed by the code-standards skill)

### Development Workflows

**Choose based on scope:**

| Situation | Command | Ceremony |
|-----------|---------|----------|
| Bug investigation | `/code-foundations:debug` | Minimal |
| Vague idea or unclear requirements | `/code-foundations:research` | Minimal |
| Feature needs planning | `/code-foundations:plan` | Medium |
| Executing approved plan | `/code-foundations:build` | Full |

### Research → Whiteboard → Building Workflow

Three-stage pattern for feature development:

| Command | Purpose | Output |
|---------|---------|--------|
| `/code-foundations:research` | Clarify what the user wants through facilitated conversation | Research doc in `.code-foundations/research/` |
| `/code-foundations:plan` | Plan implementation with phases, models, and skills | Plan file in `.code-foundations/plans/` |
| `/code-foundations:build` | Checklist-based execution | Working code + tests |

**Full Flow:**
```
/code-foundations:research "I want to build a notification system"
  → Facilitated conversation to clarify intent
  → Progressive narrowing: purpose, actors, context, boundaries, needs, risks
  → Save to .code-foundations/research/ with Status: draft
  → Optional verification: grill (adversarial Q&A) + cold-read subagent
    (fresh context, no intent-framing) → Status: confirmed

        ↓ (when requirements are clear)

/code-foundations:plan .code-foundations/research/<file>.md
  → $ARGUMENTS: if a research-doc path is given, Read it and seed the problem statement
  → Codebase scan (shared step, all tracks)
  → Clarify intent (shared step, all tracks — gaps only if research doc provided)
  → Problem statement confirmed (shared step, all tracks)
  → [Quick: plan → check → present]
  → [Standard/Full: classify → explore → detail → save → check → confirm]
  → DECOMPOSE matches skills per phase against the available-skills register (internal + external), reading each skill's description
  → SAVE emits per-phase **Model:** (fable | sonnet | haiku), **Gate:** (Full | Standard | Minimal),
    **Depends on:**, and optional **File scope:** (wave-parallelism opt-in), plus the plan-header
    **Review cadence:** (default 3)
  → Save to .code-foundations/plans/YYYY-MM-DD-<topic>.md with **Status:** draft
  → Plan presented as end-turn conversation markdown; user confirms free-form → Status: ready

        ↓ (after plan approval)

/code-foundations:build .code-foundations/plans/<plan>.md
  → Feature branch required; refuses plans whose Status isn't ready
  → Waves derived from Depends on + File scope: independent Standard/Minimal phases
    build in parallel (own phase worktrees), integrated by cherry-pick in plan order
  → Model per phase from plan (fable judgment-heavy / sonnet default / haiku mechanical;
    opus only as explicit override); REVIEW one tier below BUILD (floored at sonnet — never haiku), security REVIEW on fable
  → Per-phase commits: after REVIEW passes (Full, security-sensitive) or on a green suite
    (Standard, Minimal — review deferred to a batch every `Review cadence` phases)
  → Final verification + report
```

**When to use each:**

| Situation | Command |
|-----------|---------|
| "I have an idea but it's vague" / unclear requirements | `/code-foundations:research` |
| Ready to plan full feature | `/code-foundations:plan` |
| Plan exists, ready to implement | `/code-foundations:build` |

**Quality Gates (per phase during /code-foundations:build):**
```
BUILD:   baseline discipline (DW→test traceability, stub → implement → validate, anchoring, scope clamp)
         Skills listed in the phase are invoked via the Skill tool in the BUILD agent's
         dispatch prompt (Skill(code-foundations:<name>) / Skill(<plugin>:<name>)); each
         skill self-loads its own checklists.
         (discovery + design → implementation: stub → implement → validate, in one agent)
REVIEW:  debiased review protocol (execute-first, per-DW evidence + trace, anti-overcorrection)
         Blocking for Full gates and security-sensitive phases (3-sample majority vote);
         deferred into a batch REVIEW for Standard and Minimal, which fires every N phases
         (Review cadence, default 3), before any Full phase, and once before VERIFY
COMMIT:  Orchestrator commits directly — after REVIEW passes for blocking phases,
         on a green suite for deferred ones
```

**Gate policy:** each phase in the plan carries a `**Gate:**` field (Full | Standard | Minimal) —
required, like `**Model:**` and `**Depends on:**`; build stops and asks for a re-plan when any is
missing (there are no legacy plans). The gate decides review **timing**, not whether a review
happens — every phase is reviewed. Full = BUILD + blocking REVIEW + COMMIT (the commit waits for
PASS; always runs alone, never in a wave). Standard = BUILD + COMMIT, review deferred to the next
batch. Minimal = BUILD (no discovery) + COMMIT, same deferral. `**Security-sensitive:** yes`
forces an immediate 3-sample REVIEW at any gate — never deferred.

**Review cadence:** the plan header carries `**Review cadence:** N` (default 3, clamped to 1–5).
Standard and Minimal phases commit on a green suite and join an un-reviewed set; a batch REVIEW
covers the whole set at once when N accumulate, before any Full phase opens, and once before
VERIFY. Batch REVIEW runs against committed code, so a FAIL is fixed forward (a `fix(phase-N)`
commit answering the findings, then a re-run over the whole set) rather than gating a commit —
see `references/gate-failure-protocol.md` → Batch Failures. Reviewing several phases together is
also what buys the cross-phase coherence check that isolated per-phase reviews can't produce.
Commits record `Review: deferred (batch pending)`, paired with a `Covered by batch review`
addendum in the execution log; a deferred trailer with no addendum is a build defect the trust
report must catch.

**Checkpoint doctrine:** content the user must review (plan summaries, skeletons, approach
comparisons, problem statements) is presented as the turn's final conversation markdown and
answered free-form — dialog previews truncate multi-phase content. `AskUserQuestion` is reserved
for decisive 2-4-option picks (clarify, coverage level, handoff). The draft→ready Status flip is
the structural guard: unconfirmed plans can't build.

**Effort doctrine:** plan at high effort (the reasoning lives there); build at low effort for
all-serial plans, default when any phase carries `File scope` (wave-eligible). Subagent depth is
separate: BUILD/REVIEW agents are steered by dispatch wording (the Agent tool has no effort knob) —
derived from each phase's `Model`, REVIEW never below "think carefully"; build's Effort Alignment
stops to ask when a phase's `Model` (effort) and `Gate` (rigor) disagree.

Skills are **workflow-internal** (all 19 carry `user-invocable: false`; `planning` additionally keeps
`disable-model-invocation: true` so the model can't run the planning pipeline ad-hoc). They are
hidden from the user's slash menu but ARE in the model's skill register — model-discoverable and
invocable. Plan/build discover them (alongside external plugin skills) via the register — each
skill's description carries its own when-to-match and sibling-disambiguation (the "not for X (use
Y)" clauses), so matching is done on the descriptions directly. Build (and the
planner's DETAIL step) load each assigned skill via the Skill tool — `Skill(code-foundations:<name>)`
for this plugin's own, `Skill(<plugin>:<name>)` for any other plugin's — and each skill self-loads
its checklists. A subagent doesn't inherit the register, but an explicit `Skill(...)` line in its
dispatch prompt invokes the skill regardless.

The REVIEW dispatch is deliberately stripped of intent-framing (no plan context, no progress
narrative, no discovery file) — the reviewer is an independent critic.

Models are assigned per phase at plan's SAVE step. Cannot proceed to next phase until current
phase passes all gates including REVIEW PASS (Full gate).

## Skill File Structure

```
skills/<skill-name>/
├── SKILL.md         # Main skill definition with YAML frontmatter (required)
└── checklists.md    # Checklists loaded by build's checklist-resolution step (where present)
```

Some skills have a `references/` subdirectory (e.g. `gof-design-patterns/references/` for the
23 pattern files; `code-standards/references/` for section-templates.md). Every bundled file
must be linked from SKILL.md or it is a dead orphan. The `hard-data.md` and `language-notes.md`
patterns are not standard — they were removed during the 2026-06 audit (orphan files with
proven drift).

## Key Concepts

**APOSD Complexity Symptoms:**
- Change amplification (simple change → many modifications)
- Cognitive load (must know too much)
- Unknown unknowns (worst)

**CC Metrics:**
- Cohesion (routine does ONE thing)
- Coupling (minimized dependencies)
- Parameters ≤7, Inheritance depth < 3

**CC Skills (7 total):** cc-control-flow-quality, cc-debugging, cc-defensive-programming,
cc-pseudocode-programming, cc-quality-practices, cc-refactoring-guidance, cc-routine-and-class-design.
All 7 CC skills reference `references/cc-foundations.md` for shared vocabulary (cohesion spectrum,
coupling criteria, key metrics, routine-length thresholds).

- `cc-debugging` — scientific debugging: STABILIZE → LOCATE → HYPOTHESIZE → EXPERIMENT → FIX → TEST → SEARCH

## Publishing

### Plugin Structure

- `.claude-plugin/plugin.json` - Plugin manifest with name, version, description
- Version follows semver (e.g., 4.1.0)

### Marketplace

Published to `ryanthedev/rtd-claude-inn` marketplace. Marketplace tracks `ref: main`, so publishing is just pushing to origin.

**To publish:**
1. Bump version in `.claude-plugin/plugin.json`
2. Commit and push to `origin/main`

**Install commands:**
```bash
/plugin marketplace add ryanthedev/rtd-claude-inn
/plugin install code-foundations@rtd
/plugin update code-foundations@rtd
```
