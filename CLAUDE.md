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
- `references/` - Shared reference materials
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
3. Executes task-specific checklist
4. Runs pre-commit gate via `aposd-verifying-correctness`

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
