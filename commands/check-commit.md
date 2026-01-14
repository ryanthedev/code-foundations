---
description: "Quick review of a single commit. Checks Big-O, complexity, style, and obvious bugs. Use before pushing or for quick sanity check."
argument-hint: "[commit-hash]"
allowed-tools: ["Bash", "Glob", "Grep", "Read"]
---

# Check Commit (Level 1 - Quick Review)

Quick sanity check of a single commit. No subagents—run through checklist directly.

**Commit:** "$ARGUMENTS" (default: HEAD)

---

## Execution Checklist

### Phase 1: Get Commit Diff

- [ ] **1.1** Determine commit to review:
  ```bash
  # If argument provided, use it; otherwise HEAD
  COMMIT="${ARGUMENTS:-HEAD}"
  git show --stat $COMMIT
  git diff $COMMIT^ $COMMIT
  ```

- [ ] **1.2** List changed files and identify languages

---

### Phase 2: Quick Big-O Scan

**Skill lens:** cc-performance-tuning, aposd-optimizing-critical-paths

- [ ] **2.1** Scan for nested loops:
  - `for` inside `for` → potential O(n²)
  - `while` inside `while` → potential O(n²)
  - `.forEach` inside `.map` → potential O(n²)

- [ ] **2.2** Scan for repeated operations in loops:
  - Database queries inside loops
  - File I/O inside loops
  - API calls inside loops

- [ ] **2.3** Flag if found:
  ```
  BIG-O WARNING: [file:line] - [pattern found]
  Potential complexity: O(n²) or worse
  Consider: [brief suggestion]
  ```

---

### Phase 3: Quick Complexity Scan

**Skill lens:** cc-control-flow-quality

- [ ] **3.1** Check nesting depth:
  - Flag if > 3 levels deep
  - Look for arrow-shaped code

- [ ] **3.2** Check function length:
  - Flag functions > 50 lines (quick heuristic)

- [ ] **3.3** Check cyclomatic complexity signals:
  - Many `if/else` chains
  - Large `switch/case` statements
  - Multiple return points

- [ ] **3.4** Flag if found:
  ```
  COMPLEXITY WARNING: [file:line] - [issue]
  ```

---

### Phase 4: Quick Style Scan

**Skill lens:** cc-code-layout-and-style

- [ ] **4.1** Check obvious style issues:
  - Inconsistent indentation
  - Mixed tabs/spaces
  - Trailing whitespace
  - Missing semicolons (if applicable)

- [ ] **4.2** Check naming:
  - Single-letter variables (except `i`, `j`, `k` in loops)
  - Unclear abbreviations
  - Inconsistent casing

- [ ] **4.3** Flag if found:
  ```
  STYLE WARNING: [file:line] - [issue]
  ```

---

### Phase 5: Quick Bug Scan

**Skill lens:** cc-defensive-programming, aposd-verifying-correctness

- [ ] **5.1** Check for obvious bugs:
  - Null/undefined access without check
  - Off-by-one errors (< vs <=)
  - Empty catch blocks
  - Unreachable code
  - Unused variables

- [ ] **5.2** Check boundary conditions:
  - Array access without bounds check
  - Division without zero check
  - String operations on potentially null

- [ ] **5.3** Flag if found:
  ```
  BUG WARNING: [file:line] - [issue]
  Risk: [what could go wrong]
  ```

---

### Phase 6: Output Summary

- [ ] **6.1** Produce summary:
  ```markdown
  # Commit Check: [commit-hash]

  ## Result: [PASS / WARN / FAIL]

  ### Issues Found: [count]

  #### Big-O Warnings
  - [list or "None"]

  #### Complexity Warnings
  - [list or "None"]

  #### Style Warnings
  - [list or "None"]

  #### Bug Warnings
  - [list or "None"]

  ### Verdict
  [PASS: Ready to push / WARN: Review flagged items / FAIL: Fix before pushing]
  ```

---

## Quick Reference

| Check | What to Look For | Severity |
|-------|------------------|----------|
| Big-O | Nested loops, loops with I/O | WARN if O(n²)+ |
| Complexity | Deep nesting, long functions | WARN if >3 deep |
| Style | Formatting, naming | WARN |
| Bugs | Null access, off-by-one, empty catch | FAIL if found |

---

## Pass/Warn/Fail Criteria

| Result | Criteria |
|--------|----------|
| **PASS** | No warnings or bugs |
| **WARN** | Style or complexity warnings only |
| **FAIL** | Any bug warnings OR Big-O issues in hot paths |
