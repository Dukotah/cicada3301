import hashlib, json, os, sys
ROOT = "/mnt/c/Users/dukot/projects/cicada3301"
targets = []
def add(p, cls):
    if os.path.isfile(p): targets.append((p, cls))
# LP pages
for i in range(56):
    add(f"{ROOT}/liber-primus/data/relikd/p{i}.jpg", "lp_page")
# pads
padd = f"{ROOT}/liber-primus/analysis/round12/A1/pads"
if os.path.isdir(padd):
    for f in sorted(os.listdir(padd)):
        add(os.path.join(padd,f), "cicadaos_pad")
# mp3
add(f"{ROOT}/puzzles/2013/artifacts/761_The-Instar-Emergence.mp3", "audio_2013")
# onion artifacts (recursive)
ad = f"{ROOT}/liber-primus/analysis/armada_osint/artifacts"
for dp,dn,fn in os.walk(ad):
    for f in sorted(fn): add(os.path.join(dp,f), "onion_artifact")
# onion html
od = f"{ROOT}/liber-primus/analysis/armada_osint/onions_ibotpeaches"
for dp,dn,fn in os.walk(od):
    for f in sorted(fn): add(os.path.join(dp,f), "onion_html")
out=[]
for p,cls in targets:
    h=hashlib.sha256()
    with open(p,'rb') as fh:
        for chunk in iter(lambda: fh.read(1<<20), b''): h.update(chunk)
    out.append({"path":p,"class":cls,"size":os.path.getsize(p),"sha256":h.hexdigest()})
json.dump(out, open("TARGETS.json","w"), indent=1)
print(len(out),"targets hashed")
from collections import Counter
print(Counter(t['class'] for t in out))
