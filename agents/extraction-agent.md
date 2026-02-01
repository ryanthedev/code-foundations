---
name: extraction-agent
description: "Extract semantic units using AST, enrich with diff/summary, handle fallback files."
model: haiku
allowed-tools: ["Bash", "Glob", "Grep", "Read"]
---

# Extraction Agent

Extract semantic units from changed files using AST, then enrich each with diff hunk and summary.

## Inputs

- `DIFF_ARGS`: Git diff arguments (e.g., `--staged`, `HEAD~1`)
- `PLUGIN_ROOT`: Path to plugin directory
- `BASE_DIR`: Output directory

## Workflow

### 1. Run AST Extraction

```bash
AST_OUTPUT=$($PLUGIN_ROOT/agents/extract-units.sh $DIFF_ARGS)
echo "$AST_OUTPUT" | jq .
```

Output:
```json
{
  "units": [
    {
      "type": "method",
      "name": "ValidateUser",
      "file": "src/api.ts",
      "lines": [10, 45],
      "has_loops": false,
      "has_async": true,
      "has_try_catch": true,
      "has_io_calls": true,
      "nesting_depth": 3
    }
  ],
  "fallback_files": ["src/utils.sh"],
  "tree_sitter_available": true
}
```

### 2. For Each AST Unit

For each unit in the `units` array:

**Get the diff hunk:**
```bash
git diff $DIFF_ARGS -- "src/api.ts" | head -50
```

**Generate summary:** Read the hunk, describe what changed in <10 words.

**Call add-unit.sh:**
```bash
$PLUGIN_ROOT/agents/add-unit.sh \
  --file "src/api.ts" \
  --name "ValidateUser" \
  --type "method" \
  --start-line 10 \
  --end-line 45 \
  --diff "@@ -10,6 +10,15 @@ async function ValidateUser..." \
  --summary "Added input validation and error handling" \
  --has-async \
  --has-try-catch
```

### 3. For Each Fallback File

For files in `fallback_files` (AST couldn't parse):

```bash
# Read the file
Read(file_path)

# Get the diff
git diff $DIFF_ARGS -- "$FILE"
```

Identify each function/method/class, then call add-unit.sh:

```bash
$PLUGIN_ROOT/agents/add-unit.sh \
  --file "src/utils.sh" \
  --name "process_data" \
  --type "function" \
  --start-line 10 \
  --end-line 45 \
  --diff "@@ -10,5 +10,12 @@..." \
  --summary "Added logging" \
  --has-loops
```

## CLI Flags Reference

**Required:**
- `--file <path>` - File path
- `--name <name>` - Unit name
- `--type <type>` - function, method, or class
- `--start-line <n>` - Start line
- `--end-line <n>` - End line
- `--diff <text>` - Diff hunk
- `--summary <text>` - What changed (<10 words)

**Optional (set flag if true):**
- `--has-loops` - Contains loops
- `--has-async` - Contains async/await
- `--has-try-catch` - Contains try/catch

## Count Verification

```bash
# Count units in output
ACTUAL=$(wc -l < "$BASE_DIR/units.jsonl" | tr -d ' ')

# Should match: AST units + fallback units
AST_COUNT=$(echo "$AST_OUTPUT" | jq '.units | length')
echo "Total: $ACTUAL units (AST: $AST_COUNT)"
```

## Output

Return: "Extracted N units from M files"
