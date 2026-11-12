# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
"""EXPLORATORY (not pre-registered): are LP2 pages XOR-style shares of each other?
2014 precedent: three signed 991-byte blobs XOR -> signed message. Test all pairs (a+-b) and triples (a+-b+-c)
of the 57 segments at rune-offset 0, IoC*29 of the combined stream over the common length. Plant control included."""
import sys, itertools, math, random, time
sys.path.insert(0,_PROBES)
import numpy as np
from lpdata import load
P=[np.array([r['i'] for r in p],dtype=np.int16) for p in load()]
n=len(P)
def ioc29(x):
    L=len(x); c=np.bincount(x,minlength=29).astype(float)
    return 29*float((c*(c-1)).sum())/(L*(L-1))
def z(v,L): return (v-1.0)/(math.sqrt(2*28)/L)
t=time.time()
best=[]
# pairs
for a,b in itertools.combinations(range(n),2):
    L=min(len(P[a]),len(P[b]))
    if L<60: continue
    for s in (1,-1):
        v=ioc29((P[a][:L]+s*P[b][:L])%29); best.append((z(v,L),v,L,(a,b),(s,)))
npair=len(best)
for a,b,c in itertools.combinations(range(n),3):
    L=min(len(P[a]),len(P[b]),len(P[c]))
    if L<60: continue
    A=P[a][:L];B=P[b][:L];C=P[c][:L]
    for s1,s2 in ((1,1),(1,-1),(-1,1),(-1,-1)):
        v=ioc29((A+s1*B+s2*C)%29); best.append((z(v,L),v,L,(a,b,c),(s1,s2)))
best.sort(reverse=True)
print("tests: pairs",npair,"triples",len(best)-npair,"time %.1fs"%(time.time()-t))
print("top 8:",[(round(x[0],2),round(x[1],3),x[2],x[3],x[4]) for x in best[:8]])
zs=np.array([x[0] for x in best]); print("z mean %.3f sd %.3f max %.2f; expected null max ~ %.1f"%(zs.mean(),zs.std(),zs.max(),math.sqrt(2*math.log(len(zs)))))
# positive control: plant plaintext-like stream as sum of three random shares
rng=np.random.default_rng(3301)
pt=P[-1]  # PARABLE plaintext page (95 runes) as an English-rune sample
L=len(pt); a=rng.integers(0,29,L); b=rng.integers(0,29,L); c=(pt-a-b)%29
v=ioc29((a+b+c)%29); print("plant control: IoC*29=%.3f z=%.1f at L=%d"%(v,z(v,L),L))
