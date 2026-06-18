#!/bin/bash
# Cost watchdog for the full-matrix run. Polls summed build cost_usd from
# meta.json every 2 min; if it reaches CAP, kills the matrix + child builds.
# CAP is on *build* cost; the rubric judge adds ~$5-8 untracked, so CAP is set
# below the $250 ceiling to keep the true total under it. The matrix is
# resumable, so a kill is safe (re-launch the same command to continue).
set -u
cd "$(dirname "$0")"
CAP=242
LOG=results/watchdog.log
PIDFILE=results/full-run.pid
MATRIX_PID="$(cat "$PIDFILE" 2>/dev/null)"
PY=.venv/bin/python

ts() { date '+%Y-%m-%d %H:%M:%S'; }
echo "$(ts) watchdog start — guarding matrix PID $MATRIX_PID, CAP=\$$CAP (build cost)" >> "$LOG"

while true; do
  total="$($PY -c "import json,glob; print(round(sum((json.load(open(m)).get('cost_usd') or 0) for m in glob.glob('results/full-run/**/meta.json',recursive=True)),2))" 2>/dev/null)"
  cells="$(find results/full-run -name meta.json 2>/dev/null | wc -l | tr -d ' ')"
  echo "$(ts) cells=${cells}/120 build_cost=\$${total}" >> "$LOG"

  over="$($PY -c "print(1 if float('${total:-0}')>=${CAP} else 0)" 2>/dev/null)"
  if [ "$over" = "1" ]; then
    echo "$(ts) CAP HIT (\$${total} >= \$${CAP}) — stopping matrix ${MATRIX_PID} + child builds" >> "$LOG"
    pkill -P "$MATRIX_PID" 2>/dev/null
    pkill -f "runbuild-" 2>/dev/null
    kill "$MATRIX_PID" 2>/dev/null
    sleep 3
    pkill -9 -f "runbuild-" 2>/dev/null
    echo "$(ts) STOPPED at \$${total} (${cells}/120 cells). Resume with the same run_matrix command." >> "$LOG"
    exit 0
  fi

  if ! ps -p "$MATRIX_PID" >/dev/null 2>&1; then
    echo "$(ts) matrix process ${MATRIX_PID} no longer running (completed or externally stopped) — watchdog exiting at \$${total}, ${cells}/120 cells" >> "$LOG"
    exit 0
  fi

  sleep 120
done
