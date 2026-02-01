#!/bin/bash
# add-finding.sh - Checker agents use this to add findings
# Enforces schema. Exits non-zero if validation fails.

set -e

# Required args
BATCH=""
UNIT=""
FILE=""
CHECK_ID=""
VERDICT=""

# Optional args
LINE=""
ISSUE=""
REASON=""
CONFIDENCE=""

usage() {
  cat <<EOF
Usage: add-finding.sh --batch <n> --unit <name> --file <path> --check-id <id> --verdict <PASS|FINDING|N/A> [options]

Required:
  --batch <n>         Batch number (integer)
  --unit <name>       Unit name (function/class/method)
  --file <path>       File path
  --check-id <id>     Check ID (e.g., NULL-4, ERR-3)
  --verdict <v>       PASS, FINDING, or N/A

Required if verdict=FINDING:
  --line <n>          Line number
  --issue <text>      Issue description

Required if verdict=N/A:
  --reason <text>     Why check doesn't apply

Optional:
  --confidence <v>    HIGH, MEDIUM, or LOW (default: HIGH)
  --output <path>     Output file (default: \$BASE_DIR/findings.jsonl)

EOF
  exit 1
}

error() {
  echo "ERROR: $1" >&2
  exit 1
}

# Parse args
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

# Validate required fields
[[ -z "$BATCH" ]] && error "Missing required: --batch"
[[ -z "$UNIT" ]] && error "Missing required: --unit"
[[ -z "$FILE" ]] && error "Missing required: --file"
[[ -z "$CHECK_ID" ]] && error "Missing required: --check-id"
[[ -z "$VERDICT" ]] && error "Missing required: --verdict"

# Validate batch is integer
[[ ! "$BATCH" =~ ^[0-9]+$ ]] && error "--batch must be an integer, got: $BATCH"

# Validate verdict enum
case "$VERDICT" in
  PASS|FINDING|N/A) ;;
  *) error "--verdict must be PASS, FINDING, or N/A, got: $VERDICT" ;;
esac

# Validate verdict-specific requirements
if [[ "$VERDICT" == "FINDING" ]]; then
  [[ -z "$LINE" ]] && error "FINDING requires --line"
  [[ -z "$ISSUE" ]] && error "FINDING requires --issue"
  [[ ! "$LINE" =~ ^[0-9]+$ ]] && error "--line must be an integer, got: $LINE"
fi

if [[ "$VERDICT" == "N/A" ]]; then
  [[ -z "$REASON" ]] && error "N/A requires --reason"
fi

# Validate confidence enum if provided
if [[ -n "$CONFIDENCE" ]]; then
  case "$CONFIDENCE" in
    HIGH|MEDIUM|LOW) ;;
    *) error "--confidence must be HIGH, MEDIUM, or LOW, got: $CONFIDENCE" ;;
  esac
else
  CONFIDENCE="HIGH"
fi

# Determine output file
if [[ -z "$OUTPUT" ]]; then
  if [[ -z "$BASE_DIR" ]]; then
    error "Either --output or \$BASE_DIR must be set"
  fi
  OUTPUT="$BASE_DIR/findings.jsonl"
fi

# Build JSON based on verdict
if [[ "$VERDICT" == "FINDING" ]]; then
  JSON=$(jq -n \
    --argjson batch "$BATCH" \
    --arg unit "$UNIT" \
    --arg file "$FILE" \
    --arg check_id "$CHECK_ID" \
    --arg verdict "$VERDICT" \
    --argjson line "$LINE" \
    --arg issue "$ISSUE" \
    --arg confidence "$CONFIDENCE" \
    '{batch: $batch, unit: $unit, file: $file, check_id: $check_id, verdict: $verdict, line: $line, issue: $issue, confidence: $confidence}')
elif [[ "$VERDICT" == "N/A" ]]; then
  JSON=$(jq -n \
    --argjson batch "$BATCH" \
    --arg unit "$UNIT" \
    --arg file "$FILE" \
    --arg check_id "$CHECK_ID" \
    --arg verdict "$VERDICT" \
    --arg reason "$REASON" \
    '{batch: $batch, unit: $unit, file: $file, check_id: $check_id, verdict: $verdict, reason: $reason}')
else
  # PASS
  JSON=$(jq -n \
    --argjson batch "$BATCH" \
    --arg unit "$UNIT" \
    --arg file "$FILE" \
    --arg check_id "$CHECK_ID" \
    --arg verdict "$VERDICT" \
    '{batch: $batch, unit: $unit, file: $file, check_id: $check_id, verdict: $verdict}')
fi

# Append to output file
echo "$JSON" >> "$OUTPUT"
echo "Added $VERDICT for $CHECK_ID on $UNIT ($FILE)"
