<!-- base-commit: e455f11 -->
# code-foundations authoring standards

This repo is a Claude Code plugin: the "code" is skill/command/agent markdown. These are the conventions LLM-written edits must follow. Derived from the 2026-06 full audit, grug decision memos, and oberskills:skill-craft doctrine.

## Frontmatter

- Quote every `description:` value with double quotes. Unquoted descriptions containing `:` (e.g. `Triggers on:`) are invalid YAML and break spec-compliant hosts and the eval harness.
  ```yaml
  # Good (skills/gof-design-patterns/SKILL.md)
  description: "Use when applying or selecting a Gang of Four design pattern. Triggers on: design pattern, ..."
  # Bad (broke performance-optimization)
  description: Use when code is too slow. Triggers on: profiler hot spots, ...
  ```
- `name` must match the directory name; lowercase alphanumeric + hyphens.
- Description formula: `[capability]. Use when [triggers/contexts]. Not for: [near-miss exclusions].` Third person, key use case first, concrete trigger nouns, **never workflow steps**.

## File references (grug: plugin-root-must-be-braced)

- Inside SKILL.md bodies → `${CLAUDE_SKILL_DIR}/checklists.md` (or `${CLAUDE_PLUGIN_ROOT}/skills/<name>/...`).
- Inside commands/, agents/, hooks → `${CLAUDE_PLUGIN_ROOT}/references/...`.
- NEVER: bare relative paths (resolve against user CWD), unbraced `$CLAUDE_PLUGIN_ROOT` (passed literally to Read), invented vars (`$SKILL_DIR`).
- Cross-skill handoffs name the fully qualified skill: `Skill(code-foundations:welc-legacy-code)` — bare names are not invocable.

## Structure

- SKILL.md body < 500 lines hard, ~200-line core preferred. Every bundled file (checklists.md, hard-data.md, language-notes.md, references/*) must be linked from SKILL.md or deleted — orphans never load and drift.
- One canonical home per fact. Before "deduplicating" commands/build.md, read grug `build-command-progressive-disclosure`: Gate Policy, Model Resolution, Skill Resolution, Execution Loop are **deliberately inline**; the REVIEW debias rule is **deliberately duplicated** (build.md + dispatch-templates § REVIEW); commit recipe lives only in references/commit-format.md.
- References > 100 lines need a Contents/ToC heading.
- No stated item counts ("Total items: N") — they drift; 6 of 7 were wrong at audit.

## Voice and constructs

- No banned constructs: anti-rationalization tables (`| Myth | Reality |`, `| Pattern | Reality |`), self-assessed compliance checklists ("Did I follow the workflow?"), self-directed "Red Flags — STOP" sections. Replace with checkable gates ("proceed only when X", artifact/output-shape requirements) — welc-legacy-code is the house model.
- No CRISIS/STOP/NEVER-SKIP shouting blocks, no scripted user-pushback lines, no emergency-bypass ceremony, no human-time bounds ("takes 1-2 hours"). State a rule once, neutrally.
- Write to Claude, not about the domain: cut textbook definitions Claude already knows; keep the project-opinionated rules and decision tables.
- Checklist items must be externally checkable assertions about artifacts, phrased so checked = satisfied.

## Commands and agents

- Title commands `# Command: <name>` (not `# Skill:`).
- Command descriptions are trigger-bearing and concrete (model: research.md), with `argument-hint` when the command takes input.
- Dispatch templates and agent files share seam contracts: a placeholder in a template must name its source rule; paths written by parallel-dispatched agents must be parameterized per sample.

## Verification gates for any skill/command edit

1. `validate_skill` on every touched skill dir — zero errors required.
2. Description changed → re-run `test_triggers` (existing query sets: `.skill-audit/trigger-workspaces/<skill>-workspace/trigger-queries.json`).
3. Workflow semantics changed → re-run the skill's behavioral eval (`.skill-audit/<skill>/evals.json`).
