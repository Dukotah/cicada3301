#!/usr/bin/env bash
# L5-seed32 — resumable, checkpointed full-32-bit seed sweep driver.
#
# Differences from Round 8's run_full32.sh (which appended ONE line per generator and
# therefore lost everything if killed mid-generator — which is exactly what happened):
#   * sweeps in fixed 2^26-seed chunks, appending one TSV row per completed chunk
#   * resumes automatically from the highest completed chunk for that (gen, ct) pair
#   * per-chunk bests double as the best-of-N null-growth curve (see nullcurve.py)
#   * ct can be pointed at a shuffled null control without touching the real data
#
# Usage:
#   ./run32.sh <gen 0-9> <real|shufa|shufb> [n_chunks]     # n_chunks default: all remaining
#   ./run32.sh 0 real 16      # advance gen 0 on real ciphertext by 16 chunks (~16 min)
#   ./run32.sh 0 real         # run gen 0 to completion of the 32-bit space
#
# State:  chunks_<tag>.tsv   (gen  lo  hi  best  bestseed  hits  seconds)
# Resume: just re-run the same command. Nothing is recomputed.
set -u
cd "$(dirname "$0")"

GEN=${1:?gen}
TAG=${2:?tag: real|shufa|shufb}
WANT=${3:-0}

case "$TAG" in
  real)  CTP=../../seed_sweep/ct.bin ;;
  shufa) CTP=ct_shuf_a.bin ;;
  shufb) CTP=ct_shuf_b.bin ;;
  *) echo "bad tag $TAG" >&2; exit 1 ;;
esac

export LP_CT="$CTP"
export LP_NGRAM=../../seed_sweep/ngram.bin
export OMP_NUM_THREADS=${OMP_NUM_THREADS:-32}   # measured optimum on this box (Ultra 7 258V / WSL2)

CHUNK=67108864          # 2^26
END=4294967296          # 2^32
WINDOW=48               # pre-registered
THRESH=-12.5            # pre-registered (Round 8)

LOG=chunks_${TAG}.tsv
if [ ! -f "$LOG" ]; then
  printf 'gen\tlo\thi\tbest\tbestseed\thits\tsecs\n' > "$LOG"
fi

# resume point: highest hi already recorded for this gen
LO=$(awk -v g="$GEN" '$1==g && $3+0>m {m=$3+0} END{print m+0}' "$LOG")

n=0
while [ "$LO" -lt "$END" ]; do
  if [ "$WANT" -gt 0 ] && [ "$n" -ge "$WANT" ]; then break; fi
  HI=$((LO + CHUNK)); [ "$HI" -gt "$END" ] && HI=$END
  OUT=$(./sweep32 "$GEN" "$LO" "$HI" "$WINDOW" "$THRESH")
  echo "$OUT" | grep '^HIT' >> hits_${TAG}.txt 2>/dev/null
  # parse: gen=G NAME seeds=lo..hi best=B @S hits>-12.5=H  T s
  BEST=$(echo "$OUT" | grep -o 'best=[-0-9.]*'   | tail -1 | cut -d= -f2)
  BSD=$(echo  "$OUT" | grep -o '@[0-9]*'          | tail -1 | tr -d '@')
  HITS=$(echo "$OUT" | grep -o 'hits>[-0-9.]*=[0-9]*' | tail -1 | cut -d= -f2)
  SECS=$(echo "$OUT" | grep -o '[0-9.]*s$'        | tail -1 | tr -d 's')
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$GEN" "$LO" "$HI" "$BEST" "$BSD" "$HITS" "$SECS" >> "$LOG"
  echo "[$TAG gen=$GEN] $LO..$HI best=$BEST hits=$HITS ${SECS}s"
  LO=$HI; n=$((n+1))
done

DONE_AT=$(awk -v g="$GEN" '$1==g && $3+0>m {m=$3+0} END{print m+0}' "$LOG")
echo "coverage: gen=$GEN tag=$TAG seeds 0..$DONE_AT of $END ($(awk -v a="$DONE_AT" -v b="$END" 'BEGIN{printf "%.2f", 100*a/b}')%)"
