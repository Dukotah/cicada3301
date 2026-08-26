#!/bin/bash
# L8 / I-03 -- grep the mailing-list archives actually retrieved, with the term set
# fixed in PREREG.md. Case-insensitive, whole corpus, per-term counts.
set -u
BASE="$(cd "$(dirname "$0")" && pwd)"
A="$BASE/evidence/archives"
OUT="$A/grep-results.txt"
: > "$OUT"

TERMS=(
  "3301"
  "845145127"
  "cicada"
  "instar"
  "highly intelligent individuals"
  "liber primus"
  "futhorc"
  "futhark"
  "anglo-saxon rune"
  "runic cipher"
  "mabinogion"
  "outguess"
  "a2e7j6ic78h0j"
  "onion.*puzzle"
  "gematria"
  "totient.*cipher"
  "mruzuki"
  "cicadeur"
)

echo "corpus: $(find "$A" -name '*.txt.gz' | wc -l) monthly archives" | tee -a "$OUT"
find "$A" -name '*.txt.gz' | sort | sed 's|.*/||' | tr '\n' ' ' | tee -a "$OUT"
echo | tee -a "$OUT"
echo "searched_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)" | tee -a "$OUT"
echo "---- per-term hit counts (case-insensitive) ----" | tee -a "$OUT"
for t in "${TERMS[@]}"; do
  n=$(zgrep -aiEc "$t" $(find "$A" -name '*.txt.gz') 2>/dev/null | awk -F: '{s+=$NF} END{print s+0}')
  printf '%-32s %s\n' "$t" "$n" | tee -a "$OUT"
  if [ "${n:-0}" -gt 0 ]; then
    zgrep -aiE -m 8 -H "$t" $(find "$A" -name '*.txt.gz') 2>/dev/null | head -8 \
      | sed 's/^/      /' | tee -a "$OUT"
  fi
done
echo "---- done ----" | tee -a "$OUT"
