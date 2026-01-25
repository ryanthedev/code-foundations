# Whiteboarding Example: Z-Index Preservation During Layout Refresh

**Type:** WHITEBOARDING
**Skills:** `cc-construction-prerequisites`, `aposd-designing-deep-modules`
**Context:** Grid window manager - preserving window stacking order when applying default layout

## Why This Case Study Matters

This example demonstrates the whiteboarding skill's **discovery-first approach**:

1. **Explores before asking** - Reads 1000+ lines of code to understand the system
2. **Asks clarifying questions** - Doesn't assume what "preserve z-index" means
3. **Surfaces hidden complexity** - macOS private APIs, async window ordering events
4. **Multiple valid interpretations** - Same request could mean 3 different things

---

## The Request

```
/code-foundations:whiteboarding when I do layout refresh and I don't have any
layout and it applys the default layout. do you think it would be at all
possible to somehow preserve the z-index layout order maybe keep whatever the
top most window was? or when it adds them to a cell, it keeps whatever
z-index/layer index they were at.
```

---

## The Exploration Phase

Before asking any questions, whiteboarding loads prerequisite skills and explores:

```
⏺ Skill(code-foundations:cc-construction-prerequisites)
  ⎿  Successfully loaded skill

⏺ Skill(code-foundations:aposd-designing-deep-modules)
  ⎿  Successfully loaded skill

⏺ Let me understand the current implementation before we discuss approaches.

⏺ Explore(Explore layout refresh z-index handling)
  ⎿  Done (18 tool uses · 90.9k tokens · 1m 2s)
```

The Explore agent examined:
- `grid-cli/internal/layout/assignment.go` - How windows get assigned to cells
- `grid-server` window list APIs - How macOS reports window ordering
- `grid-cli/internal/server/snapshot.go` - How CLI receives window data
- macOS private API spec - What z-order information is available

---

## Key Discovery: Windows Parsed from Unordered Map

```
⏺ Read(grid-cli/internal/server/snapshot.go)
  ⎿  Read 617 lines

⏺ I see that windows are parsed from a map (unordered). Let me check how the
  server sends windows and whether there's any ordering information captured.
```

The exploration revealed that:
1. Server has access to `SLSWindowLevel` APIs and `windowOrdered` events (808)
2. But CLI parses windows from a JSON map - **ordering is lost in transit**
3. `AssignPosition` strategy assigns by screen position overlap, ignoring z-order

---

## The Clarifying Question

Only after understanding the system does whiteboarding ask what the user actually wants:

```
⏺ Now I understand the full picture. Let me ask the first discovery question.

  ---
  Problem Understanding

  When you run layout refresh with no existing layout state, the CLI applies a
  default layout using AssignPosition strategy, which assigns windows to cells
  based on their current screen positions (maximum overlap).

  The issue: z-index ordering is lost. Windows get assigned based on position,
  not their front-to-back stacking order. So if you had Window A in front of
  Window B, after refresh they might end up with arbitrary ordering in their
  cell's window list.

  ---
  Clarifying Question 1

  Before diving into approaches, I need to understand what behavior you
  actually want:
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ ☐ Behavior                                                                  │
│                                                                             │
│ When multiple windows end up in the same cell after a default layout apply, │
│ what should 'preserving z-index' mean?                                      │
│                                                                             │
│ ❯ 1. Frontmost window is focused                                            │
│      The window that was on top (frontmost) before refresh should be the    │
│      focused/active window in that cell after refresh                       │
│   2. Preserve stacking order in cell                                        │
│      Within each cell, windows should be ordered by their original z-order  │
│      (frontmost first in the list, affects tab cycling order)               │
│   3. Both                                                                   │
│      Frontmost gets focus AND tab cycling follows original z-order          │
│   4. Type something.                                                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Why This Matters

The user asked a simple question: "can we preserve z-index?"

But there are **three different interpretations**:

| Interpretation | Scope | Complexity |
|----------------|-------|------------|
| Frontmost gets focus | Per-cell, one-time | Low - just focus the right window after assignment |
| Preserve stacking order | Per-cell ordering | Medium - need to sort cell's window list by z-order |
| Both | Full preservation | Medium - combine both behaviors |

Without this clarifying question, the implementation could solve the wrong problem.

---

## What Exploration Revealed About Feasibility

| Requirement | Feasibility | Notes |
|-------------|-------------|-------|
| Get z-order from macOS | ✅ Available | `CGWindowListCopyWindowInfo` returns windows in front-to-back order |
| Server has ordering | ✅ Has it | `windowOrdered` event 808, `SLSWindowLevel` APIs |
| CLI receives ordering | ❌ Lost | Windows parsed from JSON map (unordered) |
| Fix needed | Propagate | Server needs to send windows as ordered array, not map |

---

## The Conversation Continues

User answers the first question:

```
⏺ User answered Claude's questions:
  ⎿  · When multiple windows end up in the same cell after a default layout
       apply, what should 'preserving z-index' mean? → Frontmost window is focused

