#!/usr/bin/env bash
set -euo pipefail
REPO=/Users/r/repos/code-foundations

echo "=== DW-5.1: Non-SKILL.md files in scope dirs ==="
for dir in \
  "$REPO/skills/cc-control-flow-quality" \
  "$REPO/skills/cc-debugging" \
  "$REPO/skills/cc-defensive-programming" \
  "$REPO/skills/cc-pseudocode-programming" \
  "$REPO/skills/cc-quality-practices" \
  "$REPO/skills/cc-refactoring-guidance" \
  "$REPO/skills/cc-routine-and-class-design" \
  "$REPO/skills/welc-legacy-code"; do
  echo "--- $dir ---"
  find "$dir" -maxdepth 1 -type f ! -name 'SKILL.md' | sort
done

echo ""
echo "=== DW-5.1: hard-data.md and language-notes.md anywhere in scope ==="
find "$REPO/skills/cc-control-flow-quality" \
     "$REPO/skills/cc-debugging" \
     "$REPO/skills/cc-defensive-programming" \
     "$REPO/skills/cc-pseudocode-programming" \
     "$REPO/skills/cc-quality-practices" \
     "$REPO/skills/cc-refactoring-guidance" \
     "$REPO/skills/cc-routine-and-class-design" \
     "$REPO/skills/welc-legacy-code" \
     -name 'hard-data.md' -o -name 'language-notes.md' 2>/dev/null | sort

echo ""
echo "=== DW-5.2: Line count of commands/debug.md ==="
wc -l "$REPO/commands/debug.md"

echo ""
echo "=== DW-5.2: STABILIZE grep in cc-debugging/ ==="
grep -rn 'STABILIZE' "$REPO/skills/cc-debugging/" || echo "(none)"

echo ""
echo "=== DW-5.3: Artifact-checkable preconditions in cc-debugging SKILL.md ==="
grep -n 'STABILIZE\|SEARCH\|artifact\|captured\|transcript\|recorded\|precondition' "$REPO/skills/cc-debugging/SKILL.md" || echo "(none)"

echo ""
echo "=== DW-5.4: Parameter count in cc-routine-and-class-design ==="
grep -rn '8+\|8-9\|VIOLATION\|WARNING\|param' "$REPO/skills/cc-routine-and-class-design/" | grep -v '\.pyc' | head -40 || echo "(none)"

echo ""
echo "=== DW-5.4: '< 50' in cc-refactoring-guidance ==="
grep -rn '< 50' "$REPO/skills/cc-refactoring-guidance/" || echo "(none)"

echo ""
echo "=== DW-5.5: Reality tables in scope dirs + debug.md ==="
grep -rn 'Reality' \
  "$REPO/skills/cc-control-flow-quality" \
  "$REPO/skills/cc-debugging" \
  "$REPO/skills/cc-defensive-programming" \
  "$REPO/skills/cc-pseudocode-programming" \
  "$REPO/skills/cc-quality-practices" \
  "$REPO/skills/cc-refactoring-guidance" \
  "$REPO/skills/cc-routine-and-class-design" \
  "$REPO/skills/welc-legacy-code" \
  "$REPO/commands/debug.md" || echo "(none)"

echo ""
echo "=== DW-5.5: Self-assessed 'Did I' items in scope dirs ==="
grep -rn '"Did I\|Did I ' \
  "$REPO/skills/cc-control-flow-quality" \
  "$REPO/skills/cc-debugging" \
  "$REPO/skills/cc-defensive-programming" \
  "$REPO/skills/cc-pseudocode-programming" \
  "$REPO/skills/cc-quality-practices" \
  "$REPO/skills/cc-refactoring-guidance" \
  "$REPO/skills/cc-routine-and-class-design" \
  "$REPO/skills/welc-legacy-code" \
  "$REPO/commands/debug.md" || echo "(none)"

echo ""
echo "=== DW-5.6: STABILIZE in cc-quality-practices ==="
grep -rn 'STABILIZE\|SEARCH\|scientific.debug' "$REPO/skills/cc-quality-practices/" || echo "(none)"

echo ""
echo "=== DW-5.6: language-notes.md existence check ==="
ls -la "$REPO/skills/cc-quality-practices/language-notes.md" 2>/dev/null || echo "cc-quality-practices/language-notes.md: NOT FOUND (good)"
ls -la "$REPO/skills/cc-pseudocode-programming/language-notes.md" 2>/dev/null || echo "cc-pseudocode-programming/language-notes.md: NOT FOUND (good)"

echo ""
echo "=== DW-5.7: Skill() calls in scope files ==="
grep -rn 'Skill(' \
  "$REPO/skills/cc-control-flow-quality" \
  "$REPO/skills/cc-debugging" \
  "$REPO/skills/cc-defensive-programming" \
  "$REPO/skills/cc-pseudocode-programming" \
  "$REPO/skills/cc-quality-practices" \
  "$REPO/skills/cc-refactoring-guidance" \
  "$REPO/skills/cc-routine-and-class-design" \
  "$REPO/skills/welc-legacy-code" \
  "$REPO/commands/debug.md" || echo "(none)"

echo ""
echo "=== git diff HEAD --stat (scope files) ==="
cd "$REPO" && git diff HEAD --stat -- \
  'skills/cc-control-flow-quality/' \
  'skills/cc-debugging/' \
  'skills/cc-defensive-programming/' \
  'skills/cc-pseudocode-programming/' \
  'skills/cc-quality-practices/' \
  'skills/cc-refactoring-guidance/' \
  'skills/cc-routine-and-class-design/' \
  'skills/welc-legacy-code/' \
  'commands/debug.md' 2>/dev/null || echo "(clean)"

echo ""
echo "=== git diff HEAD -- welc-legacy-code SKILL.md (frontmatter check) ==="
cd "$REPO" && git diff HEAD -- 'skills/welc-legacy-code/SKILL.md' 2>/dev/null | head -60 || echo "(no diff)"

echo "DONE"
