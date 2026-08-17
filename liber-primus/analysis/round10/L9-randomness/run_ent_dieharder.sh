#!/bin/bash
# L9 — off-the-shelf batteries: ent (valid at this n) and dieharder (NOT valid,
# see the caveat printed below). Run under WSL Ubuntu.
D="$(cd "$(dirname "$0")" && pwd)"
cd "$D/bits" || exit 1

echo "########## ent — all mappings, all streams ##########"
for f in *.bin; do
  echo "### $f"
  ent "$f" | head -6
  echo
done

echo
echo "########## dieharder — CAVEAT ##########"
echo "dieharder needs ~1e8-1e11 bits. We have 6.3e4. It REWINDS the file and"
echo "re-uses the same bits, which INVALIDATES the p-values (they become"
echo "measures of self-consistency, not randomness). Reported for completeness"
echo "only, and ONLY as REAL-vs-control comparisons on identical rewind counts."
for s in REAL SHUF URAND ARFILT; do
  f="${s}_M1.bin"
  echo "### dieharder -d 0 (birthdays)  $f"
  dieharder -d 0 -g 201 -f "$f" 2>&1 | tail -4
  echo "### dieharder -d 1 (operm5)     $f"
  dieharder -d 1 -g 201 -f "$f" 2>&1 | tail -4
done
