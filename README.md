# Code Foundations

Code Complete-based software engineering skills for Claude Code.

## How It Works

### DEBUG
```
User: "X isn't working, use foundations to debug it"
  → code-foundations classifies as DEBUG
  → cc-developer-character checks mindset
  → cc-quality-practices: hypothesis → verify → fix
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
| **code-foundations** | Master dispatcher | "use foundations to debug this" |
| **cc-developer-character** | Mindset and discipline | "use dev character to write a commit message" |
| **cc-construction-prerequisites** | Requirements and planning | "use prereqs to review this plan" |
| **cc-pseudocode-programming** | Design routines first | "use pseudocode to design this function" |
| **cc-quality-practices** | Reviews, testing, debugging | "use quality practices to review this PR" |
| **cc-routine-and-class-design** | High-quality interfaces | "use routine design to check this class" |
| **cc-control-flow-quality** | Clean control structures | "use control flow to simplify this logic" |
| **cc-data-organization** | Variables, naming, types | "use data org to review these variables" |
| **cc-defensive-programming** | Error handling | "use defensive programming on this input" |
| **cc-code-layout-and-style** | Formatting and comments | "use layout style to clean up this file" |
| **cc-refactoring-guidance** | Safe refactoring | "use refactoring to clean this up" |
| **cc-integration-practices** | Integration and builds | "use integration practices for this merge" |
| **cc-performance-tuning** | Measure-first optimization | "use perf tuning, this is too slow" |

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
       ├── DEBUG ──→ cc-developer-character ──→ cc-quality-practices
       │                                              │
       │                                              └── Scientific Method
       │                                                  (hypothesis → verify → fix)
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
| 3 | [Border Window Cleanup](docs/refactor-example-border-cleanup.md) | REFACTOR | CHECKER gates, McCabe complexity |
| 4 | [Picker Text Overflow](docs/debug-flow-example-picker-overflow.md) | DEBUG | Root cause analysis, pattern matching |
| 5 | [Tab Indicator Removal](docs/refactor-example-tab-indicator-removal.md) | REFACTOR | Discipline recovery, systematic removal |
| 6 | [Picker Focus Bug](docs/debug-flow-example-picker-focus.md) | DEBUG | Scientific debugging method |
| 7 | [Window Picker Plan](docs/prerequisites-example-window-picker-plan.md) | PLAN | Phased plan with checkpoints |

## Source

Based on *Code Complete, 2nd Edition* by Steve McConnell.

## License

MIT
