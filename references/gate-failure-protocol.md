# Gate Failure Protocol

Used by the orchestrator (`commands/build.md` Phase 3: EXECUTE) when a BUILD or REVIEW task returns FAIL.

---

## Per-Failure Action

BUILD's failure status is **BLOCKED**; REVIEW's is **FAIL**. Both route here, both count against the same retry cap.

| Gate | Failure | Action |
|------|---------|--------|
| BUILD | BLOCKED — discovery finds gaps | Re-dispatch build agent with updated context |
| BUILD | BLOCKED — design/implementation obstacle | Re-dispatch build agent with the obstacle named |
| REVIEW | FAIL — findings in the review file | Re-dispatch the **build agent** with a `## Review Findings to Fix` block pasted from the review's Issues section (the orchestrator never edits code itself), then re-dispatch REVIEW |

**The failed task stays `in_progress` until it passes.** It is never marked completed on FAIL/BLOCKED, and the next sub-phase never starts until the current task completes — `blockedBy` enforcement prevents skipping.

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

---

## Wave Failures (parallel phases)

When one member of a parallel wave fails its gate while siblings pass:

- **The failer is quarantined in its own worktree** — its broken state never touches the build worktree. Fix and re-dispatch REVIEW there, same per-gate 3-retry cap as above.
- **Sync before each retry REVIEW:** merge the build branch's current HEAD into the failing phase's worktree first (clean by construction — file scopes are disjoint), so retry evidence includes any siblings already committed. Fixes made in the worktree are squashed into a fresh `wip(phase-N)` commit — its sha supersedes the one originally reported, and integration cherry-picks the latest.
- **Commits stay in plan order.** A plan-order-earlier failer holds later passers' integration — their worktrees simply wait. The barrier applies to commits, not just wave opening: never commit out of plan order, because the execution-log Summary chain that anchors later dispatches assumes it.
- **Post-integration wave-suite failure** (members green in isolation, red together): a gate failure attributed to the last-integrated member — fix forward under the normal retry cap; do not revert committed siblings.
- **3rd FAIL on a wave member:** the standard escalation template above, plus one extra user option: "Drop this phase — mark it blocked (blocks only its dependents; committed siblings stand)."
- **The next wave opens only when every member is committed or escalated.**
