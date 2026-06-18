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
  → Save confirmed requirements to .code-foundations/research/

        ↓ (when requirements are clear)

/code-foundations:plan .code-foundations/research/<file>.md
  → $ARGUMENTS: if a research-doc path is given, Read it and seed the problem statement
  → Codebase scan (shared step, all tracks)
  → Clarify intent (shared step, all tracks — gaps only if research doc provided)
  → Problem statement confirmed (shared step, all tracks)
  → [Quick: plan → check → present]
  → [Standard/Full: classify → explore → detail → save → check → confirm]
  → DECOMPOSE matches skills per phase against the available-skills register (internal + external), reading each skill's description
  → SAVE emits per-phase **Gate:** field (Full | Standard | Minimal)
  → Save to .code-foundations/plans/YYYY-MM-DD-<topic>.md
  → User confirms

        ↓ (after plan approval)

/code-foundations:build .code-foundations/plans/<plan>.md
  → Feature branch required
  → Execute phases with quality gates
  → Model assigned per phase in plan (sonnet/opus)
  → Per-phase commits after REVIEW passes (or BUILD completes for standard/minimal gate)
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
         (Full gate only — standard/minimal use tests as the gate;
          Security-sensitive phases get 3-sample majority-vote REVIEW)
COMMIT:  Orchestrator commits directly after gates pass
```

**Gate policy:** each phase in the plan carries a `**Gate:**` field (Full | Standard | Minimal).
When absent, build falls back to risk rules: security/auth/payment → Full; multi-file with new
seams → Full; docs/config-only → Minimal; else Standard. Full = BUILD + REVIEW + COMMIT.
Standard = BUILD + COMMIT. Minimal = BUILD (no discovery) + COMMIT.

Skills are **workflow-internal** (18 carry `user-invocable: false`; `planning` additionally keeps
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
