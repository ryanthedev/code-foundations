#!/usr/bin/env bash
#
# Extract semantic units (functions, classes, methods) from code using ast-grep.
#
# Usage:
#   ./extract-units.sh [--staged | --files file1 file2 | <git-diff-args>]
#   ./extract-units.sh --status   # Check ast-grep availability
#
# Output: JSON with:
#   - units: extracted functions/classes/etc with full metadata
#   - skipped_files: files with unsupported languages
#   - sg_available: true if ast-grep is installed
#
# Requirements: sg (ast-grep), jq
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SG_RULES_DIR="$SCRIPT_DIR/sg-rules"

# =============================================================================
# Dependency Check
# =============================================================================

check_deps() {
  local missing=""

  if ! command -v sg &>/dev/null; then
    missing="sg (ast-grep)"
  fi

  if ! command -v jq &>/dev/null; then
    if [[ -n "$missing" ]]; then
      missing="$missing, jq"
    else
      missing="jq"
    fi
  fi

  if [[ -n "$missing" ]]; then
    echo "{\"error\": \"Missing required tools: $missing\", \"sg_available\": false}" >&2
    exit 1
  fi
}

# Check status (for --status flag)
check_status() {
  if ! command -v sg &>/dev/null; then
    echo '{"sg_available": false, "error": "ast-grep (sg) not installed. Run: cargo install ast-grep"}'
    exit 0
  fi

  local sg_version
  sg_version=$(sg --version 2>/dev/null | head -1)

  # Check which rule files exist
  local rules_found=0
  for rule in "$SG_RULES_DIR"/*.yaml; do
    [[ -f "$rule" ]] && ((rules_found++)) || true
  done

  echo "{\"sg_available\": true, \"version\": \"$sg_version\", \"rules_found\": $rules_found}"
  exit 0
}

# =============================================================================
# Helper Functions (preserved from original)
# =============================================================================

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
infer_tests_unit() {
  local filepath="$1"
  local basename="${filepath##*/}"
  local name_no_ext="${basename%.*}"

  # Handle double extensions like .test.ts, .spec.js
  if [[ "$name_no_ext" == *".test" ]] || [[ "$name_no_ext" == *".spec" ]]; then
    name_no_ext="${name_no_ext%.*}"
  fi

  # JS/TS: foo.test.ts -> foo
  if [[ "$basename" == *".test."* ]]; then
    echo "${basename%.test.*}"
    return
  fi
  if [[ "$basename" == *".spec."* ]]; then
    echo "${basename%.spec.*}"
    return
  fi

  # Python: test_foo.py -> foo
  if [[ "$basename" == test_* ]]; then
    local without_prefix="${name_no_ext#test_}"
    echo "$without_prefix"
    return
  fi

  # Python: foo_test.py -> foo
  if [[ "$name_no_ext" == *_test ]]; then
    echo "${name_no_ext%_test}"
    return
  fi

  # Java/C#: FooTest.java -> Foo, FooTests.cs -> Foo
  if [[ "$name_no_ext" == *Tests ]]; then
    echo "${name_no_ext%Tests}"
    return
  fi
  if [[ "$name_no_ext" == *Test ]]; then
    echo "${name_no_ext%Test}"
    return
  fi

  # C#: FooSpecs.cs -> Foo
  if [[ "$name_no_ext" == *Specs ]]; then
    echo "${name_no_ext%Specs}"
    return
  fi
  if [[ "$name_no_ext" == *Spec ]]; then
    echo "${name_no_ext%Spec}"
    return
  fi

  echo ""
}

# Layer overrides storage
LAYER_OVERRIDES=""
LAYER_OVERRIDES_LOADED=false

