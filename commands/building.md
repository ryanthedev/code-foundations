---
description: "Execute whiteboard plans with checklist-based tracking. Produces working code with tests."
argument-hint: "[path/to/plan.md]"
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash", "Task", "Skill", "TodoWrite"]
---

# /building

## STOP - READ BEFORE PROCEEDING

- **No building on main/master** - Create feature branch first
- **DO NOT implement directly** - Dispatch subagent for implementation
- **PRE-GATE must pass** - Pseudocode required before any code
- **POST-GATE must pass** - Reviewer agent must return PASS
- **Cannot skip gates** - All gates are blocking, not advisory

---

**Load Plan → Checklist → Execute → Verify → Report**

---

## Invoke Skill

```
Skill(code-foundations:building)
```

---

## Execution Flow

### 0. Branch Gate (FIRST CHECK)

```bash
git branch --show-current
```

| Branch | Action |
|--------|--------|
| `main`/`master` | **STOP.** Create `feature/<topic>` first |
| Feature branch | Proceed |

**Non-negotiable.** No building on main.

### 1. Load Plan

If path provided:
```bash
cat docs/plans/<path>.md
```

If no path:
```bash
ls -la docs/plans/*.md | head -20
```

Ask: "Which plan should I execute?"

### 2. Initialize Tracking

Convert plan phases to TodoWrite:
```
TodoWrite([
  {content: "Phase 1 task", status: "pending", activeForm: "..."},
  ...
])
```

Update plan: `Status: in-progress`

### 3. Execute Each Phase (Gated)

For each phase, run this **mandatory** sequence:

```
PRE-GATE (BLOCKS IMPLEMENTATION)
├─ Skill(code-foundations:cc-pseudocode-programming)
├─ Skill(code-foundations:aposd-designing-deep-modules)
└─ Confirm: Pseudocode exists? Design reviewed?

IMPLEMENT (via subagent - DO NOT code directly)
├─ Task tool → implementation subagent
├─ Wait for subagent DONE
└─ Run tests

POST-GATE (BLOCKS CHECKPOINT)
├─ Skill(code-foundations:aposd-verifying-correctness)
├─ Skill(code-foundations:cc-defensive-programming)
├─ Task tool → reviewer agent
└─ Wait for PASS

CHECKPOINT (only if reviewer returns PASS)
├─ Commit
└─ Update execution log
```

### 4. Implementation Subagent (MANDATORY)

**DO NOT implement directly. Dispatch subagent:**

```
Task tool:
- subagent_type: "general-purpose"
- description: "Implement Phase N"
- prompt: |
    INVOKE code-foundations skill.
    Implement Phase N from this pseudocode:
    [pseudocode from PRE-GATE]

    Files: [list]
    Return: DONE or BLOCKED
```

### 5. Phase Reviewer Agent (MANDATORY)

```
Task tool:
- subagent_type: "general-purpose"
- description: "Phase N review"
- prompt: |
    INVOKE code-foundations skill.
    Review Phase N: [files changed]
    Return: PASS or FAIL with issues
```

**STOP. Cannot proceed until reviewer returns PASS.**

### 6. Final Verification

```bash
npm test  # or equivalent
```

All tests must pass before completion.

### 7. Report

Update plan: `Status: complete`

Output summary:
```markdown
# Build Complete

**Plan:** [name]
**Phases:** N/N complete
**Tests:** All passing

## Files Changed
- [list]

## Commits
- [hash] Phase 1: ...
```

---

## Error Handling

If task fails:
1. STOP - don't proceed
2. Log failure in execution log
3. Update plan: `Status: blocked`
4. Ask user: Debug now / Skip / Pause

---

## Resume Protocol

For `Status: in-progress` or `Status: blocked`:
1. Read execution log
2. Find last checkpoint
3. Ask: "Resume from Phase N? Or discuss blocker first?"

---

## Scope Discipline

If you see improvements not in plan:
- Do NOT implement
- Ask: "Add to plan / Add to backlog / Skip"
