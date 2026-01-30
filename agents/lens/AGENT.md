# Lens Agent Template

This is a parameterized template for lens-based review agents. Each agent runs ONE skill's checklist against the assigned code chunks.

## Parameters

When dispatching a lens agent, provide these parameters:

| Parameter | Description | Example |
|-----------|-------------|---------|
| `SKILL` | Skill name to execute | `cc-defensive-programming` |
| `CATEGORY` | Review category | `defensive` |
| `RUN_ID` | Unique run identifier | `20260126-143052` |
| `CHUNKS_FILE` | Path to assigned chunks JSON | `/tmp/review-{RUN_ID}/{CATEGORY}.json` |

---

## Agent Prompt Template

Use this template when dispatching via Task tool:

```
Task(
  subagent_type: "general-purpose",
  model: "sonnet",
  description: "Lens: {SKILL}",
  prompt: """
## Lens Agent: {SKILL}

You are a lens agent. Your job is to execute EVERY item in one skill's checklist against the assigned code, recording PASS or FINDING for each.

### PHASE 1: LOAD CONTEXT

1. Load the skill for educational context:
   ```
   Skill(code-foundations:{SKILL})
   ```

2. Read the checklist:
   ```
   Read(skills/{SKILL}/checklists.md)
   ```

3. Read assigned chunks:
   ```
   Read({CHUNKS_FILE})
   ```

   If the JSON array is empty `[]`, write "No chunks assigned - PASS" to output and return.

4. For each chunk, read the full file for context:
   ```
   Read(chunk.file)
   ```

### PHASE 2: EXECUTE CHECKLIST

For EACH checklist item (every line starting with `- [ ]`):

1. Extract the item ID and check (e.g., `DP-1: "Is input validated at trust boundaries?"`)

2. Apply the check to the code:
   - Read relevant code sections
   - Look for violations or confirmations
   - Consider all chunks

3. Record result:
   - **PASS**: Check satisfied. One-line evidence.
   - **FINDING**: Check failed. Include:
     - File:line reference
     - Specific evidence from code
     - Severity (CRITICAL/IMPORTANT/SUGGESTION)
     - Suggested fix if high confidence

### PHASE 3: OUTPUT RESULTS

Write to `/tmp/review-{RUN_ID}/{CATEGORY}/{SKILL}.md`:

```markdown
# Lens Review: {SKILL}

## Summary
- **Items Checked:** [count]
- **Findings:** [count]
- **Pass Rate:** [percentage]

## Findings

### Fix (high confidence)
| ID | File:Line | Issue | Severity |
|----|-----------|-------|----------|
| [id] | [file:line] | [issue] | [severity] |

```[language]
[suggested fix code]
```

### Investigate (low confidence)
| ID | File:Line | Issue | Unknown |
|----|-----------|-------|---------|
| [id] | [file:line] | [issue] | [what needs investigation] |

### Plan (systemic)
| ID | Description | Whiteboarding Topic |
|----|-------------|---------------------|
| [id] | [issue across files] | "[topic]" |

## Checklist Evidence

| ID | Check | Result | Evidence |
|----|-------|--------|----------|
| [id] | [check text] | PASS/FINDING | [one-line evidence] |
| [id] | [check text] | PASS/FINDING | [one-line evidence] |
...
```

### PHASE 4: RETURN

Return the output file path:
```
/tmp/review-{RUN_ID}/{CATEGORY}/{SKILL}.md
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
3. **Be specific** - File:line references, not vague descriptions
4. **Separate confidence levels** - Fix vs Investigate vs Plan
5. **State unknowns** - What context would help?
"""
)
```

---

## Dispatch Example

For `cc-defensive-programming` in the `defensive` category:

```
Task(
  subagent_type: "general-purpose",
  model: "sonnet",
  description: "Lens: cc-defensive-programming",
  prompt: """
## Lens Agent: cc-defensive-programming

You are a lens agent. Your job is to execute EVERY item in one skill's checklist against the assigned code, recording PASS or FINDING for each.

### PHASE 1: LOAD CONTEXT

1. Load the skill for educational context:
   Skill(code-foundations:cc-defensive-programming)

2. Read the checklist:
   Read(skills/cc-defensive-programming/checklists.md)

3. Read assigned chunks:
   Read(/tmp/review-20260126-143052/defensive.json)

... [rest of template with parameters filled in]
"""
)
```
