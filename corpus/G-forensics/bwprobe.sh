#!/bin/bash
cd /mnt/c/Users/dukot/projects/cicada3301/corpus/G-forensics
P=$(python3 -c "import json;t=json.load(open('TARGETS.json'));print([x['path'] for x in t if x['class']=='onion_artifact'][0])")
echo "probe target: $P"
ls -la "$P"
echo "--- binwalk timing ---"
start=$(date +%s%N)
timeout 30 binwalk --signature "$P" > /tmp/bwout.txt 2>&1
rc=$?
end=$(date +%s%N)
echo "exit=$rc elapsed_ms=$(( (end-start)/1000000 ))"
head -10 /tmp/bwout.txt
