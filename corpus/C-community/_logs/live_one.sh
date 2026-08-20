#!/bin/bash
B="/c/Users/dukot/projects/cicada3301/corpus/C-community"
p="$1"; OD="$2"; N="$3"
slug=$(echo "$p"|sed 's|^/||; s|/|_|g')
out="$OD/${slug}.html"
[ -s "$B/$out" ] && exit 0
TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
U="https://cicada3301.boards.net${p}"
CODE=$(curl -sL --max-time 45 -A "cicada-corpus-research/1.0 (archival preservation)" -o "$B/$out" -w "%{http_code}" "$U")
if [ -s "$B/$out" ]; then SHA=$(sha256sum "$B/$out"|cut -d' ' -f1); SZ=$(stat -c %s "$B/$out")
echo "{\"path\":\"$out\",\"sha256\":\"$SHA\",\"bytes\":$SZ,\"source_url\":\"$U\",\"retrieved_utc\":\"$TS\",\"http_status\":$CODE,\"method\":\"scrape\",\"notes\":\"$N\"}" >> "$B/_logs/manifest.jsonl"; else rm -f "$B/$out"; fi
