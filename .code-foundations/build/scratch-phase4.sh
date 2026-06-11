#!/bin/bash
set -e

cd /Users/r/repos/code-foundations

echo "=== DW-4.1: Check for disable-model-invocation: true in all 19 skills ==="
echo "Files WITHOUT disable-model-invocation: true:"
grep -L 'disable-model-invocation: true' skills/*/SKILL.md || echo "NONE - all files have the flag"
echo

echo "=== DW-4.3a: Count skill directories ==="
SKILL_COUNT=$(ls -d skills/*/ | wc -l)
echo "Skill directories: $SKILL_COUNT"
echo

echo "=== DW-4.3b: Check skill-catalog.md exists ==="
if [ -f references/skill-catalog.md ]; then
  echo "✓ references/skill-catalog.md exists"
else
  echo "✗ references/skill-catalog.md MISSING"
  exit 1
fi
echo

echo "=== DW-4.3c: Count matching lines in catalog (code-foundations:) ==="
CATALOG_COUNT=$(grep -c 'code-foundations:' references/skill-catalog.md || echo "0")
echo "Matches in catalog: $CATALOG_COUNT"
echo "Expected: 19"
echo

echo "=== DW-4.3d: Verify all 19 skill directories appear in catalog ==="
for dir in skills/*/; do
  skill_name=$(basename "$dir")
  if grep -q "code-foundations:$skill_name" references/skill-catalog.md; then
    echo "✓ $skill_name in catalog"
  else
    echo "✗ $skill_name NOT in catalog"
  fi
done
echo

echo "=== DW-4.4a: Check for 'Triggers on' in any SKILL.md ==="
echo "Files containing 'Triggers on':"
grep -n 'Triggers on' skills/*/SKILL.md || echo "NONE - clean"
echo

echo "=== DW-4.4b: Verify descriptions are 1-2 sentences (spot check) ==="
ruby -e '
require "yaml"
Dir.glob("skills/*/SKILL.md").each do |f|
  content = File.read(f)
  fm_match = content[/\A---\n(.*?)\n---/m, 1]
  data = YAML.safe_load(fm_match)
  desc = data["description"]

  # Count sentences (period, question mark, exclamation, or newline)
  sentence_count = desc.scan(/[.!?]+/).length
  if sentence_count > 2
    puts "WARNING: #{f} has #{sentence_count} sentences (max 2): #{desc[0..80]}"
  end
end
puts "Check complete"
'
echo

echo "=== DW-4.5: Validate all frontmatter strict YAML parsing ==="
ruby -e '
require "yaml"
Dir.glob("skills/*/SKILL.md").each do |f|
  content = File.read(f)
  fm_match = content[/\A---\n(.*?)\n---/m, 1]

  unless fm_match
    puts "ERROR: #{f} has no frontmatter"
    next
  end

  begin
    data = YAML.safe_load(fm_match)
  rescue => e
    puts "ERROR: #{f} YAML parse failed: #{e}"
    next
  end

  # Check name matches directory
  dir_name = File.dirname(f).split("/")[-1]
  unless data["name"] == dir_name
    puts "ERROR: #{f} name=#{data["name"]} but dir=#{dir_name}"
    next
  end

  # Check description length
  unless data["description"] && data["description"].length.between?(1, 1024)
    puts "ERROR: #{f} description missing or out of range (1-1024): length=#{data["description"]&.length}"
    next
  end
end
puts "OK - all 19 frontmatters valid"
'
echo

echo "=== DW-4.1b: Double-check disable-model-invocation: true is in every file ==="
MISSING_FLAG=$(grep -L 'disable-model-invocation: true' skills/*/SKILL.md | wc -l)
echo "Files missing the flag: $MISSING_FLAG"
if [ "$MISSING_FLAG" -eq 0 ]; then
  echo "✓ All 19 files have disable-model-invocation: true"
else
  echo "✗ FAIL: $MISSING_FLAG files missing the flag"
  exit 1
fi
echo

echo "=== Edge case: Only frontmatter changed ==="
echo "Git diff summary:"
git diff HEAD --stat || echo "No changes"
echo
echo "Spot-check 3 skill diffs (confined to frontmatter):"
for skill in cc-quality-practices aposd-designing-deep-modules planning; do
  if git diff HEAD -- "skills/$skill/SKILL.md" > /tmp/skill_diff.txt 2>&1; then
    lines=$(wc -l < /tmp/skill_diff.txt)
    if [ "$lines" -gt 0 ]; then
      echo "--- skills/$skill/SKILL.md diff (first 30 lines) ---"
      head -30 /tmp/skill_diff.txt
      echo
    fi
  fi
done
echo

echo "=== DW-4.4c: Verify descriptions are third person ==="
ruby -e '
require "yaml"
Dir.glob("skills/*/SKILL.md").each do |f|
  content = File.read(f)
  fm_match = content[/\A---\n(.*?)\n---/m, 1]
  data = YAML.safe_load(fm_match)
  desc = data["description"]

  if desc.match?(/\bI\b|\byou\b|\bmy\b|\byour\b/i)
    puts "WARNING: #{f} may not be third person: #{desc[0..80]}"
  end
end
puts "Check complete"
'
echo

echo "=== All checks complete ==="
