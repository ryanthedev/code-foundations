# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Code-foundations is a Claude Code plugin providing software engineering skills based on *Code Complete* (McConnell) and *A Philosophy of Software Design* (Ousterhout). It includes a building workflow with gated phases (BUILD, REVIEW, orchestrator commit) and an experimental code review system.

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

- `skills/` - Individual skill definitions (SKILL.md + checklists.md)
- `commands/` - User-invocable commands (slash commands)
- `agents/` - Agent templates (build-agent, post-gate-agent)
- `references/` - Shared reference materials
- `docs/` - Case study examples

### Development Workflows

**Choose based on scope:**

| Situation | Command | Ceremony |
|-----------|---------|----------|
| Bug investigation | `/code-foundations:debug` | Minimal |
| Vague idea or unclear requirements | `/code-foundations:research` | Minimal |
| Feature needs planning | `/code-foundations:whiteboard` | Medium |
| Executing approved plan | `/code-foundations:building` | Full |

### Research → Whiteboard → Building Workflow

Three-stage pattern for feature development:

| Command | Purpose | Output |
|---------|---------|--------|
| `/code-foundations:research` | Clarify what the user wants through facilitated conversation | Research doc in `.claude/code-foundations/research/` |
| `/code-foundations:whiteboard` | Plan implementation with phases, models, and skills | Plan file in `.claude/code-foundations/plans/` |
| `/code-foundations:building` | Checklist-based execution | Working code + tests |

**Full Flow:**
```
/code-foundations:research "I want to build a notification system"
  → Facilitated conversation to clarify intent
  → Progressive narrowing: purpose, actors, context, boundaries, needs, risks
  → Save confirmed requirements to .claude/code-foundations/research/

        ↓ (when requirements are clear)

/code-foundations:whiteboard .claude/code-foundations/research/<file>.md
  → Codebase scan (shared step, all tracks)
  → Clarify intent (shared step, all tracks)
  → Problem statement confirmed (shared step, all tracks)
  → [Quick: plan → check → present]
  → [Standard/Full: classify → explore → detail → save → check → confirm]
  → Save to .claude/code-foundations/plans/YYYY-MM-DD-<topic>.md
  → User confirms

        ↓ (after plan approval)

/code-foundations:building .claude/code-foundations/plans/<plan>.md
  → Feature branch required
  → Execute phases with quality gates
  → Model auto-detected per phase (haiku/sonnet/opus)
  → Per-phase commits after REVIEW passes (or BUILD completes for standard/minimal gate)
  → Final verification + report
```

**When to use each:**

| Situation | Command |
|-----------|---------|
| "I have an idea but it's vague" / unclear requirements | `/code-foundations:research` |
| Ready to plan full feature | `/code-foundations:whiteboard` |
| Plan exists, ready to implement | `/code-foundations:building` |

**Quality Gates (per phase during /code-foundations:building):**
```
BUILD:   references/pre-gate-standards.md + references/implement-standards.md + [plan Skills]
         (discovery + design → TDD implementation in one agent)
REVIEW:  references/post-gate-standards.md + [plan Skills]
         (Full gate only — standard/minimal use tests as gate)
VERIFY:  performance-optimization + cc-refactoring-guidance + build + tests + lint
COMMIT:  Orchestrator commits directly after gates pass
```

`[plan Skills]` = skills assigned per phase during whiteboard's SAVE step, then validated/resolved during building's SETUP skill resolution task.

Model and skills are assigned during whiteboard's SAVE step. Building's SETUP runs a one-time skill resolution task that validates assignments, fills gaps, and updates the plan before creating phase tasks (skills affect gate policy). Cannot proceed to next phase until current phase passes all gates including REVIEW PASS (Full gate).

## Skill File Structure

```
skills/<skill-name>/
├── SKILL.md         # Main skill definition with YAML frontmatter
├── checklists.md    # Detailed checklists
├── hard-data.md     # Research/data backing the skill
└── language-notes.md # Language-specific guidance (optional)
```

## Key Concepts

**APOSD Complexity Symptoms:**
- Change amplification (simple change → many modifications)
- Cognitive load (must know too much)
- Unknown unknowns (worst)

**CC Metrics:**
- Cohesion (routine does ONE thing)
- Coupling (minimized dependencies)
- Parameters ≤7, Inheritance depth < 3

**CC Skills (13 total):**
All CC skills reference `references/cc-foundations.md` for shared vocabulary (cohesion spectrum, coupling criteria, key metrics).

Additional skills:
- `cc-debugging` - Scientific debugging (Chapter 23): STABILIZE → LOCATE → HYPOTHESIZE → EXPERIMENT → FIX → TEST → SEARCH

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
