import os, hashlib, json, collections
import gcore as G
D="/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/armada_osint/artifacts/rune_pages"
fs=sorted(os.listdir(D))
outs=[f for f in fs if f.endswith('.out')]
jpgs=[f for f in fs if f.endswith('.jpg')]
print("n .out:",len(outs)," n .jpg:",len(jpgs))
print("jpg numbers:",sorted(int(f[:-4]) for f in jpgs))
print("out numbers:",sorted(int(f[:-4]) for f in outs))
rows=[]
for f in sorted(outs, key=lambda x:int(x[:-4])):
    p=os.path.join(D,f); sz=os.path.getsize(p)
    d=open(p,'rb').read()
    rows.append({"n":int(f[:-4]),"size":sz,"sha256":hashlib.sha256(d).hexdigest() if sz else None,
      "entropy":round(G.entropy(d),4) if sz else None,
      "ascii_frac":round(sum(1 for c in d if 32<=c<127 or c in (9,10,13))/sz,4) if sz else None,
      "head_hex":d[:32].hex() if sz else None})
ne=[r for r in rows if r["size"]>0]
print("NON-EMPTY .out:",len(ne))
for r in ne: print("  ",r)
# shared-prefix analysis among non-empty
blobs={r["n"]:open(os.path.join(D,f"{r['n']}.out"),'rb').read() for r in ne}
ns=sorted(blobs)
print("\npairwise common prefix:")
import itertools
pref={}
for a,b in itertools.combinations(ns,2):
    x,y=blobs[a],blobs[b]; n=min(len(x),len(y))
    cp=next((i for i in range(n) if x[i]!=y[i]), n)
    m=sum(1 for i in range(n) if x[i]==y[i])
    pref[f"{a}|{b}"]={"common_prefix":cp,"match_pct":round(100*m/n,3),"len_a":len(x),"len_b":len(y)}
    print(f"  {a:2d}|{b:2d} prefix={cp:6d} match={100*m/n:6.3f}%")
json.dump({"rows":rows,"pairwise":pref}, open("raw/rune_pages_outguess.json","w"), indent=1)
