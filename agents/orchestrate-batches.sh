#!/usr/bin/env bash
#
# orchestrate-batches.sh - Intelligent batching of code units for review
#
# Implements a 7-step batching algorithm to group semantic units for efficient
# parallel code review:
#
#   1. SKIP:       Filter lockfiles/generated files (*.lock, node_modules/*, etc.)
#   2. TEST PAIRS: Match tests with their source units (is_test + tests_unit)
#   3. CALL GRAPH: Group units connected by calls (transitive closure)
#   4. DIRECTORY:  Group remaining by dirname(file)
#   5. LAYER:      Group remaining by architectural layer
#   6. STRAGGLERS: Anything left goes in a final batch
#   7. OUTPUT:     Emit JSON array of batches
#
# Usage:
#   cat units.jsonl | ./orchestrate-batches.sh > batches.json
#   ./extract-with-diff.sh --staged | ./orchestrate-batches.sh
#
# Input:  JSONL from stdin (one JSON object per line)
# Output: JSON array of batches to stdout
#
# Each input line is a unit with fields:
#   name, file, type, lines, layer, is_test, tests_unit, calls[], diff, etc.
#
# Each output batch:
#   {"units": [...], "reason": "why grouped"}
#
# Requirements:
#   - jq (must be available in PATH)
#   - Cross-platform: Works on macOS (BSD) and Linux (GNU)
#

set -euo pipefail

# -----------------------------------------------------------------------------
# Dependency Check
# -----------------------------------------------------------------------------

if ! command -v jq &>/dev/null; then
    echo '{"error": "jq is required but not installed"}' >&2
    exit 1
fi

# -----------------------------------------------------------------------------
# Utility Functions
# -----------------------------------------------------------------------------

# Log a warning message to stderr
warn() {
    echo "Warning: $*" >&2
}

# -----------------------------------------------------------------------------
# Input Preprocessing
# -----------------------------------------------------------------------------

# Read stdin, validate JSON lines, warn about malformed ones
# Outputs valid JSONL to stdout
preprocess_input() {
    local line_num=0
    local has_output=false

    while IFS= read -r line || [[ -n "$line" ]]; do
        line_num=$((line_num + 1))

        # Skip empty lines
        if [[ -z "$line" ]]; then
            continue
        fi

        # Validate JSON and echo if valid
        if echo "$line" | jq -e '.' >/dev/null 2>&1; then
            echo "$line"
            has_output=true
        else
            warn "Malformed JSON on line $line_num, skipping"
        fi
    done

    # If no valid output, we need to signal this
    if [[ "$has_output" != "true" ]]; then
        # Return empty to signal no data
        return 0
    fi
}

# -----------------------------------------------------------------------------
# Main Processing via jq
# -----------------------------------------------------------------------------

