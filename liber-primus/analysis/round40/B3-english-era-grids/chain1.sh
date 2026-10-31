#!/bin/bash
cd "$(dirname "$0")"
B3_DECOYS=128 python b3.py control KDF > control_KDF.out 2>&1
python b3.py run B04 > run_B04.out 2>&1
python b3.py run KDF > run_KDF.out 2>&1
echo CHAIN1 DONE > chain1.done
