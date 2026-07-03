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

## Done-When items

- DW-H1.1: `migrate(db)` is idempotent — safe to call on: (a) a fresh empty db, (b) a db that
  already has only the pre-existing `sites`/`site_versions` tables (no `storage_format` column
  yet), and (c) a db that has already been fully migrated. After migration, `blobs`,
  `version_files` exist and `site_versions.storage_format` exists with `DEFAULT 'prefix'` and a
  `CHECK(storage_format IN ('prefix','cas'))` constraint.
- DW-H1.2: Add `referenceBlobs(db, spaceId, versionId, files)` and
  `dereferenceVersion(db, spaceId, versionId)`. Both run their mutations in a single transaction —
  an injected mid-operation failure (e.g. a duplicate `version_files` path) leaves NO partial
  refcount changes (the whole operation rolls back).
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
- DW-H1.4: Add `sumUniqueStorageForSpace(db, spaceId)`. It equals `sumStorageForSpace` EXACTLY on a
  CAS-free space (no `blobs` rows, every version `storage_format = 'prefix'`). On a space with CAS
  data, a blob referenced by 2 versions counts once. A TRANSITION fixture — one site whose LIVE
  version is CAS-format, and (elsewhere in the same space) an unrelated site with an ARCHIVED
  prefix-format version — counts every byte exactly once (no double-count, no drop).
- DW-H1.5: Add `projectUniqueStorage(db, spaceId, incoming)` — `sumUniqueStorageForSpace` plus the
  sizes of incoming `{hash, size}` entries whose hash is NOT already present at `refcount > 0` for
  the space. Incoming entries are deduplicated by hash first (the same hash under two incoming
  paths counts once).

## Output paths

- Implementation: `outputs/schema.ts`, `outputs/db.ts` (the full modified modules)
- Tests: `outputs/schema.test.ts`, `outputs/db.test.ts` (bun test)

Run your tests and make sure they pass before finishing.
