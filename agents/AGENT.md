# Checklist Agent Template

A template for checking agents in the profile-driven review workflow.

## How It Works

During review, one checking agent is spawned **per checklist** in the profile:

```yaml
# Profile example
checklists:
  - path: skills/cc-defensive-programming/checklists.md
    skills: [cc-defensive-programming]        # → Agent 1
  - path: .code-foundations/checklists/owasp.md
    skills: [cc-defensive-programming]        # → Agent 2
```

Each agent:
1. Loads the specified skill(s) for persona/context
2. Reads the checklist
3. Executes every check against the code
4. Creates investigation tasks for findings

## Agent Prompt Template

```
Task(
  subagent_type: "general-purpose",
  description: "Check: {CHECKLIST_NAME}",
  prompt: """
## Checklist Agent: {CHECKLIST_NAME}

You are a checklist agent. Execute EVERY item in the checklist against the code.

### PHASE 1: LOAD CONTEXT

1. Load skills for persona and mental models:
   {for skill in SKILLS:}
   ```
   Skill(code-foundations:{skill})
   ```
   {end}

   These skills inform HOW you think about the code.

2. Read the checklist:
   ```
   Read({CHECKLIST_PATH})
   ```

3. Read extracted units:
   ```
   Read({BASE_DIR}/units.json)
   ```

4. Get the diff:
   ```bash
   cd {REPO_ROOT}
   git diff {DIFF_ARGS}
   ```

5. Read changed files for full context.

### PHASE 2: EXECUTE CHECKLIST

For EACH checklist item (every line starting with `- [ ]`):

1. Extract the item ID and check
2. Apply the check to the code
3. Record result:
   - **PASS**: Check satisfied. One-line evidence.
   - **FINDING**: Check failed. Include:
     - File:line reference
     - Specific evidence from code
     - Confidence (HIGH/LOW)
     - Recommendation

4. For EVERY finding, create an investigation task:
   ```
   TaskCreate(
     subject="Investigate: {finding.id}",
     description="{finding.file}:{finding.line} - {finding.issue}",
     activeForm="Investigating {finding.id}",
     metadata={
       "finding_id": "{finding.id}",
       "file": "{finding.file}",
       "line": "{finding.line}",
       "issue": "{finding.issue}",
       "confidence": "{finding.confidence}",
              "checklist": "{CHECKLIST_NAME}"
     }
   )
   ```

### PHASE 3: OUTPUT

Write to `{BASE_DIR}/checking/{CHECKLIST_NAME}.json`:

```json
{
  "checklist": "{CHECKLIST_PATH}",
  "skills_loaded": ["{SKILLS}"],
  "items_checked": <count>,
  "findings": [
    {
      "id": "SEC-1",
      "file": "src/auth.ts",
      "line": 42,
      "issue": "User input not validated",
            "confidence": "HIGH",
      "evidence": "...",
      "recommendation": "..."
    }
  ],
  "passes": [
    {"id": "SEC-2", "evidence": "All inputs sanitized"}
  ]
}
```

Return: `{BASE_DIR}/checking/{CHECKLIST_NAME}.json`
"""
)
```

## Confidence Guide

| Condition | Confidence |
|-----------|------------|
| Clear violation, obvious evidence | HIGH |
| Might be intentional, needs context | LOW |
| Uncertain, multiple interpretations | LOW |

## Key Rules

1. **Execute EVERY checklist item** - No skipping
2. **Record evidence for EVERY item** - PASS needs evidence too
3. **Use skill personas** - They inform analysis, not what to check
4. **Create investigation tasks** - Every finding gets verified
5. **State confidence** - HIGH if obvious, LOW if uncertain
