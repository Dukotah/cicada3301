import sys, os, json, time, urllib.request, urllib.parse, urllib.error, threading, queue
DEADLINE=time.time()+float(sys.argv[1]); ORDER=sys.argv[2] if len(sys.argv)>2 else "all"
UA="cicada3301-corpus-research/1.0 (archival research)"
targets=[l.rstrip("\n").split("\t") for l in open("targets.tsv",encoding="utf-8") if l.strip()]
if ORDER!="all": targets=[t for t in targets if t[0].startswith(ORDER+"_")]
todo=[t for t in targets if not os.path.exists("cdx/"+t[0]+".json")]
q=queue.Queue(); [q.put(t) for t in todo]
lock=threading.Lock(); log=open("logs/cdx.log","a",encoding="utf-8"); stats={"ok":0,"err":0,"hits":[]}
def work():
    while time.time()<DEADLINE:
        try: tid,url,mt,lab=q.get_nowait()
        except queue.Empty: return
        p={"output":"json","collapse":"digest","limit":"3000","url":url}
        if mt in ("domain","prefix"): p["matchType"]=mt
        api="http://web.archive.org/cdx/search/cdx?"+urllib.parse.urlencode(p)
        try:
            r=urllib.request.urlopen(urllib.request.Request(api,headers={"User-Agent":UA}),timeout=75)
            body=r.read(); st=r.status
            open("cdx/"+tid+".json","wb").write(body)
            try: n=max(0,len(json.loads(body or b"[]"))-1)
            except Exception: n=-1
            with lock:
                log.write(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}\t{tid}\t{st}\t{n}\t{api}\n"); log.flush()
                stats["ok"]+=1
                if n>0: stats["hits"].append((tid,n))
        except Exception as e:
            code=getattr(e,"code",None)
            with lock:
                log.write(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}\t{tid}\t{code or type(e).__name__}\t-\t{api}\n"); log.flush()
                stats["err"]+=1
            if code==429: time.sleep(15)
        time.sleep(0.3)
ts=[threading.Thread(target=work,daemon=True) for _ in range(3)]
[t.start() for t in ts]; [t.join() for t in ts]
print("ok",stats["ok"],"err",stats["err"])
for h in sorted(stats["hits"],key=lambda x:-x[1]): print("HIT",h[0],h[1])
print("remaining",sum(1 for t in targets if not os.path.exists("cdx/"+t[0]+".json")))
