# Round 36 / S1 build + run commands (as executed)
Sandbox: Vercel Sandbox, create_sandboxes_v4 body {"projectId":"skyfling"} (8-vCPU request returned 400), team dukotahs-projects. Default Ubuntu 26.04.1, 2 vCPU, 4 GB; session cap 45 min (extend_session_timeout +2.4e6).
```
sudo apt-get install -y gcc make libgomp1                       # gcc 15.2.0 is not preinstalled
# inputs: tar.gz of round36/P1-panel-r36/engine_inputs_copy (-> in/) + round27/P1-engine/run (-> run/), fetched via temp secret gist, sha256-verified
cd in && python3 check_panel_gate.py                            # must print "PANEL GATE: panel-R36 OK"
gcc -O2 -Wall -Wextra -std=gnu17 -fopenmp -ffp-contract=off -o grind27 grind27.c -lm
./grind27 --self-test --data engine.dat                         # V1 64/64, V2 17.931158509762
export GRIND27_S2_CONTROL_OK=1                                  # S2 (exact) lane guard
./grind27 --data engine.dat --plan sweep_plan.json --threads 6 --run-dir ../run_r36 --seconds N
```
Resume: re-run the last command on the same run_r36 dir (cursors are in STATUS.json). run_r36 = copy of run/STATUS.json with per-worker best_pmax/best_word/n_candidates/flagged reset, HIT-CANDIDATE hits emptied, no top list / histogram (the engine writes them fresh).
