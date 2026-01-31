#!/usr/bin/env bash
#
# Setup tree-sitter CLI and grammars for AST-powered code review.
#
# Usage:
#   ./setup-tree-sitter.sh              # Install core grammars
#   ./setup-tree-sitter.sh --all        # Install all supported grammars
#   ./setup-tree-sitter.sh --status     # Check current status only
#   ./setup-tree-sitter.sh --languages  # List available grammars
#
# Environment:
#   GRAMMAR_DIR  - Where to install grammars (default: ~/repos/tree-sitter-grammars)
#

set -euo pipefail

# Configuration
GRAMMAR_DIR="${GRAMMAR_DIR:-$HOME/repos/tree-sitter-grammars}"

# Core grammars (most common languages)
CORE_GRAMMARS=(
  "tree-sitter/tree-sitter-javascript"
  "tree-sitter/tree-sitter-typescript"
  "tree-sitter/tree-sitter-python"
  "tree-sitter/tree-sitter-go"
  "tree-sitter/tree-sitter-rust"
  "tree-sitter/tree-sitter-java"
  "tree-sitter/tree-sitter-ruby"
  "tree-sitter/tree-sitter-c"
  "tree-sitter/tree-sitter-cpp"
)

# Extended grammars (less common but useful)
EXTENDED_GRAMMARS=(
  "tree-sitter/tree-sitter-c-sharp"
  "tree-sitter/tree-sitter-php"
  "tree-sitter/tree-sitter-scala"
  "elixir-lang/tree-sitter-elixir"
  "elm-tooling/tree-sitter-elm"
  "tree-sitter/tree-sitter-ocaml"
  "tree-sitter/tree-sitter-bash"
  "tree-sitter/tree-sitter-html"
  "tree-sitter/tree-sitter-css"
  "tree-sitter/tree-sitter-json"
)

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}==>${NC} $1"; }
log_success() { echo -e "${GREEN}✓${NC} $1"; }
log_warn() { echo -e "${YELLOW}⚠${NC} $1"; }
log_error() { echo -e "${RED}✗${NC} $1"; }

# Check current status
check_status() {
  echo ""
  log_info "Tree-sitter Status"
  echo ""

  # CLI
  if command -v tree-sitter &>/dev/null; then
    log_success "CLI: tree-sitter $(tree-sitter --version 2>/dev/null | awk '{print $2}')"
  else
    log_error "CLI: not installed"
  fi

  # Grammar directory
  if [[ -d "$GRAMMAR_DIR" ]]; then
    count=$(ls -d "$GRAMMAR_DIR"/tree-sitter-*/ 2>/dev/null | wc -l | tr -d ' ')
    log_success "Grammar dir: $GRAMMAR_DIR ($count grammars)"
  else
    log_error "Grammar dir: not found"
  fi

  # Environment variable
  if [[ -n "${TREE_SITTER_GRAMMAR_DIR:-}" ]]; then
    log_success "Env var: TREE_SITTER_GRAMMAR_DIR=$TREE_SITTER_GRAMMAR_DIR"
  else
    log_warn "Env var: TREE_SITTER_GRAMMAR_DIR not set"
  fi

  # Shell config
  local shell_rc=""
  for f in ~/.zshrc ~/.bashrc ~/.bash_profile; do
    if [[ -f "$f" ]] && grep -q "TREE_SITTER_GRAMMAR_DIR" "$f" 2>/dev/null; then
      shell_rc="$f"
      break
    fi
  done
  if [[ -n "$shell_rc" ]]; then
    log_success "Shell config: $shell_rc"
  else
    log_warn "Shell config: not configured"
  fi

  # Working grammars
  echo ""
  log_info "Working Grammars (with tags.scm)"
  local working=0
  local missing=0
  for dir in "$GRAMMAR_DIR"/tree-sitter-*/; do
    [[ ! -d "$dir" ]] && continue
    local lang=$(basename "$dir" | sed 's/tree-sitter-//')
    if [[ -f "$dir/queries/tags.scm" ]]; then
      echo -e "  ${GREEN}✓${NC} $lang"
      ((working++))
    else
      echo -e "  ${YELLOW}-${NC} $lang (no tags.scm)"
      ((missing++))
    fi
  done
  echo ""
  echo "  $working working, $missing without tags.scm"
  echo ""
}

# List available grammars
list_languages() {
  echo ""
  log_info "Core Grammars (installed by default)"
  for repo in "${CORE_GRAMMARS[@]}"; do
    echo "  - ${repo#*/}"
  done

  echo ""
  log_info "Extended Grammars (with --all)"
  for repo in "${EXTENDED_GRAMMARS[@]}"; do
    echo "  - ${repo#*/}"
  done
  echo ""
}

