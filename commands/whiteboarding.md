---
description: "Discovery-oriented brainstorming to create implementation-ready plans. Saves to docs/plans/ for /building execution."
argument-hint: "[feature description or user story]"
allowed-tools: ["Read", "Glob", "Grep", "Write", "Bash", "AskUserQuestion"]
---

# /whiteboarding

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

Ask questions sequentially. Wait for each answer. Use multiple-choice when possible.

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

```
Plan saved. Next steps:
1. Refresh context → /building <plan-path> (recommended for complex)
2. Continue now → /building (OK for simple)
```

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

## Test Plan
- [ ] Unit: ...
- [ ] Integration: ...

## Notes
[edge cases, gotchas]

## Execution Log
_Filled during /building_
```

---

## Quality Gate

Before saving, verify:
- [ ] Problem statement confirmed by user
- [ ] At least 2 approaches were considered
- [ ] Each section validated by user
- [ ] Test plan included
- [ ] YAGNI applied (no hypothetical features)
