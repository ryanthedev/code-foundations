# Dispatch Templates

Subagent dispatch prompts used by the orchestrator (`commands/build.md`) when dispatching the build and post-gate agents. Templates are referenced by section header (e.g., `§ FULL_BUILD`) from the orchestrator and substituted with phase-specific values at dispatch time.

## Contents

| Section | Used for |
|---------|----------|
| `§ FULL_BUILD` | Full and Standard gate BUILD sub-phases |
| `§ MINIMAL_BUILD` | Minimal gate BUILD sub-phases (no discovery) |
| `§ REVIEW` | Full and Standard gate REVIEW sub-phases (post-gate-agent) |
| `§ CATCHUP_REVIEW` | Batch review inserted before a Full phase when 2+ phases have run since the last REVIEW |

Keeping these here instead of inline in `build.md`:
- Keeps the orchestrator's hot path lean
- Lets templates evolve without touching orchestration logic
- Makes the dispatch surface a single auditable file

**Substitution rules (orchestrator):**
- `[bracketed]` placeholders → phase-specific values. Each placeholder names its source (plan section, agent report, project config); conditional blocks (`[if plan phase has ...]`) are emitted only when the condition holds, with items pasted verbatim.
- `## Additional Skills` blocks: for EACH skill assigned to the phase, emit one `Skill(<plugin:name>)` line — this plugin's own skills as `Skill(code-foundations:<name>)`, skills from other installed plugins as `Skill(<plugin>:<name>)`. All assigned skills are real, model-invocable skills; the build subagent invokes them via the Skill tool (an explicit `Skill(...)` line in the dispatch prompt invokes the skill even though subagents don't inherit the register). The Skill tool loads the SKILL.md body, and each skill self-loads its own checklists via `${CLAUDE_SKILL_DIR}` once invoked — so emit NO separate checklist `Read()` lines. Do not Read-inject SKILL.md text; that was the old workaround for non-invocable skills.
- **Skills propagate BUILD → REVIEW:** if the BUILD agent's `### Skills Loaded` output reports skills beyond the plan's assignment, add those as `Skill(<plugin:name>)` lines to the REVIEW dispatch's `## Additional Skills` block too. The reviewer needs the same skill context to verify against.
- Test/typecheck/lint command placeholders → resolve from project config (package.json scripts, Makefile, Cargo.toml, etc.) — exact runnable commands, not descriptions.
- **Wave mode (parallel phases only):** when a phase runs in its own phase worktree (build.md → Parallel Waves), every path in the prompt is rooted at that worktree, and the prompt gains two additions — for BUILD: "Work ONLY inside `<worktree-root>`; run all commands from there. End with exactly ONE commit: `wip(phase-N): <name>` — squash if you made more. Report the worktree path and wip sha in your output." For REVIEW: "Run all commands from `<worktree-root>`." Serial phases omit all of this.

---

## § FULL_BUILD

Use for **Full gate** and **Standard gate** phases. The build agent runs discovery + design + implementation in one pass.

```
Agent tool:
- subagent_type: "code-foundations:build-agent"
- model: [from plan's **Model:** field — required; a plan without it stops the build at LOAD]
- description: "BUILD Phase N"
- prompt: |
    Build Phase N of the build plan. This is a two-part task:
    1. Discovery + Design — scope the phase work, identify gaps vs plan, make design decisions, map DW items to test cases
    2. Implementation — stub the interface, implement it, then write tests that validate each DW item (all tests must pass)

    Write discovery file before implementing.

    The phase body and its skills carry the design reasoning — implement steadily
    within them; when the plan doesn't fit reality, return UPDATE_PLAN rather than
    re-architecting on your own.

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
    Invoke EVERY Skill() below, in order, BEFORE starting work:
    - Skill([plugin:name from plan -- this plugin's own skills as code-foundations:<name>])
    [repeat the Skill() line for each assigned skill; each self-loads its own checklists]

    [if plan has Assumptions with "Verify Before Phase: N", include:]
    ## Assumption Verification
    Before proceeding with discovery, verify these assumptions from the plan:
    - [assumption text] (Confidence: [level])
    If any assumption is wrong, return UPDATE_PLAN with the invalidated assumption
    and what you found instead.

    [ONLY on a gate-failure re-dispatch after a REVIEW FAIL, include:]
    ## Review Findings to Fix
    An independent review found these defects — fix each, keeping all existing
    tests passing (the passing set only grows):
    [paste the Issues section from the review file verbatim]

    ## Inputs
    - Plan file: .code-foundations/plans/<plan-name>.md
    - Phase: N - [name]

    ## Output Files
    - Discovery + Design: .code-foundations/build/<plan-name>-phase-N-discovery.md
```

