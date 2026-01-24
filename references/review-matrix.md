# Review Matrix Reference

Three levels of code review, each building on the previous.

---

## Level Overview

| Level | Command | Scope | Time | Agents |
|-------|---------|-------|------|--------|
| **1** | `/review-commit` | Single commit | ~2 min | None (single pass) |
| **2** | `/review-changes` | Staged/unstaged changes | ~5-10 min | 2-3 parallel |
| **3** | `/review-pr` | Full PR (branch vs main) | ~15-30 min | 6+ parallel |

---

## Dimension Coverage Matrix

| Dimension | Check Commit | Review Changes | Review PR |
|-----------|:------------:|:--------------:|:---------:|
| **Big-O / Complexity** | ✓ Quick | ✓ | ✓ Full |
| **Style / Layout** | ✓ Quick | ✓ | ✓ |
| **Obvious Bugs** | ✓ | ✓ | ✓ |
| **Design Depth** | - | ✓ | ✓ Full |
| **Error Handling** | - | ✓ Quick | ✓ Full |
| **Clarity / Naming** | - | ✓ | ✓ Full |
| **Correctness** | - | ✓ | ✓ Full |
| **Security** | - | - | ✓ Full |
| **Performance** | - | - | ✓ Full |
| **Maintainability** | - | - | ✓ Full |
| **Tests** | - | - | ✓ If applicable |
| **Types** | - | - | ✓ If applicable |
| **Comments** | - | - | ✓ Full |

---

## Agent → Skill Mapping

| Agent | Code-Foundations Skills | Focus |
|-------|------------------------|-------|
| **security-reviewer** | cc-defensive-programming | Input validation, injection, auth, secrets |
| **performance-reviewer** | cc-performance-tuning, aposd-optimizing-critical-paths | Big-O, algorithms, scaling |
| **maintainability-reviewer** | aposd-reviewing-module-design, cc-routine-and-class-design | Complexity symptoms, cohesion, coupling |
| **error-handling-reviewer** | cc-defensive-programming, aposd-simplifying-complexity | Silent failures, catch blocks, propagation |
| **clarity-reviewer** | aposd-improving-code-clarity, cc-code-layout-and-style | Naming, comments, formatting |
| **correctness-reviewer** | aposd-verifying-correctness | Requirements, concurrency, boundaries |

---

## Quick Reference: When to Use Each Level

| Situation | Use |
|-----------|-----|
| Quick sanity check before commit | `/review-commit` |
| Review work before staging | `/review-changes` |
| Final check before PR creation | `/review-pr` |
| Responding to PR feedback | `/review-changes` on specific files |
| Comprehensive feature review | `/review-pr` |

---

## Output Severity Levels

All levels use consistent severity classification:

| Severity | Meaning | Action |
|----------|---------|--------|
| **CRITICAL** | Blocks merge, security/correctness issue | Must fix |
| **IMPORTANT** | Significant quality issue | Should fix |
| **SUGGESTION** | Improvement opportunity | Consider |
| **POSITIVE** | Good pattern observed | Acknowledge |
