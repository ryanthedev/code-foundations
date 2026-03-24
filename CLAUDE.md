# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Code-foundations is a Claude Code plugin providing software engineering skills based on *Code Complete* (McConnell) and *A Philosophy of Software Design* (Ousterhout). It includes a building workflow with gated sub-phases (pre-gate, implement, post-gate, verify, checkpoint) and an experimental code review system.

## Architecture

### Skill Families

| Family | Prefix | Focus |
|--------|--------|-------|
| Code Complete | `cc-*` | Process rigor, metrics, checklists |
| APOSD | `aposd-*` | Design philosophy, complexity reduction |
| GoF Design Patterns | `gof-*` | 23 Gang of Four patterns, decision trees, structural recipes |

### Directory Structure

- `skills/` - Individual skill definitions (SKILL.md + checklists.md)
- `commands/` - User-invocable commands (slash commands)
- `agents/` - Agent templates (pre-gate-agent, implementation-agent, post-gate-agent, debug-agent, code-agent)
- `references/` - Shared reference materials
- `docs/` - Case study examples

### Code Review System

**Single entry point:** `/code-foundations:review`

**Two presets:**

**Sanity Flow (--sanity):** 14 core checks, intelligent batching
```
┌────────────┐   ┌─────────────┐   ┌───────────┐   ┌───────────────┐
│ EXTRACTION │ → │ ORCHESTRATE │ → │ CHECKING  │ → │ INVESTIGATION │
│  (haiku)   │   │  (sonnet)   │   │ (sonnet)  │   │   (sonnet)    │
└────────────┘   └─────────────┘   └───────────┘   └───────────────┘
      ↓                 ↓                 ↓                  ↓
  1 per 5 files   • Triage files    1 agent per      1 agent per
  Extract units   • Smart batching  batch, runs      5 findings,
  + diffs                           14 core checks   provides fixes
```

**PR Flow (--pr):** 546 checks, prefix-based grouping
```
┌────────────┐   ┌─────────────┐   ┌───────────┐   ┌─────────────┐   ┌───────────────┐
│ EXTRACTION │ → │ CHECK ORCH  │ → │ CHECKING  │ → │ ORCHESTRATE │ → │ INVESTIGATION │
│  (haiku)   │   │   (haiku)   │   │ (sonnet)  │   │   (haiku)   │   │   (sonnet)    │
└────────────┘   └─────────────┘   └───────────┘   └─────────────┘   └───────────────┘
      ↑                ↑                 ↑                ↑                  ↑
   Batch by        Group by         1 agent per      Dedupe &          1 agent per
   files (5)       ID prefix        prefix group     batch             5 findings
                   (GC-, EH-...)    + skills
```

| Preset | Checks | Use Case |
|--------|--------|----------|
| `--sanity` | 14 core (consensus-distilled) | Pre-commit sanity |
| `--pr` | 546 (8 checklists) | Full PR review |

### Skill Checklist Counts

| Skill | Checks |
|-------|--------|
| cc-defensive-programming | 41 |
| aposd-simplifying-complexity | 44 |
| aposd-reviewing-module-design | 42 |
| code-clarity-and-docs | 87 |
| cc-control-flow-quality | 104 |
| aposd-verifying-correctness | 33 |
| cc-quality-practices | 125 |
| performance-optimization | 70 |
| **Total (PR preset)** | **546** |

### Review Execution Flow

1. **Load preset** → Parse checklists and skills
2. **Validate** → Check checklist paths exist, warn on missing skills
3. **Get target** → Ask for diff args (staged, unstaged, branch)
4. **Create phase tasks** → TaskCreate for each phase (enforces flow)
5. **Extraction** → Parallel haiku agents (batch by files)
6. **Check Orchestrate** → Single haiku agent parses checklists, groups by ID prefix
7. **Checking** → Parallel sonnet agents use `add-finding.sh` to record results
8. **Orchestrate** → Single haiku agent batches findings
9. **Investigation** → Parallel sonnet agents use `add-verdict.sh` to record verdicts + fixes
10. **Summary** → Display results, offer actions (open dashboard, fix all)

**Phase enforcement via TaskCreate/TaskUpdate** - agent cannot skip phases.
**Schema enforcement via bash scripts** - `add-finding.sh` and `add-verdict.sh` validate all inputs.

### Development Workflows

**Choose based on scope:**

| Situation | Command | Ceremony |
|-----------|---------|----------|
| Bug investigation | `/code-foundations:debug` | Minimal |
| Technical uncertainty | `/code-foundations:prototype` | Minimal |
| Single feature, design-first | `/code-foundations:code` | Light |
| Feature needs planning | `/code-foundations:whiteboarding` | Medium |
| Executing approved plan | `/code-foundations:building` | Full |

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
  → Skill audit (scans all installed plugins for relevant skills)
  → Discovery questions (informed by prototype)
  → 2-3 approaches with trade-offs
  → Implementation-ready plan with Skills per phase
  → Save to docs/plans/YYYY-MM-DD-<topic>.md
  → Subagent CHECK reviews plan with fresh eyes
  → User confirms

        ↓ (after plan approval)

/code-foundations:building docs/plans/<plan>.md
  → Feature branch required
  → Execute phases with quality gates
  → Model auto-detected per phase (haiku/sonnet/opus)
  → Per-phase commits only after POST-GATE passes
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
PRE-GATE:  cc-pseudocode-programming + aposd-designing-deep-modules + cc-routine-and-class-design + [plan Skills]
IMPLEMENT: cc-control-flow-quality + aposd-simplifying-complexity + code-clarity-and-docs + [plan Skills]
POST-GATE: aposd-verifying-correctness + cc-quality-practices + aposd-reviewing-module-design + cc-defensive-programming + [plan Skills]
VERIFY:    performance-optimization + cc-refactoring-guidance + build + tests + lint
CHECKPOINT: Commit only after all gates pass
```

`[plan Skills]` = additional skills from the plan's per-phase `**Skills:**` field. These come from whiteboarding's skill audit and can include skills from any installed plugin (e.g., `react-native-foundations:coding`, `design-for-ai:a11y-audit`).

Model auto-detected per phase: haiku (<=2 tasks/files), opus (>=6 tasks/files or OPUS keyword), sonnet (default).
Plan `**Model:**` field overrides auto-detection.
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
