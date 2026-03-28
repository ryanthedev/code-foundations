---
description: "Brainstorm and plan features"
---

# Skill: whiteboarding

**Discover -> Classify -> Explore -> Detail -> Save -> Check -> Confirm -> Handoff**

The plan is a contract between whiteboarding and building. It specifies WHAT and WHY at the strategic level, with explicit interfaces between phases.

**Thinking effort:** Planning benefits from max effort. If not already at max, suggest the user increase it before proceeding.

---

## STOP - Setup First

### Load Design Standards

Before any work, read the pre-gate design standards:
1. `Read($CLAUDE_PLUGIN_ROOT/references/pre-gate-standards.md)`

### Create Progress Tasks

Create all steps as tasks upfront so progress is visible. Use `TaskCreate` for each, then `TaskUpdate` with `blockedBy` to enforce ordering.

```
TaskCreate("DISCOVER: Codebase search",          "Search codebase for patterns, conventions, similar features")
TaskCreate("DISCOVER: Skill audit",              "Audit all available skills, match to project tech stack")
TaskCreate("DISCOVER: Questioning",              "Ask clarifying questions, produce problem statement")
TaskCreate("CLASSIFY",                           "Determine complexity track: Simple / Medium / Complex")
TaskCreate("EXPLORE",                            "Research technologies, compare 2-3 approaches (Medium/Complex)")
TaskCreate("DETAIL",                             "Break into phases using track-specific template")
TaskCreate("SAVE",                               "Write plan to docs/plans/")
TaskCreate("CHECK",                              "Subagent reviews plan for structural issues")
TaskCreate("CONFIRM",                           "User confirms plan, test coverage decision, corrections")
TaskCreate("HANDOFF",                            "User chooses: build or manual execution")
```

Set `blockedBy` so each task depends on the previous one. Mark tasks `in_progress` when starting, `completed` when done.

**Simple track:** Skip EXPLORE and CHECK tasks (mark as completed with note "skipped — simple track").

---

## Quick Reference

| Step | Goal | Output |
|------|------|--------|
| DISCOVER | **Search codebase** + **audit skills** + clarify problem | Pattern summary + skill inventory + problem statement |
| CLASSIFY | Determine complexity track | Simple / Medium / Complex |
| EXPLORE | **Research technologies** + compare approaches (Medium/Complex) | Chosen approach with rationale |
| DETAIL | Break into phases using track-specific template | Phase specs |
| SAVE | Write to docs/plans/ | Plan file on disk |
| CHECK | Subagent reviews plan for structural issues | Review findings |
| CONFIRM | User confirms + corrections + test coverage decision | Approved plan |
| HANDOFF | User chooses next step | Build or manual execution |

---

## Crisis Invariants - NEVER SKIP

| Check | Why Non-Negotiable |
|-------|-------------------|
| **Search codebase BEFORE questions** | Patterns exist that user may not know about |
| **Classify complexity BEFORE detailing** | Wrong track = wrong ceremony = wasted effort or missed risks |
| **Research BEFORE proposing approaches** | Uninformed proposals waste user's decision-making |
| **One question at a time** | Multiple questions = cognitive overload = shallow answers |
| **2-3 approaches before committing (Medium/Complex)** | First idea is rarely best; comparison reveals trade-offs |
| **File paths are HINTS, not mandates** | Pre-gate agent discovers actual files; plan paths go stale |
| **No implementation details in phases** | Pre-gate writes pseudocode after fresh discovery; plan-level design is pre-discovery guesswork |
| **Plans must be pipeline-compatible** | The building pipeline dispatches subagents autonomously. Plans must not introduce interactive user prompts between sub-phases (e.g., "Fix now or proceed?"). Use deterministic rules instead (e.g., "max 2 retry iterations") |
| **Include Approach notes for non-discoverable decisions** | User decisions (JWT not sessions, event-driven not polling) cannot be rediscovered by subagents |
| **Save before checking** | Subagent needs a file to review with fresh eyes |
| **Subagent check before user validation (Medium/Complex)** | Fresh-context review catches structural gaps you're blind to |
| **User confirms after check** | User sees both plan and review findings before approving |

---

## Step 1: DISCOVER (Pattern Discovery + Skill Audit + Questioning)

### Step 1a: Codebase Search + Code Patterns (MANDATORY - Do First)

**Before asking ANY questions, check for an existing code patterns doc:**

