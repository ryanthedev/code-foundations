#!/bin/bash
# Gate skeleton for a phased multi-session build. Copy to gates/pN.sh, fill in the STEPS section, keep the rest.
# bash 3.2 safe (macOS stock bash). Prints exactly one last line: "PN GATE PASS", "PN GATE PARTIAL" or "PN GATE FAIL".
#
#   GATE_JOB=<job> gates/pN.sh  job-scoped run (builders, verifiers): this phase's steps only, incremental, ends PARTIAL
#   GATE_FULL=1 gates/pN.sh     the lead's pre-commit run: fresh target, all lower phases too, may end PASS
#
# Knobs (environment):
#   GATE_MIN_FREE_GB  refuse to start below this much free disk (default 40; set it to runs-in-flight x measured
#                     target size x 2, not a guess)
#   GATE_LOCK_WAIT    seconds to wait for the machine-wide heavy-run lock before giving up (default 1800)
#   CARGO_BUILD_JOBS  per-run compile parallelism (default 4; about cores / 3 on a shared machine)
#   SESSION_TARGET    persistent incremental cargo target for job-scoped runs (default build/target/$GATE_JOB)
set -u
PHASE="pN"                                   # EDIT: p2, p3, ...
LOWER_FULL_GATE="gates/all.sh"               # EDIT: the flat full gate that runs every lower phase once (or "")

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 2
RUN_ID="$$"
LOG="$ROOT/build/gate-logs/$PHASE/$RUN_ID"   # logs are kept; targets are not
mkdir -p "$LOG"
export CARGO_BUILD_JOBS="${CARGO_BUILD_JOBS:-4}"
MIN_FREE_GB="${GATE_MIN_FREE_GB:-40}"
LOCK="$ROOT/build/lock/heavy"
FULL="${GATE_FULL:-}"
JOB="${GATE_JOB:-}"
FAILED=""
SKIPPED=""
RUN_TARGET=""
HAVE_LOCK=""

load1() { sysctl -n vm.loadavg 2>/dev/null | awk '{print $2}' || uptime | awk -F'load averages?: ' '{print $2}' | awk '{print $1}'; }
free_gb() { df -Pk "$ROOT" | awk 'NR==2 {printf "%d", $4/1048576}'; }

