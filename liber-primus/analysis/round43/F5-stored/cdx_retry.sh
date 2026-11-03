#!/bin/bash
q() { name="$1"; url="$2"; extra="$3";
  for i in 1 2 3 4 5; do
    curl -s --max-time 60 "https://web.archive.org/cdx/search/cdx?url=${url}&output=json${extra}" -o "cdx/${name}.json"
    if head -c 1 "cdx/${name}.json" | grep -q '\['; then break; fi
    if [ ! -s "cdx/${name}.json" ]; then break; fi  # empty = 0 rows
    sleep 15
  done
  n=$(python3 -c "import json,os;p='cdx/${name}.json';d=json.load(open(p)) if os.path.getsize(p) else [];print(max(0,len(d)-1))" 2>/dev/null || echo ERR)
  echo "${name}: rows=${n}"
  sleep 4
}
q wikia-domain "uncovering-cicada.wikia.com&matchType=domain" "&from=2014&to=2016&collapse=urlkey&limit=3000"
q onion-auqg-tor2web "auqgnxjtvdbll3pv.tor2web.org&matchType=domain" "&collapse=urlkey&limit=2000"
q onion-cu34-to "cu343l33nqaekrnw.onion.to&matchType=domain" "&collapse=urlkey&limit=2000"
q onion-ky2k-to "ky2khlqdf7qdznac.onion.to&matchType=domain" "&collapse=urlkey&limit=2000"
q 845145127-domain "845145127.com&matchType=domain" "&collapse=urlkey&limit=2000"
q imgur-eAVCeeC "i.imgur.com/eAVCeeC%2A" "&limit=200"
