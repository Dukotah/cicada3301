#!/usr/bin/env bash
# L5-seed32 — sweep the FOUR generators added by this lane (10-13, harness-validated in
# VALIDATION.txt) over the same 2011-2015 unix-second slice Round 8 used for its ten.
# Output format is byte-compatible with analysis/seed_sweep/results_timeseed.txt so
# coverage.py parses both with one regex.
#
# Usage: ./run_newgens.sh [tag]     tag = real (default) | shufa | shufb
set -u
cd "$(dirname "$0")"
TAG=${1:-real}
case "$TAG" in
  real)  CTP=../../seed_sweep/ct.bin ;;
  shufa) CTP=ct_shuf_a.bin ;;
  shufb) CTP=ct_shuf_b.bin ;;
  *) echo "bad tag $TAG" >&2; exit 1 ;;
esac
export LP_CT="$CTP"
export LP_NGRAM=../../seed_sweep/ngram.bin
export OMP_NUM_THREADS=${OMP_NUM_THREADS:-32}
LO=1293840000; HI=1420070400     # 2011-01-01 .. 2015-01-01
OUT=results_newgens.txt; [ "$TAG" != real ] && OUT=results_newgens_${TAG}.txt
for g in 10 11 12 13; do
  grep -q "^gen=$g " "$OUT" 2>/dev/null && { echo "gen=$g already done"; continue; }
  ./sweep32x "$g" "$LO" "$HI" 48 -12.5 >> "$OUT" 2>&1
  tail -1 "$OUT"
done
