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

## Token Budget

```
TOTAL_TOKEN_BUDGET = 4000         # Total tokens per batch
DIFF_TOKEN_BUDGET = 2500          # Reserved for unit diffs
CHECKLIST_SKILL_BUDGET = 1500     # For checklist + skill context
TOKENS_PER_DIFF_LINE = 12         # Diff lines have +/- markers
```

**Token Estimation Formula:**
```
diff_tokens = (count_newlines_in_diff) * 12
```

Each batch should stay under 2500 diff tokens to leave room for checklist and skill context.

---

## Workflow

### Step 1: Read and Parse Units

Read `$BASE_DIR/units.jsonl` line by line. Each line is a JSON object:

```json
{
  "file": "src/api.ts",
  "name": "createUser",
  "type": "function",
  "lines": [10, 45],
  "diff": "@@ -10,6 +10,15 @@...",
  "summary": "Added validation",
  "layer": "api",
  "calls": ["validateUser", "saveUser"],
  "isTest": false,
  "testsUnit": null,
  "hasLoops": false,
  "hasAsync": true,
  "hasTryCatch": false,
  "hasThrow": false,
  "hasRecursion": false
}
```

Parse all units and count the total.

### Step 2: Apply Skip Filters

Skip files matching these patterns (do NOT batch them):

| Pattern | Reason | Examples |
|---------|--------|----------|
| `*.lock`, `*-lock.json` | lockfile | package-lock.json, Cargo.lock |
| `*.generated.*`, `*.pb.*`, `*_generated.*` | generated | api.pb.go, schema_generated.ts |
| `*.min.js`, `*.bundle.js` | bundled | app.min.js, vendor.bundle.js |
| `__snapshots__/*` | snapshot | __snapshots__/test.snap |
| `vendor/*`, `node_modules/*` | vendor | vendor/lib.go, node_modules/pkg |

For each skipped file, record: `{"file": "path", "reason": "lockfile"}`

**Result:** List of skipped files, set of remaining unit indices to batch.

### Step 3: Create Test Pairs

**Priority: Test pairs come FIRST.**

For each remaining unit where `isTest: true` and `testsUnit` is not empty:
1. Find the unit with `name` matching `testsUnit`
2. If found and that unit is also in remaining set:
   - Create batch with both units
   - Set `batch_strategy: "test_pair"`
   - Set `shared_context: "Test pair: <unit_name>"`
   - Calculate `total_diff_tokens` (sum of both units)
   - Remove both from remaining set

**Rationale:** Tests and their subjects share context and should be reviewed together.

### Step 4: Build Call Graph Clusters

For remaining units, build connected components using the `calls[]` field:

1. Initialize union-find structure (each unit is its own parent)
2. For each unit:
   - For each name in `calls[]`:
     - Find unit with that name
     - If found, union them (merge their sets)
3. Extract connected components (clusters of units that call each other)

For each cluster with more than 1 unit:
- Calculate cluster tokens (sum of all unit diff tokens)
- If `cluster_tokens <= 2500`:
  - Create batch with all cluster units
  - Set `batch_strategy: "call_graph"`
  - Set `shared_context: "Connected by calls: <unit1>, <unit2>..."`
  - Remove all cluster units from remaining
- If too large, skip clustering (fall through to directory grouping)

**Rationale:** Units that call each other have related functionality and benefit from joint review.

### Step 5: Group by Directory

For remaining units, group by directory (extract dirname from `file` path):

For each directory group:
1. Chunk units by token budget (2500 max)
2. For each chunk:
   - Create batch
   - Set `batch_strategy: "directory"`
   - Set `shared_context: "Directory: <dir_path>"`
   - Calculate `total_diff_tokens`
   - Remove units from remaining

**Chunking algorithm:**
```
current_batch = []
current_tokens = 0

for each unit in directory_group:
  unit_tokens = estimate_tokens(unit)

  if current_tokens + unit_tokens > 2500 AND current_batch not empty:
    emit current_batch
    reset current_batch and current_tokens

  add unit to current_batch
  add unit_tokens to current_tokens

if current_batch not empty:
  emit current_batch
```

### Step 6: Group by Layer

For remaining units (if any), group by `layer` field:

Valid layers: `api`, `service`, `domain`, `data`, `infra`

For each layer group:
1. Chunk units by token budget (same algorithm as Step 5)
2. For each chunk:
   - Create batch
   - Set `batch_strategy: "layer"`
   - Set `shared_context: "Layer: <layer_name>"`
   - Calculate `total_diff_tokens`
   - Remove units from remaining

**Rationale:** Units in the same architectural layer have similar concerns.

### Step 7: Handle Stragglers

If any units remain (no layer, orphaned, etc.):

1. Chunk by token budget (same algorithm)
2. For each chunk:
   - Create batch
   - Set `batch_strategy: "fallback"`
   - Set `shared_context: "Ungrouped units"`
   - Calculate `total_diff_tokens`

**Verification before output:**
- [ ] All units accounted for (batched + skipped = total_units)
- [ ] No unit appears in multiple batches
- [ ] Each batch under 2500 diff tokens
- [ ] batch_strategy matches actual grouping method

### Step 8: Write Output

Write to `$BASE_DIR/checking-batches.json`:

```json
{
  "total_units": 25,
  "total_batches": 6,
  "skipped_count": 3,
  "skipped": [
    {"file": "package-lock.json", "reason": "lockfile"},
    {"file": "src/api.generated.ts", "reason": "generated"}
  ],
  "batches": [
    {
      "id": 1,
      "batch_strategy": "test_pair",
      "shared_context": "Test pair: UserService",
      "units": [
        {
          "file": "src/user/service.ts",
          "name": "UserService",
          "type": "class",
          "lines": [10, 45],
          "diff": "@@ -10,6 +10,15 @@...",
          "layer": "service",
          "calls": ["validateUser"],
          "isTest": false,
          "testsUnit": null,
          "hasLoops": false,
          "hasAsync": true,
          "hasTryCatch": true,
          "hasThrow": false,
          "hasRecursion": false
        },
        {
          "file": "src/user/service.test.ts",
          "name": "UserServiceTest",
          "type": "class",
          "lines": [5, 30],
          "diff": "@@ -5,3 +5,12 @@...",
          "layer": "service",
          "calls": [],
          "isTest": true,
          "testsUnit": "UserService",
          "hasLoops": false,
          "hasAsync": true,
          "hasTryCatch": false,
          "hasThrow": false,
          "hasRecursion": false
        }
      ],
      "total_diff_tokens": 485
    },
    {
      "id": 2,
      "batch_strategy": "call_graph",
      "shared_context": "Connected by calls: validateUser, saveUser",
      "units": [...],
      "total_diff_tokens": 820
    },
    {
      "id": 3,
      "batch_strategy": "directory",
      "shared_context": "Directory: src/user",
      "units": [...],
      "total_diff_tokens": 1200
    }
  ]
}
```

### Batch Schema

Each batch contains:

| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Sequential batch identifier (starts at 1) |
| `batch_strategy` | string | How units were grouped: `test_pair`, `call_graph`, `directory`, `layer`, `fallback` |
| `shared_context` | string | Human-readable explanation of why these units are together |
| `units` | array | Full unit objects (ALL fields from units.jsonl preserved) |
| `total_diff_tokens` | int | Estimated tokens for all diffs in this batch |

---

## Output

Return: "Orchestration complete: {total_units} units → {total_batches} batches ({skipped_count} skipped)"