⏺ Good. So the goal is: when default layout is applied, the frontmost window
  (before tiling) should be the focused window in its cell.
```

Follow-up question narrows scope:

```
⏺ User answered Claude's questions:
  ⎿  · Should z-index preservation also affect which window gets focused
       globally, or just within each cell? → Cell-local only (Recommended)
```

Then a question about implementation data source:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ ☐ Data source                                                               │
│                                                                             │
│ Where is the z-order information most reliably available?                   │
│                                                                             │
│   1. CGWindowListCopyWindowInfo order (Recommended)                         │
│      macOS returns windows in front-to-back order. Simple, no extra API     │
│      calls.                                                                 │
│   2. SLSGetWindowSubLevel calls                                             │
│      Query sublevel per window. More explicit but requires private API      │
│      calls for each window.                                                 │
│ ❯ 3. you should research and suggest                                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## User Pushback: "You Should Research"

The user selected option 3 instead of accepting the recommended option. This is an important pattern:

**Why this matters:**
- The AI explored during the initial phase but **assumed** it knew the best data source
- The user correctly pushed back - this is a technical decision that should be researched, not assumed
- "Never be scared to correct" - whiteboarding should encourage user pushback

**What happens next:**
- Claude will research both options more deeply
- Compare reliability, performance, edge cases
- Come back with an evidence-based recommendation

This prevents the AI from railroading the user into a premature technical decision based on incomplete analysis.

---

## Research Results: The Pushback Paid Off

After user requested research, Claude discovered something important:

```
⏺ The current code uses .optionAll which does NOT guarantee z-order.
  Let me look at what options we have:

  ---
  Research Summary: Z-Order Data Sources

  Option A: CGWindowListCopyWindowInfo with .optionOnScreenOnly
  - ✅ Returns windows in front-to-back z-order (documented by Apple)
  - ❌ Only returns windows on the current space (not across all spaces)
  - Current code uses .optionAll which does NOT guarantee ordering

  Option B: Query kCGWindowLayer + sublevel per window
  - ✅ Works across spaces
  - ❌ kCGWindowLayer only gives level (0=normal, 3=floating), not
      fine-grained order within level
  - Would need SLSGetWindowSubLevel (private API) for ordering within
      same level

  Recommendation:
  For the specific case of "default layout apply" where we're operating
  on the active space only, we can do a secondary query with
  .optionOnScreenOnly to get z-order, then use that to sort windows
  before assignment.
```

**Key insight from research:** The original "recommended" option (`CGWindowListCopyWindowInfo order`) was incomplete. The current code uses `.optionAll` which does NOT guarantee z-order. The research revealed a nuanced solution: use a **secondary query** with `.optionOnScreenOnly` specifically for z-order.

User accepts the researched recommendation:

```
⏺ User answered Claude's questions:
  ⎿  · The 'default layout apply' only operates on the current active space.
       Is it acceptable to make an additional CGWindowList query with
       .optionOnScreenOnly to get z-order? → Yes, extra query is fine
```

---

## Why the Pushback Mattered

| Without Pushback | With Pushback |
|------------------|---------------|
| "Use CGWindowListCopyWindowInfo order" | Discovered `.optionAll` doesn't guarantee order |
| Assumed current code would work | Identified need for secondary query |
| Generic recommendation | Targeted solution for the specific use case |
| May have led to bugs | Evidence-based approach |

The user's "you should research" response transformed a surface-level recommendation into a proper technical analysis.

---

## The Approaches

After research, whiteboarding presents three approaches with trade-offs:

```
Approach A: Server-Side Z-Order Index (Recommended)

