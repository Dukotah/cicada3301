import sys,os,json,time,hashlib,urllib.request,urllib.parse,urllib.error,threading,queue
DEADLINE=time.time()+float(sys.argv[1])
UA="cicada3301-corpus-research/1.0 (archival research; byte-diff across capture dates)"
jobs=json.load(open("bytediff_jobs.json"))
DONE=set()
if os.path.exists("bytediff_manifest.jsonl"):
    for l in open("bytediff_manifest.jsonl",encoding="utf-8"):
        try: r=json.loads(l); DONE.add((r["original_url"],r["capture_timestamp"]))
        except Exception: pass
todo=[j for j in jobs if (j["url"],j["ts"]) not in DONE]
os.makedirs("bytediff",exist_ok=True)
q=queue.Queue(); [q.put(j) for j in todo]
lock=threading.Lock(); mf=open("bytediff_manifest.jsonl","a",encoding="utf-8")
st={"ok":0,"fail":0}
def work():
    while time.time()<DEADLINE:
        try: j=q.get_nowait()
        except queue.Empty: return
        wb="https://web.archive.org/web/%sid_/%s"%(j["ts"],j["url"])
        row={"original_url":j["url"],"capture_timestamp":j["ts"],"archive_url":wb,
             "cdx_digest":j["digest"],"cdx_mimetype":j["mime"],"cdx_length":j["cdx_len"],"target":j["target"]}
        try:
            r=urllib.request.urlopen(urllib.request.Request(wb,headers={"User-Agent":UA}),timeout=60)
            body=r.read(); code=r.status; ct=dict(r.getheaders()).get("Content-Type","")
        except Exception as e:
            row.update({"error":"%s: %s"%(type(e).__name__,e)})
            with lock: mf.write(json.dumps(row)+"\n"); mf.flush(); st["fail"]+=1
            time.sleep(2); continue
        h=hashlib.sha256(body).hexdigest()
        name=hashlib.sha1((j["url"]+j["ts"]).encode()).hexdigest()[:16]
        p=os.path.join("bytediff",name+".bin"); open(p,"wb").write(body)
        row.update({"path":p.replace("\\","/"),"sha256":h,"bytes":len(body),"http_status":code,
                    "content_type":ct,"retrieved_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())})
        with lock: mf.write(json.dumps(row)+"\n"); mf.flush(); st["ok"]+=1
        time.sleep(1.5)
ts=[threading.Thread(target=work) for _ in range(1)]
[t.start() for t in ts]; [t.join() for t in ts]
print("ok",st["ok"],"fail",st["fail"],"remaining",q.qsize())
