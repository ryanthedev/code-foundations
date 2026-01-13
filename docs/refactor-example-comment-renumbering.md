# Case Study: Comment Renumbering

**Type:** REFACTOR
**Skills:** code-foundations → cc-refactoring-guidance
**Focus:** Systematic change planning

## The Flow

```
User: "clean this up with foundations"

→ Task Classification: REFACTOR
→ cc-refactoring-guidance safe process:
  1. Save starting code ✓ (already committed)
  2. Plan the changes
  3. Make list of steps
  4. Do one at a time
```

## The Plan

| Location | Current | Fixed |
|----------|---------|-------|
| ApplyLayout line 82 | // 4. (duplicate) | // 5. |
| ApplyLayout line 89 | // 5. | // 6. |
| ApplyLayout line 101 | // 6. | // 7. |
| ApplyLayout line 130 | // 6b. | // 7b. |
| ApplyLayout line 140 | // 7. | // 8. |
| ApplyLayout line 155 | // 8b. | // 9. |
| ApplyLayout line 194 | // 9. | // 10. |
| ApplyLayout line 209 | // 9b. | // 11. |
| ApplyLayout line 226 | // 10. | // 12. |
| ApplyLayout line 238 | // 11. | // 13. |
| ApplyCellLayout line 429 | // 9b. | // 8. |
| ApplyCellLayout line 468 | // 10. | // 9. |
| ApplyCellLayout line 476 | // 11. | // 10. |

## Key Takeaway

Even "trivial" cleanup benefits from a systematic plan. The table makes it impossible to miss a change or introduce inconsistency.
