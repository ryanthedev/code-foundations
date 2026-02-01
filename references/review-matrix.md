# Review Reference

Profile-driven code review: `/code-foundations:review`

---

## Presets

| Preset | Checklists | Checks | Best For |
|--------|------------|--------|----------|
| `--sanity` | 1 | 99 | Pre-commit sanity check |
| `--pr` | 10 | 614 | PR review, major features |
| `--profile <name>` | varies | varies | Saved configuration |

**Interactive:** `/code-foundations:review` (no flags) prompts for profile.

---

## Architecture

```
Extraction → Checking → Investigation → Report
   haiku    1 per checklist   haiku       single
```

| Phase | Agents | Model |
|-------|--------|-------|
| Extraction | 1 per 5 files | haiku |
| Checking | 1 per checklist | inherited |
| Investigation | 1 per 5 findings | haiku |
| Report | 1 | inherited |

---

## Built-in Profiles

### sanity

Single quick-checklist with 99 curated critical checks.

Location: `agents/profiles/sanity.yaml`

### pr

Full review with 10 skill checklists:

| Skill | Checks |
|-------|--------|
| cc-defensive-programming | 31 |
| aposd-simplifying-complexity | 44 |
| aposd-reviewing-module-design | 36 |
| cc-code-layout-and-style | 85 |
| cc-control-flow-quality | 124 |
| aposd-verifying-correctness | 40 |
| cc-quality-practices | 115 |
| cc-performance-tuning | 50 |
| aposd-optimizing-critical-paths | 40 |
| cc-documentation-quality | 49 |
| **Total** | **614** |

Location: `agents/profiles/pr.yaml`

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

## Profile Structure

```yaml
name: my-profile
description: "Description"

checklists:
  - path: skills/cc-defensive-programming/checklists.md
    skills: [cc-defensive-programming]
  - path: .code-foundations/checklists/custom.md
    skills: [cc-defensive-programming]
```

Each checklist spawns one checking agent during review.
