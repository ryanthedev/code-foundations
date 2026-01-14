# Documentation Quality Checklists

## Pre-Commit Documentation Check

Before committing, verify:

- [ ] Changed code has updated comments
- [ ] New functions have doc comments
- [ ] README still accurate (if behavior changed)
- [ ] Changelog updated (if user-facing change)

## PR Documentation Review

### README Review
- [ ] Title/description matches project
- [ ] Installation instructions work
- [ ] Usage examples are current
- [ ] Configuration options listed
- [ ] Dependencies up to date

### Comment Review
- [ ] New code has appropriate comments
- [ ] Modified code has updated comments
- [ ] No stale comments in changed files
- [ ] Complex logic explained
- [ ] Public APIs documented

### Changelog Review
- [ ] Version bump if needed
- [ ] Breaking changes highlighted
- [ ] New features described
- [ ] Bug fixes listed
- [ ] Migration steps for breaking changes

## Documentation Debt Indicators

| Indicator | Debt Level |
|-----------|------------|
| README last updated > 6 months ago | High |
| TODO comments > 1 year old | High |
| No changelog entries for recent releases | Medium |
| Public APIs without doc comments | Medium |
| Comments that say "temporary" | Low |
