import sys, os, json, time, urllib.request, urllib.parse, urllib.error
DEADLINE = time.time() + float(sys.argv[1] if len(sys.argv)>1 else 200)
ORDER = sys.argv[2] if len(sys.argv)>2 else "all"
UA = "cicada3301-corpus-research/1.0 (archival research; contact dukotah@gmail.com)"
os.makedirs("cdx", exist_ok=True)
targets = [l.rstrip("\n").split("\t") for l in open("targets.tsv",encoding="utf-8") if l.strip()]
if ORDER=="core":   targets=[t for t in targets if not t[0].startswith(("onion_","host_"))]
elif ORDER=="onion":targets=[t for t in targets if t[0].startswith("onion_")]
elif ORDER=="host": targets=[t for t in targets if t[0].startswith("host_")]

log = open("logs/cdx.log","a",encoding="utf-8")
done=skipped=err=0
for tid,url,mt,lab in targets:
    out=f"cdx/{tid}.json"
    if os.path.exists(out): skipped+=1; continue
    if time.time()>DEADLINE:
        print("DEADLINE reached"); break
    q={"output":"json","collapse":"digest","limit":"3000"}
    if mt=="domain": q["url"]=url; q["matchType"]="domain"
    elif mt=="prefix": q["url"]=url; q["matchType"]="prefix"
    elif mt=="prefix_star": q["url"]=url
    else: q["url"]=url
    api="http://web.archive.org/cdx/search/cdx?"+urllib.parse.urlencode(q)
    try:
        req=urllib.request.Request(api, headers={"User-Agent":UA})
        with urllib.request.urlopen(req, timeout=90) as r:
            body=r.read(); status=r.status
        open(out,"wb").write(body)
        try: n=max(0,len(json.loads(body or b"[]"))-1)
        except Exception: n=-1
        log.write(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}\t{tid}\t{status}\t{n}\t{api}\n"); log.flush()
        print(f"OK {tid} rows={n}")
        done+=1
        time.sleep(0.6)
    except urllib.error.HTTPError as e:
        log.write(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}\t{tid}\tHTTP{e.code}\t-\t{api}\n"); log.flush()
        print(f"ERR {tid} HTTP{e.code}"); err+=1
        if e.code==429: time.sleep(10)
        else: open(out,"wb").write(b"[]")
        time.sleep(1)
    except Exception as e:
        log.write(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}\t{tid}\tFAIL\t-\t{type(e).__name__}:{e}\n"); log.flush()
        print(f"FAIL {tid} {type(e).__name__}"); err+=1
        time.sleep(2)
print(f"done={done} skipped={skipped} err={err} remaining={sum(1 for t in targets if not os.path.exists('cdx/'+t[0]+'.json'))}")
