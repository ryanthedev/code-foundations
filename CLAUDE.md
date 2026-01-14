# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Code-foundations is a Claude Code plugin providing software engineering skills based on *Code Complete* (McConnell) and *A Philosophy of Software Design* (Ousterhout). It includes a three-level code review system with specialized agents.

## Architecture

### Two Skill Families

| Family | Prefix | Focus |
|--------|--------|-------|
| Code Complete | `cc-*` | Process rigor, metrics, checklists |
| APOSD | `aposd-*` | Design philosophy, complexity reduction |

### Directory Structure

- `skills/` - Individual skill definitions (SKILL.md + supporting markdown)
- `commands/` - User-invocable commands (slash commands)
- `agents/` - Specialized review agents dispatched by commands
- `references/` - Shared reference materials (review-matrix.md, aposd-foundations.md)
- `docs/` - Case study examples

### Three-Level Code Review System

| Level | Command | Scope | Agents |
|-------|---------|-------|--------|
| 1 | `/check-commit` | Single commit | None (direct execution) |
| 2 | `/review-changes` | Staged/unstaged | 2-3 parallel (maintainability, error-handling, correctness) |
| 3 | `/review-pr` | Full branch | 6+ parallel (security, performance, maintainability, errors, clarity, correctness) |

### Master Dispatcher Flow

The `code-foundations` skill (`skills/code-foundations/SKILL.md`) is the entry point. It:
1. Classifies task type (WRITE, DEBUG, REVIEW, OPTIMIZE, REFACTOR, SIMPLIFY, SECURE)
2. Runs mindset check via `cc-developer-character`
3. Executes task-specific checklist
4. Runs pre-commit gate via `aposd-verifying-correctness`

### Agent → Skill Mapping

Agents use skills as evaluation lenses:
- `security-reviewer` → cc-defensive-programming
- `performance-reviewer` → cc-performance-tuning, aposd-optimizing-critical-paths
- `maintainability-reviewer` → aposd-reviewing-module-design, cc-routine-and-class-design
- `error-handling-reviewer` → cc-defensive-programming, aposd-simplifying-complexity
- `clarity-reviewer` → aposd-improving-code-clarity, cc-code-layout-and-style
- `correctness-reviewer` → aposd-verifying-correctness

## Skill File Structure

Each skill follows this pattern:
```
skills/<skill-name>/
├── SKILL.md         # Main skill definition with YAML frontmatter
├── checklists.md    # Detailed checklists
├── hard-data.md     # Research/data backing the skill
└── language-notes.md # Language-specific guidance (optional)
```

SKILL.md frontmatter format:
```yaml
---
name: skill-name
description: "When to use this skill..."
---
```

## Severity Levels

All reviews use consistent severity:
- **CRITICAL** - Blocks merge (security, correctness issues)
- **IMPORTANT** - Should fix (design, quality issues)
- **SUGGESTION** - Consider (improvements)
- **POSITIVE** - Good patterns observed

## Key Concepts from Source Material

**APOSD Complexity Symptoms:**
- Change amplification (simple change → many modifications)
- Cognitive load (must know too much)
- Unknown unknowns (worst - don't know what you don't know)

**CC Metrics:**
- Cohesion (routine does ONE thing)
- Coupling (minimized dependencies)
- Parameters ≤7 per routine
- Inheritance depth < 3
