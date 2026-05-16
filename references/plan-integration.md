# Plan ↔ Building Integration

How `/code-foundations:plan` and `/code-foundations:building` chain together. Reference material — orchestrator does not need this hot path.

---

## Expected Flow (Single Build)

```
/code-foundations:plan "user story"
  ↓
[Socratic questions]
[2-3 approaches]
[Detailed sections]
[Save to .local/state/code-foundations/plans/YYYY-MM-DD-topic.md]
  ↓
[Set thinking effort to default — plan has the reasoning, orchestration doesn't need max effort]
  ↓
/code-foundations:building .local/state/code-foundations/plans/YYYY-MM-DD-topic.md
  ↓
[Worktree Gate → creates .claude/worktrees/<slug>/]
[Checklist execution in worktree]
[Tests pass]
[Summary report with merge instructions]
```

---

## Expected Flow (Parallel Builds)

```
Claude Instance 1                        Claude Instance 2
────────────────                        ────────────────
/plan "auth system"            /plan "notifications"
  → saves plan                              → saves plan
  → clear + build                         → clear + build

/building (worktree: auth-system)       /building (worktree: notifications)
  → .claude/worktrees/auth-system/        → .claude/worktrees/notifications/
  → feature/auth-system branch            → feature/notifications branch
  → all phases run isolated               → all phases run isolated
  → report: "merge when ready"            → report: "merge when ready"

                    User merges both to main when ready
```

**Key constraint:** Each parallel build must target a different plan file. Never run two building instances against the same plan.

---

## Plan File Model Override Syntax

Plans can optionally specify model per phase:

```markdown
### Phase 1: Simple Config
- [ ] Update config file

### Phase 2: Complex Engine
**Model:** opus
- [ ] Build query parser
- [ ] Implement optimizer
```

If `**Model:**` is omitted, auto-detection applies (see Model Resolution + Gate Policy Detection in `commands/building.md`).

---

## Thinking Effort for Building

Set thinking effort to **default** before building. The plan already contains the strategic reasoning — max effort during orchestration is wasted overhead. The subagents do the heavy thinking in their own contexts. Default effort on the orchestrator saves tokens without losing quality.

- Planning: **max** effort
- Building/execution: **default** effort

Worktree provides filesystem isolation from other builds.
