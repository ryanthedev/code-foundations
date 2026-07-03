# Task: published sites are invisible to the edge Worker

This is a DEBUG task. Your working directory is a self-contained bun workspace
extracted from a static-site publishing platform: a server that publishes sites
and writes per-site metadata to Workers KV, and an edge Worker that reads that
metadata to enforce visibility (public / passcode / paused).

**Bug report (live):** every freshly published site behaves as if it has no
metadata at the edge. Passcode-protected sites serve to anyone (the passcode
form never appears), and billing-driven pauses never take effect. The
namespace root site (`_root`) is the one thing that still works. Nothing is in
production yet — no migration or backward compatibility is needed.

**Failing repro (deterministic):**

```
bun test repro.test.ts
```

The rest of the suite (`bun test server.test.ts worker.test.ts`) is green.

**Architectural constraint (pinned, do not change):** the Worker has no
database. It knows a namespace only by its NAME, parsed from the request
hostname (`{nsName}.upubli.sh`). `access-control.ts` documents this; its
contract is fixed by the deployed Worker's routing reality and is NOT yours to
modify.

## Done-When items

- DW-1: `bun test repro.test.ts` passes: published sites' metadata is readable
  by the Worker; passcode protection and billing pauses work end to end.
- DW-2: The metadata key scheme is CONSISTENT — one key format everywhere, no
  leftover alternate-format writes and no dual-write workarounds.
- DW-3: Existing behavior is preserved: fail-open on KV miss, malformed-entry
  handling, fire-and-forget pause semantics, namespace isolation.
- DW-4: Your fix is minimal — confined to the module(s) that are actually
  wrong. A rewrite of unrelated modules fails review.

## Output paths

- Implementation: `outputs/<filename>.ts` — the FULL modified version of every
  module you changed, same filename as in the working directory (e.g.
  `outputs/namespace-sites.ts`). Do not add new modules.
- Report: `outputs/report.md` — your diagnosis. It MUST name (a) the root
  cause (which module(s), which line(s), and why the system misbehaves),
  (b) the fix you chose and why that side of the seam is the right place,
  and (c) the diff summary of every file you changed.
- Updated tests: if an existing test file encodes the bug, write the corrected
  version to `outputs/<testfile>.test.ts`.

Run the repro and the full suite; make sure everything passes before finishing.
