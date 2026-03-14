---
description: "Design-first coding"
---

# /code-foundations:code

**Orchestrate design and implementation agents. You do NOT write code or pseudocode directly.**

---

## STOP — Non-Negotiable Rules

1. **You MUST dispatch `code-foundations:code-agent` for design** — do NOT draft pseudocode yourself
2. **You MUST dispatch `code-foundations:implementation-agent` for implementation** — do NOT edit code yourself
3. **You MUST use `AskUserQuestion` before transitioning from design to implementation** — no skipping the user confirmation gate
4. **You MUST use `TaskCreate` to track progress** — no invisible work

---

## Step 1: Gather Context

Collect information from the user's request:
- What to build
- Target files (if mentioned)
- Constraints (if mentioned)

If the request is vague, use `AskUserQuestion` to clarify before dispatching.

---

## Step 2: Dispatch Code Agent (Design)

```
TaskCreate("Design: [feature]")
```

```python
Task(
    subagent_type="code-foundations:code-agent",
    description="Design: [short description]",
    prompt="""
BUILD: [what to build]
TARGET FILES: [file paths if known, or "Agent should discover"]
CONSTRAINTS: [any constraints from user, or "None specified"]

Search the codebase, design pseudocode with contracts, return design spec.
"""
)
```

---

## Step 3: Present Design to User

When the code-agent returns, present its design to the user.

If the agent returned `NEEDS_INPUT`, relay the question via `AskUserQuestion`.

If the agent returned `DONE`, present the pseudocode and contracts, then ask:

```
AskUserQuestion(
  questions: [{
    header: "Design Review",
    question: "Here's the design. Ready to build?",
    options: [
      {label: "Yes, build it", description: "Dispatch implementation agent"},
      {label: "Needs changes", description: "Tell me what to adjust"},
      {label: "Start over", description: "Re-dispatch code agent with new direction"}
    ]
  }]
)
```

**ENFORCEMENT:** Do NOT proceed to Step 4 without explicit user confirmation via `AskUserQuestion`. "Looks good" in chat is NOT enough — use the tool.

### If User Wants Changes

Re-dispatch code-agent with the feedback:

```python
Task(
    subagent_type="code-foundations:code-agent",
    description="Redesign: [short description]",
    prompt="""
ORIGINAL DESIGN: [paste previous design output]
FEEDBACK: [user's requested changes]

Update the design based on feedback. Return updated pseudocode + contracts.
"""
)
```

Then present again (loop until user confirms).

---

## Step 4: Dispatch Implementation Agent

```
TaskCreate("Implement: [feature]")
```

```python
Task(
    subagent_type="code-foundations:implementation-agent",
    description="Implement: [short description]",
    prompt="""
PSEUDOCODE:
[paste confirmed pseudocode from code-agent]

CONTRACT:
[paste contracts from code-agent]

FILES:
[paste file paths from code-agent's changes summary]

Implement exactly as designed. Run tests after each file.
Return: DONE or BLOCKED with reason.
"""
)
```

---

## Step 5: Verify

After implementation agent returns DONE:

```bash
# Run tests
npm test  # or equivalent

# Build check
npm run build  # or equivalent
```

If tests or build fail, re-dispatch implementation agent with the error.

---

## Step 6: Report

```
AskUserQuestion(
  questions: [{
    header: "Implementation Complete",
    question: "Code is implemented and tests pass. What next?",
    options: [
      {label: "Review the changes", description: "Show what was changed"},
      {label: "Add more tasks", description: "Build something else"},
      {label: "Done", description: "Wrap up"}
    ]
  }]
)
```

---

## Anti-Rationalization Table

| Rationalization | Reality |
|-----------------|---------|
| "This is simple, I'll just edit the file" | You are an ORCHESTRATOR. Dispatch agents. Never edit code directly. |
| "I can draft the pseudocode faster" | Code-agent has design skills loaded. You don't. Dispatch it. |
| "User said 'yeah' so I'll start building" | Use `AskUserQuestion`. Chat confirmation is not a gate. |
| "The design is obvious, skip to implementation" | Design-first is the entire point of this command. No skipping. |
| "I'll implement and test at the same time" | Implementation-agent handles both. One agent, one concern. |
| "TaskCreate is overhead for small changes" | Tasks make work visible. Create them. |

---

## Quick Reference

```
/code-foundations:code [goal]

  1. Gather context
  2. Dispatch code-agent → returns design
  3. Present design → AskUserQuestion("Ready to build?")
     - Changes needed → re-dispatch code-agent (loop)
  4. Dispatch implementation-agent → returns DONE/BLOCKED
  5. Verify (tests + build)
  6. Report to user
```
