---
description: "Design-first coding. Pseudocode → validate with user → implement with subagents. Use when you know what to build but want to collaborate on design before code exists."
argument-hint: "[what to build]"
allowed-tools: ["Bash", "Glob", "Grep", "Read", "Edit", "Write", "Task", "Skill", "TaskCreate", "TaskUpdate", "TaskList", "AskUserQuestion"]
---

# Code Mode

**Design Loop → Implementation Loop**

---

## STOP - Load Skills First

Before coding, load your skill lenses using the Skill tool:
1. `Skill(code-foundations:cc-pseudocode-programming)` - design before code
2. `Skill(code-foundations:cc-defensive-programming)` - contracts and error handling

---

## Phase 1: DESIGN LOOP

Collaborate on design until user confirms. Use subagents and tasklist throughout.

### Start

```
User: /code-foundations:code [what to build]

1. Create initial task: "Design [feature]"
2. Draft pseudocode (flow + contracts)
3. Present to user
4. Iterate based on feedback
5. When design feels complete → ask "Ready to build?"
```

### The Loop

```
┌─────────────────────────────────────────────────────────────┐
│  PSEUDOCODE    Draft flow and contracts                     │
│       ↓                                                     │
│  EXPLORE       Dispatch subagent if research needed         │
│       ↓                                                     │
│  TASKLIST      Track decisions + open questions             │
│       ↓                                                     │
│  USER INPUT    Wait for feedback                            │
│       ↓                                                     │
│  REFINE        Update pseudocode + tasklist                 │
│       ↓                                                     │
│  ↺ REPEAT      When complete → ask user                     │
└─────────────────────────────────────────────────────────────┘
```

### Pseudocode Format

```
functionName(params) → ReturnType
  1. [step] → [result]
  2. [step] → [result]
  3. return [value]

Contract:
  Input: [types and constraints]
  Output: [types and guarantees]
  Errors: [what can go wrong]

Where: [file path]
Used by: [callers]
```

### When to Dispatch Explore Subagent

User asks about:
- "What about X?" → Research patterns, packages, prior art
- "How does Y work?" → Explore codebase
- "Is there an existing Z?" → Search for similar implementations

```
Task tool:
- subagent_type: "Explore"
- description: "Research [topic]"
- prompt: |
    Research [specific question].

    Search for:
    1. Existing patterns in codebase
    2. Related implementations
    3. Packages/libraries if applicable

    Return: Summary of findings + recommendation
```

Update tasklist with findings. Update pseudocode if needed.

### Tasklist During Design

Track everything:
- `TaskCreate`: "Design [feature]" at start
- `TaskUpdate`: When design evolves
- `TaskCreate`: For research subtasks
- `TaskUpdate`: Complete research tasks with findings

### Transition to Build

When design feels complete (no open questions, pseudocode covers all cases):

```
AskUserQuestion:
  question: "Design looks complete. Ready to build?"
  options:
    - "Yes, let's build"
    - "Need to add/change something"
```

Only proceed to Phase 2 on explicit confirmation.

---

## Phase 2: IMPLEMENTATION LOOP

Execute confirmed design with subagents. Tasklist continues from design.

### Start

```
1. Convert pseudocode to implementation tasks
2. Create tasks: Implement, Unit tests, Integration tests
3. Execute tasks in order (or as user directs)
```

### The Loop

```
┌─────────────────────────────────────────────────────────────┐
│  IMPLEMENT     Dispatch subagent with pseudocode            │
│       ↓                                                     │
│  TEST          Unit tests → integration tests               │
│       ↓                                                     │
│  COMMIT        Checkpoint with passing tests                │
│       ↓                                                     │
│  ↺ NEXT TASK   User picks priority                          │
└─────────────────────────────────────────────────────────────┘
```

### Implementation Subagent

```
Task tool:
- subagent_type: "code-foundations:implementation-agent"
- description: "Implement [task]"
- prompt: |
    Implement this design:

    PSEUDOCODE:
    [paste confirmed pseudocode]

    CONTRACT:
    [paste contract]

    FILE: [target file path]

    Follow the pseudocode exactly. Match the contract.
    Run tests after implementation.

    Return: DONE or BLOCKED with reason
```

### Test Subagent

```
Task tool:
- subagent_type: "general-purpose"
- model: "haiku"
- description: "Unit tests for [feature]"
- prompt: |
    Write unit tests for:

    CONTRACT:
    [paste contract from design]

    Test the CONTRACT, not implementation details.
    Cover:
    - Happy path
    - Edge cases from pseudocode
    - Error conditions

    FILE: [test file path]

    Return: DONE with test count
```

### Commit Checkpoint

After tests pass:

```bash
git add [files]
git commit -m "[type]: [description]"
```

Update tasklist: mark completed, show remaining.

### User Drives Priority

After each commit, show tasklist and ask:

```
Current tasks:
✅ #1 Design [feature]
✅ #2 Implement [function]
✅ #3 Unit tests
◻ #4 Integration tests
◻ #5 [new task added mid-session]

What's next?
```

User can:
- Pick a task: "do #4"
- Reorder: "do #5 first"
- Add tasks: "also need to handle X"
- Stop: "that's enough for now"

---

## Adding Tasks Mid-Session

User can add requirements anytime:

**During Design:**
```
User: "also need to handle async validation"

→ TaskCreate: "Add async validation to design"
→ Update pseudocode
→ Continue design loop
```

**During Implementation:**
```
User: "we should also add rate limiting"

→ TaskCreate: "Implement rate limiting"
→ Add to tasklist
→ Continue current task or switch
```

---

## Escape Hatches

| Situation | Action |
|-----------|--------|
| Design keeps changing | "Should we do `/code-foundations:whiteboarding` for this?" |
| Technical uncertainty | "Should we `/code-foundations:prototype` first?" |
| Scope exploding | "This is getting big. Want to `/code-foundations:whiteboarding`?" |
| User wants to stop | Complete current task, commit, show summary |

---

## Anti-Rationalization Table

| Rationalization | Reality |
|-----------------|---------|
| "I'll just start coding" | Design loop exists for a reason. Pseudocode first. |
| "User will confirm later" | Ask explicitly. "Ready to build?" is required. |
| "This is simple, skip design" | Simple designs still need contracts validated |
| "I'll figure out the contract during implementation" | Contract IS the design. Lock it first. |
| "Tasklist is overhead" | Tasklist enables user to drive priority |
| "I can implement without subagent" | Subagent has fresh context. Use it. |
| "Tests can wait" | Tests validate the contract. Write them. |
| "User is waiting, skip the question" | User drives priority. Always ask "what's next?" |
| "Design is close enough" | "Close enough" means open questions. Resolve them. |

---

## Quick Reference

```
/code-foundations:code [goal]     → Start design loop
"what about X?"                   → Triggers explore subagent
"ready to build" / "let's build"  → Transition to implementation
"do #N"                           → Execute specific task
"also add X"                      → Add task mid-session
"that's enough"                   → Stop, commit, summary
/code-foundations:whiteboarding   → Escape if scope explodes
```
