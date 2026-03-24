# Example: Full PR Review

This shows a complete `/code-foundations:review --pr` run with 10 checklists and 614 checks.

---

```
 ▐▛███▜▌   Claude Code v2.1.27
▝▜█████▛▘  Opus 4.5 · Claude Max
  ▘▘ ▝▝    ~/repos/PricingAPI

❯ /code-foundations:review --pr

⏺ Starting PR review with the full 614-check profile.

  PLUGIN_ROOT: /Users/user/.claude/plugins/cache/rtd/code-foundations/3.0.5

⏺ Read 1 file (ctrl+o to expand)

⏺ Profile loaded. 10 checklists identified. Let me validate the checklist paths exist and ask about the diff target.

⏺ User answered Claude's questions:
  ⎿  · What do you want to review? → Branch diff (Recommended)

⏺ Bash(\
      REPO_ROOT=$(git rev-parse --show-toplevel) && \…)
  ⎿  REPO_ROOT=/Users/user/repos/PricingAPI
     BASE_DIR=/tmp/PricingAPI-x-features-header-toggle-1237
     MERGE_BASE=0a7a1e4b30fac3b73e220a4c832cc3d5da1bc6b4
     … +15 lines (ctrl+o to expand)

⏺ Review Configuration

  Profile: pr - Full PR review - 10 skills, 614 checks
  Checklists: 10
  Target: Branch diff from main (14 files)
  Output: /tmp/PricingAPI-x-features-header-toggle-1237

  Files to review:
  - 6 test files
  - 8 source files (adapters, middleware, services, constants)

  Proceeding with extraction phase. I'll dispatch 3 extraction agents (5 files each max).

⏺ 3 Task agents finished (ctrl+o to expand)
   ├─ Extract batch 1 · 7 tool uses · 58.1k tokens
   │  ⎿  Done
   ├─ Extract batch 2 · 7 tool uses · 35.5k tokens
   │  ⎿  Done
   └─ Extract batch 3 · 6 tool uses · 18.1k tokens
      ⎿  Done

⏺ Extraction complete. Let me merge the results and proceed to Phase 2 - Checking.

⏺ Bash(/usr/bin/jq -s '{files: map(.files) | add}' /tmp/PricingAPI-x-features-header-toggle-1237/extraction/batch-*.json >
      /tmp/PricingAPI-x-features-header-toggle-1237/units.json && echo "Merged" && …)
  ⎿  Merged
     14

⏺ Extraction merged (14 files). Now launching Phase 2 - Checking with all 10 checklist agents in parallel.

⏺ 10 Task agents finished (ctrl+o to expand)
   ├─ Check: cc-defensive-programming · 25 tool uses · 105.2k tokens
   │  ⎿  Done
   ├─ Check: aposd-simplifying-complexity · 26 tool uses · 104.2k tokens
   │  ⎿  Done
   ├─ Check: aposd-reviewing-module-design · 36 tool uses · 106.1k tokens
   │  ⎿  Done
   ├─ Check: cc-code-layout-and-style · 28 tool uses · 117.7k tokens
   │  ⎿  Done
   ├─ Check: cc-control-flow-quality · 18 tool uses · 103.6k tokens
   │  ⎿  Done
   ├─ Check: aposd-verifying-correctness · 18 tool uses · 100.2k tokens
   │  ⎿  Done
   ├─ Check: cc-quality-practices · 20 tool uses · 106.1k tokens
   │  ⎿  Done
   ├─ Check: cc-performance-tuning · 14 tool uses · 76.3k tokens
   │  ⎿  Done
   ├─ Check: aposd-optimizing-critical-paths · 16 tool uses · 98.2k tokens
   │  ⎿  Done
   └─ Check: cc-documentation-quality · 30 tool uses · 106.2k tokens
      ⎿  Done

⏺ All 10 checklists complete. Let me verify the checking outputs and proceed to Phase 3 - Investigation.

⏺ Read 1 file (ctrl+o to expand)

⏺ All 10 checking outputs created. 8 investigation tasks pending. Let me deduplicate - RF-3, TA-3/IH-1 are the same issue (duplicate GetDpMarket). I'll
  dispatch investigation agents for the unique findings.

⏺ 2 Task agents finished (ctrl+o to expand)
   ├─ Investigate batch 1 · 12 tool uses · 37.6k tokens
   │  ⎿  Done
   └─ Investigate batch 2 · 8 tool uses · 22.4k tokens
      ⎿  Done

⏺ Investigation complete. Let me mark the investigation tasks as completed and generate the final report.

⏺ Now generating the final report.

⏺ Task(Generate final report)
  ⎿  Done (16 tool uses · 85.3k tokens · 48s)

⏺ Read 1 file (ctrl+o to expand)

⏺ ---
  Review Complete

  pr | 14 files | 10 checklists | 6 findings

  Phases

  - Extraction: 3 batches (14 files)
  - Checking: 10 checklists (614 items)
  - Investigation: 2 batches (7 findings → 6 confirmed, 1 false positive)
  - Report: generated

  Top Issues
  ┌──────────┬─────────┬───────────────────────────────────────────────────────────┬──────────────────────────────────────────────┐
  │ Priority │   ID    │                         Location                          │                    Issue                     │
  ├──────────┼─────────┼───────────────────────────────────────────────────────────┼──────────────────────────────────────────────┤
  │ 🔴       │ RF-3    │ QuoteRequestAdapter.cs:215 + RepriceRequestAdapter.cs:110 │ Duplicated GetDpMarket() method              │
  ├──────────┼─────────┼───────────────────────────────────────────────────────────┼──────────────────────────────────────────────┤
  │ 🟡       │ TC-07   │ FeatureHeaderMiddlewareTests.cs:379                       │ Missing boundary test for exactly 4096 bytes │
  ├──────────┼─────────┼───────────────────────────────────────────────────────────┼──────────────────────────────────────────────┤
  │ 🟡       │ DOC-001 │ README.md                                                 │ Missing X-Features header documentation      │
  ├──────────┼─────────┼───────────────────────────────────────────────────────────┼──────────────────────────────────────────────┤
  │ 🟢       │ DOC-002 │ HeaderFeatureToggleService.cs:5                           │ Interface lacks XML docs                     │
  ├──────────┼─────────┼───────────────────────────────────────────────────────────┼──────────────────────────────────────────────┤
  │ 🟢       │ DOC-003 │ FeatureContextAccessor.cs:5                               │ Interface lacks XML docs                     │
  ├──────────┼─────────┼───────────────────────────────────────────────────────────┼──────────────────────────────────────────────┤
  │ 🟢       │ DOC-004 │ FeatureHeaderMiddleware.cs:14                             │ Class lacks documentation                    │
  └──────────┴─────────┴───────────────────────────────────────────────────────────┴──────────────────────────────────────────────┘
  Summary

  The implementation is well-designed with good defensive programming, proper error handling, and comprehensive test coverage. The primary issue is the
  duplicated GetDpMarket() method which should be consolidated. Documentation gaps should be addressed before merging.

──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
 ☐ Action

What would you like to do with these findings?

❯ 1. Fix All
     Create a plan to fix all 6 issues
  2. Fix Critical Only
     Fix RF-3 (duplicate code) and TC-07 (missing test)
  3. View Report
     Show the full report
  4. Done
     Exit review
```