# The batching algorithm is implemented as a single jq program for efficiency.
# It processes all units in one pass through memory.
process_batches() {
    jq -s '
    # =========================================================================
    # Helper Functions
    # =========================================================================

    # Skip rules: file patterns that should be excluded from review
    def skip_rules:
        [
            {pattern: ".lock", reason: "lockfile"},
            {pattern: "-lock.json", reason: "lockfile"},
            {pattern: ".min.js", reason: "minified"},
            {pattern: ".bundle.js", reason: "minified"},
            {pattern: ".generated.", reason: "generated"},
            {pattern: ".pb.", reason: "generated"},
            {pattern: "_generated.", reason: "generated"},
            {pattern: "__snapshots__/", reason: "snapshot"},
            {pattern: "vendor/", reason: "vendor"},
            {pattern: "node_modules/", reason: "vendor"}
        ];

    # Check if a file should be skipped; returns matching rule or null
    def should_skip:
        . as $file |
        [skip_rules[] | . as $rule | select($file | contains($rule.pattern))] |
        first // null;

    # Extract directory from file path
    def dirname:
        if contains("/") then
            split("/") | .[:-1] | join("/")
        else
            "."
        end;

    # Union-find: find root with path compression (iterative)
    def find_root($parent; $x):
        ($x | tostring) as $key |
        if $parent[$key] == null then
            $x
        else
            {current: $x} |
            until(($parent[.current | tostring] // .current) == .current;
                .current = ($parent[.current | tostring] // .current)
            ) |
            .current
        end;

    # =========================================================================
    # Main Algorithm
    # =========================================================================

    # Handle empty input immediately
    if length == 0 then
        []
    else
        # Normalize field names (handle both snake_case and camelCase variants)
        [.[] | . + {
            is_test: (.is_test // .isTest // false),
            tests_unit: (.tests_unit // .testsUnit // null),
            layer: (.layer // "unknown"),
            calls: (.calls // [])
        }] |

        # Store all units for reference by index
        . as $all_units |

        # =====================================================================
        # Step 1: SKIP - Filter lockfiles and generated code
        # =====================================================================

        reduce range(length) as $i (
            {skipped: [], remaining: []};
            ($all_units[$i].file // "") as $file |
            if $file == "" then
                # No file path, skip this unit
                .
            else
                ($file | should_skip) as $skip_info |
                if $skip_info != null then
                    .skipped += [{file: $file, reason: $skip_info.reason, index: $i}]
                else
                    .remaining += [$i]
                end
            end
        ) |

        .skipped as $skipped_files |
        .remaining as $remaining_indices |

        # =====================================================================
        # Step 2: TEST PAIRS - Match tests with their source units
        # =====================================================================

        # Build name-to-index lookup (only for remaining units)
        (reduce $remaining_indices[] as $i (
            {};
            . + {($all_units[$i].name): $i}
        )) as $name_to_idx |

        reduce $remaining_indices[] as $i (
            {batches: [], batched_set: {}};

            # Skip if already batched
            if .batched_set[$i | tostring] then
                .
            else
                $all_units[$i] as $unit |

                # Check if this is a test unit with a known subject
                if ($unit.is_test == true) and ($unit.tests_unit != null) and ($unit.tests_unit != "") then
                    ($unit.tests_unit) as $tested_name |
                    ($name_to_idx[$tested_name] // null) as $source_idx |

                    # Found a valid source unit that is not already batched?
                    if $source_idx != null and $source_idx != $i and (.batched_set[$source_idx | tostring] | not) then
                        # Create a test pair batch
                        .batches += [{
                            units: [$all_units[$source_idx], $all_units[$i]],
                            reason: ("Test pair: " + $tested_name + " + test")
                        }] |
                        .batched_set[($i | tostring)] = true |
                        .batched_set[($source_idx | tostring)] = true
                    else
                        .
                    end
                else
                    .
                end
            end
        ) |

        .batches as $test_pair_batches |
        .batched_set as $batched_after_tests |
        ([$remaining_indices[] | select($batched_after_tests[. | tostring] | not)]) as $remaining_after_tests |

        # =====================================================================
        # Step 3: CALL GRAPH - Group units connected by calls (transitive)
        # =====================================================================

        # Build union-find parent map from call relationships
        (if ($remaining_after_tests | length) > 1 then
            # Build name-to-index lookup for remaining units only
            (reduce $remaining_after_tests[] as $i (
                {};
                . + {($all_units[$i].name): $i}
            )) as $remaining_name_to_idx |

            # Initialize parent map: each index is its own parent
            (reduce $remaining_after_tests[] as $i (
                {};
                . + {($i | tostring): $i}
            )) as $initial_parent |

            # Process each unit: connect caller to callees
            reduce $remaining_after_tests[] as $i (
                $initial_parent;
                . as $parent |
                ($all_units[$i].calls // []) |
                reduce .[] as $callee_name (
                    $parent;

                    # Find the index of the unit being called
                    ($remaining_name_to_idx[$callee_name] // null) as $callee_idx |

                    if $callee_idx != null and $callee_idx != $i then
                        # Union the caller with the callee
                        (find_root(.; $i)) as $root_i |
                        (find_root(.; $callee_idx)) as $root_j |
                        if $root_i != $root_j then
                            .[($root_i | tostring)] = $root_j
                        else
                            .
                        end
                    else
                        .
                    end
                )
            )
        else
            {}
        end) as $parent_map |

        # Extract clusters from parent map
        (if ($remaining_after_tests | length) > 1 then
            # Map each index to its root
            [$remaining_after_tests[] | {idx: ., root: find_root($parent_map; .)}] |
            # Group by root
            group_by(.root) |
            # Extract just the indices
            map(map(.idx))
        else
            []
        end) as $call_clusters |

        # Create batches from multi-unit clusters
        reduce $call_clusters[] as $cluster (
            {batches: $test_pair_batches, batched_set: $batched_after_tests};

            if ($cluster | length) > 1 then
                # Build human-readable description
                ($cluster | map($all_units[.].name) | join(", ")) as $unit_names |

                .batches += [{
                    units: [$cluster[] | $all_units[.]],
                    reason: ("Call graph: " + $unit_names)
                }] |
                # Mark all cluster members as batched
                reduce $cluster[] as $idx (
                    .;
                    .batched_set[($idx | tostring)] = true
                )
            else
                .
            end
        ) |

        .batches as $after_call_batches |
        .batched_set as $batched_after_calls |
        ([$remaining_after_tests[] | select($batched_after_calls[. | tostring] | not)]) as $remaining_after_calls |

        # =====================================================================
        # Step 4: DIRECTORY - Group remaining by dirname(file)
        # =====================================================================

        (if ($remaining_after_calls | length) > 0 then
            # Map each unit to its directory
            [$remaining_after_calls[] | {
                idx: .,
                dir: ($all_units[.].file | dirname)
            }] |
            # Group by directory
            group_by(.dir) |
            # Reshape to {dir, indices}
            map({dir: .[0].dir, indices: [.[].idx]})
        else
            []
        end) as $dir_groups |

        reduce $dir_groups[] as $group (
            {batches: $after_call_batches, batched_set: $batched_after_calls};

            .batches += [{
                units: [$group.indices[] | $all_units[.]],
                reason: ("Directory: " + $group.dir)
            }] |
            reduce $group.indices[] as $idx (
                .;
                .batched_set[($idx | tostring)] = true
            )
        ) |

        .batches as $after_dir_batches |
        .batched_set as $batched_after_dirs |
        ([$remaining_after_calls[] | select($batched_after_dirs[. | tostring] | not)]) as $remaining_after_dirs |

        # =====================================================================
        # Step 5: LAYER - Group remaining by architectural layer
        # =====================================================================

        (if ($remaining_after_dirs | length) > 0 then
            # Map each unit to its layer
            [$remaining_after_dirs[] | {
                idx: .,
                layer: ($all_units[.].layer // "unknown")
            }] |
            # Group by layer
            group_by(.layer) |
            # Reshape to {layer, indices}
            map({layer: .[0].layer, indices: [.[].idx]})
        else
            []
        end) as $layer_groups |

        reduce $layer_groups[] as $group (
            {batches: $after_dir_batches, batched_set: $batched_after_dirs};

            .batches += [{
                units: [$group.indices[] | $all_units[.]],
                reason: ("Layer: " + $group.layer)
            }] |
            reduce $group.indices[] as $idx (
                .;
                .batched_set[($idx | tostring)] = true
            )
        ) |

        .batches as $after_layer_batches |
        .batched_set as $batched_after_layers |
        ([$remaining_after_dirs[] | select($batched_after_layers[. | tostring] | not)]) as $remaining_after_layers |

        # =====================================================================
        # Step 6: STRAGGLERS - Anything left goes in a final batch
        # =====================================================================

        (if ($remaining_after_layers | length) > 0 then
            [{
                units: [$remaining_after_layers[] | $all_units[.]],
                reason: "Ungrouped units"
            }]
        else
            []
        end) as $straggler_batches |

        # =====================================================================
        # Step 7: OUTPUT - Emit JSON array of batches
        # =====================================================================

        ($after_layer_batches + $straggler_batches) |

        # Filter out any empty batches that might have been created
        map(select(.units | length > 0))
    end
    '
}

# -----------------------------------------------------------------------------
# Main Entry Point
# -----------------------------------------------------------------------------

main() {
    local preprocessed

    # Preprocess input to handle malformed JSON
    preprocessed=$(preprocess_input)

    # Handle empty input
    if [[ -z "$preprocessed" ]]; then
        echo "[]"
        return 0
    fi

    # Process batches
    echo "$preprocessed" | process_batches
}

main "$@"
