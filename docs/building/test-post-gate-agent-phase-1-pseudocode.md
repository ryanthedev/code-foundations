# Pseudocode: Phase 1 - Add post-gate-agent to plugin manifest

## Files to Create/Modify
- `.claude-plugin/plugin.json` -- modify the `description` field only

## Pseudocode

### .claude-plugin/plugin.json

```
Read the existing plugin.json

Locate the "description" field

The current description ends with:
  "Building workflow: pre-gate-agent for discovery/pseudocode,
   implementation-agent for code execution."

Replace the building workflow sentence to include all three agents:
  "Building workflow: pre-gate-agent for discovery/pseudocode,
   implementation-agent for code execution,
   post-gate-agent for quality review."

All other fields remain unchanged (name, version, author, license, keywords)

Write the updated JSON back to disk

Validate the result is still valid JSON
```

## Design Notes

**Why "post-gate-agent for quality review"?**

I considered three phrasings:
1. "post-gate-agent for quality review" -- concise, matches the agent's purpose
2. "post-gate-agent for verification and review" -- more precise but longer
3. "post-gate-agent for post-implementation gates" -- too self-referential

Option 1 wins: it follows the same pattern as the other two agents (agent-name + "for" + purpose), is concise, and accurately describes what the post-gate-agent does.

**Information hiding (depth check):** Not applicable -- this is a user-facing metadata string, not a module interface. The description is intentionally a summary, not an exhaustive specification.

**Scope constraint:** Only the `description` field changes. No version bump, no structural changes, no new keys. The plan explicitly says "Phase 1 is config-only."

## PRE-GATE Status
- [x] Discovery complete
- [x] Pseudocode complete
- [x] Design reviewed (phrasing alternatives considered)
- [x] Ready for implementation
