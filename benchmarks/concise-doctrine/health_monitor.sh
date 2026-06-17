#!/bin/bash
# Health monitor for the full-matrix run. Polls every 10 min. Stays quiet when
# healthy except a heartbeat every ~2h; alerts on new failures, a progress
# stall (~40 min with no new cell while the matrix is alive), or the matrix
# exiting. Each echoed line becomes one notification — kept selective on purpose.
cd "$(dirname "$0")"
PY=.venv/bin/python
MATRIX_PID="$(cat results/full-run.pid 2>/dev/null)"
GLOB="results/full-run/**/meta.json"
last_cells=-1; last_fails=0; stall=0; hb=0
HEARTBEAT_EVERY=12   # x 600s = ~2h

snap_fails() { $PY -c "import json,glob;print(sum(1 for m in glob.glob('$GLOB',recursive=True) if (json.load(open(m)).get('status') or 'ok')!='ok'))" 2>/dev/null || echo 0; }
snap_cost()  { $PY -c "import json,glob;print('%.2f'%sum((json.load(open(m)).get('cost_usd') or 0) for m in glob.glob('$GLOB',recursive=True)))" 2>/dev/null || echo 0; }

cells=$(find results/full-run -name meta.json 2>/dev/null | wc -l | tr -d ' ')
echo "health monitor armed — ${cells}/120 cells, \$$(snap_cost) build cost; heartbeat ~2h, alerts on failures/stall/exit"

while true; do
  sleep 600
  cells=$(find results/full-run -name meta.json 2>/dev/null | wc -l | tr -d ' ')
  fails=$(snap_fails); cost=$(snap_cost)

  if ! kill -0 "$MATRIX_PID" 2>/dev/null; then
    echo "matrix ended: ${cells}/120 cells, ${fails} non-ok, \$${cost} build — Phase 6 handled by completion waiter"
    exit 0
  fi

  if [ "${fails:-0}" -gt "${last_fails:-0}" ]; then
    echo "ALERT failures rising: ${fails} non-ok cell(s) at ${cells}/120 (\$${cost}) — likely rate-limit/usage-cap; run is resumable"
  fi
  last_fails=$fails

  if [ "$cells" = "$last_cells" ]; then stall=$((stall+1)); else stall=0; fi
  last_cells=$cells
  if [ "$stall" -ge 4 ]; then
    echo "ALERT stall: no new cell in ~$((stall*10))min at ${cells}/120 while matrix alive — possible hang/rate-limit"
    stall=0
  fi

  hb=$((hb+1))
  if [ "$hb" -ge "$HEARTBEAT_EVERY" ]; then
    echo "heartbeat healthy: ${cells}/120 cells, ${fails} non-ok, \$${cost} build cost"
    hb=0
  fi
done