# Load layer overrides from repo config file
load_layer_overrides() {
  [[ "$LAYER_OVERRIDES_LOADED" == "true" ]] && return

  LAYER_OVERRIDES_LOADED=true
  local config_file=".code-foundations/layers.yaml"

  [[ ! -f "$config_file" ]] && return

  local in_overrides=false
  while IFS= read -r line; do
    if [[ "$line" =~ ^overrides: ]]; then
      in_overrides=true
      continue
    fi

    if [[ "$in_overrides" == "true" && "$line" =~ ^[a-z] && ! "$line" =~ ^[[:space:]] ]]; then
      break
    fi

    if [[ "$in_overrides" == "true" && "$line" =~ ^[[:space:]]+(\"[^\"]+\"|\'[^\']+\'|[^:]+):[[:space:]]*([a-z]+) ]]; then
      local pattern="${BASH_REMATCH[1]}"
      local layer="${BASH_REMATCH[2]}"
      pattern="${pattern#\"}"
      pattern="${pattern%\"}"
      pattern="${pattern#\'}"
      pattern="${pattern%\'}"
      pattern="${pattern#"${pattern%%[![:space:]]*}"}"
      pattern="${pattern%"${pattern##*[![:space:]]}"}"
      LAYER_OVERRIDES="${LAYER_OVERRIDES}${pattern}:${layer} "
    fi
  done < "$config_file"
}

# Check if filepath matches any layer override
check_layer_override() {
  local filepath="$1"

  load_layer_overrides

  [[ -z "$LAYER_OVERRIDES" ]] && return 1

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

  # Test layer - check FIRST since test files have specific naming that overrides path
  if is_test_file "$filepath"; then
    echo "test"
    return
  fi

  # API layer indicators
  if [[ "$filepath" == *"/api/"* ]] || [[ "$filepath" == *"/Api/"* ]] || \
     [[ "$filepath" == *"/routes/"* ]] || [[ "$filepath" == *"/Routes/"* ]] || \
     [[ "$filepath" == *"/handlers/"* ]] || [[ "$filepath" == *"/Handlers/"* ]] || \
     [[ "$filepath" == *"/controllers/"* ]] || [[ "$filepath" == *"/Controllers/"* ]]; then
    echo "api"
    return
  fi

  # Service layer indicators
  if [[ "$filepath" == *"/services/"* ]] || [[ "$filepath" == *"/Services/"* ]] || \
     [[ "$filepath" == *"/usecases/"* ]] || [[ "$filepath" == *"/UseCases/"* ]] || \
     [[ "$filepath" == *"/use-cases/"* ]] || [[ "$filepath" == *"/App/"* ]]; then
    echo "service"
    return
  fi

  # Domain layer indicators
  if [[ "$filepath" == *"/domain/"* ]] || [[ "$filepath" == *"/Domain/"* ]] || \
     [[ "$filepath" == *"/models/"* ]] || [[ "$filepath" == *"/Models/"* ]] || \
     [[ "$filepath" == *"/entities/"* ]] || [[ "$filepath" == *"/Entities/"* ]] || \
     [[ "$filepath" == *"/Core/"* ]]; then
    echo "domain"
    return
  fi

  # Data layer indicators
  if [[ "$filepath" == *"/data/"* ]] || [[ "$filepath" == *"/Data/"* ]] || \
     [[ "$filepath" == *"/repositories/"* ]] || [[ "$filepath" == *"/Repositories/"* ]] || \
     [[ "$filepath" == *"/dal/"* ]] || [[ "$filepath" == *"/persistence/"* ]] || \
     [[ "$filepath" == *"/Persistence/"* ]]; then
    echo "data"
    return
  fi

  # Integration layer
  if [[ "$filepath" == *"/Adapters/"* ]] || [[ "$filepath" == *"/adapters/"* ]] || \
     [[ "$filepath" == *"/providers/"* ]] || [[ "$filepath" == *"/Providers/"* ]] || \
     [[ "$filepath" == *"/clients/"* ]] || [[ "$filepath" == *"/Clients/"* ]] || \
     [[ "$filepath" == *"/gateways/"* ]] || [[ "$filepath" == *"/Gateways/"* ]] || \
     [[ "$filepath" == *"/external/"* ]] || [[ "$filepath" == *"/External/"* ]]; then
    echo "integration"
    return
  fi

  # Infrastructure layer
  if [[ "$filepath" == *"/infra/"* ]] || [[ "$filepath" == *"/Infra/"* ]] || \
     [[ "$filepath" == *"/infrastructure/"* ]] || [[ "$filepath" == *"/Infrastructure/"* ]] || \
     [[ "$filepath" == *"/Middleware/"* ]] || [[ "$filepath" == *"/middleware/"* ]] || \
     [[ "$filepath" == *"/Extensions/"* ]] || [[ "$filepath" == *"/extensions/"* ]] || \
     [[ "$filepath" == *"/hosting/"* ]] || [[ "$filepath" == *"/Hosting/"* ]]; then
    echo "infra"
    return
  fi

  # Config layer indicators
  if [[ "$filepath" == *"/config/"* ]] || [[ "$filepath" == *"/configs/"* ]] || \
     [[ "$filepath" == *"/Config/"* ]] || [[ "$filepath" == *"/Constants/"* ]] || \
     [[ "$filepath" == *"/constants/"* ]] || [[ "$basename" == *".config."* ]]; then
    echo "config"
    return
  fi

  echo "unknown"
}

# =============================================================================
# Language Detection
# =============================================================================

# Map file extension to ast-grep language and rule file
get_language_info() {
  local file="$1"
  local ext="${file##*.}"

  case "$ext" in
    cs)
      echo "csharp:$SG_RULES_DIR/csharp.yaml"
      ;;
    ts|tsx)
      echo "typescript:$SG_RULES_DIR/typescript.yaml"
      ;;
    js|jsx|mjs|cjs)
      echo "typescript:$SG_RULES_DIR/typescript.yaml"
      ;;
    py)
      echo "python:$SG_RULES_DIR/python.yaml"
      ;;
    go)
      echo "go:$SG_RULES_DIR/go.yaml"
      ;;
    swift)
      echo "swift:$SG_RULES_DIR/swift.yaml"
      ;;
    *)
      echo ""
      ;;
  esac
}

