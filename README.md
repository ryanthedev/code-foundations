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

### The Pushback That Paid Off

From the [Z-Index Preservation case study](docs/whiteboarding-example-zindex-preservation.md):

Claude recommended `CGWindowListCopyWindowInfo` for z-order. User selected "you should research" instead of accepting.

Research revealed: current code uses `.optionAll` which does **not** guarantee z-order. The "recommended" option was wrong. Research discovered the real solution: a secondary query with `.optionOnScreenOnly`.

| Without Pushback | With Pushback |
|------------------|---------------|
| Generic recommendation | Discovered `.optionAll` doesn't guarantee order |
| Assumed current code would work | Identified need for secondary query |
| May have led to bugs | Evidence-based approach |

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

| Other Execution Modes | Building |
|----------------------|----------|
| Run tasks sequentially | **Gated phases** — can't proceed until gate passes |
| Same context does everything | **Fresh subagent per phase** — no context pollution |
| Implementation then review | **Pseudocode first** — design before code |
| Self-review | **Different agent reviews** — fresh eyes catch different bugs |
| One big commit at end | **Per-phase commits** — rollback to any checkpoint |
| Artifacts in conversation | **Files in docs/building/** — persistent, resumable, reviewable |

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

## `/code-foundations:code` — Design With Me, Then Build

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

### Phase 1: Design Loop

Collaborative design with subagents and tasklist tracking. When the design feels complete, ask the user if they're ready to build.

```
/code-foundations:code add email validation to signup

✅ Task #1 created: Design email validation flow

PSEUDOCODE (draft 1):
validateEmail(email: string) → boolean
  if empty → return false
  if no @ → return false
  return true

User: "should return error messages, not just boolean"

✅ Task #1 updated: return ValidationResult with error messages

PSEUDOCODE (draft 2):
validateEmail(email: string) → ValidationResult
  if empty → {valid: false, error: "Email is required"}
  if no @ → {valid: false, error: "Invalid email format"}
  return {valid: true}

User: "what about disposable email domains?"

✅ Task #2 created: Research disposable email handling

→ Dispatching explore subagent...
→ Found: disposable-email-domains npm package (10M downloads)
→ Found: existing blocklist pattern in src/utils/spam.ts

✅ Task #2 completed: use existing spam.ts pattern
✅ Task #1 updated: add disposable domain check

PSEUDOCODE (draft 3):
validateEmail(email: string) → ValidationResult
  if empty → {valid: false, error: "Email is required"}
  if no @ → {valid: false, error: "Invalid email format"}
  if domain in disposableList → {valid: false, error: "Please use permanent email"}
  return {valid: true}

disposableList: use existing pattern from spam.ts

---
Design looks complete. Ready to build?

User: "yes"

→ Design confirmed. Switching to implementation.
```

### Phase 2: Implementation Loop

Execute the confirmed design. Subagents do the work, tasklist continues from design phase.

```
Tasklist from design:
✅ #1 Design email validation flow
✅ #2 Research disposable email handling

Converting to implementation tasks...
✅ Task #3 created: Implement validateEmail
✅ Task #4 created: Unit tests
✅ Task #5 created: Integration with SignupForm

IMPLEMENT #3:
→ Dispatching implementation subagent...
→ Reads confirmed pseudocode
→ Writes src/utils/validation.ts
→ DONE

✅ Task #3 completed

TEST #4:
→ Dispatching test subagent...
→ Unit tests for each case:
  ✓ rejects empty
  ✓ rejects invalid format
  ✓ rejects disposable domains
  ✓ accepts valid email
→ All pass

✅ Task #4 completed

COMMIT:
→ git commit -m "feat: add email validation with disposable domain check"

Current tasklist:
✅ #1 Design email validation flow
✅ #2 Research disposable email handling
✅ #3 Implement validateEmail
✅ #4 Unit tests
◻ #5 Integration with SignupForm
◻ #6 Add to password reset flow (added mid-session)

What's next?

User: "do #5, then #6"

[continues...]
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

---

## How It Works

### DEBUG
```
User: "X isn't working, use foundations to debug it"
  → code-foundations classifies as DEBUG
  → cc-developer-character checks mindset
  → cc-debugging: stabilize → hypothesize → experiment → fix
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

### Output Format

Issues are grouped by action type:
````markdown
## Fix
1. 🔴 [CRITICAL] Handler.cs:84 - Memory amplification (defensive)
   ```csharp
   if (encoded.Length > MaxDecodedSize / 1.34) return null;
   ```

2. 🟡 [IMPORTANT] Handler.cs:58 - Silent failure (defensive)
   Fix: Add logging

## Investigate
1. 🟡 [IMPORTANT] UserService.cs:200 - Race condition? (correctness)
   Check: Is this called concurrently?
   **Unknown**: Thread safety requirements

## Plan
1. 🔴 [CRITICAL] Auth missing from 5 endpoints
   → `/code-foundations:whiteboarding "auth middleware"`
````

**Workflow**: Apply "Fix" → Spin off "Investigate" → `/code-foundations:whiteboarding` for "Plan"

---

## Example

**Question:**
> "The picker text is overflowing into the icons on the right side"

**Result:**
```
Step 1: Task Classification
  → DEBUG (signals: "overflowing", visual bug)

Step 2: Developer Character Check ✓

Step 3: Root Cause Analysis
  | Location        | Uses maxWidth? |
  |-----------------|----------------|
  | ResultRow       | ✓ maxWidth set |
  | PickerTextField | ✗ No maxWidth  |

  Root cause: PickerTextField missing the pattern already used elsewhere.

Step 4: Surgical Fix
  → Add maxWidth: "calc(100% - iconSpace)" to PickerTextField
  → Done in 57 seconds
```

---

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

