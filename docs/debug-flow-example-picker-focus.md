# Debug Flow Example: Picker Focus Bug

## Summary: How Code-Foundations Guided This Fix

This document demonstrates how the `code-foundations` skill applied the Scientific Debugging Method to fix a focus bug, avoiding trial-and-error debugging.

### What the Skill Did

**1. Task Classification**
The skill classified this as DEBUG and applied systematic discipline before touching any code.

**2. Understanding Before Acting**
Read 369 lines of the picker implementation to understand the view hierarchy before forming any hypothesis.

**3. Scientific Debugging Method**
Instead of adding `print` statements or randomly trying fixes:

- **Hypothesis:** The focus code `window?.contentView?.subviews.first { $0 is NSTextField }` is finding the wrong text field
- **Reasoning:** View hierarchy shows promptLabel (NSLabel) added before textField, and `.first` would match promptLabel
- **Verification:** Grep confirmed `NSLabel: NSTextField` - so NSLabel *is* an NSTextField, making the hypothesis correct
- **Fix:** Add `focusInput()` method on PickerWindow that directly references the correct textField

### What Could Have Gone Wrong Without This Approach

A typical ad-hoc debug might have:
- **Tried random fixes** - Calling `makeFirstResponder` multiple times, adding delays, forcing focus in different lifecycle methods
- **Missed the root cause** - The bug wasn't "focus isn't working," it was "we're focusing the wrong view"
- **Added fragile code** - Like searching for the second NSTextField, or filtering by specific properties
- **Taken longer** - Trial-and-error debugging can take 10x longer than hypothesis-driven debugging

### The Methodology

```
Classify Task → Mindset Check → Read Code → Form Hypothesis → Verify → Fix
```

The verification step (grepping for `class NSLabel`) took seconds but provided certainty. Without it, the fix would have been a guess.

---

## Full Session Transcript

```
User: The issue is when the window pops up, the input box does not have focus.
      Can we make sure it starts with focus?

Skill(code-foundations)
  Successfully loaded skill

Task Classification: DEBUG - The picker window opens but the input box
  doesn't have focus when it should.

  Let me invoke the developer character skill first, then examine the code.

Skill(code-foundations)
  Successfully loaded skill

Good. DEBUG task - I need to understand the code before fixing.

Read(grid-server/Sources/GridPicker/main.swift)
  Read 369 lines

I can see the issue. Let me apply the Scientific Debugging Method
  from cc-quality-practices.

  Hypothesis: The focus code on line 346 is finding the wrong NSTextField.
  Looking at the view hierarchy:
  1. promptLabel (NSLabel, which extends NSTextField) - added first
  2. textField (the actual editable input) - added second
  3. closeButton - added third

  The code `window?.contentView?.subviews.first { $0 is NSTextField }`
  will find promptLabel first since NSLabel inherits from NSTextField.

  Verification: Let me confirm NSLabel extends NSTextField.

Grep(pattern: "class NSLabel", path: "...", output_mode: "content")
  Found 1 match: class NSLabel: NSTextField { ... }

Confirmed. NSLabel extends NSTextField on line 286, so `.first`
  matches the prompt label, not the input field.

  Fix: Add a method on PickerWindow to focus the input, since it
  already has the textField reference. This avoids fragile subview searching.

Edit(grid-server/Sources/GridPicker/main.swift)
  Added focusInput() method and updated caller
```

---

## Key Takeaways

1. **Classification → Mindset → Understanding → Fix** - The skill enforced this order
2. **Hypothesis-driven** - "I think X is happening because Y" before touching code
3. **Verification** - A quick grep confirmed the hypothesis with certainty
4. **Targeted fix** - The solution avoided fragile subview searching by using an existing reference
