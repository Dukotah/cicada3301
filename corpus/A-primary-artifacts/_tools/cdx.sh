#!/bin/sh
# usage: cdx.sh <url-pattern> <outfile> [extra]
u="$1"; o="$2"; extra="$3"
curl -s --max-time 110 -A "Mozilla/5.0 (corpus-recovery; research archival)" \
  "https://web.archive.org/cdx/search/cdx?url=$u&output=text&fl=timestamp,original,mimetype,statuscode,digest,length&limit=500&collapse=digest$extra" \
  -o "$o"
printf "%s  %s lines\n" "$u" "$(wc -l < "$o")"
