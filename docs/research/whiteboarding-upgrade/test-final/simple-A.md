# Whiteboarding Session: Rename 'whiteboarding' Command to 'plan'

## Skill Loaded

`code-foundations:whiteboarding` (FINAL-SKILL.md)

---

## Step 1: DISCOVER (Pattern Discovery + Questioning)

### Step 1a: Codebase Search (MANDATORY)

**Search performed before any questions.**

#### Existing Patterns Found

- **Command files live in `commands/`** as markdown files. Each has YAML frontmatter with `description`, `argument-hint`, and `allowed-tools`. The filename IS the command name (e.g., `commands/whiteboarding.md` maps to `/code-foundations:whiteboarding`).
- **The whiteboarding command file** (`commands/whiteboarding.md`) references the `whiteboarding` skill via `Skill(code-foundations:whiteboarding)`. The skill itself lives at `skills/whiteboarding/SKILL.md`.
- **Other commands follow the same pattern:** `building.md`, `debug.md`, `review.md`, `prototype.md`, `code.md`, `setup-ast.md`.
- **References to "whiteboarding" exist across the codebase:** CLAUDE.md mentions `/code-foundations:whiteboarding` in workflow tables, the building skill references it in integration docs, and the whiteboarding skill's SKILL.md frontmatter uses `name: whiteboarding`.

#### Conventions to Follow

- Naming: Command files are lowercase, no prefix. Filename = command name.
- Structure: YAML frontmatter + markdown body with skill invocation.
- Cross-references: Other files reference commands by their full path (`/code-foundations:<command-name>`).

#### Similar Implementations

- No prior command renames found in the codebase. This will be the first.

---

### Step 1b: Adaptive Questioning

Based on pattern discovery, this is a **Simple** task. It touches 1 file directly (the command file rename), follows 1 known pattern (command naming), has no cross-cutting concerns, low uncertainty, and needs 1-2 phases. I'll follow the Simple track.

### Questions (Simple track: 2-3 questions)

**Q1:** "The command file is `commands/whiteboarding.md`. Renaming it to `commands/plan.md` will make `/code-foundations:plan` work. Should I also update references to the old command name in CLAUDE.md and other docs, or just the command file itself?"

[USER]: "Yeah, update the references too. Wherever it says /code-foundations:whiteboarding, change it to /code-foundations:plan."

**Q2:** "The skill itself (`skills/whiteboarding/SKILL.md`) has `name: whiteboarding` in its frontmatter and references throughout. Should the skill stay named 'whiteboarding' internally, or rename that too?"

[USER]: "Just the command. Leave the skill alone."

**Q3:** "What does 'done' look like -- just that `/code-foundations:plan` works and all docs point to the new name?"

[USER]: "Exactly. Old name gone from docs, new name works."

### Problem Statement

Rename the user-facing `/code-foundations:whiteboarding` command to `/code-foundations:plan` by renaming the command file and updating all documentation references. The underlying whiteboarding skill remains unchanged.

### Constraints

- Only the command file and documentation references change; the skill directory and skill files are untouched.
- Every occurrence of `/code-foundations:whiteboarding` in docs must become `/code-foundations:plan`.

### Success Criteria

- `/code-foundations:plan` invokes the whiteboarding skill.
- No remaining references to `/code-foundations:whiteboarding` in documentation.
- The whiteboarding skill itself is unchanged.

[USER]: "Does this capture what you want?"
[USER]: "Yes."

---

## Step 2: CLASSIFY

> Based on pattern discovery, this is a **Simple** task. It touches 2-3 files (command file + doc references), follows 1 known pattern (command naming convention), has zero cross-cutting concerns, and uncertainty is low -- the rename is mechanical. I'll follow the Simple track.

---

## Step 3: EXPLORE

**Skipped per Simple track.** The approach is obvious from codebase patterns: rename the file, update references.

---

## Step 4: DETAIL (Simple Track Template)

---

# Plan: Rename whiteboarding command to plan

**Created:** 2026-03-10
**Status:** ready
**Complexity:** simple

---

## Context

The user-facing command `/code-foundations:whiteboarding` should be renamed to `/code-foundations:plan` for brevity. This requires renaming the command file (`commands/whiteboarding.md` to `commands/plan.md`) and updating all documentation references to the old command name. The underlying `whiteboarding` skill is not affected.

## Constraints

- The skill directory `skills/whiteboarding/` and its files must not be modified.
- The internal skill invocation inside the command file (`Skill(code-foundations:whiteboarding)`) stays the same -- only the command name changes.
- All occurrences of `/code-foundations:whiteboarding` in documentation must be updated to `/code-foundations:plan`.

---

## Implementation Phases

### Phase 1: Rename command file and update internal heading
**Model:** haiku

**Goal:** Rename `commands/whiteboarding.md` to `commands/plan.md` and update the command's internal heading from `# /whiteboarding` to `# /plan`.

**Scope:**
- IN: The command file rename and its internal heading/description.
- OUT: The whiteboarding skill, other command files, documentation references (Phase 2).

**Done when:**
- [ ] `commands/plan.md` exists with correct frontmatter and heading
- [ ] `commands/whiteboarding.md` no longer exists

---

### Phase 2: Update all documentation references
**Model:** haiku

