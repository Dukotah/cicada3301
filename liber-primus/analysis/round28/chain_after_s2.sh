#!/usr/bin/env bash
# Round 28 post-S2 auto-chainer.
#
# Waits for the R27 S2 sweep (PID in round27/sweep.pid) to exit, then:
#   - if S2 did NOT finish its lane (lanes_completed lacks "S2"): the sweep died
#     mid-lane -> resume grind27 per round27/MONITORING.md with GRIND27_S2_CONTROL_OK=1,
#     update sweep.pid, and keep polling.
#   - if S2 IS complete: write round28/S2-COMPLETE.marker (FIRST action, the
#     coordinator's watcher keys off it), then launch the grind28 25-cell queue
#     (queued_cells.json) sequentially, setsid nice -n 10, run dir round28/run/,
#     with per-lane progress + HIT-CANDIDATE flagging appended to round28/chain.log.
#
# Launched detached (setsid nohup); survives session death. PID -> round28/chainer.pid.
set -u

LP=/mnt/c/Users/dukot/projects/cicada3301/liber-primus
R27=$LP/analysis/round27
R28=$LP/analysis/round28
P1=$R27/P1-engine
L4=$R28/L4
SWEEP_PID_FILE=$R27/sweep.pid
STATUS=$P1/run/STATUS.json
CHAINLOG=$R28/chain.log
MARKER=$R28/S2-COMPLETE.marker

log() { printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" >> "$CHAINLOG"; }

s2_complete() {
  # returns 0 if STATUS.json lanes_completed contains "S2"
  python3 - "$STATUS" <<'PY'
import json,sys
try:
    d=json.load(open(sys.argv[1]))
except Exception:
    sys.exit(2)
sys.exit(0 if "S2" in d.get("lanes_completed",[]) else 1)
PY
}

resume_s2() {
  # guard: never double-launch (two grind27s on one run dir = corruption)
  if pgrep -x grind27 >/dev/null 2>&1; then
    existing=$(pgrep -x grind27 | head -1)
    echo "$existing" > "$SWEEP_PID_FILE"
    log "resume skipped: grind27 already running (PID $existing) -> sweep.pid updated"
    return 0
  fi
  log "S2 INCOMPLETE at sweep exit -> resuming grind27 (GRIND27_S2_CONTROL_OK=1) per MONITORING.md"
  cd "$P1" || { log "FATAL: cannot cd $P1"; exit 1; }
  GRIND27_S2_CONTROL_OK=1 setsid nice -n 10 nohup ./grind27 --plan ../sweep_plan.json \
      --run-dir run >> "$R27/sweep.log" 2>&1 &
  sleep 3
  newpid=$(pgrep -x grind27 | head -1)
  if [ -n "$newpid" ]; then
    echo "$newpid" > "$SWEEP_PID_FILE"
    log "grind27 resumed, new PID $newpid -> sweep.pid updated"
  else
    log "WARNING: resume launched but grind27 not found by pgrep; will re-poll"
  fi
}

launch_queue() {
  PLAN="$R28/sweep_plan_r28.json"   # merged + validated plan (R28 coordinator, 2026-09-15)
  if [ ! -s "$PLAN" ]; then
    log "FATAL: merged plan $PLAN missing/empty; falling back to $L4/queued_cells.json"
    PLAN="$L4/queued_cells.json"
  fi
  n=$(python3 -c "import json,sys;print(len(json.load(open(sys.argv[1]))))" "$PLAN" 2>/dev/null || echo '?')
  log "S2 COMPLETE -> marker written; launching grind28 queue ($n cells, plan $PLAN)"
  mkdir -p "$R28/run"
  cd "$L4" || { log "FATAL: cannot cd $L4"; exit 1; }
  export PANEL_PATH="$L4/panel_lm.f32"
  setsid nice -n 10 nohup ./grind28 --plan "$PLAN" --run-dir "$R28/run" \
      >> "$R28/run/grind28.log" 2>&1 &
  sleep 3
  qpid=$(pgrep -f 'grind28 --plan' | head -1)
  echo "${qpid:-unknown}" > "$R28/grind28.pid"
  log "grind28 queue launched, PID ${qpid:-unknown}, run-dir $R28/run"
}

monitor_queue() {
  local last_lane="" hit_flagged=""
  while :; do
    qpid=$(cat "$R28/grind28.pid" 2>/dev/null)
    alive=no
    [ -n "${qpid:-}" ] && kill -0 "$qpid" 2>/dev/null && alive=yes
    if [ -f "$R28/run/STATUS.json" ]; then
      read -r cur frac done < <(python3 - "$R28/run/STATUS.json" <<'PY'
import json,sys
try:
    d=json.load(open(sys.argv[1]))
    ag=d.get("aggregate",{})
    print(d.get("current_lane","?"), round(ag.get("lane_coverage_fraction",0),4),
          ",".join(d.get("lanes_completed",[])) or "-")
except Exception:
    print("? 0 -")
PY
)
      if [ "$cur" != "$last_lane" ]; then
        log "grind28 lane -> $cur (completed: $done)"
        last_lane="$cur"
      fi
    fi
    # HIT-CANDIDATE flagging (engine writes run/HIT-CANDIDATE.json; flag it, do not certify)
    if [ -f "$R28/run/HIT-CANDIDATE.json" ] && [ "$hit_flagged" != "yes" ]; then
      cp "$R28/run/HIT-CANDIDATE.json" "$R28/run/HIT-CANDIDATE.flagged.$(date -u +%s).json"
      log "*** HIT-CANDIDATE.json present -> FLAGGED-FOR-ORACLE (not auto-certified) ***"
      hit_flagged=yes
    fi
    if [ "$alive" = no ]; then
      log "grind28 queue process exited; chainer done"
      return 0
    fi
    sleep 300
  done
}

log "chainer started (PID $$); watching sweep.pid $(cat "$SWEEP_PID_FILE" 2>/dev/null)"

# ---- Phase 1: wait for S2 to exit; resume if it died mid-lane ----
while :; do
  pid=$(cat "$SWEEP_PID_FILE" 2>/dev/null)
  if [ -n "${pid:-}" ] && kill -0 "$pid" 2>/dev/null; then
    # still running; concise heartbeat with S2 coverage
    frac=$(python3 - "$STATUS" <<'PY' 2>/dev/null
import json,sys
try:
    d=json.load(open(sys.argv[1]))
    print(round(d.get("aggregate",{}).get("lane_coverage_fraction",0),4), d.get("current_lane","?"))
except Exception:
    print("? ?")
PY
)
    log "poll: sweep PID $pid alive; S2 lane=$frac"
    sleep 60
    continue
  fi
  # sweep PID not alive
  log "sweep PID ${pid:-<none>} not alive; inspecting STATUS.json"
  if s2_complete; then
    break
  else
    rc=$?
    if [ "$rc" = 2 ]; then
      log "STATUS.json unreadable; waiting 60s before retry"
      sleep 60; continue
    fi
    resume_s2
    sleep 60
    continue
  fi
done

# ---- Phase 2: S2 complete. Marker FIRST, then launch + monitor the queue ----
date -u +%Y-%m-%dT%H:%M:%SZ > "$MARKER"
echo "S2 lanes_completed confirmed; round28 grind28 queue authorized." >> "$MARKER"
launch_queue
monitor_queue
log "chainer exiting cleanly"
