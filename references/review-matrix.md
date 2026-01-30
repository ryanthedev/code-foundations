# Review Reference

Single entry point: `/code-foundations:review` with depth selection or presets.

---

## Presets

| Preset | Depth | Skills | Checks | Best For |
|--------|-------|--------|--------|----------|
| `--sanity` | Sanity | 3 agents | 99 | Pre-commit sanity check |
| `--pr` | PR | 9 | ~550 | PR review, major features |
| `--profile <name>` | Custom | varies | varies | Saved configuration |

**Interactive:** `/code-foundations:review` (no flags) prompts for depth.

---

## Depth Levels

| Depth | Categories | Skills | Execution |
|-------|------------|--------|-----------|
| **Sanity** | — | — | 3 subagents: extraction (haiku) → checker → reviewer |
| **PR** | All 5 | 9 | Parallel subagents |
| **Custom** | User picks | User picks | Parallel subagents |

---

## Dimension Coverage

| Dimension | Sanity | PR |
|-----------|:------:|:--:|
| **Obvious Bugs** | ✓ | ✓ |
| **Style / Layout** | ✓ | ✓ |
| **Error Handling** | ✓ | ✓ Full |
| **Design Depth** | — | ✓ Full |
| **Correctness** | — | ✓ Full |
| **Security** | — | ✓ Full |
| **Performance** | — | ✓ Full |
| **Documentation** | — | ✓ Full |

---

## Custom Profiles

Create reusable configurations:

```bash
/code-foundations:review-profile --setup my-profile
```

Profiles saved to `.code-foundations/profiles/<name>.yaml`.

Use with:
```bash
/code-foundations:review --profile my-profile
```

---

## Severity Levels

| Severity | Meaning | Action |
|----------|---------|--------|
| **CRITICAL** | Blocks merge, security/correctness issue | Must fix |
| **IMPORTANT** | Significant quality issue | Should fix |
| **SUGGESTION** | Improvement opportunity | Consider |
