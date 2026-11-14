---
name: lean-build
description: "Resource and verification rules for leading a long phased build run by many agent sessions (builders, verifiers, a lead) on one shared machine: phase gate scripts (job-scoped incremental runs, one flat full gate before commit, disk floor, lock, cleanup on a passing exit), scratch and disk hygiene, load caps, which jobs get a top-tier verifier and which model, fix-round limits, iOS Simulator versus real device, and a speed review of an existing plan. Use when leading or setting up a multi-session build team, writing a gate script that several sessions share, reviewing a written plan for speed or cost, or when gates are slow, the disk fills, load is high, verifier rounds repeat, or someone asks whether tests need the real phone. Not for: writing a new implementation plan (use plan), executing a plan in one session with subagents (use build), or diagnosing one flaky or failing test (use cc-debugging)."
user-invocable: false
---

# lean-build

A phased multi-agent build is bounded by the machine, not the models: disk, CPU load and repeated gate runs.
These rules come from a seven-phase Rust build run by parallel Claude Code sessions on one 12-core Mac (cited
as "the omni build"). Numbers marked "omni" are what that machine used; formulas marked "heuristic" are a
starting point to measure against, not recorded derivations.

## When not to apply

- One session building with subagents: code-foundations `build` already sequences that, and nothing competes
  for the machine.
- Gates that finish in seconds, or CI on fresh machines per run: disk, lock and load rules buy nothing there.
- Writing the plan itself: use `plan`. This skill reviews a plan for speed once it exists.

## Before building: speed-review the plan

Run the checklist in Read(${CLAUDE_SKILL_DIR}/references/plan-speed-review.md) on the plan, and write its table
into the plan or next to it, before the first builder starts. It costs one reviewer session, and every finding
it makes is multiplied by the number of gate runs and fix rounds that follow.

## Gates

| Rule | Why |
|---|---|
| Builders and verifiers run a **job-scoped** gate: this phase's steps only, incremental, last line `PARTIAL`. Only the lead's pre-commit run is full and may print `PASS` | omni: the nested lower-gate rerun was 87% of one phase-4 gate run and 58% of one phase-2 run (log timestamps) |
| The full run is **one flat gate** (`gates/all.sh`): one target, one `cargo test --workspace`, then each phase's non-cargo steps. Never pN calling p(N-1) calling ... | Nesting builds one fresh target per level and runs the workspace tests at every level; it grows by one level per phase |
| A clean build runs once, in the lead's full run. Every other run is incremental | Clean building is about 1/15 of a nested run: it costs disk, not time. A stale incremental build is caught by the lead's clean run |
| Each gate refuses to start under a **free-disk floor**, takes a **machine-wide lock**, and deletes its per-run target when it passes. A failed run keeps its target for debugging and prints the path; the parent deletes it at job close | omni: 86 gate runs (targets up to ~7 GB each) were never deleted; `build/tmp` reached 308 GB, the disk filled, the agent tooling broke and two gates failed |
| Functional tests carry **no timing thresholds**. Timing lines are printed with the load; verdicts come only from a quiet run that refuses to start above a load limit and discards runs that end above it | At load 30-60, timing tests flaked, and builders lost rounds telling load from bugs. One "load" failure was a real deadlock; one was a cold compile cache past a 10 s test timeout |
| **Freeze files under check.** Nobody edits a job's files while its verifier runs, and gates scope to the job's packages (`-p`) | One verifier's files were rewritten mid-check, voiding its verdict. Two more failed on another job's untracked test. That is 3 lost verifier runs in 10 jobs |
| Read the gate's exit code and output, then commit in a **separate command**. Never `gate && git commit`, never `gate \| tee` | A pipe reports the last command's exit code, so a failing gate looks like a pass |

Template: `${CLAUDE_SKILL_DIR}/scripts/gate-skeleton.sh`. Copy the file (`cp`), then fill in its STEPS block. Don't
retype it: in testing, retyped gates dropped the lock and the cleanup, or swapped in `flock`, which stock macOS
lacks. Give each session its own `GATE_JOB` so job-scoped runs never share a target. It is
bash 3.2 safe and does the disk floor, stale-lock-aware `mkdir` lock, job-versus-full mode, PARTIAL, and trap
cleanup. STEPS holds functional checks only. A test with a latency or throughput threshold goes in the quiet
runner (`gates/timing-pN.sh`), even when the task lists it with the phase's other tests. Detail, the flat full
gate, the quiet runner, fuzzing and the shared test kit are in Read(${CLAUDE_SKILL_DIR}/references/gates.md).

