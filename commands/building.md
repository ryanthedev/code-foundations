---
description: "Execute whiteboard plans with checklist-based tracking. Produces working code with tests."
argument-hint: "[path/to/plan.md]"
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash", "Task", "Skill"]
---

# /building

## STOP - READ BEFORE PROCEEDING

- **No building on main/master** - Create feature branch first
- **DO NOT implement directly** - Dispatch subagent for implementation
- **PRE-GATE must pass** - Pseudocode required before any code
- **POST-GATE must pass** - Reviewer agent must return PASS
- **Cannot skip gates** - Sub-phases enforced via TaskCreate with blockedBy chains

---

**Load Plan → Setup → Execute → Verify → Report**

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

### 2. Initialize Tracking + Create ALL Sub-Phase Tasks

Update plan: `Status: in-progress`

**DO NOT create phase-level tasks. DO NOT use TodoWrite.**

Create 4 sub-phase tasks for EVERY phase upfront, then chain them all:

```
For each phase N:
  TaskCreate: "Phase N.1: PRE-GATE - [name]"
  TaskCreate: "Phase N.2: IMPLEMENT - [name]"
  TaskCreate: "Phase N.3: POST-GATE - [name]"
  TaskCreate: "Phase N.4: CHECKPOINT - [name]"

Chain within phase: N.2 blockedBy N.1, N.3 blockedBy N.2, N.4 blockedBy N.3
Chain between phases: (N+1).1 blockedBy N.4
```

**The user sees the full pipeline immediately.**

### 3. Execute Each Phase (TaskCreate-Enforced)

For each phase, **auto-detect model** then create 5 TaskCreate tasks with blockedBy chains:

#### Model Auto-Detection

```
Parse phase: count tasks, count files, scan keywords

task_count <= 2 AND file_count <= 2 → haiku
task_count >= 6 OR file_count >= 6  → opus
OPUS_KEYWORDS in heading            → opus
Otherwise                           → sonnet

Plan **Model:** override wins over auto-detection.
```

#### Execute Sub-Phases (tasks already created in step 2)

For each sub-phase:
1. TaskGet → verify blockedBy is empty
2. TaskUpdate → in_progress
3. Dispatch subagent with resolved model
4. If gate FAIL → do NOT mark completed → re-dispatch
5. If success → TaskUpdate → completed

### 4. PRE-GATE Agent (Discovery + Pseudocode)

Skills are baked into the agent template. No skill loading needed in prompt.

```
Agent tool:
- subagent_type: "code-foundations:pre-gate-agent"
- model: [resolved_model]
- description: "PRE-GATE for Phase N"
- prompt: |
    Run PRE-GATE for Phase N.
    Plan: docs/plans/<plan>.md
    Output discovery to: docs/building/<plan>-phase-N-discovery.md
    Output pseudocode to: docs/building/<plan>-phase-N-pseudocode.md
```

### 5. Implementation Agent

```
Agent tool:
- subagent_type: "code-foundations:implementation-agent"
- model: [resolved_model]
- description: "Implement Phase N"
- prompt: |
    Read input files:
    - docs/building/<plan>-phase-N-discovery.md
    - docs/building/<plan>-phase-N-pseudocode.md
    Return: DONE or BLOCKED
```

### 6. POST-GATE Agent

Skills baked into the agent template. No skill loading needed in prompt.

```
Agent tool:
- subagent_type: "code-foundations:post-gate-agent"
- model: [resolved_model]
- description: "POST-GATE for Phase N"
- prompt: |
    Review Phase N implementation.
    Plan: docs/plans/<plan>.md
    Discovery: docs/building/<plan>-phase-N-discovery.md
    Pseudocode: docs/building/<plan>-phase-N-pseudocode.md
    Write review to: docs/building/<plan>-phase-N-review.md
```

**STOP. Cannot proceed until post-gate-agent returns PASS.**

### 7. VERIFY (Final Quality Gate)

Load skills for final verification:
```
Skill(code-foundations:cc-code-layout-and-style)
Skill(code-foundations:cc-documentation-quality)
Skill(code-foundations:cc-performance-tuning)
Skill(code-foundations:aposd-optimizing-critical-paths)
```

Run verification checks:
```bash
# Tests
npm test  # or equivalent
npm run test:integration  # if applicable

# Build verification
npm run build  # or equivalent
# Must be clean — no new warnings or errors

# Lint
npm run lint  # if configured
```

All tests must pass, build must be clean before completion.

### 8. Report (Trust Report)

Update plan: `Status: complete`

Output a **trust report** (not a status dashboard):

```markdown
# Build Complete: [plan name]

## Pipeline: N/N phases, M/M sub-phases

### Phase 1: [name] ([model])
- PRE-GATE: Pseudocode covered N tasks, M files
- POST-GATE: PASS (attempt 1)
  - [What reviewer verified/found]
- Commit: [hash]
- Artifacts: docs/building/<plan>-phase-1-*.md

## Gate Summary
| Phase | PRE-GATE | POST-GATE | Retries |
|-------|----------|-----------|---------|
| 1     | PASS     | PASS      | 0       |

## Files Changed
- [file] - [what changed]

## Follow-up
- [Reviewer-flagged items, or "None"]
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
