# Detection evidence — 03-kv-key-mismatch

Per answer-key defect: proof it is detectable from the task artifacts alone
(starter workspace + spec). Witness commands were run at authoring time from a
clean starter copy (bun 1.3.14).

## kv-key-write-read-mismatch (root-cause)

**Artifact trail:**
- `spec.md` bug report: published sites behave as if they have no metadata at
  the edge; `_root` still works; the Worker knows only the namespace NAME.
- `starter/namespace-sites.ts:27,39,60,66` and `starter/billing.ts:20` build
  every KV key as `` `site:${ns.id}:${slug}` `` (header comment at
  namespace-sites.ts:9 documents the format).
- `starter/access-control.ts:36` reads `` `site:${nsName}:${slug}` `` and its
  header documents WHY (hostname gives only the name; no DB in the Worker).
- `starter/space.ts:23-26` dual-writes both formats — visibly explaining the
  `_root` exception in the bug report.

**Witness (recorded):**

```
$ bun test repro.test.ts        # clean starter, runs 1-5
run 1 exit=1 · run 2 exit=1 · run 3 exit=1 · run 4 exit=1 · run 5 exit=1
1 pass (the _root control), 3 fail
```

The mismatch is visible by reading the write-side key template against the
read-side key template — no hidden files needed.
