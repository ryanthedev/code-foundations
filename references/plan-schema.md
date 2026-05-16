# Plan File Schema

Shared schema for plan/building workflow.

---

## File Location

```
.local/state/code-foundations/plans/YYYY-MM-DD-<topic-slug>.md
```

**Naming convention:**
- Date prefix for chronological ordering
- Lowercase, hyphen-separated slug
- Example: `2024-03-15-user-authentication.md`

---

## Status Values

| Status | Meaning |
|--------|---------|
| `ready` | Plan complete, awaiting execution |
| `in-progress` | Execution started |
| `blocked` | Execution paused due to issue |
| `complete` | All phases done, tests pass |

---

## Full Schema

```markdown
# Plan: [Topic]

**Created:** YYYY-MM-DD
**Status:** ready | in-progress | blocked | complete
**Started:** YYYY-MM-DD HH:MM (filled during building)
**Completed:** YYYY-MM-DD HH:MM (filled when done)

---

## Context

[1-2 sentence problem statement from plan Phase 1]

## Constraints

- [constraint from discovery questions]
- [constraint from discovery questions]

## Success Criteria

- [criterion 1]
- [criterion 2]

## Chosen Approach

**[Approach Name]**

[Rationale explaining why this approach over alternatives]

**Alternatives Considered:**
- [Approach B] - Not chosen because [reason]
- [Approach C] - Not chosen because [reason]

---

## Implementation Checklist

### Phase 1: [Phase Name]

- [ ] [Specific task with file path if applicable]
- [ ] [Specific task with file path if applicable]

**Files:**
- `path/to/file.ts` - [what this file does]
- `path/to/other.ts` - [what this file does]

**Details:**
[Implementation specifics, patterns to use, edge cases]

**Dependencies:** [what must be done first, or "None"]

---

### Phase 2: [Phase Name]

[Same structure as Phase 1]

---

## Test Coverage

**Level:** 100% | Backend only | Backend + frontend | None | Per-phase

_Chosen during planning. Affects REVIEW gate and final verification._

---

## Test Plan

### Unit Tests
- [ ] [specific test: what it verifies]
- [ ] [specific test: what it verifies]

### Integration Tests
- [ ] [specific test: what it verifies]

### Manual Verification
- [ ] [step to verify manually]

---

## Notes

- [Edge cases identified during planning]
- [Gotchas or warnings for implementation]
- [Decisions made and rationale]

---

## Execution Log

_Filled during /code-foundations:building execution_

### Phase 1: [Name]
- [x] Task 1 - Completed YYYY-MM-DD HH:MM
- [x] Task 2 - Completed YYYY-MM-DD HH:MM
- [ ] Task 3 - **BLOCKED:** [description]

**Commit:** [git hash]
**Notes:** [issues encountered, deviations from plan]

### Phase 2: [Name]
...

---

## Post-Completion

**Final Status:** complete
**Total Duration:** [calculated from started to completed]
**Commits:**
- [hash] Phase 1: [name]
- [hash] Phase 2: [name]

**Follow-up Items:**
- [items discovered during building that weren't in scope]
```

---

## Minimal Schema (Quick Plans)

For simple features, minimal required fields:

```markdown
# Plan: [Topic]

**Created:** YYYY-MM-DD
**Status:** ready

## Context
[problem statement]

## Implementation Checklist

### Phase 1: [Name]
- [ ] [task]

## Test Coverage
**Level:** 100%

## Test Plan
- [ ] [test]
```

---

## Validation Checklist

Before saving plan:
- [ ] Status is `ready`
- [ ] Context clearly states what we're building
- [ ] At least one phase in implementation checklist
- [ ] Each phase has specific tasks (not vague goals)
- [ ] **Test coverage level specified** (default: 100%)
- [ ] Test plan has at least one item
- [ ] No hypothetical/YAGNI features included
