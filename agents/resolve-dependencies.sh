#!/usr/bin/env bash
#
# Resolve external dependencies for investigation agents.
#
# Usage:
#   ./resolve-dependencies.sh --detect <project_root>         # Detect project type
#   ./resolve-dependencies.sh --restore <project_root>        # Download/restore dependencies
#   ./resolve-dependencies.sh --resolve <type> <project_root> # Resolve a specific type/symbol
#   ./resolve-dependencies.sh --cache-status                  # Show cache statistics
#
# Reads config from: agents/dependencies.yaml
#
# Output:
#   --detect:  {"type": "dotnet|java-maven|...", "markers": [...]}
#   --restore: {"success": true, "cached": N, "errors": [...]}
#   --resolve: {"type": "...", "source": "...", "file": "...", "lines": [...]}
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/dependencies.yaml"
CACHE_DIR="${REVIEW_CACHE_DIR:-/tmp/review-dependencies}"

# Colors for logging (disable if not terminal)
if [[ -t 1 ]]; then
  RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[0;33m'; NC='\033[0m'
else
  RED=''; GREEN=''; YELLOW=''; NC=''
fi

log_info()  { echo -e "${GREEN}[INFO]${NC} $*" >&2; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $*" >&2; }
log_error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }

# Detect project type from marker files
# Searches project root and common subdirectories (src/, app/, etc.)
detect_project_type() {
  local project_root="$1"

  # Search paths: root first, then common subdirs
  local search_paths=("$project_root" "$project_root/src" "$project_root/app" "$project_root/lib")

  # .NET: *.csproj, *.sln, *.fsproj
  for path in "${search_paths[@]}"; do
    if compgen -G "$path/*.csproj" >/dev/null 2>&1 || \
       compgen -G "$path/*.sln" >/dev/null 2>&1 || \
       compgen -G "$path/*.fsproj" >/dev/null 2>&1; then
      echo '{"type": "dotnet", "markers": ["*.csproj", "*.sln"]}'
      return 0
    fi
  done

  # Java Maven: pom.xml
  for path in "${search_paths[@]}"; do
    if [[ -f "$path/pom.xml" ]]; then
      echo '{"type": "java-maven", "markers": ["pom.xml"]}'
      return 0
    fi
  done

  # Java Gradle: build.gradle, build.gradle.kts
  for path in "${search_paths[@]}"; do
    if [[ -f "$path/build.gradle" ]] || [[ -f "$path/build.gradle.kts" ]]; then
      echo '{"type": "java-gradle", "markers": ["build.gradle"]}'
      return 0
    fi
  done

  # TypeScript: tsconfig.json, package.json
  for path in "${search_paths[@]}"; do
    if [[ -f "$path/tsconfig.json" ]] || [[ -f "$path/package.json" ]]; then
      echo '{"type": "typescript", "markers": ["tsconfig.json", "package.json"]}'
      return 0
    fi
  done

  # Python: pyproject.toml, setup.py, requirements.txt
  for path in "${search_paths[@]}"; do
    if [[ -f "$path/pyproject.toml" ]] || [[ -f "$path/setup.py" ]] || \
       [[ -f "$path/requirements.txt" ]]; then
      echo '{"type": "python", "markers": ["pyproject.toml", "requirements.txt"]}'
      return 0
    fi
  done

  # Go: go.mod
  for path in "${search_paths[@]}"; do
    if [[ -f "$path/go.mod" ]]; then
      echo '{"type": "go", "markers": ["go.mod"]}'
      return 0
    fi
  done

  echo '{"type": "unknown", "markers": []}'
  return 1
}

# Restore/download dependencies for a project
restore_dependencies() {
  local project_root="$1"
  local project_type errors=()
  local cached=0

  project_type=$(detect_project_type "$project_root" | jq -r '.type')

  if [[ "$project_type" == "unknown" ]]; then
    echo '{"success": false, "error": "Unknown project type"}'
    return 1
  fi

  log_info "Detected project type: $project_type"

  case "$project_type" in
    dotnet)
      log_info "Running: dotnet restore"
      if ! dotnet restore "$project_root" --verbosity quiet 2>/dev/null; then
        errors+=("dotnet restore failed")
      fi
      ;;

    java-maven)
      log_info "Running: mvn dependency:resolve + sources"
      (cd "$project_root" && mvn dependency:resolve -DincludeScope=compile -q 2>/dev/null) || errors+=("mvn resolve failed")
      (cd "$project_root" && mvn dependency:sources -DincludeScope=compile -q 2>/dev/null) || log_warn "Source JARs not available for all deps"
      ;;

    java-gradle)
      log_info "Running: gradle dependencies"
      (cd "$project_root" && ./gradlew dependencies --configuration compileClasspath -q 2>/dev/null) || errors+=("gradle deps failed")
      ;;

    typescript)
      log_info "Running: npm install"
      (cd "$project_root" && npm ci --ignore-scripts 2>/dev/null) || \
      (cd "$project_root" && npm install --ignore-scripts 2>/dev/null) || errors+=("npm install failed")
      ;;

    python)
      log_info "Running: pip install"
      (cd "$project_root" && pip install -e . --quiet 2>/dev/null) || \
      (cd "$project_root" && pip install -r requirements.txt --quiet 2>/dev/null) || errors+=("pip install failed")
      ;;

    go)
      log_info "Running: go mod download"
      (cd "$project_root" && go mod download 2>/dev/null) || errors+=("go mod download failed")
      ;;
  esac

  if [[ ${#errors[@]} -gt 0 ]]; then
    printf '{"success": false, "type": "%s", "errors": %s}\n' \
      "$project_type" "$(printf '%s\n' "${errors[@]}" | jq -R . | jq -s .)"
    return 1
  fi

  echo "{\"success\": true, \"type\": \"$project_type\", \"cached\": $cached}"
}

# Resolve a specific type/symbol
resolve_symbol() {
  local symbol="$1"
  local project_root="$2"
  local project_type

  project_type=$(detect_project_type "$project_root" | jq -r '.type')

  log_info "Resolving symbol: $symbol (project type: $project_type)"

  case "$project_type" in
    dotnet)
      resolve_dotnet_symbol "$symbol" "$project_root"
      ;;

    java-maven|java-gradle)
      resolve_java_symbol "$symbol" "$project_root"
      ;;

    typescript)
      resolve_typescript_symbol "$symbol" "$project_root"
      ;;

    python)
      resolve_python_symbol "$symbol" "$project_root"
      ;;

    go)
      resolve_go_symbol "$symbol" "$project_root"
      ;;

    *)
      echo '{"resolved": false, "error": "Unknown project type"}'
      return 1
      ;;
  esac
}

