---
description: "Write, build, implement, or add code. Use when asked to code something — from a one-line fix to a multi-file feature. Classifies complexity, designs when needed, implements with TDD, reviews before done. Triggers on 'write', 'build', 'implement', 'add', 'create', 'code this'."
---

# /code-foundations:code

**Orchestrate design and implementation. You do NOT write code directly — you dispatch agents.**

---

## STOP — Classify First

Read the user's request and classify immediately:

| Signal | Track | What happens |
|--------|-------|-------------|
| 1-2 files, clear ask, no design decisions | **Quick** | Straight to implement (TDD) |
| 3+ files, needs interface decisions, new patterns | **Standard** | Design first, then implement |
| Architectural, cross-cutting, multi-system | **Redirect** | → `/code-foundations:whiteboarding` |

**Default to Quick.** Only upgrade if design decisions genuinely need upfront resolution.

State your classification:
> "This is a **[Quick/Standard]** task — [1-sentence why]."

---

## Quick Track

```
IMPLEMENT → REVIEW → REPORT
```

Skip design. Dispatch build-agent directly with TDD emphasis.

### 1. Dispatch Implementation

```
TaskCreate("Implement: [feature]", activeForm="Implementing [feature]")
```

```python
Agent(
    subagent_type="code-foundations:build-agent",
    description="Implement: [short description]",
    prompt="""
This is a minimal gate build — no prior pseudocode exists.

BUILD: [what to build — from user's request]
TARGET FILES: [file paths if known, or "Discover from codebase"]
CONSTRAINTS: [any constraints, or "None"]

## TDD Required

For EVERY change:
1. Write a failing test first (RED)
2. Implement minimal code to make it pass (GREEN)
3. Run tests to confirm
4. Commit

Do NOT write implementation code before its test exists.
If no test framework is set up, set one up first.

## When Done

Run the full test suite. All tests must pass.
Return: DONE | BLOCKED with reason.
"""
)
```

### 2. Review

After build-agent returns DONE:

```bash
# Run full test suite
[test command for this project]

# Type check / lint if available
[typecheck/lint command]
```

If anything fails, re-dispatch build-agent with the errors.

If everything passes, do a quick eyeball:
- Read the diff (`git diff HEAD~1` or similar)
- Check: does the change match what was asked? Any obvious issues?

### 3. Report

```
AskUserQuestion(
  questions: [{
    header: "Done",
    question: "Implementation complete, tests pass. What next?",
    options: [
      {label: "Show the changes", description: "Display what was modified"},
      {label: "Done", description: "Wrap up"}
    ]
  }]
)
```

---

## Standard Track

```
DESIGN → USER GATE → IMPLEMENT → REVIEW → REPORT
```

### 1. Dispatch Design Agent

```
TaskCreate("Design: [feature]", activeForm="Designing [feature]")
```

```python
Agent(
    subagent_type="code-foundations:code-agent",
    description="Design: [short description]",
    prompt="""
BUILD: [what to build]
TARGET FILES: [file paths if known, or "Discover from codebase"]
CONSTRAINTS: [any constraints, or "None"]

Search the codebase, design pseudocode with contracts,
persist design to docs/code/<topic>-design.md, return summary.
"""
)
```

### 2. Present Design + User Gate

When code-agent returns, present its design summary.

If `NEEDS_INPUT`: relay the question via `AskUserQuestion`.

If `DONE`:

```
AskUserQuestion(
  questions: [{
    header: "Design",
    question: "Design saved to [path]. Ready to build?",
    options: [
      {label: "Yes, build it", description: "Dispatch implementation with TDD"},
      {label: "Needs changes", description: "Tell me what to adjust"},
      {label: "Start over", description: "Re-dispatch with new direction"}
    ]
  }]
)
```

**ENFORCEMENT:** Do NOT proceed without explicit user confirmation via `AskUserQuestion`.

If changes needed: re-dispatch code-agent with feedback + path to existing design file.

### 3. Dispatch Implementation

```
TaskCreate("Implement: [feature]", activeForm="Implementing [feature]")
```

```python
Agent(
    subagent_type="code-foundations:build-agent",
    description="Implement: [short description]",
    prompt="""
This is a minimal gate build — pseudocode already exists.

DESIGN FILE: docs/code/<topic>-design.md
Read the design file for pseudocode and contracts.

## TDD Required

For EVERY change:
1. Write a failing test first (RED)
2. Implement minimal code to make it pass (GREEN)
3. Run tests to confirm
4. Commit

Do NOT write implementation code before its test exists.

## Spec Compliance

Implement exactly as designed. If the design is wrong or unclear:
- Return BLOCKED with what's ambiguous
- Do NOT deviate silently

Return: DONE | BLOCKED with reason.
"""
)
```

### 4. Review

After build-agent returns DONE:

```bash
# Run full test suite
[test command]

# Type check / lint
[typecheck/lint command]
```

Then **spec compliance check** — read the design file and the diff side by side:
- Does the implementation match the pseudocode?
- Are all contracts satisfied?
- Any additions not in the design? (YAGNI violation)
- Any design items missing from the implementation?

If issues found: re-dispatch build-agent with specific fixes.

### 5. Report

```
AskUserQuestion(
  questions: [{
    header: "Done",
    question: "Implemented and reviewed against design. Tests pass. What next?",
    options: [
      {label: "Show the changes", description: "Display diff + design compliance"},
      {label: "Done", description: "Wrap up"}
    ]
  }]
)
```

---

## Quick Reference

```
/code [goal]

  1. Classify → Quick or Standard

  Quick:
    → build-agent (TDD) → review → report

  Standard:
    → code-agent (design, persisted) → user gate
    → build-agent (TDD, from design) → spec review → report
```
