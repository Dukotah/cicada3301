#!/bin/bash
# F5a Wayback leg: CDX queries, outputs saved to cdx/<name>.json
q() { name="$1"; shift; url="$1"; shift; extra="$*";
  curl -s --max-time 60 "https://web.archive.org/cdx/search/cdx?url=${url}&output=json${extra}" -o "cdx/${name}.json";
  n=$(python3 -c "import json;d=json.load(open('cdx/${name}.json')) if __import__('os').path.getsize('cdx/${name}.json') else [];print(max(0,len(d)-1))" 2>/dev/null || echo ERR);
  echo "${name}: rows=${n}  url=${url} ${extra}";
  sleep 2;
}
q wikia-domain "uncovering-cicada.wikia.com&matchType=domain" "&from=2014&to=2016&collapse=urlkey&limit=3000"
q onion-auqg-to "auqgnxjtvdbll3pv.onion.to&matchType=domain" "&collapse=urlkey&limit=2000"
q onion-auqg-cab "auqgnxjtvdbll3pv.onion.cab&matchType=domain" "&collapse=urlkey&limit=2000"
q onion-auqg-link "auqgnxjtvdbll3pv.onion.link&matchType=domain" "&collapse=urlkey&limit=2000"
q onion-auqg-tor2web "auqgnxjtvdbll3pv.tor2web.org&matchType=domain" "&collapse=urlkey&limit=2000"
q onion-cu34-to "cu343l33nqaekrnw.onion.to&matchType=domain" "&collapse=urlkey&limit=2000"
q onion-ky2k-to "ky2khlqdf7qdznac.onion.to&matchType=domain" "&collapse=urlkey&limit=2000"
q 845145127-domain "845145127.com&matchType=domain" "&collapse=urlkey&limit=2000"
q imgur-D5eBa "imgur.com/a/D5eBa" "&limit=200"
q imgur-AENeJ "imgur.com/a/AENeJ" "&limit=200"
q imgur-7Rhb9 "imgur.com/a/7Rhb9" "&limit=200"
q imgur-eAVCeeC "i.imgur.com/eAVCeeC*" "&limit=200"
