# Code Foundations

Code Complete-based software engineering skills for Claude Code.

## Installation

```bash
# Add marketplace (if not already added)
/plugin marketplace add ryanthedev/rtd-claude-inn

# Install plugin
/plugin install code-foundations@rtd
```

## Skills

| Skill | Purpose |
|-------|---------|
| **code-foundations** | Master dispatcher - invokes appropriate skills based on activity |
| **cc-developer-character** | Mindset and discipline foundations |
| **cc-construction-prerequisites** | Requirements and design before coding |
| **cc-pseudocode-programming** | Design routines with pseudocode first |
| **cc-routine-and-class-design** | High-quality routine and class interfaces |
| **cc-control-flow-quality** | Clean control structures and logic |
| **cc-data-organization** | Variable naming, scope, and data types |
| **cc-defensive-programming** | Error handling and robustness |
| **cc-code-layout-and-style** | Formatting and self-documenting code |
| **cc-quality-practices** | Code reviews, testing, debugging |
| **cc-refactoring-guidance** | Safe refactoring strategies |
| **cc-integration-practices** | Integration and build processes |
| **cc-performance-tuning** | Measure-first optimization |

## Usage

The `code-foundations` skill acts as a dispatcher. Invoke it before any code activity and it will guide you to the appropriate phase-specific skills.

## Examples

### Debug Flow

A bug fix that demonstrates skill chaining: `code-foundations` classifies the task as DEBUG, invokes `cc-developer-character` for mindset discipline, then applies the Scientific Debugging Method—forming a hypothesis, verifying it, and implementing a targeted fix.

User asks to fix a focus bug in a picker window:

```
User: The issue is when the window pops up, the input box does not have focus.
      Can we make sure it starts with focus?

⏺ Skill(code-foundations)
  ⎿  Successfully loaded skill

⏺ Task Classification: DEBUG - The picker window opens but the input box
   doesn't have focus when it should.

   Let me invoke the developer character skill first, then examine the code.

⏺ Skill(cc-developer-character)
  ⎿  Successfully loaded skill

⏺ Good. DEBUG task - I need to understand the code before fixing.

⏺ Read(grid-server/Sources/GridPicker/main.swift)
  ⎿  Read 369 lines

⏺ I can see the issue. Let me apply the Scientific Debugging Method
   from cc-quality-practices.

   Hypothesis: The focus code on line 346 is finding the wrong NSTextField.
   Looking at the view hierarchy:
   1. promptLabel (NSLabel, which extends NSTextField) - added first
   2. textField (the actual editable input) - added second
   3. closeButton - added third

   The code `window?.contentView?.subviews.first { $0 is NSTextField }`
   will find promptLabel first since NSLabel inherits from NSTextField.

   Verification: Let me confirm NSLabel extends NSTextField.

⏺ Grep(pattern: "class NSLabel", path: "...", output_mode: "content")
  ⎿  Found 1 match: class NSLabel: NSTextField { ... }

⏺ Confirmed. NSLabel extends NSTextField on line 286, so `.first`
   matches the prompt label, not the input field.

   Fix: Add a method on PickerWindow to focus the input, since it
   already has the textField reference. This avoids fragile subview searching.

⏺ Edit(grid-server/Sources/GridPicker/main.swift)
  ⎿  Added focusInput() method and updated caller
```

The flow demonstrates:
1. **Classification** → DEBUG task identified
2. **cc-developer-character** → Mindset check before acting
3. **Understanding first** → Read the code before changing it
4. **Scientific Method** → Hypothesis, verification, then fix

## Source

Based on *Code Complete, 2nd Edition* by Steve McConnell.
