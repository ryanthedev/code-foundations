#!/usr/bin/env bash
#
# Extract semantic units (functions, classes) from code using tree-sitter CLI.
#
# Usage:
#   ./extract-units.sh [--staged | --files file1 file2 | <git-diff-args>]
#   ./extract-units.sh --status   # Check tree-sitter availability
#
# Output: JSON with:
#   - units: extracted functions/classes/etc
#   - fallback_files: files that need LLM extraction (unsupported/missing grammar)
#
# If tree-sitter CLI not installed, outputs all files in fallback_files.
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check tree-sitter availability
check_status() {
  local ts_version parsers_count

  if ! command -v tree-sitter &>/dev/null; then
    echo '{"available": false, "error": "tree-sitter CLI not found"}'
    exit 0
  fi

  ts_version=$(tree-sitter --version 2>/dev/null | awk '{print $2}')

  # Count available parsers by checking which languages parse successfully
  parsers_count=0
  for lang in javascript typescript python go rust java ruby c cpp; do
    if tree-sitter parse --quiet /dev/null --scope "source.$lang" 2>/dev/null; then
      ((parsers_count++)) || true
    fi
  done

  echo "{\"available\": true, \"version\": \"$ts_version\", \"parsers\": $parsers_count}"
  exit 0
}

# Get file extension to language scope mapping
get_scope() {
  local file="$1"
  case "${file##*.}" in
    js|mjs|cjs) echo "source.js" ;;
    ts) echo "source.ts" ;;
    tsx) echo "source.tsx" ;;
    jsx) echo "source.jsx" ;;
    py) echo "source.python" ;;
    go) echo "source.go" ;;
    rs) echo "source.rust" ;;
    java) echo "source.java" ;;
    rb) echo "source.ruby" ;;
    c|h) echo "source.c" ;;
    cpp|cc|cxx|hpp) echo "source.cpp" ;;
    *) echo "" ;;
  esac
}

# Grammar directory (where tree-sitter grammars are cloned)
GRAMMAR_DIR="${TREE_SITTER_GRAMMAR_DIR:-$HOME/repos/tree-sitter-grammars}"

# Get query file for a language - prefer official tags.scm from grammar repos
get_query_file() {
  local scope="$1"
  local lang="${scope#source.}"

  # Map scope to grammar directory name
  # Note: TypeScript uses JavaScript queries for code constructs
  local grammar_name
  case "$lang" in
    js|ts|tsx) grammar_name="javascript" ;;  # TS inherits JS queries
    python) grammar_name="python" ;;
    *) grammar_name="$lang" ;;
  esac

  # Use official tags.scm from grammar repo
  local official_tags="$GRAMMAR_DIR/tree-sitter-$grammar_name/queries/tags.scm"
  if [[ -f "$official_tags" ]]; then
    echo "$official_tags"
  else
    echo ""  # No query file -> will use LLM fallback
  fi
}

