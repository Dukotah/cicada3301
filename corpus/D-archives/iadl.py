import os,sys,json,time,hashlib,urllib.request,urllib.parse
UA="cicada3301-corpus-research/1.0"
DEADLINE=time.time()+float(sys.argv[1])
items=[
 ("845145127","232.jpg"),("845145127","845145127_meta.xml"),("845145127","845145127_files.xml"),
 ("a2e7j6ic78h0j7eiejd0120","a2e7j6ic78h0j7eiejd0120.html"),
 ("a2e7j6ic78h0j7eiejd0120","a2e7j6ic78h0j7eiejd0120_meta.xml"),
 ("avowyfgl5lkzfj3n.onion",".htaccess"),("avowyfgl5lkzfj3n.onion","3301"),
 ("avowyfgl5lkzfj3n.onion","avowyfgl5lkzfj3n.onion_meta.xml"),
 ("cicada3301_midi","oq17i.mid"),("cicada3301_midi","cicada3301_midi_meta.xml"),
 ("plpage0","Book-cover.webp"),("plpage0","plpage0_meta.xml"),
 ("warc-cicada3301_org","cicada3301.org-2016-11-26-1e758227.cdx"),
 ("warc-cicada3301_org","wpull.log"),
 ("warc-cicada3301_org","start_url"),("warc-cicada3301_org","cookies.txt"),
 ("warc-cicada3301_org","cicada3301.org-2016-11-26-1e758227-00000.warc.gz"),
 ("liber-primus","Liber Primus.zip"),("liber-primus","liber-primus_reviews.xml"),
 ("cicada_202405","cicada.zip"),
 ("desmistificando-cicada-3301","Desmistificando - Cicada 3301.png"),
 ("desmistificando-cicada-3301","Desmistificando - Cicada 3301.xlsx"),
 ("1231507051321","Feed @1231507051321.html"),
 ("3301.iso","3301.iso_meta.xml"),
 ("3301.iso","3301.iso"),
]
mf=open("manifest.jsonl","a",encoding="utf-8")
done=set()
for l in open("manifest.jsonl",encoding="utf-8"):
    try: done.add(json.loads(l)["archive_url"])
    except Exception: pass
for item,fn in items:
    url="https://archive.org/download/"+urllib.parse.quote(item)+"/"+urllib.parse.quote(fn)
    if url in done: print("skip",item,fn); continue
    if time.time()>DEADLINE: print("DEADLINE"); break
    out=os.path.join("iarchive","items",item.replace(":","_"),fn.replace("/","_"))
    os.makedirs(os.path.dirname(out),exist_ok=True)
    try:
        t0=time.time()
        r=urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":UA}),timeout=180)
        h=hashlib.sha256(); n=0
        with open(out,"wb") as f:
            while True:
                c=r.read(1<<20)
                if not c: break
                f.write(c); h.update(c); n+=len(c)
        hdrs=dict(r.getheaders())
        mf.write(json.dumps({"path":out.replace("\\","/"),"sha256":h.hexdigest(),"bytes":n,
          "original_url":url,"archive_url":url,"capture_timestamp":"",
          "retrieved_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
          "http_status":r.status,"content_type":hdrs.get("Content-Type",""),
          "group":"archive.org-item","ia_item":item,"ia_file":fn,
          "orig_headers":{"Last-Modified":hdrs.get("Last-Modified",""),"ETag":hdrs.get("ETag","")}})+"\n"); mf.flush()
        print(f"OK {item}/{fn} {n}B {time.time()-t0:.0f}s")
    except Exception as e:
        print("FAIL",item,fn,type(e).__name__,e)
