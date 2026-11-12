# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
import sys, math, itertools, collections
import numpy as np
from lpdata import load, TR
PG=load()
def lines(pg):
    out=[[]]
    for k,r in enumerate(pg):
        if k>0 and '/' in r['pre']: out.append([])
        out[-1].append(r['i'])
    return out
def chi(c,L,e=None):
    c=np.asarray(c,float); return float(((c-L/29)**2/(L/29)).sum())
def foldchi(d):
    L=len(d); c=np.bincount(np.array(d)%29,minlength=29).astype(float)
    f=np.concatenate([[c[0]],c[1:15]+c[28:14:-1]]); e=np.concatenate([[L/29],np.full(14,2*L/29)]); return float(((f-e)**2/e).sum()), chi(c,L), L
a,b=28,42
LA,LB=lines(PG[a]),lines(PG[b])
print("line lengths A:",[len(x) for x in LA]); print("line lengths B:",[len(x) for x in LB])
# per-line stats at PAGE alignment (offset 0): which lines carry the signal?
A=[r['i'] for r in PG[a]]; B=[r['i'] for r in PG[b]]; L=min(len(A),len(B))
pos=0
for n,ln in enumerate(LA):
    seg=[(A[i]-B[i])%29 for i in range(pos,min(pos+len(ln),L))]
    S={0,2,3,5,6,27,26,24,23}
    print("  line %2d pos %3d-%3d: in-set(0,+-2,3,5,6) %2d/%2d (exp %.1f)  zeros %d"%(n,pos,pos+len(ln)-1,sum(1 for v in seg if v in S),len(seg),len(seg)*9/29,seg.count(0)))
    pos+=len(ln)
# line-aligned (left) and right-aligned pooled difference
dl=[];dr=[]
for x,y in zip(LA,LB):
    m=min(len(x),len(y)); dl+=[(x[i]-y[i])%29 for i in range(m)]; dr+=[(x[-1-i]-y[-1-i])%29 for i in range(m)]
print("line-left-aligned: folded chi2=%.1f chi2=%.1f L=%d"%foldchi(dl)); print("line-right-aligned: folded chi2=%.1f chi2=%.1f L=%d"%foldchi(dr))
# running "in-set" indicator along the page: runs
S={0,2,3,5,6,27,26,24,23}
ind=''.join('#' if ((A[i]-B[i])%29) in S else '.' for i in range(L)); print(ind)
# set-membership enrichment: is the in-set fraction uniform along the page? chi2 over 9 blocks of 30
blk=[ind[i:i+30].count('#') for i in range(0,L,30)]; print("in-set counts per 30-rune block:",blk,"(exp %.1f)"%(30*9/29))
