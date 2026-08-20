#!/bin/bash
set -u
REPO=/mnt/c/Users/dukot/projects/cicada3301
G=$REPO/corpus/G-forensics
D=$REPO/liber-primus/analysis/armada_osint/artifacts/rune_pages
O=$G/raw/og/keysweep
mkdir -p "$O"
TSV="$G/raw/og/keysweep_$1.tsv"
printf "page\tkey\tseed\tlen\tout_size\tsha256\tprintable_frac\thead32\n" > "$TSV"
KEYS=("3301" "cicada" "CICADA" "DIVINITY" "divinity" "CIRCUMFERENCE" "circumference" "FIRFUMFERENFE" "firfumferenfe" "INSTAR" "instar" "MOBIUS" "ADHERE" "WELCOME" "welcome" "PILGRIM" "pilgrim" "TOTIENT" "SHADOWS" "AN END" "845145127" "7A35090F" "1033" "761" "33011033" "1595277641")
for n in $(echo "$1" | tr ',' ' '); do
  f="$D/$n.jpg"; [ -f "$f" ] || continue
  for k in "${KEYS[@]}"; do
    safe=$(echo "$k" | tr ' ' '_')
    out="$O/${n}_k${safe}.out"
    err=$(outguess -k "$k" -r "$f" "$out" 2>&1)
    sd=$(echo "$err" | grep -o 'seed: [0-9]*' | grep -o '[0-9]*'); ln=$(echo "$err" | grep -o 'len: [0-9]*' | grep -o '[0-9]*')
    if [ -s "$out" ]; then
      sz=$(stat -c%s "$out"); sh=$(sha256sum "$out" | cut -c1-64); hd=$(head -c 16 "$out" | xxd -p | tr -d '\n')
      pf=$(python3 -c "d=open('$out','rb').read()[:8192];print(round(sum(1 for c in d if 32<=c<127 or c in (9,10,13))/len(d),4))")
    else sz=0; sh="-"; hd="-"; pf="-"; rm -f "$out"; fi
    printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" "$n" "$k" "${sd:--}" "${ln:--}" "$sz" "$sh" "$pf" "$hd" >> "$TSV"
  done
done
column -t -s $'\t' "$TSV"
