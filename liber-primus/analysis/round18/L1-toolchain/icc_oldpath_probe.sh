#!/usr/bin/env bash
# Early Ghostscript releases kept the ICC profiles under gs/iccprofiles/ rather
# than iccprofiles/.  Probe both paths for the 9.0x-9.17 tags so the LOWER bound
# on the profile's first appearance can be measured, not assumed.
# Appends to icc_versions_early.json.
set -u
D="$(cd "$(dirname "$0")" && pwd)"
W=/tmp/gsicc; mkdir -p "$W"
OUT="$D/icc_versions_early.json"
: > "$OUT.tmp"
for t in ghostpdl-9.00 ghostpdl-9.01 ghostpdl-9.02 ghostpdl-9.04 ghostpdl-9.05 \
         ghostpdl-9.06 ghostpdl-9.07 ghostpdl-9.09 ghostpdl-9.10 ghostpdl-9.12 \
         ghostpdl-9.14 ghostpdl-9.15 ghostpdl-9.16 ghostpdl-9.17 ; do
  found=""
  for p in gs/iccprofiles/srgb.icc iccprofiles/srgb.icc gs/iccprofiles/default_rgb.icc ; do
    f="$W/${t}__$(echo "$p" | tr / _)"
    if [ ! -s "$f" ]; then
      timeout 30 curl -sSLf -o "$f" \
        "https://raw.githubusercontent.com/ArtifexSoftware/ghostpdl/$t/$p" || rm -f "$f"
    fi
    if [ -s "$f" ]; then found="$p"; break; fi
  done
  if [ -n "$found" ]; then
    python3 - "$f" "$t" "$found" >> "$OUT.tmp" <<'PY'
import sys, hashlib, json
p, tag, path = sys.argv[1], sys.argv[2], sys.argv[3]
d = open(p, 'rb').read()
print(json.dumps({"tag": tag, "path": path, "len": len(d),
                  "md5": hashlib.md5(d).hexdigest(),
                  "illuminant_68_79": d[68:80].hex() if len(d) >= 80 else None,
                  "matches_LP2": hashlib.md5(d).hexdigest() == "e409cef13cd06f6b371f6cddc8e31fcf"}))
PY
  else
    echo "{\"tag\": \"$t\", \"error\": \"no srgb.icc at any probed path\"}" >> "$OUT.tmp"
  fi
  tail -1 "$OUT.tmp"
done
python3 - "$OUT.tmp" "$OUT" <<'PY'
import sys, json
rows = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
json.dump(rows, open(sys.argv[2], 'w'), indent=1)
PY
rm -f "$OUT.tmp"
echo DONE
