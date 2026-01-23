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

### 3. Execute Each Phase (Gated, File-Based)

For each phase, run this **mandatory** sequence. All outputs go to files in `docs/building/`:

```
DISCOVERY (via subagent)
├─ Explore subagent reads codebase
├─ Writes: docs/building/<plan>-phase-N-discovery.md
└─ Returns: file path only

PRE-GATE (via subagent)
├─ Reads discovery file
├─ Runs pseudocode + design skills
├─ Writes: docs/building/<plan>-phase-N-pseudocode.md
└─ Returns: file path only

IMPLEMENT (via subagent)
├─ Reads discovery + pseudocode files
├─ Implementation agent writes code
└─ Returns: DONE or BLOCKED

POST-GATE (via subagent)
├─ Reads all phase files
├─ Reviewer agent runs checklists
├─ Writes: docs/building/<plan>-phase-N-review.md
└─ Returns: PASS or FAIL

CHECKPOINT (only if PASS)
├─ Commit
└─ Update execution log
```

### 4. Discovery Subagent (MANDATORY)

```
Task tool:
- subagent_type: "Explore"
- description: "Discovery for Phase N"
- prompt: |
    Explore Phase N files.
    Write findings to: docs/building/<plan>-phase-N-discovery.md
    Return: file path only
```

### 5. PRE-GATE Subagent (MANDATORY)

```
Task tool:
- subagent_type: "general-purpose"
- description: "PRE-GATE for Phase N"
- prompt: |
    Load skills: cc-pseudocode-programming, aposd-designing-deep-modules
    Read: docs/building/<plan>-phase-N-discovery.md
    Write pseudocode to: docs/building/<plan>-phase-N-pseudocode.md
    Return: file path only
```

### 6. Implementation Agent (MANDATORY)

```
Task tool:
- subagent_type: "code-foundations:implementation-agent"
- description: "Implement Phase N"
- prompt: |
    Read input files:
    - docs/building/<plan>-phase-N-discovery.md
    - docs/building/<plan>-phase-N-pseudocode.md
    Return: DONE or BLOCKED
```

### 7. POST-GATE Reviewer (MANDATORY)

| Focus | Agent |
|-------|-------|
| General | `code-foundations:correctness-reviewer` |
| Error handling | `code-foundations:defensive-reviewer` |
| Design | `code-foundations:quality-reviewer` |

```
Task tool:
- subagent_type: "code-foundations:correctness-reviewer"
- description: "POST-GATE for Phase N"
- prompt: |
    Read all phase files in docs/building/<plan>-phase-N-*
    Write review to: docs/building/<plan>-phase-N-review.md
    Return: PASS or FAIL
```

**STOP. Cannot proceed until reviewer returns PASS.**

### 7. Final Verification

```bash
npm test  # or equivalent
```

All tests must pass before completion.

### 8. Report

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
