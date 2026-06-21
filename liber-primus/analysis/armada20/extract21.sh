#!/bin/bash
# OutGuess + steghide extraction sweep, id=21
OG=/tmp/outguess/src/outguess
OUT=/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/armada20/og_out
mkdir -p "$OUT"
KEYS=("" "DIVINITY" "divinity" "SACRED" "sacred" "PRIMES" "primes" "CIRCUMFERENCE" "circumference" "WELCOME" "welcome" "3301" "INSTAR" "instar")

# Image sets
declare -a IMGS
for f in /mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/relikd/*.jpg; do IMGS+=("$f"); done
while IFS= read -r f; do IMGS+=("$f"); done < <(find /mnt/c/Users/dukot/projects/cicada3301/puzzles -iname '*.jpg' | sort)

echo "Total images: ${#IMGS[@]}"
HITS=0
for img in "${IMGS[@]}"; do
  base=$(echo "$img" | md5sum | cut -c1-8)
  tag=$(basename "$img" .jpg)
  for key in "${KEYS[@]}"; do
    of="$OUT/${tag}_${base}_k${key:-NONE}.bin"
    if [ -z "$key" ]; then
      "$OG" -r "$img" "$of" >/dev/null 2>&1
    else
      "$OG" -k "$key" -r "$img" "$of" >/dev/null 2>&1
    fi
    if [ -s "$of" ]; then
      sz=$(stat -c%s "$of")
      # printable ratio
      pr=$(python3 -c "
import sys
d=open('$of','rb').read()
if not d: print(0); sys.exit()
p=sum(1 for b in d if 32<=b<127 or b in (9,10,13))
print(round(100*p/len(d)))
")
      if [ "$pr" -ge 75 ] && [ "$sz" -ge 8 ]; then
        echo "CANDIDATE og $tag key=${key:-NONE} size=$sz printable=$pr%"
        HITS=$((HITS+1))
      fi
    else
      rm -f "$of"
    fi
  done
done
echo "OutGuess candidates: $HITS"
