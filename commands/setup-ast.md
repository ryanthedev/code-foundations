---
description: "Setup tree-sitter CLI and grammars for AST-powered code review"
allowed-tools: ["Bash", "Read", "Glob", "Grep", "Write", "Edit", "TaskCreate", "TaskUpdate", "TaskList", "AskUserQuestion"]
---

# Setup AST

Configure tree-sitter for AST-powered code extraction.

## Quick Start

For non-interactive setup, just run the script:

```bash
./scripts/setup-tree-sitter.sh          # Core grammars (JS, TS, Py, Go, Rust, Java, Ruby, C, C++)
./scripts/setup-tree-sitter.sh --all    # All supported grammars
./scripts/setup-tree-sitter.sh --status # Check current status
```

---

## Interactive Mode

**Flow:** `DIAGNOSE → DETECT → PLAN → EXECUTE → VERIFY`

---

## MANDATORY GATES

| Gate | Rule |
|------|------|
| **No skipping diagnosis** | DIAGNOSE must complete before EXECUTE |
| **Verification required** | VERIFY must run after EXECUTE |
| **Task tracking** | Every step uses TaskCreate/TaskUpdate |

**If user says "skip diagnosis":**
> "Diagnosis takes 30 seconds and prevents overwriting a working setup. Proceeding..."

Then run DIAGNOSE anyway.

---

## STEP 1: DIAGNOSE

```
TaskCreate(
  subject: "Diagnose tree-sitter setup",
  description: "Check CLI installation, grammar directory, and environment",
  activeForm: "Diagnosing tree-sitter setup"
)
TaskUpdate(taskId: "...", status: "in_progress")
```

Run diagnostics:

```bash
# Check CLI
echo "=== CLI Check ==="
if command -v tree-sitter &>/dev/null; then
  echo "✅ tree-sitter $(tree-sitter --version | awk '{print $2}')"
  CLI_OK=true
else
  echo "❌ tree-sitter CLI not found"
  CLI_OK=false
fi

# Check grammar directory
echo -e "\n=== Grammar Directory ==="
GRAMMAR_DIR="${TREE_SITTER_GRAMMAR_DIR:-$HOME/repos/tree-sitter-grammars}"
if [[ -d "$GRAMMAR_DIR" ]]; then
  count=$(ls -d "$GRAMMAR_DIR"/tree-sitter-*/ 2>/dev/null | wc -l | tr -d ' ')
  echo "✅ $GRAMMAR_DIR ($count grammars)"
  GRAMMAR_OK=true
else
  echo "❌ Grammar directory not found: $GRAMMAR_DIR"
  GRAMMAR_OK=false
fi

# Check environment
echo -e "\n=== Environment ==="
if [[ -n "$TREE_SITTER_GRAMMAR_DIR" ]]; then
  echo "✅ TREE_SITTER_GRAMMAR_DIR=$TREE_SITTER_GRAMMAR_DIR"
  ENV_OK=true
else
  echo "⚠️ TREE_SITTER_GRAMMAR_DIR not set (using default: $HOME/repos/tree-sitter-grammars)"
  ENV_OK=false
fi

# Check shell config
echo -e "\n=== Shell Config ==="
for f in ~/.zshrc ~/.bashrc ~/.bash_profile; do
  if [[ -f "$f" ]] && grep -q "TREE_SITTER_GRAMMAR_DIR" "$f"; then
    echo "✅ Found in $f"
  fi
done
```

```
TaskUpdate(taskId: "...", status: "completed")
```

---

## STEP 2: DETECT PROJECT LANGUAGES

```
TaskCreate(
  subject: "Detect project languages",
  description: "Scan repository for file types",
  activeForm: "Scanning project languages"
)
```

```bash
echo "=== Language Detection ==="
echo ""

# Count files by type (exclude node_modules, .git, etc.)
declare -A counts
for ext in ts tsx js jsx py go rs java rb c h cpp cc swift kt; do
  count=$(find . -type f -name "*.$ext" \
    -not -path "*/node_modules/*" \
    -not -path "*/.git/*" \
    -not -path "*/vendor/*" \
    -not -path "*/dist/*" \
    2>/dev/null | wc -l | tr -d ' ')
  if [[ $count -gt 0 ]]; then
    echo "$ext: $count files"
  fi
done
```

Present detected languages to user:

```
AskUserQuestion(
  questions: [{
    header: "Languages",
    question: "Which grammars should I install? (Detected languages shown first)",
    multiSelect: true,
    options: [
      // Dynamically built from detection
      {label: "TypeScript", description: "tree-sitter-javascript + tree-sitter-typescript"},
      {label: "JavaScript", description: "tree-sitter-javascript"},
      {label: "Python", description: "tree-sitter-python"},
      {label: "Go", description: "tree-sitter-go"},
      {label: "Rust", description: "tree-sitter-rust"}
    ]
  }]
)
```

---

## STEP 3: CREATE INSTALLATION PLAN

Based on diagnosis, create tasks:

**If CLI missing:**
```
TaskCreate(subject: "Install tree-sitter CLI", description: "brew install tree-sitter", activeForm: "Installing tree-sitter")
```

**If grammars missing:**
```
TaskCreate(subject: "Create grammar directory", description: "mkdir ~/repos/tree-sitter-grammars", activeForm: "Creating directory")
TaskCreate(subject: "Clone grammars", description: "Clone selected grammar repos", activeForm: "Cloning grammars")
TaskCreate(subject: "Build grammars", description: "tree-sitter generate", activeForm: "Building grammars")
```

