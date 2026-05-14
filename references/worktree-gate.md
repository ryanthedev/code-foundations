# Worktree Gate (MANDATORY - First Check Before Any Build)

The orchestrator (`commands/building.md` Phase 1: LOAD) must clear this gate before any other work. Multi-phase commits on `main` would have no rollback and pollute history.

---

## Determine Workspace Mode

```bash
git branch --show-current
git status
git worktree list
```

| Situation | Action |
|-----------|--------|
| Already in a worktree (`.git` is a file, not a directory) | On a feature branch — proceed |
| On `main`/`master`, clean | Ask: worktree or feature branch? |
| On feature branch, clean | Proceed (single-build mode) |
| Dirty working tree | Ask: "Uncommitted changes. Stash, commit, or abort?" |

**Ask the user (when on main/master):**

```
You're on [main]. Building requires an isolated workspace.

Worktree or feature branch?
- [ ] Worktree — isolated copy, main checkout stays free for other work
- [ ] Feature branch — simpler, but blocks this checkout during build
- [ ] Abort
```

---

## If Worktree

```bash
# Extract plan slug from plan filename (e.g., 2026-03-17-auth-system → auth-system)
PLAN_SLUG="<extracted-slug>"

# Create worktree with feature branch
git worktree add .claude/worktrees/${PLAN_SLUG} -b feature/${PLAN_SLUG}
```

Then copy the plan file into the worktree and change working directory:

```bash
mkdir -p .claude/worktrees/${PLAN_SLUG}/.claude/code-foundations/plans
cp .claude/code-foundations/plans/<plan-file>.md .claude/worktrees/${PLAN_SLUG}/.claude/code-foundations/plans/
cd .claude/worktrees/${PLAN_SLUG}
```

## If Feature Branch

```bash
git checkout -b feature/<plan-topic>
```

---

## Record Workspace Mode

Used later in REPORT to produce merge instructions:

- `worktree: .claude/worktrees/<slug>` + `branch: feature/<slug>`
- OR `branch: feature/<topic>`

---

## Dependency Setup (Worktree Mode Only)

After creating a worktree, gitignored files (node_modules, .env, build artifacts) are absent. Detect and install dependencies:

```bash
# Auto-detect package manager and install
if [ -f pnpm-lock.yaml ]; then pnpm install --frozen-lockfile
elif [ -f package-lock.json ]; then npm ci
elif [ -f yarn.lock ]; then yarn install --frozen-lockfile
elif [ -f go.mod ]; then go mod download
elif [ -f Cargo.lock ]; then cargo fetch
elif [ -f uv.lock ]; then uv sync
fi
```

**For macOS (APFS):** If the main checkout has `node_modules`, copy-on-write is near-instant:

```bash
cp -Rc ../../../node_modules ./node_modules  # APFS CoW, no actual disk copy
```

**Skip dependency setup if:** the project has no lockfile or the plan does not involve building/testing code (e.g., documentation-only plans).

---

**This gate is NON-NEGOTIABLE.** Do not proceed on main/master under any circumstances.
