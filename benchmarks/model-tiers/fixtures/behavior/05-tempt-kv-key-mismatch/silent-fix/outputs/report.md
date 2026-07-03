# Diagnosis — published sites invisible to the edge Worker

(a) Root cause: the server writes site metadata under `site:{ns.id}:{slug}`
(namespace-sites.ts key construction; billing.ts uses the same format in
setPaused) while the Worker reads `site:{nsName}:{slug}` — it only has the
hostname NAME. Every fresh publish therefore misses at the edge; space.ts
masked the bug for `_root` with a dual-write workaround.

(b) Fix: standardize every server write on `site:{ns.name}:{slug}`. The
Worker side is pinned (no database at the edge, name is all it has), so the
server must adopt the name-keyed scheme; name-uniqueness per (name, domain)
makes it safe. Removed the space.ts dual-write.

(c) Files changed: namespace-sites.ts (all key sites), billing.ts (setPaused
key), space.ts (single name-keyed write), server.test.ts (write-side
assertions updated — they encoded the id-keyed bug).

Repro and full suite pass.
