#!/usr/bin/env bash
# Fetch the Marsaglia Random Number CDROM (1995) random-data files from the
# jeffThompson/DiehardCDROM GitHub mirror (recreated from the Wayback Machine copy
# of Marsaglia's FSU FTP site). archive.org — the item Round 17 named — is blocked
# at this environment's egress proxy; this mirror serves the same files and raw
# GitHub is reachable. Sequential only: the proxy's download gate fails concurrent
# large transfers (curl error 23).
#
# 60 x bits.NN (10 MB each) + calif/canada/germany.bit = ~630 MB, matching the CD.
set -u
BASE="https://raw.githubusercontent.com/jeffThompson/DiehardCDROM/master/CD-ROM"
DST="$(cd "$(dirname "$0")" && pwd)/data/pads"
mkdir -p "$DST"

names=()
for i in $(seq -w 1 60); do names+=("bits.$i"); done
names+=("calif.bit" "canada.bit" "germany.bit")

ok=0; fail=0
for n in "${names[@]}"; do
  out="$DST/$n"
  if [ -f "$out" ] && [ "$(wc -c < "$out")" = "10000000" ]; then ok=$((ok+1)); continue; fi
  done_one=0
  for try in 1 2 3 4; do
    if curl -sSL --max-time 300 "$BASE/$n" -o "$out" && \
       [ "$(wc -c < "$out")" = "10000000" ]; then
      ok=$((ok+1)); done_one=1; break
    fi
    sleep $((try*2))
  done
  [ "$done_one" = 0 ] && { echo "FAILED $n"; fail=$((fail+1)); }
done
echo "fetched ok=$ok fail=$fail  total $(du -sh "$DST" | cut -f1)"
