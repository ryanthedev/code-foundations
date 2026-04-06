# Pseudocode: Phase 1 - Create whiteboarding-planning skill

## DW Verification

| DW-ID | Done-When Item | Status | Pseudocode Section |
|-------|---------------|--------|-------------------|
| DW-1.1 | `skills/whiteboarding-planning/SKILL.md` exists and is under 320 lines | COVERED | Overall structure + all sections |
| DW-1.2 | All Standard/Full pipeline steps (DISCOVER through HANDOFF) are present | COVERED | Steps 1-8 sections |
| DW-1.3 | Plan schema is one merged template with `[Medium/Complex only]` markers (or two short schemas if markers exceed 30%) | COVERED | Merged Plan Schema section |
| DW-1.4 | Questioning protocol replaced with "load clarify skill" (no duplication) | COVERED | Step 1: DISCOVER section |
| DW-1.5 | Skill assignment requires `**Skills:**` on every phase -- `none -- [reason]` valid, omission not | COVERED | Step 5: SAVE section |

**All items COVERED:** YES

## Files to Create
- `skills/whiteboarding-planning/SKILL.md` (new, ~300 lines target, hard cap 320)

## Design Notes

### Merged Schema Decision
The plan prefers a merged schema with `[Medium/Complex only]` markers. Analysis shows markers cover ~39% of lines by strict count, but the additions cluster into 4-5 distinct blocks (Chosen Approach, Rejected Approaches, per-phase extras, Assumptions, Decision Log). Using block markers like `[Medium/Complex only: begin]`/`[end]` keeps the reading experience clean. Since the whole-section markers are easy to skip visually, this passes the readability test despite borderline percentage. Proceeding with merged approach.

### Trimming Strategy
Need to cut from ~883 raw lines to ~300. Major cuts:
- Questioning protocol: 45 lines -> 5 lines (delegate to clarify skill)
- Code-standards template: 49 lines -> 10 lines (section list only)
- Two plan schemas: 190 lines -> 55 lines (one merged schema)
- Crisis invariants: 19 lines -> 0 (fold into steps)
- Quick Reference: 15 lines -> 0 (redundant)
- "What Plan Specifies" table: 27 lines -> 0 (docs, not instruction)
- EXPLORE verbose formats: compress research/approach sections
- DETAIL verbose examples: keep rules, cut approach notes examples
- CHECK subagent prompt: compress to essentials
- CONFIRM test coverage options: compress
- Duplicate phase template in Simple schema: remove (one template per track inline)

### Crisis Invariant Folding
These non-obvious invariants need to be preserved by folding into their steps:
- "Search before questions" -> fold into Step 1 as ordering enforcement
- "Research before approaches" -> fold into Step 3 as prerequisite
- "Save before checking" -> fold into Step 5/6 boundary
- "Plans must be pipeline-compatible" -> fold into Step 4 as constraint
- "Include approach notes for non-discoverable decisions" -> fold into Step 4
- Others are obvious from step ordering (classify before detail, etc.) or already stated (one question at a time is in clarify skill)

## Pseudocode

### skills/whiteboarding-planning/SKILL.md [DW-1.1, DW-1.2, DW-1.3, DW-1.4, DW-1.5]

