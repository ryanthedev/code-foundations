# Phase 3: Smart Batching Pseudocode

**Purpose:** Guide the orchestrate-checking-agent to build intelligent batches from units.jsonl

---

## Constants

```
TOKEN_BUDGET = 4000         # Total tokens per batch
DIFF_TOKEN_BUDGET = 2500    # Reserved for unit diffs (rest for checklist + skills)
TOKENS_PER_DIFF_LINE = 12   # Diff lines include +/- markers, slightly more verbose
```

---

## Helper Functions

### estimate_tokens(unit)

```
Count the number of newline characters in unit.diff
Multiply by TOKENS_PER_DIFF_LINE (12)
Return the result
```

### is_skippable(unit)

```
If unit.file matches any of these patterns, return true with reason:
  - *.lock, *-lock.json → "lockfile"
  - *.generated.*, *.pb.*, *_generated.* → "generated"
  - *.min.js, *.bundle.js → "bundled"
  - __snapshots__/* → "snapshot"
  - vendor/*, node_modules/* → "vendor"
Otherwise return false
```

### find_tested_unit(test_unit, all_units)

```
Get the name from test_unit.testsUnit
If testsUnit is empty or null, return null

For each unit in all_units:
  If unit.name equals testsUnit:
    Return unit

Return null (no match found)
```

### build_call_clusters(units)

```
Initialize a parent map: each unit maps to itself (union-find)

For each unit in units:
  For each called_name in unit.calls:
    Find any unit whose name equals called_name
    If found:
      Union the two units (merge their sets)

Extract connected components from the union-find structure
Return list of clusters (each cluster is a list of units)
```

### chunk_by_tokens(units, token_limit)

```
Initialize batches as empty list
Initialize current_batch as empty list
Initialize current_tokens as 0

For each unit in units:
  unit_tokens = estimate_tokens(unit)

  If current_tokens + unit_tokens > token_limit AND current_batch is not empty:
    Add current_batch to batches
    Reset current_batch to empty
    Reset current_tokens to 0

  Add unit to current_batch
  Add unit_tokens to current_tokens

If current_batch is not empty:
  Add current_batch to batches

Return batches
```

### dirname(file_path)

```
Find the last "/" in file_path
Return everything before that last "/"
If no "/" found, return "."
```

---

## Main Workflow

### Step 1: Read and Parse Units

```
Read the file at $BASE_DIR/units.jsonl
Initialize all_units as empty list

For each line in the file:
  Parse line as JSON
  Add parsed object to all_units

Record total_units = count of all_units
```

### Step 2: Apply Skip Filters

```
Initialize skipped as empty list
Initialize remaining as empty set (will hold indices of units to batch)

For each unit at index i in all_units:
  Check if is_skippable(unit) returns true

  If skippable:
    Add {file: unit.file, reason: skip_reason} to skipped
  Else:
    Add index i to remaining
```

### Step 3: Create Test Pairs

```
Initialize batches as empty list
Initialize batch_id = 1

For each index i in remaining:
  unit = all_units[i]

  If unit.isTest is true AND unit.testsUnit is not empty:
    tested_unit = find_tested_unit(unit, all_units)

    If tested_unit found AND tested_unit's index is in remaining:
      Create batch:
        id = batch_id
        batch_strategy = "test_pair"
        shared_context = "Test pair: " + tested_unit.name
        units = [unit, tested_unit]
        total_diff_tokens = estimate_tokens(unit) + estimate_tokens(tested_unit)

      Add batch to batches
      Increment batch_id
      Remove unit's index from remaining
      Remove tested_unit's index from remaining
```

### Step 4: Build Call Graph Clusters

```
Get units at indices still in remaining
clusters = build_call_clusters(those units)

For each cluster in clusters:
  If cluster has more than 1 unit:
    cluster_tokens = sum of estimate_tokens for each unit in cluster

    If cluster_tokens <= DIFF_TOKEN_BUDGET:
      Create batch:
        id = batch_id
        batch_strategy = "call_graph"
        shared_context = "Connected by calls: " + join unit names with ", "
        units = cluster
        total_diff_tokens = cluster_tokens

      Add batch to batches
      Increment batch_id
      Remove all cluster unit indices from remaining

    Else:
      # Cluster too large, leave units for directory grouping
      Continue
```

### Step 5: Group by Directory

```
Get units at indices still in remaining
Group these units by dirname(unit.file)

For each directory, units_in_dir:
  dir_batches = chunk_by_tokens(units_in_dir, DIFF_TOKEN_BUDGET)

  For each chunk in dir_batches:
    Create batch:
      id = batch_id
      batch_strategy = "directory"
      shared_context = "Directory: " + directory path
      units = chunk
      total_diff_tokens = sum of estimate_tokens for each unit

    Add batch to batches
    Increment batch_id
    Remove all chunk unit indices from remaining
```

### Step 6: Group by Layer

```
Get units at indices still in remaining (should be few if any)
Group these units by unit.layer

For each layer, units_in_layer:
  layer_batches = chunk_by_tokens(units_in_layer, DIFF_TOKEN_BUDGET)

  For each chunk in layer_batches:
    Create batch:
      id = batch_id
      batch_strategy = "layer"
      shared_context = "Layer: " + layer name
      units = chunk
      total_diff_tokens = sum of estimate_tokens for each unit

    Add batch to batches
    Increment batch_id
    Remove all chunk unit indices from remaining
```

### Step 7: Handle Stragglers

```
If remaining is not empty:
  # Units with no layer, no directory match, orphaned
  stragglers = units at indices still in remaining
  straggler_batches = chunk_by_tokens(stragglers, DIFF_TOKEN_BUDGET)

  For each chunk in straggler_batches:
    Create batch:
      id = batch_id
      batch_strategy = "fallback"
      shared_context = "Ungrouped units"
      units = chunk
      total_diff_tokens = sum of estimate_tokens for each unit

    Add batch to batches
    Increment batch_id
```

---

## Output

### Write checking-batches.json

```
Build output object:
  total_units = count of all_units
  total_batches = count of batches
  skipped_count = count of skipped
  skipped = skipped array
  batches = batches array

Write output object as JSON to $BASE_DIR/checking-batches.json
```

### Return Summary

```
Return message: "Orchestration complete: {total_units} units -> {total_batches} batches ({skipped_count} skipped)"
```

---

## Batch Object Schema

Each batch in the output contains:

| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Sequential batch identifier |
| `batch_strategy` | string | How units were grouped: test_pair, call_graph, directory, layer, fallback |
| `shared_context` | string | Human-readable description of why these units are together |
| `units` | array | Full unit objects (all fields preserved from units.jsonl) |
| `total_diff_tokens` | int | Estimated tokens for all diffs in this batch |

---

## Verification Checklist

Before outputting, verify:

- [ ] All units accounted for (batched + skipped = total_units)
- [ ] No unit appears in multiple batches
- [ ] Each batch is under DIFF_TOKEN_BUDGET (2500 tokens)
- [ ] Test pairs keep test with subject
- [ ] batch_strategy reflects actual grouping method used