**If env not set:**
```
TaskCreate(subject: "Configure environment", description: "Add TREE_SITTER_GRAMMAR_DIR to shell", activeForm: "Configuring environment")
```

**Always:**
```
TaskCreate(subject: "Verify installation", description: "Test parsing with each grammar", activeForm: "Verifying installation")
```

---

## STEP 4: EXECUTE

**GATE CHECK before proceeding:**
```
TaskList()  # Verify "Diagnose tree-sitter setup" is completed
```

If diagnosis task not completed → Go to STEP 1.

---

### Install CLI (if needed)

```bash
# macOS
brew install tree-sitter

# Verify
tree-sitter --version
```

### Create & Clone Grammars (if needed)

```bash
GRAMMAR_DIR="$HOME/repos/tree-sitter-grammars"
mkdir -p "$GRAMMAR_DIR"
cd "$GRAMMAR_DIR"

# Clone selected grammars
# JavaScript (also used by TypeScript)
[[ ! -d tree-sitter-javascript ]] && git clone --depth 1 https://github.com/tree-sitter/tree-sitter-javascript.git

# TypeScript
[[ ! -d tree-sitter-typescript ]] && git clone --depth 1 https://github.com/tree-sitter/tree-sitter-typescript.git

# Python
[[ ! -d tree-sitter-python ]] && git clone --depth 1 https://github.com/tree-sitter/tree-sitter-python.git

# Go
[[ ! -d tree-sitter-go ]] && git clone --depth 1 https://github.com/tree-sitter/tree-sitter-go.git

# Rust
[[ ! -d tree-sitter-rust ]] && git clone --depth 1 https://github.com/tree-sitter/tree-sitter-rust.git

# Java
[[ ! -d tree-sitter-java ]] && git clone --depth 1 https://github.com/tree-sitter/tree-sitter-java.git

# Ruby
[[ ! -d tree-sitter-ruby ]] && git clone --depth 1 https://github.com/tree-sitter/tree-sitter-ruby.git

# C
[[ ! -d tree-sitter-c ]] && git clone --depth 1 https://github.com/tree-sitter/tree-sitter-c.git

# C++
[[ ! -d tree-sitter-cpp ]] && git clone --depth 1 https://github.com/tree-sitter/tree-sitter-cpp.git
```

### Build Grammars

```bash
cd "$GRAMMAR_DIR"
for dir in tree-sitter-*/; do
  if [[ -f "$dir/grammar.js" ]]; then
    echo "Building $dir..."
    (cd "$dir" && tree-sitter generate 2>/dev/null) || echo "  (pre-built)"
  fi
done
```

### Configure Environment (if needed)

```bash
# Detect shell config file
if [[ -f "$HOME/.zshrc" ]]; then
  SHELL_RC="$HOME/.zshrc"
elif [[ -f "$HOME/.bashrc" ]]; then
  SHELL_RC="$HOME/.bashrc"
else
  SHELL_RC="$HOME/.profile"
fi

# Add if not present
if ! grep -q "TREE_SITTER_GRAMMAR_DIR" "$SHELL_RC" 2>/dev/null; then
  echo '' >> "$SHELL_RC"
  echo '# Tree-sitter grammar location for code-foundations AST extraction' >> "$SHELL_RC"
  echo 'export TREE_SITTER_GRAMMAR_DIR="$HOME/repos/tree-sitter-grammars"' >> "$SHELL_RC"
  echo "✅ Added to $SHELL_RC"
  echo "   Run: source $SHELL_RC"
else
  echo "✅ Already configured in $SHELL_RC"
fi

# Set for current session
export TREE_SITTER_GRAMMAR_DIR="$HOME/repos/tree-sitter-grammars"
```

---

## STEP 5: VERIFY

```bash
echo "=== Verification ==="
echo ""

# Test CLI
echo "CLI: $(tree-sitter --version)"
echo ""

# Test each grammar
echo "Grammar Tests:"
GRAMMAR_DIR="${TREE_SITTER_GRAMMAR_DIR:-$HOME/repos/tree-sitter-grammars}"

test_grammar() {
  local lang="$1"
  local scope="$2"
  local query_file="$GRAMMAR_DIR/tree-sitter-$lang/queries/tags.scm"

  if [[ -f "$query_file" ]]; then
    echo "  ✅ $lang (tags.scm found)"
  elif [[ -d "$GRAMMAR_DIR/tree-sitter-$lang" ]]; then
    echo "  ⚠️ $lang (grammar exists, no tags.scm)"
  else
    echo "  ❌ $lang (not installed)"
  fi
}

test_grammar "javascript" "source.js"
test_grammar "typescript" "source.ts"
test_grammar "python" "source.python"
test_grammar "go" "source.go"
test_grammar "rust" "source.rust"
test_grammar "java" "source.java"
test_grammar "ruby" "source.ruby"
test_grammar "c" "source.c"
test_grammar "cpp" "source.cpp"

echo ""
echo "=== Ready for AST Extraction ==="
echo "Run: /review --quick   to test"
```

---

## FINAL REPORT

```markdown
## Setup Complete

| Component | Status |
|-----------|--------|
| CLI | ✅ tree-sitter {version} |
| Grammar Dir | ✅ {path} |
| Environment | ✅ TREE_SITTER_GRAMMAR_DIR set |
| Grammars | ✅ {count} installed |

### Installed Grammars
- ✅ JavaScript
- ✅ TypeScript
- ✅ Python
...

### Next Steps
1. Open new terminal (or `source ~/.zshrc`)
2. Run `/review --quick` to test AST extraction
```
