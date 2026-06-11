#!/bin/bash
set -e

cd /Users/r/repos/code-foundations

echo "=== COMPREHENSIVE VERIFICATION ==="
echo

echo "1. DW-4.1: All 19 skills have disable-model-invocation: true"
MISSING=$(grep -L 'disable-model-invocation: true' skills/*/SKILL.md | wc -l)
if [ "$MISSING" -eq 0 ]; then
  echo "   PASS: All 19 files have the flag"
else
  echo "   FAIL: $MISSING files missing the flag"
  exit 1
fi
echo

echo "2. DW-4.3: Catalog exists and has all 19 entries"
if [ ! -f references/skill-catalog.md ]; then
  echo "   FAIL: references/skill-catalog.md not found"
  exit 1
fi

ENTRY_COUNT=$(grep '^code-foundations:' references/skill-catalog.md | wc -l)
if [ "$ENTRY_COUNT" -ne 19 ]; then
  echo "   FAIL: Expected 19 entries, found $ENTRY_COUNT"
  exit 1
fi

MISSING_ENTRIES=$(comm -23 <(ls -1d skills/*/ | sed 's|.*skills/||;s|/||' | sort) <(grep '^code-foundations:' references/skill-catalog.md | sed 's|code-foundations:||;s| —.*||' | sort) | wc -l)
if [ "$MISSING_ENTRIES" -gt 0 ]; then
  echo "   FAIL: Some skills missing from catalog"
  comm -23 <(ls -1d skills/*/ | sed 's|.*skills/||;s|/||' | sort) <(grep '^code-foundations:' references/skill-catalog.md | sed 's|code-foundations:||;s| —.*||' | sort)
  exit 1
fi

echo "   PASS: All 19 skills present in catalog with correct count"
echo

echo "3. DW-4.4: Descriptions are 1-2 sentences, no 'Triggers on', third person"
ruby -e '
require "yaml"

failed = []

Dir.glob("skills/*/SKILL.md").sort.each do |f|
  content = File.read(f)
  fm_match = content[/\A---\n(.*?)\n---/m, 1]
  data = YAML.safe_load(fm_match)
  desc = data["description"]
  skill_name = File.dirname(f).split("/")[-1]

  # Check for "Triggers on"
  if desc.include?("Triggers on")
    failed << "#{skill_name}: contains \"Triggers on\""
  end

  # Count sentences (only counting natural sentence boundaries)
  periods = desc.scan(/\.\s/).length
  sentence_count = desc.strip.empty? ? 0 : periods + 1

  if sentence_count > 2
    failed << "#{skill_name}: has #{sentence_count} sentences (max 2)"
  end

  # Check for first/second person
  if desc.match?(/\b(I|you|my|your|we|our)\b/i)
    first_person_words = desc.scan(/\b(I|you|my|your|we|our)\b/i).flatten.uniq.join(", ")
    failed << "#{skill_name}: contains first/second person: #{first_person_words}"
  end

  # Warn about workflow lists (e.g., "Steps:", "comma-separated pipeline")
  if desc.match?(/Steps:|step \d+:|^.*,\s*.*,\s*.*/m) && desc.length > 100
    # Check if it looks like a pipeline
    if desc.count(",") >= 2
      failed << "#{skill_name}: may contain pipeline/steps list"
    end
  end
end

if failed.empty?
  puts "   PASS: All descriptions meet criteria"
else
  puts "   FAIL:"
  failed.each { |msg| puts "     - #{msg}" }
  exit 1
end
'
echo

echo "4. DW-4.5: All frontmatter parses as strict YAML, names match dirs, lengths OK"
ruby -e '
require "yaml"

failed = []

Dir.glob("skills/*/SKILL.md").sort.each do |f|
  content = File.read(f)
  fm_match = content[/\A---\n(.*?)\n---/m, 1]

  unless fm_match
    failed << "#{f}: missing frontmatter"
    next
  end

  begin
    data = YAML.safe_load(fm_match)
  rescue => e
    failed << "#{f}: YAML parse error: #{e.message}"
    next
  end

  dir_name = File.dirname(f).split("/")[-1]
  unless data["name"] == dir_name
    failed << "#{f}: name mismatch (name=#{data["name"]}, dir=#{dir_name})"
  end

  unless data["description"] && data["description"].length.between?(1, 1024)
    failed << "#{f}: description missing or out of range"
  end
end

if failed.empty?
  puts "   PASS: All 19 frontmatters valid"
else
  puts "   FAIL:"
  failed.each { |msg| puts "     - #{msg}" }
  exit 1
end
'
echo

echo "5. Edge case: planning preserves user-invocable: false"
if grep -q 'user-invocable: false' skills/planning/SKILL.md; then
  echo "   PASS: planning skill preserves user-invocable: false"
else
  echo "   FAIL: planning skill missing user-invocable: false"
  exit 1
fi
echo

echo "6. Edge case: Only frontmatter changed (spot-check 3 diffs)"
for skill in cc-quality-practices aposd-designing-deep-modules planning; do
  DIFF_OUTPUT=$(git diff HEAD -- "skills/$skill/SKILL.md" 2>/dev/null || true)
  # Count lines after the --- --- line separator
  BODY_CHANGES=$(echo "$DIFF_OUTPUT" | tail -n +6 | grep -c '^[+-]' || true)
  if [ "$BODY_CHANGES" -gt 0 ]; then
    echo "   FAIL: skills/$skill/SKILL.md has body changes beyond frontmatter"
    exit 1
  fi
done
echo "   PASS: All spot-checked diffs contain only frontmatter changes"
echo

echo "=== ALL VERIFICATIONS PASSED ==="
