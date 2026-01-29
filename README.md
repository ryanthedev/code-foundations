# Code Foundations

> **Experimental** - This plugin is under active development, currently incorporating knowledge from *Code Complete* and *A Philosophy of Software Design*, with more books planned. Subagent orchestration for plan execution is being fine-tuned to ensure reliable skill loading and phase execution. GitHub releases will be added once the plugin reaches a stable state.

Software engineering skills for Claude Code based on *Code Complete* and *A Philosophy of Software Design*.

---

## `/code-foundations:whiteboarding` — Planning That Investigates First

Most AI planning modes ask you questions, take your answers at face value, then generate a plan. **Whiteboarding inverts this:** it searches your codebase and researches technologies *before* asking anything.

```
User: "/code-foundations:whiteboarding preserve z-index when applying layout"

  SEARCH FIRST (before any questions)
  ├─ Grep for similar features
  ├─ Read nearby files for patterns
  ├─ Find how similar problems were solved
  └─ Note naming conventions, error handling patterns

  ASK ONE QUESTION AT A TIME (not a wall of questions)
  ├─ "What should 'preserving z-index' mean?"
  │   ☐ Frontmost window gets focus
  │   ☐ Preserve stacking order in cell
  │   ☐ Both
  └─ Wait for answer → ask next question

  RESEARCH BEFORE PROPOSING (not guessing)
  ├─ Check existing dependencies (don't propose new lib if similar exists)
  ├─ Web search for current best practices
  └─ User can push back: "you should research" → triggers deeper investigation

  2-3 STRUCTURALLY DIFFERENT APPROACHES (not variations)
  ├─ Option A: Server-side z-order field (recommended)
  ├─ Option B: CLI requests z-order on-demand
  └─ Option C: Infer from focus history

  → Saves to docs/plans/YYYY-MM-DD-<topic>.md
  → Execute with /code-foundations:building
```

### What Makes It Different

| Other Plan Modes | Whiteboarding |
|-----------------|---------------|
| Ask user about existing patterns | **Search codebase** — user may not know all patterns |
| Batch questions into a wall | **One question at a time** — better answers |
| Recommend based on training data | **Research first** — your codebase, current best practices |
| First approach wins | **2-3 structurally different approaches** — comparison reveals trade-offs |
| Plan lives in conversation | **Persistent plan file** — survives context refresh, enables `/building` execution |

---

## `/code-foundations:building` — Gated Execution With Fresh Eyes

Most AI execution just runs through tasks sequentially. Building enforces **quality gates per phase** with **separate subagents** for discovery, implementation, and review — each with fresh context.

```
User: "/code-foundations:building docs/plans/2026-01-24-preserve-zorder.md"

  BRANCH GATE (mandatory)
  ├─ On main? → STOP. Create feature branch first.
  └─ Feature branch ensures per-phase commits can be rolled back

  FOR EACH PHASE:
  ┌────────────────────────────────────────────────────────────┐
  │  DISCOVERY (Explore subagent)                              │
  │  ├─ Fresh agent explores codebase                          │
  │  ├─ Writes findings to docs/building/*-discovery.md        │
  │  └─ Returns: BUILD | SKIP | UPDATE_PLAN                    │
  │                                                            │
  │  ⛔ Cannot proceed until discovery complete                │
  ├────────────────────────────────────────────────────────────┤
  │  PRE-GATE (Pseudocode subagent)                            │
  │  ├─ Loads cc-pseudocode-programming skill                  │
  │  ├─ Reads discovery notes                                  │
  │  └─ Writes pseudocode to docs/building/*-pseudocode.md     │
  │                                                            │
  │  ⛔ Cannot implement until pseudocode exists               │
  ├────────────────────────────────────────────────────────────┤
  │  IMPLEMENT (Implementation subagent)                       │
  │  ├─ Reads discovery + pseudocode files                     │
  │  ├─ Implements exactly what pseudocode specifies           │
  │  └─ Returns: DONE | BLOCKED                                │
  ├────────────────────────────────────────────────────────────┤
  │  POST-GATE (Reviewer subagent)                             │
  │  ├─ Different agent reviews the implementation             │
  │  ├─ Checks: matches pseudocode? requirements covered?      │
  │  └─ Writes review to docs/building/*-review.md             │
  │                                                            │
  │  ⛔ Cannot commit until reviewer returns PASS              │
  ├────────────────────────────────────────────────────────────┤
  │  CHECKPOINT                                                │
  │  ├─ Commit with phase summary                              │
  │  └─ Update execution log in plan file                      │
  └────────────────────────────────────────────────────────────┘

  → Per-phase commits enable rollback
  → All artifacts in docs/building/ are reviewable
```

