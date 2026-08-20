#!/bin/bash
# usage: runbatch.sh <start_line> <count>
E=/c/Users/dukot/projects/cicada3301/corpus/E-tooling
cd "$E" || exit 1
START=$1
CNT=$2
END=$((START + CNT - 1))
sed -n "${START},${END}p" ${TF:-targets.txt} | while IFS='|' read -r d u dep; do
  [ -z "$d" ] && continue
  timeout 150 ./clone.sh "$d" "$u" "$dep"
done
echo "BATCH ${START}+${CNT} done $(date -u +%FT%TZ)" >> "$E/clone.log"
