#!/bin/bash
set -e

cd /Users/r/repos/code-foundations/.claude/worktrees/concise-code-doctrine-and-quality-benchmark

echo "=== DW-6.1: Check additions are the only changes (baseline vs. current) ==="
diff benchmarks/concise-doctrine/arms/build-agent.baseline.md agents/build-agent.md || true

echo ""
echo "=== DW-6.3: Check current file matches concise source ==="
diff agents/build-agent.md benchmarks/concise-doctrine/arms/build-agent.concise.md || true

echo ""
echo "=== Additional Check: Verify four pre-existing subsections still present ==="
echo "Checking for 'Scope Latitude'..."
grep -n "^### Scope Latitude" agents/build-agent.md || echo "NOT FOUND"

echo "Checking for 'Done-When Traceability'..."
grep -n "^### Done-When Traceability" agents/build-agent.md || echo "NOT FOUND"

echo "Checking for 'Validation Coverage'..."
grep -n "^### Validation Coverage" agents/build-agent.md || echo "NOT FOUND"

echo "Checking for 'Test Anchoring'..."
grep -n "^### Test Anchoring" agents/build-agent.md || echo "NOT FOUND"

echo ""
echo "=== Additional Check: Verify 'Concise Implementation' subsection is present ==="
grep -n "^### Concise Implementation" agents/build-agent.md || echo "NOT FOUND"

echo ""
echo "=== Additional Check: Verify no 'aposd' token in the additions ==="
# Extract the lines that differ between baseline and current
diff benchmarks/concise-doctrine/arms/build-agent.baseline.md agents/build-agent.md | grep "^>" | grep -i "aposd" || echo "No 'aposd' found in additions (GOOD)"

echo ""
echo "=== Additional Check: Verify Validation Coverage is not weakened ==="
echo "Current Validation Coverage section:"
sed -n '/^### Validation Coverage/,/^### [^C]/p' agents/build-agent.md | head -20

echo ""
echo "=== Additional Check: Verify Scope Latitude is not weakened ==="
echo "Current Scope Latitude section:"
sed -n '/^### Scope Latitude/,/^### [^S]/p' agents/build-agent.md | head -20

echo ""
echo "=== Additional Check: Verify the added text is in Phase 1 ==="
# Check if 'Concise Implementation' appears before 'Phase 2'
grep -n "^### Concise Implementation\|^## Phase 2:" agents/build-agent.md | head -2
