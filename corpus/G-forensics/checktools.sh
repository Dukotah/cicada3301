#!/bin/bash
for t in exiftool binwalk steghide sox convert ffmpeg gem zsteg outguess stegdetect ruby; do
  p=$(command -v "$t")
  if [ -n "$p" ]; then echo "$t OK $p"; else echo "$t MISSING"; fi
done
echo "--- apt log tail ---"
tail -4 /tmp/g_apt2.log 2>&1
