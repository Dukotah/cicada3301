#!/bin/bash
cd ~/liber-primus/analysis/round38/S2-php-sandbox
date +%s > t_start.txt
(setsid nohup ./up.sh > up.out 2>&1 < /dev/null &)
python3 sweep_s2.py smoke > smoke.log 2>&1
python3 sweep_s2.py fpr > fpr.log 2>&1
python3 sweep_s2.py control 2 > control.log 2>&1 || { echo CONTROL_FAIL > driver.status; exit 1; }
date +%s > t_control_done.txt
python3 sweep_s2.py window W1 3301 199 317 1000 2 > w1.log 2>&1
date +%s > t_w1_done.txt
python3 sweep_s2.py window W3 3301 318 100000 1250 2 > w3.log 2>&1
date +%s > t_w3_done.txt
python3 sweep_s2.py finalize > fin.log 2>&1
echo DONE > driver.status