---

## § MINIMAL_BUILD

Use for **Minimal gate** phases. Skips discovery — implements directly from plan description: stub, implement, then validate with tests.

```
Agent tool:
- subagent_type: "code-foundations:build-agent"
- model: [from plan's **Model:** field — required; a plan without it stops the build at LOAD]
- description: "BUILD Phase N (minimal)"
- prompt: |
    Build Phase N of the build plan. This phase uses minimal gate
    policy — skip discovery, implement directly from the plan
    description: stub the interface, implement it, then write tests
    that validate each DW item (all tests must pass).

    ## Plan Context
    [paste the Context section from the plan file]

    ## Progress
    [For Phase N>1: "Completed: Phase 1: [name] — [1 sentence summary]. Phase 2: ..."]
    Current: Phase N of M

    [if plan phase has **Skills:** field, include:]
    ## Additional Skills
    Invoke EVERY Skill() below, in order, BEFORE starting work:
    - Skill([plugin:name from plan -- this plugin's own skills as code-foundations:<name>])
    [repeat the Skill() line for each assigned skill; each self-loads its own checklists]

    ## Phase N: [name]
    [paste the full phase description from the plan]

    ## Done-When Items (DW-IDs)
    These are the acceptance criteria from the plan. Each DW item must
    have corresponding test(s) (e.g., `test_DW_1_1_creates_user`).
    Any DW item without a test is a visible gap.
    If any item cannot be met, return UPDATE_PLAN.
    [paste ALL DW items from the plan phase, verbatim:]
    - [ ] DW-N.1: [done-when item 1]
    - [ ] DW-N.2: [done-when item 2]
    - [ ] DW-N.X: [done-when item N...]

    ## Inputs
    - Plan file: .code-foundations/plans/<plan-name>.md
    - Phase: N - [name]
```

---

## § REVIEW

Use for **Full and Standard gate** REVIEW sub-phases. Always uses `code-foundations:post-gate-agent`.

**Debiasing rules (do not violate):** the reviewer must receive NO intent-framing. Do NOT include the plan's Context/problem statement, progress summaries ("Completed Phase…"), the discovery file, or any account of what the build agent did or intended. Requirements + files + commands only.

**Security-sensitive (3-sample):** if the phase is marked `**Security-sensitive:** yes` in the plan, dispatch THREE independent copies of this prompt as three Agent calls **in a single message** (they run concurrently — independence is contextual, not temporal) on **fable**, and take the majority verdict. The copies are identical EXCEPT for the per-sample review path: substitute `K`=1,2,3 so each sample's review path is `<plan-name>-phase-N-review-sample-K.md`. Without this the three samples race and overwrite a single review file. Each sample writes its own scratch artifacts (coverage output, temp files) under a sample-unique directory and runs no mutating commands (no `lint --fix`, no dependency installs). If the suite uses shared mutable resources (DB, ports, docker services, on-disk fixtures), run the three samples sequentially instead. For a non-sampled (single) review, drop the `-sample-K` suffix (review → `<plan-name>-phase-N-review.md`).

