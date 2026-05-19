# Build Failure & Resume Protocol

Used by the orchestrator (`commands/build.md`) when implementation encounters a blocker that the per-phase Gate Failure Protocol cannot resolve, or when resuming a previously blocked plan.

These are cold paths — they fire only on real failures or explicit resume.

---

## Build Failure Protocol

If implementation fails (beyond the per-phase retry cap, or a structural blocker like missing dependency):

1. **Stop immediately** — don't proceed to next task.
2. **Document failure** in the plan's execution log:

   ```markdown
   ### Phase N: [Name]
   - [x] Task 1 - Complete
   - [ ] Task 2 - **FAILED**
     Error: [description]
     Attempted: [what was tried]
   ```

3. **Update plan status:** `Status: blocked`
4. **Ask user:**

   ```
   Task failed. Options:
   - (A) Debug now
   - (B) Skip and continue
   - (C) Pause build
   ```

---

## Resume Protocol

When resuming a blocked plan (status: `blocked` on load):

1. Read execution log.
2. Find last successful checkpoint.
3. Show: `Resuming from Phase N, Task M. Last failure: [description]`
4. Ask: `Ready to retry, or should we discuss the blocker first?`
