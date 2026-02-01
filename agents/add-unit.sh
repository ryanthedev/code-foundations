#!/bin/bash
# add-unit.sh - Extraction agents use this to add semantic units
# Enforces schema. Exits non-zero if validation fails.
# Supports single record (CLI args) or batch (--stdin JSON array)

set -e

error() {
  echo "ERROR: $1" >&2
  exit 1
}

# Determine output file
get_output_file() {
  if [[ -n "$OUTPUT" ]]; then
    echo "$OUTPUT"
  elif [[ -n "$BASE_DIR" ]]; then
    echo "$BASE_DIR/units.jsonl"
  else
    error "Either --output or \$BASE_DIR must be set"
  fi
}

# Validate a single unit JSON object, returns validated JSON or exits
validate_unit() {
  local json="$1"

  # Extract fields
  local file=$(echo "$json" | jq -r '.file // empty')
  local name=$(echo "$json" | jq -r '.name // empty')
  local type=$(echo "$json" | jq -r '.type // empty')
  local start_line=$(echo "$json" | jq -r '.lines[0] // .start_line // empty')
  local end_line=$(echo "$json" | jq -r '.lines[1] // .end_line // empty')
  local diff=$(echo "$json" | jq -r '.diff // empty')
  local summary=$(echo "$json" | jq -r '.summary // empty')
  local has_loops=$(echo "$json" | jq -r '.has_loops // false')
  local has_async=$(echo "$json" | jq -r '.has_async // false')
  local has_try_catch=$(echo "$json" | jq -r '.has_try_catch // false')

  # Validate required fields
  [[ -z "$file" ]] && error "Missing required: file"
  [[ -z "$name" ]] && error "Missing required: name"
  [[ -z "$type" ]] && error "Missing required: type"
  [[ -z "$start_line" ]] && error "Missing required: start_line/lines[0]"
  [[ -z "$end_line" ]] && error "Missing required: end_line/lines[1]"
  [[ -z "$diff" ]] && error "Missing required: diff"
  [[ -z "$summary" ]] && error "Missing required: summary"

  # Validate type enum
  case "$type" in
    function|method|class) ;;
    *) error "type must be function, method, or class, got: $type" ;;
  esac

  # Validate lines are integers
  [[ ! "$start_line" =~ ^[0-9]+$ ]] && error "start_line must be an integer, got: $start_line"
  [[ ! "$end_line" =~ ^[0-9]+$ ]] && error "end_line must be an integer, got: $end_line"

  # Validate start <= end
  [[ "$start_line" -gt "$end_line" ]] && error "start_line ($start_line) cannot be greater than end_line ($end_line)"

  # Build normalized JSON (compact for JSONL)
  jq -cn \
    --arg file "$file" \
    --arg name "$name" \
    --arg type "$type" \
    --argjson start_line "$start_line" \
    --argjson end_line "$end_line" \
    --arg diff "$diff" \
    --arg summary "$summary" \
    --argjson has_loops "$has_loops" \
    --argjson has_async "$has_async" \
    --argjson has_try_catch "$has_try_catch" \
    '{file: $file, name: $name, type: $type, lines: [$start_line, $end_line], diff: $diff, summary: $summary, has_loops: $has_loops, has_async: $has_async, has_try_catch: $has_try_catch}'
}

# Batch mode: read JSON array from stdin
process_stdin() {
  local output_file=$(get_output_file)
  local input=$(cat)
  local count=0

  # Check if input is valid JSON array
  if ! echo "$input" | jq -e 'type == "array"' > /dev/null 2>&1; then
    error "Input must be a JSON array"
  fi

  # Process each object in the array
  local total=$(echo "$input" | jq 'length')
  for ((i=0; i<total; i++)); do
    local unit=$(echo "$input" | jq -c ".[$i]")
    local validated
    if ! validated=$(validate_unit "$unit"); then
      error "Validation failed for item $i"
    fi
    echo "$validated" >> "$output_file"
    ((count++))
  done

  echo "Added $count units"
}

