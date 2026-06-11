# Checklists: code-clarity-and-docs

Sources: A Philosophy of Software Design (Ousterhout), Chapters 12-15, 18; Code Complete (McConnell), Chapter 32

---

## New Code Documentation

- [ ] CF-1: Every new class in the diff has an interface comment describing the abstraction it provides
- [ ] CF-2: Every new public method in the diff has an interface comment (what it does, not how)
- [ ] CF-4: Every new instance variable in the diff has a comment (units, bounds, null meaning, ownership, invariants)
- [ ] CF-5: Every new method added during implementation has a comment
- [ ] CF-6: Every new non-obvious variable has a comment at declaration

---

## What Counts as New Code

- [ ] NC-1: "Writing from scratch?" -> Comments-first applies
- [ ] NC-2: "Copy-paste-modify?" -> Comments-first applies (new context)
- [ ] NC-3: "Extending existing function (>5 lines)?" -> Comments-first applies
- [ ] NC-4: "Refactoring that changes interfaces?" -> Comments-first applies
- [ ] NC-5: "Converting prototype to production?" -> Comments-first applies
- [ ] NC-6: "Test methods?" -> Comments-first applies
- [ ] NC-7: "Lambda functions with non-trivial logic (>1 expression)?" -> Comments-first applies

---

## Comment Quality

- [ ] CQ-1: "Does comment describe the abstraction (not just 'does the thing')?"
- [ ] CQ-2: "Does comment include non-obvious details?"
- [ ] CQ-3: "Does comment use different words than code (not just repeat function name)?"
- [ ] CQ-4: "For variables: does comment include precision (units, bounds, null, ownership)?"
- [ ] CQ-5: "Does comment explain WHY, not WHAT?"
- [ ] CQ-6: "Is complex logic explained with rationale?" (Good: "Batch for memory", Bad: "Loop through items")

---

## Variable Comments

- [ ] VC-1: "What are the units? (seconds? milliseconds? bytes?)"
- [ ] VC-2: "Are boundaries inclusive or exclusive?"
- [ ] VC-3: "What does null mean, if permitted?"
- [ ] VC-4: "Who owns the resource (responsible for freeing/closing)?"
- [ ] VC-5: "What invariants always hold?"

---

## Naming - Precision

- [ ] NP-1: "Can someone seeing this name in isolation guess what it refers to?"
- [ ] NP-2: "Could this name refer to multiple things?" -> Too vague
- [ ] NP-3: "Does this name imply narrower usage than actual?" -> Too specific
- [ ] NP-4: "Does name match actual scope exactly?"

---

## Naming - Consistency

- [ ] NK-1: "Is this name used everywhere for this purpose?"
- [ ] NK-2: "Is this name used ONLY for this purpose?"
- [ ] NK-3: "Do all variables with this name behave identically?"

---

## Common Naming Mistakes

- [ ] NM-1: "Vague status words?" (e.g., `blinkStatus` -> `cursorVisible`)
- [ ] NM-2: "Too generic?" (e.g., `getCount()` -> `numActiveIndexlets`)
- [ ] NM-3: "Too specific for actual usage?" (e.g., `selection` -> `range` if method works on any range)
- [ ] NM-4: "Similar names for different things?" (e.g., `socket` vs `sock`)
- [ ] NM-5: "Type in name?" (e.g., `strName` -> `name`)
- [ ] NM-6: "Repeating class in variable?" (e.g., `File.fileBlock` -> `File.block`)

---

## Interface vs Implementation Comments

- [ ] IC-1: "Does interface comment describe externally visible behavior (not internals)?"
- [ ] IC-2: "Does interface comment define the abstraction (not how it works)?"
- [ ] IC-3: "Does interface comment tell what user needs to use it (not maintainer details)?"
- [ ] IC-4: "Does interface comment NEVER include implementation details?"

---

## Pre-Commit Documentation Check

- [ ] PC-1: All changed code has current comments (no stale comment contradicts the new behavior)
- [ ] PC-2: Every new public function in the diff has a doc comment
- [ ] PC-3: README accurately describes current behavior (if behavior changed, README updated)
- [ ] PC-4: Changelog has an entry for any user-facing change

---

## README Review

- [ ] RR-1: "Does title/description match current project scope?"
- [ ] RR-2: "Do installation instructions work as written?"
- [ ] RR-3: "Are usage examples current and runnable?"
- [ ] RR-4: "Are all configuration options listed?"
- [ ] RR-5: "Are dependencies up to date with package manifests?"

---

## Changelog Review

- [ ] CL-1: Version number bumped if release warranted
- [ ] CL-2: Breaking changes highlighted with examples
- [ ] CL-3: New features described with usage examples
- [ ] CL-4: Bug fixes listed with issue references
- [ ] CL-5: Migration steps included for any breaking changes
- [ ] CL-6: Changelog entry is under the correct version header

---

## AI Documentation Review

Check whichever files exist: `CLAUDE.md`, `.cursorrules`, `.github/copilot-instructions.md`, `AGENTS.md`, `.windsurfrules`, `.aider.conf.yml`, `.continue/config.json`, `.clinerules`, `.roomodes`, `CONVENTIONS.md`

- [ ] AI-1: "Does architecture description match actual code structure?"
- [ ] AI-2: "Is file structure section accurate?"
- [ ] AI-3: "Are agent/skill lists complete and current?"
- [ ] AI-4: "Are tool permissions correct for actual capabilities?"
- [ ] AI-5: "Do workflow instructions reflect current processes?"
- [ ] AI-6: "Are all AI config files consistent with each other?"
- [ ] AI-7: "Is version synchronized with plugin.json/package.json?"

---

## Documentation Debt Detection

- [ ] DD-1: "Was README last updated > 6 months ago?" -> High debt
- [ ] DD-2: "Are there TODO comments > 1 year old?" -> High debt
- [ ] DD-3: "Does CLAUDE.md reference deleted files?" -> High debt
- [ ] DD-4: "Are there missing changelog entries for recent releases?" -> Medium debt
- [ ] DD-5: "Do public APIs lack doc comments?" -> Medium debt
- [ ] DD-6: "Does CLAUDE.md version != plugin.json version?" -> Medium debt
- [ ] DD-7: "Are there comments that say 'temporary'?" -> Low debt

---

## Documentation Coverage

- [ ] DC-1: "Can a new developer understand the project from README alone?"
- [ ] DC-2: "Can public APIs be used without reading implementation?"
- [ ] DC-3: "Are error messages documented with resolution steps?"
- [ ] DC-4: "Is unusual/surprising behavior documented?"

---

## Red Flags

- [ ] RF-1: "Comment repeats code?" -> Rewrite with different words
- [ ] RF-2: "Hard to describe?" -> Design problem, fix the design
- [ ] RF-3: "Hard to pick name?" -> Design smell
- [ ] RF-4: "Vague name (status, flag, data)?" -> Conveys little information
- [ ] RF-5: "Interface describes implementation?" -> Shallow abstraction
- [ ] RF-6: "Implementation contaminates interface?" -> Violates separation
- [ ] RF-7: "Comments contradict code?" -> Stale documentation
- [ ] RF-8: "Public API without documentation?" -> Missing docs
- [ ] RF-9: "README versions differ from manifests?" -> Synchronization failure
- [ ] RF-10: "Breaking changes buried in changelog?" -> Not highlighted
- [ ] RF-11: "AI docs reference deleted files?" -> Architectural drift
- [ ] RF-12: "Version mismatch across files?" -> Docs out of sync
- [ ] RF-13: "Migration steps missing for breaking changes?" -> Users can't upgrade

---
