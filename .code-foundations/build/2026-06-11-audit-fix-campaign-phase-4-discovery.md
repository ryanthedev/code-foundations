# Discovery + Design: Phase 4 - Invocation surface

## Files Found

- `skills/aposd-designing-deep-modules/SKILL.md` — exists, 3-line frontmatter, no flags
- `skills/aposd-reviewing-module-design/SKILL.md` — exists, 3-line frontmatter, no flags
- `skills/aposd-simplifying-complexity/SKILL.md` — exists, 3-line frontmatter, no flags
- `skills/aposd-verifying-correctness/SKILL.md` — exists, 3-line frontmatter, no flags
- `skills/ca-architecture-boundaries/SKILL.md` — exists, 3-line frontmatter, no flags
- `skills/cc-control-flow-quality/SKILL.md` — exists, 3-line frontmatter, no flags
- `skills/cc-debugging/SKILL.md` — exists, 3-line frontmatter, no flags
- `skills/cc-defensive-programming/SKILL.md` — exists, 3-line frontmatter, no flags
- `skills/cc-pseudocode-programming/SKILL.md` — exists, 3-line frontmatter, no flags
- `skills/cc-quality-practices/SKILL.md` — exists, 3-line frontmatter, no flags
- `skills/cc-refactoring-guidance/SKILL.md` — exists, 3-line frontmatter, no flags
- `skills/cc-routine-and-class-design/SKILL.md` — exists, 3-line frontmatter, no flags
- `skills/clarify/SKILL.md` — exists, 3-line frontmatter, no flags
- `skills/code-clarity-and-docs/SKILL.md` — exists, 3-line frontmatter, no flags
- `skills/code-standards/SKILL.md` — exists, 3-line frontmatter, no flags
- `skills/gof-design-patterns/SKILL.md` — exists, 3-line frontmatter, no flags
- `skills/performance-optimization/SKILL.md` — exists, 3-line frontmatter, no flags
- `skills/planning/SKILL.md` — exists, 4-line frontmatter, has `user-invocable: false` only
- `skills/welc-legacy-code/SKILL.md` — exists, 3-line frontmatter, no flags
- `references/skill-catalog.md` — does NOT exist (new file required)

## Current State

All 19 skills have valid YAML frontmatter (Phase 1 fixed the two broken ones). None carry
`disable-model-invocation: true`. `planning` has `user-invocable: false` — per-plan constraint,
leave as-is. 14 of 19 descriptions contain "Triggers on:" lists or "Use when..." trigger
engineering language. No near-miss "Not for:" exclusion clauses exist on any skill (audit P1-8).
No skill-catalog.md exists.

## Gaps

| Gap | What's needed |
|-----|---------------|
| `disable-model-invocation: true` absent from all 19 skills | Add to every frontmatter |
| "Triggers on:" language in 14/19 descriptions | Rewrite to honest capability statements |
| Planning description still lists workflow steps | Rewrite (capability-only, no step list) |
| `references/skill-catalog.md` does not exist | Create with 19 entries, family-grouped |

## Code Standards

From `docs/code-standards.md` — conventions that apply here:

- Quote every `description:` value with double quotes (already done post-Phase 1)
- Description formula: `[capability]. Use when [triggers/contexts]. Not for: [near-miss exclusions].` Third person, key use case first, **never workflow steps**
- BUT: Phase 4 instruction supersedes the "Not for:" part — the "Not for:" exclusion-clause guidance is superseded by the catalog, since these skills will not be model-invocable. Descriptions become honest capability statements only.
- `validate_skill` is normative: description must be 1–1024 chars, third person, no XML tags

## DW-4.2: Flag Semantics Verification (before rollout)

**Source:** https://code.claude.com/docs/en/skills (fetched 2026-06-11)

**Frontmatter reference table** (quoted exactly):

> | Field | Required | Description |
> | `disable-model-invocation` | No | Set to `true` to prevent Claude from automatically loading this skill. Use for workflows you want to trigger manually with `/name`. Also prevents the skill from being preloaded into subagents. Default: `false`. |

**Invocation control table** (quoted exactly):

> | Frontmatter | You can invoke | Claude can invoke | When loaded into context |
> | (default) | Yes | Yes | Description always in context, full skill loads when invoked |
> | `disable-model-invocation: true` | Yes | No | Description not in context, full skill loads when you invoke |
> | `user-invocable: false` | No | Yes | Description always in context, full skill loads when invoked |

**Explicit statement** (quoted exactly from the "Restrict Claude's skill access" section):

> **Hide individual skills** by adding `disable-model-invocation: true` to their frontmatter. This removes the skill from Claude's context entirely.

