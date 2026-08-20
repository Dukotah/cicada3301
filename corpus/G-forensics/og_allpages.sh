#!/bin/bash
set -u
REPO=/mnt/c/Users/dukot/projects/cicada3301
G=$REPO/corpus/G-forensics
D=$REPO/liber-primus/analysis/armada_osint/artifacts/rune_pages
O=$G/raw/og/pages
mkdir -p "$O"
: > "$G/raw/og/pages_seed_table.tsv"
printf "page\tusable_bits\tseed\tlen\tout_size\tsha256\thead32\n" >> "$G/raw/og/pages_seed_table.tsv"
for n in $(seq "$1" "$2"); do
  f="$D/$n.jpg"
  [ -f "$f" ] || continue
  err=$(outguess -r "$f" "$O/$n.out" 2>&1)
  ub=$(echo "$err" | grep -o 'usable bits: *[0-9]*' | grep -o '[0-9]*')
  sd=$(echo "$err" | grep -o 'seed: [0-9]*' | grep -o '[0-9]*')
  ln=$(echo "$err" | grep -o 'len: [0-9]*' | grep -o '[0-9]*')
  if [ -s "$O/$n.out" ]; then
    sz=$(stat -c%s "$O/$n.out"); sh=$(sha256sum "$O/$n.out" | cut -c1-64); hd=$(head -c 16 "$O/$n.out" | xxd -p | tr -d '\n')
  else sz=0; sh="-"; hd="-"; fi
  printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\n" "$n" "${ub:--}" "${sd:--}" "${ln:--}" "$sz" "$sh" "$hd" >> "$G/raw/og/pages_seed_table.tsv"
done
cat "$G/raw/og/pages_seed_table.tsv"