# =============================================================================
# Unit Extraction
# =============================================================================

# Map rule ID to unit type
map_rule_to_type() {
  local rule_id="$1"

  case "$rule_id" in
    # C#
    cs-method|cs-async-method) echo "method" ;;
    cs-class|cs-primary-constructor) echo "class" ;;
    cs-interface) echo "interface" ;;
    cs-constructor|cs-partial-constructor) echo "constructor" ;;
    cs-property|cs-partial-property) echo "property" ;;
    cs-record) echo "class" ;;
    cs-enum) echo "class" ;;
    cs-operator|cs-compound-assignment-op|cs-conversion-operator) echo "method" ;;
    cs-local-function) echo "function" ;;
    cs-delegate) echo "interface" ;;
    cs-struct|cs-inline-array) echo "class" ;;
    cs-event|cs-partial-event) echo "field" ;;
    cs-indexer) echo "property" ;;
    cs-ref-readonly-param) echo "" ;;  # Skip - not a unit

    # TypeScript
    ts-function) echo "function" ;;
    ts-arrow-const|ts-arrow-let) echo "function" ;;
    ts-method) echo "method" ;;
    ts-class) echo "class" ;;
    ts-interface) echo "interface" ;;

    # Python
    py-function|py-function-typed|py-async-function) echo "function" ;;
    py-method|py-method-typed|py-async-method) echo "method" ;;
    py-class|py-class-with-bases) echo "class" ;;
    py-decorated) echo "" ;;  # Skip - handled by underlying def
    py-has-*) echo "" ;;  # Skip - characteristic markers

    # Go
    go-function) echo "function" ;;
    go-method) echo "method" ;;
    go-struct) echo "class" ;;
    go-interface) echo "interface" ;;
    go-has-*) echo "" ;;  # Skip - characteristic markers

    # Swift
    swift-function|swift-throwing-function|swift-public-function|swift-private-function) echo "function" ;;
    swift-class|swift-class-with-inheritance) echo "class" ;;
    swift-struct) echo "class" ;;
    swift-protocol) echo "interface" ;;
    swift-extension) echo "class" ;;
    swift-enum) echo "class" ;;
    swift-actor) echo "class" ;;
    swift-typealias) echo "" ;;  # Skip type aliases
    swift-init) echo "constructor" ;;
    swift-deinit) echo "method" ;;
    swift-closure) echo "" ;;  # Skip inline closures
    swift-property) echo "property" ;;

    *) echo "" ;;
  esac
}

