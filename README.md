# Code Foundations

Code Complete-based software engineering skills for Claude Code.

## Installation

```bash
# Add marketplace (if not already added)
/plugin marketplace add ryanthedev/rtd-claude-inn

# Install plugin
/plugin install code-foundations@rtd
```

## Documentation

For guides, examples, and detailed documentation, visit the **[Wiki](https://github.com/ryanthedev/code-foundations/wiki)**.

## Case Studies

Real-world examples showing how the skills guide debugging and development.

| Case Study | Skill | Description |
|------------|-------|-------------|
| [Picker History Review](docs/review-example-picker-history-plan.md) | cc-quality-practices | REVIEW task: Multi-skill chaining found ID collision risk, missing dirty tests, and naming issues. 4 violations, 3 warnings with actionable fixes. |
| [Border Window Cleanup](docs/refactor-example-border-cleanup.md) | cc-refactoring-guidance | REFACTOR task: Post-refactoring CHECKER gates verify McCabe complexity, cohesion, and design compliance. |
| [Picker Text Overflow](docs/debug-flow-example-picker-overflow.md) | code-foundations | DEBUG task: Root cause analysis revealed the codebase already had the correct pattern—the fix was applying it consistently. |
| [Picker Focus Bug](docs/debug-flow-example-picker-focus.md) | code-foundations | DEBUG task: Scientific Debugging Method—hypothesis formation, verification via code search, then targeted fix. |
| [Window Picker Plan](docs/prerequisites-example-window-picker-plan.md) | cc-construction-prerequisites | PLAN task: Phased implementation plan with checkpoint gates, risk register, and explicit inputs/outputs for each phase. |

## Skills

| Skill | Purpose | Example Prompt |
|-------|---------|----------------|
| [**code-foundations**](skills/code-foundations/SKILL.md) | Master dispatcher | "Use code-foundations to help me fix this bug" |
| [**cc-developer-character**](skills/cc-developer-character/SKILL.md) | Mindset and discipline | "I'm stuck debugging for hours, check my developer-character" |
| [**cc-construction-prerequisites**](skills/cc-construction-prerequisites/SKILL.md) | Requirements and planning | "Check our construction-prerequisites before we start coding" |
| [**cc-pseudocode-programming**](skills/cc-pseudocode-programming/SKILL.md) | Design routines first | "Use pseudocode-programming to design this function" |
| [**cc-routine-and-class-design**](skills/cc-routine-and-class-design/SKILL.md) | High-quality interfaces | "Review this class using routine-and-class-design" |
| [**cc-control-flow-quality**](skills/cc-control-flow-quality/SKILL.md) | Clean control structures | "Check the control-flow-quality of this nested logic" |
| [**cc-data-organization**](skills/cc-data-organization/SKILL.md) | Variables, naming, types | "Review data-organization for these variables" |
| [**cc-defensive-programming**](skills/cc-defensive-programming/SKILL.md) | Error handling | "Check defensive-programming for this input validation" |
| [**cc-code-layout-and-style**](skills/cc-code-layout-and-style/SKILL.md) | Formatting and comments | "Review code-layout-and-style for this file" |
| [**cc-quality-practices**](skills/cc-quality-practices/SKILL.md) | Reviews, testing, debugging | "Use quality-practices to debug this issue" |
| [**cc-refactoring-guidance**](skills/cc-refactoring-guidance/SKILL.md) | Safe refactoring | "Should I refactor or rewrite? Check refactoring-guidance" |
| [**cc-integration-practices**](skills/cc-integration-practices/SKILL.md) | Integration and builds | "Review our integration-practices for this merge" |
| [**cc-performance-tuning**](skills/cc-performance-tuning/SKILL.md) | Measure-first optimization | "This is too slow, use performance-tuning to optimize" |

## Source

Based on *Code Complete, 2nd Edition* by Steve McConnell.
