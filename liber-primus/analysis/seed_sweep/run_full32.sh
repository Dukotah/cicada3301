#!/usr/bin/env bash
# Full 32-bit seed space, generators in descending order of prior plausibility.
# Appends one line per generator so partial coverage is always well-defined.
cd "$(dirname "$0")"
while pgrep -x sweep >/dev/null; do sleep 20; done
for g in 0 3 5 7 9 1 4 6 8 2; do
  ./sweep $g 0 4294967296 48 -12.5 >> results_full32.txt 2>&1
done
echo DONE >> results_full32.txt
