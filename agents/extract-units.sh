#!/usr/bin/env bash
#
# Extract semantic units (functions, classes) from code using tree-sitter CLI.
#
# Usage:
#   ./extract-units.sh [--staged | --files file1 file2 | <git-diff-args>]
#   ./extract-units.sh --status   # Check tree-sitter availability
#
# Output: JSON with:
#   - units: extracted functions/classes/etc with full metadata
#   - fallback_files: files that need LLM extraction (unsupported/missing grammar)
#
# If tree-sitter CLI not installed, outputs all files in fallback_files.
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Field delimiter (unit separator ASCII 31, won't appear in code)
DELIM=$'\x1f'

# Check tree-sitter availability
check_status() {
  local ts_version parsers_count

  if ! command -v tree-sitter &>/dev/null; then
    echo '{"available": false, "error": "tree-sitter CLI not found. Run: ./scripts/setup-tree-sitter.sh"}'
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

# Grammar directory (where tree-sitter grammars are cloned)
GRAMMAR_DIR="${TREE_SITTER_GRAMMAR_DIR:-$HOME/repos/tree-sitter-grammars}"

# Get query file based on file extension
# Prefers custom queries from $SCRIPT_DIR/queries/ over official tags.scm
get_query_file_for_ext() {
  local file="$1"
  local ext="${file##*.}"

  # Map extension to language name
  local lang_name
  case "$ext" in
    js|mjs|cjs|jsx) lang_name="javascript" ;;
    ts|tsx) lang_name="typescript" ;;
    py) lang_name="python" ;;
    go) lang_name="go" ;;
    rs) lang_name="rust" ;;
    java) lang_name="java" ;;
    rb) lang_name="ruby" ;;
    c|h) lang_name="c" ;;
    cpp|cc|cxx|hpp) lang_name="cpp" ;;
    cs) lang_name="csharp" ;;
    sh|bash) lang_name="bash" ;;
    swift) lang_name="swift" ;;
    kt) lang_name="kotlin" ;;
    *) return ;;  # Unknown extension
  esac

  # 1. Check for custom query first (preferred)
  local custom_query="$SCRIPT_DIR/queries/$lang_name.scm"
  if [[ -f "$custom_query" ]]; then
    echo "$custom_query"
    return
  fi

  # 2. Fall back to official tags.scm from grammar repo
  local official_tags="$GRAMMAR_DIR/tree-sitter-$lang_name/queries/tags.scm"
  if [[ -f "$official_tags" ]]; then
    echo "$official_tags"
  fi
}

# JSON-escape a string
json_escape() {
  local s="$1"
  # Escape backslashes, double quotes, and control characters
  s="${s//\\/\\\\}"
  s="${s//\"/\\\"}"
  s="${s//$'\n'/\\n}"
  s="${s//$'\r'/\\r}"
  s="${s//$'\t'/\\t}"
  echo "$s"
}

# Determine if a file is a test file based on naming conventions
is_test_file() {
  local filepath="$1"
  local basename="${filepath##*/}"

  # Check basename patterns
  if [[ "$basename" == *".test."* ]] || [[ "$basename" == *".spec."* ]]; then
    return 0
  fi

  if [[ "$basename" == test_* ]] || [[ "$basename" == *"_test."* ]]; then
    return 0
  fi

  if [[ "$basename" == *"Test."* ]] || [[ "$basename" == *"Spec."* ]]; then
    return 0
  fi

  # C# convention: *Tests.cs (plural)
  if [[ "$basename" == *"Tests."* ]] || [[ "$basename" == *"Specs."* ]]; then
    return 0
  fi

  # Check path patterns
  if [[ "$filepath" == *"__tests__"* ]]; then
    return 0
  fi

  if [[ "$filepath" == *"/tests/"* ]] || [[ "$filepath" == *"/test/"* ]]; then
    return 0
  fi

  if [[ "$filepath" == *"/spec/"* ]] || [[ "$filepath" == *"/specs/"* ]]; then
    return 0
  fi

  # C#/.NET convention: *.Tests.* or *.Test.* in path (e.g., MyProject.Tests.Unit/)
  if [[ "$filepath" == *".Tests."* ]] || [[ "$filepath" == *".Test."* ]]; then
    return 0
  fi

  return 1
}

