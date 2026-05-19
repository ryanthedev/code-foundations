# Gate Failure Protocol

Used by the orchestrator (`commands/build.md` Phase 3: EXECUTE) when a BUILD or REVIEW task returns FAIL.

---

## Per-Failure Action

| Gate | Failure | Action |
|------|---------|--------|
| BUILD | Discovery finds gaps | Re-dispatch build agent with updated context |
| BUILD | Design issues | Re-dispatch build agent |
| REVIEW | Verification fails | Fix code, re-dispatch REVIEW agent |
| REVIEW | Reviewer finds issues | Fix issues, re-dispatch REVIEW agent |

**The failed task stays `in_progress` until it passes.** You CANNOT mark it completed on FAIL. You CANNOT proceed to next sub-phase until the current task is completed. `blockedBy` enforcement prevents skipping — the next task's `blockedBy` list is not empty until the predecessor is completed.

---

## Retry Cap (max 3 failures per gate)

Track the number of times each gate has returned FAIL for the current phase.

| Attempt | Action |
|---------|--------|
| 1st FAIL | Fix issues, re-dispatch |
| 2nd FAIL | Fix issues, re-dispatch. Note: if the same issues recur, the fix approach is wrong. |
| 3rd FAIL | **STOP.** Do not re-dispatch. Present findings to user (template below). |

**On the 3rd FAIL — present this to the user:**

```
Phase N REVIEW has failed 3 times.

Recurring issues:
- [list findings that appeared in multiple reviews]

Options:
1. I fix the remaining issues and retry (explain what you'd do differently)
2. You provide guidance on the recurring issues
3. We revisit the plan for this phase (UPDATE_PLAN)
```

**Do NOT silently retry a 4th time.** Three failures indicate a structural problem — either the plan is wrong, the pseudocode is wrong, or the fix approach isn't addressing root causes. Escalate to the user.
