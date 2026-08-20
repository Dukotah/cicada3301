#!/bin/bash
cd /mnt/c/Users/dukot/projects/cicada3301/corpus/G-forensics
python3 ext_tools.py 1500 onion_artifact binwalk
python3 ext_tools.py 300 onion_html binwalk
