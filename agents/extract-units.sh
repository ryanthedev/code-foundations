#!/usr/bin/env bash
#
# extract-units.sh v3.5.1 - AST extraction with diff context
#
# Extract semantic units from code using ast-grep, with optional diff context.
#
# Usage:
#   ./extract-units.sh [--staged | --files file1 file2 | <git-diff-args>]
#   ./extract-units.sh --status   # Check ast-grep availability
#
# Output: JSONL (one JSON object per line) with:
#   - name, file, type, lines, layer, is_test, tests_unit
#   - calls, params, param_count, return_type
#   - has_loops, has_async, has_try_catch, has_throw, has_recursion
#   - visibility, modifiers
#   - diff, changeStatus, summary (when using git diff args)
#
# Requirements: sg (ast-grep), jq
#

set -euo pipefail

VERSION="3.5.1"
echo "[extract-units.sh v$VERSION]" >&2

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SG_RULES_DIR="$SCRIPT_DIR/sg-rules"
DELIM=$'\x1f'

# =============================================================================
# Dependency Check
# =============================================================================

check_deps() {
  local missing=""
  if ! command -v sg &>/dev/null; then
    missing="sg (ast-grep)"
  fi
  if ! command -v jq &>/dev/null; then
    [[ -n "$missing" ]] && missing="$missing, jq" || missing="jq"
  fi
  if [[ -n "$missing" ]]; then
    echo "{\"error\": \"Missing: $missing\", \"sg_available\": false}" >&2
    exit 1
  fi
}

check_status() {
  if ! command -v sg &>/dev/null; then
    echo '{"sg_available": false, "error": "ast-grep not installed"}'
    exit 0
  fi
  local sg_version rules_found=0
  sg_version=$(sg --version 2>/dev/null | head -1)
  for rule in "$SG_RULES_DIR"/*.yaml; do
    [[ -f "$rule" ]] && ((rules_found++)) || true
  done
  echo "{\"sg_available\": true, \"version\": \"$sg_version\", \"rules_found\": $rules_found}"
  exit 0
}

# =============================================================================
# Test/Layer Detection
# =============================================================================

is_test_file() {
  local filepath="$1" basename="${filepath##*/}"
  [[ "$basename" == *".test."* || "$basename" == *".spec."* ]] && return 0
  [[ "$basename" == test_* || "$basename" == *"_test."* ]] && return 0
  [[ "$basename" == *"Test."* || "$basename" == *"Tests."* || "$basename" == *"Spec."* || "$basename" == *"Specs."* ]] && return 0
  [[ "$filepath" == *"__tests__"* || "$filepath" == *"/tests/"* || "$filepath" == *"/test/"* ]] && return 0
  [[ "$filepath" == *".Tests."* || "$filepath" == *".Test."* ]] && return 0
  return 1
}

infer_tests_unit() {
  local filepath="$1" basename="${filepath##*/}" name_no_ext="${basename%.*}"
  [[ "$name_no_ext" == *".test" || "$name_no_ext" == *".spec" ]] && name_no_ext="${name_no_ext%.*}"
  [[ "$basename" == *".test."* ]] && echo "${basename%.test.*}" && return
  [[ "$basename" == *".spec."* ]] && echo "${basename%.spec.*}" && return
  [[ "$basename" == test_* ]] && echo "${name_no_ext#test_}" && return
  [[ "$name_no_ext" == *_test ]] && echo "${name_no_ext%_test}" && return
  [[ "$name_no_ext" == *Tests ]] && echo "${name_no_ext%Tests}" && return
  [[ "$name_no_ext" == *Test ]] && echo "${name_no_ext%Test}" && return
  [[ "$name_no_ext" == *Specs ]] && echo "${name_no_ext%Specs}" && return
  [[ "$name_no_ext" == *Spec ]] && echo "${name_no_ext%Spec}" && return
  echo ""
}

LAYER_OVERRIDES="" LAYER_OVERRIDES_LOADED=false

