# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Code-foundations is a Claude Code plugin providing software engineering skills based on *Code Complete* (McConnell) and *A Philosophy of Software Design* (Ousterhout). It includes a lens-based code review system that dispatches one agent per skill for full checklist execution with evidence trails.

## Architecture

### Two Skill Families

| Family | Prefix | Focus |
|--------|--------|-------|
| Code Complete | `cc-*` | Process rigor, metrics, checklists |
| APOSD | `aposd-*` | Design philosophy, complexity reduction |

### Directory Structure

- `skills/` - Individual skill definitions (SKILL.md + checklists.md)
- `commands/` - User-invocable commands (slash commands)
- `agents/lens/` - Lens-based review system (config + agent template)
- `references/` - Shared reference materials (including `cc-foundations.md` for shared CC vocabulary)
- `docs/` - Case study examples

### Lens-Based Code Review System

Reviews dispatch **one agent per skill**, each executing their full checklist with evidence.

| Level | Command | Skills | Agents | Checklist Items |
|-------|---------|--------|--------|-----------------|
| 1 | `/review-commit` | 0 | 0 | Quick scan (direct execution) |
| 2 | `/review-changes` | 7 | 7 | ~360 |
| 3 | `/review-pr` | 9 | 9 | ~548 |

### Review Categories & Skills

| Category | Skills | Items |
|----------|--------|-------|
| **defensive** | cc-defensive-programming, aposd-simplifying-complexity | 75 |
| **quality** | aposd-reviewing-module-design, cc-code-layout-and-style, cc-control-flow-quality | 221 |
| **correctness** | aposd-verifying-correctness, cc-quality-practices | 146 |
| **performance** | cc-performance-tuning, aposd-optimizing-critical-paths | 80 |
| **documentation** | cc-documentation-quality | 26 |

### Lens System Configuration

Edit `agents/lens/config.yaml` to add/remove skills:

```yaml
review-changes:
  categories:
    quality:
      skills:
        - aposd-reviewing-module-design
        - cc-code-layout-and-style
        - new-skill  # ← add here
```

No code changes needed when modifying skills.

### Master Dispatcher Flow

The `code-foundations` skill (`skills/code-foundations/SKILL.md`) is the entry point:
1. Classifies task type (WRITE, DEBUG, REVIEW, OPTIMIZE, REFACTOR, SIMPLIFY, SECURE)
2. Runs mindset check via `cc-developer-character`
3. Routes DEBUG tasks to `cc-debugging` (scientific method)
4. Executes task-specific checklist
5. Runs pre-commit gate via `aposd-verifying-correctness`

### Development Workflows

**Choose based on scope:**

| Situation | Command | Ceremony |
|-----------|---------|----------|
| Quick hack, TDD, pair programming | `/code-foundations:hack` | None |
| Technical uncertainty | `/code-foundations:prototype` | Minimal |
| Feature needs planning | `/code-foundations:whiteboarding` | Medium |
| Executing approved plan | `/code-foundations:building` | Full |

### Hack Mode

```
/code-foundations:hack [what to build]
→ RED: Write failing test
→ GREEN: Minimum code to pass
→ REFACTOR: Clean up
→ REPEAT
```

No plans, no checkpoints, no subagents. Direct code slinging.

### Prototype → Whiteboarding → Building Workflow

Three-stage pattern for feature development:

| Command | Purpose | Output |
|---------|---------|--------|
| `/code-foundations:prototype` | Prove feasibility with minimum code | Prototype log in `docs/prototypes/` |
| `/code-foundations:whiteboarding` | Discovery-oriented brainstorming | Plan file in `docs/plans/` |
| `/code-foundations:building` | Checklist-based execution | Working code + tests |

**Full Flow:**
```
/code-foundations:prototype "can I show a notification?"
  → One question to prove
  → Minimum code (~50 lines max)
  → Binary answer: YES/NO/PARTIAL
  → Capture learnings to docs/prototypes/

        ↓ (if feasible)

/code-foundations:whiteboarding "build notification system"
  → Discovery questions (informed by prototype)
  → 2-3 approaches with trade-offs
  → Implementation-ready plan
  → Save to docs/plans/YYYY-MM-DD-<topic>.md

        ↓ (after plan approval)

/code-foundations:building docs/plans/<plan>.md
  → Feature branch required
  → Execute phases with quality gates
  → Per-phase commits + reviewer agent
  → Final verification + report
```

**When to use each:**

