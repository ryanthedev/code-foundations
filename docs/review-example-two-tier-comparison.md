# Review Example: Two-Tier Review Comparison

**Type:** REVIEW
**Commands:** `pr-review-toolkit:code-reviewer` vs `/code-foundations:review-changes`
**Context:** Zoxide PATH fallback feature (5 files, 225 lines)

## Why This Case Study Matters

This example demonstrates when to use quick single-agent review vs. full multi-agent review:

1. **First pass (quick)** - Single agent validates the implementation is reasonable
2. **Second pass (thorough)** - Three parallel agents find subtle issues the first pass missed

---

## The Scenario

A feature adding configurable PATH fallback for zoxide binary discovery:
- Resolution order: config override → PATH lookup → fallback paths
- 5 files changed across config, sources, and tests

---

## First Review: Quick Single-Agent

```
⏺ pr-review-toolkit:code-reviewer(Review zoxide PATH fallback changes)
  ⎿  Done (13 tool uses · 31.2k tokens · 1m 9s)

⏺ Let me check the changes directly and verify everything looks good.

⏺ Bash(git diff --stat)
  ⎿   grid-cli/cmd/grid/main.go                 |  1 +
      grid-cli/internal/config/types.go         | 11 ++---
      grid-cli/internal/sources/sources.go      |  5 ++-
     … +3 lines (ctrl+o to expand)

⏺ Bash(git diff grid-cli/internal/sources/zoxide.go)
  ⎿  diff --git a/grid-cli/internal/sources/zoxide.go b/grid-cli/internal/sources/zoxide.go
     index 19716a6..a052c32 100644
     --- a/grid-cli/internal/sources/zoxide.go
     … +65 lines (ctrl+o to expand)

⏺ Bash(git diff grid-cli/internal/sources/sources_test.go)
  ⎿  diff --git a/grid-cli/internal/sources/sources_test.go b/grid-cli/internal/sources/sources_test.go
     index 414573d..cb7a970 100644
     --- a/grid-cli/internal/sources/sources_test.go
     … +97 lines (ctrl+o to expand)

⏺ Bash(git diff grid-cli/internal/config/types.go grid-cli/internal/sources/sources.go grid-cli/cmd/grid/main.go)
  ⎿  diff --git a/grid-cli/cmd/grid/main.go b/grid-cli/cmd/grid/main.go
     index 1f342a4..161ea98 100644
     --- a/grid-cli/cmd/grid/main.go
     … +54 lines (ctrl+o to expand)

⏺ Bash(cd /Users/r/repos/theGrid/grid-cli && go test ./internal/sources/... -v -run "Zoxide|FindZoxide" 2>&1)
  ⎿  === RUN   TestDiscoverZoxide
         sources_test.go:80: found 171 zoxide paths
     --- PASS: TestDiscoverZoxide (0.02s)
     … +12 lines (ctrl+o to expand)

⏺ All tests pass. Here's my review summary:

  Code Review Summary

  Overall: Good implementation ✅

  Positives

  - Clean separation of concerns with findZoxideBinary() function
  - Proper priority ordering: config → PATH → fallbacks
  - Good structured logging at each resolution step
  - Tests cover all paths: config override (valid/invalid), PATH lookup, fallback verification
  - Config field correctly uses omitempty for optional nature

  Minor observations (not blocking)

  - The tests are pragmatic - they test what can be tested on the host system and skip gracefully when zoxide isn't available
  - Fallback paths correctly handle ~ expansion via filepath.Join(home, ...)

  Verified

  - Config wiring from YAML → sources package is complete
  - All existing tests continue to pass
  - New tests cover the added functionality
```

**Verdict:** ✅ Good implementation

**Time:** 1m 9s

---

## Second Review: Full Three-Agent Parallel

