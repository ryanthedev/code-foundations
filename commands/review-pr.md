---
description: "Comprehensive multi-dimensional PR review. Dispatches parallel agents for security, performance, maintainability, error handling, clarity, correctness, tests, types, and comments. Use before merging."
argument-hint: "[aspects...] [--parallel]"
allowed-tools: ["Bash", "Glob", "Grep", "Read", "Task"]
---

# Review PR (Level 3 - Full Review)

Comprehensive multi-dimensional review using parallel specialized agents. Each agent uses code-foundations skills as evaluation lenses.

**Arguments:** "$ARGUMENTS"
- Aspects: `security`, `performance`, `maintainability`, `errors`, `clarity`, `correctness`, `tests`, `types`, `comments`, `all`
- Flags: `--parallel` (launch all agents simultaneously)

---

## Execution Checklist

### Phase 1: Determine Scope

- [ ] **1.1** Identify PR scope:
  ```bash
  # Check if PR exists
  gh pr view --json number,title,baseRefName,headRefName 2>/dev/null

  # Get changed files
  git diff --name-only $(git merge-base HEAD main)..HEAD

  # Get full diff for review
  git diff $(git merge-base HEAD main)..HEAD
  ```

- [ ] **1.2** Parse arguments for requested aspects (default: `all`)

- [ ] **1.3** Identify file types to determine applicable reviews:
  - Test files present? → Include test-reviewer
  - Type definitions present? → Include type-reviewer
  - Significant comments? → Include comment-reviewer

---

### Phase 2: Launch Review Agents

**Use oberagent skill for agent dispatch.**

**IMPORTANT:** When launching agents, invoke oberagent first to ensure proper orchestration.

#### Core Agents (Always Run)

- [ ] **2.1** Launch **security-reviewer**:
  ```
  Focus: Input validation, injection, auth, secrets, OWASP top 10
  Skills: cc-defensive-programming
  Priority: CRITICAL findings block merge
  ```

- [ ] **2.2** Launch **performance-reviewer**:
  ```
  Focus: Big-O complexity, algorithms, scaling, resource usage
  Skills: cc-performance-tuning, aposd-optimizing-critical-paths
  Priority: Hot path issues are CRITICAL
  ```

- [ ] **2.3** Launch **maintainability-reviewer**:
  ```
  Focus: Complexity symptoms, module depth, cohesion, coupling
  Skills: aposd-reviewing-module-design, cc-routine-and-class-design
  Priority: Design issues are IMPORTANT
  ```

- [ ] **2.4** Launch **error-handling-reviewer**:
  ```
  Focus: Silent failures, catch blocks, error propagation
  Skills: cc-defensive-programming, aposd-simplifying-complexity
  Priority: Silent failures are CRITICAL
  ```

- [ ] **2.5** Launch **clarity-reviewer**:
  ```
  Focus: Naming precision, comment quality, formatting, readability
  Skills: aposd-improving-code-clarity, cc-code-layout-and-style
  Priority: Most are SUGGESTION unless severely unclear
  ```

- [ ] **2.6** Launch **correctness-reviewer**:
  ```
  Focus: Requirements, concurrency, boundaries, edge cases, resources
  Skills: aposd-verifying-correctness
  Priority: Correctness issues are CRITICAL
  ```

#### Conditional Agents (If Applicable)

- [ ] **2.7** If test files changed, launch **test-reviewer**:
  ```
  Focus: Test coverage, test quality, missing edge cases
  Priority: Coverage gaps are IMPORTANT
  ```

- [ ] **2.8** If types added/modified, launch **type-reviewer**:
  ```
  Focus: Type design, encapsulation, invariants
  Priority: Type design issues are IMPORTANT
  ```

- [ ] **2.9** Launch **comment-reviewer**:
  ```
  Focus: Comment accuracy, staleness, completeness
  Priority: Stale comments are IMPORTANT
  ```

---

### Phase 3: Monitor Agent Progress

- [ ] **3.1** Track agent completion status

