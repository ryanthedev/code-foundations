---
description: "Brainstorm and plan features"
---

# Skill: whiteboarding

The plan is a contract between whiteboarding and building. It specifies WHAT and WHY at the strategic level, with explicit interfaces between phases.

---

## STOP - Quick Classification First

Before anything else, read the user's request and make an instant complexity call:

| Signal in user's request | Track |
|---|---|
| Small, focused ask. One thing to change. User knows what they want even if they don't know the implementation. | **Quick** |
| Feature request, multiple concerns, "how should we", needs approach comparison | **Standard** (Medium) |
| "redesign", "migrate", cross-cutting, high uncertainty, multi-system | **Full** (Complex) |

**Default to Quick.** Only upgrade if the signals clearly demand it. Under-planning a simple task is cheap to fix. Over-planning it wastes everyone's time.

---

## Before Planning (All Tracks)

These steps run regardless of track. They produce the confirmed problem statement that anchors all downstream work.

### 1. Codebase Scan

Check for `docs/code-standards.md` (or legacy `docs/code-patterns.md`).
- **If exists:** Read it, check staleness via `git rev-list <commit-ref>..HEAD --count`. 0 commits -> trust it. 1-20 -> spot-check recent diffs, update if changed. 20+ -> regenerate.
- **If missing:** Full codebase search, generate `docs/code-standards.md` with sections: Architecture, Naming, Imports, Error Handling, File Organization, Testing, Technology Decisions, Forbidden Patterns, Similar Implementations. Include `<!-- base-commit: [HEAD] -->` and `<!-- generated: [date] -->`.
- Grep for similar patterns. 30 seconds, not 5 minutes.

### 2. Clarify Intent

Ask 1-2 questions max via `AskUserQuestion` -- only if genuinely ambiguous. Load `Skill(code-foundations:clarify)` to classify what's unclear (fault type + ambiguity direction) and generate targeted questions. If the request is already clear, skip to step 3.

### 3. Problem Statement

After scanning and clarifying, write:

- **Problem:** 1-2 sentences — what's wrong or missing
- **Constraints:** non-negotiable boundaries
- **Success criteria:** how we know it's done

Confirm via `AskUserQuestion`: "Does this capture what you want?"

Corrections → update and re-confirm. This becomes the plan's `## Context` section. **No plan writing begins until the problem statement is confirmed.**

---

## Quick Track (default for simple tasks)

**Problem statement confirmed → plan → check → present → go.**

1. **Write the plan inline** -- 1-2 phases, 50-75 words each. Use this template per phase:

   ```markdown
   ### Phase N: [Name]
   **Skills:** [matched skills, or `none -- [reason]`]

   **Goal:** [One sentence]

   **Scope:**
   - IN: [covered]
   - OUT: [excluded]

   **Done when:**
   - [ ] DW-N.1: [Verifiable criterion]
   ```

2. **Save** to `docs/plans/YYYY-MM-DD-<topic>.md` wrapped in plan file format:

   ```markdown
   # Plan: [Topic]
   **Created:** YYYY-MM-DD
   **Status:** ready
   **Complexity:** simple
   ---
   ## Context
   [Problem statement from shared step 3]
   ## Constraints
   - [constraints from shared step 3]
   ---
   ## Implementation Phases
   [phases from step 3]
   ---
   ## Test Coverage
   **Level:** [ask user or default to 100%]
   ## Test Plan
   - [ ] [specific tests]
   ---
   ## Execution Log
   _To be filled during /code-foundations:building_
   ```

   Do NOT commit the plan file.

3. **Check** — dispatch a sonnet subagent to review the saved plan with fresh eyes:

   ```
   Agent: sonnet, "Review whiteboarding plan"
   Prompt: Review docs/plans/<plan>.md for structural issues.

   Checklist:
   - Structural: done-when items cover problem statement,
     no scope overlap, union covers full feature, done-when observable + has DW-ID, YAGNI
   - Coherence: no contradictions, Phase N output matches N+1 input
   - Skills: every phase has Skills field, skills match work type, skills actually available

   Output: PASS or FINDINGS with specific fix recommendations.
   ```

   PASS -> proceed. FINDINGS -> fix issues, then proceed.

4. **Present and ask** via `AskUserQuestion`: "Here's the plan. Build it, adjust it, or tell me what to do?"

5. **If building:** Suggest default thinking effort, run `/code-foundations:building docs/plans/<plan>.md`.

That's it. No EXPLORE, no 10-task pipeline. Quick track should take under 3 minutes from invocation to handoff.

---

## Standard / Full Track

For Medium and Complex tasks, load the planning pipeline:

`Skill(code-foundations:whiteboarding-planning)`

**Pass the confirmed problem statement** from shared step 3. The planning pipeline's DISCOVER step deepens codebase research and may refine the problem statement, but does not redo clarification from scratch.

---

## Chain

- **Receives from:** User request, feature description, user story
- **Chains to:** building (via saved plan file)