Idea: Server includes a zOrder field in window data (derived from position
in .optionOnScreenOnly query). CLI uses this to determine frontmost window
per cell.

Pros:
- Z-order data available to CLI without extra round-trip
- Can be used by other features (visualize, debug)
- Clean separation: server provides data, CLI makes decisions

Cons:
- Server changes required
- Extra CGWindowList query on server

---
Approach B: CLI Requests Z-Order On-Demand

Idea: CLI makes a new RPC call getZOrder that returns window IDs in
front-to-back order. Only called during default layout apply.

Pros:
- No change to existing dump/snapshot flow
- Server complexity isolated to new endpoint

Cons:
- Extra round-trip during layout apply
- More moving parts

---
Approach C: CLI Infers Z-Order From Focus History

Idea: Track which windows have been focused recently. Most recently
focused = frontmost.

Pros:
- No server changes
- Works with existing data

Cons:
- Inaccurate (focus != z-order; windows can be raised without focusing)
- Doesn't work for windows never focused
```

User selects Approach A.

---

## The Implementation Plan

Whiteboarding produces a phased implementation plan:

```
Phase 1: Server - Add Z-Order to Window State

Changes to StateManager.swift:
1. Add zOrder: Int field to WindowState struct (lower = closer to front)
2. In refreshWindows():
   - Do secondary query with .optionOnScreenOnly to get on-screen windows
     in z-order
   - Build a windowID → zOrder map from this ordered list
   - Populate zOrder field when building WindowState
   - Windows not on screen get zOrder = Int.max (back)

Files: grid-server/Sources/GridServer/StateModels.swift,
       grid-server/Sources/GridServer/StateManager.swift

---
Phase 2: CLI - Parse and Use Z-Order

Changes to snapshot.go:
1. Add ZOrder int field to WindowInfo struct
2. Parse zOrder from server response in parseWindow()

Changes to assignment.go:
1. Add ZOrder int field to Window struct
2. In assignByPosition(): after assigning windows to cells, sort each
   cell's window list by ZOrder (ascending = frontmost first)

Files: grid-cli/internal/server/snapshot.go,
       grid-cli/internal/layout/assignment.go

---
Phase 3: Apply Layout - Set Focused Window Per Cell

Changes to apply.go:
1. In ApplyLayout() when strategy is AssignPosition:
   - After AssignWindows() returns, each cell has windows ordered by zOrder
   - The first window in each cell's list (lowest zOrder = frontmost)
     becomes the cell's "active" window
   - Send this as the focused window for that cell to the server

Files: grid-cli/internal/layout/apply.go
```

---

## Final Verification

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ ☐ Verify                                                                    │
│                                                                             │
│ Does this implementation plan look correct? Any concerns before I save it?  │
│                                                                             │
│ ❯ 1. Looks good, save the plan                                              │
│      Save to docs/plans/ for implementation                                 │
│   2. Need clarification                                                     │
│      I have questions about the approach                                    │
│   3. Type something.                                                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

The plan gets saved to `docs/plans/` for execution via `/code-foundations:building`.

---

## The Quirk: Exit Plan Mode?

After saving the plan:

```
⏺ Bash(mkdir -p /Users/r/repos/theGrid/docs/plans)
  ⎿  (No content)

⏺ Write(docs/plans/2026-01-24-preserve-zorder-default-layout.md)
  ⎿  Wrote 144 lines to docs/plans/2026-01-24-preserve-zorder-default-layout.md

──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
 Exit plan mode?

  Claude wants to exit plan mode

  ❯ 1. Yes
    2. No
```

**The funny part:** The user never put Claude in plan mode. The whiteboarding skill prompted to exit a mode that was never entered.

This is a quirk in the interaction between:
- The `ExitPlanMode` tool (designed for formal plan mode)
- The whiteboarding skill (which has its own planning flow)

The skill completed successfully - the plan was saved - but the "exit plan mode" prompt was spurious. User can just say "Yes" to dismiss it.

---

## The Clean Handoff

After dismissing the exit prompt, whiteboarding provides a clean summary and next steps:

```
⏺ Exited plan mode

