# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Code-foundations is a Claude Code plugin providing software engineering skills based on *Code Complete* (McConnell) and *A Philosophy of Software Design* (Ousterhout). It includes a profile-driven code review system that dispatches one agent per checklist.

## Architecture

### Two Skill Families

| Family | Prefix | Focus |
|--------|--------|-------|
| Code Complete | `cc-*` | Process rigor, metrics, checklists |
| APOSD | `aposd-*` | Design philosophy, complexity reduction |

### Directory Structure

- `skills/` - Individual skill definitions (SKILL.md + checklists.md)
- `commands/` - User-invocable commands (slash commands)
- `agents/` - Agent templates, profiles, and configuration
  - `agents/profiles/` - Built-in profiles (sanity.yaml, pr.yaml)
  - `agents/config.yaml` - Agent settings
- `references/` - Shared reference materials
- `docs/` - Case study examples

### Code Review System

**Single entry point:** `/code-foundations:review`

**Profile-driven architecture:** One unified flow, configurable via profiles.

```
┌────────────┐   ┌──────────┐   ┌─────────────┐   ┌───────────────┐   ┌────────┐
│ EXTRACTION │ → │ CHECKING │ → │ ORCHESTRATE │ → │ INVESTIGATION │ → │ REPORT │
│  (haiku)   │   │ (haiku)  │   │   (haiku)   │   │    (haiku)    │   │(haiku) │
└────────────┘   └──────────┘   └─────────────┘   └───────────────┘   └────────┘
```

| Preset | Checklists | Checks | Use Case |
|--------|------------|--------|----------|
| `--sanity` | 1 | 99 | Pre-commit sanity |
| `--pr` | 10 | 614 | Full PR review |
| `--profile <name>` | varies | varies | Custom configuration |

**Interactive mode:** `/code-foundations:review` (no flags) asks for profile.
**Profile management:** `/code-foundations:review-profile --setup`

### Profile Structure

Profiles define which checklists to run and which skills inform each:

```yaml
# agents/profiles/pr.yaml or .code-foundations/profiles/custom.yaml
name: my-profile
description: "Description"

# Parallelism (optional - default: unlimited)
max_parallelism: 5      # Max concurrent agents per phase (0 = unlimited)

# Model configuration (optional - all default to haiku)
models:
  checking: haiku       # Checklist execution
  investigation: haiku  # Finding verification
  report: haiku         # JSON compilation

# Custom dashboard (optional - generates project-specific HTML)
dashboard:
  enabled: true         # Set true for custom dashboard
  model: sonnet         # Needs creativity

checklists:
  # Skill checklist with its persona
  - path: skills/cc-defensive-programming/checklists.md
    skills: [cc-defensive-programming]

  # Custom checklist with skill persona
  - path: .code-foundations/checklists/owasp.md
    skills: [cc-defensive-programming]

  # Self-contained checklist
  - path: agents/quick-checklist.md
    skills: []
```

**Each checklist = 1 checking agent** during review.

### Built-in Profiles

| Profile | Location | Checklists | Checks |
|---------|----------|------------|--------|
| sanity | `agents/profiles/sanity.yaml` | 1 | 99 |
| pr | `agents/profiles/pr.yaml` | 10 | 614 |

### Skill Checklist Counts

| Skill | Checks |
|-------|--------|
| cc-defensive-programming | 31 |
| aposd-simplifying-complexity | 44 |
| aposd-reviewing-module-design | 36 |
| cc-code-layout-and-style | 85 |
| cc-control-flow-quality | 124 |
| aposd-verifying-correctness | 40 |
| cc-quality-practices | 115 |
| cc-performance-tuning | 50 |
| aposd-optimizing-critical-paths | 40 |
| cc-documentation-quality | 49 |
| **Total (PR profile)** | **614** |

### Review Execution Flow

1. **Load profile** → Parse checklists and skills
2. **Validate** → Check checklist paths exist, warn on missing skills
3. **Get target** → Ask for diff args (staged, unstaged, branch)
4. **Extraction** → Parallel haiku agents (batch by files)
5. **Checking** → Parallel agents (1 per checklist, loads skills)
6. **Orchestrate** → Single haiku agent batches findings, creates investigation tasks
7. **Investigation** → Parallel haiku agents (1 per 5 findings), verify and filter
8. **Report** → Single haiku agent compiles findings into JSON report

**Main agent orchestrates** - dispatches all agents directly for true parallelism.

### Master Dispatcher Flow

The `code-foundations` skill (`skills/code-foundations/SKILL.md`) is the entry point:
1. Classifies task type (WRITE, DEBUG, REVIEW, OPTIMIZE, REFACTOR, SIMPLIFY, SECURE)
2. Runs mindset check via `cc-developer-character`
3. Routes DEBUG tasks to `cc-debugging` (scientific method)
4. Executes task-specific checklist
5. Runs pre-commit gate via `aposd-verifying-correctness`

