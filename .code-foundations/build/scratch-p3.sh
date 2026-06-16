#!/usr/bin/env bash
set -euo pipefail
BENCH="/Users/r/repos/code-foundations/.claude/worktrees/concise-code-doctrine-and-quality-benchmark/benchmarks/concise-doctrine"
REPO_ROOT="/Users/r/repos/code-foundations/.claude/worktrees/concise-code-doctrine-and-quality-benchmark"

echo "=== Fast mocked test suite ==="
cd "$BENCH"
.venv/bin/python -m pytest test_phase3.py -q 2>&1
echo ""

echo "=== Diff real agent vs baseline arm ==="
diff -q "$REPO_ROOT/agents/build-agent.md" "$BENCH/arms/build-agent.baseline.md" && echo "MATCH: byte-identical" || echo "DIFFER"

echo ""
echo "=== Live smoke meta.json ==="
cat "$BENCH/_live-smoke/01-duration/baseline/sonnet/run-1/meta.json"

echo ""
echo "=== Live smoke outputs/ ==="
ls -1 "$BENCH/_live-smoke/01-duration/baseline/sonnet/run-1/outputs/"
