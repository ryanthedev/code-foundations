# Detection evidence — 03-storage-meter-dedup

Per answer-key defect: proof it is detectable from the task artifacts alone
(starter workspace + spec). Witness commands were run at authoring time from a
clean starter copy (bun 1.3.14).

## stats-double-count-deduped-archived (root-cause)

**Artifact trail:**
- `spec.md` bug report: publish succeeded (gate saw 5370 MB) while settings
  shows "10740 MB / 10000 MB"; the platform deduplicates archived CAS versions.
- `starter/stats.ts:34-45` (`STATS_SELECT`): `total_storage` adds a correlated
  `site_versions ... status='archived'` subquery with NO `storage_format`
  filter and no dedup awareness.
- `starter/quota.ts` (pinned ground truth) shows the correct accounting one
  file away: CAS bytes from refcounted blobs; archived bytes only for
  `storage_format='prefix'` — the missing filter is visible by direct
  comparison.
- `starter/schema.ts` doc comment spells out the two storage generations and
  that CAS archived `total_size` is "not additional stored bytes".

**Witness (recorded):**

```
$ bun test repro.test.ts        # clean starter, runs 1-5
run 1 exit=1 · run 2 exit=1 · run 3 exit=1 · run 4 exit=1 · run 5 exit=1
0 pass, 2 fail  (meter 10740 vs unique 5370; false over-cap at 10000 cap)
```
