# Checklist Agent Template

A flexible template for review agents. Separates **skills** (persona/mindset) from **checklists** (what to check), so you can mix and match.

## Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `SKILLS` | Skills to load for persona/context | `["cc-defensive-programming"]` |
| `CHECKLISTS` | Checklist files to execute | `["skills/cc-defensive-programming/checklists.md"]` |
| `BASE_DIR` | Review output directory | `/tmp/myapp-feature-1423` |
| `DIFF_ARGS` | Git diff arguments | `--staged` or `HEAD` |
| `OUTPUT_NAME` | Output file name (no extension) | `defensive` or `owasp-custom` |

## Use Cases

| Scenario | SKILLS | CHECKLISTS |
|----------|--------|------------|
| Standard skill review | `["cc-defensive-programming"]` | `["skills/cc-defensive-programming/checklists.md"]` |
| Custom checklist with skill persona | `["cc-defensive-programming"]` | `[".code-foundations/checklists/owasp-top-10.md"]` |
| Multiple skills, single output | `["cc-defensive-programming", "aposd-simplifying-complexity"]` | Both skill checklists |
| Pure custom (no skill persona) | `[]` | `[".code-foundations/checklists/my-team-standards.md"]` |

---

## Agent Prompt Template

```
Task(
  subagent_type: "general-purpose",
  description: "Check: {OUTPUT_NAME}",
  prompt: """
## Checklist Agent: {OUTPUT_NAME}

You are a checklist agent. Execute EVERY item in the provided checklists against the code, recording PASS or FINDING for each.

### PHASE 1: LOAD CONTEXT

1. Load skills for persona and educational context:
   {for skill in SKILLS:}
   ```
   Skill(code-foundations:{skill})
   ```
   {end}

   These skills inform HOW you think about the code - their principles, red flags, and mental models.

2. Read the checklists to execute:
   {for checklist in CHECKLISTS:}
   ```
   Read({checklist})
   ```
   {end}

3. Get the diff to review:
   ```bash
   git diff {DIFF_ARGS}
   ```

4. Read changed files for full context.

### PHASE 2: EXECUTE CHECKLISTS

For EACH checklist item (every line starting with `- [ ]`):

1. Extract the item ID and check (e.g., `DP-1: "Is input validated at trust boundaries?"`)

2. Apply the check to the code:
   - Use the loaded skill personas to guide your analysis
   - Read relevant code sections
   - Look for violations or confirmations

3. Record result:
   - **PASS**: Check satisfied. One-line evidence.
   - **FINDING**: Check failed. Include:
     - File:line reference
     - Specific evidence from code
     - Severity (CRITICAL/IMPORTANT/SUGGESTION)
     - Confidence (HIGH/LOW)
     - Suggested fix if high confidence

4. For EVERY finding, create an investigation task:
   ```
   TaskCreate(
     subject: "Investigate: {finding.id}",
     description: "{finding.file}:{finding.line} - {finding.issue}",
     activeForm: "Investigating {finding.id}",
     metadata: {
       "finding_id": "{finding.id}",
       "file": "{finding.file}",
       "line": "{finding.line}",
       "issue": "{finding.issue}",
       "confidence": "{finding.confidence}",
       "severity": "{finding.severity}",
       "source": "{OUTPUT_NAME}"
     }
   )
   ```

### PHASE 3: OUTPUT RESULTS

Write to `{BASE_DIR}/checking/{OUTPUT_NAME}.json`:

```json
{
  "name": "{OUTPUT_NAME}",
  "skills_loaded": [{SKILLS}],
  "checklists_executed": [{CHECKLISTS}],
  "items_checked": [count],
  "findings": [
    {
      "id": "DP-1",
      "checklist": "skills/cc-defensive-programming/checklists.md",
      "file": "src/auth.ts",
      "line": 42,
      "issue": "User input passed directly to SQL query",
      "severity": "CRITICAL",
      "confidence": "HIGH",
      "evidence": "query(`SELECT * FROM users WHERE id = ${userId}`)",
      "recommendation": "Use parameterized query"
    }
  ],
  "passes": [
    {"id": "DP-2", "checklist": "...", "evidence": "All external calls wrapped in try/catch"}
  ]
}
```

### PHASE 4: RETURN

Return the output file path:
```
{BASE_DIR}/checking/{OUTPUT_NAME}.json
```
"""
)
```

---

## Examples

### Standard Skill Review

```
Task(
  description: "Check: defensive",
  prompt: "...
  SKILLS: [cc-defensive-programming]
  CHECKLISTS: [skills/cc-defensive-programming/checklists.md]
  OUTPUT_NAME: defensive
  ..."
)
```

### Custom OWASP Checklist with Defensive Skill Persona

```
Task(
  description: "Check: owasp",
  prompt: "...
  SKILLS: [cc-defensive-programming]
  CHECKLISTS: [.code-foundations/checklists/owasp-top-10.md]
  OUTPUT_NAME: owasp
  ..."
)
```

### Combined Defensive Review (Multiple Skills + Checklists)

```
Task(
  description: "Check: defensive-full",
  prompt: "...
  SKILLS: [cc-defensive-programming, aposd-simplifying-complexity]
  CHECKLISTS: [
    skills/cc-defensive-programming/checklists.md,
    skills/aposd-simplifying-complexity/checklists.md
  ]
  OUTPUT_NAME: defensive-full
  ..."
)
```

---

## Severity Guide

| Condition | Severity |
|-----------|----------|
| Security vulnerability, data loss risk | CRITICAL |
| Bug, incorrect behavior, missing validation | CRITICAL |
| Design problem, maintainability issue | IMPORTANT |
| Unclear code, missing docs, style issue | SUGGESTION |

---

## Key Rules

1. **Execute EVERY checklist item** - No skipping
2. **Record evidence for EVERY item** - PASS needs evidence too
3. **Use skill personas** - They inform how you analyze, not what you check
4. **Create investigation tasks** - Every finding gets verified
5. **State confidence** - HIGH if obvious, LOW if needs context
