#!/bin/bash
# stdin lines: URL<TAB>outpath<TAB>notes
B="/c/Users/dukot/projects/cicada3301/corpus/C-community"
f(){ IFS=$'\t' read -r U O N <<< "$1"
 [ -s "$B/$O" ] && exit 0
 mkdir -p "$(dirname "$B/$O")"
 TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
 C=$(curl -sL --max-time 90 -A "cicada-corpus-research/1.0" -o "$B/$O" -w "%{http_code}" "$U")
 if [ -s "$B/$O" ] && [ "$C" = "200" ]; then SHA=$(sha256sum "$B/$O"|cut -d' ' -f1); SZ=$(stat -c %s "$B/$O")
  echo "{\"path\":\"$O\",\"sha256\":\"$SHA\",\"bytes\":$SZ,\"source_url\":\"$U\",\"retrieved_utc\":\"$TS\",\"http_status\":$C,\"method\":\"scrape\",\"notes\":\"$N\"}" >> "$B/_logs/manifest.jsonl"
 else rm -f "$B/$O"; echo "{\"path\":null,\"source_url\":\"$U\",\"retrieved_utc\":\"$TS\",\"http_status\":$C,\"method\":\"scrape\",\"notes\":\"FAILED; $N\"}" >> "$B/_logs/failed.jsonl"; fi
}
export -f f 2>/dev/null
f "$1"
