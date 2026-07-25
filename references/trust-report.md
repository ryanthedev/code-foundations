# Trust Report

The summary output for `commands/build.md` Phase 5: REPORT. The summary is a **trust report**, not a status dashboard. Engineers need to verify what the AI built.

Gate metadata (model, review results, epistemic status) lives in commit trailers and is derived from `git log` at report time — not duplicated in this template.

---

## Trailer Dump Commands

Run these against the commits made during the build (`first-commit..HEAD`):

```bash
# Full trailer dump for the build
git log --format="%(trailers)" first-commit..HEAD

# Find all provisional decisions
git log --format="%(trailers:key=AI-Epistemic-Status)" first-commit..HEAD

# Phases still carrying a deferred review trailer
git log --format="%(trailers:key=Review)" first-commit..HEAD | grep -i deferred

# One-line summary
git log --oneline first-commit..HEAD
```

**Resolve deferred reviews before writing the report.** Standard and Minimal phases commit with `Review: deferred (batch pending)` and are covered later by a batch REVIEW, which records itself as an execution-log addendum rather than by editing the commit. So a `deferred` trailer is expected — what must not exist is a `deferred` trailer whose phase has no `Covered by batch review` addendum in the plan's execution log. Check every one, and if any is unresolved, that is a build defect: the trailing batch REVIEW in VERIFY did not run or did not cover everything. Fix it before reporting rather than footnoting it.

State the review shape plainly in the report's Build & Test Summary — how many phases reviewed at their gate, how many by batch, and each batch's verdict. A reader who sees only "all gates passed" cannot tell that some reviews landed after their commits, and that is exactly the thing they would want to know.

---

## Report Template

The trust report text output focuses on what commit trailers can't capture (build/test results, manual verification steps, follow-ups, merge instructions):

```markdown
# Build Complete: [plan name]

## Build & Test Summary
- **Build:** PASS (no new warnings or errors)
- **Unit tests:** X passed, Y failed, Z skipped
- **Integration tests:** [results or N/A]
- **Lint:** PASS (no new issues)

## Manual Testing Steps
[If the plan includes manual testing steps, or if the feature involves UI/UX,
user-facing behavior, or interactions that automated tests cannot fully cover:]
1. [Step-by-step instructions to manually verify the feature]
2. [Expected behavior for each step]
3. [Edge cases worth checking manually]

[If no manual testing needed: "All behavior covered by automated tests."]

## Follow-up
- [Issues flagged by reviewers for future work]
- [Or: "None identified"]

## Merge Instructions
[Substitute from `references/merge-instructions.md` based on workspace mode
recorded in LOAD — § Worktree Mode for worktree, § Feature Branch Mode otherwise.]
```