```
Agent tool:
- subagent_type: "code-foundations:post-gate-agent"
- model: [resolved REVIEW model per the orchestrator's Model Resolution — the phase's BUILD model downgraded one tier (fable→sonnet, opus→sonnet, sonnet→haiku, haiku floor); fable for security-sensitive samples]
- description: "REVIEW Phase N"
- prompt: |
    Independently verify the implementation in the files below against the
    requirements below. You did not write this code and have no information
    about how or why it was written. Do NOT assume it is correct or complete.
    Assume requirements may be unmet and bugs may be present; verify each item
    from scratch against the actual code and executed test results. Do NOT
    introduce requirements that are not listed here.

    ## Requirements to verify (Done-When items)
    For EACH item, fill the template. A PASS verdict REQUIRES execution
    evidence (a passing test you ran, or observed behavior) — not "implemented".
    Do NOT skip items.
    [paste ALL DW items from the plan phase, verbatim:]
    - DW-N.1: [done-when item 1]
      PREMISE: ___  EVIDENCE (file:line): ___  TRACE (input→output): ___  VERDICT: ___
    - DW-N.2: [done-when item 2]
      PREMISE: ___  EVIDENCE (file:line): ___  TRACE (input→output): ___  VERDICT: ___
    - DW-N.X: ...

    [if plan phase has **Edge cases:**, include:]
    ## Edge cases — verify handling
    These are explicit plan requirements with the same verdict standing as the
    DW items above: an unhandled case listed here is a FAIL, not a Note.
    Verify the implementation handles each.
    [paste the phase's Edge cases verbatim]

    ## Test Coverage Level
    [paste the plan's Test Coverage level, e.g. "100%"]

    ## Files to review
    [implementation + test file paths from the BUILD agent's report — paths only, no commentary]

    ## How to run the suite
    [exact test command + typecheck/lint commands for this project]
    Run these directly via Bash and capture the output.

    [ONLY if this phase consumes an interface from a prior phase — neutral
    wording, no "completed/done/working" language:]
    ## Dependency
    Phase N consumes [interface X] defined in [file:line]. Treat its contract
    as given; do not re-review it, but flag if this phase misuses it.

    [if plan phase has **Skills:** field OR BUILD agent reported additional skills, include:]
    ## Additional Skills
    Invoke EVERY Skill() below BEFORE reviewing:
    - Skill([plugin:name from plan -- this plugin's own skills as code-foundations:<name>])
    [repeat the Skill() line for each skill; also include skills from BUILD's "Skills Loaded" output not already listed]

    ## Output
    Write review to: [review path — `.code-foundations/build/<plan-name>-phase-N-review.md`,
    or `.code-foundations/build/<plan-name>-phase-N-review-sample-K.md` for
    security-sensitive sample K]
```

---

## § CATCHUP_REVIEW

Inserted dynamically before a Full gate phase when 2+ phases have run since the last REVIEW. Batches verification across accumulated Minimal phases — the only tier without per-phase REVIEW. Same debiasing rules as § REVIEW: no plan Context, no progress narrative, no discovery files.

**Model:** use the upcoming Full phase's resolved REVIEW model (its BUILD model downgraded one tier per the orchestrator's Model Resolution). When fired before VERIFY (no upcoming Full phase), use the highest resolved REVIEW model among the covered phases.

```
Agent tool:
- subagent_type: "code-foundations:post-gate-agent"
- model: [upcoming Full phase's resolved REVIEW model]
- description: "Catch-up REVIEW for Phases X-Y"
- prompt: |
    Independently verify the implementations below against their requirements.
    You did not write this code. Do NOT assume it is correct or complete.
    Assume requirements may be unmet and bugs may be present; verify each item
    from scratch against the actual code and executed test results. Do NOT
    introduce requirements that are not listed here.

    ## Phases to verify
    [For each accumulated phase:]
    ### Phase X: [name]
    Requirements (fill the template per item; PASS requires execution evidence):
    - DW-X.1: [item]
      PREMISE: ___  EVIDENCE (file:line): ___  TRACE (input→output): ___  VERDICT: ___
    Files: [implementation + test file paths]

    ### Phase Y: [name]
    Requirements:
    - DW-Y.1: [item]
      PREMISE: ___  EVIDENCE (file:line): ___  TRACE (input→output): ___  VERDICT: ___
    Files: [implementation + test file paths]

    ## How to run the suite
    [exact test command + typecheck/lint commands]

    ## Cross-Phase Coherence
    Check that the accumulated phases work together:
    - No contradictions between phase outputs
    - No regressions introduced by later phases
    - Tests still pass for earlier phases' functionality

    ## Output
    Write review to: .code-foundations/build/<plan-name>-catchup-phases-X-Y-review.md
```
