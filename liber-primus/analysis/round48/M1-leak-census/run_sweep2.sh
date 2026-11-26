#!/bin/bash
# Arm B2 (word-start extra draws), queued behind Arm B. 3 h cap: generators run in 2^30-seed chunks and no
# new chunk starts after the cap. Appends to sweep2.log.
cd "$(dirname "$0")"
until grep -q "ALL-DONE" sweep.log; do sleep 30; done
t0=$(date +%s)
for g in drand48 bash42 bash42_32 glibc py27; do
  for c in 0 1 2 3; do
    if [ $(( $(date +%s) - t0 )) -gt 10800 ]; then echo "CAP-REACHED before $g chunk $c $(date -u +%FT%TZ)" >> sweep2.log; continue; fi
    lo=$(( c * 1073741824 )); hi=$(( lo + 1073741824 ))
    echo "START $g chunk $c $(date -u +%FT%TZ)" >> sweep2.log
    ./repro2 stream.txt layout.txt $g $lo $hi >> sweep2.log 2>&1
  done
done
echo "ALL-DONE-B2 $(date -u +%FT%TZ)" >> sweep2.log
