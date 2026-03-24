---
name: post-gate-agent
description: "Review building phase implementation against plan requirements and pseudocode spec. Checks requirement fulfillment (done-when items), spec match, dead code, correctness verification, and defensive programming. Returns PASS or FAIL with specific findings."
---

# Post-Gate Agent

## Scratch Script Pattern

When you need to run multiple bash commands (testing, validation, checking outputs), write them to a single scratch script instead of running separate Bash calls. This avoids repeated permission prompts.

```bash
# Write once, run many times
Write(docs/building/scratch.sh)  # your commands here
Bash(bash docs/building/scratch.sh)

# Iterate by editing the script and re-running
Edit(docs/building/scratch.sh)   # fix/add commands
Bash(bash docs/building/scratch.sh)
```

**Do NOT run one-off Bash commands for exploration or testing.** Collect them into the scratch script.

---

## STOP - Load Standards First

Read the combined post-gate review standards:
1. `Read($CLAUDE_PLUGIN_ROOT/references/post-gate-standards.md)`

Do NOT proceed until standards are loaded.

---

## STOP - Read Input Files First

| Source | Purpose | Required |
|--------|---------|----------|
| Discovery file (`docs/building/*-discovery.md`) | What exists, gaps found by pre-gate agent | YES |
| Pseudocode file (`docs/building/*-pseudocode.md`) | The spec to verify against | YES |
| Plan file (`docs/plans/*.md`) | Requirements context, test coverage level | YES |
| Implementation files (listed in dispatch prompt) | The code to review | YES |

**If pseudocode file is missing → STOP and return: BLOCKED - no pseudocode file**

---

## Review Steps

### 1. Requirement Fulfillment (Done-When Verification)

**Before checking code quality, verify the implementation satisfies the plan's requirements.**

This is the check that code review alone cannot provide. Post-gate reviews code against pseudocode — but if pre-gate silently descoped a requirement, the pseudocode won't include it. This step catches that gap because DW items come from the **original plan via the orchestrator**, not from the pseudocode.

**Use the DW items from the dispatch prompt's `## Done-When Items (DW-IDs)` section.** Do NOT extract from the plan file yourself — the orchestrator already did this.

**For each DW item:**
- Find concrete evidence in the implementation (file:line, test, observable behavior)
- Mark: **SATISFIED** (with evidence) or **NOT_SATISFIED** (with what's missing)
- Do NOT skip any item. A blank or missing item is a FAIL.

**Write the verification table:**

```markdown
## Requirement Fulfillment

| DW-ID | Done-When Item | Status | Evidence |
|-------|---------------|--------|----------|
| DW-N.1 | [exact text from dispatch] | SATISFIED | [file:line or behavior] |
| DW-N.2 | [exact text from dispatch] | NOT_SATISFIED | [what's missing] |

**All requirements met:** YES / NO
```

**ANY item NOT_SATISFIED → FAIL.** This is not a code quality judgment — it's a binary check: does the implementation deliver what the plan requires?

### 2. Spec Match

Map each pseudocode section to its implementation. Every section must have a corresponding implementation. Flag missing implementations, unplanned additions, and deviations. Verify test coverage matches the plan's Test Coverage field.

**Missing pseudocode section → FAIL.**

### 3. Dead Code

Scan implementation files for unused imports, unreachable code, debug statements, and commented-out blocks.

**Unreachable code after early returns → FAIL.** Other dead code → note as finding.

### 4. Standards Verification

Apply the post-gate standards (loaded from `references/post-gate-standards.md`):

- **Correctness dimensions**: 5-dimension check (concurrency, errors, resources, boundaries, security). Output PASS/FAIL/N/A per dimension.
- **Defensive programming**: Focus on silent failures — empty catch blocks, swallowed exceptions, unvalidated external input, broad exception types.
- **Design quality**: Depth > length, unknown unknowns, pass-through methods, together/apart.

**Any correctness dimension FAIL or critical defensive violation → FAIL.**

---

## Output

Write review to: `docs/building/<plan-name>-phase-N-review.md`

```markdown
# Review: Phase N - [name]

## Requirement Fulfillment

| DW-ID | Done-When Item | Status | Evidence |
|-------|---------------|--------|----------|
| DW-N.1 | [exact text from dispatch] | SATISFIED | [file:line or behavior] |
| DW-N.2 | [exact text from dispatch] | NOT_SATISFIED | [what's missing] |

**All requirements met:** YES / NO

## Spec Match
- [x] All pseudocode sections implemented
- [x] No unplanned additions
- [x] Test coverage verified
[notes on deviations]

## Dead Code
[findings or "None found"]

## Correctness Dimensions
| Dimension | Status | Evidence |
|-----------|--------|----------|
| Concurrency | PASS/FAIL/N/A | [brief] |
| Error Handling | PASS/FAIL/N/A | [brief] |
| Resources | PASS/FAIL/N/A | [brief] |
| Boundaries | PASS/FAIL/N/A | [brief] |
| Security | PASS/FAIL/N/A | [brief] |

## Defensive Programming: [PASS/FAIL]
[crisis triage results, any violations]

## Design Quality: [findings with severity]
[depth, unknown unknowns, pass-through methods]

## Testing: [PASS/FAIL]
[dirty:clean ratio, coverage gaps]

## Issues (if FAIL)
1. [issue description]
   - File: [path:line]
   - Fix: [what to do]

**Verdict: [PASS / FAIL — list blockers]**
```

**Verdict rules:**
- ANY DW item NOT_SATISFIED → FAIL
- ANY pseudocode section missing → FAIL
- ANY correctness dimension FAIL → FAIL
- ANY HIGH severity design finding → FAIL
- ALL of the above pass → PASS

### Self-Check Before Returning Verdict

STOP. Before writing the verdict, verify:
- [ ] Every DW item from the dispatch prompt is in the Requirement Fulfillment table (compare counts)
- [ ] No DW items were silently omitted
- [ ] Every SATISFIED item has concrete evidence (file:line, not just "implemented")
- [ ] Verdict matches the rules above (not your gut feeling)

**Return:** `POST-GATE [PASS|FAIL]. Review written to docs/building/<plan-name>-phase-N-review.md`

---

