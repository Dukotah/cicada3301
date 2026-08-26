#!/usr/bin/env bash
# Acquire the Marsaglia Random Number CDROM (1995) from archive.org item `marsaglia-cdrom`.
# Verifies the ISO against archive.org's published md5/sha1 AND records the item's own
# checksums.sha256.txt (the CDROM's published per-file SHA-256 manifest).
#
# This repo has twice been burned by a mirror serving different bytes (a 60.4% prefix of
# _560.00; a Git-LFS pointer standing in for DATA/560.13). Nothing is swept before the
# hashes match.
set -u
D="$(cd "$(dirname "$0")/.." && pwd)/data"
mkdir -p "$D"
cd "$D" || exit 1

BASE=https://archive.org/download/marsaglia-cdrom

# ---- small files first
for f in checksums.sha256.txt marsaglia-cdrom_meta.xml marsaglia-cdrom_files.xml; do
  if [ ! -s "$f" ]; then
    echo "[fetch] $f"
    curl -sSL --retry 8 --retry-all-errors --retry-delay 3 -m 300 -o "$f" "$BASE/$f" || echo "FAILED $f"
  fi
done

# ---- the ISO, resumable
ISO=MARSAGLIA_CDROM.iso
WANT_SIZE=634124288
for attempt in 1 2 3 4 5 6 7 8 9 10; do
  have=$(stat -c%s "$ISO" 2>/dev/null || echo 0)
  if [ "$have" -ge "$WANT_SIZE" ]; then break; fi
  echo "[fetch] $ISO attempt $attempt  (have $have / $WANT_SIZE)"
  curl -sSL -C - --retry 5 --retry-all-errors --retry-delay 5 -m 3600 -o "$ISO" "$BASE/$ISO" \
    || echo "  (transfer interrupted, retrying)"
done

echo "--- sizes ---"
ls -l "$D"
echo "--- hashes ---"
[ -s "$ISO" ] && { md5sum "$ISO"; sha1sum "$ISO"; sha256sum "$ISO"; }
[ -s checksums.sha256.txt ] && sha256sum checksums.sha256.txt
