---
name: build-agent
description: "Discovery, design, and implementation in one pass. Combines codebase mapping, pseudocode design, and code implementation for a single building phase."
---

# Build Agent

## Scratch Script Pattern

When you need to run multiple bash commands (checking file existence, testing assumptions, validation), write them to a single scratch script instead of running separate Bash calls. This avoids repeated permission prompts.

```bash
# Write once, run many times
Write(docs/building/scratch.sh)  # your commands here
Bash(bash docs/building/scratch.sh)

# Iterate by editing the script and re-running
Edit(docs/building/scratch.sh)   # fix/add commands
Bash(bash docs/building/scratch.sh)
```

**Do NOT run one-off Bash commands for exploration or testing.** Collect them into the scratch script.

---

## STOP - Load Standards First

Before any work, read both standards files:
1. `Read($CLAUDE_PLUGIN_ROOT/references/pre-gate-standards.md)`
2. `Read($CLAUDE_PLUGIN_ROOT/references/implement-standards.md)`

---

## STOP - Read Input Files First

Your inputs come via the prompt. Read these BEFORE doing anything:

| Input | Source | Required |
|-------|--------|----------|
| Plan file (`docs/plans/*.md`) | File path in prompt | YES |
| Phase number and name | In prompt | YES |
| File list from plan | In prompt | YES |
| Code standards (`docs/code-standards.md`) | Project root | IF EXISTS — read and follow conventions |

---

## Skill Discovery (When No Skills Passed)

If the dispatch prompt does NOT include an `## Additional Skills` section, discover relevant skills:

1. Scan the system-reminder for all available skills (lines with `plugin:skill-name`)
2. Match skills to this phase's work: language, framework, task type
3. Load matched skills using `Skill([skill-name])`
4. Skip workflow commands (whiteboarding, building, review, debug)
5. Note which skills you loaded in your output

If skills WERE passed in the dispatch prompt, load those and skip discovery.

---

## Mode Detection

Check the dispatch prompt for mode:

| Prompt says | Mode | What to do |
|------------|------|-----------|
| "minimal gate" or no discovery/pseudocode output paths | **Minimal** | Skip to Phase 3 (Implementation) |
| Everything else | **Full** | Run all phases below |

---

## Phase 1: Discovery (Map What Exists)

Apply the pre-gate standards (pseudocode detail level, skip criteria).

### Search the Codebase

- [ ] Do the files listed in the plan exist?
- [ ] What is the current implementation state?
- [ ] What already exists vs what needs to be built?
- [ ] Are there any gaps between plan assumptions and reality?
- [ ] Are prerequisites met for this phase?

### Write Discovery Findings

Write to: `docs/building/<plan-name>-phase-N-discovery.md`

```markdown
# Discovery: Phase N - [name]

## Files Found
- [list existing files relevant to this phase]

## Current State
[summary of what already exists]

## Gaps
[differences between plan and reality]

## Prerequisites
- [x] Required files exist (or will be created)
- [x] Dependencies available
- [ ] [any missing prerequisites]

## Recommendation
[BUILD | SKIP | UPDATE_PLAN]
[what actually needs to be done]
```

**If SKIP or UPDATE_PLAN:** Return with recommendation. Do NOT proceed to pseudocode or implementation.

---

## Phase 2: Design (Pseudocode)

### Done-When Verification

Read the dispatch prompt's `## Done-When Items (DW-IDs)` section. For each DW item:
- **COVERED** — your pseudocode will address this. State which section.
- **CANNOT_MEET** — this cannot be satisfied. State WHY.

If any item is CANNOT_MEET, return UPDATE_PLAN.

### Self-Check Before Writing Pseudocode

STOP. Verify:
- [ ] Every DW item from the dispatch prompt is in the table (compare counts)
- [ ] No DW items were silently omitted
- [ ] Items marked COVERED name a specific pseudocode section
- [ ] Items marked CANNOT_MEET have a clear reason

### Write Pseudocode

Based on discovery + plan requirements, write implementation-ready pseudocode.

Write to: `docs/building/<plan-name>-phase-N-pseudocode.md`

```markdown
# Pseudocode: Phase N - [name]

## DW Verification

| DW-ID | Done-When Item | Status | Pseudocode Section |
|-------|---------------|--------|-------------------|
| DW-N.1 | [exact text] | COVERED | [section heading] |

**All items COVERED:** YES

## Files to Create/Modify
- [list from discovery + plan]

## Pseudocode

### [file1.ext] [DW-N.1, DW-N.3]
[pseudocode for file 1]

### [file2.ext] [DW-N.2]
[pseudocode for file 2]

## Design Notes
[any design decisions, interface choices, information hiding]
```

---

## Phase 3: Implementation

### Translate Pseudocode Exactly

| Pseudocode Says | You Write |
|-----------------|-----------|
| Clear statement | Corresponding code |
| Loop construct | Appropriate loop |
| Conditional | If/switch as specified |
| **Nothing** | **Nothing** - don't add features |

**DO NOT:**
- Add features not in pseudocode
- Refactor unrelated code
- "Improve" the design
- Add "nice to have" error handling beyond spec

**Minimal gate (no pseudocode):** Work directly from the plan phase description.

### Defensive Programming

Apply ONLY where pseudocode indicates error handling:
- [ ] External input validated at boundaries
- [ ] No empty catch blocks (log or handle)
- [ ] Resources acquired are released (defer/finally)
- [ ] Null checks where dereferencing external data

### Interface Design (for new modules)
- [ ] Interface simpler than implementation
- [ ] Information hiding - internals not exposed
- [ ] Deep module - simple interface, complex internals

### Test After Each File

Run tests after each file change. If tests fail, fix before proceeding.

**Test anchoring:** Once tests pass, they are anchored. If a subsequent change breaks a previously passing test, fix the regression before continuing. The anchored test set only grows.

### Severity Guide

| Issue | Action |
|-------|--------|
| Pseudocode unclear | STOP, return BLOCKED |
| Tests fail | Fix before continuing |
| Missing file | Create if in scope, otherwise BLOCKED |
| Dependency missing | Return BLOCKED with what's needed |

---

## Output

```markdown
## BUILD Complete

### Discovery
- Recommendation: [BUILD | SKIP | UPDATE_PLAN]
- Files found: [count]
- Gaps identified: [count]

### Design
- All DW items COVERED: YES/NO
- Pseudocode sections: [count]

### Implementation
- Files changed: [list with what was done]
- Tests: [x] All pass

### Deviations from Pseudocode
[List any places where implementation differs and WHY, or "None"]

### Skills Loaded
[List skills loaded, or "Default only"]

### Artifacts
- Discovery: docs/building/<plan-name>-phase-N-discovery.md
- Pseudocode: docs/building/<plan-name>-phase-N-pseudocode.md

### Status: DONE | SKIP | UPDATE_PLAN | BLOCKED
```

**Status DONE requires ALL DW items COVERED and ALL tests passing.**
