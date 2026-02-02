#!/usr/bin/env bash
#
# Extract semantic units from changed files with diff context.
#
# Usage:
#   ./extract-with-diff.sh [<git-diff-args>]
#   ./extract-with-diff.sh --staged
#   ./extract-with-diff.sh main..feature-branch
#
# Output: JSONL (one JSON object per line) with:
#   - All fields from extract-units.sh
#   - diff: unified diff hunks for this unit
#   - changeStatus: added, modified, or deleted
#   - summary: heuristic description of changes
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXTRACT_UNITS="$SCRIPT_DIR/extract-units.sh"

# Field delimiter (unit separator ASCII 31, won't appear in code)
DELIM=$'\x1f'

# Parse command line arguments to extract git-diff-args
parse_args() {
  # All arguments are passed to git diff
  printf '%s\n' "$@"
}

# Get the list of changed files with their change status
get_file_statuses() {
  local -a git_args=("$@")

  if [[ ${#git_args[@]} -eq 0 ]]; then
    # Default: unstaged changes
    git diff --name-status 2>/dev/null || {
      echo "Error: git diff failed" >&2
      exit 1
    }
  else
    git diff --name-status "${git_args[@]}" 2>/dev/null || {
      echo "Error: git diff failed with args: ${git_args[*]}" >&2
      exit 1
    }
  fi
}

# Map git status letter to semantic change status
get_change_status() {
  local status="$1"

  case "$status" in
    A)
      echo "added"
      ;;
    M)
      echo "modified"
      ;;
    D)
      echo "deleted"
      ;;
    R*)
      # Handle rename with or without percentage (R, R100, R095, etc.)
      echo "modified"
      ;;
    *)
      # Default to modified for unknown statuses (C, T, U, X)
      echo "modified"
      ;;
  esac
}

# Determine if a unit's line range overlaps with a hunk's line range
overlaps() {
  local unit_start="$1"
  local unit_end="$2"
  local hunk_start="$3"
  local hunk_end="$4"

  if (( unit_start <= hunk_end && unit_end >= hunk_start )); then
    return 0  # true
  fi

  return 1  # false
}

# Generate a brief summary of what changed in a unit
generate_summary() {
  local name="$1"
  local diff_content="$2"

  # Count lines starting with "+" but not "++"
  local added_count=0
  while IFS= read -r line; do
    if [[ "$line" =~ ^[+][^+] ]]; then
      ((added_count++))
    fi
  done <<< "$diff_content"

  # Count lines starting with "-" but not "--"
  local removed_count=0
  while IFS= read -r line; do
    if [[ "$line" =~ ^[-][^-] ]]; then
      ((removed_count++))
    fi
  done <<< "$diff_content"

  # Apply heuristics
  if (( removed_count == 0 && added_count > 0 )); then
    echo "Add $name"
  elif (( added_count > removed_count * 2 )); then
    echo "Extend $name"
  elif (( removed_count > added_count * 2 )); then
    echo "Simplify $name"
  else
    echo "Update $name"
  fi
}

# Infer architectural layer from file path
infer_layer() {
  local filepath="$1"
  local basename="${filepath##*/}"

  # API layer indicators (lowercase and PascalCase for C#)
  if [[ "$filepath" == *"/api/"* ]] || [[ "$filepath" == *"/Api/"* ]] || \
     [[ "$filepath" == *"/routes/"* ]] || [[ "$filepath" == *"/Routes/"* ]] || \
     [[ "$filepath" == *"/handlers/"* ]] || [[ "$filepath" == *"/Handlers/"* ]] || \
     [[ "$filepath" == *"/controllers/"* ]] || [[ "$filepath" == *"/Controllers/"* ]]; then
    echo "api"
    return
  fi

  # Service layer indicators (lowercase and PascalCase for C#)
  if [[ "$filepath" == *"/services/"* ]] || [[ "$filepath" == *"/Services/"* ]] || \
     [[ "$filepath" == *"/usecases/"* ]] || [[ "$filepath" == *"/UseCases/"* ]] || \
     [[ "$filepath" == *"/use-cases/"* ]] || [[ "$filepath" == *"/App/"* ]]; then
    echo "service"
    return
  fi

  # Domain layer indicators (lowercase and PascalCase for C#)
  if [[ "$filepath" == *"/domain/"* ]] || [[ "$filepath" == *"/Domain/"* ]] || \
     [[ "$filepath" == *"/models/"* ]] || [[ "$filepath" == *"/Models/"* ]] || \
     [[ "$filepath" == *"/entities/"* ]] || [[ "$filepath" == *"/Entities/"* ]] || \
     [[ "$filepath" == *"/Core/"* ]]; then
    echo "domain"
    return
  fi

  # Data layer indicators (lowercase and PascalCase for C#)
  if [[ "$filepath" == *"/data/"* ]] || [[ "$filepath" == *"/Data/"* ]] || \
     [[ "$filepath" == *"/repositories/"* ]] || [[ "$filepath" == *"/Repositories/"* ]] || \
     [[ "$filepath" == *"/dal/"* ]] || [[ "$filepath" == *"/persistence/"* ]] || \
     [[ "$filepath" == *"/Persistence/"* ]]; then
    echo "data"
    return
  fi

  # Infrastructure layer indicators (lowercase and PascalCase for C#)
  if [[ "$filepath" == *"/infra/"* ]] || [[ "$filepath" == *"/Infra/"* ]] || \
     [[ "$filepath" == *"/infrastructure/"* ]] || [[ "$filepath" == *"/Infrastructure/"* ]] || \
     [[ "$filepath" == *"/providers/"* ]] || [[ "$filepath" == *"/Providers/"* ]] || \
     [[ "$filepath" == *"/Adapters/"* ]] || [[ "$filepath" == *"/adapters/"* ]]; then
    echo "infra"
    return
  fi

  # Test layer (lowercase, PascalCase, and C# conventions)
  if [[ "$basename" == *".test."* ]] || [[ "$basename" == *".spec."* ]] || \
     [[ "$basename" == *"Test."* ]] || [[ "$basename" == *"Tests."* ]] || \
     [[ "$filepath" == *"__tests__"* ]] || [[ "$filepath" == *"/tests/"* ]] || \
     [[ "$filepath" == *".Tests."* ]] || [[ "$filepath" == *".Test."* ]]; then
    echo "test"
    return
  fi

  # Config layer indicators
  if [[ "$filepath" == *"/config/"* ]] || [[ "$basename" == *".config."* ]]; then
    echo "config"
    return
  fi

  # Default
  echo "unknown"
}