### What Makes It Different

Engineering best practices are **automatically loaded** at each phase — not optional guidelines, but enforced checklists.

| Phase | Skills Loaded | What Gets Enforced |
|-------|---------------|-------------------|
| PRE-GATE | `cc-pseudocode-programming` | Design before code, routine cohesion |
| PRE-GATE | `aposd-designing-deep-modules` | Interface depth, information hiding |
| POST-GATE | `aposd-verifying-correctness` | Requirements coverage, boundary conditions |
| POST-GATE | `cc-defensive-programming` | Error handling, input validation |

Subagents load these skills and execute their checklists.

### Why Separate Subagents?

From the [Z-Index case study](docs/whiteboarding-example-zindex-preservation.md), the implementation agent loaded skills before touching code:

```
Skill(cc-pseudocode-programming)
Skill(cc-defensive-programming)
Skill(aposd-designing-deep-modules)

Read(docs/building/preserve-zorder-phase-1-discovery.md)
Read(docs/building/preserve-zorder-phase-1-pseudocode.md)
```

The reviewer agent started fresh — different context, different assumptions, catches what the implementer missed.

**File-based handoff means:**
- Main context stays clean (no pseudocode bloat)
- Each agent has full context via files
- Artifacts persist if interrupted
- Anyone can review what happened

---

## `/code-foundations:code` — Design With Me, Then Build (Experimental)

You know what to build. You don't need a full whiteboarding session. But you want to work through the design together before code exists.

**Two phases: Design Loop → Implementation Loop**

```
User: "/code-foundations:code add email validation to signup"

  PHASE 1: DESIGN LOOP (collaborate until ready)
  ┌─────────────────────────────────────────────────────────────┐
  │  PSEUDOCODE    Draft the flow and contracts                 │
  │       ↓                                                     │
  │  EXPLORE       Subagents research patterns, packages, etc   │
  │       ↓                                                     │
  │  TASKLIST      Track design decisions and open questions    │
  │       ↓                                                     │
  │  USER INPUT    "add X" / "what about Y?" / feedback         │
  │       ↓                                                     │
  │  REFINE        Update pseudocode, tasklist                  │
  │       ↓                                                     │
  │  ↺ REPEAT      When design feels complete → ask user        │
  └─────────────────────────────────────────────────────────────┘
                          ↓
                   "Ready to build?"
                          ↓
  PHASE 2: IMPLEMENTATION LOOP (execute with subagents)
  ┌─────────────────────────────────────────────────────────────┐
  │  IMPLEMENT     Subagent codes from pseudocode               │
  │  TEST          Unit tests → integration tests               │
  │  COMMIT        Checkpoint with passing tests                │
  │  ↺ NEXT TASK   User picks from tasklist                     │
  └─────────────────────────────────────────────────────────────┘
```

### Why Two Phases?

| Single Loop | Design → Build |
|-------------|----------------|
| Design evolves during coding | **Design locked before code** |
| "Actually, change the interface" | **Interface confirmed upfront** |
| Rework when requirements shift | **Shifts happen in design phase (cheap)** |
| User reviews code | **User reviews pseudocode (faster)** |

The design loop is where changes are cheap. Once you say "let's build," the contract is set.

### When to Use What

| Situation | Use |
|-----------|-----|
| Know what to build, want to design together | `/code` |
| Need to explore multiple approaches | `/whiteboarding` |
| Have a plan file, need full gated execution | `/building` |
| Technical uncertainty, prove feasibility | `/prototype` |
| Bug hunting, predict → log → repeat | `/debug` |

---

## `/code-foundations:debug` — Resolution Loop With Tasks

You always have a **current task** — the question you're answering. Predict, log, run. Then resolve: either you answered it (next task) or you need more info (narrower task). The task list keeps you on track.

