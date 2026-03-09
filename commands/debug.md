---
description: "Debug loop: predict → log → run → resolve or narrow. Tasks keep you on track."
argument-hint: "[error message / bug description / 'test X is failing']"
allowed-tools: ["Bash", "Glob", "Grep", "Read", "Edit", "Write", "Task", "Skill", "AskUserQuestion", "TaskCreate", "TaskUpdate", "TaskList"]
---

# /code-foundations:debug

**Orchestrate a debug agent to investigate and fix bugs systematically.**

---

## Step 1: Gather Context

Collect information before dispatching:

1. **Bug description** from the user's argument
2. **Reproduction steps** if provided
3. **Relevant file paths** — search the codebase if not provided:

```
Grep for error messages, function names, or symptoms mentioned by the user.
Note the top 3-5 relevant files.
```

---

## Step 2: Create Tracking Task

```
TaskCreate("Debug: [bug description]")
```

---

## Step 3: Dispatch Debug Agent

```python
Task(
    subagent_type="code-foundations:debug-agent",
    description="Debug: [short description]",
    prompt="""
BUG: [bug description]
REPRODUCTION: [steps if known, or "Not provided — agent should reproduce"]
RELEVANT FILES: [file paths found in Step 1]

Investigate, find root cause, fix, and verify.
Return your findings in the debug output format.
"""
)
```

---

## Step 4: Review Results

When the agent returns, check its output:

| Status | Action |
|--------|--------|
| **DONE** | Show root cause, fix, and hypothesis trail to user |
| **BLOCKED** | Show what was narrowed, ask user for missing context, re-dispatch |

### If DONE

Display the agent's summary and ask:

```
AskUserQuestion(
  questions: [{
    header: "Debug Complete",
    question: "The debug agent found and fixed the issue. What next?",
    options: [
      {label: "Show full hypothesis trail", description: "See the investigation steps"},
      {label: "Review the fix", description: "Look at the code changes"},
      {label: "Done", description: "Accept and move on"}
    ]
  }]
)
```

### If BLOCKED

Show what the agent found and ask:

```
AskUserQuestion(
  questions: [{
    header: "Debug Blocked",
    question: "[Agent's blocking reason]. Can you provide more context?",
    options: [
      {label: "Provide more info", description: "I can help narrow it down"},
      {label: "Re-dispatch with different approach", description: "Try again from a different angle"},
      {label: "Debug manually", description: "I'll take over from here"}
    ]
  }]
)
```

If user provides more info, re-dispatch the agent with the additional context.

---

## Quick Reference

```
/code-foundations:debug [issue]

  1. Gather context (search for relevant files)
  2. TaskCreate tracking task
  3. Dispatch debug-agent (autonomous investigate → fix → verify)
  4. Review results
     - DONE → show summary
     - BLOCKED → ask user, re-dispatch
```
