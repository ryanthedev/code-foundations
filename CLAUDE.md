# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Code-foundations is a Claude Code plugin providing software engineering skills based on *Code Complete* (McConnell) and *A Philosophy of Software Design* (Ousterhout). It includes a building workflow with gated sub-phases (pre-gate, implement, post-gate, checkpoint) and an experimental code review system.

## Architecture

### Two Skill Families

| Family | Prefix | Focus |
|--------|--------|-------|
| Code Complete | `cc-*` | Process rigor, metrics, checklists |
| APOSD | `aposd-*` | Design philosophy, complexity reduction |

### Directory Structure

- `skills/` - Individual skill definitions (SKILL.md + checklists.md)
- `commands/` - User-invocable commands (slash commands)
- `agents/` - Agent templates (pre-gate-agent, implementation-agent, post-gate-agent)
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

**PR Flow (--pr):** 614 checks, prefix-based grouping
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
| `--pr` | 614 (10 checklists) | Full PR review |

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
| **Total (PR preset)** | **614** |

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
PRE-GATE:  cc-construction-prerequisites + cc-pseudocode-programming + aposd-designing-deep-modules
IMPLEMENT: Write code, run tests
POST-GATE: aposd-verifying-correctness + cc-defensive-programming + reviewer agent
CHECKPOINT: Commit only after all gates pass
```

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