# Infer the unit name being tested from a test file name
# Returns the inferred unit name, or empty string if not inferrable
infer_tests_unit() {
  local filepath="$1"
  local basename="${filepath##*/}"
  local name_no_ext="${basename%.*}"  # Remove extension

  # Handle double extensions like .test.ts, .spec.js
  if [[ "$name_no_ext" == *".test" ]] || [[ "$name_no_ext" == *".spec" ]]; then
    name_no_ext="${name_no_ext%.*}"
  fi

  # JS/TS: foo.test.ts → foo, foo.spec.ts → foo
  if [[ "$basename" == *".test."* ]]; then
    echo "${basename%.test.*}"
    return
  fi
  if [[ "$basename" == *".spec."* ]]; then
    echo "${basename%.spec.*}"
    return
  fi

  # Python: test_foo.py → foo
  if [[ "$basename" == test_* ]]; then
    local without_prefix="${name_no_ext#test_}"
    echo "$without_prefix"
    return
  fi

  # Python: foo_test.py → foo
  if [[ "$name_no_ext" == *_test ]]; then
    echo "${name_no_ext%_test}"
    return
  fi

  # Java/C#: FooTest.java → Foo, FooTests.cs → Foo
  if [[ "$name_no_ext" == *Tests ]]; then
    echo "${name_no_ext%Tests}"
    return
  fi
  if [[ "$name_no_ext" == *Test ]]; then
    echo "${name_no_ext%Test}"
    return
  fi

  # C#: FooSpecs.cs → Foo
  if [[ "$name_no_ext" == *Specs ]]; then
    echo "${name_no_ext%Specs}"
    return
  fi
  if [[ "$name_no_ext" == *Spec ]]; then
    echo "${name_no_ext%Spec}"
    return
  fi

  # Could not infer
  echo ""
}

# Layer overrides storage (loaded from .code-foundations/layers.yaml)
# Format: "pattern1:layer1 pattern2:layer2 ..."
LAYER_OVERRIDES=""
LAYER_OVERRIDES_LOADED=false

