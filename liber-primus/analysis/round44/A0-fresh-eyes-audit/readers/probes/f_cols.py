# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
import math, collections, sys, random
sys.path.insert(0,_PROBES)
from lpdata import *
RUN="ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
txt=open(REPO+'/data/krisyotam_runes.txt',encoding='utf-8').read()
segs=[s for s in txt.split('%') if any(c in RUN for c in s)][:-2]
lines=[]   # (page, lineno, [idx])
for pi,s in enumerate(segs):
    cur=[]; ln=0
    for c in s:
        if c in RUN: cur.append(RUN.index(c))
        elif c=='/':
            if cur: lines.append((pi,ln,cur)); cur=[]; ln+=1
    if cur: lines.append((pi,ln,cur))
print("lines",len(lines), "len dist", sorted(collections.Counter(len(l[2]) for l in lines).items()))
N=sum(len(l[2]) for l in lines)
glob=collections.Counter(x for l in lines for x in l[2])
def colstat(sel, maxc=24, rev=False):
    out=[]
    for c in range(maxc):
        col=[(l[2][::-1] if rev else l[2])[c] for l in sel if len(l[2])>c]
        n=len(col); cnt=collections.Counter(col)
        chi=sum((cnt.get(r,0)-n*glob[r]/N)**2/(n*glob[r]/N) for r in range(29))
        pairs=n*(n-1)/2; eq=sum(v*(v-1)/2 for v in cnt.values())
        z=(eq-pairs/29)/math.sqrt(pairs*(1/29)*(28/29))
        top=sorted(((cnt.get(r,0)-n/29)/math.sqrt(n/29*28/29),TR[r],cnt.get(r,0)) for r in range(29))
        out.append((c,n,round(chi,1),round(z,2),[(t[1],t[2],round(t[0],1)) for t in top[-2:]],[(t[1],t[2],round(t[0],1)) for t in top[:2]]))
    return out
print("column  n  chi2(28df)  kappa-z   top-over   top-under   [all lines, from line start]")
for r in colstat(lines,24): print(r)
print("--- from line END (reverse)")
for r in colstat(lines,6,True): print(r)
