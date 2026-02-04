#!/usr/bin/env bash
#
# orchestrate-batches.sh v3.5.0 - Deterministic file-based batching
#
# orchestrate-batches.sh - Deterministic file-based batching for code review
#
# Groups units by "logical source file" - each source file and its corresponding
# test file(s) become one batch. 100% deterministic based on file paths.
#
# Usage:
#   cat units.jsonl | ./orchestrate-batches.sh > batches.json
#   ./extract-units.sh --staged | ./orchestrate-batches.sh
#
# Input:  JSONL from stdin (one JSON object per line)
# Output: JSON array of batches to stdout

set -euo pipefail

VERSION="3.5.0"
echo "[orchestrate-batches.sh v$VERSION] Starting..." >&2

if ! command -v jq &>/dev/null; then
    echo '{"error": "jq is required but not installed"}' >&2
    exit 1
fi

# Read and validate input
preprocess_input() {
    local line_num=0
    while IFS= read -r line || [[ -n "$line" ]]; do
        line_num=$((line_num + 1))
        [[ -z "$line" ]] && continue
        if echo "$line" | jq -e '.' >/dev/null 2>&1; then
            echo "$line"
        else
            echo "Warning: Malformed JSON on line $line_num, skipping" >&2
        fi
    done
}

process_batches() {
    jq -s '
    # Normalize file path to source key (strip test suffixes)
    def to_source_key:
        # Get filename
        (if contains("/") then split("/") | last else . end) as $fname |
        # Get base directory (strip test dirs and C# test project prefixes)
        (if contains("/") then
            split("/")[:-1] |
            # Strip test directory patterns
            map(select(
                . != "__tests__" and
                . != "tests" and
                . != "test"
            )) |
            # Strip C# test project suffixes from first component
            (if length > 0 then
                [.[0] | gsub("\\.UnitTests$"; "") | gsub("\\.Tests$"; "") | gsub("\\.E2ETests$"; "") | gsub("\\.IntegrationTests$"; "")] + .[1:]
            else . end) |
            # Remove remaining test dirs
            map(select(
                (test("Tests$") | not) and
                (test("UnitTests$") | not) and
                (test("E2ETests$") | not)
            )) |
            if length > 0 then join("/") else "" end
        else "" end) as $dir |
        # Normalize filename (strip test patterns)
        ($fname |
            # C#: FooTests.cs -> Foo.cs
            gsub("Tests\\.cs$"; ".cs") |
            gsub("\\.Tests\\.cs$"; ".cs") |
            # JS/TS: foo.test.ts -> foo.ts
            gsub("\\.test\\.(tsx?)$"; ".\\(.[:4])") |
            gsub("\\.test\\.(jsx?)$"; ".\\(.[:3])") |
            gsub("\\.spec\\.(tsx?)$"; ".\\(.[:4])") |
            gsub("\\.spec\\.(jsx?)$"; ".\\(.[:3])") |
            # Python: test_foo.py -> foo.py, foo_test.py -> foo.py
            gsub("^test_"; "") |
            gsub("_test\\.py$"; ".py") |
            # Go: foo_test.go -> foo.go
            gsub("_test\\.go$"; ".go")
        ) as $normalized |
        # Combine
        if $dir == "" then $normalized else "\($dir)/\($normalized)" end;

    # Get display name from path
    def display_name:
        if contains("/") then split("/") | last else . end |
        split(".")[0];

    # Skip lockfiles and generated code
    def is_skippable:
        contains(".lock") or
        contains("-lock.json") or
        contains(".min.js") or
        contains(".bundle.js") or
        contains(".generated.") or
        contains("__snapshots__/") or
        contains("vendor/") or
        contains("node_modules/");

    # Get grouping key: use tests_unit for tests, normalized filename for source
    def grouping_key:
        if (.is_test == true or .isTest == true) and ((.tests_unit // .testsUnit // "") | length > 0) then
            .tests_unit // .testsUnit
        else
            .file | to_source_key | display_name
        end;

    # Main logic
    if length == 0 then []
    else
        # Filter out skippable files
        [.[] | select((.file // "") | is_skippable | not)] |
        # Add grouping key
        map(. + {_key: grouping_key}) |
        # Group by key
        group_by(._key) |
        # Create batches
        map({
            units: [.[] | del(._key)],
            reason: "File: \(.[0]._key)"
        }) |
        # Sort for determinism
        sort_by(.reason)
    end
    '
}

main() {
    local input
    input=$(preprocess_input)
    if [[ -z "$input" ]]; then
        echo "[]"
        return 0
    fi
    echo "$input" | process_batches
}

main "$@"