# Extract units from a single file
extract_file() {
  local file="$1"
  local scope query_file

  scope=$(get_scope "$file")
  [[ -z "$scope" ]] && return

  query_file=$(get_query_file "$scope")
  [[ -z "$query_file" ]] && return

  # Run tree-sitter query and parse output
  local output type name start_line end_line first=true

  while IFS= read -r line; do
    # Capture type from "capture: definition.function" or "capture: function"
    # Matches: "definition.function", "definition.method", "definition.class", etc.
    if [[ "$line" =~ capture:\ (definition\.)?(function|method|class|interface|test),\ start:\ \(([0-9]+), ]]; then
      type="${BASH_REMATCH[2]}"
      start_line=$(( ${BASH_REMATCH[3]} + 1 ))
    fi

    # Also capture end from same line "end: (row,"
    if [[ "$line" =~ capture:\ (definition\.)?(function|method|class|interface|test),.*end:\ \(([0-9]+), ]]; then
      end_line=$(( ${BASH_REMATCH[3]} + 1 ))
    fi

    # Capture name from "text: `name`"
    if [[ "$line" =~ text:\ \`([^\`]+)\` ]]; then
      name="${BASH_REMATCH[1]}"

      # Output unit if we have all fields (name line comes after type line)
      if [[ -n "$type" && -n "$name" && -n "$start_line" && -n "$end_line" ]]; then
        if [[ "$first" != "true" ]]; then
          printf ","
        fi
        printf '{"type":"%s","name":"%s","file":"%s","lines":[%d,%d]}' \
          "$type" "$name" "$file" "$start_line" "$end_line"
        first=false
        type="" name="" start_line="" end_line=""
      fi
    fi
  done < <(tree-sitter query "$query_file" "$file" --scope "$scope" 2>/dev/null)
}

# Analyze a unit for characteristics
analyze_characteristics() {
  local file="$1"
  local start_line="$2"
  local end_line="$3"

  # Extract the code block
  local code
  code=$(sed -n "${start_line},${end_line}p" "$file" 2>/dev/null || echo "")

  # Detect characteristics
  local has_loops=false has_try_catch=false has_async=false
  local has_io_calls=false has_input_params=false

  # Loops
  if echo "$code" | grep -qE '\b(for|while|forEach|map|reduce|filter)\b'; then
    has_loops=true
  fi

  # Try/catch
  if echo "$code" | grep -qE '\b(try|catch|except|rescue|finally)\b'; then
    has_try_catch=true
  fi

  # Async
  if echo "$code" | grep -qE '\b(async|await|Promise)\b'; then
    has_async=true
  fi

  # I/O calls
  if echo "$code" | grep -qE '\b(fetch|axios|http|fs\.|readFile|writeFile|query|execute|connect)\b'; then
    has_io_calls=true
  fi

  # Nesting depth (approximate)
  local max_indent=0 line_indent
  while IFS= read -r line; do
    line_indent=$(echo "$line" | sed 's/[^ \t].*//' | wc -c)
    ((line_indent > max_indent)) && max_indent=$line_indent
  done <<< "$code"
  local nesting_depth=$((max_indent / 2))
  ((nesting_depth > 10)) && nesting_depth=10

  echo "{\"has_loops\":$has_loops,\"has_try_catch\":$has_try_catch,\"has_async\":$has_async,\"has_io_calls\":$has_io_calls,\"nesting_depth\":$nesting_depth}"
}

# Get changed files based on arguments
get_files() {
  local args=("$@")

  if [[ ${#args[@]} -eq 0 ]]; then
    # Default: unstaged changes
    git diff --name-only 2>/dev/null
  elif [[ "${args[0]}" == "--staged" ]]; then
    git diff --cached --name-only 2>/dev/null
  elif [[ "${args[0]}" == "--files" ]]; then
    # Explicit file list
    printf '%s\n' "${args[@]:1}"
  else
    # Pass through to git diff
    git diff --name-only "${args[@]}" 2>/dev/null
  fi
}

# Check if we can parse a file (grammar available)
can_parse_file() {
  local file="$1"
  local scope

  scope=$(get_scope "$file")
  [[ -z "$scope" ]] && return 1

  # Try to parse the file - if it works, grammar is available
  tree-sitter parse --quiet "$file" --scope "$scope" 2>/dev/null
}

# Main
main() {
  # Handle --status flag
  [[ "${1:-}" == "--status" ]] && check_status

  local files
  files=$(get_files "$@")

  # Track files needing LLM fallback
  local fallback_files=()
  local ts_available=true

  # Check if tree-sitter is available
  if ! command -v tree-sitter &>/dev/null; then
    ts_available=false
  fi

  # Collect units and fallback files
  local units_output=""
  local first=true

  while IFS= read -r file; do
    [[ -z "$file" ]] && continue
    [[ ! -f "$file" ]] && continue

    # Skip non-code files
    local scope
    scope=$(get_scope "$file")
    if [[ -z "$scope" ]]; then
      # Check if it's a code file we don't support yet
      case "${file##*.}" in
        md|json|yaml|yml|txt|lock|toml) continue ;;  # Skip config/doc files
        *) fallback_files+=("$file") ;;  # Unknown code file -> fallback
      esac
      continue
    fi

    # If tree-sitter not available, all code files need fallback
    if [[ "$ts_available" != "true" ]]; then
      fallback_files+=("$file")
      continue
    fi

    # Check if we have the query file for this language
    local query_file
    query_file=$(get_query_file "$scope")
    if [[ -z "$query_file" ]]; then
      fallback_files+=("$file")
      continue
    fi

    # Check if grammar is available by trying to parse
    if ! can_parse_file "$file"; then
      fallback_files+=("$file")
      continue
    fi

    # Extract units from this file
    local file_units
    file_units=$(extract_file "$file")

    if [[ -n "$file_units" ]]; then
      if [[ "$first" != "true" ]]; then
        units_output+=","
      fi
      units_output+="$file_units"
      first=false
    fi
  done <<< "$files"

  # Build fallback files JSON array
  local fallback_json="["
  local fb_first=true
  if [[ ${#fallback_files[@]} -gt 0 ]]; then
    for fb in "${fallback_files[@]}"; do
      if [[ "$fb_first" != "true" ]]; then
        fallback_json+=","
      fi
      fallback_json+="\"$fb\""
      fb_first=false
    done
  fi
  fallback_json+="]"

  # Output final JSON
  echo "{\"units\":[$units_output],\"fallback_files\":$fallback_json,\"tree_sitter_available\":$ts_available}"
}

main "$@"