# JSON-escape a string
json_escape() {
  local s="$1"
  s="${s//\\/\\\\}"
  s="${s//\"/\\\"}"
  s="${s//$'\n'/\\n}"
  s="${s//$'\r'/\\r}"
  s="${s//$'\t'/\\t}"
  echo "$s"
}

# Parse unified diff output into a lookup table of file → hunks
# Returns data via stdout: each line is "filepath${DELIM}hunk_data"
parse_diff_hunks() {
  local diff_output="$1"

  local current_file=""
  local current_hunk_start=""
  local current_hunk_end=""
  local current_hunk_content=""
  local in_hunk=false

  while IFS= read -r line; do
    # If line starts with "diff --git"
    if [[ "$line" =~ ^diff\ --git ]]; then
      # Save previous hunk if exists
      if [[ -n "$current_file" && -n "$current_hunk_start" ]]; then
        echo "${current_file}${DELIM}${current_hunk_start}${DELIM}${current_hunk_end}${DELIM}${current_hunk_content}"
      fi

      # Extract file path from "diff --git a/... b/..."
      if [[ "$line" =~ b/(.+)$ ]]; then
        current_file="${BASH_REMATCH[1]}"
      fi

      # Reset hunk state
      current_hunk_start=""
      current_hunk_end=""
      current_hunk_content=""
      in_hunk=false

    # If line starts with "@@"
    elif [[ "$line" =~ ^@@\ -[0-9]+(,[0-9]+)?\ \+([0-9]+)(,([0-9]+))?\ @@ ]]; then
      # Save previous hunk if exists
      if [[ -n "$current_file" && -n "$current_hunk_start" ]]; then
        echo "${current_file}${DELIM}${current_hunk_start}${DELIM}${current_hunk_end}${DELIM}${current_hunk_content}"
      fi

      # Parse hunk header: @@ -oldstart,oldcount +newstart,newcount @@
      local newstart="${BASH_REMATCH[2]}"
      local newcount="${BASH_REMATCH[4]}"

      # Handle case where count is omitted (means count of 1)
      if [[ -z "$newcount" ]]; then
        newcount=1
      fi

      # Calculate hunk end
      current_hunk_start="$newstart"
      current_hunk_end=$((newstart + newcount - 1))

      # Start content with the hunk header line
      current_hunk_content="$line"
      in_hunk=true

    # Skip git header lines
    elif [[ "$line" =~ ^(---|[+][+][+]|index\ |new\ file|deleted\ file|similarity\ ) ]]; then
      continue

    # Append to current hunk content
    elif [[ "$in_hunk" == "true" ]]; then
      current_hunk_content+=$'\n'"$line"
    fi

  done <<< "$diff_output"

  # Save last hunk if exists
  if [[ -n "$current_file" && -n "$current_hunk_start" ]]; then
    echo "${current_file}${DELIM}${current_hunk_start}${DELIM}${current_hunk_end}${DELIM}${current_hunk_content}"
  fi
}

