# Gates in depth

## Contents
1. Two modes, one script
2. The flat full gate
3. Targets and cleanup
4. The quiet timing runner
5. Gate lines that cannot fail (or cannot pass)
6. Shared test kit
7. Fuzz harness
8. Migrating an existing nested gate

## 1. Two modes, one script

| Mode | Who runs it | Target | Lower phases | Last line on success |
|---|---|---|---|---|
| job-scoped (default) | builders, verifiers, fix rounds | the session's persistent `build/target/<job>` | skipped | `PN GATE PARTIAL: skipped ...` |
| full (`GATE_FULL=1`) | the lead, right before commit | fresh per run, deleted on exit | once, through `gates/all.sh` | `PN GATE PASS` |

A builder's PARTIAL run shows only that its own phase works. A break in an earlier phase shows up at the
lead's full run, which is when it matters. The omni speed review estimated (not measured) that this saves
about 7 of every 8 parts of a phase-4-and-later gate run.

## 2. The flat full gate

`gates/all.sh` builds the workspace once and runs `cargo test --workspace` once. Then it runs each phase's
non-cargo steps in order (client scripts, offline rebuild checks, packaging checks). Phase scripts expose those
steps as functions or small scripts so `all.sh` can call them without re-running cargo.

Before switching from nested to flat, run one nested run and one flat run and diff the list of test names that
ran. A test that was only reached through a nested script is the usual casualty.

## 3. Targets and cleanup

- Never share a cargo target between sessions. Cargo takes a file lock on it, so a second session blocks or
  thrashes it.
- A per-run target is deleted when the run passes. A failed or interrupted run keeps it and prints its path, so
  the failure can be inspected; the parent deletes it at job close. The lock is always released (EXIT trap).
- Use `cargo clean --target-dir <dir>` to delete. It works where `rm -rf` is refused by an agent's permission
  check, and it only deletes cargo's own output.
- Keep logs under a separate directory (`build/gate-logs/`). They are small, and a verifier or the lead needs
  them after the target is gone.
- sccache or a shared cache is rarely worth it here: on the omni build, compiling was about 1/15 of a nested run,
  and the cache adds a pinned download and a shared mutable resource.

## 4. The quiet timing runner

`gates/quiet.sh pN` runs only phase N's timing set:
- refuses to start when the 1-minute load is at or above a limit (omni used 15 on 12 cores);
- reads the load again at the end and discards the run if it is over the limit;
- prints every TIMING line with both loads;
- fails if the timing test did not run. Grep for the test's own "1 passed" line and its TIMING line.

It is a heavy run, so it takes the same machine-wide lock as the gates: copy the skeleton's lock block, not
just its load check. The lead runs it at a quiet moment. A timing FAIL verdict comes only from a run it kept.

## 5. Gate lines that cannot fail (or cannot pass)

Four of six first-round verifier FAILs on the omni build included a gate or test-infrastructure HIGH. The
recurring shapes:
- a name filter matching zero tests (`--exact` on a prefix), so the step "passes" having run nothing;
- grepping `^test name ... ok` under `--nocapture` with parallel test threads, where output interleaves and a
  passing test reads as missing;
- grepping `^TIMING` when libtest prints it mid-line;
- a summary step that prints PASS when the keys it checks are missing.

Each named test the gate relies on should be checked as having run: a count, or its own marker line, read from a
log written with `--test-threads=1` when output order matters.

## 6. Shared test kit

A dev-only crate (or module) every test uses:
- forces data, cache and runtime directories under the job's scratch, and fails the test if they are unset;
- binds port 0 and reads back the real port;
- stops only the PIDs it started;
- prints `TIMING <name> p50=.. p95=.. load1=..` in one fixed format;
- asserts that the tests a gate names actually ran.

## 7. Fuzz harness

When verifiers keep finding the same class of bug, such as a new patch that panics or cycles, or a frame that
overflows, write property-based generators (`proptest`, `cargo fuzz`) for the untrusted inputs, with a fixed
case budget. Run it behind the gate lock. That moves the bug class from top-tier verifier rounds to CPU.

## 8. Migrating an existing nested gate

1. Add a skip switch to each nested call (`PN_SKIP_PN-1=1`) and make a skipped run end PARTIAL.
2. Point builders and verifiers at the skipped form in their briefs.
3. Build `gates/all.sh`, diff its test list against one nested run, then make the full mode call it.
4. Delete old per-run targets with `cargo clean --target-dir`, oldest first, until free space clears the floor.