```
1. Look for docs/code-patterns.md in the project root
2. IF EXISTS:
   a. Read it
   b. Check staleness: git rev-list <commit-ref>..HEAD --count
      - 0 commits since → trust it, skip full search
      - 1-20 commits since → spot-check: read recent diffs, update doc if patterns changed
      - 20+ commits since → full re-scan, regenerate doc
3. IF MISSING:
   a. Run full codebase search (below)
   b. Generate docs/code-patterns.md with findings
```

**Full codebase search (when needed):**

| Search | Action |
|--------|--------|
| Similar features | `grep -r "keyword"` across codebase |
| Module patterns | Read 2-3 files in target directory |
| Related components | Find how similar problems were solved |
| Conventions | Note naming, structure, error handling patterns |

**Output: `docs/code-patterns.md`**
```markdown
<!-- base-commit: [current HEAD hash] -->
<!-- generated: [YYYY-MM-DD] -->

# Code Patterns

## Architecture
- [pattern]: [where used, how it works]

## Naming Conventions
- [convention]: [examples]

## Error Handling Strategy
- [approach]: [where enforced]

## File Organization
- [rule]: [examples]

## Testing Conventions
- [what gets tested, naming, location]

## Technology Decisions
- [decision]: [rationale]

## Forbidden Patterns
- [pattern]: [why forbidden]

## Similar Implementations
- [file]: [what it does, relevance to current task]
```

**If new project with no code:** Write a minimal doc with the technology decisions from the user's request and skip the search.

**See:** [pattern-reuse-gate.md]($CLAUDE_PLUGIN_ROOT/references/pattern-reuse-gate.md)

---

### Step 1b: Skill Discovery (MANDATORY)

**After codebase search, discover ALL available skills by scanning the system-reminder.**

The system-reminder at conversation start lists every installed skill with its description and trigger conditions. Scan it — do not rely on a hardcoded list.

```
DISCOVER:
1. Identify project tech stack (language, framework, platform) from codebase search
2. Read the system-reminder's skill list — every line with "plugin:skill-name" is a candidate
3. For each skill, read its description and trigger conditions
4. Match: does the skill's trigger overlap with this project's tech stack, task type, or domain?
5. Classify each matched skill by phase: design, coding, testing, review, or deployment
```

**Matching rules:**
- Match on description keywords (e.g., "React Native" in description → RN project match)
- Match on trigger conditions (e.g., "Use when designing modules" → design phase)
- Include skills from ANY installed plugin, not just code-foundations
- When uncertain, include the skill — the building agent can skip it if irrelevant
- Exclude skills that are workflows (`whiteboarding`, `building`, `review`, `debug`) — those are commands, not loadable skills

**Output: Skill Inventory**
```markdown
## Discovered Skills for This Project
- **Tech stack:** [language, framework, platform]
- **Matched skills:**
  - `plugin:skill-name`: [why it matches] → Phase: [design/coding/testing/review]
  - `plugin:skill-name`: [why it matches] → Phase: [design/coding/testing/review]
- **Unmatched (excluded):** [skills scanned but not relevant, with 1-word reason]
```

This inventory feeds into Step 4 (DETAIL) where skills are assigned to each plan phase's `**Skills:**` field.

---

### Step 1c: Adaptive Questioning

After pattern discovery, classify complexity using the signal table in Step 2 (CLASSIFY). State the classification, then ask questions accordingly.

### Question Sequence (Ask ONE at a time via AskUserQuestion)

**ENFORCEMENT:** Each question below MUST use `AskUserQuestion` tool. Do NOT output questions as text -- the tool forces a stop and wait. No proceeding until the user answers.

**Simple (2-3 questions):**
1. What specific outcome do you want?
2. What constraints should I know about?
3. What does "done" look like?

**Medium (add these):**
4. Who/what will use this?
5. What could go wrong?

**Complex (add these):**
6. What other systems does this touch?
7. What's the rollback plan if it fails?
8. What's the testing strategy?

**NOTE:** Questions about "existing patterns" removed -- we searched instead of asking.

### Question Format

Use multiple-choice when possible:

```
Which authentication approach fits best?
- [ ] JWT tokens (stateless, scalable)
- [ ] Session cookies (simpler, server-state)
- [ ] OAuth2 (if external providers needed)
- [ ] Other (describe)
```

### Questioning Gate