```
❯ /code-foundations:review-changes

⏺ I'll execute the review-changes workflow. Let me start by creating the execution checklist.
✔ Task #1 created: Get diff and check size
✔ Task #2 created: Run triage to create JSON for review agents
✔ Task #3 created: GATE: Dispatch ALL 3 review agents in parallel
✔ Task #4 created: GATE: Wait for all 3 agents to complete
✔ Task #5 created: Aggregate results grouped by action type
✔ Task #6 created: GATE: Get user decision on execution
✔ Task #1 updated: status → in progress

⏺ Bash(git diff --name-only && echo "---" && git diff | wc -l)
  ⎿  grid-cli/cmd/grid/main.go
     grid-cli/internal/config/types.go
     grid-cli/internal/sources/sources.go
     … +4 lines (ctrl+o to expand)
✔ Task #1 updated: status → completed
✔ Task #2 updated: status → in progress

⏺ Bash(RUN_ID=$(date +%Y%m%d-%H%M%S) && mkdir -p /tmp/review-changes-$RUN_ID && echo $RUN_ID)
  ⎿  20260124-115044

⏺ Task(Triage changes)
  ⎿  Done (11 tool uses · 29.2k tokens · 1m 34s)
✔ Task #2 updated: status → completed
✔ Task #3 updated: status → in progress

⏺ Now dispatching ALL 3 review agents in parallel:

⏺ 3 agents finished (ctrl+o to expand)
   ├─ code-foundations:defensive-reviewer (Defensive review) · 6 tool uses · 22.2k tokens
   │  ⎿  Done
   ├─ code-foundations:quality-reviewer (Quality review) · 15 tool uses · 27.0k tokens
   │  ⎿  Done
   └─ code-foundations:correctness-reviewer (Correctness review) · 7 tool uses · 28.0k tokens
      ⎿  Done
✔ Task #3 updated: status → completed
✔ Task #4 updated: status → completed
✔ Task #5 updated: status → in progress

⏺ Bash(cat /tmp/review-changes-20260124-115044/defensive.md)
  ⎿  ## Defensive Review

     ### Fix (high confidence)
     … +76 lines (ctrl+o to expand)

⏺ Bash(cat /tmp/review-changes-20260124-115044/quality.md)
  ⎿  ## Quality Review

     ### Positive Patterns
     … +24 lines (ctrl+o to expand)

⏺ Bash(cat /tmp/review-changes-20260124-115044/correctness.md)
  ⎿  ## Correctness Review

     ### Fix (high confidence)
     … +86 lines (ctrl+o to expand)

⏺ Now I'll write the aggregated report and present it to the user.

⏺ Write(/tmp/review-changes-20260124-115044/REPORT.md)
  ⎿  Wrote 97 lines to ../../../../../tmp/review-changes-20260124-115044/REPORT.md
✔ Task #5 updated: status → completed
✔ Task #6 updated: status → in progress

⏺ Review Changes Report

  Scope

  - grid-cli/cmd/grid/main.go
  - grid-cli/internal/config/types.go
  - grid-cli/internal/sources/sources.go
  - grid-cli/internal/sources/sources_test.go
  - grid-cli/internal/sources/zoxide.go

  Total: 5 files, 225 lines changed

  Verdict: NEEDS WORK

  ---
  Fix

  High confidence. Apply now.

  grid-cli/internal/sources/zoxide.go

  1. [IMPORTANT] Line 32 - Silently discarding UserHomeDir error causes incorrect fallback paths

  When os.UserHomeDir() fails, filepath.Join("", ".cargo", "bin", "zoxide") produces
  relative path ".cargo/bin/zoxide" instead of absolute.

  // Fall back to common installation locations
  home, err := os.UserHomeDir()
  if err != nil {
      jsonlog.Log("sources.zoxide.warn", jsonlog.WithMsg("could not determine home directory"), jsonlog.WithData(map[string]any{"err": err.Error()}))
      home = ""
  }
  fallbackPaths := []string{}
  if home != "" {
      fallbackPaths = append(fallbackPaths, filepath.Join(home, ".cargo", "bin", "zoxide"))
  }
  fallbackPaths = append(fallbackPaths,
      "/opt/homebrew/bin/zoxide",
      "/usr/local/bin/zoxide",
  )

  2. [IMPORTANT] Line 66 - Silent failure when os.UserHomeDir() fails for display paths

  home, err := os.UserHomeDir()
  if err != nil {
      jsonlog.Log("sources.zoxide.warn", jsonlog.WithMsg("failed to get home directory for display"), jsonlog.WithData(map[string]any{"err": err.Error()}))
      home = ""
  }

  ---
  Investigate

  1. [IMPORTANT] Path traversal risk with configured path - Is config trusted?
  2. [IMPORTANT] Test coverage gaps - Add tests for execution errors?

  ---
  Summary Table
  ┌─────────────┬───────┐
  │   Action    │ Count │
  ├─────────────┼───────┤
  │ Fix         │ 2     │
  ├─────────────┼───────┤
  │ Investigate │ 2     │
  ├─────────────┼───────┤
  │ Plan        │ 0     │
  └─────────────┴───────┘
  ┌─────────────┬────────────────┐
  │  Reviewer   │    Verdict     │
  ├─────────────┼────────────────┤
  │ Defensive   │ ADEQUATE       │
  ├─────────────┼────────────────┤
  │ Quality     │ GOOD           │
  ├─────────────┼────────────────┤
  │ Correctness │ LIKELY CORRECT │
  └─────────────┴────────────────┘
```

