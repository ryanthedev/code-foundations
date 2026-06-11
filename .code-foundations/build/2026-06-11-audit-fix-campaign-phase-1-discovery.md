# Discovery + Design: Phase 1 - Mechanical floor sweep

## Files Found

**11 YAML description files to quote:**
- `skills/performance-optimization/SKILL.md` (line 3) — unquoted, contains `Triggers on:`
- `skills/code-clarity-and-docs/SKILL.md` (line 3) — unquoted, contains `Triggers on:`
- `skills/gof-design-patterns/references/gof-singleton.md` (line 4) — contains `; Symptoms:`
- `skills/gof-design-patterns/references/gof-abstract-factory.md` (line 4)
- `skills/gof-design-patterns/references/gof-builder.md` (line 4)
- `skills/gof-design-patterns/references/gof-decorator.md` (line 4)
- `skills/gof-design-patterns/references/gof-facade.md` (line 4)
- `skills/gof-design-patterns/references/gof-factory-method.md` (line 4)
- `skills/gof-design-patterns/references/gof-prototype.md` (line 4)
- `skills/gof-design-patterns/references/gof-proxy.md` (line 4)
- `skills/gof-design-patterns/references/gof-state.md` (line 4)

**11 checklist files with `Total items: N` lines (7 unique skills, 11 instances):**
- `skills/cc-routine-and-class-design/checklists.md:90`
- `skills/cc-refactoring-guidance/checklists.md:72`
- `skills/cc-defensive-programming/checklists.md:132`
- `skills/aposd-reviewing-module-design/checklists.md:108`
- `skills/aposd-simplifying-complexity/checklists.md:102`
- `skills/cc-pseudocode-programming/checklists.md:115`
- `skills/cc-debugging/checklists.md:150`
- `skills/aposd-verifying-correctness/checklists.md:100`
- `skills/aposd-designing-deep-modules/checklists.md:86`
- `skills/performance-optimization/checklists.md:127`
- `skills/code-clarity-and-docs/checklists.md:171`

**4 command files with wrong title prefix:**
- `commands/build.md:5` — `# Skill: build`
- `commands/plan.md:5` — `# Skill: plan`
- `commands/research.md:5` — `# Skill: research`
- `commands/debug.md:5` — `# Skill: cc-debugging`

**2 path fixes:**
- `skills/cc-debugging/SKILL.md:123` — `Read skills/cc-debugging/checklists.md`
- `skills/gof-design-patterns/SKILL.md:95` — `skills/gof-design-patterns/references/`

**23 CSO KEYWORDS sections to delete** (one per gof reference file, always the final section, `## CSO KEYWORDS` heading + keyword bullet lines to EOF).

## Current State

All 6 categories of defects confirmed present via baseline grep/parse checks:
- DW-1.2: Ruby YAML safe_load fails both skills with "mapping values are not allowed" at the `: ` inside unquoted descriptions
- DW-1.3: 11 `Total items:` lines across 11 checklist files
- DW-1.4: All 4 command files have `# Skill:` not `# Command:` at line 5
- DW-1.5: 23 `## CSO KEYWORDS` sections confirmed across all 23 gof reference files
- DW-1.6: 11 unquoted description lines match `description: [^"|>].*: `

## Gaps

None. Plan assumptions match reality exactly. The `pyyaml` module is not installed (Python 3.14 brew install has a broken libexpat dependency), but Ruby stdlib YAML is available and is a valid strict YAML parser that confirms the same parse failures. DW-1.2 proxy check uses ruby instead of python3.

## Assumption Verification

**Assumption:** quoting is strictly additive; description VALUE must be byte-identical after unquoting.
**Status: CONFIRMED VALID.** All 11 descriptions are plain scalar text — no characters that require escaping in double-quoted YAML style (no backslashes, no embedded double quotes). Wrapping with `"..."` preserves the value byte-for-byte.

## Code Standards

Key conventions from `docs/code-standards.md` that apply:
- `description:` must be double-quoted (the exact defect being fixed)
- File references inside SKILL.md bodies use `${CLAUDE_SKILL_DIR}/...`; commands/agents use `${CLAUDE_PLUGIN_ROOT}/...`
- Commands titled `# Command: <name>` not `# Skill:`
- No stated item counts (`Total items: N`) — they drift

## Test Infrastructure

No automated test framework. Tests are executable shell assertions (grep, ruby yaml parse). The plan specifies: run each assertion before changes (expect FAIL), implement, re-run (expect PASS). All pre-change baseline checks run above and confirm RED state.

## DW Verification

| DW-ID | Done-When Item | Status | Test Cases |
|-------|----------------|--------|------------|
| DW-1.1 | `validate_skill` zero errors for all 19 skill dirs (orchestrator-run; proxy: DW-1.2 + DW-1.6 + no YAML parse errors) | COVERED | After fixing DW-1.2 and DW-1.6, verify no other YAML issues exist via ruby YAML parse of all 19 SKILL.mds |
| DW-1.2 | ruby/python strict YAML parse of performance-optimization and code-clarity-and-docs frontmatter succeeds | COVERED | `ruby -e "require 'yaml'; ..."` on both files — baseline FAIL confirmed, expect PASS after quoting |
| DW-1.3 | `grep -rn "Total items" skills/` returns nothing | COVERED | grep count = 0 after deleting all 11 lines |
| DW-1.4 | 4 command files titled `# Command: <name>` (grep -L returns nothing) | COVERED | `grep -L '^# Command: ' commands/*.md` returns empty after retitling 4 files |
| DW-1.5 | `grep -rn "CSO KEYWORDS" skills/` returns nothing | COVERED | grep count = 0 after deleting 23 sections |
| DW-1.6 | `grep -rEn 'description: [^"|>].*: ' skills/` returns nothing | COVERED | grep returns empty after quoting all 11 descriptions |

**All items COVERED:** YES

## Design Decisions

**YAML quoting style:** Use double-quoted strings (`"..."`) for all 11 descriptions. None contain embedded double quotes or backslashes, so no escaping is needed. This matches the code-standards.md example (`description: "..."`) and is the simplest additive change.

**CSO KEYWORDS deletion:** Each `## CSO KEYWORDS` section is the final section in its file (verified). Deletion = truncate file at the line before `## CSO KEYWORDS`. The heading line and all following content (keyword bullets) go. Blank lines between prior section and CSO heading are preserved as the file ending if they exist, but since CSO is last, truncation to just before the heading is cleanest.

**Total items deletion:** Each occurrence is a standalone line preceded by `---`. Delete just the `Total items: N` line. The surrounding `---` separators remain (they are structure, not count-specific).

**Command retitling:** The debug command is titled `# Skill: cc-debugging` — it gets retitled `# Command: debug` (the command name matches the filename). Build, plan, research get their filename as the command name.

**Path fixes:** Exact substitutions per plan:
- `Read skills/cc-debugging/checklists.md` → `Read(${CLAUDE_SKILL_DIR}/checklists.md)`
- `skills/gof-design-patterns/references/` → `${CLAUDE_SKILL_DIR}/references/`

## Prerequisites

- [x] All target files exist and are readable
- [x] Ruby YAML available for DW-1.2 proxy check
- [x] Feature branch confirmed: `feature/audit-fix-campaign`

## Recommendation

BUILD — all defects confirmed present, all fixes deterministic, no judgment required.
