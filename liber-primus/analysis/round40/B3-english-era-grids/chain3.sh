#!/bin/bash
cd "$(dirname "$0")"
while [ ! -f chain2.done ]; do sleep 20; done
python b3extra.py > control_B04red.out 2>&1
python finalize.py KDF R17PAD COSPAD > finalize_rest.out 2>&1
echo CHAIN3 DONE > chain3.done
