# Commit Format

Used by the orchestrator (`commands/build.md` Phase 3: EXECUTE) when committing after each phase. Read once per build; the trailer names are listed in build.md so routine commits don't require re-reading this file.

---

## Commit Recipe

```bash
git add .
git commit -m "[prefix]([scope]): [description]

[WHY this phase exists — goal, key decisions, constraints that shaped implementation]

Phase: N/M \"[phase name]\"
Plan: .code-foundations/plans/[plan-file].md
AI-Model: [model used]
AI-Epistemic-Status: [tested|assumed|provisional]
Gate-Policy: [Full|Standard|Minimal]
Review: [see the table below]"
```

## The `Review:` Trailer

The trailer records the review state **at the moment of the commit**, and for deferred phases that state is "not yet". It is never back-edited — a batch PASS is recorded in the execution log, not by rewriting the commit.

| Value | When |
|---|---|
| `pass` | Blocking REVIEW returned PASS before this commit (Full gate) |
| `pass (3-sample)` | Security-sensitive phase; majority PASS across three samples |
| `fail->pass (N attempts)` | Blocking REVIEW failed N times, then passed, all before this commit |
| `deferred (batch pending)` | Standard or Minimal phase committing on a green suite; a batch REVIEW will cover it |
| `batch fail->pass (attempt K)` | A fix-forward commit answering batch review findings (see gate-failure-protocol.md → Batch Failures) |

**Reading the history:** `deferred (batch pending)` on a phase commit does not mean the phase went unreviewed — it means the review is recorded elsewhere. The pairing evidence is the execution-log addendum line naming the batch that covered it, and the trust report resolves the two at REPORT time. A phase with a `deferred` trailer and no addendum is the one real anomaly to look for.

## Wave-Member Variant (parallel phases only)

A phase built in its own phase worktree lands via cherry-pick instead of `git add .` — run in the **build worktree**, in plan order:

```bash
git cherry-pick -n [latest reported wip-sha — gate-failure fixes produce a fresh wip commit that supersedes the original]
git commit -m "..."   # identical message + trailers as the standard recipe
```

A cherry-pick conflict means the phase's File scope declaration was violated — treat as a gate failure (build.md → Parallel Waves step 5), not something to resolve by hand. After committing: copy the phase's discovery/review artifacts into the build worktree's `.code-foundations/build/`, then `git worktree remove` the phase worktree.

## Message Rules

- **Subject**: Conventional Commits prefix (`feat`, `fix`, `refactor`, `chore`, etc.) + scope + description
- **Body**: WHY — goal, key decisions, constraints. Not operational telemetry.
- **Trailers**: Machine-parseable metadata via git trailer format. The trust report (Phase 5: REPORT) derives gate metadata from these trailers via `git log` — they are the system of record, so fill every one.
- **AI-Epistemic-Status**: `tested` (verified by tests), `assumed` (believed correct, not proven), `provisional` (expected to change)
- **AI-Temporal-Validity**: Add only when a decision has a known expiry (e.g., `until-v2-migration`)

---

## Execution Log Entry (per phase, written at commit time)

Append to the plan file's `## Execution Log`:

```markdown
### Phase N: [Name] (Gate: [Full/Standard/Minimal])
- [x] BUILD: Discovery + design + implementation (stub → implement → validate) complete
- [x] REVIEW: [see the REVIEW line variants below]
- [x] Committed
Commit: [hash]
Summary: [1 sentence — what this phase delivered and what state it left the codebase in]
```

**REVIEW line variants:**

| Phase | Line at commit time | Later addendum |
|---|---|---|
| Blocking (Full, or security-sensitive) | `Verification passed` | none |
| Deferred (Standard, Minimal) | `DEFERRED — batch pending (tests green at commit)` | on batch PASS, append a dated `Covered by batch review YYYY-MM-DD (phases X–Y)` line |
| Fix-forward commit | `Fixed batch review findings — [1 clause naming what]` | covered by the next batch PASS addendum like any other |

The addendum is appended, never substituted for the original line — the pairing of "deferred here, covered there" is the audit trail, and collapsing it into a single "passed" loses the fact that the commit preceded the review.

**The Summary line is critical for goal anchoring.** It feeds the `## Progress` block of subsequent subagent dispatch prompts, giving later phases context about what earlier phases accomplished. Write it for that audience.