**Verdict:** ⚠️ NEEDS WORK (2 fixes, 2 investigations)

**Time:** ~4m (triage + 3 parallel agents)

---

## What the Multi-Agent Review Found

### Issue 1: Silent Home Directory Failure

The quick review noted "Fallback paths correctly handle ~ expansion via filepath.Join(home, ...)"

The defensive-reviewer caught the edge case: when `os.UserHomeDir()` fails, the code sets `home = ""` and `filepath.Join("", ".cargo", "bin", "zoxide")` produces a **relative path** `.cargo/bin/zoxide` instead of skipping it entirely.

**Fix:** Only add home-based paths when home is successfully resolved.

### Issue 2: Duplicate Error Handling Pattern

The correctness-reviewer identified the same `UserHomeDir` error handling pattern appears twice in the file (lines 32 and 66), each silently continuing with empty home. This is a code smell suggesting the home directory lookup should be factored out.

### Issue 3: Path Traversal Question

The defensive-reviewer flagged a question about whether the config file is trusted. If `ZoxidePath` comes from user config, path traversal isn't a risk. But if it could come from untrusted input, validation would be needed.

---

## Comparison

| Aspect | Quick Review | Full Review |
|--------|--------------|-------------|
| **Time** | 1m 9s | ~4m |
| **Agents** | 1 | 3 parallel |
| **Token cost** | 31k | 77k (triage) + 77k (agents) |
| **Context impact** | All in main window | Offloaded to subagents |
| **Verdict** | ✅ Good | ⚠️ Needs work |
| **Issues found** | 0 blocking | 2 fixes, 2 investigations |

### Context Window Trade-off

The quick review runs in the main conversation - every diff, every file read, every analysis consumes your session's context window. After a few quick reviews, you'll hit summarization.

The full review dispatches work to **subagents**. The main conversation only sees:
- Task creation/updates
- Final aggregated report
- User decision prompt

The 77k tokens of agent work happen in isolated contexts that get discarded. Your main session stays clean for continued work.

### What Quick Review Caught
- Clean separation of concerns
- Proper priority ordering
- Good test coverage
- Config wiring complete

### What Quick Review Missed
- Silent failure edge case in `UserHomeDir()`
- Relative path bug when home directory unavailable
- Duplicate error handling pattern

---

## When to Use Each

| Situation | Command |
|-----------|---------|
| Quick sanity check during development | `pr-review-toolkit:code-reviewer` |
| Before committing to shared branch | `/code-foundations:review-changes` |
| Before creating PR | `/code-foundations:review-pr` (5 agents) |
| Time-critical, low-risk change | Quick review only |
| Complex feature, many files | Full review |

---

## Key Takeaway

The quick review correctly identified that the implementation was **functionally complete and well-structured**. The full review found **subtle edge cases** that only emerge when multiple specialized perspectives (defensive, quality, correctness) examine the same code.

Both verdicts were "correct" for their purpose:
- Quick: "Is this implementation reasonable?" → Yes
- Full: "Is this production-ready?" → Almost, but fix these edge cases first
