---
description: "Lens-based review with 7 parallel agents (one per skill). Full checklist execution with evidence trail."
argument-hint: "[--staged | files...]"
allowed-tools: ["Bash", "Glob", "Grep", "Read", "Task", "Skill", "Write", "TaskCreate", "TaskUpdate", "TaskList", "AskUserQuestion"]
---

# Review Changes (Lens-Based)

**This command uses lens-based review by default.**

Lens review dispatches **one agent per skill**, each executing their full checklist with evidence. This provides complete traceability of what was checked.

## Redirect to Lens Orchestrator

**Immediately invoke the lens orchestrator:**

```
Read(commands/lens-review.md)
```

Then execute lens-review with:
- **Review type:** `review-changes`
- **Arguments:** Pass through all arguments (--staged, files, etc.)

```
Execute lens-review orchestrator for: review-changes $ARGUMENTS
```

---

## What This Does

| Aspect | Value |
|--------|-------|
| Categories | 3 (defensive, quality, correctness) |
| Skills | 7 |
| Agents | 7 parallel |
| Checklist Items | ~360 |
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

---

## Usage

```bash
/review-changes           # Unstaged changes
/review-changes --staged  # Staged only
/review-changes file.ts   # Specific files
```

---

## Adding/Removing Skills

Edit `agents/lens/config.yaml`:

```yaml
review-changes:
  categories:
    quality:
      skills:
        - existing-skill
        - new-skill  # ← add here
```

No code changes needed.
