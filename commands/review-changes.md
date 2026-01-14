---
description: "Medium-depth review of staged or unstaged changes. Checks design, quality, error handling, clarity, and correctness. Use before committing or creating PR."
argument-hint: "[--staged | files...]"
allowed-tools: ["Bash", "Glob", "Grep", "Read", "Task"]
---

# Review Changes (Level 2 - Medium Review)

Medium-depth review of current changes. Dispatches 2-3 focused agents for parallel analysis.

**Scope:** "$ARGUMENTS" (default: unstaged changes via `git diff`)

---

## Execution Checklist

### Phase 1: Determine Scope

- [ ] **1.1** Identify what to review:
  ```bash
  # Check arguments
  if [[ "$ARGUMENTS" == "--staged" ]]; then
    git diff --cached --name-only
  elif [[ -n "$ARGUMENTS" ]]; then
    # Specific files provided
    echo "$ARGUMENTS"
  else
    # Default: unstaged changes
    git diff --name-only
  fi
  ```

- [ ] **1.2** Get the actual diff content for review

- [ ] **1.3** Identify file types and languages

---

### Phase 2: Launch Review Agents

**Use oberagent skill if available for agent dispatch.**

Launch these agents in parallel:

- [ ] **2.1** Launch **maintainability-reviewer** agent:
  ```
  Focus: Design depth, complexity symptoms, cohesion/coupling
  Skills: aposd-reviewing-module-design, cc-routine-and-class-design
  ```

- [ ] **2.2** Launch **error-handling-reviewer** agent:
  ```
  Focus: Silent failures, catch blocks, error propagation
  Skills: cc-defensive-programming, aposd-simplifying-complexity
  ```

- [ ] **2.3** Launch **correctness-reviewer** agent:
  ```
  Focus: Requirements coverage, boundaries, edge cases
  Skills: aposd-verifying-correctness
  ```

---

### Phase 3: Quick Local Checks (While Agents Run)

Run these checks directly (no agent needed):

- [ ] **3.1** Clarity quick check:
  - Variable names precise?
  - Comments present for non-obvious code?
  - Formatting consistent?

- [ ] **3.2** Style quick check:
  - Follows project conventions?
  - No obvious violations?

---

### Phase 4: Aggregate Results

- [ ] **4.1** Collect agent results

- [ ] **4.2** Merge into unified report:
  ```markdown
  # Review Changes Report

  ## Scope
  [files reviewed]

  ## Critical Issues (Must Fix)
  - [agent]: [issue] at [file:line]

  ## Important Issues (Should Fix)
  - [agent]: [issue] at [file:line]

  ## Suggestions
  - [agent]: [suggestion] at [file:line]

  ## Positive Patterns
  - [what's good]

  ## Verdict
  [READY / NEEDS WORK / BLOCKED]
  ```

---

### Phase 5: Provide Action Plan

- [ ] **5.1** If issues found:
  ```markdown
  ## Recommended Actions

  1. **Fix Critical Issues First:**
     - [specific action items]

  2. **Address Important Issues:**
     - [specific action items]

  3. **Consider Suggestions:**
     - [optional improvements]

  4. **Re-run Review:**
     After fixes, run `/review-changes` again to verify.
  ```

- [ ] **5.2** If clean:
  ```markdown
  ## Ready to Commit

  Changes look good. Proceed with:
  1. Stage changes: `git add [files]`
  2. Commit with descriptive message
  3. Consider `/review-pr` before creating PR
  ```

---

## Dimension Checklist (What Agents Check)

### Maintainability (maintainability-reviewer)

| Check | Skill | Severity |
|-------|-------|----------|
| Shallow modules | aposd-reviewing-module-design | IMPORTANT |
| Information leakage | aposd-reviewing-module-design | IMPORTANT |
| Pass-through methods | aposd-reviewing-module-design | SUGGESTION |
| Cohesion issues | cc-routine-and-class-design | IMPORTANT |
| High coupling | cc-routine-and-class-design | IMPORTANT |
| Deep inheritance (>3) | cc-routine-and-class-design | IMPORTANT |
| Too many parameters (>7) | cc-routine-and-class-design | CRITICAL |

### Error Handling (error-handling-reviewer)

| Check | Skill | Severity |
|-------|-------|----------|
| Empty catch blocks | cc-defensive-programming | CRITICAL |
| Silent failures | aposd-simplifying-complexity | CRITICAL |
| Broad exception catching | cc-defensive-programming | IMPORTANT |
| Missing error context | cc-defensive-programming | IMPORTANT |
| Swallowed errors | aposd-simplifying-complexity | CRITICAL |

### Correctness (correctness-reviewer)

| Check | Skill | Severity |
|-------|-------|----------|
| Boundary conditions | aposd-verifying-correctness | CRITICAL |
| Null/undefined handling | aposd-verifying-correctness | CRITICAL |
| Concurrency issues | aposd-verifying-correctness | CRITICAL |
| Resource leaks | aposd-verifying-correctness | IMPORTANT |
| Edge cases unhandled | aposd-verifying-correctness | IMPORTANT |

---

## Verdict Criteria

| Verdict | Criteria |
|---------|----------|
| **READY** | No critical or important issues |
| **NEEDS WORK** | Important issues found, no critical |
| **BLOCKED** | Critical issues found |

---

## Usage Examples

```bash
# Review unstaged changes (default)
/review-changes

# Review staged changes only
/review-changes --staged

# Review specific files
/review-changes src/api/handler.ts src/utils/validate.ts
```