load_layer_overrides() {
  [[ "$LAYER_OVERRIDES_LOADED" == "true" ]] && return
  LAYER_OVERRIDES_LOADED=true
  local config_file=".code-foundations/layers.yaml"
  [[ ! -f "$config_file" ]] && return
  local in_overrides=false
  while IFS= read -r line; do
    [[ "$line" =~ ^overrides: ]] && in_overrides=true && continue
    [[ "$in_overrides" == "true" && "$line" =~ ^[a-z] && ! "$line" =~ ^[[:space:]] ]] && break
    if [[ "$in_overrides" == "true" && "$line" =~ ^[[:space:]]+(\"[^\"]+\"|\'[^\']+\'|[^:]+):[[:space:]]*([a-z]+) ]]; then
      local pattern="${BASH_REMATCH[1]}" layer="${BASH_REMATCH[2]}"
      pattern="${pattern#\"}" && pattern="${pattern%\"}" && pattern="${pattern#\'}" && pattern="${pattern%\'}"
      pattern="${pattern#"${pattern%%[![:space:]]*}"}" && pattern="${pattern%"${pattern##*[![:space:]]}"}"
      LAYER_OVERRIDES+="${pattern}:${layer} "
    fi
  done < "$config_file"
}

check_layer_override() {
  local filepath="$1"
  load_layer_overrides
  [[ -z "$LAYER_OVERRIDES" ]] && return 1
  for entry in $LAYER_OVERRIDES; do
    local pattern="${entry%:*}" layer="${entry#*:}"
    [[ "$filepath" == *"$pattern"* ]] && echo "$layer" && return 0
  done
  return 1
}

infer_layer() {
  local filepath="$1" basename="${filepath##*/}"
  local override_layer
  override_layer=$(check_layer_override "$filepath") && echo "$override_layer" && return
  is_test_file "$filepath" && echo "test" && return
  [[ "$filepath" == *"/api/"* || "$filepath" == *"/Api/"* || "$filepath" == *"/controllers/"* || "$filepath" == *"/Controllers/"* || "$filepath" == *"/routes/"* || "$filepath" == *"/handlers/"* ]] && echo "api" && return
  [[ "$filepath" == *"/services/"* || "$filepath" == *"/Services/"* || "$filepath" == *"/usecases/"* || "$filepath" == *"/App/"* ]] && echo "service" && return
  [[ "$filepath" == *"/domain/"* || "$filepath" == *"/Domain/"* || "$filepath" == *"/models/"* || "$filepath" == *"/Models/"* || "$filepath" == *"/entities/"* || "$filepath" == *"/Core/"* ]] && echo "domain" && return
  [[ "$filepath" == *"/data/"* || "$filepath" == *"/Data/"* || "$filepath" == *"/repositories/"* || "$filepath" == *"/Repositories/"* || "$filepath" == *"/persistence/"* ]] && echo "data" && return
  [[ "$filepath" == *"/Adapters/"* || "$filepath" == *"/adapters/"* || "$filepath" == *"/providers/"* || "$filepath" == *"/clients/"* || "$filepath" == *"/gateways/"* || "$filepath" == *"/external/"* ]] && echo "integration" && return
  [[ "$filepath" == *"/infra/"* || "$filepath" == *"/infrastructure/"* || "$filepath" == *"/Middleware/"* || "$filepath" == *"/middleware/"* || "$filepath" == *"/Extensions/"* || "$filepath" == *"/hosting/"* ]] && echo "infra" && return
  [[ "$filepath" == *"/config/"* || "$filepath" == *"/Config/"* || "$filepath" == *"/Constants/"* || "$filepath" == *"/constants/"* ]] && echo "config" && return
  echo "unknown"
}

# =============================================================================
# Language & Unit Extraction
# =============================================================================

get_language_info() {
  local ext="${1##*.}"
  case "$ext" in
    cs) echo "csharp:$SG_RULES_DIR/csharp.yaml" ;;
    ts|tsx) echo "typescript:$SG_RULES_DIR/typescript.yaml" ;;
    js|jsx|mjs|cjs) echo "typescript:$SG_RULES_DIR/typescript.yaml" ;;
    py) echo "python:$SG_RULES_DIR/python.yaml" ;;
    go) echo "go:$SG_RULES_DIR/go.yaml" ;;
    swift) echo "swift:$SG_RULES_DIR/swift.yaml" ;;
    *) echo "" ;;
  esac
}

