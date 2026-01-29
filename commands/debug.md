---
description: "Debug loop: predict → log → run → resolve or narrow. Tasks keep you on track."
argument-hint: "[error message / bug description / 'test X is failing']"
allowed-tools: ["Bash", "Glob", "Grep", "Read", "Edit", "Write", "Task", "Skill", "AskUserQuestion", "TaskCreate", "TaskUpdate", "TaskList"]
---

# /code-foundations:debug

**One task at a time. Predict, log, run. Resolve or narrow. Repeat.**

---

## Load Skill

```
Skill(code-foundations:cc-debugging)
```

---

## How It Works

You always have a **current task** — the question you're trying to answer.

Each cycle:
1. **Predict** what you expect to see
2. **Log** to test that prediction
3. **Run** and check the output
4. **Resolve** the task:
   - Answered? → Mark complete, create next task
   - Need more info? → Create narrower task

The task list is your debug trail. It keeps you focused and shows your reasoning.

---

## The Resolution Loop

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   CURRENT TASK: "Why does login fail 20% of the time?"     │
│                                                             │
│   1. PREDICT   "Cache should HIT on second request"         │
│   2. LOG       Add log at cache check                       │
│   3. RUN       Execute, check output                        │
│                                                             │
│   4. RESOLVE   What did we learn?                           │
│      ├─ Answered → complete task, what's next?              │
│      │   ├─ Root cause found → TaskCreate("Fix: ...")       │
│      │   ├─ Fix applied → TaskCreate("Verify: ...")         │
│      │   └─ Verified → Done!                                │
│      │                                                      │
│      └─ Need more info → TaskCreate("Why does X happen?")   │
│         (narrower question, keep digging)                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Task Types

| Task | Question It Answers |
|------|---------------------|
| `Investigate: [area]` | Where is the problem? |
| `Narrow: [specific thing]` | Is it this specific thing? |
| `Fix: [root cause]` | Apply the fix |
| `Verify: [expected behavior]` | Does the fix work? |

---

## Predictions

Before adding any log, state:

```
PREDICT: [what I expect to see]
IF WRONG: [what that would mean]
```

This forces you to think. When output arrives, you immediately know if you're on track.

---

## Example Session

```
/code-foundations:debug login fails 20% of the time

─────────────────────────────────────────────────────────────
TASK #1: Investigate login failure (20% of requests)
─────────────────────────────────────────────────────────────

PREDICT: All tokens should be valid
IF WRONG: Token generation or validation problem

LOG: Added at validateToken entry
RUN: 10 requests → 2 fail, logs show tokens are valid

Learned: Tokens are fine, problem is downstream
→ TaskCreate("Narrow: is validateToken returning wrong result?")
→ Mark #1 complete

─────────────────────────────────────────────────────────────
TASK #2: Narrow: is validateToken returning wrong result?
─────────────────────────────────────────────────────────────

PREDICT: Should return cached result on second call
IF WRONG: Cache miss = race condition or wrong key

LOG: Added at cache check
RUN: Failures show two MISS for same token within 10ms

Learned: Race condition - second request arrives before first caches
→ TaskCreate("Fix: add request deduplication")
→ Mark #2 complete

─────────────────────────────────────────────────────────────
TASK #3: Fix: add request deduplication
─────────────────────────────────────────────────────────────

FIX: Added inFlightValidations Map to dedupe concurrent requests
→ TaskCreate("Verify: parallel logins succeed")
→ Mark #3 complete

─────────────────────────────────────────────────────────────
TASK #4: Verify: parallel logins succeed
─────────────────────────────────────────────────────────────

RUN: 100 parallel logins → 0 failures
→ Mark #4 complete
→ Done!

─────────────────────────────────────────────────────────────
FINAL TASK LIST:
  #1 ✓ Investigate: login failure (20%)
  #2 ✓ Narrow: validateToken result
  #3 ✓ Fix: request deduplication
  #4 ✓ Verify: parallel logins
─────────────────────────────────────────────────────────────
```

---

## Staying On Track

The task list prevents:
- **Rabbit holes** — You see where you've been
- **Forgetting to verify** — Verify task is explicit
- **Losing context** — Each task documents what you learned
- **Guessing** — Predictions force structured thinking

If you feel lost: `TaskList` — see where you are.

---

## Anti-Patterns

| Temptation | Reality |
|------------|---------|
| "I'll just try this fix" | Create a task first. Predict. Log. Prove it. |
| "I don't need a task for this" | Tasks keep you honest. Create one. |
| "I'll add lots of logs" | One prediction per cycle. Stay focused. |
| "It mostly works now" | Create verify task. Prove it works 100%. |

---

## Quick Reference

```
/code-foundations:debug [issue]

  TaskCreate("Investigate: [issue]")

  Loop on current task:
    1. PREDICT what you expect
    2. LOG to test it
    3. RUN and check
    4. RESOLVE:
       - Need more info → TaskCreate (narrow)
       - Found cause → TaskCreate (fix)
       - Applied fix → TaskCreate (verify)
       - Verified → Done

  Task list = your debug trail
```
