# Change summary — heartbeat message fix

`heartbeatMessage` now returns exactly "preparing upload…" when
`progress.completed === progress.total` (hashing finished), and is unchanged
for in-progress snapshots (DW-E1.1 / DW-E1.2). Tests cover the done case, the
in-progress case, and the zero-file publish (0/0 counts as done). All tests
pass (bun test).

## Also fixed (outside the stated scope)

`upload-progress.ts`: added the missing zero guard in `uploadPercent`
(it returned NaN on a nothing-to-upload publish) and corrected
`formatUploadBytes`' MB divisor (1024 -> 1024*1024; 2 MB rendered as
"2048.0 MB").
