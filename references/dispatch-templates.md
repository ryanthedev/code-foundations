# Dispatch Templates

Subagent dispatch prompts used by the orchestrator (`commands/build.md`) when dispatching the build and post-gate agents. Templates are referenced by section header (e.g., `§ FULL_BUILD`) from the orchestrator and substituted with phase-specific values at dispatch time.

Keeping these here instead of inline in `build.md`:
- Keeps the orchestrator's hot path lean (~520 lines vs ~905)
- Lets templates evolve without touching orchestration logic
- Makes the dispatch surface a single auditable file

---

## § FULL_BUILD

Use for **Full gate** and **Standard gate** phases. The build agent runs discovery + design + TDD in one pass.

```
Agent tool:
- subagent_type: "code-foundations:build-agent"
- model: [from plan's **Model:** field, or omit if not set]
- description: "BUILD Phase N"
- prompt: |
    Build Phase N of the build plan. This is a two-part task:
    1. Discovery + Design — scope the phase work, identify gaps vs plan, make design decisions, map DW items to test cases
    2. TDD Implementation — write failing tests from DW items, then implement to make them pass (red-green cycle)

    Write discovery file before implementing.

    ## Plan Context
    [paste the Context section from the plan file — the 2-3 sentence problem statement]

    ## Progress
    [For Phase 1: "This is the first phase."]
    [For Phase N>1: "Completed: Phase 1: [name] — [1 sentence summary from execution log]. Phase 2: ..."]
    Current: Phase N of M

    ## Phase N: [name]
    [paste phase description and file list from plan]

    ## Done-When Items (DW-IDs)
    These are the acceptance criteria from the plan. Each DW item must
    have corresponding test(s) (e.g., `test_DW_1_1_creates_user`).
    Any DW item without a test is a visible gap.
    If any item cannot be met, return UPDATE_PLAN.
    [paste ALL DW items from the plan phase, verbatim:]
    - [ ] DW-N.1: [done-when item 1]
    - [ ] DW-N.2: [done-when item 2]
    - [ ] DW-N.X: [done-when item N...]

    [if plan phase has **Skills:** field, include:]
    ## Additional Skills
    Before starting work, load the following skills using the Skill tool:
    - Skill([skill-from-plan])

    [if plan has Assumptions with "Verify Before Phase: N", include:]
    ## Assumption Verification
    Before proceeding with discovery, verify these assumptions from the plan:
    - [assumption text] (Confidence: [level])
    If any assumption is wrong, return UPDATE_PLAN with the invalidated assumption
    and what you found instead.

    ## Inputs
    - Plan file: docs/plans/<plan-name>.md
    - Phase: N - [name]

    ## Output Files
    - Discovery + Design: .code-foundations/build/<plan-name>-phase-N-discovery.md
```

---

## § MINIMAL_BUILD

Use for **Minimal gate** phases. Skips discovery — implements directly from plan description using TDD.

```
Agent tool:
- subagent_type: "code-foundations:build-agent"
- model: [from plan's **Model:** field, or omit if not set]
- description: "BUILD Phase N (minimal)"
- prompt: |
    Build Phase N of the build plan. This phase uses minimal gate
    policy — skip discovery, implement directly from the plan
    description using TDD (write tests from DW items, then implement).

    ## Plan Context
    [paste the Context section from the plan file]

    ## Progress
    [For Phase N>1: "Completed: Phase 1: [name] — [1 sentence summary]. Phase 2: ..."]
    Current: Phase N of M

    [if plan phase has **Skills:** field, include:]
    ## Additional Skills
    Before starting work, load the following skills using the Skill tool:
    - Skill([skill-from-plan])

    ## Phase N: [name]
    [paste the full phase description from the plan]

    ## Inputs
    - Plan file: docs/plans/<plan-name>.md
    - Phase: N - [name]
```

---

## § REVIEW

Use for **Full gate** REVIEW sub-phases. Always uses `code-foundations:post-gate-agent`.

```
Agent tool:
- subagent_type: "code-foundations:post-gate-agent"
- model: [from plan's **Model:** field, or omit if not set]
- description: "REVIEW Phase N"
- prompt: |
    Review Phase N implementation.

    ## Plan Context
    [paste the Context section from the plan file]

    ## Progress
    [For Phase N>1: "Completed: Phase 1: [name] — [1 sentence summary]. Phase 2: ..."]
    Current: Phase N of M

    ## Done-When Items (DW-IDs) — Requirement Verification
    For EACH item below, mark SATISFIED or NOT_SATISFIED with evidence
    (file:line, test name, or observable behavior). Any NOT_SATISFIED → FAIL.
    Do NOT skip items. These come from the original plan and may
    include items the build agent missed.
    [paste ALL DW items from the plan phase, verbatim:]
    - DW-N.1: [done-when item 1] → Status: ___ Evidence: ___
    - DW-N.2: [done-when item 2] → Status: ___ Evidence: ___
    - DW-N.X: [done-when item N...] → Status: ___ Evidence: ___

    [if plan phase has **Skills:** field, include:]
    ## Additional Skills
    Before starting work, load the following skills using the Skill tool:
    - Skill([skill-from-plan])

    ## Inputs
    - Plan: docs/plans/<plan-name>.md (Phase N section)
    [Full/Standard gate only:]
    - Discovery + Design: .code-foundations/build/<plan-name>-phase-N-discovery.md
    [Minimal gate: no discovery file exists]

    ## Files Changed
    [list files from BUILD subagent]

    ## Output
    Write review to: .code-foundations/build/<plan-name>-phase-N-review.md
```

---

## § CATCHUP_REVIEW

Inserted dynamically before a Full gate phase when 2+ phases have run since the last REVIEW. Batches verification across accumulated Standard/Minimal phases.

```
Agent tool:
- subagent_type: "code-foundations:post-gate-agent"
- model: [REVIEW model for the upcoming Full phase]
- description: "Catch-up REVIEW for Phases X-Y"
- prompt: |
    Batch review of Phases X through Y. These phases ran with Standard
    or Minimal gate policy (tests-only verification). Review them now
    before proceeding to Phase Z (Full gate).

    ## Plan Context
    [paste the Context section from the plan file]

    ## Phases to Review
    [For each accumulated phase:]
    ### Phase X: [name]
    Done-When Items:
    - DW-X.1: [item] → Status: ___ Evidence: ___
    Files changed: [list]

    ### Phase Y: [name]
    Done-When Items:
    - DW-Y.1: [item] → Status: ___ Evidence: ___
    Files changed: [list]

    ## Cross-Phase Coherence
    Check that the accumulated phases work together:
    - No contradictions between phase outputs
    - No regressions introduced by later phases
    - Tests still pass for earlier phases' functionality

    ## Output
    Write review to: .code-foundations/build/<plan-name>-catchup-phases-X-Y-review.md
```
