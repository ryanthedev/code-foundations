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
Review: [pass|fail->pass (N attempts)|skipped (Standard/Minimal)|catch-up (batch)]"
```

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
- [x] BUILD: Discovery + design + TDD implementation complete
- [x] REVIEW: Verification passed [or "SKIPPED — tests are gate" or "Covered by catch-up review"]
- [x] Committed
Commit: [hash]
Summary: [1 sentence — what this phase delivered and what state it left the codebase in]
```

**The Summary line is critical for goal anchoring.** It feeds the `## Progress` block of subsequent subagent dispatch prompts, giving later phases context about what earlier phases accomplished. Write it for that audience.
