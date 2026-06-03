---
description: "Plan features and implementation"
---

# Skill: plan

The plan is a contract between plan and build. It specifies WHAT and WHY at the strategic level, with explicit interfaces between phases.

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

Load `Skill(code-foundations:code-standards)` to generate or update `docs/code-standards.md`. The skill handles staleness detection, scanning, and writing.

### 2. Clarify Intent

Load `Skill(code-foundations:clarify)`. Ask questions via `AskUserQuestion` until answers are decisive and no new open questions remain. Skip if the request is already unambiguous.

**Cap: 5 rounds.** If still unclear at cap, state your remaining assumptions explicitly and ask the user to object.

### 3. Problem Statement

After scanning and clarifying, write:

- **Problem:** 1-2 sentences — what's wrong or missing
- **Constraints:** non-negotiable boundaries
- **Success criteria:** how we know it's done

Confirm via `AskUserQuestion`: "Does this capture what you want?"

Corrections → update and re-confirm. If the response raises new open questions, re-enter clarify (step 2) on the new gaps before proceeding. This becomes the plan's `## Context` section. **No plan writing begins until the problem statement is confirmed.**

---

## Quick Track (default for simple tasks)

**Problem statement confirmed → decompose → detail → cross-cut → save → check → present → go.** Even Quick is staged, just compressed — don't write all phase bodies in one shot.

1. **Decompose (skeleton).** For each of the 1-2 phases write only: name, one-line goal, matched skills (compare the phase goal against available skill descriptions in the system-reminder; `none -- [reason]` valid; exclude workflow commands), difficulty. If there are 2 phases, add `**Depends on:**` and `**Produces:**` (what phase 1 hands phase 2). Write this skeleton to the plan file.

2. **Skeleton checkpoint.** If 2 phases: `AskUserQuestion` showing the split + handoff — "Looks right" / "Adjust". If 1 phase: skip — nothing to decompose.

3. **Detail each phase**, in order, one short pass each. Start with a one-line reframe — `Phase N: [name]. Consumes: [upstream Produces, or "nothing"]. Must produce: [Produces]. Difficulty: X.` — then load the phase's matched skills if not already loaded (`Skill()` + checklist `Read()`; they inform Edge cases and Done-when), and fill the body in place using this template:

   ```markdown
   ### Phase N: [Name]
   **Skills:** [matched skills, or `none -- [reason]`]

   **Goal:** [One sentence]

   **Scope:**
   - IN: [covered]
   - OUT: [excluded]

   **Edge cases:** [boundaries + error paths -- omit if none]

   **Produces:** [what downstream consumes -- if the seam is code, state the contract (signature/type/route); omit if single phase]

   **Done when:**
   - [ ] DW-N.1: [Verifiable criterion]
   ```

4. **Cross-cut.** Derive the test plan from the done-when items, plus at least one dirty test (error path or boundary from Edge cases) per code-touching phase; record the test coverage level (ask user or default to 100%).

5. **Finalize the file.** The plan was built progressively across steps 1-4; ensure it matches the schema. **Do NOT commit it.**

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
   [phase bodies from step 3]
   ---
   ## Test Coverage
   **Level:** [from step 4]
   ## Test Plan
   - [ ] [tests from step 4]
   ---
   ## Execution Log
   _To be filled during /code-foundations:build_
   ```

6. **Check** — dispatch a sonnet subagent to review the saved plan with fresh eyes:

   ```
   Agent: sonnet, "Review plan"
   Prompt: Review .code-foundations/plans/<plan>.md for structural issues.

   Checklist:
   - Structural: done-when items cover problem statement,
     no scope overlap, union covers full feature, done-when observable + has DW-ID, YAGNI
   - Coherence: no contradictions, phase 1's Produces matches what phase 2 consumes (if 2 phases),
     code seams in Produces stated as contracts (signature/type/route)
   - Tests: test plan covers DW items + at least one dirty test per code-touching phase
   - Skills: every phase has Skills field, skills match work type, skills actually available

   Output: PASS or FINDINGS with specific fix recommendations.
   ```

   PASS -> proceed. FINDINGS -> fix issues, then proceed.

7. **Present and ask** via `AskUserQuestion`: "Here's the plan. Build it, adjust it, or tell me what to do?"

8. **If build:** Suggest default thinking effort, run `/code-foundations:build .code-foundations/plans/<plan>.md`.

That's it. No EXPLORE, no 10-task pipeline. Quick track stays compressed — the staging is lightweight at 1-2 phases — and should take under 3 minutes from invocation to handoff.

---

## Standard / Full Track

For Medium and Complex tasks, load the planning pipeline:

`Skill(code-foundations:planning)`

**Pass the confirmed problem statement** from shared step 3. The planning pipeline's DISCOVER step deepens codebase research and may refine the problem statement, but does not redo clarification from scratch.

---

## Chain

- **Receives from:** User request, feature description, user story
- **Chains to:** build (via saved plan file)