---

## Phases Explained

| Phase | Agents | Purpose |
|-------|--------|---------|
| **Extraction** | 3 haiku | Parse files, extract semantic units (functions, classes) |
| **Checking** | 10 (inherited) | Run each checklist against the code |
| **Investigation** | 2 haiku | Verify findings, reduce false positives |
| **Report** | 1 (inherited) | Merge results, generate final report |

## Checklists Used (PR Profile)

| Checklist | Checks | Focus |
|-----------|--------|-------|
| cc-defensive-programming | 31 | Error handling, validation |
| aposd-simplifying-complexity | 44 | Complexity reduction |
| aposd-reviewing-module-design | 36 | Module depth, information hiding |
| code-clarity-and-docs | 134 | Formatting, readability, comments, docs |
| cc-control-flow-quality | 124 | Loops, conditionals, nesting |
| aposd-verifying-correctness | 40 | Requirements coverage, edge cases |
| cc-quality-practices | 115 | Testing, debugging |
| performance-optimization | 90 | Performance issues, hot paths, optimization |
| **Total** | **614** | |

## Token Usage

With haiku for extraction, checking, and investigation (v3.0.7+):
- Extraction: ~112k tokens (haiku)
- Checking: ~1M tokens (10 haiku agents)
- Investigation: ~60k tokens (haiku)
- Report: ~85k tokens (inherited)

**Cost comparison:**
| Model for Checking | Estimated Cost |
|-------------------|----------------|
| Opus (v3.0.6) | $20-50+ |
| Haiku (v3.0.7+) | ~$2-5 |

Haiku handles systematic checklist execution well - deep reasoning is only needed for report synthesis.