```
FRONTMATTER:
  name: whiteboarding-planning
  description: "Standard/Full planning pipeline for whiteboarding.
    Steps: discover, classify, explore, detail, save, check, confirm, handoff.
    Use when dispatched from whiteboarding command for Medium/Complex tasks."

TITLE: "Skill: whiteboarding-planning"
Subtitle: "Standard/Full planning pipeline — DISCOVER through HANDOFF"

---

SECTION: Pipeline Overview
  Text: Pipeline steps, ordered with dependencies
  "Discover -> Classify -> Explore -> Detail -> Save -> Check -> Confirm -> Handoff"
  
  Note about thinking effort: suggest max before proceeding
  
  Subsection: Load Design Standards
    Read pre-gate-standards.md before any work
  
  Subsection: Create Progress Tasks
    TaskCreate for all 9 tasks (same as current but compressed format)
    Set blockedBy for ordering
    Medium track: skip CHECK

---

SECTION: Step 1 - DISCOVER [DW-1.2, DW-1.4]
  
  Subsection: 1a - Codebase Search (MANDATORY first)
    Check for docs/code-standards.md:
      If exists: read, check staleness via git rev-list
        0 commits -> trust, skip search
        1-20 -> spot-check
        20+ -> full re-scan
      If missing: full search + generate
    
    Full search checklist (compressed, no prose):
      Similar features, module patterns, related components, conventions
    
    Code-standards output format (SECTION LIST ONLY, not full template) [DW-1.4 partial]:
      Architecture, Naming, Imports, Error Handling, File Organization,
      Testing, Technology Decisions, Forbidden Patterns, Similar Implementations
      (just the section names with 1-line descriptions, not the full markdown template)
    
    Migration note: code-patterns.md -> code-standards.md
    Reference link: pattern-reuse-gate.md
  
  Subsection: 1b - Clarify Intent [DW-1.4]
    "Load clarify skill: Skill(code-foundations:clarify)"
    Use its framework for fault classification + hypothesis-driven questions.
    
    Enforcement: each question via AskUserQuestion (not text)
    Short-circuit: zero questions if already clear
    
    (NO questioning protocol duplication — 5 lines max, delegate to clarify skill)
  
  Subsection: Questioning Gate
    Compressed checklist: codebase searched, complexity classified,
    hypotheses converged, each Q via AskUserQuestion, each A received
  
  Subsection: Output - Problem Statement
    Template: Problem Statement + Constraints + Success Criteria (compressed)
    Confirm via AskUserQuestion

---

SECTION: Step 2 - CLASSIFY [DW-1.2]
  Signal table (same as current):
    Files touched, patterns, cross-cutting, uncertainty, phase count
    -> Simple / Medium / Complex
  
  State classification explicitly (same enforcement text)
  
  Track overview table (compressed):
    Simple: 1-2 phases, flat, skip approach comparison
    Medium: 3-5 phases, contract, 2 approaches
    Complex: 5-7 phases, full contract, 2-3 + pre-mortem
  
  Hard cap: 7 phases

---

SECTION: Step 3 - EXPLORE [DW-1.2]
  Simple: skip (exception: conflicting patterns -> quick 2-approach)
  
  Subsection: Research (Medium/Complex)
    Fold crisis invariant: "Research BEFORE proposing — uninformed proposals waste decisions"
    Codebase research checklist (compressed to 4 items)
    Web research: when to use + search pattern (compressed)
  
  Subsection: Generate Alternatives
    Must be structurally different (keep the good/bad examples)
    Table format: approach, trade-offs, best when, research source
  
  Subsection: Pre-Mortem (Complex only)
    Failure mode table format (compressed)
  
  Subsection: Decision
    Ask preference, record chosen approach + rationale + fallback

---

SECTION: Step 4 - DETAIL [DW-1.2]
  
  Subsection: The Plan Is a Contract
    Keep the 4-reader table (orchestrator, pre-gate, post-gate, human)
    Fold crisis invariant: "No implementation details in phases"
    Fold: "Plans must be pipeline-compatible — deterministic rules, not interactive prompts"
  
  Subsection: Phase Template (one template covering both tracks)
    Simple fields shown as base, Medium/Complex extras marked inline
    
    ```
    ### Phase N: [Name]
    **Model:** [recommended model]
    **Skills:** [assigned at SAVE — skills or `none — [reason]`]
    **Goal:** [One sentence | 1-2 sentences for Medium/Complex]
    **Scope:**
    - IN: [covered]
    - OUT: [excluded]
    **Constraints:** [non-discoverable requirements -- omit if none]
    [Medium/Complex only] **Approach notes:** [non-discoverable user decisions]
    [Medium/Complex only] **File hints:** [paths + why relevant]
    [Medium/Complex only] **Depends on:** [Phase X] | **Unlocks:** [Phase Y]
    **Done when:**
    - [ ] DW-N.1: [verifiable criterion]
    [Medium/Complex only] **Difficulty:** LOW / MEDIUM / HIGH
    [Medium/Complex only] **Uncertainty:** [what could change, or "None"]
    ```
  
  DW-ID format note: DW-{phase}.{item}
  
  Subsection: Approach Notes rule (compressed)
    Only non-discoverable user decisions. Test: could codebase search find it?
    2 good examples, 2 bad examples (cut verbose current set)
  
  Subsection: YAGNI Gate (compressed)
    3 questions before each phase
    Phase granularity test (keep, it's load-bearing)
  
  Subsection: Phase Count + Dependencies (compressed)
    Table: Simple 1-2, Medium 3-5, Complex 5-7
    Prefer fewer phases. 200-word cap per phase.
    DAG guidance (1-2 sentences, not a paragraph)

---

SECTION: Step 5 - SAVE [DW-1.2, DW-1.3, DW-1.5]
  
  File location: docs/plans/YYYY-MM-DD-<topic-slug>.md
  
  Subsection: Model Detection + Skill Assignment [DW-1.5]
    Model detection rules (same logic, compressed format):
      OPUS_KEYWORDS, HAIKU_KEYWORDS, threshold rules
    
    Skill assignment (EVERY phase MUST have Skills field) [DW-1.5]:
      1. Scan system-reminder for available skills
      2. Match to phase goal/scope/work type
      3. Exclude workflow commands
      4. Write Skills on every phase — `none — [reason]` valid, omission NOT valid
    
    Fold crisis invariant: "Save before checking — subagent needs a file"
  
  Subsection: Merged Plan File Schema [DW-1.3]
    One schema with block markers for Medium/Complex sections:
    
    ```
    # Plan: [Topic]
    **Created:** YYYY-MM-DD
    **Status:** ready
    **Complexity:** [simple/medium/complex]
    ---
    ## Context
    [Problem statement]
    ## Constraints
    - [constraints]
    
    [Medium/Complex only]
    ## Chosen Approach
    **[Name]** [Rationale] **Fallback:** [sentence]
    ## Rejected Approaches
    - **[Name]:** [why rejected]
    [/Medium/Complex only]
    
    ---
    ## Implementation Phases
    (use phase template from Step 4)
    ---
    ## Test Coverage
    **Level:** [100% / Backend only / Backend + frontend / None / Per-phase]
    ## Test Plan
    - [ ] [tests]
    [Medium/Complex only] - [ ] Integration: / Manual:
    
    [Medium/Complex only]
    ## Assumptions
    | Assumption | Confidence | Verify Before Phase | Fallback |
    ## Decision Log
    | Decision | Alternatives | Rationale | Phase |
    [/Medium/Complex only]
    
    ---
    ## Notes
    - [edge cases, gotchas, open questions]
    ---
    ## Execution Log
    _To be filled during building_
    ```
    
    Marker burden check: 4 block markers, 2 inline in test plan = ~6 marked regions.
    Marked lines: ~18 out of ~55 total = ~33%. Borderline but readable because
    blocks are visually distinct sections, not scattered inline markers.
  
  Subsection: Save + Commit
    mkdir -p docs/plans
    git add + commit (mandatory — worktrees need committed files)

---

SECTION: Step 6 - CHECK [DW-1.2]
  Simple: skip (mark completed)
  
  Medium/Complex: dispatch subagent
    Fold crisis invariant: "Fresh context review catches gaps you're blind to"
    
    Compressed subagent prompt (keep checklist, cut prose):
      Structural completeness (11 items)
      Cross-phase coherence (4 items)
      Skills audit (3 items)
    
    After return: PASS -> proceed, FINDINGS -> fix then proceed

---

SECTION: Step 7 - CONFIRM [DW-1.2]
  Present plan + review results
  Simple: "Does this look right?"
  Medium/Complex: structured summary (phases, constraint coverage, review results)
  
  Test coverage question (mandatory):
    5 options: 100%, backend, backend+frontend, none, per-phase
    Record in plan file
  
  Corrections: update plan, re-run CHECK if structural, re-present if minor

---

SECTION: Step 8 - HANDOFF [DW-1.2]
  AskUserQuestion with 2 options:
    1. Build now (suggest default thinking effort, run /code-foundations:building)
    2. Tell me what to do (numbered manual steps)

---

SECTION: Chain (footer)
  Receives from: whiteboarding command (router dispatch)
  Chains to: building (via saved plan file)
  Related: oberplan, aposd-designing-deep-modules
```

## Line Budget Estimate

| Section | Estimated Lines |
|---------|----------------|
| Frontmatter + title + overview | 30 |
| Step 1: DISCOVER | 50 |
| Step 2: CLASSIFY | 25 |
| Step 3: EXPLORE | 35 |
| Step 4: DETAIL | 55 |
| Step 5: SAVE | 60 |
| Step 6: CHECK | 30 |
| Step 7: CONFIRM | 25 |
| Step 8: HANDOFF | 12 |
| Chain footer | 5 |
| **Total** | **~327** |

This is over the 320-line hard cap by ~7 lines. Need to trim further during implementation:
- CONFIRM can be tighter (compress test coverage options to a list, not block format)
- CHECK subagent checklist can use tighter formatting
- Step 4 approach notes examples can be 1 good + 1 bad instead of 2+2

Revised estimate after these micro-cuts: ~310-315 lines. Within budget.