**STOP. You CANNOT proceed to Step 2 until ALL of the following are true:**
- [ ] Codebase searched
- [ ] Complexity classified (Simple/Medium/Complex)
- [ ] Minimum questions asked: Simple=2, Medium=4, Complex=6
- [ ] Each question asked via `AskUserQuestion` (not text output)
- [ ] Each answer received and recorded

**If you catch yourself about to skip to approaches -- STOP. Count questions asked. If below minimum, ask the next one.**

### Output: Problem Statement

After ALL questions answered, summarize:

```markdown
## Problem Statement
[1-2 sentences describing what we're building]

## Constraints
- [constraint 1]
- [constraint 2]

## Success Criteria
- [criterion 1]
- [criterion 2]
```

Get user confirmation via `AskUserQuestion`: "Does this capture what you want?"

---

## Step 2: CLASSIFY (Complexity Assessment)

### Classify BEFORE Proceeding

After pattern discovery and questioning, classify the task using these signals:

| Signal | Simple | Medium | Complex |
|--------|--------|--------|---------|
| Files touched | 1-3 | 4-8 | 9+ |
| Patterns involved | 1 known pattern | 2-3 patterns, some new | Multiple new patterns, cross-cutting |
| Cross-cutting concerns | None | 1-2 (e.g., auth, logging) | 3+ (e.g., auth, caching, migration, backward compat) |
| Uncertainty | Low -- clear what to build | Medium -- approach unclear | High -- requirements or feasibility uncertain |
| Phase count | 1-2 | 3-5 | 5-7 |

**State classification explicitly:**

> "Based on pattern discovery, this is a **[Simple/Medium/Complex]** task. [1-sentence justification based on signals above]. I'll follow the [Simple/Medium/Complex] track."

**If uncertain between two tracks, choose the higher one.** Under-planning costs more than slight over-planning.

### Track Overview

| Track | Phases | Ceremony | Approach Comparison | Self-Check |
|-------|--------|----------|--------------------|----|
| **Simple** | 1-2 | Flat checklist, 50-75 words/phase | Skip (unless conflicting patterns found) | Skip |
| **Medium** | 3-5 | Contract, ~100-150 words/phase | 2 approaches | Full |
| **Complex** | 5-7 | Full contract with risk/uncertainty, ~100-150 words/phase | 2-3 approaches + pre-mortem | Full |

**Hard cap: 7 phases regardless of complexity.** If you need more than 7, the scope is too large -- split into multiple plans.

---

## Step 3: EXPLORE (Research + Approaches)

### Simple Track: SKIP This Step

For Simple tasks, the approach is usually obvious from the codebase patterns found in Step 1. Proceed directly to DETAIL.

**Exception:** If pattern discovery found conflicting patterns, do a quick 2-approach comparison even on Simple track.

### Medium Track: Compare 2 Approaches

### Complex Track: Compare 2-3 Approaches + Pre-Mortem

### Research Before Proposing (Medium/Complex Only)

#### Codebase Research
```
SEARCH FOR:
1. How similar problems are solved in this codebase
2. What libraries/patterns are already in use
3. What the codebase is NOT using (intentional omissions?)
```

| Check | Why |
|-------|-----|
| Existing dependencies | Don't propose new lib if similar exists |
| Rejected patterns | Check git history/comments for "we tried X" |
| Team conventions | Match what's already working |

#### Web Research (When technology choice is involved)

**Use WebSearch/WebFetch when:**
- Comparing libraries/frameworks
- Evaluating technology trade-offs
- Checking current best practices (your knowledge may be outdated)

```
SEARCH FOR:
1. "[technology A] vs [technology B] [current year]"
2. "[problem domain] best practices [current year]"
3. "[framework] [specific feature] implementation"
```

**Output: Research Summary**
```markdown
## Codebase Findings
- Already using: [libraries, patterns]
- Similar solutions: [where, how]

## Web Research (if applicable)
- [Technology A]: [pros, cons, current status]
- [Technology B]: [pros, cons, current status]
- Recommendation: [based on research]
```

### Generate Alternatives

**Approaches must be STRUCTURALLY different** (different technology, pattern, or architecture). Variations of the same approach do NOT count:
- Bad: "JWT with refresh tokens" vs "JWT without refresh tokens" = same approach
- Good: "JWT tokens" vs "Session cookies" vs "OAuth2" = different approaches

**Approaches must be informed by research.** Don't propose technologies you didn't research.

