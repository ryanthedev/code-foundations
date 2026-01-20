---
description: "TDD hacker mode. No plans, no checkpoints, just code. Write test → make it pass → refactor → repeat."
argument-hint: "[what to build]"
allowed-tools: ["Bash", "Glob", "Grep", "Read", "Edit", "Write"]
---

# Hack Mode

Fast iteration. No ceremony. You and me slinging code.

---

## The Loop

```
1. RED    - Write a failing test (or describe what should work)
2. GREEN  - Minimum code to pass
3. REFACTOR - Clean it up
4. REPEAT
```

**No subagents. No plan files. No checkpoints. Direct execution.**

---

## Rules

1. **Tests first** - If no test exists, write one before coding
2. **Smallest step** - One behavior at a time
3. **Run tests constantly** - After every change
4. **Refactor only when green** - Never refactor broken code
5. **No gold plating** - If it passes, move on

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

### End
```
All behaviors working? → Done
Want review? → /review-changes (optional)
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

[continues...]
```

---

## When to Exit Hack Mode

- Feature complete → `/review-changes` (optional)
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
