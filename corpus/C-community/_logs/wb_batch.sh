#!/bin/bash
# wb_batch.sh <targetfile> <outdir> <start> <count> <notes>
B="/c/Users/dukot/projects/cicada3301/corpus/C-community"
TF="$1"; OD="$2"; S="$3"; C="$4"; N="$5"
mkdir -p "$B/$OD"
sed -n "$((S+1)),$((S+C))p" "$TF" | while IFS=$'\t' read -r ts u; do
  slug=$(echo "$u" | sed 's|https\?://||; s|[:/?&=]|_|g' | cut -c1-120)
  out="$OD/${ts}__${slug}.html"
  [ -s "$B/$out" ] && { echo "SKIP $out"; continue; }
  TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  WU="https://web.archive.org/web/${ts}id_/${u}"
  CODE=$(curl -sL --max-time 60 -A "cicada-corpus-research/1.0" -o "$B/$out" -w "%{http_code}" "$WU")
  if [ -s "$B/$out" ]; then
    SHA=$(sha256sum "$B/$out"|cut -d' ' -f1); SZ=$(stat -c %s "$B/$out")
    echo "{\"path\":\"$out\",\"sha256\":\"$SHA\",\"bytes\":$SZ,\"source_url\":\"$WU\",\"retrieved_utc\":\"$TS\",\"http_status\":$CODE,\"method\":\"archive\",\"notes\":\"$N; original=$u; wayback_ts=$ts\"}" >> "$B/_logs/manifest.jsonl"
    echo "OK $CODE $SZ $out"
  else
    rm -f "$B/$out"; echo "FAIL $CODE $u"
    echo "{\"path\":null,\"source_url\":\"$WU\",\"retrieved_utc\":\"$TS\",\"http_status\":$CODE,\"method\":\"archive\",\"notes\":\"FAILED; $N\"}" >> "$B/_logs/manifest.jsonl"
  fi
  sleep 1
done
