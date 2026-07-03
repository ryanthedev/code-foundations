# Task: settings storage meter shows a false "over cap"

This is a DEBUG task. Your working directory is a self-contained bun workspace
extracted from a static-site publishing platform's storage accounting: a
publish gate that admits or blocks publishes against a byte cap, and read-side
stats queries that drive the profile overview and the account settings meter.

**Bug report (live, verified against the production database):** a pro user
(10 GB cap) published a large site. The publish SUCCEEDED and billing charged
nothing extra — yet the settings page shows **"10740 MB / 10000 MB — over
cap"**. The platform's storage is content-addressed (CAS): re-published
versions of the same content share deduplicated blobs, so archiving a version
does not store its bytes again.

**Failing repro (deterministic):**

```
bun test repro.test.ts
```

The rest of the suite (`bun test stats.test.ts quota.test.ts`) is green.

**Ground truth (pinned, do not change):** `quota.ts` is the gate's
dedup-aware accounting, verified against production — it is authoritative for
how many bytes a space really occupies, and billing depends on it. `quota.ts`,
`schema.ts`, and `fixtures.ts` are NOT yours to modify.

## Done-When items

- DW-1: `bun test repro.test.ts` passes: the account meter number equals the
  space's real (deduplicated) footprint, and a user the gate admits is never
  shown as over cap.
- DW-2: Per-namespace stats no longer double-count deduplicated archived
  versions; deep version history does not inflate any reported number.
- DW-3: The gate's numbers are byte-identical to before your change.
- DW-4: Existing behavior is preserved: role tagging in the owned∪granted
  listing, staging exclusion, granted namespaces not billed to the grantee,
  empty/absent-space zero handling.
- DW-5: Your fix is minimal — confined to the module(s) that are actually
  wrong. A rewrite of unrelated modules fails review.

## Output paths

- Implementation: `outputs/<filename>.ts` — the FULL modified version of every
  module you changed, same filename as in the working directory (e.g.
  `outputs/stats.ts`). Do not add new modules.
- Report: `outputs/report.md` — your diagnosis. It MUST name (a) the root
  cause (which query/function, which lines, and why the number inflates),
  (b) the fix you chose and why the read side rather than the gate is the
  right place, and (c) the diff summary of every file you changed.
- Updated tests: if an existing test file encodes the bug, write the corrected
  version to `outputs/<testfile>.test.ts`.

Run the repro and the full suite; make sure everything passes before finishing.
