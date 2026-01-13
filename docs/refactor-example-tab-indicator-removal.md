# Case Study: Tab Indicator Inset Removal

**Type:** REFACTOR
**Skills:** code-foundations → cc-developer-character → cc-refactoring-guidance
**Focus:** Discipline recovery and systematic feature removal

## Why This Case Study Matters

This example shows the **discipline enforcement** aspect of code-foundations:

1. **User intervention** - Claude started editing before being asked to use the skill
2. **Honest self-assessment** - cc-developer-character acknowledged the premature edit
3. **Systematic plan** - cc-refactoring-guidance created a step-by-step removal plan
4. **Verification after each step** - Build checks between each file change

---

## The Problem

Remove the `TabIndicatorInset` feature from the codebase. This feature touched:
- Config types and parsing
- Layout calculation logic
- Window move operations
- Tests

Claude started making edits before being asked to use the systematic approach.

---

## The Flow

```
User: "remove the tab indicator inset feature"
Claude: [starts editing types.go]

User: "please use the code-foundations skill to remove this"

→ code-foundations classifies as REFACTOR
→ cc-developer-character runs self-assessment
  → Acknowledges: "I already made one edit before being asked to use the skill"
→ cc-refactoring-guidance creates removal plan
```

---

## Developer Character Self-Assessment

The skill caught the discipline slip:

| Check | Assessment |
|-------|------------|
| Understanding vs hoping | ✓ Traced feature through git history and all files |
| Intellectual honesty | "This is a multi-file removal... needs systematic approach" |
| Discipline | "Will follow refactoring guidance - one change at a time" |
| Humility | **"I already made one edit before being asked to use the skill"** |

**Key insight:** The skill didn't hide the premature action - it acknowledged it and committed to proceeding properly.

---

## Refactoring Plan

cc-refactoring-guidance produced this systematic plan:

| Step | File | Change | Verify |
|------|------|--------|--------|
| 1 | config/types.go | Remove TabIndicatorInset field | ✅ Done |
| 2 | config/config.go | Remove GetTabIndicatorInset() | Build |
| 3 | layout/windows.go | Remove params + inset logic | Build |
| 4 | layout/apply.go | Update call sites | Build |
| 5 | window/move.go | Update call sites | Build |
| 6 | layout/windows_test.go | Remove related tests | Build + Test |

**One change at a time, verify after each step.**

---

## What the Skill Prevented

| Without Skill | With Skill |
|---------------|------------|
| Ad-hoc edits across files | Systematic step-by-step plan |
| No verification between changes | Build check after each step |
| Hidden premature action | Honest acknowledgment |
| Potential missed references | Complete file inventory |

---

## Key Takeaways

1. **Skills can recover discipline** - Starting wrong doesn't mean you can't correct course
2. **Honest self-assessment** - cc-developer-character acknowledges mistakes, doesn't hide them
3. **Feature removal needs a plan** - Multiple files means systematic approach
4. **Verification gates** - Build after each step catches errors early
5. **Human-AI collaboration** - User intervention triggered proper methodology