map_rule_to_type() {
  local rule_id="$1"
  case "$rule_id" in
    cs-method|cs-async-method) echo "method" ;;
    cs-class|cs-primary-constructor|cs-record|cs-enum|cs-struct|cs-inline-array) echo "class" ;;
    cs-interface|cs-delegate) echo "interface" ;;
    cs-constructor|cs-partial-constructor) echo "constructor" ;;
    cs-property|cs-partial-property|cs-indexer) echo "property" ;;
    cs-operator|cs-compound-assignment-op|cs-conversion-operator) echo "method" ;;
    cs-local-function) echo "function" ;;
    cs-event|cs-partial-event) echo "field" ;;
    ts-function) echo "function" ;;
    ts-arrow-const|ts-arrow-let) echo "function" ;;
    ts-method) echo "method" ;;
    ts-class) echo "class" ;;
    ts-interface) echo "interface" ;;
    py-function|py-function-typed|py-async-function) echo "function" ;;
    py-method|py-method-typed|py-async-method) echo "method" ;;
    py-class|py-class-with-bases) echo "class" ;;
    go-function) echo "function" ;;
    go-method) echo "method" ;;
    go-struct) echo "class" ;;
    go-interface) echo "interface" ;;
    swift-function|swift-throwing-function|swift-public-function|swift-private-function) echo "function" ;;
    swift-class|swift-class-with-inheritance|swift-struct|swift-extension|swift-enum|swift-actor) echo "class" ;;
    swift-protocol) echo "interface" ;;
    swift-init) echo "constructor" ;;
    swift-deinit|swift-property) echo "method" ;;
    *) echo "" ;;
  esac
}

extract_visibility() {
  local rule_id="$1"
  case "$rule_id" in
    *-public-*|swift-public-function) echo "public" ;;
    *-private-*|swift-private-function) echo "private" ;;
    *) echo "null" ;;
  esac
}

has_loops() {
  local source="$1" lang="$2"
  case "$lang" in
    csharp|typescript) [[ "$source" =~ (for[[:space:]]*\(|foreach[[:space:]]*\(|while[[:space:]]*\(|do[[:space:]]*\{) ]] && return 0 ;;
    python|swift) [[ "$source" =~ (for[[:space:]]|while[[:space:]]) ]] && return 0 ;;
    go) [[ "$source" =~ for[[:space:]] ]] && return 0 ;;
  esac
  return 1
}

has_try_catch() {
  local source="$1" lang="$2"
  case "$lang" in
    csharp|typescript) [[ "$source" =~ try[[:space:]]*\{ ]] && return 0 ;;
    python) [[ "$source" =~ try: ]] && return 0 ;;
    go) [[ "$source" =~ recover\( ]] && return 0 ;;
    swift) [[ "$source" =~ (do[[:space:]]*\{|try[[:space:]]) ]] && return 0 ;;
  esac
  return 1
}

has_async() {
  local source="$1" lang="$2"
  case "$lang" in
    csharp|swift) [[ "$source" =~ (async[[:space:]]|await[[:space:]]) ]] && return 0 ;;
    typescript) [[ "$source" =~ (async[[:space:]]|await[[:space:]]|Promise) ]] && return 0 ;;
    python) [[ "$source" =~ (async[[:space:]]def|await[[:space:]]) ]] && return 0 ;;
    go) [[ "$source" =~ go[[:space:]] ]] && return 0 ;;
  esac
  return 1
}

has_throw() {
  local source="$1" lang="$2"
  case "$lang" in
    csharp|typescript|swift) [[ "$source" =~ throw[[:space:]] ]] && return 0 ;;
    python) [[ "$source" =~ raise[[:space:]] ]] && return 0 ;;
    go) [[ "$source" =~ panic\( ]] && return 0 ;;
  esac
  return 1
}

extract_calls() {
  local body
  body=$(echo "$1" | tail -n +2)
  echo "$body" | grep -oE '\b[a-zA-Z_][a-zA-Z0-9_]*\s*\(' | sed 's/[[:space:]]*($//' | sort -u | head -20 | tr '\n' ',' | sed 's/,$//'
}

has_recursion() { [[ ",$2," == *",$1,"* ]]; }

count_params() {
  local params="${1//[()]/}"
  params="${params#"${params%%[![:space:]]*}"}"
  params="${params%"${params##*[![:space:]]}"}"
  [[ -z "$params" ]] && echo 0 && return
  echo $(($(echo "$params" | tr -cd ',' | wc -c) + 1))
}

extract_modifiers() {
  local source="$1" lang="$2" is_async="$3" mods=""
  [[ "$is_async" == "true" ]] && mods="async"
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
      ;;
    swift)
      [[ "$source" =~ static[[:space:]] ]] && mods="${mods:+$mods,}static"
      [[ "$source" =~ mutating[[:space:]] ]] && mods="${mods:+$mods,}mutating"
      ;;
  esac
  echo "$mods"
}