```
User: "/code-foundations:debug login fails 20% of the time"

  Current task: "Investigate: login failure"
  ┌──────────────────────────────────────────────────┐
  │  PREDICT   What do I expect to see?              │
  │  LOG       Add log to test prediction            │
  │  RUN       Execute, check output                 │
  │  RESOLVE   What did we learn?                    │
  │     ├─ Need more info → TaskCreate (narrow)      │
  │     ├─ Found cause   → TaskCreate (fix)          │
  │     ├─ Applied fix   → TaskCreate (verify)       │
  │     └─ Verified      → Done!                     │
  └──────────────────────────────────────────────────┘

  Task list = your debug trail:

  #1 ✓ Investigate: login failure (20%)
  #2 ✓ Narrow: validateToken result → race condition!
  #3 ✓ Fix: request deduplication
  #4 ✓ Verify: parallel logins work
  Done.
```

### What Makes It Different

| Typical Debugging | /debug |
|-------------------|--------|
| Debug trail in your head | **Task list shows your reasoning** |
| Add logs randomly | **Predict first, then log to test it** |
| "It's probably X" → fix | **PREDICT + IF WRONG forces you to think** |
| Fix, hope it works | **Verify task required before done** |

### Staying On Track

The task list prevents rabbit holes, forgotten verifications, and lost context. If you feel lost: `TaskList` — see where you are, what you've learned, what's next.

---

## How It Works

### DEBUG
```
User: "/code-foundations:debug X isn't working"
  → Loop: PREDICT → LOG → RUN → DECIDE
  → Task list grows: narrow → fix → verify
  → Done when verified
```

### WRITE
```
User: "Build feature X with foundations"
  → code-foundations classifies as WRITE
  → cc-construction-prerequisites: requirements check
  → cc-pseudocode-programming: design first
  → CHECKER gates before done
```

### REVIEW
```
User: "Use foundations to review this code"
  → cc-quality-practices (CHECKER mode)
  → cc-routine-and-class-design (CHECKER mode)
  → Output: violations, warnings, fixes
```

### REFACTOR
```
User: "Clean this up with foundations"
  → cc-refactoring-guidance: plan steps
  → Execute one change at a time
  → CHECKER gates verify quality preserved
```

### CODE REVIEW (Parallel Agents)
```
User: "/review-pr" (on feature branch)
  → Triage: Categorize files by change type
  → Dispatch agents IN PARALLEL:
      ┌──────────────────────────────────────────────────────────────────────┐
      │  code-foundations:defensive-reviewer    → security + error handling  │
      │  code-foundations:quality-reviewer      → design + readability       │
      │  code-foundations:correctness-reviewer  → bugs + test coverage       │
      │  code-foundations:performance-reviewer  → algorithms + hot paths     │
      │  code-foundations:documentation-reviewer → docs + comments           │
      └──────────────────────────────────────────────────────────────────────┘
  → Aggregate findings by action type:
      Fix         → Apply immediately
      Investigate → Spin off research
      Plan        → /code-foundations:whiteboarding for design work
```

---

## Skills

| Skill | Purpose | Example |
|-------|---------|---------|
| **code-foundations** | Master dispatcher | "use foundations to [anything]" |
| **cc-developer-character** | Mindset and discipline | "use dev character to check my approach" |
| **cc-construction-prerequisites** | Requirements and planning | "use prereqs to review this plan" |
| **cc-pseudocode-programming** | Design routines first | "use pseudocode to design this feature" |
| **cc-quality-practices** | Reviews, testing, debugging | "use quality practices to review this code" |
| **cc-routine-and-class-design** | High-quality interfaces | "use routine design to review this code" |
| **cc-control-flow-quality** | Clean control structures | "use control flow to review this code" |
| **cc-data-organization** | Variables, naming, types | "use data org to review this code" |
| **cc-defensive-programming** | Error handling | "use defensive programming to review this code" |
| **cc-code-layout-and-style** | Formatting and comments | "use layout style to review this code" |
| **cc-refactoring-guidance** | Safe refactoring | "use refactoring to clean this up" |
| **cc-integration-practices** | Integration and builds | "use integration to review this merge" |
| **cc-performance-tuning** | Measure-first optimization | "use perf tuning, this is slow" |
| **cc-documentation-quality** | README, comments, API docs | "use doc quality to review this" |
| **cc-debugging** | Scientific debugging method | "debug this", "figure out why this fails" |
| **cc-table-driven-methods** | Replace if/else with tables | "too many if statements", "switch growing" |

