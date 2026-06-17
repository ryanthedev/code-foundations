---
description: "Turn a feature request or research doc into a phased, build-ready implementation plan. Use after research, or whenever a change needs decomposition into phases with skills, models, and gates before building."
argument-hint: "[research-doc path or feature description]"
---

# Command: plan

The plan is a contract between plan and build. It specifies WHAT and WHY at the strategic level, with explicit interfaces between phases.

---

## STOP - Read the Input First

`$ARGUMENTS` is either a **research-doc path** or a **feature description**:

- **Path to an existing file** (e.g. `.code-foundations/research/2026-06-11-notifications.md`): `Read` it. Its confirmed requirements seed the problem statement (shared step 3) directly — you clarify only the gaps it left open, not the whole request.
- **Path that does not exist:** say so ("No file at `<path>` — treating it as a feature description"), then fall back to using the text as the feature description.
- **Plain text (not a path):** treat it as the feature description and proceed to classification.
- **Empty:** ask the user what they want to plan.

A research doc carries confirmed intent — do not re-derive it from scratch. Skip straight to filling the gaps.

---

## STOP - Quick Classification First

Before anything else, read the request (from `$ARGUMENTS` or the seeded research doc) and make an instant complexity call:

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

Load `Skill(code-foundations:code-standards)` to generate or update `docs/code-standards.md`. The skill handles staleness detection, scanning, and writing — including the non-git-repo case, so do not assume a git repo here.

### 2. Clarify Intent

Load `Skill(code-foundations:clarify)`. Ask questions via `AskUserQuestion` until answers are decisive and no new open questions remain. Skip if the request is already unambiguous (a research doc usually answers most of this — clarify only its gaps).

**Cap: 5 rounds.** If still unclear at cap, state your remaining assumptions explicitly and ask the user to object. (This cap lives only here — the planning pipeline's DISCOVER does not re-clarify.)

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

1. **Decompose (skeleton).** For each of the 1-2 phases write only: name, one-line goal, matched skills (compare the phase goal against your available-skills register — the internal 19 plus any external plugin skills now in context; each description carries its own when-to-match and sibling-disambiguation (the "not for X (use Y)" clauses); `none -- [reason]` valid; exclude workflow commands), difficulty. If there are 2 phases, add `**Depends on:**` and `**Produces:**` (what phase 1 hands phase 2). Write this skeleton to the plan file.

2. **Skeleton checkpoint.** If 2 phases: `AskUserQuestion` — "Does the split look right? Review it in the preview." Options "Looks right" / "Adjust", **`preview` REQUIRED on both**: the identical split as markdown (each phase's name + goal, and the Produces handoff between them). The preview is the only guaranteed-visible surface — bare labels ask the user to confirm something they cannot see. If 1 phase: skip — nothing to decompose.

3. **Detail each phase**, in order, one short pass each. Start with a one-line reframe — `Phase N: [name]. Consumes: [upstream Produces, or "nothing"]. Must produce: [Produces]. Difficulty: X.` — then load the phase's matched skills if not already loaded (`Skill(code-foundations:<name>)` for this plugin's own, `Skill(<plugin>:<name>)` for external ones — each self-loads its checklists; they inform Edge cases and Done-when), and fill the body in place using this template:

   ```markdown
   ### Phase N: [Name]
   **Skills:** [matched skills, or `none -- [reason]`]
   **Gate:** [Full | Standard | Minimal]

   **Goal:** [One sentence]

   **Scope:**
   - IN: [covered]
   - OUT: [excluded]

   **Edge cases:** [boundaries + error paths -- omit if none]

   **Produces:** [what downstream consumes -- if the seam is code, state the contract (signature/type/route); omit if single phase]

   **Done when:**
   - [ ] DW-N.1: [Verifiable criterion]
   ```

   **Assign `**Gate:**` per phase** — build consumes this field verbatim (see `commands/build.md` resolution order). Mirror its risk rules: **Full** for security/auth/payment work or a multi-file change introducing new cross-phase seams; **Minimal** for a docs-only or config-only change; **Standard** otherwise. Even a Quick 1-2 phase plan sets the field — absent it, build falls back to risk inference, but the planner has the risk context in hand now, so decide it here.

4. **Cross-cut.** Derive the test plan from the done-when items, plus at least one dirty test (error path or boundary from Edge cases) per code-touching phase; record the test coverage level (ask user or default to 100%).

5. **Finalize the file.** The plan was built progressively across steps 1-4; ensure it matches the schema. **Do NOT commit it.**

   This is the **full plan-file schema minus the Medium/Complex-only sections** (Chosen Approach, Rejected Approaches, Assumptions, Decision Log). The canonical schema lives in `Skill: planning` Step 7 — **keep this Quick variant in sync with it.** Each phase body carries `**Gate:**` (see step 3's assignment rule).

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
   [phase bodies from step 3 -- each carries **Gate:**]
   ---
   ## Test Coverage
   **Level:** [from step 4]
   ## Test Plan
   - [ ] [tests from step 4]
   ---
   ## Notes
   - [edge cases, gotchas, open questions surfaced while detailing -- omit if none]
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
   - Gate: every phase has a **Gate:** field (Full/Standard/Minimal) matching its risk

   Output: PASS or FINDINGS with specific fix recommendations.
   ```

   PASS -> proceed. FINDINGS -> fix; **structural fixes (phase boundaries, DW set, Produces seams) -> re-run CHECK**; minor fixes -> proceed.

7. **Present and ask.** Print the plan summary as markdown in conversation — phases with goals, done-when items, test coverage — then `AskUserQuestion`: "Build it, adjust it, or tell me what to do?" **`preview` REQUIRED on every option**: the identical plan summary, so the user can review it inside the dialog even if the print was skipped. The collapsed Write output doesn't count as presentation.

8. **If build:** Suggest default thinking effort, run `/code-foundations:build .code-foundations/plans/<plan>.md`.

That's it. No EXPLORE, no multi-step planning pipeline. Quick track stays compressed — the staging is lightweight at 1-2 phases — and should take under 3 minutes from invocation to handoff.

---

## Standard / Full Track

For Medium and Complex tasks, load the planning pipeline:

`Read(${CLAUDE_PLUGIN_ROOT}/skills/planning/SKILL.md)`

**Pass the confirmed problem statement** from shared step 3. The planning pipeline's DISCOVER step deepens codebase research and may refine the problem statement, but does not redo clarification from scratch.

---

## Chain

- **Receives from:** User request, feature description, user story
- **Chains to:** build (via saved plan file)
