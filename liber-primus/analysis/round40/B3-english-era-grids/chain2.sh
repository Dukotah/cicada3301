#!/bin/bash
cd "$(dirname "$0")"
while [ ! -f chain1.done ]; do sleep 20; done
python b3pads.py regen > regen.out 2>&1
python b3pads.py counts > counts_pads.out 2>&1
B3_DECOYS=256 python b3pads.py control G4 > control_G4.out 2>&1
B3_DECOYS=256 python b3pads.py control G3 > control_G3.out 2>&1
python b3pads.py run G4 > run_G4.out 2>&1
python b3pads.py run G3 > run_G3.out 2>&1
echo CHAIN2 DONE > chain2.done