# Load layer overrides from repo config file
load_layer_overrides() {
  [[ "$LAYER_OVERRIDES_LOADED" == "true" ]] && return

  LAYER_OVERRIDES_LOADED=true
  local config_file=".code-foundations/layers.yaml"

  [[ ! -f "$config_file" ]] && return

  # Parse YAML overrides section (simple key: value format)
  # Supports: /Pattern/: layer
  local in_overrides=false
  while IFS= read -r line; do
    # Check for overrides: section
    if [[ "$line" =~ ^overrides: ]]; then
      in_overrides=true
      continue
    fi

    # Stop at next top-level key
    if [[ "$in_overrides" == "true" && "$line" =~ ^[a-z] && ! "$line" =~ ^[[:space:]] ]]; then
      break
    fi

    # Parse override entries (indented lines with pattern: layer)
    if [[ "$in_overrides" == "true" && "$line" =~ ^[[:space:]]+(\"[^\"]+\"|\'[^\']+\'|[^:]+):[[:space:]]*([a-z]+) ]]; then
      local pattern="${BASH_REMATCH[1]}"
      local layer="${BASH_REMATCH[2]}"
      # Remove quotes if present
      pattern="${pattern#\"}"
      pattern="${pattern%\"}"
      pattern="${pattern#\'}"
      pattern="${pattern%\'}"
      # Trim whitespace
      pattern="${pattern#"${pattern%%[![:space:]]*}"}"
      pattern="${pattern%"${pattern##*[![:space:]]}"}"
      LAYER_OVERRIDES="${LAYER_OVERRIDES}${pattern}:${layer} "
    fi
  done < "$config_file"
}

# Check if filepath matches any layer override
check_layer_override() {
  local filepath="$1"

  # Load overrides if not already loaded
  load_layer_overrides

  [[ -z "$LAYER_OVERRIDES" ]] && return 1

  # Check each override pattern
  for entry in $LAYER_OVERRIDES; do
    local pattern="${entry%:*}"
    local layer="${entry#*:}"

    if [[ "$filepath" == *"$pattern"* ]]; then
      echo "$layer"
      return 0
    fi
  done

  return 1
}

# Infer architectural layer from directory path patterns
infer_layer() {
  local filepath="$1"
  local basename="${filepath##*/}"

  # Check repo-specific overrides first
  local override_layer
  if override_layer=$(check_layer_override "$filepath"); then
    echo "$override_layer"
    return
  fi

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

  # Integration layer - code that talks to external systems (adapters, providers, clients)
  if [[ "$filepath" == *"/Adapters/"* ]] || [[ "$filepath" == *"/adapters/"* ]] || \
     [[ "$filepath" == *"/providers/"* ]] || [[ "$filepath" == *"/Providers/"* ]] || \
     [[ "$filepath" == *"/clients/"* ]] || [[ "$filepath" == *"/Clients/"* ]] || \
     [[ "$filepath" == *"/gateways/"* ]] || [[ "$filepath" == *"/Gateways/"* ]] || \
     [[ "$filepath" == *"/external/"* ]] || [[ "$filepath" == *"/External/"* ]]; then
    echo "integration"
    return
  fi

  # Infrastructure layer - HTTP pipeline, DI, cross-cutting concerns
  if [[ "$filepath" == *"/infra/"* ]] || [[ "$filepath" == *"/Infra/"* ]] || \
     [[ "$filepath" == *"/infrastructure/"* ]] || [[ "$filepath" == *"/Infrastructure/"* ]] || \
     [[ "$filepath" == *"/Middleware/"* ]] || [[ "$filepath" == *"/middleware/"* ]] || \
     [[ "$filepath" == *"/Extensions/"* ]] || [[ "$filepath" == *"/extensions/"* ]] || \
     [[ "$filepath" == *"/hosting/"* ]] || [[ "$filepath" == *"/Hosting/"* ]]; then
    echo "infra"
    return
  fi

  # Test layer (checked after specific layers)
  if is_test_file "$filepath"; then
    echo "test"
    return
  fi

  # Config layer indicators
  if [[ "$filepath" == *"/config/"* ]] || [[ "$filepath" == *"/configs/"* ]] || \
     [[ "$filepath" == *"/Config/"* ]] || [[ "$filepath" == *"/Constants/"* ]] || \
     [[ "$filepath" == *"/constants/"* ]] || [[ "$basename" == *".config."* ]]; then
    echo "config"
    return
  fi

  if [[ "$basename" == *".config."* ]]; then
    echo "config"
    return
  fi

  # Default
  echo "unknown"
}

# Extract units from a single file using comprehensive AST parsing
extract_file() {
  local file="$1"
  local query_file

  query_file=$(get_query_file_for_ext "$file")
  [[ -z "$query_file" ]] && return

  # Parse tree-sitter query output
  local output
  output=$(tree-sitter query "$query_file" "$file" 2>/dev/null) || return

  # Track definitions: each entry uses DELIM as separator
  # Format: "start${DELIM}end${DELIM}type${DELIM}name${DELIM}params${DELIM}return_type${DELIM}visibility${DELIM}modifiers"
  local definitions=()

  # Track pattern captures for characteristics: "pattern_type${DELIM}start${DELIM}end"
  local patterns=()

  # Track call names: "start${DELIM}name"
  local call_names=()

  # Current parsing state
  local current_def_start="" current_def_end="" current_def_type=""
  local current_name="" current_params="" current_return_type=""
  local current_visibility="" current_modifiers=""

  # Parse the output line by line
  while IFS= read -r line; do
    # New pattern starts
    if [[ "$line" =~ ^[[:space:]]*pattern:[[:space:]]*([0-9]+) ]]; then
      # Save previous definition if complete
      if [[ -n "$current_def_start" && -n "$current_name" ]]; then
        definitions+=("${current_def_start}${DELIM}${current_def_end}${DELIM}${current_def_type}${DELIM}${current_name}${DELIM}${current_params}${DELIM}${current_return_type}${DELIM}${current_visibility}${DELIM}${current_modifiers}")
      fi

      # Reset for new pattern
      current_def_start="" current_def_end="" current_def_type=""
      current_name="" current_params="" current_return_type=""
      current_visibility="" current_modifiers=""
      continue
    fi

    # Parse capture lines
    # Format: "    capture: definition.function.exported.async, start: (2, 0), end: (13, 1)"
    # Also handles numbered format: "    capture: 4 - definition.function.exported.async, start: (0, 0), end: (0, 40)"
    if [[ "$line" =~ capture:\ ([0-9]+\ -\ )?([^,]+),\ start:\ \(([0-9]+),\ [0-9]+\),\ end:\ \(([0-9]+), ]]; then
      local capture_name="${BASH_REMATCH[2]}"
      local start_row="${BASH_REMATCH[3]}"
      local end_row="${BASH_REMATCH[4]}"

      # Convert 0-indexed to 1-indexed
      local start_line=$((start_row + 1))
      local end_line=$((end_row + 1))

      # Check for definition captures
      if [[ "$capture_name" =~ ^definition\. ]]; then
        current_def_start="$start_line"
        current_def_end="$end_line"

        # Parse type and modifiers from capture name
        local parts="${capture_name#definition.}"
        local base_type="${parts%%.*}"
        current_def_type="$base_type"

        # Extract visibility and modifiers
        current_visibility=""
        if [[ "$parts" == *".exported"* ]]; then
          current_visibility="exported"
        elif [[ "$parts" == *".private"* ]]; then
          current_visibility="private"
        elif [[ "$parts" == *".public"* ]]; then
          current_visibility="public"
        fi

        current_modifiers=""
        if [[ "$parts" == *".async"* ]]; then
          current_modifiers="${current_modifiers}async,"
        fi
        if [[ "$parts" == *".static"* ]]; then
          current_modifiers="${current_modifiers}static,"
        fi
        if [[ "$parts" == *".arrow"* ]]; then
          current_modifiers="${current_modifiers}arrow,"
        fi
        if [[ "$parts" == *".decorated"* ]]; then
          current_modifiers="${current_modifiers}decorated,"
        fi
        current_modifiers="${current_modifiers%,}"

      # Check for pattern captures (characteristics)
      elif [[ "$capture_name" =~ ^(pattern\.|[0-9]+\ -\ pattern\.) ]]; then
        local pattern_type
        if [[ "$capture_name" =~ pattern\.([a-z_]+) ]]; then
          pattern_type="${BASH_REMATCH[1]}"
          patterns+=("${pattern_type}${DELIM}${start_line}${DELIM}${end_line}")
        fi
      fi
    fi

    # Parse named captures with text (with number prefix)
    # Format: "    capture: 0 - name, start: (2, 22), end: (2, 33), text: `processUser`"
    if [[ "$line" =~ capture:\ [0-9]+\ -\ ([^,]+),.*text:\ \`([^\`]*)\` ]]; then
      local field_name="${BASH_REMATCH[1]}"
      local field_text="${BASH_REMATCH[2]}"

      case "$field_name" in
        name) current_name="$field_text" ;;
        params) current_params="$field_text" ;;
        return_type) current_return_type="$field_text" ;;
        call.name)
          # Extract start line from the line for correlation
          if [[ "$line" =~ start:\ \(([0-9]+), ]]; then
            local call_start=$(( ${BASH_REMATCH[1]} + 1 ))
            call_names+=("${call_start}${DELIM}${field_text}")
          fi
          ;;
      esac
    fi

    # Also check for named captures without number prefix (fallback)
    # Format: "    capture: name, start: (2, 22), end: (2, 33), text: `processUser`"
    if [[ "$line" =~ capture:\ (name|params|return_type),\ start:.*text:\ \`([^\`]*)\` ]]; then
      local field_name="${BASH_REMATCH[1]}"
      local field_text="${BASH_REMATCH[2]}"

      case "$field_name" in
        name) [[ -z "$current_name" ]] && current_name="$field_text" ;;
        params) [[ -z "$current_params" ]] && current_params="$field_text" ;;
        return_type) [[ -z "$current_return_type" ]] && current_return_type="$field_text" ;;
      esac
    fi

  done <<< "$output"

  # Save last definition if any
  if [[ -n "$current_def_start" && -n "$current_name" ]]; then
    definitions+=("${current_def_start}${DELIM}${current_def_end}${DELIM}${current_def_type}${DELIM}${current_name}${DELIM}${current_params}${DELIM}${current_return_type}${DELIM}${current_visibility}${DELIM}${current_modifiers}")
  fi

  # Deduplicate definitions:
  # 1. Remove entries where one definition contains another with same name (keep outer)
  # 2. For exact duplicates (same start/end/name), keep the one with more modifiers
  local unique_defs=()

  # Guard for empty definitions
  if [[ ${#definitions[@]} -eq 0 ]]; then
    return
  fi

  for def in "${definitions[@]}"; do
    local start end type name params return_type visibility modifiers
    IFS="$DELIM" read -r start end type name params return_type visibility modifiers <<< "$def"

    # Check if this definition is contained within or duplicates another
    local dominated=false
    local replace_idx=-1

    if [[ ${#unique_defs[@]} -gt 0 ]]; then
      local idx=0
      for existing in "${unique_defs[@]}"; do
        local ex_start ex_end ex_type ex_name ex_params ex_return ex_vis ex_mods
        IFS="$DELIM" read -r ex_start ex_end ex_type ex_name ex_params ex_return ex_vis ex_mods <<< "$existing"

        if [[ "$name" == "$ex_name" ]]; then
          # Exact same range - keep one with more metadata
          if (( start == ex_start && end == ex_end )); then
            # Count fields: modifiers + visibility
            local new_score=0 old_score=0
            [[ -n "$modifiers" ]] && new_score=$((new_score + 1))
            [[ -n "$visibility" ]] && new_score=$((new_score + 1))
            [[ -n "$ex_mods" ]] && old_score=$((old_score + 1))
            [[ -n "$ex_vis" ]] && old_score=$((old_score + 1))

            if (( new_score > old_score )); then
              replace_idx=$idx
            else
              dominated=true
            fi
            break
          fi

          # This one is contained within existing -> skip it
          if (( start >= ex_start && end <= ex_end )); then
            dominated=true
            break
          fi

          # This one contains existing -> will replace
          if (( start <= ex_start && end >= ex_end )); then
            replace_idx=$idx
            break
          fi
        fi
        ((idx++))
      done
    fi

    [[ "$dominated" == "true" ]] && continue

    # Replace existing entry if found
    if (( replace_idx >= 0 )); then
      unique_defs[$replace_idx]="$def"
    else
      unique_defs+=("$def")
    fi
  done

  # Sort definitions by start line (simple bubble sort for small arrays)
  local n=${#unique_defs[@]}
  for ((i = 0; i < n - 1; i++)); do
    for ((j = 0; j < n - i - 1; j++)); do
      local start_j start_j1
      IFS="$DELIM" read -r start_j _ <<< "${unique_defs[$j]}"
      IFS="$DELIM" read -r start_j1 _ <<< "${unique_defs[$((j + 1))]}"
      if (( start_j > start_j1 )); then
        local tmp="${unique_defs[$j]}"
        unique_defs[$j]="${unique_defs[$((j + 1))]}"
        unique_defs[$((j + 1))]="$tmp"
      fi
    done
  done

  # File-level calculations
  local is_test=false
  is_test_file "$file" && is_test=true
  local layer
  layer=$(infer_layer "$file")

  # Infer testsUnit for test files
  local tests_unit=""
  if [[ "$is_test" == "true" ]]; then
    tests_unit=$(infer_tests_unit "$file")
  fi

  # Build JSON output for each definition
  local first=true
  for def in "${unique_defs[@]}"; do
    local start end type name params return_type visibility modifiers
    IFS="$DELIM" read -r start end type name params return_type visibility modifiers <<< "$def"

    # Definition-level calculations
    local param_count=0
    # Remove parentheses and whitespace for empty check
    local params_trimmed="${params//[()[:space:]]/}"
    if [[ -n "$params_trimmed" ]]; then
      param_count=$(($(printf '%s' "$params" | tr -cd ',' | wc -c) + 1))
    fi

    local line_count=$((end - start + 1))

    # Count characteristics within this definition's line range
    local loop_count=0 try_catch_count=0 async_count=0 call_count=0 throw_count=0

    if [[ ${#patterns[@]} -gt 0 ]]; then
      for pattern in "${patterns[@]}"; do
        local ptype pstart pend
        IFS="$DELIM" read -r ptype pstart pend <<< "$pattern"
        if (( pstart >= start && pstart <= end )); then
          case "$ptype" in
            loop) ((loop_count++)) ;;
            try_catch) ((try_catch_count++)) ;;
            async) ((async_count++)) ;;
            call) ((call_count++)) ;;
            throw) ((throw_count++)) ;;
          esac
        fi
      done
    fi

    # Collect unique call names within this definition and detect recursion
    local calls_json="["
    local calls_first=true
    local seen_calls=""
    local has_recursion=false
    if [[ ${#call_names[@]} -gt 0 ]]; then
      for call_entry in "${call_names[@]}"; do
        local cstart cname
        IFS="$DELIM" read -r cstart cname <<< "$call_entry"
        if (( cstart >= start && cstart <= end )); then
          # Check for recursion
          if [[ "$cname" == "$name" ]]; then
            has_recursion=true
          fi

          if [[ "$seen_calls" != *"${DELIM}${cname}${DELIM}"* ]]; then
            seen_calls="${seen_calls}${DELIM}${cname}${DELIM}"
            if [[ "$calls_first" != "true" ]]; then
              calls_json+=","
            fi
            calls_json+="\"$(json_escape "$cname")\""
            calls_first=false
          fi
        fi
      done
    fi
    calls_json+="]"

    # Build modifiers array
    local modifiers_json="[]"
    if [[ -n "$modifiers" ]]; then
      modifiers_json="["
      local mods_first=true
      IFS=',' read -ra mods <<< "$modifiers"
      for m in "${mods[@]}"; do
        if [[ -n "$m" ]]; then
          if [[ "$mods_first" != "true" ]]; then
            modifiers_json+=","
          fi
          modifiers_json+="\"$m\""
          mods_first=false
        fi
      done
      modifiers_json+="]"
    fi

    # Boolean characteristics
    local has_loops=false has_try_catch=false has_async=false has_throw=false
    (( loop_count > 0 )) && has_loops=true
    (( try_catch_count > 0 )) && has_try_catch=true
    (( async_count > 0 )) && has_async=true
    (( throw_count > 0 )) && has_throw=true

    # Output JSON
    if [[ "$first" != "true" ]]; then
      printf ","
    fi
    first=false

    # Escape strings for JSON
    local escaped_name escaped_params escaped_return_type escaped_visibility
    escaped_name=$(json_escape "$name")
    escaped_params=$(json_escape "$params")
    escaped_return_type=$(json_escape "$return_type")
    escaped_visibility=$(json_escape "$visibility")

    printf '{"type":"%s","name":"%s","file":"%s","lines":[%d,%d]' \
      "$type" "$escaped_name" "$file" "$start" "$end"

    # Add optional fields
    [[ -n "$visibility" ]] && printf ',"visibility":"%s"' "$escaped_visibility"
    printf ',"modifiers":%s' "$modifiers_json"
    [[ -n "$params" ]] && printf ',"params":"%s"' "$escaped_params"
    [[ -n "$return_type" ]] && printf ',"return_type":"%s"' "$escaped_return_type"
    printf ',"calls":%s' "$calls_json"
    printf ',"has_loops":%s,"has_try_catch":%s,"has_async":%s' "$has_loops" "$has_try_catch" "$has_async"
    printf ',"loop_count":%d,"call_count":%d' "$loop_count" "$call_count"
    printf ',"is_test":%s,"layer":"%s","param_count":%d,"line_count":%d,"has_throw":%s,"has_recursion":%s' \
      "$is_test" "$layer" "$param_count" "$line_count" "$has_throw" "$has_recursion"

    # Add tests_unit for test files (only if non-empty)
    if [[ -n "$tests_unit" ]]; then
      printf ',"tests_unit":"%s"' "$(json_escape "$tests_unit")"
    fi

    printf '}'
  done
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

  # Try to parse the file - tree-sitter auto-detects language by extension
  tree-sitter parse --quiet "$file" 2>/dev/null
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
    case "${file##*.}" in
      md|json|yaml|yml|txt|lock|toml|xml|config) continue ;;
    esac

    # If tree-sitter not available, all code files need fallback
    if [[ "$ts_available" != "true" ]]; then
      fallback_files+=("$file")
      continue
    fi

    # Check if we have a query file for this extension
    local query_file
    query_file=$(get_query_file_for_ext "$file")
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
