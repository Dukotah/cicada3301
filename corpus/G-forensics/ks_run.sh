#!/bin/bash
G=/mnt/c/Users/dukot/projects/cicada3301/corpus/G-forensics
bash "$G/og_keysweep.sh" "$1" > /tmp/ks_$2.txt 2>&1
T="$G/raw/og/keysweep_$1.tsv"
echo "rows: $(wc -l < "$T")"
echo "--- rows with printable_frac > 0.50 (any textual structure) ---"
awk -F'\t' 'NR>1 && $7+0>0.50' "$T"
echo "--- max printable_frac observed ---"
awk -F'\t' 'NR>1 && $7!="-" {if($7+0>m){m=$7;r=$0}} END{print "max="m; print r}' "$T"
echo "--- keys yielding NO extraction (validity check failed) ---"
awk -F'\t' 'NR>1 && $5==0{print $1"  "$2}' "$T"
echo "--- distinct output sha256 count vs rows ---"
awk -F'\t' 'NR>1 && $6!="-"{print $6}' "$T" | sort -u | wc -l
