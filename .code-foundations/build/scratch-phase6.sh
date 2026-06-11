#!/bin/bash
set -e

cd /Users/r/repos/code-foundations

echo "=== PHASE 6 VERIFICATION SCRIPT ==="
echo ""

# DW-6.1: Four drift items + duplicate removal
echo "DW-6.1: Checking for drift items and removed duplicates"
echo "---"

# Check RF-8 in aposd-designing-deep-modules
echo "RF-8 (silent failure masking) in aposd-designing-deep-modules/SKILL.md:"
grep -n "RF-8\|absorb.*fail\|mask.*fail\|silent.*fail" skills/aposd-designing-deep-modules/SKILL.md || echo "NOT FOUND"

# Check SF-1 in aposd-reviewing-module-design
echo "SF-1 (silent failure) in aposd-reviewing-module-design/SKILL.md:"
grep -n "SF-1\|silent.*fail" skills/aposd-reviewing-module-design/SKILL.md || echo "NOT FOUND"

# Check RF-7 in aposd-simplifying-complexity
echo "RF-7 (error masked without observability) in aposd-simplifying-complexity/SKILL.md:"
grep -n "RF-7\|error.*mask\|mask.*observ" skills/aposd-simplifying-complexity/SKILL.md || echo "NOT FOUND"

# Check EH-5 in aposd-verifying-correctness
echo "EH-5 (silent error-path continuation) in aposd-verifying-correctness/SKILL.md:"
grep -n "EH-5\|error.*path\|continue.*error" skills/aposd-verifying-correctness/SKILL.md || echo "NOT FOUND"

# Check for duplicates removed
echo ""
echo "Checking duplicate Quick Reference removal:"
grep -n "Quick Reference" skills/aposd-reviewing-module-design/SKILL.md && echo "FOUND IN aposd-reviewing" || echo "NOT IN aposd-reviewing (good)"
grep -n "Quick Reference" skills/aposd-simplifying-complexity/SKILL.md && echo "FOUND IN aposd-simplifying" || echo "NOT IN aposd-simplifying (good)"
grep -n "Quick Checklist" skills/aposd-verifying-correctness/SKILL.md && echo "FOUND IN aposd-verifying" || echo "NOT IN aposd-verifying (good)"

echo ""
echo "=== DW-6.2: Discipline-theater removal ==="
echo "---"
echo "Checking for 'Did I' impatience script:"
grep -rn 'Did I' skills/aposd-* skills/ca-architecture-boundaries skills/gof-design-patterns skills/clarify skills/code-clarity-and-docs skills/code-standards skills/performance-optimization 2>/dev/null && echo "FOUND" || echo "NOT FOUND (good)"

echo ""
echo "Checking for 'Emergency Bypass':"
grep -rn 'Emergency Bypass' skills/aposd-* skills/ca-architecture-boundaries skills/gof-design-patterns skills/clarify skills/code-clarity-and-docs skills/code-standards skills/performance-optimization 2>/dev/null && echo "FOUND" || echo "NOT FOUND (good)"

echo ""
echo "Checking for 'Show Your Work' heading:"
grep -rn 'Show Your Work' skills/aposd-* skills/ca-architecture-boundaries skills/gof-design-patterns skills/clarify skills/code-clarity-and-docs skills/code-standards skills/performance-optimization 2>/dev/null && echo "FOUND" || echo "NOT FOUND (good)"

echo ""
echo "=== DW-6.3: GoF reference cleanup ==="
echo "---"
echo "Checking if orphan GoF files exist:"
ls -la skills/gof-design-patterns/references/creational.md 2>/dev/null && echo "EXISTS (BAD)" || echo "DELETED (good)"
ls -la skills/gof-design-patterns/references/structural-behavioral.md 2>/dev/null && echo "EXISTS (BAD)" || echo "DELETED (good)"
ls -la skills/gof-design-patterns/references/implementation-and-review.md 2>/dev/null && echo "EXISTS (BAD)" || echo "DELETED (good)"

echo ""
echo "Checking for Myth | Reality table:"
grep -rn '| Myth | Reality |' skills/gof-design-patterns skills/aposd-* skills/ca-architecture-boundaries skills/clarify skills/code-clarity-and-docs skills/code-standards skills/performance-optimization 2>/dev/null && echo "FOUND (BAD)" || echo "NOT FOUND (good)"

echo ""
echo "Checking for Pattern | Reality patterns:"
grep -rn 'Mistake.*Reality\|Pattern.*Reality' skills/gof-design-patterns skills/aposd-* skills/ca-architecture-boundaries skills/clarify skills/code-clarity-and-docs skills/code-standards skills/performance-optimization 2>/dev/null && echo "FOUND (BAD)" || echo "NOT FOUND (good)"

echo ""
echo "Checking foundations.md line count:"
wc -l skills/gof-design-patterns/references/foundations.md

echo ""
echo "=== DW-6.4: Performance-optimization priority workflow ==="
echo "---"
echo "Counting priority workflow statements in SKILL.md:"
grep -c "PRIORITY\|priority.*order\|Priority.*Workflow" skills/performance-optimization/SKILL.md || echo "COUNT: 0"

echo ""
echo "Checking for latency table in SKILL.md:"
grep -n "latency\|timing\|ms\|microsecond" skills/performance-optimization/SKILL.md | head -3

