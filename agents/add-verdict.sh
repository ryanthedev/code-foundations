#!/bin/bash
# add-verdict.sh - Investigation agents use this to add verified findings with fixes
# Enforces schema. Exits non-zero if validation fails.

set -e

# Required args
FINDING_ID=""
FILE=""
LINE=""
CHECK_ID=""
VERDICT=""

# Optional/conditional args
REASON=""
EXPLANATION=""
OLD_STRING=""
NEW_STRING=""

usage() {
  cat <<EOF
Usage: add-verdict.sh --finding-id <id> --file <path> --line <n> --check-id <id> --verdict <v> [options]

Required:
  --finding-id <id>   Original finding ID (e.g., "batch-2-NULL-4")
  --file <path>       File path
  --line <n>          Line number
  --check-id <id>     Check ID (e.g., NULL-4)
  --verdict <v>       CONFIRMED, FALSE_POSITIVE, or NEEDS_CONTEXT

Required for all verdicts:
  --reason <text>     Why this verdict was reached

Required if verdict=CONFIRMED:
  --explanation <text>  What the fix does
  --old-string <text>   Code to replace (for Edit tool)
  --new-string <text>   Replacement code (for Edit tool)

Optional:
  --question <text>   For NEEDS_CONTEXT: what info is missing
  --output <path>     Output file (default: \$BASE_DIR/verdicts.jsonl)

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
    --finding-id) FINDING_ID="$2"; shift 2 ;;
    --file) FILE="$2"; shift 2 ;;
    --line) LINE="$2"; shift 2 ;;
    --check-id) CHECK_ID="$2"; shift 2 ;;
    --verdict) VERDICT="$2"; shift 2 ;;
    --reason) REASON="$2"; shift 2 ;;
    --explanation) EXPLANATION="$2"; shift 2 ;;
    --old-string) OLD_STRING="$2"; shift 2 ;;
    --new-string) NEW_STRING="$2"; shift 2 ;;
    --question) QUESTION="$2"; shift 2 ;;
    --output) OUTPUT="$2"; shift 2 ;;
    -h|--help) usage ;;
    *) error "Unknown option: $1" ;;
  esac
done

# Validate required fields
[[ -z "$FINDING_ID" ]] && error "Missing required: --finding-id"
[[ -z "$FILE" ]] && error "Missing required: --file"
[[ -z "$LINE" ]] && error "Missing required: --line"
[[ -z "$CHECK_ID" ]] && error "Missing required: --check-id"
[[ -z "$VERDICT" ]] && error "Missing required: --verdict"
[[ -z "$REASON" ]] && error "Missing required: --reason"

# Validate line is integer
[[ ! "$LINE" =~ ^[0-9]+$ ]] && error "--line must be an integer, got: $LINE"

# Validate verdict enum
case "$VERDICT" in
  CONFIRMED|FALSE_POSITIVE|NEEDS_CONTEXT) ;;
  *) error "--verdict must be CONFIRMED, FALSE_POSITIVE, or NEEDS_CONTEXT, got: $VERDICT" ;;
esac

# Validate CONFIRMED requires fix fields
if [[ "$VERDICT" == "CONFIRMED" ]]; then
  [[ -z "$EXPLANATION" ]] && error "CONFIRMED requires --explanation"
  [[ -z "$OLD_STRING" ]] && error "CONFIRMED requires --old-string"
  [[ -z "$NEW_STRING" ]] && error "CONFIRMED requires --new-string"
fi

# Determine output file
if [[ -z "$OUTPUT" ]]; then
  if [[ -z "$BASE_DIR" ]]; then
    error "Either --output or \$BASE_DIR must be set"
  fi
  OUTPUT="$BASE_DIR/verdicts.jsonl"
fi

# Build JSON based on verdict
if [[ "$VERDICT" == "CONFIRMED" ]]; then
  JSON=$(jq -n \
    --arg finding_id "$FINDING_ID" \
    --arg file "$FILE" \
    --argjson line "$LINE" \
    --arg check_id "$CHECK_ID" \
    --arg verdict "$VERDICT" \
    --arg reason "$REASON" \
    --arg explanation "$EXPLANATION" \
    --arg old_string "$OLD_STRING" \
    --arg new_string "$NEW_STRING" \
    '{finding_id: $finding_id, file: $file, line: $line, check_id: $check_id, verdict: $verdict, reason: $reason, fix: {explanation: $explanation, old_string: $old_string, new_string: $new_string}}')
elif [[ "$VERDICT" == "NEEDS_CONTEXT" ]]; then
  JSON=$(jq -n \
    --arg finding_id "$FINDING_ID" \
    --arg file "$FILE" \
    --argjson line "$LINE" \
    --arg check_id "$CHECK_ID" \
    --arg verdict "$VERDICT" \
    --arg reason "$REASON" \
    --arg question "${QUESTION:-}" \
    '{finding_id: $finding_id, file: $file, line: $line, check_id: $check_id, verdict: $verdict, reason: $reason, question: $question}')
else
  # FALSE_POSITIVE
  JSON=$(jq -n \
    --arg finding_id "$FINDING_ID" \
    --arg file "$FILE" \
    --argjson line "$LINE" \
    --arg check_id "$CHECK_ID" \
    --arg verdict "$VERDICT" \
    --arg reason "$REASON" \
    '{finding_id: $finding_id, file: $file, line: $line, check_id: $check_id, verdict: $verdict, reason: $reason}')
fi

# Append to output file
echo "$JSON" >> "$OUTPUT"
echo "Added $VERDICT for $CHECK_ID at $FILE:$LINE"
