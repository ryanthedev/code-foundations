# Phase 2: extract-with-diff.sh Pseudocode

**Date:** 2026-02-01
**Status:** Ready for Implementation

---

## Design Decision

### Approaches Considered

1. **Two-Pass Processing** - Separate git calls for status and hunks, then batch process
2. **Single-Pass Streaming** - Parse everything from one git diff call as we stream
3. **Per-File Processing** - N git calls, one per file

### Choice: Two-Pass with Streaming Output

- Two git calls (acceptable constant)
- Parse all hunks into memory first (small for typical PRs)
- Stream JSONL output per unit (constant memory for output)
- Simpler than full streaming parser

---

## Main Script Flow

```
Parse command line arguments to extract git-diff-args
  If no args provided, use unstaged changes (empty args)
  Validate that args are valid git diff arguments

Get the list of changed files with their change status
  Run git diff with name-status option and provided args
  Parse output to get file paths and status letters
  Map status letters to semantic values:
    A → added
    M → modified
    D → deleted
    R → modified (treat rename as modification)

Get all diff hunks for the changed files
  Run git diff with unified format and provided args
  Capture the complete diff output for parsing

Parse the diff output into a file-to-hunks lookup table
  Call parse_diff_hunks with the diff output
  Result is an associative structure: file path → list of hunks

For each changed file in the status list:
  Determine the source for unit extraction
    If file is deleted:
      Extract file content from HEAD revision
      Use temporary file for extraction
    Otherwise:
      Use the working tree version of the file

  Extract semantic units from the file source
    Call extract-units.sh with the file path
    Parse the JSON output to get list of units

  Get the hunks for this file from the lookup table
    If no hunks exist, skip this file

  For each unit extracted from the file:
    Find overlapping hunks for this unit
      For each hunk in the file's hunk list:
        If overlaps(unit lines, hunk range):
          Add hunk to the matching list

    If no hunks overlap with this unit:
      Skip this unit (it was not changed)

    Build the diff field
      Concatenate all matching hunks
      Strip git header lines (diff --git, index, ---, +++)
      Keep only hunk headers and content lines

    Generate a summary from the unit name and diff content
      Call generate_summary with name and diff

    Infer the architectural layer from file path
      Match path against layer patterns
      Default to "unknown" if no pattern matches

    Compute the change status for this unit
      Use the file-level status (added, modified, deleted)

    Build the complete JSON object
      Include all required fields from spec
      Include diff, summary, changeStatus, layer
      Include all fields from extract-units.sh output

    Output the JSON object as a single line to stdout
      This enables streaming consumption

Exit with success
```

---

## Function: parse_diff_hunks

**Purpose:** Parse unified diff output into a lookup table of file → hunks

**Input:** Complete git diff output as string

**Output:** Associative array mapping file path to list of hunk objects

```
Initialize empty file-to-hunks lookup table
Initialize current file as empty
Initialize current hunk as empty
Initialize current hunk content as empty list

For each line in the diff output:

  If line starts with "diff --git":
    If current hunk is not empty:
      Finalize current hunk with collected content
      Add current hunk to current file's hunk list
      Clear current hunk

    Extract file path from the line
      Parse the b/ path from "diff --git a/... b/..."
    Set current file to the extracted path

    If file not in lookup table:
      Initialize empty hunk list for this file

  Else if line starts with "@@":
    If current hunk is not empty:
      Finalize current hunk with collected content
      Add current hunk to current file's hunk list

    Parse hunk header to extract line ranges
      Match pattern: @@ -oldstart,oldcount +newstart,newcount @@
      Extract newstart and newcount from the + portion
      Calculate hunk_end as newstart + newcount - 1
      Handle case where count is omitted (means count of 1)

    Initialize new hunk object
      Set start_line to newstart
      Set end_line to calculated end
      Start content with the hunk header line

  Else if current hunk is not empty:
    Append line to current hunk content
      Skip --- and +++ header lines
      Keep context lines (space prefix)
      Keep added lines (+ prefix)
      Keep removed lines (- prefix)

If current hunk is not empty at end of input:
  Finalize current hunk with collected content
  Add current hunk to current file's hunk list

Return the file-to-hunks lookup table
```

---

## Function: get_change_status

**Purpose:** Map git status letter to semantic change status

**Input:** Single character status from git diff --name-status

**Output:** String: "added", "modified", or "deleted"

```
If status is "A":
  Return "added"

Else if status is "M":
  Return "modified"

Else if status is "D":
  Return "deleted"

Else if status is "R":
  Return "modified"
  Comment: Renames are treated as modifications

Else if status starts with "R":
  Return "modified"
  Comment: Handle rename with percentage (R100, R095, etc.)

Else:
  Return "modified"
  Comment: Default to modified for unknown statuses (C, T, U, X)
```

---

## Function: overlaps

**Purpose:** Determine if a unit's line range overlaps with a hunk's line range

**Input:**
- unit_lines: Array of two integers [start_line, end_line]
- hunk_range: Object with start_line and end_line