echo ""
echo "Checking if latency table exists in checklists.md:"
grep -n "latency\|timing\|μs\|microsecond" skills/performance-optimization/checklists.md | head -3

echo ""
echo "Checking if before/after examples in checklists.md:"
grep -n "Before\|After\|before:\|after:" skills/performance-optimization/checklists.md | head -3

echo ""
echo "Checking for \${CLAUDE_SKILL_DIR} in checklist link:"
grep -n "checklist\|CLAUDE_SKILL_DIR" skills/performance-optimization/SKILL.md | head -3

echo ""
echo "=== DW-6.5: CA Integration Checklist polarity ==="
echo "---"
echo "Reading CA Integration Checklist:"
grep -A 30 "Integration Checklist" skills/ca-architecture-boundaries/SKILL.md

echo ""
echo "Checking clarify 70% count:"
grep -c "70%" skills/clarify/SKILL.md

echo ""
echo "Checking for adaptive-questioning.md relationship in clarify:"
grep -n "adaptive-questioning\|plugin-root" skills/clarify/SKILL.md || echo "NOT FOUND"

echo ""
echo "=== DW-6.6: Code-standards length target and failure path ==="
echo "---"
echo "Checking for 150-250 in section-templates.md:"
grep -n "150-250" skills/code-standards/references/section-templates.md && echo "FOUND" || echo "NOT FOUND"

echo ""
echo "Checking for missing/invalid base-commit failure path in SKILL.md:"
grep -n "missing.*base-commit\|invalid.*base-commit\|Generate" skills/code-standards/SKILL.md | head -3

echo ""
echo "Checking for non-git failure handling:"
grep -n "non-git\|not a git" skills/code-standards/SKILL.md | head -2

echo ""
echo "Checking for Contents/ToC in section-templates.md:"
grep -n "^## Contents\|^## Table of Contents\|^## ToC" skills/code-standards/references/section-templates.md

echo ""
echo "=== DW-6.7: Code-clarity-and-docs checklist link and item polarity ==="
echo "---"
echo "Checking checklist link in SKILL.md:"
grep -n "checklist\|CLAUDE_SKILL_DIR" skills/code-clarity-and-docs/SKILL.md | head -2

echo ""
echo "Checking CF/PC section items (should assert properties, not author process):"
grep -B2 -A2 "^### CF\|^### PC" skills/code-clarity-and-docs/checklists.md | head -20

echo ""
echo "Checking for (CHECKER) chain target:"
grep -n "(CHECKER)" skills/code-clarity-and-docs/checklists.md && echo "FOUND (BAD)" || echo "NOT FOUND (good)"

echo ""
echo "=== DW-6.8: Banned constructs check ==="
echo "---"
echo "Checking for Skill() calls in scope:"
grep -rn "Skill(" skills/aposd-* skills/ca-architecture-boundaries skills/gof-design-patterns skills/clarify skills/code-clarity-and-docs skills/code-standards skills/performance-optimization 2>/dev/null && echo "FOUND (BAD)" || echo "NOT FOUND (good)"

echo ""
echo "Checking \${CLAUDE_SKILL_DIR} usage:"
grep -rn '\${CLAUDE_SKILL_DIR}' skills/aposd-* skills/ca-architecture-boundaries skills/gof-design-patterns skills/clarify skills/code-clarity-and-docs skills/code-standards skills/performance-optimization 2>/dev/null | head -10

echo ""
echo "Checking \${CLAUDE_PLUGIN_ROOT} usage:"
grep -rn '\${CLAUDE_PLUGIN_ROOT}' skills/aposd-* skills/ca-architecture-boundaries skills/gof-design-patterns skills/clarify skills/code-clarity-and-docs skills/code-standards skills/performance-optimization 2>/dev/null | head -10

echo ""
echo "Checking for bare relative paths (unbraced):"
grep -rn 'Read.*[^}]\.\./' skills/aposd-* skills/ca-architecture-boundaries skills/gof-design-patterns skills/clarify skills/code-clarity-and-docs skills/code-standards skills/performance-optimization 2>/dev/null && echo "FOUND (BAD)" || echo "NOT FOUND (good)"

echo ""
echo "=== EDGE CASE: GoF pattern file convention ==="
echo "---"
echo "Checking if 23 gof-*.md files still exist:"
ls -1 skills/gof-design-patterns/references/gof-*.md | wc -l

echo ""
echo "Checking if SKILL.md documents gof-<pattern-name> routing:"
grep -n "gof-.*\\.md\|references/" skills/gof-design-patterns/SKILL.md | head -5

echo ""
echo "=== EDGE CASE: aposd-designing-deep-modules checklists.md deleted ==="
echo "---"
echo "Checking if checklists.md was deleted:"
ls -la skills/aposd-designing-deep-modules/checklists.md 2>/dev/null && echo "EXISTS (BAD)" || echo "DELETED (good)"

echo ""
echo "Checking if SKILL.md references deleted checklists.md:"
grep -n "checklists\\.md" skills/aposd-designing-deep-modules/SKILL.md && echo "FOUND (BAD)" || echo "NOT FOUND (good)"

echo ""
echo "=== END OF VERIFICATION SCRIPT ==="