⏺ Plan saved to docs/plans/2026-01-24-preserve-zorder-default-layout.md.

  Summary:
  - Server will add a zOrder field to window data using a secondary
    CGWindowListCopyWindowInfo(.optionOnScreenOnly) query
  - CLI parses this field and sorts windows by zOrder when assigning to cells
  - Result: frontmost window before tiling becomes the focused window in its cell

  Next steps:
  1. Refresh context → /code-foundations:building docs/plans/2026-01-24-preserve-zorder-default-layout.md
     (recommended for complex)
  2. Continue now → /code-foundations:building if you want to start implementing immediately

✻ Brewed for 3m 42s
```

Then the user runs:

```
❯ /code-foundations:building docs/plans/2026-01-24-preserve-zorder-default-layout.md
```

**The workflow:**
1. Whiteboarding produces a plan file in `docs/plans/`
2. Summary reminds user what was decided
3. Next steps gives exact command to execute the plan
4. User runs building with the plan path

No copy-paste, no context switching, no manual handoff. The plan file becomes the input to building.

---

## Building: Structured Execution

Running the building command:

```
❯ /code-foundations:building docs/plans/2026-01-24-preserve-zorder-default-layout.md

⏺ I'll execute the building skill for the specified plan. Let me start by
  checking the current branch and loading the plan.

⏺ Bash(git branch --show-current)
  ⎿  main

⏺ Read(docs/plans/2026-01-24-preserve-zorder-default-layout.md)
  ⎿  Read 144 lines

⏺ Branch Gate: FAILED - Currently on main. I need to create a feature branch first.

⏺ Bash(git checkout -b feature/preserve-zorder-default-layout)
  ⎿  Switched to a new branch 'feature/preserve-zorder-default-layout'
```

**Branch gate:** Building refuses to execute on `main`. Automatically creates a feature branch from the plan name.

```
⏺ Now let me initialize tracking and set up the building directory.

⏺ Bash(mkdir -p docs/building)
  ⎿  (No content)
✔ Task #1 created: Phase 1: Server - Add Z-Order to Window State
✔ Task #2 created: Phase 2: CLI - Parse Z-Order
✔ Task #3 created: Phase 3: CLI - Sort by Z-Order in assignByPosition
✔ Task #4 created: Phase 4: CLI - Verify Focus Frontmost Window
✔ Task #2 updated: blockedBy
✔ Task #3 updated: blockedBy
✔ Task #4 updated: blockedBy

· Hullaballooing… (Esc to interrupt · ctrl+t to hide tasks)
  ⎿  ◻ #1 Phase 1: Server - Add Z-Order to Window State
     ◻ #2 Phase 2: CLI - Parse Z-Order › blocked by #1
     ◻ #3 Phase 3: CLI - Sort by Z-Order in assignByPosition › blocked by #2
     ◻ #4 Phase 4: CLI - Verify Focus Frontmost Window › blocked by #3
```

**Task tracking:** Building parses the plan phases and creates tasks with dependencies. Phase 2 can't start until Phase 1 completes, etc.

| What Building Does | Why |
|--------------------|-----|
| Branch gate | Prevents accidental commits to main |
| Parse plan phases | Creates structured checklist from plan |
| Set dependencies | Enforces sequential execution |
| Task tracking | Progress visible, can resume if interrupted |

---

## Building: DISCOVERY Phase

Each phase starts with a DISCOVERY subagent:

```
⏺ Phase 1: Server - Add Z-Order to Window State

  Starting the gated execution sequence for Phase 1.

  DISCOVERY Subagent

⏺ Explore(Discovery for Phase 1 server zOrder)
  ⎿  Done (11 tool uses · 60.1k tokens · 33s)

