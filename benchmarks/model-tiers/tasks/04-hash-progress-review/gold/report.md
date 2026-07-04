# Review report — hashing instrumentation (enumeration + async hasher)

## Suite output

`bun test`: 10 pass, 0 fail (hashing.test.ts). A green suite — but several
requirements are unmet in ways the suite never exercises.

## Done-When verification

- DW-2.1: `HashProgress` exported `{completed, total, completedBytes, totalBytes}`;
  `hashFiles` accepts an optional synchronous `onHashProgress`.
  PREMISE: shape and optional sync callback present.
  EVIDENCE (file:line): src/hashing.ts:44-53 (interface), 316-321 (opts).
  TRACE (input→output): hashFiles(list, {onHashProgress: p => ...}) invokes the
  callback synchronously with all four fields.
  VERDICT: PASS

- DW-2.2: `listFiles` applies the ignore/exclusion rules (defaults + every
  documented `.upublishignore` pattern form), NO content reads.
  PREMISE: exact-name, `dir/`, and `*.ext` pattern forms all enforced.
  EVIDENCE (file:line): src/hashing.ts:109-115 — `matchesIgnore` implements
  exact-name and `*.ext` only; the `dir/` trailing-slash form its own doc
  comment (line 105-108) documents is not implemented.
  TRACE (input→output): `.upublishignore` = `private/` with `private/notes.txt`
  on disk → listFiles returns `["index.html", "private/notes.txt"]` — the
  directory is published.
  VERDICT: FAIL

- DW-2.3: fires at 0 and at completion; completed bytes from HASHED content;
  monotonic.
  PREMISE: opening `{completed: 0, completedBytes: 0, ...}` report before any
  hashing; byte counts from streamed content.
  EVIDENCE (file:line): src/hashing.ts:339-357 — no report is emitted before
  the loop (the first callback fires after file 1 completes), although the
  function's own doc (line 302-304) claims it; src/hashing.ts:346 —
  `completedBytes += entry.size` accumulates the statSync estimate, not
  `hashed.size` (the streamed bytes stored one line above into the result map).
  TRACE (input→output): two-file run → first report `{completed: 1, ...}`,
  never a zero report. Append 4 bytes to a listed 4-byte file before hashing →
  result map size 8, final `completedBytes` 4.
  VERDICT: FAIL

- DW-2.4: yields to the event loop ≥once during a multi-file hash AND mid-file
  for a file ≥ `yieldEvery` bytes — a scheduled MACROTASK interleaves.
  PREMISE: the yield releases the loop to queued timers/I/O.
  EVIDENCE (file:line): src/hashing.ts:173 —
  `yieldToEventLoop = () => Promise.resolve()` is a MICROTASK; awaiting it
  never lets a queued macrotask (timer, I/O completion) run. The doc comment on
  it still claims "Awaits a macrotask".
  TRACE (input→output): `setTimeout(0)` scheduled before
  `hashFiles(5 × 2 KB files, {yieldEvery: 1024})` does not fire during the
  run — no interleaving observed.
  VERDICT: FAIL

- DW-2.5: `collectFilesWithHashes` signature + return contract unchanged and
  synchronous; agrees with `hashFiles`.
  PREMISE: sync, `{files, excluded, warnings}`, digests match the async path.
  EVIDENCE (file:line): src/hashing.ts:377-387; suite test "hashes every
  listed file to the same digests as the sync collector" passed.
  TRACE (input→output): same tree → identical keys, hashes, sizes.
  VERDICT: PASS

- DW-2.6: with `onHashProgress` omitted, the returned map is identical.
  PREMISE: instrumentation changes nothing about the result.
  EVIDENCE (file:line): src/hashing.ts:351 — optional-chained callback; suite
  test "with no callback the result is identical" passed.
  TRACE (input→output): callback run vs bare run → deep-equal maps.
  VERDICT: PASS

## Edge cases

- Mid-file yield for a large file: the yield POINT exists (hashing.ts:224-228)
  but the yield itself is a microtask — BROKEN (see DW-2.4).
- All-empty files: totals carry both byte and file counts — OK.
- Empty list: fires nothing, returns {} — OK.
- File resized between stat and hash: reported bytes stale — BROKEN (see
  DW-2.3 / hashing.ts:346).
- Microtask is not a yield: violated at hashing.ts:173 (see DW-2.4).

## Issues

1. [HP-2] src/hashing.ts:173 — `yieldToEventLoop` awaits `Promise.resolve()`
   (microtask); queued macrotasks (pending notification sends, timers) never
   run during hashing, so the event loop is never actually released. Violates
   DW-2.4; contradicts its own doc comment. The visible test only proves
   async resolution, not interleaving.
2. [HP-1] src/hashing.ts:339-357 — the opening
   `{completed: 0, total, completedBytes: 0, totalBytes}` report is missing;
   the first callback fires after file 1. Violates DW-2.3 ("fires at 0");
   monotonicity tests cannot catch a sequence that starts at 1.
3. [HP-3] src/hashing.ts:346 — `completedBytes += entry.size` uses the stat
   estimate instead of `hashed.size` (the streamed bytes). Violates DW-2.3's
   bytes-from-hashed-content requirement (TOCTOU); green in tests only because
   fixtures never change size mid-run.
4. [HP-4] src/hashing.ts:109-115 — `matchesIgnore` drops the documented `dir/`
   pattern form; a `.upublishignore` directory pattern silently publishes the
   whole directory. Violates DW-2.2.

OVERALL: FAIL
