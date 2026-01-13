# Code Foundations

Code Complete-based software engineering skills for Claude Code.

## How It Works

### DEBUG
```
User: "X isn't working, use code-foundations to debug it"
  → code-foundations classifies as DEBUG
  → cc-developer-character checks mindset
  → cc-quality-practices: hypothesis → verify → fix
```

### WRITE
```
User: "Use code-foundations to build feature X"
  → code-foundations classifies as WRITE
  → cc-construction-prerequisites: requirements check
  → cc-pseudocode-programming: design first
  → CHECKER gates before done
```

### REVIEW
```
User: "Use code-foundations to review this code"
  → cc-quality-practices (CHECKER mode)
  → cc-routine-and-class-design (CHECKER mode)
  → Output: violations, warnings, fixes
```

### REFACTOR
```
User: "Use code-foundations to clean up this code"
  → cc-refactoring-guidance: plan steps
  → Execute one change at a time
  → CHECKER gates verify quality preserved
```

---

## Skills

| Skill | Purpose | Triggers |
|-------|---------|----------|
| **code-foundations** | Master dispatcher | any code task |
| **cc-developer-character** | Mindset and discipline | stuck debugging, tempted to skip steps |
| **cc-construction-prerequisites** | Requirements and planning | new project, "are we ready?" |
| **cc-pseudocode-programming** | Design routines first | new function, where to start |
| **cc-quality-practices** | Reviews, testing, debugging | review, debug, test |
| **cc-routine-and-class-design** | High-quality interfaces | new class, parameter counts |
| **cc-control-flow-quality** | Clean control structures | nested logic, complexity |
| **cc-data-organization** | Variables, naming, types | naming, variable scope |
| **cc-defensive-programming** | Error handling | validation, exceptions |
| **cc-code-layout-and-style** | Formatting and comments | style, readability |
| **cc-refactoring-guidance** | Safe refactoring | refactor, clean up |
| **cc-integration-practices** | Integration and builds | merge, integration |
| **cc-performance-tuning** | Measure-first optimization | slow, performance |

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

| Example | Type | Shows |
|---------|------|-------|
| [Picker History Review](docs/review-example-picker-history-plan.md) ⭐ | REVIEW | Multi-skill chaining, 4 violations, 3 warnings |
| [Border Window Cleanup](docs/refactor-example-border-cleanup.md) | REFACTOR | CHECKER gates, McCabe complexity |
| [Tab Indicator Removal](docs/refactor-example-tab-indicator-removal.md) | REFACTOR | Discipline recovery, systematic removal |
| [Picker Text Overflow](docs/debug-flow-example-picker-overflow.md) | DEBUG | Root cause analysis, pattern matching |
| [Picker Focus Bug](docs/debug-flow-example-picker-focus.md) | DEBUG | Scientific debugging method |
| [Window Picker Plan](docs/prerequisites-example-window-picker-plan.md) | PLAN | Phased plan with checkpoints |

## Source

Based on *Code Complete, 2nd Edition* by Steve McConnell.

## License

MIT