⏺ Write(docs/building/preserve-zorder-phase-1-discovery.md)
  ⎿  Wrote 82 lines to docs/building/preserve-zorder-phase-1-discovery.md
       1 # Phase 1 Discovery - Window State Z-Order Implementation
       2
       3 ## 1. Current WindowState Struct (StateModels.swift:170-254)
       4
       5 **Location:** Lines 170-254
       6
       7 **Current fields:**
       8 - `id: UInt32` - Window ID
       9 - `frame: CGRect` - Window bounds
      10 - `level: Int32` - Window layer/level (from `kCGWindowLayer`)
     … +72 lines (ctrl+o to expand)
```

**DISCOVERY workflow:**
1. Runs Explore subagent (60k tokens, 33s) to understand current code
2. Writes findings to `docs/building/preserve-zorder-phase-1-discovery.md`
3. Documents exact file locations, current fields, existing patterns

This ensures the implementation has accurate context about the current state of the code.

---

## Building: PRE-GATE Phase

After discovery, building runs a PRE-GATE subagent:

```
⏺ PRE-GATE Subagent

⏺ Task(PRE-GATE for Phase 1 server zOrder)
  ⎿  Prompt:
       Load skills: cc-pseudocode-programming, aposd-designing-deep-modules

       Read: docs/building/preserve-zorder-phase-1-discovery.md

       Write pseudocode for Phase 1 implementation to:
         docs/building/preserve-zorder-phase-1-pseudocode.md

       The task is to add zOrder field to WindowState and populate it
       in refreshWindows().

       The pseudocode should cover:
       1. StateModels.swift changes (add field, add to CodingKeys,
          add to initializer)
       2. StateManager.swift changes (add secondary CGWindowList query,
          build zOrder map, populate field)

       Return: file path only

     ❯ Load skills: cc-pseudocode-programming, aposd-designing-deep-modules
     Skill(cc-pseudocode-programming)
     Skill(aposd-designing-deep-modules)
     Read(/Users/r/repos/theGrid/docs/building/preserve-zorder-phase-1-discovery.md)
