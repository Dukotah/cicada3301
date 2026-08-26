#!/usr/bin/env bash
# Bound the Ghostscript release by its shipped iccprofiles/srgb.icc.
# The LP2 pages embed a 2576-byte "Artifex Software sRGB ICC Profile" whose
# PCS-illuminant bytes at offset 68..79 are 0000f6d5 00010000 0000d32c.
# Ghostscript 10.06.0 ships 0000f6d6 00010000 0000d32d -- 2 bytes different,
# every other byte identical.  Find the release where that changed.
#
# Writes icc_versions.json incrementally so a stall never loses work.
set -u
D="$(cd "$(dirname "$0")" && pwd)"
W=/tmp/gsicc; mkdir -p "$W"; cd "$W"
OUT="$D/icc_versions.json"
TAGS="ghostpdl-9.00 ghostpdl-9.01 ghostpdl-9.02 ghostpdl-9.04 ghostpdl-9.05 ghostpdl-9.06 ghostpdl-9.07 ghostpdl-9.09 ghostpdl-9.10 ghostpdl-9.12 ghostpdl-9.14 ghostpdl-9.15 ghostpdl-9.16 ghostpdl-9.17 gs918 gs919 gs920 gs921 ghostpdl-9.22 ghostpdl-9.26 ghostpdl-9.50 ghostpdl-9.53.3"
echo "[" > "$OUT.tmp"
first=1
for t in $TAGS; do
  f="$W/$t.icc"
  if [ ! -s "$f" ]; then
    timeout 40 curl -sSLf -o "$f" \
      "https://raw.githubusercontent.com/ArtifexSoftware/ghostpdl/$t/iccprofiles/srgb.icc" || rm -f "$f"
  fi
  if [ -s "$f" ]; then
    row=$(python3 - "$f" "$t" <<'PY'
import sys, hashlib, json
p, tag = sys.argv[1], sys.argv[2]
d = open(p, 'rb').read()
print(json.dumps({"tag": tag, "len": len(d),
                  "md5": hashlib.md5(d).hexdigest(),
                  "illuminant_68_79": d[68:80].hex() if len(d) >= 80 else None,
                  "matches_LP2": hashlib.md5(d).hexdigest() == "e409cef13cd06f6b371f6cddc8e31fcf"}))
PY
)
  else
    row="{\"tag\": \"$t\", \"error\": \"fetch failed\"}"
  fi
  [ $first -eq 1 ] || echo "," >> "$OUT.tmp"
  first=0
  printf '%s' "$row" >> "$OUT.tmp"
  echo "$row"
done
echo "" >> "$OUT.tmp"; echo "]" >> "$OUT.tmp"
mv "$OUT.tmp" "$OUT"
echo DONE
