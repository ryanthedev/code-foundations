---
name: orchestrate-checking-agent
description: "Build intelligent batches from extracted units for checking phase."
model: sonnet
allowed-tools: ["Bash", "Glob", "Grep", "Read"]
---

# Orchestrate Checking Agent

Build intelligent batches from extracted units for the checking phase.

## Inputs

- `BASE_DIR`: Directory containing units.jsonl
- Output: `$BASE_DIR/checking-batches.json`

## Workflow

### 1. Read Extracted Units

```bash
cat $BASE_DIR/units.jsonl
```

Each line is a JSON object:
```json
{
  "file": "src/api.ts",
  "name": "createUser",
  "type": "function",
  "lines": [10, 45],
  "diff": "@@ -10,6 +10,15 @@...",
  "summary": "Added validation",
  "has_loops": false,
  "has_async": true,
  "has_try_catch": false
}
```

### 2. Build Intelligent Batches

Group units for checking. Each batch → one checker agent.

**Skip these files** (don't batch):
- `*.lock`, `*-lock.json` → lockfiles
- `*.generated.*`, `*.pb.*`, `*_generated.*` → generated code
- `*.min.js`, `*.bundle.js` → bundled/minified
- `__snapshots__/*` → test snapshots
- `vendor/*`, `node_modules/*` → dependencies

**Batching strategy:**
1. **By directory** - units from same dir share context
2. **By size** - combine small units until ~4k tokens, large units alone
3. **By relationship** - keep `foo.ts` + `foo.test.ts` together
4. **By imports** - units that call each other → same batch

Target: ~4k tokens of diff per batch

### 3. Write Output

Write to `$BASE_DIR/checking-batches.json`:

```json
{
  "total_units": 25,
  "skipped": [
    {"file": "package-lock.json", "reason": "lockfile"},
    {"file": "src/api.generated.ts", "reason": "generated code"}
  ],
  "batches": [
    {
      "id": 1,
      "shared_context": "User module - files import from each other",
      "units": [
        {
          "file": "src/user/api.ts",
          "name": "createUser",
          "type": "function",
          "lines": [10, 45],
          "has_loops": false,
          "has_async": true,
          "has_try_catch": false,
          "diff": "@@ -10,6 +10,15 @@..."
        }
      ],
      "total_diff_tokens": 850
    }
  ]
}
```

## Output

Return: "Orchestration complete: X units → Y batches (Z skipped)"
