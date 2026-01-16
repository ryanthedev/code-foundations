---
description: "Execute whiteboard plans with checklist-based tracking. Produces working code with tests."
argument-hint: "[path/to/plan.md]"
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash", "Task", "Skill", "TodoWrite"]
---

# /building

**Load Plan → Checklist → Execute → Verify → Report**

---

## Invoke Skill

```
Skill(code-foundations:building)
```

---

## Execution Flow

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
PRE-GATE (before any code)
├─ INVOKE cc-pseudocode-programming
└─ INVOKE aposd-designing-deep-modules

IMPLEMENT
├─ Write code from pseudocode
└─ Run tests

POST-GATE (before marking complete)
├─ INVOKE aposd-verifying-correctness
├─ INVOKE cc-defensive-programming
└─ DISPATCH phase-reviewer agent

CHECKPOINT (only if all gates pass)
├─ Commit
└─ Update execution log
```

### 4. Phase Reviewer Agent (MANDATORY)

Dispatch per phase:
```
Task tool:
- subagent_type: "general-purpose"
- prompt: |
    INVOKE code-foundations skill.
    Review Phase N: [files changed]
    Return: PASS/FAIL with specific issues
```

**Cannot proceed to next phase until reviewer returns PASS.**

### 5. Final Verification

```bash
npm test  # or equivalent
```

All tests must pass before completion.

### 6. Report

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
