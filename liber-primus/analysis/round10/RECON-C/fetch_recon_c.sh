#!/bin/bash
# RECON-C — resumable fetcher for the never-ingested external sources found in Round 10.
# Writes ONLY into this folder. No git. Re-run safe (skips files already present).
#
#   bash fetch_recon_c.sh          # tier 1 only (~2 MB)
#   bash fetch_recon_c.sh reddit   # additionally paginate the Reddit archive
#
set -u
OUT="$(cd "$(dirname "$0")" && pwd)/fetched"
mkdir -p "$OUT/cijhho_leak"
RAW="https://raw.githubusercontent.com/krisyotam/cicada3301/main"
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36'

get() {  # get <url-encoded-path> <local-name>
  local dest="$OUT/cijhho_leak/$2"
  if [ -s "$dest" ]; then echo "skip  $2"; return; fi
  code=$(curl -sSL --max-time 120 -A "$UA" -w "%{http_code}" -o "$dest" "$RAW/$1")
  if [ "$code" = "200" ]; then echo "ok    $2  ($(wc -c <"$dest") B)"
  else echo "FAIL  $2  HTTP $code"; rm -f "$dest"; fi
}

echo "== RECON-C-01: cijhho insider/leak tree (krisyotam/cicada3301) =="
get "archives/irc-logs/logs%20from%20IRC%20winners%20leak.txt"                                              "irc_winners_leak.txt"
get "archives/cijhho/2012/additional%20media/Unverified%20and%20Leaked%20information/logs%20on%20zerobin.txt" "logs_on_zerobin.txt"
get "archives/cijhho/2012/additional%20docs/unverified%20claims%20from%20alleged%20winners%20on%20Unfiction.docx" "unfiction_alleged_winners.docx"
get "archives/cijhho/2012/additional%20docs/The%20Leaked%20Email/2012%20winners%20leak.txt"                  "2012_winners_leak.txt"
get "archives/cijhho/2012/additional%20docs/The%20Leaked%20Email/the%20pastebin%20leaked.txt"                "2012_pastebin_leaked.txt"
get "archives/cijhho/2013/additional%20docs/The%20Leaked%20Email/Server%20response%20-%20include%20leaker%20email%20with%20pgp.txt" "2013_server_response_leaker_pgp.txt"
get "archives/cijhho/2013/additional%20docs/The%20Leaked%20Email/WE%20GOT%20EMAILS.docx"                     "2013_we_got_emails.docx"
get "archives/cijhho/2013/additional%20docs/The%20infamous%20warnning/2013%20-%20unverified%20Warning%20found%20on%20pastebin.docx" "2013_unverified_warning.docx"
get "archives/cijhho/2014/additional%20docs/2014%20will%20change%20thise%20(leaked%20too%20much).txt"        "2014_leaked_too_much.txt"

echo
echo "== full tree manifest (for anything else worth pulling) =="
if [ ! -s "$OUT/krisyotam_tree.tsv" ]; then
  gh api "repos/krisyotam/cicada3301/git/trees/main?recursive=1" \
    --jq '.tree[] | select(.type=="blob") | "\(.size)\t\(.path)"' > "$OUT/krisyotam_tree.tsv" 2>/dev/null \
    && echo "ok    krisyotam_tree.tsv ($(wc -l <"$OUT/krisyotam_tree.tsv") blobs)" \
    || echo "FAIL  tree (needs authenticated gh)"
else echo "skip  krisyotam_tree.tsv"; fi

if [ "${1:-}" = "reddit" ]; then
  echo
  echo "== RECON-C-02: Reddit archive (arctic-shift), paginated by created_utc =="
  API="https://arctic-shift.photon-reddit.com/api"
  for sub in a2e7j6ic78h0j Cicada; do
    for kind in posts comments; do
      f="$OUT/reddit_${sub}_${kind}.jsonl"; [ -s "$f" ] && { echo "skip  $(basename "$f")"; continue; }
      after=0; total=0
      while : ; do
        page=$(curl -s --max-time 60 "$API/$kind/search?subreddit=$sub&limit=100&sort=asc&after=$after")
        n=$(printf '%s' "$page" | python3 -c 'import json,sys;print(len(json.load(sys.stdin).get("data") or []))' 2>/dev/null || echo 0)
        [ "$n" = "0" ] && break
        printf '%s' "$page" | python3 -c '
import json,sys
for r in json.load(sys.stdin)["data"]: print(json.dumps(r))' >> "$f"
        after=$(printf '%s' "$page" | python3 -c '
import json,sys
d=json.load(sys.stdin)["data"]; print(d[-1]["created_utc"])')
        total=$((total+n)); [ "$n" -lt 100 ] && break
      done
      echo "ok    $(basename "$f")  ($total rows)"
    done
  done
fi

echo
echo "Done. Output in: $OUT"
echo "NEXT: read fetched/cijhho_leak/irc_winners_leak.txt against"
echo "      analysis/attribution/CAMPAIGN-XIX-WITNESSES.md findings #1 and #2."
echo "FALSIFIER: the Campaign XIX bound survives UNLESS this log contains a first-person"
echo "      claim that 3301 distributed CIPHER MATERIAL OR KEYS to insiders."
echo "      'they gave us access / a wiki / a git' does NOT meet that bar."
