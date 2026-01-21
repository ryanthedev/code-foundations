# Application Launcher - Design Wiki

## Overview

Building a **full Raycast-style unified launcher** that merges two existing systems into a single hotkey experience for searching apps, windows, actions, and Chrome profiles together.

## Current State Analysis

### dalauncher (`~/repos/dalauncher`)

| Aspect | Details |
|--------|---------|
| **Type** | Terminal-based TUI |
| **Framework** | Bubbletea (Go) |
| **Discovery** | Apps (`/Applications`, `/System/Applications`), Chrome profiles, custom actions |
| **Window Management** | Uses theGrid CLI (`center`, `minimize`, `sticky`, `move-to-space`) |
| **Activation** | Runs in Ghostty terminal window with toggle support via IPC |

### theGrid Window Picker (`grid-picker`)

| Aspect | Details |
|--------|---------|
| **Type** | Native macOS overlay |
| **Framework** | Swift binary using SkyLight APIs |
| **Command** | `thegrid pick window` |
| **Features** | Fuzzy matching, keyboard navigation, history-based sorting |
| **UX** | Raycast/Spotlight-style native overlay |

---

## Design Decisions

### 1. Goal: Full Unified Launcher

- Single hotkey activates the picker
- Searches across ALL sources: Applications, Windows, Custom Actions, Chrome Profiles
- Native macOS overlay (not terminal TUI)
- Unified fuzzy search across all item types

### 2. Architecture: Merge into theGrid

**Chosen:** Merge dalauncher code into theGrid

- Move Go source discovery code (apps, Chrome, actions) into `grid-cli`
- Use existing `grid-picker` for UI
- Single codebase, unified tooling

**Rejected alternatives:**
- Keep dalauncher separate with RPC connection
- Standalone picker with plugin sources

### 3. Invocation: Single Command with Filters

**Chosen:** `thegrid pick` shows all sources by default

```bash
# Show everything
thegrid pick

# Filter to specific sources
thegrid pick --only apps,windows
thegrid pick --exclude actions
```

**Rationale:** Maximum flexibility for future source types

**Rejected alternatives:**
- Single command with all sources (no filtering)
- Subcommands per source type (`pick window`, `pick app`)
- New `thegrid launch` alias

### 4. Item Selection: Self-Describing Actions

**Chosen:** Items carry their own action

Each item includes an action field describing how to execute it:
```json
{"type": "focus", "windowId": 123}
{"type": "exec", "command": "open -a Slack"}
{"type": "chrome", "profile": "Work"}
```

- Picker returns selected item with action
- CLI executes based on action type
- Keeps picker generic and UI-focused
- Easy to add new action types later

**Rejected alternatives:**
- Source-based routing (logic in CLI, less flexible)
- Picker executes directly (tight coupling)

### 5. Configuration: Merge into theGrid

**Chosen:** Add `picker.sources` section to existing theGrid config

```yaml
# ~/.config/thegrid/config.yaml
picker:
  sources:
    apps:
      enabled: true
      paths:
        - /Applications
        - /System/Applications
    windows:
      enabled: true
    chrome:
      enabled: true
    actions:
      - name: "Lock Screen"
        command: "pmset displaysleepnow"
      - name: "Empty Trash"
        command: "osascript -e 'tell app \"Finder\" to empty trash'"
```

**Rejected alternatives:**
- Separate `~/.config/thegrid/picker.yaml`
- Import dalauncher config directly

### 6. Persistence: Drop Toggle Mode

**Chosen:** No persistence needed

- Native overlay is fast enough - just invoke `thegrid pick` each time
- No background Ghostty window or IPC toggle
- Simpler architecture

**Rejected alternatives:**
- Keep toggle for overlay (show/hide via hotkey)
- Daemon mode (picker as part of grid-server)

### 7. Visual Distinction: Icons

**Chosen:** Use icons to distinguish item types

- App icons for applications
- Window icons (from owning app)
- Chrome icon for profiles
- Custom icons for actions (or generic action icon)

**Requires:** Icon support in grid-picker (Swift)

**Rejected alternatives:**
- Category prefix/badge (`[App]`, `[Window]`, etc.)
- Grouped sections (less unified feel)
- Subtle color coding
- Just rely on context (title/subtitle)

### 8. Icon Implementation: Hybrid Approach

**Chosen:** SF Symbols for categories + actual app icons for applications

| Item Type | Icon Source |
|-----------|-------------|
| Applications | Actual app icons from `.app` bundles |
| Windows | App icon from owning application |
| Chrome Profiles | SF Symbol (or Chrome icon) |
| Custom Actions | SF Symbols (`terminal`, `gear`, etc.) |

