#!/bin/bash
# add-verdict.sh - Investigation agents use this to add verified findings with fixes
# Enforces schema. Exits non-zero if validation fails.
# Supports single record (CLI args) or batch (--stdin JSON array)
# Fix structure supports multiple edits per finding

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
    echo "$BASE_DIR/verdicts.jsonl"
  else
    error "Either --output or \$BASE_DIR must be set"
  fi
}

# Validate a single verdict JSON object, returns validated JSON or exits
validate_verdict() {
  local json="$1"

  # Extract fields
  local finding_id=$(echo "$json" | jq -r '.finding_id // empty')
  local file=$(echo "$json" | jq -r '.file // empty')
  local line=$(echo "$json" | jq -r '.line // empty')
  local check_id=$(echo "$json" | jq -r '.check_id // empty')
  local verdict=$(echo "$json" | jq -r '.verdict // empty')
  local reason=$(echo "$json" | jq -r '.reason // empty')
  local explanation=$(echo "$json" | jq -r '.fix.explanation // empty')
  local question=$(echo "$json" | jq -r '.question // empty')

  # Validate required fields
  [[ -z "$finding_id" ]] && error "Missing required: finding_id"
  [[ -z "$file" ]] && error "Missing required: file"
  [[ -z "$line" ]] && error "Missing required: line"
  [[ -z "$check_id" ]] && error "Missing required: check_id"
  [[ -z "$verdict" ]] && error "Missing required: verdict"
  [[ -z "$reason" ]] && error "Missing required: reason"

  # Validate line is integer
  [[ ! "$line" =~ ^[0-9]+$ ]] && error "line must be an integer, got: $line"

  # Validate verdict enum
  case "$verdict" in
    CONFIRMED|FALSE_POSITIVE|NEEDS_CONTEXT) ;;
    *) error "verdict must be CONFIRMED, FALSE_POSITIVE, or NEEDS_CONTEXT, got: $verdict" ;;
  esac

  # Validate CONFIRMED requires fix with edits
  if [[ "$verdict" == "CONFIRMED" ]]; then
    [[ -z "$explanation" ]] && error "CONFIRMED requires fix.explanation"

    # Validate edits array exists and is non-empty
    local edits_count=$(echo "$json" | jq '.fix.edits | length // 0')
    [[ "$edits_count" -eq 0 ]] && error "CONFIRMED requires fix.edits array with at least one edit"

    # Validate each edit has required fields
    for ((i=0; i<edits_count; i++)); do
      local edit_file=$(echo "$json" | jq -r ".fix.edits[$i].file // empty")
      local edit_old=$(echo "$json" | jq -r ".fix.edits[$i].old_string // empty")
      local edit_new=$(echo "$json" | jq -r ".fix.edits[$i].new_string // empty")

      [[ -z "$edit_file" ]] && error "fix.edits[$i] missing required: file"
      [[ -z "$edit_old" ]] && error "fix.edits[$i] missing required: old_string"
      [[ -z "$edit_new" ]] && error "fix.edits[$i] missing required: new_string"
    done
  fi

  # Build normalized JSON based on verdict (compact for JSONL)
  if [[ "$verdict" == "CONFIRMED" ]]; then
    local edits=$(echo "$json" | jq -c '.fix.edits')
    jq -cn \
      --arg finding_id "$finding_id" \
      --arg file "$file" \
      --argjson line "$line" \
      --arg check_id "$check_id" \
      --arg verdict "$verdict" \
      --arg reason "$reason" \
      --arg explanation "$explanation" \
      --argjson edits "$edits" \
      '{finding_id: $finding_id, file: $file, line: $line, check_id: $check_id, verdict: $verdict, reason: $reason, fix: {explanation: $explanation, edits: $edits}}'
  elif [[ "$verdict" == "NEEDS_CONTEXT" ]]; then
    jq -cn \
      --arg finding_id "$finding_id" \
      --arg file "$file" \
      --argjson line "$line" \
      --arg check_id "$check_id" \
      --arg verdict "$verdict" \
      --arg reason "$reason" \
      --arg question "$question" \
      '{finding_id: $finding_id, file: $file, line: $line, check_id: $check_id, verdict: $verdict, reason: $reason, question: $question}'
  else
    # FALSE_POSITIVE
    jq -cn \
      --arg finding_id "$finding_id" \
      --arg file "$file" \
      --argjson line "$line" \
      --arg check_id "$check_id" \
      --arg verdict "$verdict" \
      --arg reason "$reason" \
      '{finding_id: $finding_id, file: $file, line: $line, check_id: $check_id, verdict: $verdict, reason: $reason}'
  fi
}

