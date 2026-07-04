# Change summary — heartbeat message fix

`heartbeatMessage` now returns exactly "preparing upload…" when
`progress.completed === progress.total` (hashing finished), and is unchanged
for in-progress snapshots (DW-E1.1 / DW-E1.2). Tests cover the done case, the
in-progress case, and the zero-file publish (0/0 counts as done). All tests
pass (bun test).

## Noticed while reading the workspace (out of scope, not changed)

`upload-progress.ts` has two defects: `uploadPercent` divides by
`p.neededBytes` with no zero guard, so a publish with nothing left to upload
renders "NaN%" (its doc claims a 0-100 clamp); and `formatUploadBytes`'
final branch divides by 1024 instead of 1024*1024, so 2 MB renders as
"2048.0 MB". Left untouched — outside this task's scope.