to_json_array() {
  local items="$1"
  [[ -z "$items" ]] && echo "[]" && return
  local result="[" first=true
  IFS=',' read -ra arr <<< "$items"
  for item in "${arr[@]}"; do
    item="${item#"${item%%[![:space:]]*}"}"
    item="${item%"${item##*[![:space:]]}"}"
    [[ -z "$item" ]] && continue
    [[ "$first" != "true" ]] && result+=","
    item="${item//\\/\\\\}" && item="${item//\"/\\\"}"
    result+="\"$item\""
    first=false
  done
  echo "$result]"
}

extract_file() {
  local file="$1" lang_info
  lang_info=$(get_language_info "$file")
  [[ -z "$lang_info" ]] && return
  local lang="${lang_info%%:*}" rules_file="${lang_info#*:}"
  [[ ! -f "$rules_file" ]] && return
  local sg_output
  sg_output=$(sg scan --rule "$rules_file" "$file" --json 2>/dev/null) || return
  local is_test=false layer tests_unit=""
  is_test_file "$file" && is_test=true
  layer=$(infer_layer "$file")
  [[ "$is_test" == "true" ]] && tests_unit=$(infer_tests_unit "$file")

  echo "$sg_output" | jq -c '.[] | select(.ruleId != null)' | while IFS= read -r match; do
    local rule_id text start_line end_line meta_vars
    rule_id=$(echo "$match" | jq -r '.ruleId')
    text=$(echo "$match" | jq -r '.text')
    start_line=$(echo "$match" | jq -r '.range.start.line')
    end_line=$(echo "$match" | jq -r '.range.end.line')
    meta_vars=$(echo "$match" | jq -c '.metaVariables // {}')

    local unit_type
    unit_type=$(map_rule_to_type "$rule_id")
    [[ -z "$unit_type" ]] && continue

    start_line=$((start_line + 1))
    end_line=$((end_line + 1))

    local name=""
    name=$(echo "$meta_vars" | jq -r 'if .single.NAME.text then .single.NAME.text elif .NAME.text then .NAME.text else "" end')
    if [[ -z "$name" || "$name" == "null" ]]; then
      case "$rule_id" in
        ts-function) name=$(echo "$text" | grep -oE 'function[[:space:]]+([a-zA-Z_][a-zA-Z0-9_]*)' | head -1 | awk '{print $2}') ;;
        ts-class) name=$(echo "$text" | grep -oE 'class[[:space:]]+([a-zA-Z_][a-zA-Z0-9_]*)' | head -1 | awk '{print $2}') ;;
        swift-init) name="init" ;;
        swift-deinit) name="deinit" ;;
        *) name=$(echo "$text" | head -1 | grep -oE '\b[a-zA-Z_][a-zA-Z0-9_]*' | head -1) ;;
      esac
    fi
    [[ -z "$name" || "$name" == "null" ]] && continue

    local params="" return_type=""
    params=$(echo "$meta_vars" | jq -r 'if .single.PARAMS.text then .single.PARAMS.text elif .PARAMS.text then .PARAMS.text else "" end')
    [[ "$params" == "null" ]] && params=""
    return_type=$(echo "$meta_vars" | jq -r 'if .single.RET.text then .single.RET.text elif .RET.text then .RET.text elif .single.TYPE.text then .single.TYPE.text else "" end')
    [[ "$return_type" == "null" ]] && return_type=""

    local line_count=$((end_line - start_line + 1))
    local param_count=$(count_params "$params")
    local visibility=$(extract_visibility "$rule_id")
    [[ "$visibility" == "null" && "$lang" == "csharp" ]] && {
      [[ "$text" =~ public[[:space:]] ]] && visibility="public"
      [[ "$text" =~ private[[:space:]] ]] && visibility="private"
      [[ "$text" =~ protected[[:space:]] ]] && visibility="protected"
      [[ "$text" =~ internal[[:space:]] ]] && visibility="internal"
    }
    [[ "$visibility" == "null" && "$lang" == "typescript" && "$text" =~ ^export[[:space:]] ]] && visibility="exported"

    local is_async=false loops=false try_catch=false throw=false recursion=false
    [[ "$rule_id" == *async* ]] && is_async=true
    [[ "$is_async" == "false" ]] && has_async "$text" "$lang" && is_async=true
    has_loops "$text" "$lang" && loops=true
    has_try_catch "$text" "$lang" && try_catch=true
    has_throw "$text" "$lang" && throw=true

    local calls_str=$(extract_calls "$text")
    has_recursion "$name" "$calls_str" && recursion=true
    local mods_str=$(extract_modifiers "$text" "$lang" "$is_async")
    local calls_json=$(to_json_array "$calls_str")
    local mods_json=$(to_json_array "$mods_str")

    name="${name//\\/\\\\}" && name="${name//\"/\\\"}"
    params="${params//\\/\\\\}" && params="${params//\"/\\\"}"
    return_type="${return_type//\\/\\\\}" && return_type="${return_type//\"/\\\"}"

    local json_out='{'
    json_out+="\"name\":\"$name\",\"file\":\"$file\",\"type\":\"$unit_type\",\"lines\":[$start_line,$end_line]"
    json_out+=",\"is_test\":$is_test"
    if [[ -n "$tests_unit" ]]; then
      tests_unit="${tests_unit//\\/\\\\}" && tests_unit="${tests_unit//\"/\\\"}"
      json_out+=",\"tests_unit\":\"$tests_unit\""
    else
      json_out+=",\"tests_unit\":null"
    fi
    json_out+=",\"layer\":\"$layer\",\"calls\":$calls_json,\"params\":\"$params\",\"param_count\":$param_count"
    [[ -n "$return_type" ]] && json_out+=",\"return_type\":\"$return_type\"" || json_out+=",\"return_type\":null"
    json_out+=",\"has_loops\":$loops,\"has_async\":$is_async,\"has_try_catch\":$try_catch,\"has_throw\":$throw,\"has_recursion\":$recursion"
    json_out+=",\"line_count\":$line_count"
    [[ "$visibility" != "null" ]] && json_out+=",\"visibility\":\"$visibility\"" || json_out+=",\"visibility\":null"
    json_out+=",\"modifiers\":$mods_json}"
    echo "$json_out"
  done
}