# Extract visibility from rule ID
extract_visibility() {
  local rule_id="$1"

  case "$rule_id" in
    *-public-*|swift-public-function) echo "public" ;;
    *-private-*|swift-private-function) echo "private" ;;
    *) echo "null" ;;
  esac
}

# Check if rule indicates async
is_async_rule() {
  local rule_id="$1"
  case "$rule_id" in
    cs-async-method|py-async-function|py-async-method)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

# Check for loops in source text
has_loops() {
  local source="$1"
  local lang="$2"

  case "$lang" in
    csharp|typescript)
      if [[ "$source" =~ (for[[:space:]]*\(|foreach[[:space:]]*\(|while[[:space:]]*\(|do[[:space:]]*\{) ]]; then
        return 0
      fi
      ;;
    python)
      if [[ "$source" =~ (for[[:space:]]|while[[:space:]]) ]]; then
        return 0
      fi
      ;;
    go)
      if [[ "$source" =~ for[[:space:]] ]]; then
        return 0
      fi
      ;;
    swift)
      if [[ "$source" =~ (for[[:space:]]|while[[:space:]]) ]]; then
        return 0
      fi
      ;;
  esac
  return 1
}

# Check for try-catch in source text
has_try_catch() {
  local source="$1"
  local lang="$2"

  case "$lang" in
    csharp|typescript)
      if [[ "$source" =~ try[[:space:]]*\{ ]]; then
        return 0
      fi
      ;;
    python)
      if [[ "$source" =~ try: ]]; then
        return 0
      fi
      ;;
    go)
      # Go uses defer/recover pattern
      if [[ "$source" =~ recover\( ]]; then
        return 0
      fi
      ;;
    swift)
      if [[ "$source" =~ (do[[:space:]]*\{|try[[:space:]]) ]]; then
        return 0
      fi
      ;;
  esac
  return 1
}

# Check for async patterns in source text
has_async() {
  local source="$1"
  local lang="$2"

  case "$lang" in
    csharp)
      if [[ "$source" =~ (async[[:space:]]|await[[:space:]]) ]]; then
        return 0
      fi
      ;;
    typescript)
      if [[ "$source" =~ (async[[:space:]]|await[[:space:]]|Promise) ]]; then
        return 0
      fi
      ;;
    python)
      if [[ "$source" =~ (async[[:space:]]def|await[[:space:]]) ]]; then
        return 0
      fi
      ;;
    go)
      if [[ "$source" =~ go[[:space:]] ]]; then
        return 0
      fi
      ;;
    swift)
      if [[ "$source" =~ (async[[:space:]]|await[[:space:]]) ]]; then
        return 0
      fi
      ;;
  esac
  return 1
}

# Check for throw statements
has_throw() {
  local source="$1"
  local lang="$2"

  case "$lang" in
    csharp|typescript)
      if [[ "$source" =~ throw[[:space:]] ]]; then
        return 0
      fi
      ;;
    python)
      if [[ "$source" =~ raise[[:space:]] ]]; then
        return 0
      fi
      ;;
    go)
      if [[ "$source" =~ panic\( ]]; then
        return 0
      fi
      ;;
    swift)
      if [[ "$source" =~ throw[[:space:]] ]]; then
        return 0
      fi
      ;;
  esac
  return 1
}

