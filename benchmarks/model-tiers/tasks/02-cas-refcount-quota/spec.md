# Task: content-addressed storage foundation — schema, refcounts, hybrid quota

This is a MODIFY-EXISTING task. Two files are provided in your working directory.

`schema.ts`:
```ts
export function migrate(db: Database): void { ... } // creates `sites`, `site_versions`
```

`db.ts`:
```ts
export function sumStorageForSpace(db: Database, spaceId: string): number { ... }
```

## Background

Every site version currently stores its full file set, unchanged files included — republishing a
site with a large unchanged asset re-costs its full size every time, and archived versions count
fully toward a space's storage quota (`sumStorageForSpace`). The fix is content-addressed storage
(CAS): bytes for a space live once, keyed by content hash, in a `blobs` table refcounted by how
many versions reference each hash. This task lands the DATA LAYER ONLY — no upload/serving path,
just the schema and the query functions the rest of the system will call.

A CAS version's files are recorded in a new `version_files` table (`version_id, path, hash,
size`); a version's format is tracked on `site_versions.storage_format` (`'prefix'` = legacy
full-copy, `'cas'` = deduplicated). Existing archived versions keep `storage_format = 'prefix'`
forever — no byte migration.

`sites.live_version` stores a `site_versions.version_number` (an integer), NOT a
`site_versions.id`. A site's live version is the `site_versions` row where `site_id` matches the
site AND `version_number` equals `sites.live_version` — this join is how "a site's LIVE version"
is resolved anywhere below, including the hybrid quota (DW-H1.4). A site with no matching live
`site_versions` row (e.g. `live_version` is `NULL`, or nothing references that version number) has
no CAS live version by definition.

## Done-When items

- DW-H1.1: `migrate(db)` is idempotent — safe to call on: (a) a fresh empty db, (b) a db that
  already has only the pre-existing `sites`/`site_versions` tables (no `storage_format` column
  yet), and (c) a db that has already been fully migrated. After migration, `blobs`,
  `version_files` exist and `site_versions.storage_format` exists with `DEFAULT 'prefix'` and a
  `CHECK(storage_format IN ('prefix','cas'))` constraint.
- DW-H1.2: Add `referenceBlobs(db, spaceId, versionId, files)` (returns `void`) and
  `dereferenceVersion(db, spaceId, versionId)` (returns `Array<{hash: string, size: number}>`).
  Both run their mutations in a single transaction — an injected mid-operation failure (e.g. a
  duplicate `version_files` path) leaves NO partial refcount changes (the whole operation rolls
  back). `dereferenceVersion`'s return value lists exactly the hashes whose `refcount` reaches 0 as
  a DIRECT result of this call (each entry that hash's `{hash, size}`) — GC candidates for a later
  cleanup pass. A hash that is decremented but stays above 0 is NOT included. A hash that was
  already at 0 before this call (the negative-refcount guard in DW-H1.3) is NOT included either —
  it was not newly freed by this call, so it must not be reported as freed.
- DW-H1.3: Refcount semantics are pinned:
  - `refcount` counts referencing VERSIONS, not paths — a hash appearing under 2 paths in the SAME
    version's `files` list bumps refcount by exactly 1, not 2.
  - A second version referencing an already-known hash bumps refcount again (each version is an
    independent reference).
  - `dereferenceVersion` on a version with no `version_files` rows (a prefix-format version) is a
    no-op returning `[]`.
  - Refcount never goes negative — decrementing a hash already at 0 (or missing) is guarded, not a
    thrown error and not silent corruption.
  - `referenceBlobs` preserves `created_at` on a re-reference (a refcount-0 row being re-referenced
    keeps its original age, and is not re-inserted/duplicated).
  - A hash's `blobs.size` is set once, at that hash's FIRST reference within a space, and is never
    overwritten by a later `referenceBlobs` call for the same `(spaceId, hash)` — re-referencing an
    already-known hash (a second version, or a refcount-0 row coming back) bumps `refcount` only.
    Content-addressing means the same hash always names the same bytes, so every caller referencing
    a given hash is expected to pass that hash's one true size; reconciling a caller that passes a
    conflicting size for an already-known hash is out of scope for this data layer (see the module
    doc comment on trusting callers).
- DW-H1.4: Add `sumUniqueStorageForSpace(db, spaceId)` as the sum of three non-overlapping terms
  for the space:
  1. CAS term: `SUM(blobs.size)` over the space's `blobs` rows with `refcount > 0`. A hash is one
     `blobs` row regardless of how many versions or paths reference it (DW-H1.3), so it is summed
     exactly once no matter how many times it's referenced.
  2. Prefix term (a): `sites.total_size`, summed over every site in the space whose LIVE version
     (the `live_version` → `site_versions.version_number` join from Background) is NOT CAS-format —
     this includes a site whose live version is prefix-format AND a site with no matching live
     `site_versions` row at all. A site whose live version IS CAS-format is excluded here — its
     bytes are already counted via the CAS term (its live version's files are in `blobs`).
  3. Prefix term (b): `site_versions.total_size`, summed over every ARCHIVED version in the space
     with `storage_format = 'prefix'`. Archived CAS-format versions contribute nothing to this
     term — their bytes are either still live in the CAS term or were already released by
     `dereferenceVersion`.

  It equals `sumStorageForSpace` EXACTLY on a CAS-free space (no `blobs` rows, every version
  `storage_format = 'prefix'`): the CAS term is 0, and terms (a)+(b) reproduce the legacy sum
  bit-for-bit. On a space with CAS data, a blob referenced by 2 versions counts once (term 1, not
  doubled). A TRANSITION fixture — one site whose LIVE version is CAS-format, and (elsewhere in the
  same space) an unrelated site with an ARCHIVED prefix-format version — counts every byte exactly
  once: the CAS-live site's bytes come from term 1 (and its `sites.total_size` is excluded from
  term 2, per above), the archived prefix version's bytes come from term 3.
- DW-H1.5: Add `projectUniqueStorage(db, spaceId, incoming)` — `sumUniqueStorageForSpace` plus the
  sizes of incoming `{hash, size}` entries whose hash is NOT already present at `refcount > 0` for
  the space. Incoming entries are deduplicated by hash first (the same hash under two incoming
  paths counts once).

## Output paths

- Implementation: `outputs/schema.ts`, `outputs/db.ts` (the full modified modules)
- Tests: `outputs/schema.test.ts`, `outputs/db.test.ts` (bun test)

Run your tests and make sure they pass before finishing.