cleanup() {
  # Runs on every exit, including Ctrl-C, kill and HUP. The lock is always released. A per-run target is deleted
  # only after a pass (with cargo, which the permission check allows; rm -rf is often refused). A failed run keeps
  # it for debugging; the parent deletes it at job close. Logs stay.
  if [ -n "$RUN_TARGET" ] && [ -d "$RUN_TARGET" ] && [ -z "${GATE_PASSED:-}" ]; then
    echo "kept failed run's target for debugging: $RUN_TARGET (cargo clean --target-dir it at job close)"
  elif [ -n "$RUN_TARGET" ] && [ -d "$RUN_TARGET" ]; then
    cargo clean --target-dir "$RUN_TARGET" >/dev/null 2>&1
    rmdir "$RUN_TARGET" 2>/dev/null
  fi
  if [ -n "$HAVE_LOCK" ]; then
    rm -f "$LOCK/pid"
    rmdir "$LOCK" 2>/dev/null
  fi
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
trap 'exit 129' HUP   # closing a terminal tab sends HUP

# 1. Disk floor: a full disk breaks the agent tooling as well as the build.
FREE="$(free_gb)"
if [ "$FREE" -lt "$MIN_FREE_GB" ]; then
  echo "GATE REFUSED: ${FREE} GB free, floor ${MIN_FREE_GB} GB. Clean finished jobs' targets (cargo clean --target-dir <dir>)."
  echo "${PHASE} GATE FAIL: disk"
  exit 3
fi

# 2. One heavy run at a time on the machine. mkdir is atomic; a lock whose owner PID is gone is stale.
#    A nested gate called by one that already holds the lock (GATE_LOCK_HELD=1) skips this, or it would deadlock.
mkdir -p "$ROOT/build/lock"
WAITED=0
while [ -z "${GATE_LOCK_HELD:-}" ] && ! mkdir "$LOCK" 2>/dev/null; do
  OWNER="$(cat "$LOCK/pid" 2>/dev/null)"
  if [ -n "$OWNER" ] && ! kill -0 "$OWNER" 2>/dev/null; then
    echo "removing stale lock of dead PID $OWNER"
    rm -f "$LOCK/pid"; rmdir "$LOCK" 2>/dev/null
    continue
  fi
  if [ "$WAITED" -ge "${GATE_LOCK_WAIT:-1800}" ]; then
    echo "${PHASE} GATE FAIL: lock held by PID ${OWNER:-unknown} for ${WAITED}s"; exit 4
  fi
  sleep 10; WAITED=$((WAITED + 10))
done
if [ -z "${GATE_LOCK_HELD:-}" ]; then
  HAVE_LOCK=1
  echo "$RUN_ID" > "$LOCK/pid"
  export GATE_LOCK_HELD=1
fi

# 3. Target: incremental per-session target for job-scoped runs (cargo locks a target dir, so never share one
#    between sessions); a fresh per-run target for the lead's full run, deleted on exit.
if [ -n "$FULL" ]; then
  RUN_TARGET="$ROOT/build/target-run/$PHASE-$RUN_ID"
  export CARGO_TARGET_DIR="$RUN_TARGET"
else
  if [ -z "${SESSION_TARGET:-}" ] && [ -z "$JOB" ]; then
    echo "${PHASE} GATE FAIL: set GATE_JOB (your job name) or SESSION_TARGET, so sessions never share a cargo target"
    exit 2
  fi
  export CARGO_TARGET_DIR="${SESSION_TARGET:-$ROOT/build/target/$JOB}"
fi
mkdir -p "$CARGO_TARGET_DIR"
echo "${PHASE} gate: mode=$([ -n "$FULL" ] && echo full || echo job) load1=$(load1) free=${FREE}GB target=$CARGO_TARGET_DIR logs=$LOG"

step() {  # step <name> <cmd...>; exit code read directly, never through a pipe
  local name="$1"; shift
  local log="$LOG/$(echo "$name" | tr -c 'A-Za-z0-9_-' '_').log"
  echo "== $name"
  "$@" > "$log" 2>&1
  local rc=$?
  if [ $rc -ne 0 ]; then
    echo "   FAILED ($rc), log: $log"; tail -20 "$log" | sed 's/^/   | /'
    FAILED="$FAILED [$name]"
  else
    echo "   ok"
  fi
}

# 4. Lower phases: once, flat, only in the full run. A job-scoped run never claims PASS.
if [ -n "$FULL" ] && [ -n "$LOWER_FULL_GATE" ]; then
  step "lower phases ($LOWER_FULL_GATE)" bash "$ROOT/$LOWER_FULL_GATE"
elif [ -n "$LOWER_FULL_GATE" ]; then
  SKIPPED="lower phases (run GATE_FULL=1 before commit)"
fi

# ---- STEPS: this phase's functional checks. A test with a latency/throughput threshold goes in gates/timing-pN.sh (the quiet runner), not here. ----
step "example: this phase's tests" true      # EDIT: e.g. cargo test -p my-crate
# ---- END STEPS ----

# 5. Timing lines are printed with the load, never judged here. Verdicts come from a quiet run
#    (a separate script that refuses to start above a load limit and discards runs that end above it).
grep -h '^TIMING' "$LOG"/*.log 2>/dev/null | sed "s/\$/ load1=$(load1)/" | sed 's/^/   /'

if [ -n "$FAILED" ]; then echo "${PHASE} GATE FAIL:$FAILED"; exit 1; fi
GATE_PASSED=1
if [ -n "$SKIPPED" ]; then echo "${PHASE} GATE PARTIAL: skipped $SKIPPED"; exit 0; fi
echo "${PHASE} GATE PASS"
exit 0
