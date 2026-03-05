# Test: Post-Gate Agent Pipeline

Status: in-progress

## Objective

Validate the full 4-sub-phase pipeline with the new unified post-gate-agent. Two phases that make real changes — one config, one code — so the post-gate-agent has something meaningful to review.

## Phases

### Phase 1: Add post-gate-agent to plugin manifest

Register the new `post-gate-agent` in `.claude-plugin/plugin.json` alongside the existing agents field.

**Files:**
- `.claude-plugin/plugin.json` - Update description to mention post-gate-agent

**Tasks:**
1. Read plugin.json to understand current structure
2. Update description to include post-gate-agent alongside pre-gate-agent and implementation-agent
3. Verify JSON is valid

### Phase 2: Add agent validation helper script

Create a small shell script that validates all agent templates referenced in the building workflow actually exist as files.

**Files:**
- `agents/validate-agents.sh` - New script

**Tasks:**
1. Read `skills/building/SKILL.md` to find the agent type table
2. Write a script that checks each referenced agent file exists under `agents/`
3. Script should exit 0 if all found, exit 1 with missing list if any missing
4. Make it executable

## Testing

Verify:
- plugin.json is valid JSON after edits
- `agents/validate-agents.sh` runs and exits 0
- Post-gate review files exist in `docs/building/` after each phase

## Constraints

- Phase 1 is config-only
- Phase 2 is a small script (~20 lines)
- Each phase should be completable by sonnet-tier agents
