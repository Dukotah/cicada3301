#!/bin/bash
for id in vGMK330j gkqXuAZN CiPkb0rF 684DsBhk yEiTHhvF 5ETVTQfZ NqF7M1Xn wdVvWF06 n2QGsD3V dhuve6GY b8UYecg1 XbHZg5sJ PFb6eQiD H1iKcvcr DYNeEYji DK6KtTMp 9xkW41S1 smRatr3D; do
  for i in 1 2 3; do
    curl -s --max-time 45 "https://web.archive.org/cdx/search/cdx?url=pastebin.com/${id}&output=json&limit=50" -o "cdx/pb_${id}.json"
    if [ ! -s "cdx/pb_${id}.json" ] || head -c 1 "cdx/pb_${id}.json" | grep -q '\['; then break; fi
    sleep 12
  done
  n=$(python3 -c "import json,os;p='cdx/pb_${id}.json';d=json.load(open(p)) if os.path.getsize(p) else [];print(max(0,len(d)-1))" 2>/dev/null || echo ERR)
  echo "pb_${id}: rows=${n}"
  sleep 3
done
