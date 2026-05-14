# Trust Report

The summary output for `commands/building.md` Phase 5: REPORT. The summary is a **trust report**, not a status dashboard. Engineers need to verify what the AI built.

Gate metadata (model, review results, epistemic status) lives in commit trailers and is derived from `git log` at report time — not duplicated in this template.

---

## Trailer Dump Commands

Run these against the commits made during the build (`first-commit..HEAD`):

```bash
# Full trailer dump for the build
git log --format="%(trailers)" first-commit..HEAD

# Find all provisional decisions
git log --format="%(trailers:key=AI-Epistemic-Status)" first-commit..HEAD

# One-line summary
git log --oneline first-commit..HEAD
```

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
