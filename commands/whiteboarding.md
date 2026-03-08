---
description: "Discovery-oriented brainstorming to create implementation-ready plans. Saves to docs/plans/ for /code-foundations:building execution."
argument-hint: "[feature description or user story]"
allowed-tools: ["Read", "Glob", "Grep", "Write", "Bash", "AskUserQuestion", "Skill", "Task", "EnterPlanMode"]
---

# /whiteboarding

## FIRST - Enter Plan Mode

Before doing anything else, use the `EnterPlanMode` tool to enter plan mode.
This ensures all whiteboarding happens without accidental code changes.

---

## STOP - Load Skills First

Before whiteboarding, load your skill lenses using the Skill tool:
1. `Skill(code-foundations:cc-construction-prerequisites)` - requirements validation
2. `Skill(code-foundations:aposd-designing-deep-modules)` - interface design principles

---

## STOP

- **Present 2-3 approaches** - Never skip to single approach
- **One question at a time** - Wait for answer before next
- **YAGNI** - No hypothetical features in the plan

---

**Brainstorm → Design → Save → Handoff**

---

## Invoke Skill

```
Skill(code-foundations:whiteboarding)
```

---

## Execution Flow

### 1. Classify Complexity

| Signal | Complexity | Questions |
|--------|-----------|-----------|
| Single file, clear scope | Simple | 3-4 |
| Multiple files, some unknowns | Medium | 5-7 |
| Architecture changes, many unknowns | Complex | 8-12 |

### 2. Discovery-Oriented Questioning (ONE AT A TIME)

Ask questions sequentially using `AskUserQuestion` tool (NOT text output). Wait for each answer. Use multiple-choice when possible. Minimum questions: Simple=2, Medium=4, Complex=6. **Do NOT proceed to approaches until minimum questions asked and answered.**

### 3. Present 2-3 Approaches

**MANDATORY.** Never skip to single approach.

```markdown
## Approach A: [Name] (Recommended)
**Idea:** ...
**Pros:** ...
**Cons:** ...

## Approach B: [Name]
...
```

### 4. Detail Implementation

Break into sections (200-300 words each). Get user confirmation for each.

### 5. Save Plan

```bash
mkdir -p docs/plans
# Write: docs/plans/YYYY-MM-DD-<topic-slug>.md
```

### 6. Handoff

After saving the plan, use `AskUserQuestion` to ask how to proceed:

**Question:** "How would you like to proceed?"

**Options:**
1. **Clear conversation and build** (Recommended) - Execute `/clear` then run `/code-foundations:building <plan-path>`
2. **Tell me what to do** - Provide step-by-step instructions to execute manually

If user selects option 1: Execute `/clear` command, then immediately run `/code-foundations:building <plan-path>`

---

## Plan File Format

```markdown
# Plan: [Topic]

**Created:** YYYY-MM-DD
**Status:** ready

## Context
[problem statement]

## Constraints
- [list]

## Chosen Approach
[name + rationale]

## Implementation Checklist

### Phase 1: [Name]
- [ ] [task with file path]

**Files:** [list]
**Details:** [specifics]

### Phase 2: ...

## Test Coverage
**Level:** [100% / Backend only / Backend + frontend / None / Per-phase]

## Test Plan
- [ ] Unit: ...
- [ ] Integration: ...

## Notes
[edge cases, gotchas]

## Execution Log
_Filled during /code-foundations:building_
```

---

## Quality Gate

Before saving, verify:
- [ ] Problem statement confirmed by user
- [ ] At least 2 approaches were considered
- [ ] Each section validated by user
- [ ] **Test coverage level chosen** (100% recommended)
- [ ] Test plan included
- [ ] YAGNI applied (no hypothetical features)
