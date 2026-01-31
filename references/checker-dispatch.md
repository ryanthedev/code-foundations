# CHECKER(skill) Dispatch Pattern

When you see `CHECKER(skill-name)` in a checklist, dispatch a subagent to run that skill's full checklist.

---

## Pattern

```
- [ ] CHECKER(cc-defensive-programming)
```

**Means:** Dispatch a subagent that loads the skill, reads its checklist, and reports findings.

---

## Dispatch Template

```
Task(
  subagent_type: "general-purpose",
  description: "Check: {skill-name}",
  prompt: """
## Checklist Agent: {skill-name}

Run the full checklist for this skill against the code under review.

### Step 1: Load Context

1. Load skill:
   Skill(code-foundations:{skill-name})

2. Read checklist:
   Read(skills/{skill-name}/checklists.md)

3. Read the code being reviewed.

### Step 2: Execute Checklist

For each item in the checklist:
- Apply check to code
- Record PASS (with evidence) or FINDING

For findings, record:
- file:line
- issue description
- evidence from code
- confidence (HIGH/LOW)

### Step 3: Return Summary

Return:
- Total items checked
- Findings list (file:line, issue, confidence)
- Overall assessment
"""
)
```

---

## Multiple CHECKERs

When multiple CHECKERs appear together, dispatch them in parallel:

```markdown
### Verification Phase
- [ ] CHECKER(cc-routine-and-class-design)
- [ ] CHECKER(cc-defensive-programming)
```

**Dispatch in single message:**
```
Task(...cc-routine-and-class-design...)
Task(...cc-defensive-programming...)
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
