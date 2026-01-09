---
name: code-foundations
description: CRITICAL - Invoke FIRST before ANY code activity. MUST load before
  writing, planning, reviewing, debugging, fixing, implementing, or refactoring code.
  Triggers on implement, build, fix, add, create, refactor, optimize, review, debug.
---

## First Action

**Execute immediately:**
```bash
python3 ~/.claude/bin/log-skill-load.py code-foundations
```

# Code Foundations

## STOP Before Action

Baseline tests showed "Eager Developer" anti-pattern: urgency → skip prerequisites → rework.

**Before ANY code activity:**
1. INVOKE cc-developer-character (always)
2. CLARIFY requirements (don't assume)
3. DETECT phase and load skills below

## Phase Skills

| Activity | Invoke |
|----------|--------|
| Planning/New feature | cc-construction-prerequisites |
| Design/New routine | cc-pseudocode-programming, cc-routine-and-class-design |
| Implementing | cc-control-flow-quality, cc-data-organization, cc-defensive-programming |
| Reviewing/Debugging | cc-quality-practices, cc-refactoring-guidance |
| Optimizing | cc-performance-tuning (measure FIRST) |

## Red Flags (Observed Rationalizations)

| If you think... | Reality |
|-----------------|---------|
| "It's urgent" | Prerequisites = 5% time, save 10x rework |
| "I'll clarify later" | Coding first = emotional investment in wrong solution |
| "I know this pattern" | Every codebase is different; check first |
| "Just let me start" | Starting without design = debugging without tests |

## Crisis Invariants

Never skip: validate external input, ≤3 nesting, no magic numbers.