### Development Workflows

**Choose based on scope:**

| Situation | Command | Ceremony |
|-----------|---------|----------|
| Quick hack, TDD, pair programming | `/code-foundations:hack` | None |
| Technical uncertainty | `/code-foundations:prototype` | Minimal |
| Feature needs planning | `/code-foundations:whiteboarding` | Medium |
| Executing approved plan | `/code-foundations:building` | Full |

### Hack Mode

```
/code-foundations:hack [what to build]
→ RED: Write failing test
→ GREEN: Minimum code to pass
→ REFACTOR: Clean up
→ REPEAT
```

No plans, no checkpoints, no subagents. Direct code slinging.

### Prototype → Whiteboarding → Building Workflow

Three-stage pattern for feature development:

| Command | Purpose | Output |
|---------|---------|--------|
| `/code-foundations:prototype` | Prove feasibility with minimum code | Prototype log in `docs/prototypes/` |
| `/code-foundations:whiteboarding` | Discovery-oriented brainstorming | Plan file in `docs/plans/` |
| `/code-foundations:building` | Checklist-based execution | Working code + tests |

**Full Flow:**
```
/code-foundations:prototype "can I show a notification?"
  → One question to prove
  → Minimum code (~50 lines max)
  → Binary answer: YES/NO/PARTIAL
  → Capture learnings to docs/prototypes/

        ↓ (if feasible)

/code-foundations:whiteboarding "build notification system"
  → Discovery questions (informed by prototype)
  → 2-3 approaches with trade-offs
  → Implementation-ready plan
  → Save to docs/plans/YYYY-MM-DD-<topic>.md

        ↓ (after plan approval)

/code-foundations:building docs/plans/<plan>.md
  → Feature branch required
  → Execute phases with quality gates
  → Per-phase commits + reviewer agent
  → Final verification + report
```

**When to use each:**

| Situation | Command |
|-----------|---------|
| "Can I do X?" / technical uncertainty | `/code-foundations:prototype` |
| Ready to plan full feature | `/code-foundations:whiteboarding` |
| Plan exists, ready to implement | `/code-foundations:building` |

**Quality Gates (per phase during /code-foundations:building):**
```
PRE-GATE:  cc-pseudocode-programming + aposd-designing-deep-modules
IMPLEMENT: Write code, run tests
POST-GATE: aposd-verifying-correctness + cc-defensive-programming + reviewer agent
CHECKPOINT: Commit only after all gates pass
```

Cannot proceed to next phase until current phase passes all gates including reviewer agent PASS.

## Skill File Structure

```
skills/<skill-name>/
├── SKILL.md         # Main skill definition with YAML frontmatter
├── checklists.md    # Detailed checklists
├── hard-data.md     # Research/data backing the skill
└── language-notes.md # Language-specific guidance (optional)
```

## Review Output Format

Reviews are **grouped by action type** (what to do next):

```markdown
## Findings
Confirmed issues.
1. **[ID]** file:line - Issue
   Evidence: ...
   Fix: ...

## Questions
Need more context.
1. **[ID]** file:line - Issue
   **Unknown**: [missing context]
```

**Key principle**: State what you DON'T know (**Unknown** section).

## Key Concepts

**APOSD Complexity Symptoms:**
- Change amplification (simple change → many modifications)
- Cognitive load (must know too much)
- Unknown unknowns (worst)

**CC Metrics:**
- Cohesion (routine does ONE thing)
- Coupling (minimized dependencies)
- Parameters ≤7, Inheritance depth < 3

**CC Skills (15 total):**
All CC skills reference `references/cc-foundations.md` for shared vocabulary (cohesion spectrum, coupling criteria, key metrics).

Additional skills:
- `cc-debugging` - Scientific debugging (Chapter 23): STABILIZE → LOCATE → HYPOTHESIZE → EXPERIMENT → FIX → TEST → SEARCH
- `cc-table-driven-methods` - Replace complex logic with tables (Chapter 18): direct access, indexed access, stair-step access

## Publishing

### Plugin Structure

- `.claude-plugin/plugin.json` - Plugin manifest with name, version, description
- Version follows semver (e.g., 2.7.1)

### Marketplace

Published to `ryanthedev/rtd-claude-inn` marketplace:

**Marketplace files:**
- `~/repos/rtd-claude-inn/.claude-plugin/marketplace.json` - Plugin registry with versions
- `~/repos/rtd-claude-inn/README.md` - Marketplace documentation with version table

**To publish a new version:**
1. Bump version in `.claude-plugin/plugin.json`
2. Commit and push to `origin/main`
3. Update `marketplace.json` in rtd-claude-inn with new version
4. Update README.md version table
5. Commit and push rtd-claude-inn

**Install commands:**
```bash
/plugin marketplace add ryanthedev/rtd-claude-inn
/plugin install code-foundations@rtd
/plugin update code-foundations@rtd
```
