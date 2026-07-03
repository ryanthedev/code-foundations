# Detection evidence — 04-hash-progress-review

Per answer-key defect: proof it is detectable from the task artifacts alone —
the starter workspace (code + green visible suite) and the spec's requirement
text. No diff is shown to the reviewer; nothing below requires one. Witness
commands were run at authoring time from the starter (bun 1.3.14); the visible
suite over the planted code is `bun test` → **10 pass, 0 fail**.

## HP-1-missing-opening-zero-report (dw-unmet, DW-2.3)

- Trail: spec DW-2.3 ("fires at 0 ... before any file is hashed") + the
  function's own doc (`src/hashing.ts` hashFiles doc: "fires with everything
  at zero before any file is hashed") vs the loop body at
  `src/hashing.ts:339-357`, where no pre-loop report exists.
- Witness (recorded): hashFiles over 2 files → first report
  `{"completed":1,"total":2,"completedBytes":2,"totalBytes":6}` — never a zero
  report. The visible monotonicity test stays green (a sequence starting at 1
  is still monotonic).

## HP-2-microtask-yield (dw-unmet, DW-2.4)

- Trail: spec DW-2.4 ("a scheduled MACROTASK interleaves") + spec edge case
  ("a microtask is NOT a yield") vs `src/hashing.ts:173`
  (`yieldToEventLoop = () => Promise.resolve()`), whose own doc comment still
  claims "Awaits a macrotask".
- Witness (recorded): `setTimeout(0)` scheduled before
  `hashFiles(5 × 2 KB files, {yieldEvery: 1024})` → macrotask interleaved:
  `false` (spec: true). The visible test only proves the promise resolves.

## HP-3-stat-bytes-reported (hidden-defect, DW-2.3 bytes-from-hashed-content)

- Trail: `HashProgress` doc ("cumulative, from streamed content — not stat";
  "AUTHORITATIVE") + spec edge case (file resized between stat and hash) vs
  `src/hashing.ts:346` (`completedBytes += entry.size`, the stat estimate,
  while `hashed.size` is stored into the result map one line above).
- Witness (recorded): append 4 bytes to a listed 4-byte file before hashing →
  result map size `8`, final `completedBytes` `4` (spec: both 8). Green in the
  visible suite because fixtures never change size mid-run.

## HP-4-dir-pattern-dropped (dw-unmet, DW-2.2)

- Trail: spec DW-2.2 ("every documented `.upublishignore` pattern form") + the
  function's own doc comment (`src/hashing.ts:105-108` documents exact-name,
  `dir/`, and `*.ext`) vs the body at `src/hashing.ts:109-115`, which
  implements only two of the three forms.
- Witness (recorded): `.upublishignore` = `private/` with
  `private/notes.txt` on disk → `listFiles` returns
  `["index.html","private/notes.txt"]` (spec: `["index.html"]`). The visible
  suite exercises only exact-name and `*.ext`.

## Stratification note (per SWR-Bench)

Violations span enumeration rules, progress reporting, byte accounting, and
scheduling semantics inside one real extracted module (2 kinds: 3 dw-unmet +
1 hidden-defect), with no marker comments; each hides behind a realistically
weakened or absent test. Doc/code drift — not diff shape — is the detection
surface.