**If user mentioned a solution in their initial request** (e.g., "I'm thinking JWT"), this is exploratory input, NOT a decision. Still present structurally different alternatives.

| Approach | Trade-offs | Best When | Research Source |
|----------|-----------|-----------|-----------------|
| Option A | [pros/cons] | [conditions] | [codebase/web] |
| Option B | [pros/cons] | [conditions] | [codebase/web] |

### Pre-Mortem (Complex Track Only)

After presenting approaches, before the user chooses, run a pre-mortem:

```markdown
## Pre-Mortem: What Could Kill This Plan?

| Failure Mode | Probability | Impact | Which Approach Survives? |
|-------------|-------------|--------|-------------------------|
| [failure 1] | LOW/MED/HIGH | LOW/MED/HIGH | [approach] |
| [failure 2] | LOW/MED/HIGH | LOW/MED/HIGH | [approach] |
```

### Decision

Ask: "Which approach do you prefer, or should I elaborate on any?"

Record chosen approach and rationale:
```markdown
## Chosen Approach: [Name]
**Rationale:** [why this over others]
**Fallback:** [1 sentence: what to try if the chosen approach hits a wall]
```

---

## Step 4: DETAIL (Track-Specific Phase Specs)

### The Plan Is a Contract

The plan specifies WHAT and WHY. Subagents determine HOW. Each phase is a contract between the planning session and the building pipeline's independent subagents.

**The plan has four readers with different needs:**

| Reader | Needs from Plan | Ignores |
|--------|----------------|---------|
| **Building orchestrator** | Phase names, ordering, model hints, Done-when item counts | Implementation details |
| **Pre-gate agent** | Goal, scope, constraints, approach notes, file hints | Other phases' internals |
| **Post-gate agent** | Goal, done-when criteria | How it was implemented |
| **Human (user)** | Strategic intent, approach rationale, constraint coverage | Pseudocode-level detail |

---

### Simple Track Template (1-2 phases, 50-75 words each)

**No approach comparison. No subagent check. Present the full plan at once.**

Each phase is a flat checklist. No contract structure, no risk analysis.

```markdown
### Phase N: [Name]
**Model:** [recommended model]
**Skills:** [skills from inventory that match this phase's work -- omit if only default agent skills apply]

**Goal:** [One sentence: what this phase delivers]

**Scope:**
- IN: [what this phase covers]
- OUT: [what is explicitly excluded]

**Constraints:** [non-discoverable requirements -- omit if none]

**Done when:**
- [ ] DW-N.1: [Verifiable criterion]
- [ ] DW-N.2: [Verifiable criterion]
```

**DW-ID format:** `DW-{phase}.{item}` — every done-when item gets a stable ID. The building orchestrator extracts these and injects them into PRE-GATE and POST-GATE dispatch prompts to prevent silent requirement descoping.

---

### Medium/Complex Track Template (~100-150 words per phase)

**Present each section and get user confirmation before proceeding to the next.**

```markdown
### Phase N: [Name]
**Model:** [recommended model]
**Skills:** [skills from inventory that match this phase's work -- omit if only default agent skills apply]

**Goal:** [What this phase accomplishes and why -- 1-2 sentences]

**Scope:**
- IN: [what this phase covers]
- OUT: [what is explicitly excluded]

**Constraints:**
- [non-discoverable requirement the pre-gate agent must respect]

**Approach notes:** [ONLY non-discoverable user decisions -- omit if none]
- [decision + rationale]

**File hints:**
- `path/to/area/` -- [why relevant]

**Depends on:** [Phase X] | **Unlocks:** [Phase Y]

**Done when:**
- [ ] DW-N.1: [Observable, verifiable condition]
- [ ] DW-N.2: [Observable, verifiable condition]

**Difficulty:** LOW / MEDIUM / HIGH
**Uncertainty:** [what could change -- or "None"]
```

### Approach Notes: The Non-Discoverable Exception

**Approach notes exist ONLY for decisions the user made during planning that cannot be rediscovered from the codebase.** These are design choices, not implementation details.

Good approach notes:
- "Use JWT not sessions -- user chose stateless for horizontal scaling"
- "Event-driven architecture, not polling -- latency budget is <100ms"
- "Rejected: direct DB access from handlers. Use repository pattern per existing convention."