**Goal:** Replace every occurrence of `/code-foundations:whiteboarding` with `/code-foundations:plan` across documentation and cross-references.

**Scope:**
- IN: CLAUDE.md, building skill references, any other files referencing the old command name.
- OUT: The whiteboarding skill files, command logic, other command files' internal behavior.

**Constraints:** The string `whiteboarding` in non-command contexts (e.g., skill names, skill descriptions, workflow labels) must NOT be changed -- only the `/code-foundations:whiteboarding` command reference pattern.

**Done when:**
- [ ] Zero occurrences of `/code-foundations:whiteboarding` remain in the repository
- [ ] All replaced references correctly read `/code-foundations:plan`

---

## Test Coverage

**Level:** None

This is a rename of a command file and documentation references. There is no runtime code to test.

## Test Plan

- [ ] Grep the entire repo for `/code-foundations:whiteboarding` -- expect zero results
- [ ] Verify `commands/plan.md` exists and contains `Skill(code-foundations:whiteboarding)` (skill invocation unchanged)
- [ ] Verify `commands/whiteboarding.md` does not exist

---

## Notes

- The building skill (`skills/building/SKILL.md`) references `/code-foundations:whiteboarding` in its integration section -- this must be caught in Phase 2.
- CLAUDE.md has multiple references in workflow tables and the Prototype/Whiteboarding/Building flow section.
- The whiteboarding skill's own SKILL.md references itself as a chain target ("CHAINS TO: building") but does not reference the command name, so it should not need changes.

---

## Execution Log

_To be filled during /code-foundations:building_

---

## Step 5: SELF-CHECK

**Skipped per Simple track.**

---

## Step 6: VALIDATE

"Does this plan look right? Anything to add or change?"

[USER]: "Looks good, let's go."

**Test coverage question:**

"How much test coverage do you want for this implementation?"

[USER]: "None, it's just a rename."

---

## Step 7: SAVE

Plan saved to `docs/plans/2026-03-10-rename-whiteboarding-to-plan.md`.

---

## Step 8: HANDOFF

"Plan saved to docs/plans/2026-03-10-rename-whiteboarding-to-plan.md. How would you like to proceed?"

1. **Clear conversation and build** (Recommended)
2. **Tell me what to do**

[USER]: "Option 1."

Execute `/clear`, then `/code-foundations:building docs/plans/2026-03-10-rename-whiteboarding-to-plan.md`.

---
---
---

## Meta-Commentary

### Did the skill correctly route to the Simple track?

Yes. The signal table makes this unambiguous: 2-3 files touched, 1 known pattern (command naming), zero cross-cutting concerns, low uncertainty, 1-2 phases. Every signal points to Simple. The skill classified correctly and followed the Simple track throughout.

### Was the ceremony appropriate for this task's complexity?

Yes. The Simple track kept things lean:

- **2 questions** asked (plus a third to confirm "done" criteria) -- enough to surface the key ambiguity (should the skill also be renamed?) without over-interrogating.
- **No approach comparison** -- correctly skipped since no conflicting patterns were found.
- **No self-check** -- correctly skipped per Simple track rules.
- **Flat checklist phases** with 50-75 words each -- no bloated contract structure.
- **Total ceremony: about 5 minutes of simulated interaction.** Proportional to the task.

The one area worth noting: the skill says "2-3 questions" for Simple track. In practice, question 3 ("what does done look like?") overlapped with the success criteria that were already implicit. A more realistic user might have answered Q1 and Q2 and said "that's it, go." The skill handles this gracefully since it says "minimum" not "exactly."

### Is the plan sufficient for a pre-gate agent?

Yes. The plan gives the pre-gate agent everything it needs:

- **Clear goal** per phase (rename file; update references).
- **Explicit scope boundaries** (IN/OUT) prevent the agent from touching the skill files.
- **Constraints** call out the critical trap: do not change `whiteboarding` in non-command contexts.
- **Done-when criteria** are verifiable with grep and file existence checks.
- **Notes section** flags specific files the pre-gate agent should discover (CLAUDE.md, building skill).

The pre-gate agent can discover the actual files to modify through codebase search, which is exactly what the skill intends -- file hints point to areas, not mandates.

### Any friction or confusion from the skill instructions?

Minor observations:

1. **AskUserQuestion enforcement:** The skill says "Each question below MUST use `AskUserQuestion` tool." In this simulation, questions were inlined. In a real execution, each would be a tool call. The instruction is clear but adds overhead for a 2-question Simple session.

2. **Step ordering nuance:** The skill's Step 1b says "classify complexity using the signal table in Step 2" during questioning, but Step 2 is formally a separate step. In practice, you classify early (during 1b) and then formally state it again in Step 2. This double-touch is slightly redundant but not confusing -- it reinforces the classification.

3. **Test Coverage question feels ceremonial for "None" tasks:** The skill mandates asking about test coverage even when the task has no code. The user's answer is predictable. However, this is defensible -- the skill cannot know in advance that no code is involved, and recording "None" explicitly is better than assuming.

4. **Phase count:** Two phases for what is essentially one logical operation (rename + update refs) might seem like over-decomposition. But splitting "rename file" from "update references" is actually smart -- it creates a clean checkpoint between a structural change and a content change, and prevents a half-done state where the file is renamed but docs still point to the old name.

No significant friction. The Simple track is appropriately lightweight for this task.