# =============================================================================
# Diff Context (when using git diff args)
# =============================================================================

get_change_status() {
  case "$1" in
    A) echo "added" ;;
    D) echo "deleted" ;;
    *) echo "modified" ;;
  esac
}

overlaps() { (( $1 <= $4 && $2 >= $3 )); }

generate_summary() {
  local name="$1" diff_content="$2" added=0 removed=0
  while IFS= read -r line; do [[ "$line" =~ ^[+][^+] ]] && ((added++)); done <<< "$diff_content"
  while IFS= read -r line; do [[ "$line" =~ ^[-][^-] ]] && ((removed++)); done <<< "$diff_content"
  if (( removed == 0 && added > 0 )); then echo "Add $name"
  elif (( added > removed * 2 )); then echo "Extend $name"
  elif (( removed > added * 2 )); then echo "Simplify $name"
  else echo "Update $name"
  fi
}

json_escape() {
  local s="$1"
  s="${s//\\/\\\\}" && s="${s//\"/\\\"}" && s="${s//$'\n'/\\n}" && s="${s//$'\r'/\\r}" && s="${s//$'\t'/\\t}"
  echo "$s"
}

parse_diff_hunks() {
  local diff_output="$1" current_file="" hunk_start="" hunk_end="" hunk_content="" in_hunk=false
  while IFS= read -r line; do
    if [[ "$line" =~ ^diff\ --git ]]; then
      [[ -n "$current_file" && -n "$hunk_start" ]] && echo "${current_file}${DELIM}${hunk_start}${DELIM}${hunk_end}${DELIM}${hunk_content}"
      [[ "$line" =~ b/(.+)$ ]] && current_file="${BASH_REMATCH[1]}"
      hunk_start="" hunk_end="" hunk_content="" in_hunk=false
    elif [[ "$line" =~ ^@@\ -[0-9]+(,[0-9]+)?\ \+([0-9]+)(,([0-9]+))?\ @@ ]]; then
      [[ -n "$current_file" && -n "$hunk_start" ]] && echo "${current_file}${DELIM}${hunk_start}${DELIM}${hunk_end}${DELIM}${hunk_content}"
      local newstart="${BASH_REMATCH[2]}" newcount="${BASH_REMATCH[4]:-1}"
      hunk_start="$newstart" hunk_end=$((newstart + newcount - 1)) hunk_content="$line" in_hunk=true
    elif [[ "$line" =~ ^(---|[+][+][+]|index\ |new\ file|deleted\ file|similarity\ ) ]]; then
      continue
    elif [[ "$in_hunk" == "true" ]]; then
      hunk_content+=$'\n'"$line"
    fi
  done <<< "$diff_output"
  [[ -n "$current_file" && -n "$hunk_start" ]] && echo "${current_file}${DELIM}${hunk_start}${DELIM}${hunk_end}${DELIM}${hunk_content}"
}

