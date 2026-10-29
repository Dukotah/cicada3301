set -e
for d in panel_max base; do for L in 120 400; do python run_envelope.py null $d $L 0 4; done; done
for d in panel_max base; do for L in 120 400; do python run_envelope.py grid $d $L ALL 0 4; done; done
echo CHAIN1DONE