```

**PRE-GATE workflow:**
1. Loads `cc-pseudocode-programming` + `aposd-designing-deep-modules` skills
2. Reads discovery notes from previous exploration
3. Writes pseudocode **before** implementation
4. Pseudocode saved to `docs/building/` for review

This follows the Code Complete principle: design in pseudocode first, translate to code second. The pseudocode becomes a checkpoint - if the design is wrong, catch it before writing code.

---

## Building: IMPLEMENT Subagent

After PRE-GATE passes, the implementation agent launches:

```
⏺ PRE-GATE passed. Now launching the implementation agent.

  IMPLEMENT Subagent

  code-foundations:implementation-agent(Implement Phase 1 server zOrder)
  ⎿  Prompt:
       Read input files:
       - docs/building/preserve-zorder-phase-1-discovery.md
       - docs/building/preserve-zorder-phase-1-pseudocode.md

       Implement Phase 1: Add zOrder field to WindowState and populate
       in refreshWindows()

       Files to modify:
       1. grid-server/Sources/GridServer/StateModels.swift
         - Add var zOrder: Int32 field after displayUUID
         - Add case zOrder to CodingKeys enum
         - Add self.zOrder = Int32.max to init(id:)
       2. grid-server/Sources/GridServer/StateManager.swift
         - After the main CGWindowList query succeeds, add secondary
           query with .optionOnScreenOnly
         - Build zOrderMap dictionary
         - Populate windowState.zOrder in the processing loop

       Return: DONE or BLOCKED

     ❯ Read input files:
     Skill(cc-pseudocode-programming)
     Skill(cc-defensive-programming)
     Skill(aposd-designing-deep-modules)

     Read(/Users/r/repos/theGrid/docs/building/preserve-zorder-phase-1-discovery.md)
     Read(/Users/r/repos/theGrid/docs/building/preserve-zorder-phase-1-pseudocode.md)
     Read(/Users/r/repos/theGrid/docs/plans/2026-01-24-preserve-zorder-default-layout.md)

     Read(/Users/r/repos/theGrid/grid-server/Sources/GridServer/StateMo...
```

**IMPLEMENT agent workflow:**
1. Loads skills: `cc-pseudocode-programming`, `cc-defensive-programming`, `aposd-designing-deep-modules`
2. Reads discovery notes, pseudocode, and original plan
3. Then reads actual source files
4. Implements changes following the pseudocode
5. Returns DONE or BLOCKED

**Notice:** The agent loads skills before touching code. This ensures defensive programming patterns and deep module design principles are active during implementation - not just during planning.

---

## Building: POST-GATE Review

After implementation, a POST-GATE reviewer checks the work:

```
⏺ code-foundations:correctness-reviewer(POST-GATE for Phase 1 server zOrder)
  ⎿  Prompt:
       Read all phase files:
       - docs/building/preserve-zorder-phase-1-discovery.md
       - docs/building/preserve-zorder-phase-1-pseudocode.md

       Review the implementation in:
       - grid-server/Sources/GridServer/StateModels.swift
         (WindowState struct around line 170-260)
       - grid-server/Sources/GridServer/StateManager.swift
         (refreshWindows() function around line 957-1100)

       Check:
       1. Does the implementation match the pseudocode?
       2. Is the zOrder field correctly added to WindowState with proper default?
       3. Is the secondary CGWindowList query correctly placed and implemented?
       4. Is the zOrder map correctly built and used?
       5. Are there any bugs or edge cases not handled?

       Write review to: docs/building/preserve-zorder-phase-1-review.md
       Return: PASS or FAIL

     ❯ Read all phase files:
     Read(/Users/r/repos/theGrid/docs/building/preserve-zorder-phase-1-discovery.md)
     Read(/Users/r/repos/theGrid/docs/building/preserve-zorder-phase-1-pseudocode.md)
     Read(grid-server/Sources/GridServer/StateModels.swift · lines 170-269)
     Read(grid-server/Sources/GridServer/StateManager.swift · lines 957-1106)

     Search(pattern: "**/*test*.swift", path: "/Users/r/repos/theGrid/grid-server")
     Search(pattern: "zOrder", path: "/Users/r/repos/theGrid/grid-server")
```

**POST-GATE workflow:**
1. Reads discovery + pseudocode (knows what was intended)
2. Reads actual implementation
3. Checks implementation against pseudocode
4. Searches for tests and usage patterns
5. Writes review to `docs/building/`
6. Returns PASS or FAIL

---

## Observation: Skill Loading Inconsistency

The **implementation-agent** explicitly loaded skills:
```
Skill(cc-pseudocode-programming)
Skill(cc-defensive-programming)
Skill(aposd-designing-deep-modules)
```

The **correctness-reviewer** did NOT load skills - it just started reading files.

**Expected behavior:** The `correctness-reviewer` agent definition (`agents/correctness-reviewer.md`) says:

```
## STOP - Load Skills First

Before reviewing, load your skill lenses using the Skill tool:
1. `Skill(code-foundations:aposd-verifying-correctness)`
2. `Skill(code-foundations:cc-quality-practices)`
```

The agent should have loaded these skills but didn't. This is either:
- An **older plugin version** that doesn't have this instruction
- The agent **not following its own instructions** (needs investigation)

---

## Summary: The Whiteboarding Flow

| Stage | What Happened |
|-------|---------------|
| **Load skills** | `cc-construction-prerequisites`, `aposd-designing-deep-modules` |
| **Explore** | 90k tokens examining layout, assignment, macOS APIs |
| **Clarify scope** | 3 interpretations → user picks "frontmost gets focus" |
| **Clarify scope** | Global vs cell-local → user picks cell-local |
| **Research** | User pushes back on assumed recommendation |
| **Discover** | `.optionAll` doesn't guarantee z-order; need secondary query |
| **Approaches** | 3 options with trade-offs → user picks server-side field |
| **Plan** | 3-phase implementation with specific files and changes |
| **Verify** | User approves, plan saved for building |

---

## Key Takeaways

1. **Explore before asking** - 1 minute of exploration (90k tokens in subagent) revealed the real constraint: ordering lost in JSON serialization

2. **Clarify interpretation** - "Preserve z-index" has 3 valid meanings with different implementation costs

3. **Surface hidden complexity** - User might not know that macOS provides z-order but the CLI discards it

4. **Feasibility assessment** - The answer to "is this possible?" is "yes, but requires server-side change to preserve ordering in transit"

5. **User can push back** - When given options with a "recommended" choice, user can say "research more" - the AI shouldn't assume it knows best on technical decisions
