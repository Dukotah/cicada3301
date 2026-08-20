import os, json, glob, collections
tgt={}
for l in open("targets.tsv",encoding="utf-8"):
    p=l.rstrip("\n").split("\t"); tgt[p[0]]=(p[1],p[2],p[3])
timeline={}; summary=[]
for f in sorted(glob.glob("cdx/*.json")):
    tid=os.path.basename(f)[:-5]
    try: rows=json.load(open(f,encoding="utf-8",errors="replace"))
    except Exception: continue
    if not rows or len(rows)<2: 
        summary.append((tid,0,"","")); continue
    hdr=rows[0]; recs=rows[1:]
    byurl=collections.defaultdict(list)
    for r in recs:
        d=dict(zip(hdr,r))
        byurl[d["original"]].append({"ts":d["timestamp"],"status":d.get("statuscode"),
            "digest":d.get("digest"),"mime":d.get("mimetype"),"len":d.get("length")})
    for u,v in byurl.items():
        v.sort(key=lambda x:x["ts"])
        timeline.setdefault(u,{"target":tid,"query":tgt.get(tid,("","",""))[0],
            "label":tgt.get(tid,("","",""))[2],"captures":[]})["captures"].extend(v)
    ts=[d["ts"] for u in byurl for d in byurl[u]]
    summary.append((tid,len(recs),min(ts),max(ts)))
for u in timeline:
    timeline[u]["captures"].sort(key=lambda x:x["ts"])
    timeline[u]["n_distinct_digests"]=len({c["digest"] for c in timeline[u]["captures"]})
json.dump(timeline,open("TIMELINE.json","w",encoding="utf-8"),indent=1)
print("urls:",len(timeline),"captures:",sum(len(v['captures']) for v in timeline.values()))
open("logs/cdx_summary.tsv","w",encoding="utf-8").write("\n".join(f"{a}\t{b}\t{c}\t{d}" for a,b,c,d in summary))
# report: URLs with most distinct digests
top=sorted(timeline.items(),key=lambda kv:-kv[1]["n_distinct_digests"])[:40]
for u,v in top: print(v["n_distinct_digests"],u)
