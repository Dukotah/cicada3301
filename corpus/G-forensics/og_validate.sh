#!/bin/bash
set -u
REPO=/mnt/c/Users/dukot/projects/cicada3301
A=$REPO/liber-primus/analysis/armada_osint/artifacts
G=$REPO/corpus/G-forensics
mkdir -p "$G/raw/og"
echo "=== outguess version ==="
outguess 2>&1 | head -1
echo
echo "=== INSTRUMENT VALIDATION: reproduce the known 4gq25.jpg extraction ==="
outguess -r "$A/4gq25.jpg" "$G/raw/og/val_4gq25.out" 2>&1 | sed 's/^/  /'
echo "  ours:"; sha256sum "$G/raw/og/val_4gq25.out" 2>/dev/null
echo "  held:"; sha256sum "$A/4gq25.jpg.outguess" 2>/dev/null
if cmp -s "$G/raw/og/val_4gq25.out" "$A/4gq25.jpg.outguess"; then echo "  RESULT: BYTE-IDENTICAL to the held prior-work output"; else echo "  RESULT: DIFFERS"; fi
echo "  first 200 bytes of ours:"
head -c 200 "$G/raw/og/val_4gq25.out" | sed 's/^/    /'
echo
echo "=== VALIDATION 2: a known LP1/2013 carrier with real PGP stego ==="
for f in "$REPO/liber-primus/analysis/armada_osint/onions_ibotpeaches/onions__imgur.com__KXLOP.jpeg" \
         "$REPO/liber-primus/analysis/armada_osint/onions_ibotpeaches/onions__845145127.com__post__cicada.jpg"; do
  b=$(basename "$f")
  echo "-- $b"
  outguess -r "$f" "$G/raw/og/val_$b.out" 2>&1 | sed 's/^/   /'
  if [ -s "$G/raw/og/val_$b.out" ]; then
    echo "   size: $(stat -c%s "$G/raw/og/val_$b.out")"
    head -c 160 "$G/raw/og/val_$b.out" | tr -c '[:print:]\n' '.' | sed 's/^/     /'
  else echo "   EMPTY"; fi
done
