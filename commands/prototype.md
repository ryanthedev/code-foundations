---
description: "Quick proof-of-concept with minimum code. Prove feasibility before committing to full implementation."
argument-hint: "[can I...? / prove X works / spike on Y]"
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash", "Skill"]
---

# /prototype

**Prove it works. Minimum code. Maximum learning.**

---

## Invoke Skill

```
Skill(code-foundations:prototype)
```

---

## Execution Flow

### 1. SCOPE (One Question)

Ask: "What ONE thing are you trying to prove?"

Narrow until atomic:
- "Can I show a system notification?"
- "Can I read from this database?"
- "Can I render a window?"

**Not:** "Can I build the feature?" (too broad)

### 2. CONTEXT (Quick Check)

```bash
# Where are we?
git branch --show-current
ls -la
```

- Existing repo or new?
- What APIs/libraries available?
- Constraints?

### 3. MINIMUM (Shortest Path)

**INVOKE cc-pseudocode-programming** (3-5 lines only):
- Happy path ONLY
- Hardcode values
- Skip validation

**Target: ~50 lines max.** If more, re-scope.

### 4. EXECUTE (Surgical Code)

```bash
git checkout -b prototype/<scope-slug>
```

Write clean minimum:
```javascript
// PROTOTYPE: [scope question]
// NOT PRODUCTION: no error handling
[minimal code that proves concept]
// Result: [what happened]
```

### 5. VERIFY (Binary Answer)

| Result | Action |
|--------|--------|
| YES | Capture what worked |
| NO | Capture the blocker |
| PARTIAL | Narrow scope, retry |

### 6. CAPTURE (Prototype Log)

```bash
mkdir -p docs/prototypes
```

Write to `docs/prototypes/YYYY-MM-DD-<scope>.md`:
- What we proved
- Minimum working code
- Key learnings
- Production considerations

---

## What Happens Next

```
/prototype succeeds
     ↓
/whiteboarding (informed by prototype)
     ↓
/building (production implementation)
```

---

## Key Rules

- **One thing** - Multiple goals = nothing proven
- **Minimum code** - Extra code obscures learnings
- **Clean over fast** - Messy POC = unclear learnings
- **Always branch** - Even POC doesn't go on main
- **Always capture** - Undocumented = forgotten
