# Checklists: cc-documentation-quality

Source: Code Complete (McConnell), Chapter 32

---

## Pre-Commit Documentation Check

Before committing, verify:

- [ ] PC-1: "Did I update comments for changed code?"
- [ ] PC-2: "Do new functions have doc comments?" → Red flag: Public API without documentation
- [ ] PC-3: "Is README still accurate if behavior changed?"
- [ ] PC-4: "Did I update changelog for user-facing changes?"

---

## README Review

- [ ] RR-1: "Does title/description match current project scope?"
- [ ] RR-2: "Do installation instructions work as written?" (Good: Tested commands, Bad: Untested "should work")
- [ ] RR-3: "Are usage examples current and runnable?"
- [ ] RR-4: "Are all configuration options listed?"
- [ ] RR-5: "Are dependencies up to date with package manifests?" → Red flag: README lists different versions than package.json

---

## Comment Review

- [ ] CR-1: "Does new code have appropriate comments?"
- [ ] CR-2: "Did I update comments in modified code?"
- [ ] CR-3: "Did I remove stale comments in changed files?" → Red flag: Comments contradicting code
- [ ] CR-4: "Is complex logic explained with WHY not WHAT?" (Good: "Batch for memory", Bad: "Loop through items")
- [ ] CR-5: "Are public APIs fully documented?" → Red flag: Missing parameter descriptions or return values
- [ ] CR-6: "Do comments explain non-obvious design decisions?"

---

## Changelog Review

- [ ] CL-1: "Did I bump version number if needed?"
- [ ] CL-2: "Are breaking changes highlighted with examples?" → Red flag: Breaking change buried in "fixes"
- [ ] CL-3: "Are new features described with usage examples?"
- [ ] CL-4: "Are bug fixes listed with issue references?"
- [ ] CL-5: "Did I include migration steps for breaking changes?" (Good: Code snippets showing before/after, Bad: "Update your code")
- [ ] CL-6: "Is changelog entry under correct version header?"

---

## AI Documentation Review

Check whichever files exist: `CLAUDE.md`, `.cursorrules`, `.github/copilot-instructions.md`, `AGENTS.md`, `.windsurfrules`, `.aider.conf.yml`, `.continue/config.json`, `.clinerules`, `.roomodes`, `CONVENTIONS.md`

- [ ] AI-1: "Does architecture description match actual code structure?"
- [ ] AI-2: "Is file structure section accurate?" → Red flag: Documents reference deleted/moved files
- [ ] AI-3: "Are agent/skill lists complete and current?"
- [ ] AI-4: "Are tool permissions correct for actual capabilities?"
- [ ] AI-5: "Do workflow instructions reflect current processes?"
- [ ] AI-6: "Are all AI config files consistent with each other?" (Good: Single source of truth, Bad: Conflicting instructions)
- [ ] AI-7: "Is version synchronized with plugin.json/package.json?" → Red flag: Version mismatch between docs and manifest

---

## Documentation Debt Detection

- [ ] DD-1: "Was README last updated > 6 months ago?" → High debt
- [ ] DD-2: "Are there TODO comments > 1 year old?" → High debt (Good: Recent TODOs with dates, Bad: Ancient TODOs)
- [ ] DD-3: "Does CLAUDE.md reference deleted files?" → High debt
- [ ] DD-4: "Are there missing changelog entries for recent releases?" → Medium debt
- [ ] DD-5: "Do public APIs lack doc comments?" → Medium debt
- [ ] DD-6: "Does CLAUDE.md version != plugin.json version?" → Medium debt
- [ ] DD-7: "Are there comments that say 'temporary'?" → Low debt (but track them)

---

## Documentation Coverage Test

- [ ] DC-1: "Can a new developer understand the project from README alone?"
- [ ] DC-2: "Can public APIs be used without reading implementation?"
- [ ] DC-3: "Are error messages documented with resolution steps?"
- [ ] DC-4: "Is unusual/surprising behavior documented?"

---

## Red Flags

- [ ] RF-1: "Comments contradicting code?" → Stale documentation, code changed without updating comments
- [ ] RF-2: "Public API without documentation?" → Missing function/class docs, no parameter descriptions
- [ ] RF-3: "README different versions than manifests?" → Synchronization failure between docs and dependencies
- [ ] RF-4: "Breaking changes buried in changelog?" → User-breaking changes not highlighted or explained
- [ ] RF-5: "AI docs reference deleted files?" → High maintenance debt, architectural drift from documentation
- [ ] RF-6: "Version mismatch across files?" → CLAUDE.md, plugin.json, package.json showing different versions
- [ ] RF-7: "Comments explain WHAT not WHY?" → Low-value comments that duplicate code meaning
- [ ] RF-8: "Migration steps missing for breaking changes?" → Users can't upgrade without reverse-engineering
- [ ] RF-9: "TODO comments > 1 year old?" → Forgotten debt, indicates abandoned work
- [ ] RF-10: "Installation instructions untested?" → Documentation written but never validated

---

Total items: 49
