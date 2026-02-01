#!/bin/bash
# add-verdict.sh - Investigation agents use this to add verified findings with fixes
# Enforces schema. Exits non-zero if validation fails.
# CLI args only - one call per verdict (debuggable, simple)
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

# Parse CLI args and record verdict
process_single() {
  local FINDING_ID=""
  local FILE=""
  local LINE=""
  local CHECK_ID=""
  local VERDICT=""
  local REASON=""
  local QUESTION=""
  local FIX_EXPLANATION=""
  local FIX_EDITS=""

  while [[ $# -gt 0 ]]; do
    case $1 in
      --finding-id) FINDING_ID="$2"; shift 2 ;;
      --file) FILE="$2"; shift 2 ;;
      --line) LINE="$2"; shift 2 ;;
      --check-id) CHECK_ID="$2"; shift 2 ;;
      --verdict) VERDICT="$2"; shift 2 ;;
      --reason) REASON="$2"; shift 2 ;;
      --question) QUESTION="$2"; shift 2 ;;
      --fix-explanation) FIX_EXPLANATION="$2"; shift 2 ;;
      --fix-edits) FIX_EDITS="$2"; shift 2 ;;
      --output) OUTPUT="$2"; shift 2 ;;
      -h|--help) usage ;;
      *) error "Unknown option: $1" ;;
    esac
  done

  # CONFIRMED requires fix args
  if [[ "$VERDICT" == "CONFIRMED" ]]; then
    [[ -z "$FIX_EXPLANATION" ]] && error "CONFIRMED requires --fix-explanation"
    [[ -z "$FIX_EDITS" ]] && error "CONFIRMED requires --fix-edits (JSON array)"
    # Validate fix-edits is valid JSON array
    if ! echo "$FIX_EDITS" | jq -e 'type == "array"' > /dev/null 2>&1; then
      error "--fix-edits must be a JSON array"
    fi
  fi

  # Build JSON from args
  local json
  if [[ "$VERDICT" == "CONFIRMED" ]]; then
    json=$(jq -n \
      --arg finding_id "$FINDING_ID" \
      --arg file "$FILE" \
      --arg line "$LINE" \
      --arg check_id "$CHECK_ID" \
      --arg verdict "$VERDICT" \
      --arg reason "$REASON" \
      --arg explanation "$FIX_EXPLANATION" \
      --argjson edits "$FIX_EDITS" \
      '{finding_id: $finding_id, file: $file, line: $line, check_id: $check_id, verdict: $verdict, reason: $reason, fix: {explanation: $explanation, edits: $edits}}')
  else
    json=$(jq -n \
      --arg finding_id "$FINDING_ID" \
      --arg file "$FILE" \
      --arg line "$LINE" \
      --arg check_id "$CHECK_ID" \
      --arg verdict "$VERDICT" \
      --arg reason "$REASON" \
      --arg question "$QUESTION" \
      '{finding_id: $finding_id, file: $file, line: $line, check_id: $check_id, verdict: $verdict, reason: $reason, question: $question}')
  fi

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
  add-verdict.sh --finding-id <id> --file <path> --line <n> --check-id <id> --verdict <v> --reason <text> [options]

Required:
  --finding-id <id>       Original finding ID (e.g., "batch-2-NULL-4")
  --file <path>           File path where finding was found
  --line <n>              Line number
  --check-id <id>         Check ID (e.g., NULL-4)
  --verdict <v>           CONFIRMED, FALSE_POSITIVE, or NEEDS_CONTEXT
  --reason <text>         Why this verdict was reached

Conditional:
  CONFIRMED requires:
    --fix-explanation <text>   What the fix does
    --fix-edits <json>         JSON array of edits

  NEEDS_CONTEXT requires:
    --question <text>          What info is missing

Optional:
  --output <path>         Output file (default: \$BASE_DIR/verdicts.jsonl)

Examples:
  # FALSE_POSITIVE
  add-verdict.sh --finding-id "batch-1-ERR-3" --file "src/api.ts" --line 50 \\
    --check-id "ERR-3" --verdict "FALSE_POSITIVE" --reason "Error handled by caller"

  # NEEDS_CONTEXT
  add-verdict.sh --finding-id "batch-1-CONC-2" --file "src/api.ts" --line 60 \\
    --check-id "CONC-2" --verdict "NEEDS_CONTEXT" --reason "Unclear threading model" \\
    --question "Is this service accessed concurrently?"

  # CONFIRMED (single file fix)
  add-verdict.sh --finding-id "batch-1-NULL-4" --file "src/api.ts" --line 42 \\
    --check-id "NULL-4" --verdict "CONFIRMED" --reason "Array accessed without bounds check" \\
    --fix-explanation "Add bounds check" \\
    --fix-edits '[{"file":"src/api.ts","old_string":"items[0]","new_string":"items?.[0]"}]'

  # CONFIRMED (multi-file fix)
  add-verdict.sh --finding-id "batch-1-API-2" --file "src/utils.ts" --line 10 \\
    --check-id "API-2" --verdict "CONFIRMED" --reason "Function renamed but callers not updated" \\
    --fix-explanation "Rename function and update call sites" \\
    --fix-edits '[{"file":"src/utils.ts","old_string":"export function oldName(","new_string":"export function newName("},{"file":"src/api.ts","old_string":"oldName(data)","new_string":"newName(data)"}]'

EOF
  exit 1
}

# Main
OUTPUT=""

if [[ "$1" == "-h" || "$1" == "--help" || -z "$1" ]]; then
  usage
else
  process_single "$@"
fi
