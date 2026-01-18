# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Code-foundations is a Claude Code plugin providing software engineering skills based on *Code Complete* (McConnell) and *A Philosophy of Software Design* (Ousterhout). It includes a three-level code review system with 5 specialized dual-role agents.

## Architecture

### Two Skill Families

| Family | Prefix | Focus |
|--------|--------|-------|
| Code Complete | `cc-*` | Process rigor, metrics, checklists |
| APOSD | `aposd-*` | Design philosophy, complexity reduction |

### Directory Structure

- `skills/` - Individual skill definitions (SKILL.md + supporting markdown)
- `commands/` - User-invocable commands (slash commands)
- `agents/` - 5 consolidated review agents with dual roles
- `references/` - Shared reference materials (including `cc-foundations.md` for shared CC vocabulary)
- `docs/` - Case study examples

### Three-Level Code Review System

| Level | Command | Agents | Focus |
|-------|---------|--------|-------|
| 1 | `/check-commit` | 0 | Quick scan (direct execution) |
| 2 | `/review-changes` | 3 | defensive, quality, correctness |
| 3 | `/review-pr` | 5 | All agents including performance + documentation |

### 5 Consolidated Agents (Dual Roles)

| Agent | Combines | Skills |
|-------|----------|--------|
| **defensive-reviewer** | security + error-handling | cc-defensive-programming, aposd-simplifying-complexity |
| **quality-reviewer** | maintainability + clarity | aposd-reviewing-module-design, cc-code-layout-and-style |
| **correctness-reviewer** | bugs + test coverage | aposd-verifying-correctness, cc-quality-practices |
| **performance-reviewer** | algorithms + hot paths | cc-performance-tuning, aposd-optimizing-critical-paths |
| **documentation-reviewer** | docs + comments | cc-documentation-quality |

Each agent invokes 2 skills: one from CC (process) + one from APOSD (philosophy).

### Master Dispatcher Flow

The `code-foundations` skill (`skills/code-foundations/SKILL.md`) is the entry point:
1. Classifies task type (WRITE, DEBUG, REVIEW, OPTIMIZE, REFACTOR, SIMPLIFY, SECURE)
2. Runs mindset check via `cc-developer-character`
3. Routes DEBUG tasks to `cc-debugging` (scientific method)
4. Executes task-specific checklist
5. Runs pre-commit gate via `aposd-verifying-correctness`

### Prototype → Whiteboarding → Building Workflow

Three-stage pattern for feature development:

| Command | Purpose | Output |
|---------|---------|--------|
| `/prototype` | Prove feasibility with minimum code | Prototype log in `docs/prototypes/` |
| `/whiteboarding` | Discovery-oriented brainstorming | Plan file in `docs/plans/` |
| `/building` | Checklist-based execution | Working code + tests |

**Full Flow:**
```
/prototype "can I show a notification?"
  → One question to prove
  → Minimum code (~50 lines max)
  → Binary answer: YES/NO/PARTIAL
  → Capture learnings to docs/prototypes/

        ↓ (if feasible)

/whiteboarding "build notification system"
  → Discovery questions (informed by prototype)
  → 2-3 approaches with trade-offs
  → Implementation-ready plan
  → Save to docs/plans/YYYY-MM-DD-<topic>.md

        ↓ (after plan approval)

/building docs/plans/<plan>.md
  → Feature branch required
  → Execute phases with quality gates
  → Per-phase commits + reviewer agent
  → Final verification + report
```

**When to use each:**

| Situation | Command |
|-----------|---------|
| "Can I do X?" / technical uncertainty | `/prototype` |
| Ready to plan full feature | `/whiteboarding` |
| Plan exists, ready to implement | `/building` |

**Quality Gates (per phase during /building):**
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

Reviews are **grouped by file** with effort estimates:

```markdown
### src/file.cs

1. 🔴 [CRITICAL] Line 84 - Issue (agent)
   Fix: [specific code]
   Effort: 🟢 Quick / 🟡 Medium / 🔴 Large
```

## Severity Levels

- **CRITICAL** 🔴 - Blocks merge (security, correctness)
- **IMPORTANT** 🟡 - Should fix (design, quality)
- **SUGGESTION** 🟢 - Consider (improvements)

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

New skills added:
- `cc-debugging` - Scientific debugging (Chapter 23): STABILIZE → LOCATE → HYPOTHESIZE → EXPERIMENT → FIX → TEST → SEARCH
- `cc-table-driven-methods` - Replace complex logic with tables (Chapter 18): direct access, indexed access, stair-step access
