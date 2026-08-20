import os, hashlib, json
import gcore as G
from jpegdeep import parse_jpeg
D="/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/armada_osint/artifacts/rune_pages"
R="/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/relikd"
rel={}
for i in range(56):
    p=f"{R}/p{i}.jpg"
    rel[hashlib.sha256(open(p,'rb').read()).hexdigest()]=f"p{i}.jpg"
extra=[]
for n in range(58):
    p=f"{D}/{n}.jpg"
    if not os.path.exists(p): continue
    h=hashlib.sha256(open(p,'rb').read()).hexdigest()
    if h not in rel:
        r=parse_jpeg(p)
        extra.append({"file":f"rune_pages/{n}.jpg","sha256":h,"size":os.path.getsize(p),
          "sof":r["sof"],"ndqt":len(r["dqt"]),"trailing":r["trailing"],
          "icc_sha256":r["icc"]["sha256"] if r["icc"] else None,
          "icc_created":r["icc"]["created"] if r["icc"] else None,
          "appn":[a["ident"] for a in r["appn"]],"com":r["com"],
          "jfif":[a.get("jfif") for a in r["appn"] if a["ident"]=="JFIF"]})
print("Pages in rune_pages NOT present in data/relikd:", len(extra))
for e in extra: print(json.dumps(e, indent=1))
# ICC identical to the 56?
p0=parse_jpeg(f"{R}/p0.jpg"); print("\nrelikd p0 ICC sha256:", p0["icc"]["sha256"])
json.dump(extra, open("raw/extra_pages_not_in_relikd.json","w"), indent=1)
for e in extra:
    G.emit({"artifact_path":f"{D}/{e['file'].split('/')[-1]}","artifact_sha256":e["sha256"],
     "tool":"corpus cross-check (sha256 vs data/relikd set)","tool_version":"G-1.0",
     "command":"hash every rune_pages/*.jpg; test membership in the 56-page relikd set","params":{},
     "exit_code":0,"finding":"HIT","output_excerpt":json.dumps(e),
     "output_file":"raw/extra_pages_not_in_relikd.json",
     "note":"The repo's canonical LP page set (data/relikd, 56 files) is INCOMPLETE relative to what this repo actually holds. armada_osint/artifacts/rune_pages/ contains 58 page JPEGs; two of them have no byte-equal counterpart in data/relikd. INVENTORY.md counts 56. Any per-page analysis driven off data/relikd has silently skipped these."})
