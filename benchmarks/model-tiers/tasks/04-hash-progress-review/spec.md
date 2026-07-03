# Review: verify this implementation against its requirements

Independently verify the implementation in the files below against the
requirements below. You did not write this code and have no information
about how or why it was written. Do NOT assume it is correct or complete.
Assume requirements may be unmet and bugs may be present; verify each item
from scratch against the actual code and executed test results. Do NOT
introduce requirements that are not listed here.

FIRST ACTION: run the test suite (command under "How to run the suite") via
Bash and capture its output BEFORE reading any source file. A passing suite is
evidence, not a verdict — requirements may be unmet in ways the suite never
exercises.

## Ground rules the requirements refer to (authoritative)

These definitions are part of the requirements below — verify against THEM,
not against whatever the code or its comments happen to say.

- `.upublishignore` convention: an optional file at the root of the directory
  being enumerated, listing exclusion patterns one per line; `#` comment lines
  and blank lines are skipped. Exactly three pattern forms are documented:
  an exact file or directory name (`secrets.txt`), a trailing-slash directory
  form (`private/`) that excludes a directory of that name and everything
  under it, and a `*.ext` suffix form (`*.log`). DW-2.2's "every documented
  `.upublishignore` pattern form" means these three.
- Prior contract of `collectFilesWithHashes` (the baseline DW-2.5's
  "unchanged" is judged against): `collectFilesWithHashes(dirPath: string)`
  returns SYNCHRONOUSLY (a plain value, never a Promise) an object
  `{ files, excluded, warnings }`, where `files` maps each kept file's
  root-relative path to `{ hash, size, fullPath }` — the file's MD5 hex
  digest, its byte size, and its absolute on-disk path — and
  `excluded`/`warnings` are string path lists from the enumeration.

## Requirements to verify (Done-When items)

For EACH item, fill the template. A PASS verdict REQUIRES execution evidence
(a passing test you ran, or observed behavior from code you executed) — not
"implemented". Do NOT skip items.

- DW-2.1: `HashProgress` is exported as `{completed, total, completedBytes,
  totalBytes}`; `hashFiles` accepts an optional synchronous `onHashProgress`
  callback.
  PREMISE: ___  EVIDENCE (file:line): ___  TRACE (input→output): ___  VERDICT: ___
- DW-2.2: `listFiles` enumerates publishable files with sizes applying the
  ignore/exclusion rules (defaults + every documented `.upublishignore`
  pattern form), performing NO content reads.
  PREMISE: ___  EVIDENCE (file:line): ___  TRACE (input→output): ___  VERDICT: ___
- DW-2.3: `hashFiles` fires `onHashProgress` at 0 (before any file is hashed)
  and at completion with `completed === total` and
  `completedBytes === totalBytes`, where completed bytes come from HASHED
  content (not stat sizes); counts are monotonically non-decreasing.
  PREMISE: ___  EVIDENCE (file:line): ___  TRACE (input→output): ___  VERDICT: ___
- DW-2.4: `hashFiles` yields to the event loop ≥once during a multi-file hash
  AND mid-file for a file ≥ `yieldEvery` bytes — a scheduled MACROTASK
  interleaves with the hashing work.
  PREMISE: ___  EVIDENCE (file:line): ___  TRACE (input→output): ___  VERDICT: ___
- DW-2.5: `collectFilesWithHashes(dirPath)` signature + return contract are
  unchanged and synchronous; it and `hashFiles` agree on hashes and sizes for
  the same tree.
  PREMISE: ___  EVIDENCE (file:line): ___  TRACE (input→output): ___  VERDICT: ___
- DW-2.6: With `onHashProgress` omitted, `hashFiles`' returned map is
  identical to a run with the callback supplied (the instrumentation changes
  nothing about the result).
  PREMISE: ___  EVIDENCE (file:line): ___  TRACE (input→output): ___  VERDICT: ___

## Edge cases — verify handling

These are explicit requirements with the same verdict standing as the DW items
above: an unhandled case listed here is a FAIL, not a Note. Verify the
implementation handles each.

- A single file ≥ `yieldEvery` bytes must yield MID-FILE, not only between
  files (one large asset must not block the event loop for its whole hash).
- All-empty files (`totalBytes === 0`): no divide-by-zero is forced on a
  consumer — both byte and file counts are carried.
- Empty list: no progress fires at all.
- A file whose on-disk size changes between enumeration (stat) and hashing:
  reported completed bytes follow the bytes actually hashed.
- A microtask is NOT a yield: awaiting a resolved promise does not release the
  event loop to queued I/O — the yield must be a macrotask.

## Files to review

- src/hashing.ts
- test/hashing.test.ts

## How to run the suite

```
bun test
```

Run it directly via Bash and capture the output.

## Output

Write your review to `outputs/report.md`. It MUST contain:

1. The captured suite output (pass/fail counts).
2. The filled PREMISE/EVIDENCE/TRACE/VERDICT template for every DW item.
3. An `## Issues` section: one entry per defect found — exact location
   (file:line), what is wrong, and why it violates a requirement above. Write
   "none" if you found none.
4. A final line: `OVERALL: PASS` or `OVERALL: FAIL`.
