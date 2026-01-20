---
description: "TDD hacker mode. Write test → make it pass → refactor → checkpoint → repeat."
argument-hint: "[what to build]"
allowed-tools: ["Bash", "Glob", "Grep", "Read", "Edit", "Write", "Task"]
---

# Hack Mode

Fast iteration. Minimal ceremony. You and me slinging code.

---

## The Loop

```
1. RED        - Write a failing test
2. GREEN      - Minimum code to pass
3. REFACTOR   - Clean it up
4. CHECKPOINT - Validate before moving on
5. REPEAT
```

**No plan files. No whiteboarding. Direct execution with quality gates.**

---

## Rules

1. **Tests first** - If no test exists, write one before coding
2. **Smallest step** - One behavior at a time
3. **Run tests constantly** - After every change
4. **Refactor only when green** - Never refactor broken code
5. **Checkpoint before continuing** - Validate patterns + tests after each feature
6. **No gold plating** - If it passes and checkpoint approves, move on

---

## Session Flow

### Start
```
User: /hack [what to build]

→ Understand the goal (30 seconds, no docs)
→ Find or create test file
→ Start the loop
```

### Each Iteration
```
1. What's the next behavior to add?
2. Write test for it (RED)
3. Run test, confirm it fails
4. Write minimum code (GREEN)
5. Run test, confirm it passes
6. Quick refactor if obvious smell
7. Run tests again
8. → Next behavior
```

### Checkpoint (after feature complete)

When a logical chunk of work is done, run the checkpoint before continuing.

**Dispatch checkpoint agent:**
```
Task tool:
- subagent_type: "general-purpose"
- model: "haiku"
- description: "Hack checkpoint"
- prompt: |
    Quick validation checkpoint for hack mode.

    FILES CHANGED:
    [list files]

    VALIDATE:
    1. PATTERNS - Does new code follow existing patterns in codebase?
       - Naming conventions match?
       - Error handling matches nearby code?
       - File organization consistent?

    2. TESTS - Are tests valid?
       - Testing behavior, not implementation?
       - Edge cases covered?
       - Test names describe the behavior?

    3. INTEGRATION - Will this work with the rest?
       - Imports/exports correct?
       - Types align?
       - No obvious conflicts?

    RETURN:
    - ✅ PASS: Ready to continue
    - 🔧 FIX: [specific issues to address]

    Be fast. Be specific. No essays.
```

**If checkpoint returns FIX:** Address issues, run tests, re-checkpoint.

**If checkpoint returns PASS:** Continue to next feature or exit.

### End
```
All behaviors working + checkpoint passed? → Done
Want deeper review? → /review-changes
```

---

## Test Commands by Language

| Language | Run Tests |
|----------|-----------|
| TypeScript/JS | `npm test` or `npx jest [file]` |
| Python | `pytest [file]` or `python -m pytest` |
| Go | `go test ./...` |
| Rust | `cargo test` |
| C# | `dotnet test` |

Detect from project and use appropriate command.

---

## Anti-Patterns

| If You Catch Yourself... | Stop and... |
|--------------------------|-------------|
| Writing code before test | Delete it, write test first |
| Writing multiple tests at once | Pick one, delete others |
| Refactoring while red | Undo, get green first |
| Planning for 10 minutes | Just write a test |
| Asking "what if X?" | Write test for X, then decide |
| Making it "nice" before it works | Ship ugly, refactor when green |
| Skipping checkpoint "it's small" | Small mistakes compound. Checkpoint. |
| Checkpoint after every test | Too slow. Checkpoint after feature. |

---

## Example Session

```
User: /hack add email validation to signup form

Claude: Got it. Let me find the signup code and tests.

[Reads signup.ts, signup.test.ts]

First behavior: reject empty email.

RED:
test('rejects empty email', () => {
  expect(validateEmail('')).toBe(false);
});

Running... ❌ validateEmail is not defined

GREEN:
function validateEmail(email: string): boolean {
  return email.length > 0;
}

Running... ✅

Next behavior: reject missing @.

RED:
test('rejects email without @', () => {
  expect(validateEmail('invalid')).toBe(false);
});

Running... ❌ expected false, got true

GREEN:
function validateEmail(email: string): boolean {
  return email.length > 0 && email.includes('@');
}

Running... ✅

[...more behaviors until feature complete...]

CHECKPOINT:
[Dispatches haiku agent]

Agent returns:
✅ PASS
- Patterns: Matches existing validation in passwordValidator.ts
- Tests: Good behavior coverage, names are clear
- Integration: Export added to index.ts ✓

Ready for next feature or done.
```

---

## When to Exit Hack Mode

- Feature complete + checkpoint passed → Done (or `/review-changes` for deeper review)
- Checkpoint keeps failing → Stop, something's wrong with the approach
- Scope creep detected → `/whiteboarding` (stop, plan properly)
- Stuck on architecture → `/prototype` first
- Need multiple files/systems → Exit hack mode, this is too big

---

## Quick Ref

```
/hack [goal]     → Start hacking
/review-changes  → Quick review when done (optional)
/whiteboarding   → Escape hatch if scope explodes
```