## Scratch and disk

- **Where:** one persistent incremental target per session (`build/target/<job>`). Cargo locks a target, so
  sessions never share one. A full gate's target is per run, deleted when the run passes, kept on failure until the job closes. Logs live apart from targets and
  are kept.
- **Who deletes, and when:** the parent deletes a job's scratch and target when it commits the job or closes the
  session. Scratch is never left for "later". When disk is short, delete in this order: committed jobs' scratch,
  then failed per-run gate targets, then idle sessions' targets.
- **How:** `cargo clean --target-dir <dir>`. Plain `rm -rf` is often refused by the permission check, and a
  session blocked on that question stalls silently.
- **Disk floor:** omni used 40 GB. Heuristic: (runs in flight) × (measured size of one target) × 2, measured
  with `du -sh` after the first full run.
- **Check on a timer:** the lead arms a recurring check (`df -h`, `du -sh build/*`) and cleans before starting
  more work whenever free space nears the floor.
- **Tests write only under the repo.** Force data and runtime directories into scratch (an env var each test rig
  sets). Two first-round verifiers found 5.1 GB of test byte logs in the user's real `~/Library`.

## Load

- Cap heavy work by **measured load**, not session count. Allow one heavy run (gate, benchmark, fuzz) at a time
  through the gate lock. omni capped each run at `CARGO_BUILD_JOBS=4` on 12 cores.
- **Ceiling:** omni started nothing above a 1-minute load of 60, on a Mac that sat at 30-48 from other work.
  Heuristic: measure the baseline with your own sessions idle, and start a heavy run or a new builder only
  under baseline + cores. A ceiling read as "load 47 is fine" on an idle machine is too high.
- An idle session costs memory, not CPU. Close finished sessions instead of keeping them warm, except a verifier
  you will reuse for its own re-check (below).

## Verification and models

| Job | Builder | First verifier |
|---|---|---|
| Untrusted input, sandboxing, auth, concurrency, timing | mid tier (Sonnet) | top tier (Opus), plus an automated security review of the builder's diff first |
| Ordinary code (UI, layout, tooling, rigs) | mid tier | mid tier |
| Wording, renames, fixtures, file moves, status checks | small tier (Haiku) | lead reads it |
| Plan and design reviews; the lead | top tier | — |

- **Fix rounds:** the verifier that found the problem re-checks the fix, ideally by rerunning probes it left as
  tests. Bring in a new verifier only when the design changed. That is cheaper than a fresh session reading
  everything again.
- **At most two verifier rounds per job.** Then the lead decides: accept and record, narrow the remaining item
  into a targeted fix the lead checks, or split it into a follow-up job. omni jobs needed 1-2 fix rounds each;
  the one job that ran to four verifiers had matching numbers every time, and its later FAILs were wording.
- **Verifier isolation:** give the verifier the goal, done-when, paths, and the builder's not-verified list.
  Leave out the builder's claims of success; a checker told "this works" tends to agree.
- Top-tier security verifiers found real HIGHs on every security-sensitive job. Keep them there. Move the
  bug classes they keep finding (panics on untrusted input, unbounded growth) into a fuzz harness and the
  builder checklist. Policy detail: Read(${CLAUDE_SKILL_DIR}/references/verification.md).

## Simulator or device

Use the Simulator or emulator for everything functional: builds, UI tests, flows, protocol attach. Use a real
device only for numbers the Simulator cannot give: frame rate and hitches, memory footprint, GPU traces, cold
launch, and real network legs. The Simulator runs on the host's GPU and memory, so its numbers say nothing
about the device. Whether a GPU render path works in the Simulator at all is not a given: confirm it with a
small smoke job early, before planning on it. Batch the
device work into **one rehearsed script** (`gates/pN-device.sh`), dry-run it on the Simulator first, and keep
the device session to plug in, one command, unplug. If the device is someone's personal phone, tell them before
each session.

## While running (the lead)

- Before starting anything: `df -h`, `uptime`, roster. Clean, then start.
- Read a gate's last line: `PARTIAL` never counts as `PASS` for a commit.
- An idle session's input box may show Claude Code's **suggested** next prompt in grey. It is not typed input;
  don't act on it or record it as the user's words.
- No fail verdict on a timing line until a quiet run has measured it.