Bad approach notes (these belong in pseudocode, not the plan):
- "Create a UserService class with getUser(), createUser(), deleteUser() methods"
- "Use bcrypt with 12 rounds for password hashing"
- "Add try-catch around the database call on line 47"
- "Use PERT formula: E = (O + 4M + P) / 6" (the decision to use three-point estimation is non-discoverable; the formula itself is discoverable from any estimation reference)

**Test:** If the decision could be arrived at by searching the codebase, it does NOT belong in approach notes. If only the user knows why this choice was made, it belongs.

### YAGNI Gate

Before each phase, ask:
- Is this phase actually needed for the stated success criteria?
- Could we ship without it?
- Are we building for hypothetical future needs?

If answer is "not needed now" -> Remove from plan.

**Phase granularity test:** Each phase should produce a deliverable that is meaningful to the building orchestrator and verifiable by the post-gate agent. If a "phase" describes an internal component of another phase's deliverable (e.g., "selection logic" inside a "review agent"), it belongs in that phase's scope, not as a separate phase. Phases are contracts for WHAT to deliver, not a task breakdown of HOW to build.

### Phase Count Guidance

| Complexity | Phase Count | Rationale |
|-----------|-------------|-----------|
| Simple | 1-2 phases | More phases than tasks = overhead exceeds value |
| Medium | 3-5 phases | Standard decomposition |
| Complex | 5-7 phases | If >7, the feature should be split into multiple plans |

**Prefer fewer phases within the range.** A 3-phase Medium plan is usually better than a 5-phase Medium plan -- fewer phases mean less pre-gate/post-gate overhead per phase and more substantial work per phase. Add phases only when scope boundaries genuinely require separate pre-gate discovery or when different model recommendations apply.

**If a phase exceeds 200 words, it is too large.** Split it into two phases.

### Dependency Structure Guidance

Use the simplest dependency chain that accurately models reality. If Phase 3 and Phase 4 can both start after Phase 2 completes (and they do not depend on each other), express this as a DAG: both depend on Phase 2, and a later phase depends on both. Do not artificially linearize independent work -- it forces sequential execution in the building pipeline when parallel execution would be safe.

---

## Step 5: SAVE (Write Plan File)

### File Location

```
docs/plans/YYYY-MM-DD-<topic-slug>.md
```

### Model Recommendations (Apply Per Phase)

When writing each phase, recommend a model based on the phase's content:

```
OPUS_KEYWORDS  = [refactor, architect, migrate, redesign, rewrite, overhaul]
HAIKU_KEYWORDS = [config, rename, typo, bump, cleanup, delete, remove]

If Done-when items <= 2 AND file hints reference <= 2 areas AND no OPUS_KEYWORDS:
  -> haiku (simple, mechanical work)

If Done-when items >= 6 OR file hints reference >= 6 areas OR any OPUS_KEYWORD:
  -> opus (complex, architectural work)

Otherwise:
  -> sonnet (default)
```

**Write `**Model:** [model]` into each phase heading.** This is not optional -- the plan should make the model choice visible so the user can adjust before building begins.

### Plan File Schema: Simple Track

```markdown
# Plan: [Topic]

**Created:** YYYY-MM-DD
**Status:** ready
**Complexity:** simple

---

## Context

[Problem statement from Step 1 -- 2-3 sentences]

## Constraints

- [constraint 1]
- [constraint 2]

---

## Implementation Phases

### Phase 1: [Name]
**Model:** [recommended model]
**Skills:** [additional skills for this phase -- omit if none]

**Goal:** [One sentence]

**Scope:**
- IN: [covered]
- OUT: [excluded]

**Constraints:** [non-discoverable requirements -- omit if none]

**Done when:**
- [ ] [Verifiable criterion]

---

### Phase 2: [Name] (if needed)
**Model:** [recommended model]
**Skills:** [additional skills for this phase -- omit if none]

**Goal:** [One sentence]

**Scope:**
- IN: [covered]
- OUT: [excluded]

**Constraints:** [non-discoverable requirements -- omit if none]

**Done when:**
- [ ] [Verifiable criterion]

---

## Test Coverage

**Level:** [100% / Backend only / Backend + frontend / None / Per-phase]

## Test Plan

- [ ] [specific tests]

---

## Notes

- [anything pre-gate agents should know that does not fit in phase constraints]

---

## Execution Log

_To be filled during /code-foundations:building_
```

### Plan File Schema: Medium/Complex Track

