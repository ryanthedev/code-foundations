---
description: "Turn a feature request or research doc into a phased, build-ready implementation plan. Use after research, or whenever a change needs decomposition into phases with skills, models, and gates before building."
argument-hint: "[research-doc path or feature description]"
---

# Command: plan

The plan is a contract between plan and build. It specifies WHAT and WHY at the strategic level, with explicit interfaces between phases.

---

## Read the Input First

`$ARGUMENTS` is either a **research-doc path** or a **feature description**:

- **Path to an existing file** (e.g. `.code-foundations/research/2026-06-11-notifications.md`): `Read` it. Its confirmed requirements seed the problem statement (shared step 3) directly — you clarify only the gaps it left open, not the whole request.
- **Path that does not exist:** say so ("No file at `<path>` — treating it as a feature description"), then fall back to using the text as the feature description.
- **Plain text (not a path):** treat it as the feature description and proceed to classification.
- **Empty:** ask the user what they want to plan.

A research doc carries confirmed intent — do not re-derive it from scratch. Skip straight to filling the gaps.

---

## Quick Classification

Read the request (from `$ARGUMENTS` or the seeded research doc) and make an instant complexity call before any other work — the track determines everything downstream:

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

Render the statement as markdown in conversation and end the turn asking "Does this capture what you want?" — the user replies in their own words. Content confirmations happen in conversation, not in a dialog: the conversation is the only surface that renders the full statement (dialog previews truncate, and the user can't correct nuance through option buttons).

Corrections → update and re-confirm. If the response raises new open questions, re-enter clarify (step 2) on the new gaps before proceeding. This becomes the plan's `## Context` section. **No plan writing begins until the problem statement is confirmed.**

---

## Quick Track (default for simple tasks)

**Problem statement confirmed → decompose → detail → cross-cut → save → check → present → go.** Even Quick is staged, just compressed — don't write all phase bodies in one shot.

1. **Decompose (skeleton).** For each of the 1-2 phases write only: name, one-line goal, matched skills (compare the phase goal against your available-skills register — the 18 matchable internal skills plus any external plugin skills now in context; each description carries its own when-to-match and sibling-disambiguation (the "not for X (use Y)" clauses); `none -- [reason]` valid; exclude workflow commands), difficulty. Every phase gets `**Depends on:**` (`none` or `Phase N`); with 2 phases, add `**Produces:**` (what phase 1 hands phase 2). Hold the skeleton in conversation — the file is written in step 3 after the split is confirmed.

2. **Skeleton checkpoint.** If 2 phases: render the split as markdown in conversation (each phase's name + goal, the Produces handoff, and the dependency between them) and end the turn asking "Does the split look right?" — the user replies free-form. The skeleton must be the final message of that turn, with no tool calls after it: the conversation is the only surface that renders it in full, and nothing is written to disk yet, so there is nothing to chain into. If 1 phase: skip — nothing to decompose.

3. **Detail each phase**, in order, one short pass each. Start with a one-line reframe — `Phase N: [name]. Consumes: [upstream Produces, or "nothing"]. Must produce: [Produces]. Difficulty: X.` — then load the phase's matched skills if not already loaded (`Skill(code-foundations:<name>)` for this plugin's own, `Skill(<plugin>:<name>)` for external ones — each self-loads its checklists; they inform Edge cases and Done-when), and fill the body in place using this template:

   ```markdown
   ### Phase N: [Name]
   **Skills:** [matched skills, or `none -- [reason]`]
   **Model:** [fable | sonnet | haiku]
   **Gate:** [Full | Standard | Minimal]
   **Depends on:** [none | Phase N]
   **File scope:** [globs the phase may touch, e.g. src/auth/**, tests/auth/** -- omit only if unknowable]

   **Goal:** [One sentence]

   **Scope:**
   - IN: [covered]
   - OUT: [excluded]

   **Edge cases:** [boundaries + error paths -- omit if none]

   **Produces:** [what downstream consumes -- if the seam is code, state the contract (signature/type/route); omit if single phase]
   **Security-sensitive:** [yes -- only if the phase touches auth, crypto, secrets, deserialization, or untrusted input; omit otherwise]
   **Rollback:** [required for destructive/irreversible actions: compensating action, or "point of no return -- [mitigation]"; omit otherwise]

   **Done when:**
   - [ ] DW-N.1: [Verifiable criterion]
   ```

   **Assign `**Gate:**` per phase** — build consumes this field verbatim (see `commands/build.md` resolution order) and stops on a plan that omits it, so always set it. Risk rules: **Full** for security/auth/payment work or a multi-file change introducing new cross-phase seams; **Minimal** for a docs-only or config-only change; **Standard** otherwise. A phase doing auth/crypto/secrets/deserialization/untrusted-input work also gets `**Security-sensitive:** yes` (triggers the 3-sample fable REVIEW during build) and, if it performs destructive or irreversible actions, a `**Rollback:**` line (compensating action, or "point of no return -- [mitigation]").

   **Assign `**Model:**` per phase** — **sonnet** is the default (Sonnet 5: fast, cheap, handles well-specified implementation work); **haiku** for purely mechanical phases (config edits, renames, doc moves); **fable** for judgment-heavy phases (novel architecture, security-sensitive design, cross-cutting refactors). **opus** stays a valid override — use it when fable is unavailable or when the user asks for it. Build resolves the REVIEW model by downgrading one tier (fable→sonnet, opus→sonnet, sonnet→haiku).

   **`**Depends on:**` and `**File scope:**`** feed build's wave derivation: phases with no dependency between them and disjoint file scopes run their BUILD agents in parallel. A phase without `File scope` never runs in parallel — omitting it is the opt-out.

4. **Cross-cut.** Derive the test plan from the done-when items, plus at least one dirty test (error path or boundary from Edge cases) per code-touching phase; record the test coverage level (ask user or default to 100%).

5. **Finalize the file.** The plan was built progressively across steps 1-4; ensure it matches the schema. **Do NOT commit it.**

   This is the **full plan-file schema minus the Medium/Complex-only sections** (Chosen Approach, Rejected Approaches, Assumptions, Decision Log). The canonical schema lives in `Skill: planning` Step 7 — **keep this Quick variant in sync with it.** Each phase body carries `**Model:**`, `**Gate:**`, `**Depends on:**`, and `**File scope:**` (see step 3's assignment rules).

   ```markdown
   # Plan: [Topic]
   **Created:** YYYY-MM-DD
   **Status:** draft
   **Complexity:** simple
   ---
   ## Context
   [Problem statement from shared step 3]
   ## Constraints
   - [constraints from shared step 3]
   ---
   ## Implementation Phases
   [phase bodies from step 3 -- each carries **Model:**, **Gate:**, **Depends on:**, **File scope:**]
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

6. **Check** — dispatch a fable subagent to review the saved plan with fresh eyes (the plan is the highest-leverage artifact in the pipeline; one fable pass here is cheap insurance):

   ```
   Agent: fable, "Review plan"
   Prompt: Review .code-foundations/plans/<plan>.md for structural issues.

   Checklist:
   - Structural: done-when items cover problem statement,
     no scope overlap, union covers full feature, done-when observable + has DW-ID, YAGNI
   - Coherence: no contradictions, phase 1's Produces matches what phase 2 consumes (if 2 phases),
     code seams in Produces stated as contracts (signature/type/route)
   - Tests: test plan covers DW items + at least one dirty test per code-touching phase
   - Skills: every phase has Skills field, skills match work type, skills actually available
   - Model: every phase has a **Model:** field (fable/sonnet/haiku; opus only as an explicit
     user-requested override) matching its difficulty
   - Gate: every phase has a **Gate:** field (Full/Standard/Minimal) matching its risk;
     auth/crypto/secrets/deserialization/untrusted-input phases carry **Security-sensitive:** yes;
     destructive/irreversible phases carry **Rollback:**
   - Dependencies: every phase has **Depends on:** and referenced phases exist; a phase
     consuming another's Produces depends on it; phases declared independent have
     disjoint **File scope:** globs
   - Header: **Status:** is present and reads `draft` (step 7 flips it to `ready`)

   Output: PASS or FINDINGS with specific fix recommendations.
   ```

   PASS -> proceed. FINDINGS -> fix; **structural fixes (phase boundaries, DW set, Produces seams) -> re-run CHECK**; minor fixes -> proceed.

7. **Present and ask.** End the turn with the full plan summary rendered as markdown in conversation — every phase with its goal, model, gate, dependencies, done-when items, and the test coverage — closing with "Build it, adjust it, or tell me what to do?" The user replies in their own words. The summary must be the turn's **final message, with no tool calls after it**: the conversation is the only surface that renders a multi-phase plan in full (dialog previews truncate it, and the collapsed Write output doesn't count as presentation). Parse the reply — "build it" and equivalents proceed to step 8; "tell me what to do" is also a confirmation (flip the status, then give numbered manual steps instead of running build); anything else is an adjustment or a question, handle it and re-present.

   **On any confirmation, flip `**Status:** draft` → `**Status:** ready` in the plan file.** Build refuses to execute a plan whose Status isn't `ready`, so the confirmed presentation is a structural gate, not a convention — a plan the user never saw cannot build.

8. **If build:** Suggest the effort level for the build run — **low** if the plan is all-serial, **default** if any phase carries `**File scope:**` (wave-eligible; the orchestrator keeps real judgment there) — then run `/code-foundations:build .code-foundations/plans/<plan>.md`.

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
