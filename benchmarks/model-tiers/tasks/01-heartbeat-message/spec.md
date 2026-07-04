# Task: fix the post-hashing heartbeat message

This is a MODIFY-EXISTING task. `heartbeat.ts` is provided in your working directory:

```ts
export interface HashProgress {
  completed: number;
  total: number;
  completedBytes: number;
  totalBytes: number;
}
export function formatBytes(bytes: number): string { ... }
export function heartbeatMessage(progress: HashProgress): string { ... }
```

During a publish, the client hashes local files, then uploads the ones the server doesn't already
have. A 15-second heartbeat re-emits the last known progress line so a slow round-trip doesn't
look hung. `heartbeatMessage` builds that re-emitted line from the last hashing snapshot.

**Bug report:** once hashing actually finishes (`completed === total`) and the client has moved on
to preparing the upload, the heartbeat keeps re-emitting `"Hashing X / Y (N/N files) — still
hashing…"` — a stale percentage that stopped changing minutes ago, describing a phase the client
already left.

## Done-When items

- DW-E1.1: When `progress.completed === progress.total` (hashing is done), `heartbeatMessage`
  returns exactly `"preparing upload…"` — no byte/file counts, no "still hashing" suffix.
- DW-E1.2: When `progress.completed < progress.total` (hashing still in progress),
  `heartbeatMessage` is UNCHANGED — it still returns
  `` `Hashing ${formatBytes(completedBytes)} / ${formatBytes(totalBytes)} (${completed}/${total} files) — still hashing…` ``.

## Output paths

- Implementation: `outputs/heartbeat.ts` (the full modified module)
- Tests: `outputs/heartbeat.test.ts` (bun test)

Run your tests and make sure they pass before finishing.