```markdown
# Plan: [Topic]

**Created:** YYYY-MM-DD
**Status:** ready
**Complexity:** [medium/complex]

---

## Context

[Problem statement from Step 1]

## Constraints

- [constraint 1]
- [constraint 2]

## Chosen Approach

**[Approach name]**

[Rationale from Step 3]

**Fallback:** [1 sentence: what to try if the chosen approach hits a wall]

## Rejected Approaches

- **[Approach B name]:** [1 sentence why rejected]
- **[Approach C name]:** [1 sentence why rejected]

---

## Implementation Phases

### Phase 1: [Name]
**Model:** [recommended model]
**Skills:** [additional skills for this phase -- omit if none]

**Goal:** [1-2 sentences: what and why]

**Scope:**
- IN: [what this covers]
- OUT: [what is excluded]

**Constraints:**
- [constraint]

**Approach notes:**
- [non-discoverable user decision, if any]

**File hints:**
- `path/to/area/` -- [why relevant]

**Depends on:** None | **Unlocks:** Phase 2

**Done when:**
- [ ] DW-1.1: [verifiable criterion]
- [ ] DW-1.2: [verifiable criterion]

**Difficulty:** [LOW/MEDIUM/HIGH]
**Uncertainty:** [what we don't know, or "None"]

---

### Phase 2: [Name]
**Model:** [recommended model]
**Skills:** [additional skills for this phase -- omit if none]
...

---

## Test Coverage

**Level:** [100% / Backend only / Backend + frontend / None / Per-phase]

## Test Plan

- [ ] Unit: [specific tests]
- [ ] Integration: [specific tests]
- [ ] Manual: [verification steps]

---

## Assumptions

| Assumption | Confidence | Verify Before Phase | Fallback If Wrong |
|-----------|-----------|--------------------|--------------------|
| [assumption] | HIGH/MED/LOW | [phase N] | [what to do instead] |

## Decision Log

| Decision | Alternatives Considered | Rationale | Phase |
|----------|------------------------|-----------|-------|
| [decision] | [alternatives] | [why this one] | [N] |

---

## Notes

- [edge cases identified during planning]
- [gotchas discovered during codebase search]
- [open questions for future consideration]

---

## Execution Log

_To be filled during /code-foundations:building_
```

### Save Command

```bash
mkdir -p docs/plans
# Write plan file
```

### Commit Plan File (MANDATORY)

After writing the plan file, commit it to git. This is required because building creates a worktree from the git history — uncommitted files are invisible to worktrees.

```bash
git add docs/plans/YYYY-MM-DD-<topic-slug>.md
git commit -m "plan: <topic-slug>"
```

**Do NOT skip this commit.** Without it, `/code-foundations:building` in worktree mode cannot see the plan file.

---

## Step 6: CHECK (Subagent Plan Review)

### Simple Track: SKIP This Step

Simple plans are short enough that structural issues are visible on inspection. Mark CHECK task as completed with "skipped — simple track". Proceed to CONFIRM.

### Medium/Complex Track: Subagent Review

**Dispatch a subagent to review the saved plan file with fresh eyes.**

The subagent has no prior context — it reads the plan cold, which catches assumptions and gaps you're blind to.

```
Agent tool:
- subagent_type: "general-purpose"
- model: sonnet
- description: "Review whiteboarding plan"
- prompt: |
    Review the plan at docs/plans/<plan-file>.md for structural issues.

    ## Checklist

    ### Structural Completeness
    - [ ] Every constraint maps to at least one phase's Constraints field
    - [ ] Done-when criteria across all phases collectively satisfy the Context/problem statement
    - [ ] No phase's IN scope overlaps with another phase's IN scope
    - [ ] The union of all phases' IN scopes covers the full feature
    - [ ] Every Depends-on references an existing phase
    - [ ] No orphan phases (every phase connects to the chain)
    - [ ] Approach notes contain ONLY non-discoverable user decisions, not implementation details
    - [ ] Every phase has at least one file hint (Medium/Complex)
    - [ ] Every done-when criterion is externally observable and verifiable
    - [ ] Every done-when item has a DW-ID (`DW-{phase}.{item}`)
    - [ ] No phase exists solely for hypothetical future needs (YAGNI)

    ### Cross-Phase Coherence
    - [ ] No contradictions between phase constraints
    - [ ] What Phase N produces (Done-when) matches what Phase N+1 assumes (Depends-on)
    - [ ] At least one phase produces user-observable output (not just infrastructure)
    - [ ] Highest-uncertainty phases appear early, not late

    ### Skills Audit
    - [ ] Skills field is present on phases where non-default skills are useful
    - [ ] Skills match the phase's work type (e.g., design skills for design phases, not coding phases)
    - [ ] No skills listed that aren't actually available in the environment

    ## Output

    Return a structured review:
    - PASS: no issues found
    - FINDINGS: list of issues with specific fix recommendations
    - Each finding references the specific phase and field
```

