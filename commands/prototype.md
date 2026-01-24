---
description: "Quick proof-of-concept with minimum code. Prove feasibility before committing to full implementation."
argument-hint: "[can I...? / prove X works / spike on Y]"
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash", "Skill", "Task"]
---

# /prototype

## STOP - Load Skills First

Before prototyping, load your skill lenses using the Skill tool:
1. `Skill(code-foundations:cc-pseudocode-programming)` - design before code
2. `Skill(code-foundations:aposd-reviewing-module-design)` - interface simplicity check

---

## STOP

- **ONE question** - If scope isn't atomic, narrow it
- **<50 lines** - If more, re-scope
- **Branch off main** - Never prototype on main

---

**Prove it works. Minimum code. Maximum learning.**

---

## Invoke Skill

```
Skill(code-foundations:prototype)
```

---

## Master Checklist - Execute In Order

**YOU MUST complete each step. No skipping.**

### Phase 1: SCOPE
- [ ] **1.1** Ask: "What ONE thing are you trying to prove?"
- [ ] **1.2** Narrow until atomic ("Can I...")
- [ ] **1.3** State: `SCOPE: [question]`

### Phase 2: CONTEXT
- [ ] **2.1** `git branch --show-current`
- [ ] **2.2** If main → `git checkout -b prototype/<slug>`
- [ ] **2.3** Run `Skill(code-foundations:aposd-reviewing-module-design)`
- [ ] **2.4** State: `CONTEXT: [summary]`

### Phase 3: MINIMUM
- [ ] **3.1** Run `Skill(code-foundations:cc-pseudocode-programming)` - 3-5 lines
- [ ] **3.2** Verify: happy path only, no error handling
- [ ] **3.3** Verify: <50 lines (re-scope if not)
- [ ] **3.4** State: `MINIMUM PATH: [pseudocode]`

### Phase 4: EXECUTE
- [ ] **4.1** Write code from pseudocode
- [ ] **4.2** Add header: `// PROTOTYPE: [scope] // NOT PRODUCTION`
- [ ] **4.3** Run the code
- [ ] **4.4** State: `RESULT: [what happened]`

### Phase 5: VERIFY
- [ ] **5.1** Answer: YES / NO / PARTIAL
- [ ] **5.2** If PARTIAL → specify what worked/didn't

### Phase 6: CAPTURE
- [ ] **6.1** `mkdir -p docs/prototypes`
- [ ] **6.2** Write `docs/prototypes/YYYY-MM-DD-<slug>.md`
- [ ] **6.3** Commit: `git commit -m "prototype: [scope] - [result]"`

---

## Mandatory Skill Invocations

**These are NOT optional:**

1. `Skill(code-foundations:aposd-reviewing-module-design)` - Step 2.3
2. `Skill(code-foundations:cc-pseudocode-programming)` - Step 3.1

---

## Gates

| Gate | Blocks |
|------|--------|
| Scope not atomic | Phase 2 |
| On main/master | Phase 4 |
| No pseudocode | Phase 4 |
| >50 lines | Phase 4 (re-scope) |
| No prototype log | Completion |

---

## What Happens Next

```
/code-foundations:prototype succeeds
     ↓
/code-foundations:whiteboarding (informed by learnings)
     ↓
/code-foundations:building (production code)
```