# Single mode: parse CLI args
process_single() {
  local FILE=""
  local NAME=""
  local TYPE=""
  local START_LINE=""
  local END_LINE=""
  local DIFF=""
  local SUMMARY=""
  local HAS_LOOPS="false"
  local HAS_ASYNC="false"
  local HAS_TRY_CATCH="false"

  while [[ $# -gt 0 ]]; do
    case $1 in
      --file) FILE="$2"; shift 2 ;;
      --name) NAME="$2"; shift 2 ;;
      --type) TYPE="$2"; shift 2 ;;
      --start-line) START_LINE="$2"; shift 2 ;;
      --end-line) END_LINE="$2"; shift 2 ;;
      --diff) DIFF="$2"; shift 2 ;;
      --summary) SUMMARY="$2"; shift 2 ;;
      --has-loops) HAS_LOOPS="true"; shift ;;
      --has-async) HAS_ASYNC="true"; shift ;;
      --has-try-catch) HAS_TRY_CATCH="true"; shift ;;
      --output) OUTPUT="$2"; shift 2 ;;
      -h|--help) usage ;;
      *) error "Unknown option: $1" ;;
    esac
  done

  # Build JSON from args
  local json=$(jq -n \
    --arg file "$FILE" \
    --arg name "$NAME" \
    --arg type "$TYPE" \
    --arg start_line "$START_LINE" \
    --arg end_line "$END_LINE" \
    --arg diff "$DIFF" \
    --arg summary "$SUMMARY" \
    --argjson has_loops "$HAS_LOOPS" \
    --argjson has_async "$HAS_ASYNC" \
    --argjson has_try_catch "$HAS_TRY_CATCH" \
    '{file: $file, name: $name, type: $type, start_line: $start_line, end_line: $end_line, diff: $diff, summary: $summary, has_loops: $has_loops, has_async: $has_async, has_try_catch: $has_try_catch}')

  local validated
  if ! validated=$(validate_unit "$json"); then
    exit 1
  fi
  local output_file=$(get_output_file)

  echo "$validated" >> "$output_file"
  echo "Added $TYPE $NAME ($FILE:$START_LINE-$END_LINE)"
}

usage() {
  cat <<EOF
Usage:
  Single: add-unit.sh --file <path> --name <name> --type <type> --start-line <n> --end-line <n> --diff <text> --summary <text> [options]
  Batch:  cat units.json | add-unit.sh --stdin

Single mode options:
  --file <path>       File path
  --name <name>       Unit name (function/class/method name)
  --type <type>       function, method, or class
  --start-line <n>    Starting line number
  --end-line <n>      Ending line number
  --diff <text>       Diff hunk for this unit
  --summary <text>    One-line summary of what changed (<10 words)
  --has-loops         Unit contains loops (default: false)
  --has-async         Unit is async/await (default: false)
  --has-try-catch     Unit has try/catch (default: false)
  --output <path>     Output file (default: \$BASE_DIR/units.jsonl)

Batch mode:
  --stdin             Read JSON array from stdin

Batch JSON format:
  [
    {
      "file": "src/api.ts",
      "name": "createUser",
      "type": "function",
      "lines": [10, 45],
      "diff": "@@ -10,6 +10,15 @@...",
      "summary": "Added input validation",
      "has_loops": false,
      "has_async": true,
      "has_try_catch": false
    }
  ]

EOF
  exit 1
}

# Main
OUTPUT=""

# Check for --stdin first
if [[ "$1" == "--stdin" ]]; then
  shift
  # Check for --output after --stdin
  if [[ "$1" == "--output" ]]; then
    OUTPUT="$2"
    shift 2
  fi
  process_stdin
elif [[ "$1" == "-h" || "$1" == "--help" || -z "$1" ]]; then
  usage
else
  process_single "$@"
fi
