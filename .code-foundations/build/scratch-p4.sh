#!/bin/bash
set -e
cd /Users/r/repos/code-foundations/.claude/worktrees/concise-code-doctrine-and-quality-benchmark/benchmarks/concise-doctrine
.venv/bin/python -m pytest test_phase4.py -q
