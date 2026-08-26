#!/bin/bash
# L8 / I-03 -- pre-disclosure search of the actual mailing-list archives.
#
# Method: download the pipermail monthly mbox archives directly and grep them, rather than
# trusting a search engine's index of them. A grep over the real corpus is reproducible and
# its negative is a measurable bound; a search-engine miss is not.
#
# Window: 2011-01-01 .. 2012-01 inclusive (first 3301 image = 2012-01-04), extended through
# 2013-12 for context.
set -u
BASE="$(cd "$(dirname "$0")" && pwd)"
OUT="$BASE/evidence/archives"
mkdir -p "$OUT/metzdowd" "$OUT/cpunks"
LOG="$BASE/evidence/archives/fetch-log.txt"
: > "$LOG"

months() {
  for y in 2011 2012 2013; do
    for m in January February March April May June July August September October November December; do
      echo "$y-$m"
    done
  done
}

echo "=== metzdowd cryptography list ===" | tee -a "$LOG"
for ym in $(months); do
  f="$OUT/metzdowd/$ym.txt.gz"
  [ -s "$f" ] && continue
  code=$(curl -s -m 45 -o "$f" -w '%{http_code}' \
    "https://www.metzdowd.com/pipermail/cryptography/$ym.txt.gz")
  sz=$(stat -c%s "$f" 2>/dev/null || echo 0)
  echo "metzdowd $ym http=$code bytes=$sz" >> "$LOG"
  [ "$code" != "200" ] && rm -f "$f"
done

echo "=== cypherpunks (cpunks.org) ===" | tee -a "$LOG"
for ym in $(months); do
  f="$OUT/cpunks/$ym.txt.gz"
  [ -s "$f" ] && continue
  code=$(curl -s -m 45 -o "$f" -w '%{http_code}' \
    "https://lists.cpunks.org/pipermail/cypherpunks/$ym.txt.gz")
  sz=$(stat -c%s "$f" 2>/dev/null || echo 0)
  echo "cpunks $ym http=$code bytes=$sz" >> "$LOG"
  [ "$code" != "200" ] && rm -f "$f"
done

echo "retrieved_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$LOG"
echo "--- fetched ---"
grep -c 'http=200' "$LOG" || true
du -sh "$OUT" 2>/dev/null