# Extract function calls from source (simple regex approach)
extract_calls() {
  local source="$1"
  local lang="$2"

  # Extract function/method call names from BODY only (skip first line which is the signature)
  # This avoids counting the function definition itself as a call
  local body
  body=$(echo "$source" | tail -n +2)

  # Match: word( patterns (function calls)
  local calls=""
  calls=$(echo "$body" | grep -oE '\b[a-zA-Z_][a-zA-Z0-9_]*\s*\(' | sed 's/[[:space:]]*($//' | sort -u | head -20 | tr '\n' ',' | sed 's/,$//')

  echo "$calls"
}

# Check for recursion (function calls itself)
has_recursion() {
  local name="$1"
  local calls="$2"

  if [[ ",$calls," == *",$name,"* ]]; then
    return 0
  fi
  return 1
}

# Count parameters from parameter string
count_params() {
  local params="$1"

  # Remove parentheses and whitespace
  params="${params//[()]/}"
  params="${params#"${params%%[![:space:]]*}"}"
  params="${params%"${params##*[![:space:]]}"}"

  if [[ -z "$params" ]]; then
    echo 0
    return
  fi

  # Count commas + 1
  local count
  count=$(($(echo "$params" | tr -cd ',' | wc -c) + 1))
  echo "$count"
}

# Extract modifiers from source
extract_modifiers() {
  local source="$1"
  local lang="$2"
  local is_async="$3"

  local mods=""

  # Add async if detected
  if [[ "$is_async" == "true" ]]; then
    mods="async"
  fi

  case "$lang" in
    csharp)
      [[ "$source" =~ static[[:space:]] ]] && mods="${mods:+$mods,}static"
      [[ "$source" =~ abstract[[:space:]] ]] && mods="${mods:+$mods,}abstract"
      [[ "$source" =~ virtual[[:space:]] ]] && mods="${mods:+$mods,}virtual"
      [[ "$source" =~ override[[:space:]] ]] && mods="${mods:+$mods,}override"
      [[ "$source" =~ sealed[[:space:]] ]] && mods="${mods:+$mods,}sealed"
      [[ "$source" =~ partial[[:space:]] ]] && mods="${mods:+$mods,}partial"
      ;;
    typescript)
      [[ "$source" =~ static[[:space:]] ]] && mods="${mods:+$mods,}static"
      [[ "$source" =~ =\> ]] && mods="${mods:+$mods,}arrow"
      [[ "$source" =~ export[[:space:]] ]] && mods="${mods:+$mods,}exported"
      ;;
    python)
      [[ "$source" =~ @staticmethod ]] && mods="${mods:+$mods,}static"
      [[ "$source" =~ @classmethod ]] && mods="${mods:+$mods,}classmethod"
      [[ "$source" =~ @property ]] && mods="${mods:+$mods,}property"
      [[ "$source" =~ ^@[a-zA-Z] ]] && mods="${mods:+$mods,}decorated"
      ;;
    go)
      # Go doesn't have traditional modifiers
      ;;
    swift)
      [[ "$source" =~ static[[:space:]] ]] && mods="${mods:+$mods,}static"
      [[ "$source" =~ class[[:space:]]func ]] && mods="${mods:+$mods,}class"
      [[ "$source" =~ mutating[[:space:]] ]] && mods="${mods:+$mods,}mutating"
      [[ "$source" =~ @objc ]] && mods="${mods:+$mods,}objc"
      ;;
  esac

  echo "$mods"
}

