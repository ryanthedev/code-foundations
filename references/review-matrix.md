# Review Reference

Single entry point: `/review` with depth/focus selection or presets.

---

## Presets

| Preset | Depth | Skills | Checks | Best For |
|--------|-------|--------|--------|----------|
| `--quick` | Quick | 3 agents | 99 | Pre-commit sanity check |
| `--security` | Standard | 4 | ~150 | Security-sensitive changes |
| `--design` | Standard | 5 | ~250 | Refactoring, new modules |
| `--full` | Deep | 9 | ~550 | Major features, PR review |
| `--profile <name>` | Custom | varies | varies | Saved configuration |

**Interactive:** `/review` (no flags) prompts for depth and focus.

---

## Depth Levels

| Depth | Categories | Skills | Execution |
|-------|------------|--------|-----------|
| **Quick** | — | — | 3 subagents: extraction (haiku) → checker → reviewer |
| **Standard** | defensive, quality, correctness | 7 | Parallel subagents |
| **Deep** | All 5 | 9 | Parallel subagents |
| **Custom** | User picks | User picks | Parallel subagents |

---

## Focus Areas

| Focus | Priority Categories | Skills |
|-------|---------------------|--------|
| **Security & Errors** | defensive | cc-defensive-programming, aposd-simplifying-complexity |
| **Design Quality** | quality | aposd-reviewing-module-design, cc-code-layout-and-style, cc-control-flow-quality |
| **Correctness** | correctness | aposd-verifying-correctness, cc-quality-practices |
| **All Areas** | balanced | All skills for selected depth |

---

## Dimension Coverage

| Dimension | Quick | Standard | Deep |
|-----------|:-----:|:--------:|:----:|
| **Obvious Bugs** | ✓ | ✓ | ✓ |
| **Style / Layout** | ✓ | ✓ | ✓ |
| **Error Handling** | ✓ | ✓ | ✓ Full |
| **Design Depth** | — | ✓ | ✓ Full |
| **Correctness** | — | ✓ | ✓ Full |
| **Security** | — | — | ✓ Full |
| **Performance** | — | — | ✓ Full |
| **Documentation** | — | — | ✓ Full |

---

## Custom Profiles

Create reusable configurations:

```bash
/review-profile --setup my-profile
```

Profiles saved to `.code-foundations/profiles/<name>.yaml`.

Use with:
```bash
/review --profile my-profile
```

---

## Severity Levels

| Severity | Meaning | Action |
|----------|---------|--------|
| **CRITICAL** | Blocks merge, security/correctness issue | Must fix |
| **IMPORTANT** | Significant quality issue | Should fix |
| **SUGGESTION** | Improvement opportunity | Consider |
