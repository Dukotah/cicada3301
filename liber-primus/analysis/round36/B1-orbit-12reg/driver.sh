#!/bin/bash
cd "$(dirname "$0")"
python readjud.py null > null.out 2>&1 && python readjud.py control > control.out 2>&1 && python readjud.py pfpower > pfpower.out 2>&1 && python readjud.py run 3300 > run.out 2>&1 && python readjud.py final > final.out 2>&1
echo DONE > driver.done
