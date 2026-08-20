import sys,os,json,time,hashlib,urllib.request,urllib.parse,urllib.error,threading,queue,re
DEADLINE=time.time()+float(sys.argv[1]); ONLY=sys.argv[2] if len(sys.argv)>2 else None
UA="cicada3301-corpus-research/1.0 (archival research)"
jobs=json.load(open("fetchjobs.json"))
if ONLY: jobs=[j for j in jobs if j["group"]==ONLY]
DONE=set()
if os.path.exists("manifest.jsonl"):
    for l in open("manifest.jsonl",encoding="utf-8"):
        try: r=json.loads(l); DONE.add((r["original_url"],r["capture_timestamp"]))
        except Exception: pass
if os.path.exists("logs/fetch_fail.jsonl"):
    for l in open("logs/fetch_fail.jsonl",encoding="utf-8"):
        try: r=json.loads(l); DONE.add((r["original_url"],r["capture_timestamp"]))
        except Exception: pass
todo=[j for j in jobs if (j["url"],j["ts"]) not in DONE]
def safepath(u,ts):
    p=urllib.parse.urlparse(u)
    host=(p.netloc or "unknown").replace(":","_")
    path=p.path or "/"
    if path.endswith("/"): path+="index.html"
    if p.query: path+="__q_"+hashlib.sha1(p.query.encode()).hexdigest()[:10]
    BAD = set('<>:"|?*' + chr(92))
    path = "".join("_" if ch in BAD else ch for ch in path.lstrip("/")) or "index.html"
    path="/".join(seg[:80] for seg in path.split("/"))
    return os.path.join("captures",host,ts,path)
q=queue.Queue(); [q.put(j) for j in todo]
lock=threading.Lock()
mf=open("manifest.jsonl","a",encoding="utf-8"); ff=open("logs/fetch_fail.jsonl","a",encoding="utf-8")
st={"ok":0,"fail":0,"bytes":0}
def work():
    while time.time()<DEADLINE:
        try: j=q.get_nowait()
        except queue.Empty: return
        wb=f"https://web.archive.org/web/{j['ts']}id_/{j['url']}"
        try:
            r=urllib.request.urlopen(urllib.request.Request(wb,headers={"User-Agent":UA}),timeout=70)
            body=r.read(); hdrs=dict(r.getheaders()); code=r.status
        except urllib.error.HTTPError as e:
            try: body=e.read()
            except Exception: body=b""
            hdrs=dict(e.headers.items()) if e.headers else {}; code=e.code
            if code in (403,404,412,429,500,502,503,504) and not body:
                with lock:
                    ff.write(json.dumps({"original_url":j["url"],"capture_timestamp":j["ts"],"http_status":code,"archive_url":wb})+"\n"); ff.flush(); st["fail"]+=1
                if code==429: time.sleep(12)
                continue
        except Exception as e:
            with lock:
                ff.write(json.dumps({"original_url":j["url"],"capture_timestamp":j["ts"],"http_status":type(e).__name__,"archive_url":wb})+"\n"); ff.flush(); st["fail"]+=1
            time.sleep(1); continue
        path=safepath(j["url"],j["ts"])
        os.makedirs(os.path.dirname(path),exist_ok=True)
        open(path,"wb").write(body)
        row={"path":path.replace("\\","/"),"sha256":hashlib.sha256(body).hexdigest(),"bytes":len(body),
             "original_url":j["url"],"archive_url":wb,"capture_timestamp":j["ts"],
             "retrieved_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
             "http_status":code,"content_type":hdrs.get("Content-Type",""),
             "cdx_statuscode":j["status"],"cdx_digest":j["digest"],"cdx_mimetype":j["mime"],
             "cdx_length":j["cdx_len"],"group":j["group"],
             "orig_headers":{k[len("X-Archive-Orig-"):]:v for k,v in hdrs.items() if k.lower().startswith("x-archive-orig-")},
             "archive_headers":{k:v for k,v in hdrs.items() if k.lower().startswith("x-archive-") and not k.lower().startswith("x-archive-orig-")}}
        with lock:
            mf.write(json.dumps(row)+"\n"); mf.flush(); st["ok"]+=1; st["bytes"]+=len(body)
        time.sleep(0.15)
ts=[threading.Thread(target=work,daemon=True) for _ in range(6)]
[t.start() for t in ts]; [t.join() for t in ts]
print(f"ok={st['ok']} fail={st['fail']} bytes={st['bytes']} remaining={q.qsize()}")
