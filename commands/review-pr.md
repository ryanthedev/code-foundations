---
description: "Lens-based PR review with 9 parallel agents (one per skill). Full checklist execution with evidence trail."
argument-hint: "[PR number or branch]"
allowed-tools: ["Bash", "Glob", "Grep", "Read", "Task", "Skill", "Write", "TaskCreate", "TaskUpdate", "TaskList", "AskUserQuestion"]
---

# Review PR (Lens-Based)

**This command uses lens-based review by default.**

Lens review dispatches **one agent per skill**, each executing their full checklist with evidence. This provides complete traceability of what was checked.

## Redirect to Lens Orchestrator

**Immediately invoke the lens orchestrator:**

```
Read(commands/lens-review.md)
```

Then execute lens-review with:
- **Review type:** `review-pr`
- **Arguments:** Pass through all arguments (PR number, branch, etc.)

```
Execute lens-review orchestrator for: review-pr $ARGUMENTS
```

---

## What This Does

| Aspect | Value |
|--------|-------|
| Categories | 5 (defensive, quality, correctness, performance, documentation) |
| Skills | 9 |
| Agents | 9 parallel |
| Checklist Items | ~548 |
| Output | `/tmp/lens-review-{RUN_ID}/` |

### Skills by Category

**Defensive (2 skills, 75 items):**
- cc-defensive-programming
- aposd-simplifying-complexity

**Quality (3 skills, 221 items):**
- aposd-reviewing-module-design
- cc-code-layout-and-style
- cc-control-flow-quality

**Correctness (2 skills, 146 items):**
- aposd-verifying-correctness
- cc-quality-practices

**Performance (2 skills, 80 items):**
- cc-performance-tuning
- aposd-optimizing-critical-paths

**Documentation (1 skill, 26 items):**
- cc-documentation-quality

---

## Usage

```bash
/review-pr              # Current branch vs main
/review-pr 123          # PR #123
/review-pr feature/foo  # Branch vs main
```

---

## Adding/Removing Skills

Edit `agents/lens/config.yaml`:

```yaml
review-pr:
  categories:
    performance:
      skills:
        - existing-skill
        - new-skill  # ← add here
```

No code changes needed.
