# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
"""Depth test allowing a per-unit ADDITIVE constant: if every page restarts the same positional keystream K_j but adds a
page constant o_p (the R11-N5 'per-segment, best offset per page' mode, for ANY generator), then for a page pair (p,q)
D_j = C_p[j]-C_q[j] = (P_p[j]-P_q[j]) + const for early columns -> coincidences among {D_j} exceed 1/29.
Statistic: pooled over unit pairs, # of column pairs (j<k<W) with D_j == D_k.  Null: 1/29 (verified by shuffled-unit MC).
Power: plant English (quadgram-Markov) under one shared random keystream + per-page constants + soft key-skip filter."""
import sys, math, random, collections
sys.path.insert(0,'.'); sys.path.insert(0,_ROOT+'/liber-primus/src'); sys.path.insert(0,_ROOT+'/liber-primus/analysis')
from lpdata import *
P=[[r['i'] for r in p] for p in unsolved_pages()]
def stat(U,W):
    H=[u[:W] for u in U if len(u)>=W]
    tot=co=0
    for a in range(len(H)):
        for b in range(a+1,len(H)):
            D=[(x-y)%29 for x,y in zip(H[a],H[b])]
            c=collections.Counter(D); co+=sum(v*(v-1)//2 for v in c.values()); tot+=W*(W-1)//2
    return tot,co
def z(tot,co): return (co-tot/29)/math.sqrt(tot/29*28/29)
for W in (8,12,16,24,40):
    t,c=stat(P,W); print(f"REAL pages W={W:2d}: pairs {t:8d} coinc {c:7d} rate {c/t:.4f} z={z(t,c):+.2f}")
# plant for power
import run_stats
from lp import gematria as gp
eng=gp.keyword_to_indices(run_stats._english_from_quadgrams(70000))
rng=random.Random(7)
def plant(keep=0.1925):
    K=[rng.randrange(29) for _ in range(2000)]   # one shared positional keystream
    out=[];a=0
    for p in P:
        o=rng.randrange(29); pt=eng[a:a+len(p)]; a+=len(p); j=0; c=[]; prev=None
        for x in pt:
            while True:
                y=(x+K[j]+o)%29; j+=1
                if y!=prev or rng.random()<keep: break
            c.append(y); prev=y
        out.append(c)
    return out
for W in (8,12,16,24):
    zs=[]
    for _ in range(5):
        t,c=stat(plant(),W); zs.append(z(t,c))
    print(f"PLANT (shared stream + per-page const + key-skip) W={W:2d}: z = {[round(v,1) for v in zs]}")