**Conclusion:**
- `disable-model-invocation: true` → description removed from model's context; user `/code-foundations:<name>` slash invocation is retained (confirmed: "You can invoke: Yes" in the table). DW-4.2 **VERIFIED**.

## Test Infrastructure

No traditional test runner. DW items are executable assertions (grep/YAML parse) or recorded evidence (doc citation). Proxy validation per DW-4.5: strict YAML parse of every frontmatter + name-matches-directory check + description length 1–1024 chars.

Validation script approach: `python3 -c "import yaml; ..."` over all 19 frontmatters.

## DW Verification

| DW-ID | Done-When Item | Status | Test Cases |
|-------|----------------|--------|------------|
| DW-4.1 | all 19 skills carry `disable-model-invocation: true` | COVERED | `grep -L 'disable-model-invocation: true' skills/*/SKILL.md` returns empty; implementation adds flag to all 19 |
| DW-4.2 | flag semantics verified before rollout via official docs — doc citation + quoted text in discovery file | COVERED | Doc citation above: code.claude.com/docs/en/skills table row for `disable-model-invocation: true` confirms "You can invoke: Yes, Claude can invoke: No, Description not in context" |
| DW-4.3 | references/skill-catalog.md exists, covers all 19 skills, exactly one matching line each | COVERED | Python count check: `python3 -c "..."` counts catalog entry lines matching `code-foundations:` prefix; expect 19 |
| DW-4.4 | every description is ≤2-sentence capability statement; `grep -n 'Triggers on' skills/*/SKILL.md` returns nothing; no workflow step lists | COVERED | grep assertion post-implementation; manual review of each rewritten description |
| DW-4.5 | validate_skill zero errors ×19 after rewrite — proxy: strict YAML parse + name-matches-directory + description 1–1024 chars | COVERED | Python YAML strict-parse script over all 19 frontmatters; orchestrator re-runs real validator |

**All items COVERED: YES**

## Design Decisions

**Descriptions — capability-only, no trigger engineering:**
Since `disable-model-invocation: true` removes descriptions from model context entirely, trigger optimization is irrelevant. Descriptions serve two readers only: (1) the user in the `/` slash menu picking a skill to invoke manually, (2) the catalog file where per-plan DECOMPOSE matching reads when-to-match rules. The description should state *what the skill provides* — the matching knowledge goes in the catalog.

Formula per phase instruction: ≤2 sentences, ≤~200 chars preferred, what the skill provides, third person, no "Triggers on:" lists, no workflow steps, no "Use when..." trigger engineering. The "Not for:" exclusion-clause guidance from skill-craft.md is superseded by the catalog.

**Disambiguation in catalog vs descriptions:**
The audit's disambiguation knowledge (e.g. reviewing=assessment vs simplifying=transformation; designing=new-module vs routine-and-class=routine-level; debugging=active-bug vs quality-practices=QA-process-design) belongs in the catalog lines, not the descriptions. Descriptions are for humans in the slash menu; catalog lines are for the DECOMPOSE matcher.

**planning skill description:**
Current description lists 8 pipeline steps and has `user-invocable: false`. The step list is the P1-11 finding. Rewrite to capability-only statement. Leave `user-invocable: false` as-is.

**Family grouping in skill-catalog.md:**
Groups: CC (8 skills), APOSD (4), CA (1), GoF (1), WELC (1), misc/standalone (4: clarify, code-clarity-and-docs, code-standards, planning). Header explains the file's role as the DECOMPOSE matching source. Disambiguation knowledge in each line.

## Docs with auto-trigger references (for Phase 7's doc pass — do NOT edit here)

| File | Line(s) | Content | Issue |
|------|---------|---------|-------|
| `CLAUDE.md` | 93 | `VERIFY: performance-optimization + cc-refactoring-guidance + build + tests + lint` | Lists skills by name in gate table — these are now Read()-loaded, not auto-triggered; Phase 7 updates this |
| `CLAUDE.md` | 99 | "skills affect gate policy" | Stale post-Phase 2 (gate keys off `**Gate:**` field, not skill presence); Phase 7 updates this |
| `CLAUDE.md` | 101 | "Cannot proceed to next phase until... REVIEW PASS (Full gate)" — gate table references old model | Phase 7 updates the full gate table to reflect Phase 2 gate contract |

## Prerequisites

- [x] All 19 skills exist and have valid YAML (Phase 1 completed)
- [x] `disable-model-invocation: true` semantics verified via official docs
- [x] `references/` directory exists
- [x] `docs/code-standards.md` conventions reviewed and applied

## Recommendation

BUILD — all prerequisites met, DW items all COVERED with clear test cases, flag semantics verified.
