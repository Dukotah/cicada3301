#!/bin/bash
B="/c/Users/dukot/projects/cicada3301/corpus/C-community"
line="$1"; OD="$2"; N="$3"
ts="${line%%	*}"; u="${line#*	}"
slug=$(echo "$u" | sed 's|https\?://||; s|[:/?&=%]|_|g' | cut -c1-110)
out="$OD/${ts}__${slug}.html"
[ -s "$B/$out" ] && exit 0
TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
WU="https://web.archive.org/web/${ts}id_/${u}"
CODE=$(curl -sL --max-time 60 -A "cicada-corpus-research/1.0" -o "$B/$out" -w "%{http_code}" "$WU")
if [ -s "$B/$out" ]; then
  SHA=$(sha256sum "$B/$out"|cut -d' ' -f1); SZ=$(stat -c %s "$B/$out")
  echo "{\"path\":\"$out\",\"sha256\":\"$SHA\",\"bytes\":$SZ,\"source_url\":\"$WU\",\"retrieved_utc\":\"$TS\",\"http_status\":$CODE,\"method\":\"archive\",\"notes\":\"$N; original=$u; wayback_ts=$ts\"}" >> "$B/_logs/manifest.jsonl"
else
  rm -f "$B/$out"
  echo "{\"path\":null,\"source_url\":\"$WU\",\"retrieved_utc\":\"$TS\",\"http_status\":$CODE,\"method\":\"archive\",\"notes\":\"FAILED; $N\"}" >> "$B/_logs/manifest.jsonl"
fi