# Install tree-sitter CLI
install_cli() {
  if command -v tree-sitter &>/dev/null; then
    log_success "CLI already installed: $(tree-sitter --version 2>/dev/null | awk '{print $2}')"
    return 0
  fi

  log_info "Installing tree-sitter CLI..."

  if command -v brew &>/dev/null; then
    brew install tree-sitter
  elif command -v cargo &>/dev/null; then
    cargo install tree-sitter-cli
  else
    log_error "Neither Homebrew nor Cargo found. Install one of:"
    echo "  - Homebrew: https://brew.sh"
    echo "  - Rust/Cargo: https://rustup.rs"
    exit 1
  fi

  log_success "CLI installed: $(tree-sitter --version 2>/dev/null | awk '{print $2}')"
}

# Clone a grammar repository
clone_grammar() {
  local repo="$1"
  local name="${repo#*/}"
  local target="$GRAMMAR_DIR/$name"

  if [[ -d "$target" ]]; then
    echo -e "  ${GREEN}✓${NC} $name (exists)"
    return 0
  fi

  echo -e "  ${BLUE}→${NC} Cloning $name..."
  if git clone --depth 1 --quiet "https://github.com/$repo.git" "$target" 2>/dev/null; then
    echo -e "  ${GREEN}✓${NC} $name"
  else
    echo -e "  ${RED}✗${NC} $name (failed)"
  fi
}

# Install grammars
install_grammars() {
  local install_all="${1:-false}"

  log_info "Creating grammar directory: $GRAMMAR_DIR"
  mkdir -p "$GRAMMAR_DIR"

  log_info "Installing core grammars..."
  for repo in "${CORE_GRAMMARS[@]}"; do
    clone_grammar "$repo"
  done

  if [[ "$install_all" == "true" ]]; then
    echo ""
    log_info "Installing extended grammars..."
    for repo in "${EXTENDED_GRAMMARS[@]}"; do
      clone_grammar "$repo"
    done
  fi
}

# Configure shell environment
configure_env() {
  # Detect shell config file
  local shell_rc="$HOME/.zshrc"
  [[ "$SHELL" == *"bash"* ]] && shell_rc="$HOME/.bashrc"
  [[ ! -f "$shell_rc" ]] && shell_rc="$HOME/.profile"

  if grep -q "TREE_SITTER_GRAMMAR_DIR" "$shell_rc" 2>/dev/null; then
    log_success "Environment already configured in $shell_rc"
    return 0
  fi

  log_info "Adding TREE_SITTER_GRAMMAR_DIR to $shell_rc"

  cat >> "$shell_rc" << EOF

# Tree-sitter grammar location (added by setup-tree-sitter.sh)
export TREE_SITTER_GRAMMAR_DIR="$GRAMMAR_DIR"
EOF

  log_success "Added to $shell_rc"
  log_warn "Run: source $shell_rc (or open new terminal)"
}

# Verify installation
verify() {
  log_info "Verifying installation..."

  # Export for this session
  export TREE_SITTER_GRAMMAR_DIR="$GRAMMAR_DIR"

  # Test parsing
  local test_file=$(mktemp --suffix=.js 2>/dev/null || mktemp).js
  cat > "$test_file" << 'EOF'
function test() { return 42; }
EOF

  if tree-sitter parse "$test_file" --quiet 2>/dev/null; then
    log_success "JavaScript parsing works"
  else
    log_warn "JavaScript parsing failed (may need tree-sitter generate)"
  fi

  rm -f "$test_file"

  # Count working grammars
  local working=0
  for dir in "$GRAMMAR_DIR"/tree-sitter-*/; do
    [[ -f "$dir/queries/tags.scm" ]] && ((working++))
  done

  log_success "$working grammars ready for AST extraction"
}

# Main
main() {
  case "${1:-}" in
    --status)
      check_status
      exit 0
      ;;
    --languages)
      list_languages
      exit 0
      ;;
    --help|-h)
      echo "Usage: $0 [--all | --status | --languages]"
      echo ""
      echo "Options:"
      echo "  (none)      Install core grammars (JS, TS, Python, Go, Rust, Java, Ruby, C, C++)"
      echo "  --all       Install all supported grammars"
      echo "  --status    Check current installation status"
      echo "  --languages List available grammars"
      exit 0
      ;;
  esac

  local install_all=false
  [[ "${1:-}" == "--all" ]] && install_all=true

  echo ""
  echo "┌────────────────────────────────────────┐"
  echo "│  Tree-sitter Setup for Code Review    │"
  echo "└────────────────────────────────────────┘"
  echo ""

  install_cli
  echo ""
  install_grammars "$install_all"
  echo ""
  configure_env
  echo ""
  verify

  echo ""
  echo "┌────────────────────────────────────────┐"
  echo "│  Setup Complete!                       │"
  echo "│                                        │"
  echo "│  Next: source ~/.zshrc                 │"
  echo "│  Then: /code-foundations:review --sanity                 │"
  echo "└────────────────────────────────────────┘"
  echo ""
}

main "$@"
