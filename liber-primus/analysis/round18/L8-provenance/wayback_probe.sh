#!/bin/bash
# L8 / I-03 -- Wayback CDX probes. The CDX API returns machine-checkable capture rows
# (urlkey, timestamp, status), so "earliest capture" is a measured fact, not a guess.
set -u
BASE="$(cd "$(dirname "$0")" && pwd)"
OUT="$BASE/evidence/archives/wayback-cdx.txt"
: > "$OUT"
q() {
  echo "### $1" >> "$OUT"
  curl -sL -m 45 "http://web.archive.org/cdx/search/cdx?url=$2&output=text&fl=timestamp,original,statuscode&collapse=timestamp:6&limit=$3" >> "$OUT" 2>&1
  echo >> "$OUT"
}
q "845145127.com (the 2012 countdown domain) - earliest captures" "845145127.com*" 25
q "cypherpunks archive on al-qaeda.net" "al-qaeda.net/pipermail/cypherpunks*" 30
q "cypherpunks archive on cpunks.org"  "cpunks.org/pipermail/cypherpunks*" 30
q "cypherpunks.venona.com"             "cypherpunks.venona.com*" 20
q "metzdowd cryptography archive index" "metzdowd.com/pipermail/cryptography/" 20
echo "retrieved_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$OUT"
wc -l "$OUT"