| Situation | Command |
|-----------|---------|
| "Can I do X?" / technical uncertainty | `/code-foundations:prototype` |
| Ready to plan full feature | `/code-foundations:whiteboarding` |
| Plan exists, ready to implement | `/code-foundations:building` |

**Quality Gates (per phase during /code-foundations:building):**
```
PRE-GATE:  cc-pseudocode-programming + aposd-designing-deep-modules
IMPLEMENT: Write code, run tests
POST-GATE: aposd-verifying-correctness + cc-defensive-programming + reviewer agent
CHECKPOINT: Commit only after all gates pass
```

Cannot proceed to next phase until current phase passes all gates including reviewer agent PASS.

## Skill File Structure

```
skills/<skill-name>/
├── SKILL.md         # Main skill definition with YAML frontmatter
├── checklists.md    # Detailed checklists
├── hard-data.md     # Research/data backing the skill
└── language-notes.md # Language-specific guidance (optional)
```

## Review Output Format

Reviews are **grouped by action type** (what to do next):

```markdown
## Fix
High confidence. Apply now.
1. 🔴 [CRITICAL] file:line - Issue (agent)
   ```lang
   [code to apply]
   ```

## Investigate
Low confidence. Need context first.
1. 🟡 [IMPORTANT] file:line - Issue (agent)
   Check: [what to investigate]
   **Unknown**: [missing context]

## Plan
Systemic. Spin off to whiteboarding.
1. 🔴 [CRITICAL] Multiple files - Issue
   → `/code-foundations:whiteboarding "[topic]"`

## Decide
Trade-off needing human judgment.
1. 🟡 [IMPORTANT] file:line - Issue (agent)
   Options: A vs B
   **Unknown**: [what would inform decision]
```

### Action Types

| Action | When | Output |
|--------|------|--------|
| **Fix** | High confidence, localized | Code snippet |
| **Investigate** | Low confidence | What to check |
| **Plan** | Systemic (many files) | `/code-foundations:whiteboarding` topic |
| **Decide** | Trade-off | Options for human |

**Key principle**: State what you DON'T know (**Unknown** section).

### Execution (THE LAW)

After review, **execute to completion**:

| Action | Execution |
|--------|-----------|
| **Fix** | Dispatch subagent with `code-foundations` → implement → verify |
| **Investigate** | Dispatch subagent with `cc-debugging` → resolve → fix or escalate |
| **Plan** | Output ready-to-copy prompt for new `/code-foundations:whiteboarding` session |
| **Decide** | Ask user → execute based on response |

**Do not stop until all items are resolved.**

## Severity Levels

- **CRITICAL** 🔴 - Blocks merge (security, correctness)
- **IMPORTANT** 🟡 - Should fix (design, quality)
- **SUGGESTION** 🟢 - Consider (improvements)

## Key Concepts

**APOSD Complexity Symptoms:**
- Change amplification (simple change → many modifications)
- Cognitive load (must know too much)
- Unknown unknowns (worst)

**CC Metrics:**
- Cohesion (routine does ONE thing)
- Coupling (minimized dependencies)
- Parameters ≤7, Inheritance depth < 3

**CC Skills (15 total):**
All CC skills reference `references/cc-foundations.md` for shared vocabulary (cohesion spectrum, coupling criteria, key metrics).

New skills added:
- `cc-debugging` - Scientific debugging (Chapter 23): STABILIZE → LOCATE → HYPOTHESIZE → EXPERIMENT → FIX → TEST → SEARCH
- `cc-table-driven-methods` - Replace complex logic with tables (Chapter 18): direct access, indexed access, stair-step access

## Publishing

### Plugin Structure

- `.claude-plugin/plugin.json` - Plugin manifest with name, version, description
- Version follows semver (e.g., 2.7.1)

### Marketplace

Published to `ryanthedev/rtd-claude-inn` marketplace:

**Marketplace files:**
- `~/repos/rtd-claude-inn/.claude-plugin/marketplace.json` - Plugin registry with versions
- `~/repos/rtd-claude-inn/README.md` - Marketplace documentation with version table

**To publish a new version:**
1. Bump version in `.claude-plugin/plugin.json`
2. Commit and push to `origin/main`
3. Update `marketplace.json` in rtd-claude-inn with new version
4. Update README.md version table
5. Commit and push rtd-claude-inn

**Install commands:**
```bash
/plugin marketplace add ryanthedev/rtd-claude-inn
/plugin install code-foundations@rtd
/plugin update code-foundations@rtd
```