- [ ] **3.2** If `--parallel` not specified, show progress:
  ```
  [1/6] security-reviewer: Running...
  [2/6] performance-reviewer: Running...
  ...
  ```

---

### Phase 4: Aggregate Results

- [ ] **4.1** Collect all agent reports

- [ ] **4.2** Deduplicate overlapping findings

- [ ] **4.3** Sort by severity (CRITICAL → IMPORTANT → SUGGESTION)

- [ ] **4.4** Produce unified report:
  ```markdown
  # PR Review Report

  ## Summary
  - **PR:** [title]
  - **Branch:** [head] → [base]
  - **Files Changed:** [count]
  - **Agents Run:** [list]

  ## Overall Verdict: [APPROVE / REQUEST CHANGES / BLOCKED]

  ---

  ## Critical Issues ([count]) - Must Fix Before Merge

  ### Security
  - [file:line] - [issue]

  ### Correctness
  - [file:line] - [issue]

  ### Error Handling
  - [file:line] - [issue]

  ---

  ## Important Issues ([count]) - Should Fix

  ### Performance
  - [file:line] - [issue]

  ### Maintainability
  - [file:line] - [issue]

  ### Tests
  - [file:line] - [issue]

  ---

  ## Suggestions ([count]) - Consider

  ### Clarity
  - [file:line] - [suggestion]

  ### Comments
  - [file:line] - [suggestion]

  ---

  ## Positive Patterns
  - [what's good about this PR]

  ---

  ## Action Plan

  1. **Critical (blocking):**
     - [ ] [specific fix]

  2. **Important:**
     - [ ] [specific fix]

  3. **After fixes:**
     - [ ] Re-run: `/review-pr security errors correctness`
  ```

---

### Phase 5: Verdict Logic

- [ ] **5.1** Determine verdict:

  | Condition | Verdict |
  |-----------|---------|
  | Any CRITICAL issues | **BLOCKED** |
  | IMPORTANT issues only | **REQUEST CHANGES** |
  | SUGGESTIONS only | **APPROVE** (with comments) |
  | No issues | **APPROVE** |

- [ ] **5.2** If BLOCKED, highlight what must be fixed

- [ ] **5.3** If REQUEST CHANGES, explain impact of not fixing

---

## Review Dimensions Reference

| Dimension | Agent | Skills Used | Critical If... |
|-----------|-------|-------------|----------------|
| Security | security-reviewer | cc-defensive-programming | Any vulnerability |
| Performance | performance-reviewer | cc-performance-tuning, aposd-optimizing-critical-paths | O(n²)+ in hot path |
| Maintainability | maintainability-reviewer | aposd-reviewing-module-design, cc-routine-and-class-design | Severe complexity |
| Error Handling | error-handling-reviewer | cc-defensive-programming, aposd-simplifying-complexity | Silent failure |
| Clarity | clarity-reviewer | aposd-improving-code-clarity, cc-code-layout-and-style | Rarely critical |
| Correctness | correctness-reviewer | aposd-verifying-correctness | Any correctness bug |
| Tests | test-reviewer | cc-quality-practices | Missing critical coverage |
| Types | type-reviewer | cc-routine-and-class-design | Broken invariants |
| Comments | comment-reviewer | aposd-improving-code-clarity | Dangerous staleness |

---

## Usage Examples

```bash
# Full review (all dimensions)
/review-pr

# Full review, all agents in parallel
/review-pr --parallel

# Specific dimensions only
/review-pr security errors
/review-pr performance maintainability
/review-pr tests comments

# After fixing critical issues, re-check specific areas
/review-pr security correctness errors
```

---

## Integration with Workflow

**Before creating PR:**
```
1. /check-commit          # Quick sanity check
2. /review-changes        # Medium review of all changes
3. /review-pr            # Full comprehensive review
4. Fix any issues found
5. Create PR
```

**After PR feedback:**
```
1. Make requested changes
2. /review-changes --staged  # Review just the fixes
3. /review-pr [specific-aspects]  # Re-check problem areas
4. Push updates
```