---

## Three-Level Code Review System

| Level | Command | Agents | Use Case |
|-------|---------|--------|----------|
| 1 | `/review-commit` | 1 (quick) | Pre-commit sanity check |
| 2 | `/review-changes` | 3 (parallel) | Medium review for changes |
| 3 | `/review-pr` | 5 (parallel) | Full PR review |

### 5 Consolidated Agents (Dual Roles)

| Agent | Combines | Skills |
|-------|----------|--------|
| **defensive-reviewer** | security + error-handling | cc-defensive-programming, aposd-simplifying-complexity |
| **quality-reviewer** | maintainability + clarity | aposd-reviewing-module-design, cc-code-layout-and-style |
| **correctness-reviewer** | bugs + test coverage | aposd-verifying-correctness, cc-quality-practices |
| **performance-reviewer** | algorithms + hot paths | cc-performance-tuning, aposd-optimizing-critical-paths |
| **documentation-reviewer** | docs + comments | cc-documentation-quality |

## Skill Chain

The skills chain together based on task type:

```
code-foundations (dispatcher)
       │
       ├── DEBUG ──→ cc-developer-character ──→ cc-debugging
       │                                              │
       │                                              └── Scientific Method
       │                                                  (stabilize → hypothesize → experiment → fix)
       │
       ├── WRITE ──→ cc-developer-character ──→ cc-construction-prerequisites
       │                                              │
       │                                              └── cc-pseudocode-programming
       │                                                  (design before code)
       │
       ├── REVIEW ─→ cc-quality-practices ──→ cc-routine-and-class-design
       │                                              │
       │                                              └── CHECKER mode
       │                                                  (violations, warnings)
       │
       └── REFACTOR → cc-developer-character ──→ cc-refactoring-guidance
                                                      │
                                                      └── cc-control-flow-quality (CHECKER)
                                                          cc-routine-and-class-design (CHECKER)
```

---

## Installation

```bash
# Add marketplace (if not already added)
/plugin marketplace add ryanthedev/rtd-claude-inn

# Install plugin
/plugin install code-foundations@rtd

# Update to latest
/plugin update code-foundations@rtd
```

## Documentation

For guides and detailed documentation, visit the **[Wiki](https://github.com/ryanthedev/code-foundations/wiki)**.

## Case Studies

Ranked by how well they demonstrate the skills:

| # | Example | Type | Shows |
|---|---------|------|-------|
| 1 | [Z-Index Preservation](docs/whiteboarding-example-zindex-preservation.md) ⭐ | WHITEBOARD→BUILD | Full workflow: explore, pushback, research, 3-phase gated execution |
| 2 | [Two-Tier Review Comparison](docs/review-example-two-tier-comparison.md) | REVIEW | Quick vs full review, context window trade-offs |
| 3 | [Picker History Review](docs/review-example-picker-history-plan.md) | REVIEW | Multi-skill chaining, 4 violations, 3 warnings |
| 4 | [Comment Renumbering](docs/refactor-example-comment-renumbering.md) | REFACTOR | Most concise—systematic table, one change at a time |
| 5 | [Critical Path Review](docs/perf-example-critical-path-review.md) | OPTIMIZE | Measure-first—correctly decides NOT to optimize |
| 6 | [Border Window Cleanup](docs/refactor-example-border-cleanup.md) | REFACTOR | CHECKER gates, McCabe complexity |
| 7 | [Picker Text Overflow](docs/debug-flow-example-picker-overflow.md) | DEBUG | Root cause analysis, pattern matching |
| 8 | [Tab Indicator Removal](docs/refactor-example-tab-indicator-removal.md) | REFACTOR | Discipline recovery, systematic removal |
| 9 | [Picker Focus Bug](docs/debug-flow-example-picker-focus.md) | DEBUG | Scientific debugging method |
| 10 | [Window Picker Plan](docs/prerequisites-example-window-picker-plan.md) | PLAN | Phased plan with checkpoints |

## Source

Based on *Code Complete, 2nd Edition* by Steve McConnell.

## License

MIT