**After subagent returns:**
1. If PASS → mark CHECK task completed, proceed to CONFIRM
2. If FINDINGS → fix each issue in the plan file, then mark CHECK task completed

---

## Step 7: CONFIRM (User Confirmation)

### Present Plan + Review Results

Show the user:
1. The plan summary (phases, goals, skill assignments)
2. Any findings from CHECK and how they were resolved

**Simple track:** Present full plan. Ask: "Does this plan look right? Anything to add or change?"

**Medium/Complex track:** Present the full plan structure:

```markdown
# Plan: [Topic]

## Phases
1. [Phase 1 name] -- [1 sentence goal] -- Skills: [if any]
2. [Phase 2 name] -- [1 sentence goal] -- Skills: [if any]
3. ...

## Constraint Coverage
- [constraint] -> Phase [N]
- [constraint] -> Phase [N]

## Review Results
- [findings addressed, or "Clean — no issues found"]

## Questions/Concerns
- [any remaining uncertainties]
```

Ask: "Does this plan look complete? Any phases to add, remove, or modify?"

### Test Coverage Question (MANDATORY)

Before finalizing, ask about test coverage:

```
How much test coverage do you want for this implementation?

1. 100% coverage (Recommended)
   Unit tests for all new code + integration tests for critical paths

2. Backend only
   Tests for server-side/API changes only

3. Backend + frontend
   Tests for both server and client layers

4. None
   Skip tests (not recommended - technical debt)

5. Ask at each phase
   Decide test scope when building each phase
```

**Record the answer in the plan file** under `## Test Coverage`.

**Inform building:** This choice affects POST-GATE behavior -- reviewers will check for tests matching the chosen coverage level.

### Corrections

If the user requests changes:
1. Update the plan file
2. If changes are structural (new phases, reordered dependencies), re-run CHECK (dispatch subagent again)
3. If changes are minor (wording, constraints), update directly and re-present

---

## Step 8: HANDOFF

### Ask User How to Proceed

Use `AskUserQuestion` with these options:

**Question:** "Plan saved and committed to docs/plans/YYYY-MM-DD-<topic>.md. How would you like to proceed?"

**Options:**
1. **Build now** (Recommended) - Drop thinking effort and start building
2. **Tell me what to do** - Get step-by-step instructions to execute manually

**If user selects option 1:**
Suggest setting thinking effort to default — the plan already contains the strategic reasoning, so max effort during building orchestration is wasted. The subagents do the heavy thinking in their own contexts. Then run `/code-foundations:building docs/plans/YYYY-MM-DD-<topic>.md`

Building will create a worktree at `.claude/worktrees/<topic-slug>/` and run all phases there. The user's main checkout remains free for other work or parallel builds.

**If user selects option 2:**
Provide numbered steps the user can follow to implement the plan manually

---

## What the Plan Specifies vs. What Building Discovers

The plan specifies WHAT and WHY. The building pipeline discovers HOW.

| Plan Specifies (WHAT + WHY) | Building Discovers (HOW) |
|----------------------------|--------------------------|
| Goal per phase | Current codebase state |
| Constraints and non-goals | Specific file paths and function signatures |
| Scope boundaries (IN/OUT) | Implementation patterns and algorithms |
| Success criteria (Done when) | Pseudocode and design decisions |
| Approach rationale and rejected alternatives | Edge cases and error handling |
| Cross-phase dependencies | Integration details |
| Test coverage level | Specific test cases |
| File hints (directional, not mandates) | Actual files to create/modify |
| Difficulty + Uncertainty signals | Task decomposition within phases |
| Skills per phase (from skill audit) | Which skills to load at runtime |

**The plan does NOT contain:**
- Pseudocode
- Function signatures
- Error handling specifics
- Detailed algorithms
- Edge case enumeration
- Task lists prescribing HOW

---

## Chaining

- **RECEIVES FROM:** User request, feature description, user story
- **CHAINS TO:** building (via saved plan file)
- **RELATED:** oberplan, aposd-designing-deep-modules
