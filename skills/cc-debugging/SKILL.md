---
name: cc-debugging
description: "Use when investigating a bug, diagnosing a failure, debugging a flaky test, or tracing the root cause of unexpected behavior. Triggers on: debugging, bug, defect, broken test, flaky test, intermittent failure, root cause, can't reproduce, weird behavior, race condition."
---

# Skill: cc-debugging

> 90% of debugging time is finding and understanding the defect. The fix is usually obvious once you understand it.

Never guess. Never apply random changes. Every action should be testing a hypothesis.

## Scientific Debugging Method

```
STABILIZE → LOCATE → HYPOTHESIZE → EXPERIMENT → FIX → TEST → SEARCH
```

### Step 1: STABILIZE

Get a reliable reproduction case — you cannot debug what you cannot reproduce.

- Reduce to the smallest case that still fails
- If intermittent: usually initialization errors, timing issues, or dangling pointers
- Record the exact conditions: inputs, environment, order of operations

### Step 2: LOCATE

Narrow the suspicious region before forming a hypothesis.

- Binary search: disable code sections until failure disappears → bug is in what you removed
- Check recently changed code first (defects cluster around changes)
- Check modules with prior defect history (defects cluster by module too)
- Look for patterns: specific data? specific user? specific environment?

### Step 3: HYPOTHESIZE

Form a specific, testable hypothesis — not "the bug is somewhere in module X."

- Good: "The counter isn't reset between requests because X shares state with Y"
- Use all available data: logs, stack traces, variable values, test outputs
- One hypothesis at a time; rank competing candidates
- Brainstorm alternatives before committing — avoid confirmation bias

### Step 4: EXPERIMENT

Design a test that will **disprove** your hypothesis, not confirm it.

- Add targeted logging or assertions at the suspected site
- Write a failing test that would pass if your hypothesis is correct
- Do NOT change production code yet — observe first
- Record results; update or discard hypothesis based on what you see

### Step 5: FIX

Fix the root cause, not the symptom.

- Understand the program vicinity (hundreds of lines, not just the bug line)
- Confirm diagnosis by ruling out competing hypotheses
- Make one change at a time
- Save the original source before modifying

### Step 6: TEST

Verify the fix actually works.

- Triangulate: multiple different test cases, not just the original repro
- Add a regression test that would have caught this bug
- Run the full test suite

### Step 7: SEARCH

Defects cluster — if this bug existed, similar ones likely exist nearby.

- Search for the same pattern elsewhere in the codebase
- Check the module's other methods for similar logic
- Check other code from the same author or era

---

## Red Flags

| Red Flag | What to do instead |
|---|---|
| **Shotgun debugging** — random changes until something works | Form a hypothesis first |
| **Symptom fixing** — `if (client == 45) sum += 3.45` workaround | Find the root cause |
| **Superstitious debugging** — blaming the compiler, OS, or "demon machines" | Assume it's your fault |
| **Panic debugging** — rushing, multiple changes at once | Take a break; one change at a time |
| **No regression test** — fixed it, moved on | Always add the test |
| **Circular debugging** — revisiting same code with no new data | Keep a notepad; generate new hypotheses |

---

## Common Defects Quick Check

Rule these out in 2 minutes before deep investigation:

- Off-by-one: loop bounds (`<` vs `<=`), array index vs length
- Null / undefined dereference before checking
- Race condition (intermittent, timing-dependent)
- Uninitialized variable
- Incorrect operator precedence (add explicit parentheses)
- Floating-point equality (`==` instead of epsilon comparison)
- Resource leak: file handle, connection, or lock not released on error path
- Logic inversion: wrong branch taken

---

## Time Limits

| Phase | Limit | Escalation |
|---|---|---|
| Quick-and-dirty | 15–30 min | Switch to systematic method |
| Single hypothesis | 30–60 min | Generate fresh hypotheses |
| Systematic debugging | 2–4 hours | Take break; talk to a colleague |
| Same bug, multiple days | — | Consider brute-force rewrite |

**Confessional debugging:** Explain the problem out loud to someone (or a rubber duck). Articulation frequently reveals the bug before they respond.

---

## Full Checklists

The complete 99-item checklist — finding defects, fixing defects, syntax errors, brute-force techniques, common defect patterns: `Read skills/cc-debugging/checklists.md`.

---

## Chain

| After | Next |
|---|---|
| Root cause found | Fix + add regression test (Step 6–7 above) |
| Defect is in untested legacy code | welc-legacy-code (get it under test first) |
| Fix requires structural refactoring | cc-refactoring-guidance |