# Main
main() {
  local -a git_args

  # Parse command line arguments
  if [[ $# -eq 0 ]]; then
    git_args=()
  else
    git_args=("$@")
  fi

  # Get the list of changed files with their change status
  local file_statuses
  file_statuses=$(get_file_statuses "${git_args[@]}")

  # Get all diff hunks for the changed files
  local diff_output
  if [[ ${#git_args[@]} -eq 0 ]]; then
    diff_output=$(git diff 2>/dev/null) || {
      echo "Error: git diff failed" >&2
      exit 1
    }
  else
    diff_output=$(git diff "${git_args[@]}" 2>/dev/null) || {
      echo "Error: git diff failed with args: ${git_args[*]}" >&2
      exit 1
    }
  fi

  # Parse the diff output into a file-to-hunks lookup table
  local parsed_hunks
  parsed_hunks=$(parse_diff_hunks "$diff_output")

  # For each changed file in the status list
  while IFS=$'\t' read -r status filepath; do
    [[ -z "$filepath" ]] && continue

    # Determine the source for unit extraction
    local source_file="$filepath"
    local temp_file=""

    local change_status
    change_status=$(get_change_status "$status")

    if [[ "$change_status" == "deleted" ]]; then
      # Extract file content from HEAD revision
      temp_file=$(mktemp)
      if ! git show "HEAD:$filepath" > "$temp_file" 2>/dev/null; then
        echo "Warning: Could not extract deleted file from HEAD: $filepath" >&2
        rm -f "$temp_file"
        continue
      fi
      source_file="$temp_file"
    elif [[ ! -f "$filepath" ]]; then
      echo "Warning: File not found: $filepath" >&2
      continue
    fi

    # Extract semantic units from the file source
    local units_json
    if ! units_json=$("$EXTRACT_UNITS" --files "$source_file" 2>/dev/null); then
      echo "Warning: extract-units.sh failed for: $filepath" >&2
      [[ -n "$temp_file" ]] && rm -f "$temp_file"
      continue
    fi

    # Clean up temp file for deleted files
    [[ -n "$temp_file" ]] && rm -f "$temp_file"

    # Parse the JSON output to get list of units
    # Extract just the units array from the JSON
    local units_array
    units_array=$(echo "$units_json" | jq -c '.units[]' 2>/dev/null) || {
      echo "Warning: Failed to parse units JSON for: $filepath" >&2
      continue
    }

    # Get the hunks for this file from the parsed hunks
    # Filter parsed_hunks to only include this file
    local file_hunks
    file_hunks=$(echo "$parsed_hunks" | grep "^${filepath}${DELIM}" || true)
    if [[ -z "$file_hunks" ]]; then
      # No hunks for this file, skip
      continue
    fi

    # For each unit extracted from the file
    while IFS= read -r unit_json; do
      [[ -z "$unit_json" ]] && continue

      # Extract unit line range
      local unit_lines
      unit_lines=$(echo "$unit_json" | jq -r '.lines | "\(.[0]) \(.[1])"' 2>/dev/null) || continue
      read -r unit_start unit_end <<< "$unit_lines"

      # Find overlapping hunks for this unit
      local matching_hunks=""

      # Parse hunks for this file
      while IFS= read -r hunk_line; do
        [[ -z "$hunk_line" ]] && continue

        # Parse hunk line: filepath${DELIM}hunk_start${DELIM}hunk_end${DELIM}hunk_content
        local file_from_hunk hunk_start hunk_end hunk_content
        IFS="$DELIM" read -r file_from_hunk hunk_start hunk_end hunk_content <<< "$hunk_line"

        # If overlaps(unit lines, hunk range)
        if overlaps "$unit_start" "$unit_end" "$hunk_start" "$hunk_end"; then
          if [[ -z "$matching_hunks" ]]; then
            matching_hunks="$hunk_content"
          else
            matching_hunks+=$'\n\n'"$hunk_content"
          fi
        fi
      done <<< "$file_hunks"

      # If no hunks overlap with this unit, skip
      if [[ -z "$matching_hunks" ]]; then
        continue
      fi

      # Build the diff field (already clean from parse_diff_hunks)
      local diff_field
      diff_field=$(json_escape "$matching_hunks")

      # Generate a summary from the unit name and diff content
      local unit_name
      unit_name=$(echo "$unit_json" | jq -r '.name' 2>/dev/null) || continue

      local summary
      summary=$(generate_summary "$unit_name" "$matching_hunks")
      summary=$(json_escape "$summary")

      # Infer the architectural layer from file path
      local layer
      layer=$(infer_layer "$filepath")

      # Build the complete JSON object
      # Update the file path if it was a deleted file (temp file was used)
      if [[ "$change_status" == "deleted" ]]; then
        unit_json=$(echo "$unit_json" | jq --arg file "$filepath" '.file = $file')
      fi

      # Add diff, summary, changeStatus, and layer fields
      local enhanced_json
      enhanced_json=$(echo "$unit_json" | jq -c \
        --arg diff "$diff_field" \
        --arg summary "$summary" \
        --arg changeStatus "$change_status" \
        --arg layer "$layer" \
        '. + {diff: $diff, summary: $summary, changeStatus: $changeStatus, layer: $layer}')

      # Output the JSON object as a single line to stdout
      echo "$enhanced_json"

    done <<< "$units_array"

  done <<< "$file_statuses"
}

main "$@"
