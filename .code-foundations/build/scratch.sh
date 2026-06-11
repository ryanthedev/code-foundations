#!/bin/bash

set -e

cd /Users/r/repos/code-foundations

echo "=== TEST 1: YAML parsing of all SKILL.md files ==="
ruby -e 'require "yaml"; Dir.glob("skills/*/SKILL.md").each { |f| c = File.read(f); fm = c[/\A---\n(.*?)\n---/m, 1]; YAML.safe_load(fm); puts "✓ #{f}"; }; puts "ALL PARSE"'

echo ""
echo "=== TEST 2: grep -rn Total items ==="
grep -rn "Total items" skills/ || echo "✓ No 'Total items' found"

echo ""
echo "=== TEST 3: grep -L '^# Command:' in commands/ ==="
grep -L '^# Command: ' commands/*.md || echo "✓ All commands have '# Command:' titles"

echo ""
echo "=== TEST 4: grep -rn CSO KEYWORDS ==="
grep -rn "CSO KEYWORDS" skills/ || echo "✓ No CSO KEYWORDS found"

echo ""
echo "=== TEST 5: grep -rEn 'description: [^\"|\>].*: ' ==="
grep -rEn 'description: [^"|>].*: ' skills/ || echo "✓ No unquoted description colons found"

echo ""
echo "=== TEST 6: Check git diff stat ==="
git diff HEAD --stat | head -5
