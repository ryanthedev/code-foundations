---
description: "Runs the scientific debugging method on an active bug — reproduce, locate, hypothesize, fix, verify, search for siblings. Use to chase a failing test, a flaky or intermittent failure, a crash, or any 'why is this broken' investigation, or to audit whether a debugging session was systematic."
argument-hint: "[bug description or failing test]"
---

# Command: debug

Production down or a bug to chase? First two minutes: (1) can you reproduce it — if not, make it reproducible before anything else; (2) what changed recently — commits, deploys, config; (3) what do the logs and stack traces actually say. Most debugging time is finding and understanding the defect, not fixing it, so don't jump to a fix before you can predict when the bug occurs.

For the full method — the STABILIZE → LOCATE → HYPOTHESIZE → EXPERIMENT → FIX → TEST → SEARCH steps, their gate preconditions (run the failing repro before editing; search for sibling defects before declaring done), the common-defect quick check, and the checklists:

`Read(${CLAUDE_PLUGIN_ROOT}/skills/cc-debugging/SKILL.md)`

Before forming a hypothesis, check whether this bug or its pattern has been fixed before in this codebase: `Read(${CLAUDE_PLUGIN_ROOT}/references/pattern-reuse-gate.md)`.

Mode:
- Auditing whether a debugging session followed the method → CHECKER behavior (assess each step against the captured transcript).
- Finding and fixing an active bug → APPLIER behavior (work the steps in order).
