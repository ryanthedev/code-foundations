# Code Foundations

Code Complete-based software engineering skills for Claude Code.

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
| 1 | `/check-commit` | 1 (quick) | Pre-commit sanity check |
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
```markdown
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
   → `/whiteboarding "auth middleware"`
```

**Workflow**: Apply "Fix" → Spin off "Investigate" → `/whiteboarding` for "Plan"

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
| 1 | [Picker History Review](docs/review-example-picker-history-plan.md) ⭐ | REVIEW | Multi-skill chaining, 4 violations, 3 warnings |
| 2 | [Comment Renumbering](docs/refactor-example-comment-renumbering.md) | REFACTOR | Most concise—systematic table, one change at a time |
| 3 | [Critical Path Review](docs/perf-example-critical-path-review.md) | OPTIMIZE | Measure-first—correctly decides NOT to optimize |
| 4 | [Border Window Cleanup](docs/refactor-example-border-cleanup.md) | REFACTOR | CHECKER gates, McCabe complexity |
| 5 | [Picker Text Overflow](docs/debug-flow-example-picker-overflow.md) | DEBUG | Root cause analysis, pattern matching |
| 6 | [Tab Indicator Removal](docs/refactor-example-tab-indicator-removal.md) | REFACTOR | Discipline recovery, systematic removal |
| 7 | [Picker Focus Bug](docs/debug-flow-example-picker-focus.md) | DEBUG | Scientific debugging method |
| 8 | [Window Picker Plan](docs/prerequisites-example-window-picker-plan.md) | PLAN | Phased plan with checkpoints |

## Source

Based on *Code Complete, 2nd Edition* by Steve McConnell.

## License

MIT

