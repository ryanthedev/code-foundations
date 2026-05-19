# Merge Instructions

Used in the REPORT phase of `commands/build.md`. Substituted into the trust report's "Merge Instructions" section based on workspace mode recorded by `references/worktree-gate.md`.

---

## Worktree Mode

```
Worktree: .claude/worktrees/<slug>/
Branch: feature/<slug>

To merge and clean up (run from main checkout, not the worktree):
  cd /path/to/main/checkout
  git worktree remove .claude/worktrees/<slug>   # remove worktree FIRST
  git merge --no-ff feature/<slug>                # then merge
  git branch -d feature/<slug>                    # then delete branch
  git worktree prune                              # clean up stale entries

If using GitHub PR instead of local merge:
  cd /path/to/main/checkout
  git push -u origin feature/<slug>               # push from main checkout
  gh pr create ...                                # create PR
  gh pr merge <number> --merge --delete-branch    # merge + remote delete
  git worktree remove .claude/worktrees/<slug>    # remove worktree
  git branch -D feature/<slug>                    # force-delete local branch
  git pull --ff-only                              # update main

NOTE: gh pr merge will fail if run from inside the worktree
(git can't resolve main). Always run from the main checkout.
If git pull diverges (plan commits on main not on remote),
rebase: git rebase origin/main
```

---

## Feature Branch Mode

```
Branch: feature/<topic>
To merge: git merge --no-ff feature/<topic>
```
