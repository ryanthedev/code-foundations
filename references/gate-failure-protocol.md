# Gate Failure Protocol

Used by the orchestrator (`commands/build.md` Phase 3: EXECUTE) when a BUILD or REVIEW task returns FAIL.

---

## Per-Failure Action

BUILD's failure status is **BLOCKED**; REVIEW's is **FAIL**. Both route here, both count against the same retry cap.

| Gate | Failure | Action |
|------|---------|--------|
| BUILD | BLOCKED — discovery finds gaps | Re-dispatch build agent with updated context |
| BUILD | BLOCKED — design/implementation obstacle | Re-dispatch build agent with the obstacle named |
| REVIEW (blocking) | FAIL — findings in the review file | Re-dispatch the **build agent** with a `## Review Findings to Fix` block pasted from the review's Issues section (the orchestrator never edits code itself), then re-dispatch REVIEW |
| REVIEW (batch) | FAIL — findings against committed phases | See Batch Failures below — the fix goes forward, not back |

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

## Batch Failures (deferred REVIEW over committed phases)

A batch REVIEW runs against code that is already committed, so there is no gate to hold. The fix goes **forward** — never by reverting or rewriting a phase commit. Rewriting history mid-build breaks the execution-log Summary chain that anchors later dispatch prompts, and the commit was always a rollback boundary rather than a correctness claim.

**Procedure:**

1. **Attribute each finding to a phase.** The batch review reports findings per phase (the template requires it). A finding that lives in the seam between two phases is attributed to the later one — it is the phase that had to fit the existing interface.
2. **Fix serially in plan order, one dispatch per affected phase.** Re-dispatch that phase's build agent (its plan `**Model:**`) with a `## Review Findings to Fix` block carrying **only that phase's** findings. The orchestrator never edits code itself. Serial, not parallel: batch findings frequently interact, and a fix for phase X can resolve or move a finding in phase Y.
3. **Commit each fix forward** — `fix(phase-N): address batch review findings`, with the standard trailers and `Review: batch fail->pass (attempt K)`. Append a dated fix line to that phase's execution-log entry rather than editing the original entry.
4. **Re-dispatch the batch review over the entire original set**, not just the fixed phases. A fix is itself un-reviewed code, and the covered phases still have to cohere with each other afterward.
5. **The un-reviewed set stays non-empty until a batch PASS clears it.** No Full phase opens and VERIFY does not start while it holds anything.

**Retry cap:** 3 batch attempts, same as any other gate. Count the batch as a unit — three failing batch rounds, not three per phase. On the 3rd, stop and escalate with the standard template, adding one line naming which phases keep recurring in the findings.

**Escalation option specific to batches:** if the recurring findings all sit in one phase, offer "review the rest of the set separately and escalate only Phase N" — the other phases should not stay un-reviewed because one phase is stuck.

---

## Wave Failures (parallel phases)

When one member of a parallel wave fails its gate while siblings pass:

Wave members are deferred-review phases by construction (Full gates and security-sensitive phases run alone), so the failure surface inside a wave is BUILD and integration only — their review arrives later, through Batch Failures above, against the integrated build worktree.

- **Wave BLOCKED is the deliberate exception to the retry cap:** a BUILD member returning BLOCKED (or UPDATE_PLAN) does not auto-retry — in-flight siblings finish, their worktrees are held uncommitted, and the orchestrator pauses for the user (build.md → Parallel Waves step 3). Auto-retrying one member while its siblings are held would burn the cap on a problem that usually needs plan-level intervention.
- **A member whose own suite is red never integrates** — it is quarantined in its own worktree, and its broken state never touches the build worktree. Fix and re-run there under the same 3-retry cap; fixes are squashed into a fresh `wip(phase-N)` commit whose sha supersedes the one originally reported, and integration cherry-picks the latest.
- **Commits stay in plan order.** A plan-order-earlier failer holds later passers' integration — their worktrees simply wait. The barrier applies to commits, not just wave opening: never commit out of plan order, because the execution-log Summary chain that anchors later dispatches assumes it.
- **Post-integration wave-suite failure** (members green in isolation, red together): a gate failure attributed to the last-integrated member — fix forward under the normal retry cap; do not revert committed siblings.
- **3rd FAIL on a wave member:** the standard escalation template above, plus one extra user option: "Drop this phase — mark it blocked (blocks only its dependents; committed siblings stand)."
- **The next wave opens only when every member is committed, SKIPped, or escalated.**