should_skip_file() {
  local file="$1" ext="${file##*.}"
  case "$ext" in md|json|yaml|yml|txt|lock|toml|xml|config|html|css|scss|less|svg|png|jpg|jpeg|gif|ico|woff|woff2|ttf|eot) return 0 ;; esac
  case "$file" in *-lock.json|*.lock|*.generated.*|*.pb.*|*_generated.*|*.min.js|*.bundle.js|*/__snapshots__/*|*/vendor/*|*/node_modules/*) return 0 ;; esac
  return 1
}

# =============================================================================
# Main
# =============================================================================

main() {
  [[ "${1:-}" == "--status" ]] && check_status
  check_deps

  local mode="diff" files_only=false
  local -a git_args=()

  if [[ $# -eq 0 ]]; then
    git_args=()
  elif [[ "$1" == "--files" ]]; then
    files_only=true
    shift
    for f in "$@"; do echo "$f"; done | while IFS= read -r file; do
      [[ -z "$file" || ! -f "$file" ]] && continue
      should_skip_file "$file" && continue
      [[ -z "$(get_language_info "$file")" ]] && continue
      extract_file "$file"
    done | jq -c 'select(.)' | jq -s 'group_by([.file,.name,.lines[0],.lines[1]]) | map(.[0])[]' -c
    return
  elif [[ "$1" == "--staged" ]]; then
    git_args=(--cached)
  else
    git_args=("$@")
  fi

  # Diff mode: get changed files with status
  local file_statuses diff_output parsed_hunks
  if [[ ${#git_args[@]} -eq 0 ]]; then
    file_statuses=$(git diff --name-status 2>/dev/null)
    diff_output=$(git diff 2>/dev/null)
  else
    file_statuses=$(git diff --name-status "${git_args[@]}" 2>/dev/null)
    diff_output=$(git diff "${git_args[@]}" 2>/dev/null)
  fi
  parsed_hunks=$(parse_diff_hunks "$diff_output")

  while IFS=$'\t' read -r status filepath; do
    [[ -z "$filepath" ]] && continue
    should_skip_file "$filepath" && continue

    local source_file="$filepath" temp_file="" change_status
    change_status=$(get_change_status "$status")

    if [[ "$change_status" == "deleted" ]]; then
      temp_file=$(mktemp)
      git show "HEAD:$filepath" > "$temp_file" 2>/dev/null || { rm -f "$temp_file"; continue; }
      source_file="$temp_file"
    elif [[ ! -f "$filepath" ]]; then
      continue
    fi

    [[ -z "$(get_language_info "$source_file")" ]] && { [[ -n "$temp_file" ]] && rm -f "$temp_file"; continue; }

    local file_hunks
    file_hunks=$(echo "$parsed_hunks" | grep "^${filepath}${DELIM}" || true)
    [[ -z "$file_hunks" ]] && { [[ -n "$temp_file" ]] && rm -f "$temp_file"; continue; }

    extract_file "$source_file" | while IFS= read -r unit_json; do
      [[ -z "$unit_json" ]] && continue
      local unit_lines unit_start unit_end
      unit_lines=$(echo "$unit_json" | jq -r '.lines | "\(.[0]) \(.[1])"')
      read -r unit_start unit_end <<< "$unit_lines"

      local matching_hunks=""
      while IFS= read -r hunk_line; do
        [[ -z "$hunk_line" ]] && continue
        local file_from_hunk hunk_start hunk_end hunk_content
        IFS="$DELIM" read -r file_from_hunk hunk_start hunk_end hunk_content <<< "$hunk_line"
        overlaps "$unit_start" "$unit_end" "$hunk_start" "$hunk_end" && {
          [[ -z "$matching_hunks" ]] && matching_hunks="$hunk_content" || matching_hunks+=$'\n\n'"$hunk_content"
        }
      done <<< "$file_hunks"

      [[ -z "$matching_hunks" ]] && continue

      local diff_field=$(json_escape "$matching_hunks")
      local unit_name=$(echo "$unit_json" | jq -r '.name')
      local summary=$(json_escape "$(generate_summary "$unit_name" "$matching_hunks")")

      # Update file path for deleted files, add diff fields
      echo "$unit_json" | jq -c \
        --arg file "$filepath" \
        --arg diff "$diff_field" \
        --arg summary "$summary" \
        --arg changeStatus "$change_status" \
        '.file = $file | . + {diff: $diff, summary: $summary, changeStatus: $changeStatus}'
    done

    [[ -n "$temp_file" ]] && rm -f "$temp_file"
  done <<< "$file_statuses"
}

main "$@"
