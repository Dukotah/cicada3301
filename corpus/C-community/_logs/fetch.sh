#!/bin/bash
# fetch.sh <url> <outpath> <method> <notes>
U="$1"; O="$2"; M="${3:-scrape}"; N="${4:-}"
B="/c/Users/dukot/projects/cicada3301/corpus/C-community"
mkdir -p "$(dirname "$B/$O")"
TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
CODE=$(curl -sL --max-time 110 --retry 1 -A "cicada-corpus-research/1.0 (archival research; contact dukotah@gmail.com)" -o "$B/$O" -w "%{http_code}" "$U")
if [ ! -s "$B/$O" ]; then echo "EMPTY $CODE $U"; rm -f "$B/$O"; echo "{\"path\":null,\"source_url\":\"$U\",\"retrieved_utc\":\"$TS\",\"http_status\":$CODE,\"method\":\"$M\",\"notes\":\"empty/failed: $N\"}" >> "$B/_logs/manifest.jsonl"; exit 1; fi
SHA=$(sha256sum "$B/$O" | cut -d' ' -f1)
SZ=$(stat -c %s "$B/$O")
echo "{\"path\":\"$O\",\"sha256\":\"$SHA\",\"bytes\":$SZ,\"source_url\":\"$U\",\"retrieved_utc\":\"$TS\",\"http_status\":$CODE,\"method\":\"$M\",\"notes\":\"$N\"}" >> "$B/_logs/manifest.jsonl"
echo "OK $CODE $SZ $O"
