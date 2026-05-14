# Idea: Static Analysis Rules from Code Discovery

## Problem

The `code-standards` skill scans a codebase and produces `docs/code-standards.md` — a prose file of conventions for LLM consumption. The scan discovers real invariants (forbidden patterns, dependency direction, banned APIs, naming rules) but discards them as human-readable text.

Prose guidance is probabilistic. Static analysis rules are deterministic. In agentic workflows where agents generate code at scale, you need hard enforcement gates, not soft suggestions.

## Core Insight

The discovery scan already does the hard work. The same findings that produce `code-standards.md` could produce executable rule files. Two output paths from one scan:

```
Scan → docs/code-standards.md         (LLM guidance, existing)
     → docs/static-analysis-rules/    (machine-enforced rules, new)
```

## What Maps to Static Rules

| Discovery finding | Rule type |
|---|---|
| "Never use X, use Y instead" | semgrep pattern (any language) |
| Import ordering | eslint `import/order` config |
| Dependency direction (services can't import routes) | `no-restricted-imports` or dependency-cruiser |
| Banned APIs or packages | semgrep or `no-restricted-imports` |
| Naming conventions | eslint `@typescript-eslint/naming-convention` |
| Structural patterns ("all DB calls via X") | semgrep with metavariable matching |

**Does not map well:** Higher-level design principles, cohesion quality, "prefer composition" — these stay as prose.

## Architecture Options

**Option A — Extend code-standards** — Add a step 6 to the existing skill that codifies what was already found. Simple, but couples two concerns.

**Option B — New skill: `static-analysis-rules`** — Reads `docs/code-standards.md` as input (or re-runs the scan) and generates rule files. Cleaner separation, can be invoked independently or chained.

**Option C — Parallel output path** — Same scan, two simultaneous outputs. Tightest integration but couples them at the scan level.

Option B is preferred: `code-standards` stays focused on LLM guidance, the new skill handles machine enforcement. They share the same discovery findings as input/output.

## New Skill Sketch: `static-analysis-rules`

**Input:** `docs/code-standards.md` (or raw codebase if generating fresh)

**Steps:**
1. Read `code-standards.md` and classify each finding as codifiable vs. prose-only
2. For each codifiable finding, generate a rule in the appropriate format
3. Run the rules against the codebase to check false-positive rate
4. Tune patterns where FP rate is high
5. Write output to `docs/static-analysis-rules/`

**Output format:** Semgrep YAML as primary (universal, any language), plus tool-specific configs where relevant (eslint config additions, dependency-cruiser rules).

**Verification loop:** Generate → run → check FPs → tune. The codebase is the ground truth. A rule that fires on 80% of existing code is wrong.

## The Deeper Play: Invariant Mining

Beyond translating prose standards into rules, a more powerful approach is direct invariant mining from AST structure:

1. AST-query the codebase to find structural patterns
2. Cluster similar patterns — things that *should* be uniform but aren't reveal missing rules
3. Identify invariants that hold across all files → codify them
4. Encode module boundaries discovered from actual import graphs → dependency rules

This produces rules the team didn't consciously know they had. The codebase is the spec.

## Fit in the Existing Ecosystem

- `code-standards` skill already exists and does the scan — natural predecessor
- `ast-grep` skill already exists — can be used in the discovery/rule-writing phase
- New skill slots between `code-standards` and the building workflow
- Rules can be run as part of the VERIFY phase in `/code-foundations:building`

## Open Questions for Discovery

- Which rule format has best coverage across the projects this gets used on? (semgrep vs. ast-grep vs. eslint)
- Can the skill auto-detect which tools are installed and target accordingly?
- How do you handle rule maintenance as the codebase evolves? (same staleness logic as code-standards?)
- Should generated rules live in `docs/` (owned by the skill) or in project root config files (owned by the team)?