# Build JSON array from comma-separated string
to_json_array() {
  local items="$1"

  if [[ -z "$items" ]]; then
    echo "[]"
    return
  fi

  local result="["
  local first=true

  IFS=',' read -ra arr <<< "$items"
  for item in "${arr[@]}"; do
    item="${item#"${item%%[![:space:]]*}"}"
    item="${item%"${item##*[![:space:]]}"}"
    [[ -z "$item" ]] && continue

    if [[ "$first" != "true" ]]; then
      result+=","
    fi
    # Escape quotes in item
    item="${item//\\/\\\\}"
    item="${item//\"/\\\"}"
    result+="\"$item\""
    first=false
  done

  result+="]"
  echo "$result"
}

# Extract units from a single file using ast-grep
extract_file() {
  local file="$1"
  local lang_info

  lang_info=$(get_language_info "$file")
  [[ -z "$lang_info" ]] && return

  local lang="${lang_info%%:*}"
  local rules_file="${lang_info#*:}"

  [[ ! -f "$rules_file" ]] && return

  # Run ast-grep with --json output
  local sg_output
  sg_output=$(sg scan --rule "$rules_file" "$file" --json 2>/dev/null) || return

  # Parse JSON output and transform to our schema
  # sg outputs an array of matches

  # Get file-level metadata
  local is_test=false
  is_test_file "$file" && is_test=true

  local layer
  layer=$(infer_layer "$file")

  local tests_unit=""
  if [[ "$is_test" == "true" ]]; then
    tests_unit=$(infer_tests_unit "$file")
  fi

  # Process each match from sg output
  # Use jq to parse and transform, then enrich with bash-computed fields
  echo "$sg_output" | jq -c --arg file "$file" --arg lang "$lang" \
    --argjson is_test "$is_test" --arg layer "$layer" --arg tests_unit "$tests_unit" '
    # Input is array of matches
    [.[] | select(.ruleId != null) | {
      ruleId: .ruleId,
      text: .text,
      range: .range,
      metaVariables: (.metaVariables // {})
    }]
  ' | jq -c '.[]' | while IFS= read -r match; do
    # Parse each match
    local rule_id text start_line end_line meta_vars
    rule_id=$(echo "$match" | jq -r '.ruleId')
    text=$(echo "$match" | jq -r '.text')
    start_line=$(echo "$match" | jq -r '.range.start.line')
    end_line=$(echo "$match" | jq -r '.range.end.line')
    meta_vars=$(echo "$match" | jq -c '.metaVariables')

    # Map rule to type
    local unit_type
    unit_type=$(map_rule_to_type "$rule_id")
    [[ -z "$unit_type" ]] && continue

    # Convert 0-indexed to 1-indexed
    start_line=$((start_line + 1))
    end_line=$((end_line + 1))

    # Extract name from metaVariables
    # ast-grep structure: {single: {NAME: {text: "name"}, PARAMS: {...}}, multi: {...}}
    local name=""
    name=$(echo "$meta_vars" | jq -r '
      if .single.NAME.text then .single.NAME.text
      elif .NAME.text then .NAME.text
      else ""
      end
    ')

    # Fallback: try to extract name from text for rules that might not capture it
    if [[ -z "$name" || "$name" == "null" ]]; then
      case "$rule_id" in
        ts-function)
          name=$(echo "$text" | grep -oE 'function[[:space:]]+([a-zA-Z_][a-zA-Z0-9_]*)' | head -1 | awk '{print $2}')
          ;;
        ts-class)
          name=$(echo "$text" | grep -oE 'class[[:space:]]+([a-zA-Z_][a-zA-Z0-9_]*)' | head -1 | awk '{print $2}')
          ;;
        ts-interface)
          name=$(echo "$text" | grep -oE 'interface[[:space:]]+([a-zA-Z_][a-zA-Z0-9_]*)' | head -1 | awk '{print $2}')
          ;;
        swift-init)
          name="init"
          ;;
        swift-deinit)
          name="deinit"
          ;;
        *)
          # Generic fallback - get first word-like identifier
          name=$(echo "$text" | head -1 | grep -oE '\b[a-zA-Z_][a-zA-Z0-9_]*' | head -1)
          ;;
      esac
    fi

    [[ -z "$name" || "$name" == "null" ]] && continue

    # Extract params
    # ast-grep structure: {single: {PARAMS: {text: "(params)"}}}
    local params=""
    params=$(echo "$meta_vars" | jq -r '
      if .single.PARAMS.text then .single.PARAMS.text
      elif .PARAMS.text then .PARAMS.text
      else ""
      end
    ')
    [[ "$params" == "null" ]] && params=""

    # Extract return type
    # ast-grep structure: {single: {RET: {text: "return_type"}, TYPE: {text: "type"}}}
    local return_type=""
    return_type=$(echo "$meta_vars" | jq -r '
      if .single.RET.text then .single.RET.text
      elif .RET.text then .RET.text
      elif .single.TYPE.text then .single.TYPE.text
      elif .TYPE.text then .TYPE.text
      else ""
      end
    ')
    [[ "$return_type" == "null" ]] && return_type=""

    # Compute characteristics
    local line_count=$((end_line - start_line + 1))
    local param_count
    param_count=$(count_params "$params")

    # Visibility
    local visibility
    visibility=$(extract_visibility "$rule_id")

    # Check for C# visibility modifiers in source
    if [[ "$visibility" == "null" && "$lang" == "csharp" ]]; then
      if [[ "$text" =~ public[[:space:]] ]]; then
        visibility="public"
      elif [[ "$text" =~ private[[:space:]] ]]; then
        visibility="private"
      elif [[ "$text" =~ protected[[:space:]] ]]; then
        visibility="protected"
      elif [[ "$text" =~ internal[[:space:]] ]]; then
        visibility="internal"
      fi
    fi

    # Check for TypeScript export
    if [[ "$visibility" == "null" && "$lang" == "typescript" ]]; then
      if [[ "$text" =~ ^export[[:space:]] ]]; then
        visibility="exported"
      fi
    fi

    # Async check
    local is_async=false
    is_async_rule "$rule_id" && is_async=true
    [[ "$is_async" == "false" ]] && has_async "$text" "$lang" && is_async=true

    # Other characteristics
    local loops=false try_catch=false throw=false
    has_loops "$text" "$lang" && loops=true
    has_try_catch "$text" "$lang" && try_catch=true
    has_throw "$text" "$lang" && throw=true

    # Extract calls and check recursion
    local calls_str
    calls_str=$(extract_calls "$text" "$lang")

    local recursion=false
    has_recursion "$name" "$calls_str" && recursion=true

    # Build modifiers
    local mods_str
    mods_str=$(extract_modifiers "$text" "$lang" "$is_async")

    # Build JSON arrays
    local calls_json mods_json
    calls_json=$(to_json_array "$calls_str")
    mods_json=$(to_json_array "$mods_str")

    # Escape strings for JSON
    name="${name//\\/\\\\}"
    name="${name//\"/\\\"}"
    params="${params//\\/\\\\}"
    params="${params//\"/\\\"}"
    return_type="${return_type//\\/\\\\}"
    return_type="${return_type//\"/\\\"}"

    # Build JSON output
    local json_out='{'
    json_out+="\"name\":\"$name\""
    json_out+=",\"file\":\"$file\""
    json_out+=",\"type\":\"$unit_type\""
    json_out+=",\"lines\":[$start_line,$end_line]"
    json_out+=",\"is_test\":$is_test"

    if [[ -n "$tests_unit" ]]; then
      tests_unit="${tests_unit//\\/\\\\}"
      tests_unit="${tests_unit//\"/\\\"}"
      json_out+=",\"tests_unit\":\"$tests_unit\""
    else
      json_out+=",\"tests_unit\":null"
    fi

    json_out+=",\"layer\":\"$layer\""
    json_out+=",\"calls\":$calls_json"
    json_out+=",\"params\":\"$params\""
    json_out+=",\"param_count\":$param_count"

    if [[ -n "$return_type" ]]; then
      json_out+=",\"return_type\":\"$return_type\""
    else
      json_out+=",\"return_type\":null"
    fi

    json_out+=",\"has_loops\":$loops"
    json_out+=",\"has_async\":$is_async"
    json_out+=",\"has_try_catch\":$try_catch"
    json_out+=",\"has_throw\":$throw"
    json_out+=",\"has_recursion\":$recursion"
    json_out+=",\"line_count\":$line_count"

    if [[ "$visibility" != "null" ]]; then
      json_out+=",\"visibility\":\"$visibility\""
    else
      json_out+=",\"visibility\":null"
    fi

    json_out+=",\"modifiers\":$mods_json"
    json_out+='}'

    echo "$json_out"
  done
}

# =============================================================================
# File List Handling
# =============================================================================

get_files() {
  local args=("$@")

  if [[ ${#args[@]} -eq 0 ]]; then
    git diff --name-only 2>/dev/null
  elif [[ "${args[0]}" == "--staged" ]]; then
    git diff --cached --name-only 2>/dev/null
  elif [[ "${args[0]}" == "--files" ]]; then
    printf '%s\n' "${args[@]:1}"
  else
    git diff --name-only "${args[@]}" 2>/dev/null
  fi
}

# Skip non-code files
should_skip_file() {
  local file="$1"
  local ext="${file##*.}"

  case "$ext" in
    md|json|yaml|yml|txt|lock|toml|xml|config|html|css|scss|less|svg|png|jpg|jpeg|gif|ico|woff|woff2|ttf|eot)
      return 0
      ;;
  esac

  # Skip lockfiles and generated files
  case "$file" in
    *-lock.json|*.lock|*.generated.*|*.pb.*|*_generated.*|*.min.js|*.bundle.js)
      return 0
      ;;
    */__snapshots__/*|*/vendor/*|*/node_modules/*)
      return 0
      ;;
  esac

  return 1
}

# =============================================================================
# Main
# =============================================================================

main() {
  # Handle --status flag
  [[ "${1:-}" == "--status" ]] && check_status

  # Check dependencies
  check_deps

  local files
  files=$(get_files "$@")

  local skipped_files=()
  local all_units=""
  local first=true

  while IFS= read -r file; do
    [[ -z "$file" ]] && continue
    [[ ! -f "$file" ]] && continue

    # Skip non-code files
    if should_skip_file "$file"; then
      continue
    fi

    # Check if we support this language
    local lang_info
    lang_info=$(get_language_info "$file")
    if [[ -z "$lang_info" ]]; then
      skipped_files+=("$file")
      continue
    fi

    # Extract units from this file
    local file_units
    file_units=$(extract_file "$file")

    if [[ -n "$file_units" ]]; then
      while IFS= read -r unit; do
        [[ -z "$unit" ]] && continue
        if [[ "$first" != "true" ]]; then
          all_units+=","
        fi
        all_units+="$unit"
        first=false
      done <<< "$file_units"
    fi
  done <<< "$files"

  # Build skipped files array
  local skipped_json="["
  local sf_first=true
  if [[ ${#skipped_files[@]} -gt 0 ]]; then
    for sf in "${skipped_files[@]}"; do
      if [[ "$sf_first" != "true" ]]; then
        skipped_json+=","
      fi
      skipped_json+="\"$sf\""
      sf_first=false
    done
  fi
  skipped_json+="]"

  # Deduplicate units by file+name+lines (multiple rules can match same code)
  # Keep the most complete entry (most non-null fields) for each unique unit
  local final_json
  final_json=$(echo "{\"units\":[$all_units],\"skipped_files\":$skipped_json,\"sg_available\":true}" | jq '
    .units |= (
      group_by([.file, .name, .lines[0], .lines[1]]) |
      map(
        # Sort by number of true boolean fields to get most feature-rich entry
        sort_by(-([.has_loops, .has_async, .has_try_catch, .has_throw, .has_recursion] | map(if . then 1 else 0 end) | add)) |
        .[0]
      )
    )
  ')

  echo "$final_json"
}

main "$@"