# .NET: Find type in NuGet packages or decompile DLL
resolve_dotnet_symbol() {
  local symbol="$1"
  local project_root="$2"
  local nuget_cache="$HOME/.nuget/packages"

  # Convert type to path pattern (e.g., "Namespace.Type" -> "Namespace/Type.cs")
  local path_pattern="${symbol//./\/}"

  # Search in NuGet cache (source packages might have src/)
  local found
  found=$(find "$nuget_cache" -type f -name "*.cs" -path "*${path_pattern}*" 2>/dev/null | head -1)

  if [[ -n "$found" ]]; then
    echo "{\"resolved\": true, \"method\": \"source\", \"file\": \"$found\"}"
    return 0
  fi

  # Try to find in project's compiled output and decompile
  local dll
  dll=$(find "$project_root" -type f -name "*.dll" -path "*bin*" 2>/dev/null | head -1)

  if [[ -n "$dll" ]] && command -v ilspycmd &>/dev/null; then
    local decompile_dir="$CACHE_DIR/dotnet/${symbol//./\/}"
    mkdir -p "$decompile_dir"

    log_info "Decompiling $dll for $symbol"
    if ilspycmd --file "$dll" --outputdir "$decompile_dir" --type "$symbol" 2>/dev/null; then
      local decompiled
      decompiled=$(find "$decompile_dir" -name "*.cs" 2>/dev/null | head -1)
      if [[ -n "$decompiled" ]]; then
        echo "{\"resolved\": true, \"method\": \"decompiled\", \"file\": \"$decompiled\"}"
        return 0
      fi
    fi
  fi

  echo '{"resolved": false, "error": "Symbol not found in packages or compiled output"}'
  return 1
}

# Java: Find type in Maven/Gradle cache or decompile JAR
resolve_java_symbol() {
  local symbol="$1"
  local project_root="$2"

  # Convert type to path (e.g., "com.example.Type" -> "com/example/Type.java")
  local path_pattern="${symbol//./\/}.java"

  # Search in Maven cache source JARs
  local m2_cache="$HOME/.m2/repository"
  local source_jar
  source_jar=$(find "$m2_cache" -name "*-sources.jar" -exec unzip -l {} \; 2>/dev/null | \
               grep "$path_pattern" | head -1 | awk '{print $NF}')

  if [[ -n "$source_jar" ]]; then
    # Extract the source file
    local extract_dir="$CACHE_DIR/java/$symbol"
    mkdir -p "$extract_dir"
    local jar_file
    jar_file=$(find "$m2_cache" -name "*-sources.jar" -exec sh -c 'unzip -l "$1" | grep -q "'"$path_pattern"'" && echo "$1"' _ {} \; 2>/dev/null | head -1)
    if [[ -n "$jar_file" ]]; then
      unzip -o -q "$jar_file" "$path_pattern" -d "$extract_dir" 2>/dev/null
      echo "{\"resolved\": true, \"method\": \"source_jar\", \"file\": \"$extract_dir/$path_pattern\"}"
      return 0
    fi
  fi

  # Fallback: decompile with CFR
  if command -v cfr &>/dev/null; then
    local jar
    jar=$(find "$m2_cache" -name "*.jar" ! -name "*-sources.jar" 2>/dev/null | \
          xargs -I{} sh -c 'unzip -l "$1" 2>/dev/null | grep -q "'"${path_pattern%.java}.class"'" && echo "$1"' _ {} | head -1)

    if [[ -n "$jar" ]]; then
      local decompile_dir="$CACHE_DIR/java-decompiled/$symbol"
      mkdir -p "$decompile_dir"
      log_info "Decompiling $jar for $symbol"
      cfr "$jar" --outputdir "$decompile_dir" --silent true 2>/dev/null
      local decompiled="$decompile_dir/$path_pattern"
      if [[ -f "$decompiled" ]]; then
        echo "{\"resolved\": true, \"method\": \"decompiled\", \"file\": \"$decompiled\"}"
        return 0
      fi
    fi
  fi

  echo '{"resolved": false, "error": "Symbol not found in source JARs or decompiled"}'
  return 1
}

