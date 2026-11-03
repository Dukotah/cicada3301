#!/bin/bash
q() { name="$1"; url="$2"; extra="$3";
  for i in 1 2 3 4 5; do
    curl -s --max-time 60 "https://web.archive.org/cdx/search/cdx?url=${url}&output=json${extra}" -o "cdx/${name}.json"
    if head -c 1 "cdx/${name}.json" | grep -q '\['; then break; fi
    if [ ! -s "cdx/${name}.json" ]; then break; fi
    sleep 15
  done
  n=$(python3 -c "import json,os;p='cdx/${name}.json';d=json.load(open(p)) if os.path.getsize(p) else [];print(max(0,len(d)-1))" 2>/dev/null || echo ERR)
  echo "${name}: rows=${n}"
  sleep 4
}
q wikia-img-images "images.wikia.com/uncovering-cicada%2A" "&collapse=urlkey&limit=3000"
q wikia-img-vignette "vignette.wikia.nocookie.net/uncovering-cicada%2A" "&collapse=urlkey&limit=3000"
q wikia-img-static "static.wikia.nocookie.net/uncovering-cicada%2A" "&collapse=urlkey&limit=3000"
q wikia-img1 "img1.wikia.nocookie.net/__cb%2A" "&filter=original:.*uncovering-cicada.*&collapse=urlkey&limit=2000"
q wikia-img2 "img2.wikia.nocookie.net/__cb%2A" "&filter=original:.*uncovering-cicada.*&collapse=urlkey&limit=2000"
q wikia-img3 "img3.wikia.nocookie.net/__cb%2A" "&filter=original:.*uncovering-cicada.*&collapse=urlkey&limit=2000"
q wikia-img4 "img4.wikia.nocookie.net/__cb%2A" "&filter=original:.*uncovering-cicada.*&collapse=urlkey&limit=2000"
q imgur-EKoUaoV "i.imgur.com/EKoUaoV%2A" "&limit=100"