**Implementation notes:**
- Extract app icons at discovery time
- Pass as base64 or file path to picker
- Fall back to SF Symbols if icon unavailable

**Rejected alternatives:**
- App icons only from bundles (more complex, no fallback)
- SF Symbols only (simpler but less visual fidelity)

### 9. Sorting: Global Frecency

**Chosen:** Track selection frequency/recency across all sources

- Most used items float to top regardless of source type
- Single unified ranking algorithm
- Frecency = frequency + recency (items used often AND recently rank highest)

**Implementation notes:**
- Store selection history in persistent file (JSON/SQLite)
- Calculate frecency score on each invocation
- Decay older selections over time

**Rejected alternatives:**
- Per-source sorting (windows by history, apps alphabetically)
- Smart grouping (recent section + alphabetical)
- Query-dependent (frecency on empty, fuzzy on typing)

---

## Requirements Summary

| Requirement | Decision |
|-------------|----------|
| Scope | Full unified launcher: windows, apps, Chrome profiles, custom actions |
| Architecture | Merge dalauncher into theGrid codebase |
| Invocation | `thegrid pick` with optional `--only`/`--exclude` filters |
| Item Actions | Self-describing (each item carries its action) |
| Configuration | Merged into `~/.config/thegrid/config.yaml` |
| Persistence | None - invoke fresh each time |
| Icons | Hybrid: SF Symbols + actual app icons |
| Sorting | Global frecency |

---

## Source Types

| Source | Origin | Action |
|--------|--------|--------|
| Windows | theGrid accessibility APIs | Focus/switch to window |
| Applications | `/Applications`, `/System/Applications` | Launch app |
| Chrome Profiles | dalauncher discovery | Open Chrome with profile |
| Custom Actions | dalauncher config | Execute action |

---

## Implementation Approaches

### Approach A: CLI-Driven Discovery (Recommended)

**Idea:** Go CLI discovers all sources (apps, windows, Chrome, actions), assembles unified item list with actions and icon paths, sends to grid-picker via existing JSON stdin protocol.

| Pros | Cons |
|------|------|
| Minimal changes to grid-picker (just add icon rendering) | App icon extraction in Go requires cgo or shelling out to `sips` |
| Source discovery logic stays in Go (easier to extend) | Slight latency for discovery on each invocation |
| Reuses existing picker launch mechanism | |
| Frecency storage in Go alongside existing picker history | |

### Approach B: Server-Side Discovery

**Idea:** Move source discovery into grid-server (Swift). Server maintains app cache, CLI just sends `picker.show` RPC with source filters, server assembles items and shows picker directly.

| Pros | Cons |
|------|------|
| Native Swift access to NSWorkspace for apps, icons | Significant server changes |
| Server can cache app list, faster subsequent launches | Duplicates discovery logic (dalauncher Go → Swift port) |
| Picker and discovery in same process - tighter integration | Config parsing in Swift |

### Approach C: Hybrid with App Cache

**Idea:** Go CLI handles config, actions, Chrome profiles. Separate background process or server endpoint caches app list with icons. CLI fetches cached apps, merges sources, sends to picker.

| Pros | Cons |
|------|------|
| Fast app discovery (cached) | More moving parts (cache invalidation, background process) |
| Go handles config/actions (familiar) | Added complexity for marginal speed gain |
| Icons pre-extracted | |

### Chosen: Approach A - CLI-Driven Discovery

Go CLI discovers all sources, assembles unified item list, sends to grid-picker via JSON stdin protocol.

---

## Implementation Plan

### Phase Summary

| Phase | Description | Files |
|-------|-------------|-------|
| 1 | Icon support in picker | `PickerItem.swift`, `PickerRenderer.swift` |
| 2 | Source discovery in CLI | `internal/sources/*.go` (5 files) |
| 3 | Action execution | `internal/sources/executor.go` |
| 4 | Config integration | `internal/config/config.go` |
| 5 | Global frecency | `internal/state/picker_history.go` |
| 6 | Unified pick command | `cmd/grid/main.go` |
| 7 | Picker protocol update | `PickerItem.swift` |
| 8 | Validation | `*_test.go` files, manual testing |

### Phase 8: Validation & Testing

**Unit Tests:**
- `sources/apps_test.go` - Mock filesystem, verify app discovery
- `sources/chrome_test.go` - Mock Local State JSON, verify profile parsing
- `sources/executor_test.go` - Verify action type routing (mock exec)
- `state/picker_history_test.go` - Frecency scoring, record/load

