#!/bin/bash
# L6-archives — pull the never-held CicadaSolvers Discord exports + the 13.5 MB
# 2014-01 "interconnectedness" hex block from jaxonkuipers/cicada3301
# (repo created after this project's last OSINT sweep of 2026-07-27; G1 novelty = 0 hits).
# Writes ONLY into this lane's folder. Re-run safe.
set -u
OUT="$(cd "$(dirname "$0")" && pwd)/fetched/jaxonkuipers"
mkdir -p "$OUT/discord" "$OUT/corpus"
RAW="https://raw.githubusercontent.com/jaxonkuipers/cicada3301/main"
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36'

get() {
  local dest="$OUT/$2"
  if [ -s "$dest" ]; then echo "skip  $2"; return; fi
  code=$(curl -sSL --max-time 300 -A "$UA" -w "%{http_code}" -o "$dest" "$RAW/$1")
  if [ "$code" = "200" ]; then echo "ok    $2  ($(wc -c <"$dest") B)"
  else echo "FAIL  $2  HTTP $code"; rm -f "$dest"; fi
}

for f in 0-2 3-7 8-14 15-22 23-26 27-32 33-39 40-55 54-55 \
         deep-web-hash gematria-primus solved-pages solving-lp-general README; do
  get "discord/$f.txt" "discord/$f.txt" 2>/dev/null || get "discord/$f.md" "discord/$f.md"
done
get "discord/README.md" "discord/README.md"
get "corpus/README.md" "corpus/README_corpus.md"
get "corpus/liber-primus/README.md" "corpus/README_lp.md"
get "corpus/communications/2014-01-interconnectedness-hex.asc" "corpus/2014-01-interconnectedness-hex.asc"
get "corpus/communications/2014-01-let-the-text-guide-you.asc" "corpus/2014-01-let-the-text-guide-you.asc"
get "corpus/communications/2014-01-onion5-liber-primus.asc"    "corpus/2014-01-onion5-liber-primus.asc"
get "corpus/liber-primus/sentences.csv" "corpus/sentences.csv"
get "corpus/liber-primus/pages.csv"     "corpus/pages.csv"
echo "Done -> $OUT"
