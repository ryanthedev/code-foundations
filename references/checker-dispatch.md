# CHECKER(skill) Dispatch Pattern

When you see `CHECKER(skill-name)` in a checklist, dispatch a subagent to run that skill's full checklist.

---

## Pattern

```
- [ ] CHECKER(cc-defensive-programming)
```

**Means:** Dispatch a subagent with the skill's checklist AND the code to check.

---

## Context Is Required

The subagent has no context about what code to review. **You must pass it.**

| Method | When to Use | Capacity |
|--------|-------------|----------|
| **Inline code** | Known code, fastest | ~3,000 lines (50k tokens) |
| **File paths** | Specific files | Unlimited (agent reads) |
| **Diff args** | Review workflows | Unlimited (agent reads) |

**Inline is preferred** when possible - no file I/O, no git commands, fastest execution.

---

## Template: Inline Code (Preferred)

Best for most tasks. Subagents have 200k context - you can inline ~3,000 lines (50k tokens) comfortably while leaving room for skill, checklist, and response.

```
Task(
  subagent_type: "general-purpose",
  description: "Check: {skill-name}",
  prompt: """
## Checklist Agent: {skill-name}

### Code to Review

```{language}
// {file_path}
{THE_ACTUAL_CODE}
```

### Instructions

1. Load skill:
   Skill(code-foundations:{skill-name})

2. Read checklist:
   Read(skills/{skill-name}/checklists.md)

3. Execute EVERY checklist item against the code above.

4. For each item, record:
   - **PASS**: One-line evidence
   - **FINDING**: file:line, issue, evidence, confidence (HIGH/LOW)

5. Return findings summary.
"""
)
```

---

## Template: File Paths

Use when code is too large to inline (>3,000 lines) or when you don't have the code in context.

```
Task(
  subagent_type: "general-purpose",
  description: "Check: {skill-name}",
  prompt: """
## Checklist Agent: {skill-name}

### Files to Review

- {REPO_ROOT}/src/auth.ts
- {REPO_ROOT}/src/validation.ts

### Instructions

1. Load skill:
   Skill(code-foundations:{skill-name})

2. Read checklist:
   Read(skills/{skill-name}/checklists.md)

3. Read each file listed above.

4. Execute EVERY checklist item against the code.

5. For each item, record:
   - **PASS**: One-line evidence
   - **FINDING**: file:line, issue, evidence, confidence (HIGH/LOW)

6. Return findings summary.
"""
)
```

---

## Template: Diff Args

Use in review workflows where you're checking a git diff (staged, unstaged, branch comparison).

```
Task(
  subagent_type: "general-purpose",
  description: "Check: {skill-name}",
  prompt: """
## Checklist Agent: {skill-name}

### Code to Review

Run in {REPO_ROOT}:
```bash
git diff {DIFF_ARGS}
```

Read the changed files for full context.

### Instructions

1. Load skill:
   Skill(code-foundations:{skill-name})

2. Read checklist:
   Read(skills/{skill-name}/checklists.md)

3. Get the diff and read changed files.

4. Execute EVERY checklist item against the changed code.

5. For each item, record:
   - **PASS**: One-line evidence
   - **FINDING**: file:line, issue, evidence, confidence (HIGH/LOW)

6. Return findings summary.
"""
)
```

---

## Multiple CHECKERs

Dispatch in parallel with a single message:

```markdown
### Verification Phase
- [ ] CHECKER(cc-routine-and-class-design)
- [ ] CHECKER(cc-defensive-programming)
```

**Both get the same context:**
```
Task(...cc-routine-and-class-design... Code: {same context})
Task(...cc-defensive-programming... Code: {same context})
```

---

## Investigation Tasks

If a finding has LOW confidence, create an investigation task:

```
TaskCreate(
  subject: "Investigate: {finding.id}",
  description: "{file}:{line} - {issue}",
  activeForm: "Investigating {finding.id}"
)
```

---

## Example Output

```
## Check: cc-defensive-programming

**Items checked:** 31
**Findings:** 2

1. **DP-7** src/auth.ts:42 - Empty catch block
   Evidence: `catch (e) {}`
   Confidence: HIGH

2. **DP-12** src/api.ts:89 - User input not validated
   Evidence: `query(req.body.id)`
   Confidence: LOW → Investigation task created
```