**Output:** Boolean

```
Extract unit_start as first element of unit_lines
Extract unit_end as second element of unit_lines
Extract hunk_start from hunk range
Extract hunk_end from hunk range

If unit_start is less than or equal to hunk_end:
  And unit_end is greater than or equal to hunk_start:
    Return true
    Comment: Ranges overlap

Return false
Comment: No overlap
```

**Visual explanation:**
```
Overlap cases:
  Unit:    [=====]          Unit:      [=====]
  Hunk:      [=====]        Hunk:  [=====]
  Result: overlap           Result: overlap

  Unit:    [=====]          Unit:  [===============]
  Hunk:      [=]            Hunk:       [===]
  Result: overlap           Result: overlap

No overlap:
  Unit:  [=====]
  Hunk:           [=====]
  Result: no overlap (unit_end < hunk_start)
```

---

## Function: generate_summary

**Purpose:** Create a brief summary of what changed in a unit

**Input:**
- name: The unit name (function/class/method name)
- diff: The unified diff content for this unit

**Output:** String summary, max 80 characters

```
Count lines in diff starting with "+" but not "++"
  Store as added_count

Count lines in diff starting with "-" but not "--"
  Store as removed_count

If removed_count is zero and added_count is greater than zero:
  Return "Add " concatenated with name
  Comment: New content with no removals suggests addition

Else if added_count is greater than twice removed_count:
  Return "Extend " concatenated with name
  Comment: Significantly more additions than removals

Else if removed_count is greater than twice added_count:
  Return "Simplify " concatenated with name
  Comment: Significantly more removals than additions

Else:
  Return "Update " concatenated with name
  Comment: Balanced changes suggest refactoring/updating
```

---

## Function: infer_layer

**Purpose:** Determine architectural layer from file path

**Input:** File path string

**Output:** Layer enum value: api, service, domain, data, infra, test, config, unknown

```
If path matches pattern **/api/** or **/routes/** or **/handlers/** or **/controllers/**:
  Return "api"

Else if path matches pattern **/services/** or **/usecases/**:
  Return "service"

Else if path matches pattern **/domain/** or **/models/** or **/entities/**:
  Return "domain"

Else if path matches pattern **/data/** or **/repositories/** or **/dal/**:
  Return "data"

Else if path matches pattern **/infra/** or **/infrastructure/** or **/providers/**:
  Return "infra"

Else if path matches pattern **/*.test.* or **/*.spec.* or **/tests/** or **/__tests__/**:
  Return "test"

Else if path matches pattern **/config/** or *.config.*:
  Return "config"

Else:
  Return "unknown"
```

---

## JSONL Output Format

Each line is a complete JSON object with these fields:

```
Required fields (from spec):
  file         - Relative file path
  name         - Unit identifier
  type         - Semantic type (function, method, class, etc.)
  lines        - [startLine, endLine] array
  diff         - Unified diff hunk content
  summary      - Brief description of changes

Added by this script:
  changeStatus - "added", "modified", or "deleted"
  layer        - Inferred architectural layer

Preserved from extract-units.sh:
  containingType, visibility, modifiers, params, paramCount,
  returnType, hasLoops, hasTryCatch, hasAsync, hasThrow,
  hasRecursion, nestingDepth, isTest, testsUnit, etc.
```

**Example output line:**
```
{"file":"src/api/users.ts","name":"createUser","type":"function","lines":[15,67],"diff":"@@ -15,6 +15,20 @@\n+  const email = req.body.email;","changeStatus":"modified","summary":"Extend createUser","layer":"api","hasAsync":true,"hasTryCatch":true}
```

---

## Deleted Files Handling

```
When a file has status "D" (deleted):

  The file no longer exists in working tree
  Must extract units from the last committed version

  Get file content from HEAD:
    Run git show HEAD:<filepath>
    Write to temporary file

  Extract units from the temporary file
    Run extract-units.sh on temporary file
    Update file paths in output to use original path

  Build diff showing removal:
    All lines appear with "-" prefix
    Hunk header shows old line numbers

  Set changeStatus to "deleted" for all units in file

  Clean up temporary file
```

---

## Error Handling

```
If git diff command fails:
  Output error message to stderr
  Exit with non-zero status

If extract-units.sh fails for a file:
  Output warning to stderr including file path
  Continue processing remaining files
  Comment: Partial results are better than no results

If file cannot be read:
  Output warning to stderr
  Skip the file
  Continue processing

If JSON parsing fails for a unit:
  Output warning to stderr
  Skip the malformed unit
  Continue processing
```

---

## Performance Notes

**Single git diff call:**
- Use git diff once for all hunks (not per-file)
- Parse the complete output in memory
- Typical PR diff output is small (< 1MB)

**Streaming output:**
- Output each JSONL line immediately after processing unit
- Do not accumulate all results in memory
- Consumer can process units as they arrive

**Temporary files for deleted files:**
- Create in system temp directory
- Clean up after extraction
- One temp file at a time (not all deleted files at once)