# TypeScript: Find type in node_modules
resolve_typescript_symbol() {
  local symbol="$1"
  local project_root="$2"
  local node_modules="$project_root/node_modules"

  # Symbol might be "package/Type" or just "Type"
  local package="${symbol%%/*}"
  local type="${symbol#*/}"

  if [[ -d "$node_modules/$package" ]]; then
    # Search for .ts, .d.ts, or .js files
    local found
    for ext in ts tsx d.ts js; do
      found=$(find "$node_modules/$package" -name "*$type*.$ext" 2>/dev/null | head -1)
      [[ -n "$found" ]] && break
    done

    if [[ -n "$found" ]]; then
      echo "{\"resolved\": true, \"method\": \"node_modules\", \"file\": \"$found\"}"
      return 0
    fi

    # Try main entry point
    local main
    main=$(jq -r '.main // "index.js"' "$node_modules/$package/package.json" 2>/dev/null)
    if [[ -f "$node_modules/$package/$main" ]]; then
      echo "{\"resolved\": true, \"method\": \"package_main\", \"file\": \"$node_modules/$package/$main\"}"
      return 0
    fi
  fi

  echo '{"resolved": false, "error": "Symbol not found in node_modules"}'
  return 1
}

# Python: Find module in site-packages
resolve_python_symbol() {
  local symbol="$1"
  local project_root="$2"

  # Convert module.path.Type to module/path/Type.py
  local path_pattern="${symbol//./\/}.py"

  # Search in venv or site-packages
  local found
  for search_path in "$project_root/.venv/lib" "$HOME/.local/lib" "/usr/local/lib"; do
    found=$(find "$search_path" -path "*site-packages*" -name "*.py" -path "*${path_pattern%/*}*" 2>/dev/null | head -1)
    [[ -n "$found" ]] && break
  done

  if [[ -n "$found" ]]; then
    echo "{\"resolved\": true, \"method\": \"site_packages\", \"file\": \"$found\"}"
    return 0
  fi

  echo '{"resolved": false, "error": "Symbol not found in site-packages"}'
  return 1
}

# Go: Find package in module cache
resolve_go_symbol() {
  local symbol="$1"
  local project_root="$2"

  local gomodcache
  gomodcache=$(go env GOMODCACHE 2>/dev/null || echo "$HOME/go/pkg/mod")

  # Go symbols are like "github.com/pkg/errors.Wrap"
  local package="${symbol%.*}"
  local func="${symbol##*.}"

  local found
  found=$(find "$gomodcache" -path "*${package}*" -name "*.go" 2>/dev/null | head -1)

  if [[ -n "$found" ]]; then
    echo "{\"resolved\": true, \"method\": \"gomodcache\", \"file\": \"$found\"}"
    return 0
  fi

  echo '{"resolved": false, "error": "Symbol not found in GOMODCACHE"}'
  return 1
}

# Show cache status
cache_status() {
  local total_size cached_files

  if [[ -d "$CACHE_DIR" ]]; then
    total_size=$(du -sh "$CACHE_DIR" 2>/dev/null | cut -f1)
    cached_files=$(find "$CACHE_DIR" -type f 2>/dev/null | wc -l | tr -d ' ')
  else
    total_size="0"
    cached_files="0"
  fi

  echo "{\"cache_dir\": \"$CACHE_DIR\", \"size\": \"$total_size\", \"files\": $cached_files}"
}

# Main
case "${1:-}" in
  --detect)
    [[ -z "${2:-}" ]] && { echo "Usage: $0 --detect <project_root>"; exit 1; }
    detect_project_type "$2"
    ;;

  --restore)
    [[ -z "${2:-}" ]] && { echo "Usage: $0 --restore <project_root>"; exit 1; }
    restore_dependencies "$2"
    ;;

  --resolve)
    [[ -z "${2:-}" || -z "${3:-}" ]] && { echo "Usage: $0 --resolve <symbol> <project_root>"; exit 1; }
    resolve_symbol "$2" "$3"
    ;;

  --cache-status)
    cache_status
    ;;

  *)
    echo "Usage: $0 [--detect|--restore|--resolve|--cache-status] ..."
    exit 1
    ;;
esac
