import urllib.parse
import json,os,time,urllib.request,re
ids=["3301.iso","845145127","a2e7j6ic78h0j7eiejd0120","avowyfgl5lkzfj3n.onion","warc-cicada3301_org",
"liber-primus","cicada3301_midi","cicada_202405","plpage0","https-www.dropbox.com-s-r7sgeb5dtmzj14s-3301",
"desmistificando-cicada-3301","codex-galdrux","1231507051321","cicada_201703","fav-cicada-3301",
"bitchute_-_cicada3301_2017","bitchute_-_cicada3301_2018","bitchute_-_cicada3301_2019",
"bitchute_-_cicada3301_2020","bitchute_-_cicada3301_2021","cicada-761","TrollOrRealCicada",
"3301Interconnectedness","Interconnectedness_201805"]
os.makedirs("iarchive",exist_ok=True)
for i in ids:
    fn="iarchive/meta__"+re.sub(r'[^A-Za-z0-9]','_',i)+".json"
    if os.path.exists(fn) and os.path.getsize(fn)>1500 and open(fn,'rb').read(1)==b'{': continue
    for attempt in range(3):
        try:
            b=urllib.request.urlopen("https://archive.org/metadata/"+urllib.parse.quote(i),timeout=45).read()
            if b.startswith(b'{'):
                open(fn,'wb').write(b); print("OK",i,len(b)); break
        except Exception as e: print("retry",i,type(e).__name__)
        time.sleep(3)
    else: print("FAIL",i)
    time.sleep(0.5)
