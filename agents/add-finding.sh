#!/bin/bash
# add-finding.sh - Checker agents use this to add findings
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
    echo "$BASE_DIR/findings.jsonl"
  else
    error "Either --output or \$BASE_DIR must be set"
  fi
}

# Validate a single finding JSON object, returns validated JSON or exits
validate_finding() {
  local json="$1"

  # Extract fields
  local batch=$(echo "$json" | jq -r '.batch // empty')
  local unit=$(echo "$json" | jq -r '.unit // empty')
  local file=$(echo "$json" | jq -r '.file // empty')
  local check_id=$(echo "$json" | jq -r '.check_id // empty')
  local verdict=$(echo "$json" | jq -r '.verdict // empty')
  local line=$(echo "$json" | jq -r '.line // empty')
  local issue=$(echo "$json" | jq -r '.issue // empty')
  local reason=$(echo "$json" | jq -r '.reason // empty')
  local confidence=$(echo "$json" | jq -r '.confidence // "HIGH"')

  # Validate required fields
  [[ -z "$batch" ]] && error "Missing required: batch"
  [[ -z "$unit" ]] && error "Missing required: unit"
  [[ -z "$file" ]] && error "Missing required: file"
  [[ -z "$check_id" ]] && error "Missing required: check_id"
  [[ -z "$verdict" ]] && error "Missing required: verdict"

  # Validate batch is integer or string (for prefix groups like "GC")
  if [[ ! "$batch" =~ ^[0-9]+$ && ! "$batch" =~ ^[A-Z]+$ ]]; then
    error "batch must be an integer or prefix string, got: $batch"
  fi

  # Validate verdict enum
  case "$verdict" in
    PASS|FINDING|N/A) ;;
    *) error "verdict must be PASS, FINDING, or N/A, got: $verdict" ;;
  esac

  # Validate verdict-specific requirements
  if [[ "$verdict" == "FINDING" ]]; then
    [[ -z "$line" ]] && error "FINDING requires line"
    [[ -z "$issue" ]] && error "FINDING requires issue"
    [[ ! "$line" =~ ^[0-9]+$ ]] && error "line must be an integer, got: $line"
  fi

  if [[ "$verdict" == "N/A" ]]; then
    [[ -z "$reason" ]] && error "N/A requires reason"
  fi

  # Validate confidence enum if provided
  case "$confidence" in
    HIGH|MEDIUM|LOW) ;;
    *) error "confidence must be HIGH, MEDIUM, or LOW, got: $confidence" ;;
  esac

  # Build normalized JSON based on verdict (compact for JSONL)
  if [[ "$verdict" == "FINDING" ]]; then
    jq -cn \
      --arg batch "$batch" \
      --arg unit "$unit" \
      --arg file "$file" \
      --arg check_id "$check_id" \
      --arg verdict "$verdict" \
      --argjson line "$line" \
      --arg issue "$issue" \
      --arg confidence "$confidence" \
      '{batch: $batch, unit: $unit, file: $file, check_id: $check_id, verdict: $verdict, line: $line, issue: $issue, confidence: $confidence}'
  elif [[ "$verdict" == "N/A" ]]; then
    jq -cn \
      --arg batch "$batch" \
      --arg unit "$unit" \
      --arg file "$file" \
      --arg check_id "$check_id" \
      --arg verdict "$verdict" \
      --arg reason "$reason" \
      '{batch: $batch, unit: $unit, file: $file, check_id: $check_id, verdict: $verdict, reason: $reason}'
  else
    # PASS
    jq -cn \
      --arg batch "$batch" \
      --arg unit "$unit" \
      --arg file "$file" \
      --arg check_id "$check_id" \
      --arg verdict "$verdict" \
      '{batch: $batch, unit: $unit, file: $file, check_id: $check_id, verdict: $verdict}'
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
  local findings_count=0
  local passes_count=0
  local na_count=0

  for ((i=0; i<total; i++)); do
    local finding=$(echo "$input" | jq -c ".[$i]")
    local validated
    if ! validated=$(validate_finding "$finding"); then
      error "Validation failed for item $i"
    fi
    echo "$validated" >> "$output_file"

    # Count by verdict type
    local v=$(echo "$validated" | jq -r '.verdict')
    case "$v" in
      FINDING) ((findings_count++)) ;;
      PASS) ((passes_count++)) ;;
      N/A) ((na_count++)) ;;
    esac
  done

  echo "Added $total results ($findings_count findings, $passes_count passes, $na_count n/a)"
}

# Single mode: parse CLI args
process_single() {
  local BATCH=""
  local UNIT=""
  local FILE=""
  local CHECK_ID=""
  local VERDICT=""
  local LINE=""
  local ISSUE=""
  local REASON=""
  local CONFIDENCE="HIGH"

  while [[ $# -gt 0 ]]; do
    case $1 in
      --batch) BATCH="$2"; shift 2 ;;
      --unit) UNIT="$2"; shift 2 ;;
      --file) FILE="$2"; shift 2 ;;
      --check-id) CHECK_ID="$2"; shift 2 ;;
      --verdict) VERDICT="$2"; shift 2 ;;
      --line) LINE="$2"; shift 2 ;;
      --issue) ISSUE="$2"; shift 2 ;;
      --reason) REASON="$2"; shift 2 ;;
      --confidence) CONFIDENCE="$2"; shift 2 ;;
      --output) OUTPUT="$2"; shift 2 ;;
      -h|--help) usage ;;
      *) error "Unknown option: $1" ;;
    esac
  done

  # Build JSON from args
  local json=$(jq -n \
    --arg batch "$BATCH" \
    --arg unit "$UNIT" \
    --arg file "$FILE" \
    --arg check_id "$CHECK_ID" \
    --arg verdict "$VERDICT" \
    --arg line "$LINE" \
    --arg issue "$ISSUE" \
    --arg reason "$REASON" \
    --arg confidence "$CONFIDENCE" \
    '{batch: $batch, unit: $unit, file: $file, check_id: $check_id, verdict: $verdict, line: $line, issue: $issue, reason: $reason, confidence: $confidence}')

  local validated
  if ! validated=$(validate_finding "$json"); then
    exit 1
  fi
  local output_file=$(get_output_file)

  echo "$validated" >> "$output_file"
  echo "Added $VERDICT for $CHECK_ID on $UNIT ($FILE)"
}

usage() {
  cat <<EOF
Usage:
  Single: add-finding.sh --batch <n> --unit <name> --file <path> --check-id <id> --verdict <v> [options]
  Batch:  cat findings.json | add-finding.sh --stdin

Single mode options:
  --batch <n>         Batch number or prefix (e.g., 1, "GC")
  --unit <name>       Unit name (function/class/method)
  --file <path>       File path
  --check-id <id>     Check ID (e.g., NULL-4, ERR-3)
  --verdict <v>       PASS, FINDING, or N/A

  Required if verdict=FINDING:
    --line <n>        Line number
    --issue <text>    Issue description

  Required if verdict=N/A:
    --reason <text>   Why check doesn't apply

  Optional:
    --confidence <v>  HIGH, MEDIUM, or LOW (default: HIGH)
    --output <path>   Output file (default: \$BASE_DIR/findings.jsonl)

Batch mode:
  --stdin             Read JSON array from stdin

Batch JSON format:
  [
    {"batch": 1, "unit": "createUser", "file": "src/api.ts", "check_id": "ERR-3", "verdict": "PASS"},
    {"batch": 1, "unit": "createUser", "file": "src/api.ts", "check_id": "NULL-4", "verdict": "FINDING", "line": 42, "issue": "No bounds check"}
  ]

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
