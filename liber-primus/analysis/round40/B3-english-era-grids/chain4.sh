#!/bin/bash
cd "$(dirname "$0")"
while [ ! -f chain3.done ]; do sleep 20; done
python b3pads.py regen > regen.out 2>&1
python b3pads.py counts > counts_pads.out 2>&1
B3_DECOYS=256 python b3pads.py control G3 > control_G3.out 2>&1
python b3pads.py run G3 > run_G3.out 2>&1
python finalize.py R17PAD > finalize_g3.out 2>&1
echo CHAIN4 DONE > chain4.done
