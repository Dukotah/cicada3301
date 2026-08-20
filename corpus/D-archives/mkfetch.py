import json, urllib.parse, collections, re
t=json.load(open("TIMELINE.json",encoding="utf-8"))
NOISE=("yniir5c6cmuwslfl","lwplxqzvmgu43uff")
def hostkey(u):
    h=urllib.parse.urlparse(u).netloc.lower().replace(":80","").replace(":443","")
    if h.startswith("www."): h=h[4:]
    return h
# budgets per hostkey group
def group(h):
    if ".onion" in h: return "ONION"
    for g in ("845145127.com","pastebin.com","imgur.com","clevcode.org","twitter.com",
              "opensource.exposed","cicada3301.boards.net","uncovering-cicada.fandom.com",
              "uncovering-cicada.wikia.com","cicada3301.org","cicada3301.com","cicada3301.net",
              "cicadasolvers.com","liberprimus.com","connortumbleson.com","reddit.com","iamamiwhoami.com"):
        if h==g or h.endswith("."+g): return g
    return None
BUDGET={"ONION":10000,"845145127.com":10000,"pastebin.com":10000,"imgur.com":10000,
 "clevcode.org":140,"twitter.com":80,"opensource.exposed":160,"cicada3301.boards.net":320,
 "uncovering-cicada.fandom.com":220,"uncovering-cicada.wikia.com":220,"cicada3301.org":90,
 "cicada3301.com":60,"cicada3301.net":50,"cicadasolvers.com":90,"liberprimus.com":25,
 "connortumbleson.com":40,"reddit.com":120,"iamamiwhoami.com":15}
def skip_url(u,h):
    if "load.php" in u or "wikia.php" in u or "/index.php?" in u: return True
    if re.search(r"\.(css|woff2?|ttf|eot|svg)(\?|$)",u,re.I) and "onion" not in h: return True
    if ".onion" in h and any(n in h for n in NOISE) and not u.endswith("robots.txt"): return True
    if "imgur.com" in h and not re.search(r"(i\.imgur\.com/|imgur\.com/[A-Za-z0-9]{5,8}$)",u): return True
    if "pastebin.com" in h and "yEiTHhvF" not in u: return True
    return False
buckets=collections.defaultdict(list)
for u,v in t.items():
    h=hostkey(u); g=group(h)
    if not g or skip_url(u,h): continue
    seen=set(); caps=[]
    for c in v["captures"]:
        if c["digest"] in seen: continue
        seen.add(c["digest"]); caps.append(c)
    buckets[g].append((u,caps,v["target"]))
jobs=[]
for g,items in buckets.items():
    b=BUDGET[g]; total=sum(len(c) for _,c,_ in items)
    if total<=b: per={u:len(c) for u,c,_ in items}
    else:
        # round-robin allocation
        per=collections.Counter(); left=b
        while left>0:
            prog=False
            for u,c,_ in items:
                if left<=0: break
                if per[u]<len(c): per[u]+=1; left-=1; prog=True
            if not prog: break
    for u,caps,tid in items:
        k=per.get(u,0)
        if k<=0: continue
        sel=caps if k>=len(caps) else [caps[int(i*len(caps)/k)] for i in range(k)]
        for c in sel:
            jobs.append({"url":u,"ts":c["ts"],"digest":c["digest"],"status":c["status"],
                         "mime":c["mime"],"cdx_len":c["len"],"target":tid,"group":g})
jobs.sort(key=lambda j:({"ONION":0,"845145127.com":1,"pastebin.com":2,"imgur.com":3}.get(j["group"],5), j["url"], j["ts"]))
json.dump(jobs,open("fetchjobs.json","w"),indent=0)
print("jobs",len(jobs))
for g,n in collections.Counter(j["group"] for j in jobs).most_common(): print(n,g)