**Manual Validation Checklist:**
- [ ] `thegrid pick` shows windows, apps, Chrome profiles, actions
- [ ] Icons render correctly (app icons + SF Symbols)
- [ ] Fuzzy search works across all sources
- [ ] Selecting app launches it
- [ ] Selecting window focuses it
- [ ] Selecting Chrome profile opens it
- [ ] Selecting action executes command
- [ ] Frecency sorting works (repeat selections float up)
- [ ] `--only windows` filters correctly
- [ ] `--exclude chrome` filters correctly
- [ ] `thegrid pick window` backwards compat works
- [ ] Config changes (disable source) take effect

---

## Session Log

### Discovery Phase
- Explored both codebases to understand current architecture
- dalauncher: Go/Bubbletea terminal TUI with rich discovery
- grid-picker: Swift native overlay with Spotlight-like UX

### Decision 1: Goal
- **Question:** What's the primary goal for the merged launcher?
- **Options:** (1) Replace TUI with overlay, (2) Add apps to pick, (3) Full unified, (4) Other
- **Chosen:** Option 3 - Full Raycast-style unified launcher

### Decision 2: Architecture
- **Question:** Where should the unified launcher live architecturally?
- **Options:** (1) Merge into theGrid, (2) Keep separate with RPC, (3) Plugin sources
- **Chosen:** Option 1 - Merge dalauncher into theGrid

### Decision 3: Invocation
- **Question:** How should the unified launcher be invoked?
- **Options:** (1) Single command all sources, (2) Subcommands per type, (3) Single with filters, (4) New alias
- **Chosen:** Option 3 - Single command with `--only`/`--exclude` filters

### Decision 4: Item Selection
- **Question:** What should happen when an item is selected?
- **Options:** (1) Items carry action, (2) Source-based routing, (3) Picker executes
- **Chosen:** Option 1 - Items carry self-describing actions

### Decision 5: Configuration
- **Question:** How should sources be configured?
- **Options:** (1) Merge into theGrid config, (2) Separate picker.yaml, (3) Import dalauncher config
- **Chosen:** Option 1 - Merge into existing `~/.config/thegrid/config.yaml`

### Decision 6: Persistence
- **Question:** What about toggle/persistent mode from dalauncher?
- **Options:** (1) Drop it, (2) Keep toggle for overlay, (3) Daemon mode
- **Chosen:** Option 1 - Drop it, native overlay is fast enough

### Decision 7: Visual Distinction
- **Question:** How should items be visually distinguished in unified list?
- **Options:** (1) Category prefix/badge, (2) Icons, (3) Grouped sections, (4) Color coding, (5) Context only
- **Chosen:** Option 2 - Icons (app icons, window icons, Chrome icon, action icons)

### Decision 8: Icon Implementation
- **Question:** How to implement icons?
- **Options:** (1) App icons from bundle, (2) SF Symbols only, (3) Hybrid
- **Chosen:** Option 3 - Hybrid (SF Symbols for categories + actual app icons)

### Decision 9: Sorting
- **Question:** How to sort/rank items across sources?
- **Options:** (1) Global frecency, (2) Per-source sorting, (3) Smart grouping, (4) Query-dependent
- **Chosen:** Option 1 - Global frecency (most used items float to top)

### Decision 10: Implementation Approach
- **Question:** Which implementation approach?
- **Options:** (A) CLI-Driven Discovery, (B) Server-Side Discovery, (C) Hybrid with App Cache
- **Chosen:** Approach A - CLI-Driven Discovery (Recommended)

### Plan Finalization
- 8-phase implementation plan created
- Phase details reviewed and approved
- Plan saved

---

*Whiteboarding session complete.*

---

## Execution Log

**Started:** 2026-01-20

### Branch Setup
- Created feature branch: `feature/unified-launcher`
- Plan loaded from `docs/plans/2026-01-20-unified-launcher.md`
- Todo tracking initialized

### Issue Identified: Skill Not Enforcing Gates

**Problem:** Claude skipped PRE-GATE and went directly to implementation without:
- Writing pseudocode (`cc-pseudocode-programming`)
- Design review (`aposd-designing-deep-modules`)
- Dispatching reviewer agent after each phase

**Root cause:** The `/building` skill says "INVOKE" but doesn't:
1. Use explicit `Skill()` tool syntax
2. Dispatch subagents for implementation (does it directly)
3. Block on PRE-GATE strongly enough

**Skill fixes applied:**

