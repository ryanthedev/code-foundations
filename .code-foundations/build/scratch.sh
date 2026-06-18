#!/usr/bin/env bash
set -euo pipefail

WORKDIR="/Users/r/repos/code-foundations/.claude/worktrees/concise-code-doctrine-and-quality-benchmark/benchmarks/concise-doctrine"
ARMS_DIR="$WORKDIR/arms"

echo "=== Step 0: Test Suite ==="
cd "$WORKDIR"
if [ ! -d ".venv" ]; then
  uv venv .venv -p 3.12
  uv pip install --python .venv/bin/python pytest
fi
.venv/bin/python -m pytest test_phase2.py -v 2>&1
echo ""

echo "=== Step 1: diff baseline vs concise (raw diff output) ==="
diff "$ARMS_DIR/build-agent.baseline.md" "$ARMS_DIR/build-agent.concise.md" || true
echo ""

echo "=== Step 2: Count removed and added lines ==="
python3 - <<'PYEOF'
import difflib
from pathlib import Path
arms = Path("/Users/r/repos/code-foundations/.claude/worktrees/concise-code-doctrine-and-quality-benchmark/benchmarks/concise-doctrine/arms")
base = (arms / "build-agent.baseline.md").read_text().splitlines(keepends=True)
conc = (arms / "build-agent.concise.md").read_text().splitlines(keepends=True)
removed = [l[1:] for l in difflib.unified_diff(base, conc, n=0) if l.startswith("-") and not l.startswith("---")]
added = [l[1:] for l in difflib.unified_diff(base, conc, n=0) if l.startswith("+") and not l.startswith("+++")]
print(f"Removed lines ({len(removed)}): {removed!r}")
print(f"Added lines ({len(added)}):")
for l in added:
    print(f"  {l!r}")
PYEOF
echo ""

echo "=== Step 3: diff -q baseline vs production build-agent.md ==="
PROD_AGENT="/Users/r/repos/code-foundations/.claude/worktrees/concise-code-doctrine-and-quality-benchmark/agents/build-agent.md"
if [ -f "$PROD_AGENT" ]; then
  diff -q "$ARMS_DIR/build-agent.baseline.md" "$PROD_AGENT" && echo "MATCH: baseline is verbatim copy of production agent" || echo "MISMATCH: baseline differs from production agent"
else
  echo "Production agent not found at: $PROD_AGENT"
  echo "Searching for build-agent.md..."
  find "/Users/r/repos/code-foundations/.claude/worktrees/concise-code-doctrine-and-quality-benchmark" -name "build-agent.md" 2>/dev/null | head -10
fi
echo ""

echo "=== Step 4: Show exact added subsection content ==="
python3 - <<'PYEOF'
from pathlib import Path
base_path = Path("/Users/r/repos/code-foundations/.claude/worktrees/concise-code-doctrine-and-quality-benchmark/benchmarks/concise-doctrine/arms/build-agent.baseline.md")
conc_path = Path("/Users/r/repos/code-foundations/.claude/worktrees/concise-code-doctrine-and-quality-benchmark/benchmarks/concise-doctrine/arms/build-agent.concise.md")
base = base_path.read_text()
conc = conc_path.read_text()

HEADING = "### Concise Implementation"
if HEADING in conc:
    start = conc.index(HEADING)
    end = conc.index("\n---", start)
    subsection = conc[start:end]
    print("=== Concise Implementation subsection ===")
    print(subsection)
    print()
else:
    print("ERROR: Concise Implementation heading not found!")

print(f"Heading in baseline: {HEADING in base}")
print(f"Heading in concise: {HEADING in conc}")

# Verify Phase-1 check location
PHASE1_CHECK = "When sketching the interface, note where a built-in or existing solution replaces hand-written code, and prefer the concise expression that stays readable."
print(f"\nPhase-1 check in concise: {PHASE1_CHECK in conc}")
print(f"Phase-1 check in baseline: {PHASE1_CHECK in base}")

# Find where Phase-1 check appears in concise
if PHASE1_CHECK in conc:
    idx = conc.index(PHASE1_CHECK)
    context = conc[max(0,idx-200):idx+len(PHASE1_CHECK)+50]
    print(f"\nContext around Phase-1 check:\n{context}")
PYEOF