# Batch mode: read JSON array from stdin
process_stdin() {
  local output_file=$(get_output_file)
  local input=$(cat)

  # Check if input is valid JSON array
  if ! echo "$input" | jq -e 'type == "array"' > /dev/null 2>&1; then
    error "Input must be a JSON array"
  fi

  # Process each object in the array
  local total=$(echo "$input" | jq 'length')
  local confirmed=0
  local false_pos=0
  local needs_ctx=0

  for ((i=0; i<total; i++)); do
    local verdict_obj=$(echo "$input" | jq -c ".[$i]")
    local validated
    if ! validated=$(validate_verdict "$verdict_obj"); then
      error "Validation failed for item $i"
    fi
    echo "$validated" >> "$output_file"

    # Count by verdict type
    local v=$(echo "$validated" | jq -r '.verdict')
    case "$v" in
      CONFIRMED) ((confirmed++)) ;;
      FALSE_POSITIVE) ((false_pos++)) ;;
      NEEDS_CONTEXT) ((needs_ctx++)) ;;
    esac
  done

  echo "Added $total verdicts ($confirmed confirmed, $false_pos false positives, $needs_ctx need context)"
}

# Single mode: parse CLI args (only for FALSE_POSITIVE and NEEDS_CONTEXT)
process_single() {
  local FINDING_ID=""
  local FILE=""
  local LINE=""
  local CHECK_ID=""
  local VERDICT=""
  local REASON=""
  local QUESTION=""

  while [[ $# -gt 0 ]]; do
    case $1 in
      --finding-id) FINDING_ID="$2"; shift 2 ;;
      --file) FILE="$2"; shift 2 ;;
      --line) LINE="$2"; shift 2 ;;
      --check-id) CHECK_ID="$2"; shift 2 ;;
      --verdict) VERDICT="$2"; shift 2 ;;
      --reason) REASON="$2"; shift 2 ;;
      --question) QUESTION="$2"; shift 2 ;;
      --output) OUTPUT="$2"; shift 2 ;;
      -h|--help) usage ;;
      *) error "Unknown option: $1" ;;
    esac
  done

  # CLI mode doesn't support CONFIRMED (requires fix.edits array)
  if [[ "$VERDICT" == "CONFIRMED" ]]; then
    error "CONFIRMED verdicts require batch mode (--stdin) with fix.edits array"
  fi

  # Build JSON from args
  local json=$(jq -n \
    --arg finding_id "$FINDING_ID" \
    --arg file "$FILE" \
    --arg line "$LINE" \
    --arg check_id "$CHECK_ID" \
    --arg verdict "$VERDICT" \
    --arg reason "$REASON" \
    --arg question "$QUESTION" \
    '{finding_id: $finding_id, file: $file, line: $line, check_id: $check_id, verdict: $verdict, reason: $reason, question: $question}')

  local validated
  if ! validated=$(validate_verdict "$json"); then
    exit 1
  fi
  local output_file=$(get_output_file)

  echo "$validated" >> "$output_file"
  echo "Added $VERDICT for $CHECK_ID at $FILE:$LINE"
}

usage() {
  cat <<EOF
Usage:
  CLI:   add-verdict.sh --finding-id <id> --file <path> --line <n> --check-id <id> --verdict <v> --reason <text> [options]
  Batch: cat verdicts.json | add-verdict.sh --stdin

CLI mode (FALSE_POSITIVE and NEEDS_CONTEXT only):
  --finding-id <id>   Original finding ID (e.g., "batch-2-NULL-4")
  --file <path>       File path where finding was found
  --line <n>          Line number
  --check-id <id>     Check ID (e.g., NULL-4)
  --verdict <v>       FALSE_POSITIVE or NEEDS_CONTEXT
  --reason <text>     Why this verdict was reached
  --question <text>   For NEEDS_CONTEXT: what info is missing
  --output <path>     Output file (default: \$BASE_DIR/verdicts.jsonl)

Batch mode (required for CONFIRMED):
  --stdin             Read JSON array from stdin

Batch JSON format:
  [
    {
      "finding_id": "batch-1-NULL-4",
      "file": "src/api.ts",
      "line": 42,
      "check_id": "NULL-4",
      "verdict": "CONFIRMED",
      "reason": "Array accessed without bounds check",
      "fix": {
        "explanation": "Add bounds check",
        "edits": [
          {"file": "src/api.ts", "old_string": "items[0]", "new_string": "items?.[0]"}
        ]
      }
    },
    {
      "finding_id": "batch-1-ERR-3",
      "file": "src/api.ts",
      "line": 50,
      "check_id": "ERR-3",
      "verdict": "FALSE_POSITIVE",
      "reason": "Error handled by caller"
    }
  ]

Note: CONFIRMED requires batch mode with fix.edits array (supports multi-file fixes).

EOF
  exit 1
}

# Main
OUTPUT=""

# Check for --stdin first
if [[ "$1" == "--stdin" ]]; then
  shift
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