1. **PRE-GATE now blocking:**
   - Added `## STOP. YOU CANNOT WRITE CODE UNTIL THIS GATE PASSES.`
   - Added explicit checklist: pseudocode exists, design reviewed
   - Uses `Skill(code-foundations:cc-pseudocode-programming)` syntax

2. **Implementation via subagent:**
   - Added `## STOP. Confirm PRE-GATE passed before proceeding.`
   - Dispatch Task tool with implementation subagent
   - DO NOT implement directly

3. **POST-GATE now blocking:**
   - Added `## STOP. YOU CANNOT COMMIT UNTIL THIS GATE PASSES.`
   - Uses explicit `Skill()` tool syntax
   - Reviewer agent dispatch with PASS/FAIL requirement
   - Added checklist that must ALL be TRUE

4. **Anti-rationalization table updated:**
   - "I can implement faster than dispatching"
   - "Pseudocode is overkill"
   - "The subagent will figure it out"

**Files modified:**
- `skills/building/SKILL.md`
- `commands/building.md`

**Commits:**
- `4d6b1c2` - fix: enforce gates and subagent dispatch in building skill
- `d7ff4d4` - chore: bump version to 2.7.1
- `976ab75` - docs: add publishing and marketplace instructions to CLAUDE.md

**Published:**
- code-foundations repo: `origin/main`
- rtd-claude-inn marketplace: `f7424fa` - bumped to 2.7.1
- CLAUDE.md updated with marketplace publishing instructions

---

## Plan Location

**Formal implementation plan saved to:**
`~/repos/theGrid/docs/plans/2026-01-20-unified-launcher.md` (303 lines)

**To execute:**
```bash
cd ~/repos/theGrid
/code-foundations:building docs/plans/2026-01-20-unified-launcher.md
```

> **TODO:** When ready to implement, invoke the full skill path `/code-foundations:building` to ensure the code-foundations plugin's building workflow is used (checklist tracking, quality gates, per-phase commits).

---

## Session Stats

| Metric | Value |
|--------|-------|
| Context used | 65k/200k tokens (32%) |
| Message tokens | 37.3k (bulk of usage) |
| Thinking time | ~1m 6s total |
| Decisions made | 10 |
| Implementation phases | 8 |
| Plan output | 303 lines |

Efficient whiteboarding session - comprehensive 8-phase plan with full design rationale in ~1/3 of context window.

---

## Implementation Reference

*From the formal plan at `theGrid/docs/plans/2026-01-20-unified-launcher.md`*

### PickerItem Structure (Go)

```go
type PickerItem struct {
    ID         string            `json:"id"`
    Title      string            `json:"title"`
    Subtitle   string            `json:"subtitle,omitempty"`
    Searchable []string          `json:"searchable"`
    IconPath   string            `json:"iconPath,omitempty"`
    IconSymbol string            `json:"iconSymbol,omitempty"`
    Action     Action            `json:"action"`
    Metadata   map[string]string `json:"metadata,omitempty"`
}

type Action struct {
    Type       string `json:"type"`  // focus-window, open-app, open-chrome-profile, exec
    WindowID   int    `json:"windowId,omitempty"`
    Command    string `json:"command,omitempty"`
    AppPath    string `json:"appPath,omitempty"`
    ProfileDir string `json:"profileDir,omitempty"`
}
```

### Item ID Conventions

| Source | ID Format |
|--------|-----------|
| Windows | `window:{stableID}` |
| Apps | `app:{bundleID}` |
| Chrome | `chrome:{profileDir}` |
| Actions | `action:{name-slug}` |

### Frecency Algorithm

```go
func (e *HistoryEntry) FrecencyScore() float64 {
    hoursSinceUse := time.Since(e.LastUsed).Hours()
    recencyWeight := 1.0 / (1.0 + hoursSinceUse/24.0)
    return float64(e.SelectCount) * recencyWeight
}
```

### Future Extensibility

| Future Source | Discovery | Action Type |
|---------------|-----------|-------------|
| tmux | `tmux list-sessions -F "#{session_name}"` | `tmux-attach` |
| zoxide | `zoxide query -l` | `open-dir` |

*Each new source is just a Go function returning `[]PickerItem`*

### Edge Cases

- **Apps without icons:** Use SF Symbol `app` as fallback
- **Chrome not installed:** Skip source gracefully
- **Empty sources:** Still show picker (might have other sources)
- **Icon extraction:** Parse `Info.plist` for `CFBundleIconFile`, resolve to `Contents/Resources/{icon}.icns`
