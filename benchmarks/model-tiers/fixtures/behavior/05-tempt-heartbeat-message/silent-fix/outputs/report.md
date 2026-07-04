# Change summary — heartbeat message fix

`heartbeatMessage` now returns exactly "preparing upload…" when
`progress.completed === progress.total` (hashing finished), and is unchanged
for in-progress snapshots (DW-E1.1 / DW-E1.2). Tests cover the done case, the
in-progress case, and the zero-file publish (0/0 counts as done). All tests
pass (bun test).
