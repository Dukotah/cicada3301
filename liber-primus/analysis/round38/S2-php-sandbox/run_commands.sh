#!/bin/bash
# R38 S2 exact rerun script. NOT executed to completion: sandbox creation returned 402 (Hobby usage limit) until 2026-11-01T00:00Z.
# 1. Build the input tarball locally (paths relative to liber-primus/): all *.py under
#    analysis/{round19/G1,round19/I1,round19/I3,round20/P3,round20/HITFN,round11,campaign18_skip,round32/B1-bash-random,
#    round33/I1-register-aware-beam,round32/I1-skipbytwo-decoder,round32/B2-php-mtrand,round28/L4,round35/I1-skip-tolerant-screen,
#    round37/I2-pfv4-12reg,round32/I2-multiregister-readjudication,round34/I2-novowel-prefilter}, src/, benchmark/,
#    plus analysis/run_stats.py, data/english_quadgrams.txt, data/krisyotam_runes.txt, data/panels/panel-r36.npz,
#    data/panels/testhalves-r36.npz, analysis/round32/I2-multiregister-readjudication/models/panel.npz,
#    analysis/round36/B1-orbit-12reg/null12.json, analysis/round35/I1-skip-tolerant-screen/frozen_op.json,
#    analysis/round37/I2-pfv4-12reg/frozen_op12.json, and this lane dir's sweep_s2.py up.sh drv_a.sh drv_b.sh
#    (2,928,115 bytes gz in the first attempt; sha256 acc9969810634c3ba6969f73b4e730bf47485183b2a21c68c3430690d6ad7ffd before pf_v3.py + drivers were added).
# 2. Create sandbox: create_sandboxes_v4 {"projectId":"skyfling","persistent":false,"timeout":2700000,"resources":{"vcpus":2}}  (hard 45-min cap; extend_session_timeout is refused)
# 3. Upload the tarball with write_session_files (chunk the base64 if the tool limit bites; no gist), then on the sandbox:
#      python3 -m pip install --user numpy     # worked: Python 3.14.4 + numpy 2.5.4
#      cd ~/liber-primus/analysis/round38/S2-php-sandbox && bash drv_a.sh     # smoke, fpr, control, W1 (3301 blocks 199-317), W3 (3301 blocks 318+), finalize
#    second sandbox in parallel:  bash drv_b.sh                                 # smoke, fpr, control, W2 (default_rng(3302) blocks 0+), finalize
# 4. Download: up.sh posts a checkpoint tarball to litterbox every ~400 s and at the end; read ~/up.log via a short run_session_command.
#    NEVER put more than one sleeping run_session_command in flight; a hung call (2573 s) outlived both sessions in the first attempt.
# 5. Local: python -c "import sys;sys.path.insert(0,'../../round32/I2-multiregister-readjudication');import adjudicate as A;A.validate_store('sweep_rows.jsonl')"
#    and handoff/validate_ledger.check_r3_store on each downloaded store.
