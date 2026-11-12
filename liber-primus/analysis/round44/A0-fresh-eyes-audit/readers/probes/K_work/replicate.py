# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
import sys, itertools, math
import numpy as np
from lpdata import load, TR
PG=load(); P=[np.array([r['i'] for r in pg],dtype=np.int16) for pg in PG]
def fold(dd):
    c=np.bincount(dd,minlength=29).astype(float); return np.concatenate([[2*c[0]],c[1:15]+c[28:14:-1]])  # 2*c0 so all bins have equal null expectation
L=269; d=(P[28][:L]-P[42][:L])%29
F=fold(d); print("folded (28,42):",F.astype(int).tolist(), "(bin0 doubled)")
# (a) internal replication
h1,h2=fold(d[:L//2]),fold(d[L//2:]); print("first half :",h1.astype(int).tolist()); print("second half:",h2.astype(int).tolist()); print("corr halves = %.3f"%np.corrcoef(h1,h2)[0,1])
o,e=fold(d[0::2]),fold(d[1::2]); print("corr odd/even = %.3f"%np.corrcoef(o,e)[0,1])
t=[fold(d[i::3]) for i in range(3)]; print("corr thirds: %.3f %.3f %.3f"%(np.corrcoef(t[0],t[1])[0,1],np.corrcoef(t[0],t[2])[0,1],np.corrcoef(t[1],t[2])[0,1]))
# null distribution of split-half correlation for random pairs
rng=np.random.default_rng(7); cs=[]
for a,b in itertools.combinations(range(55),2):
    LL=min(len(P[a]),len(P[b]))
    if LL<200 or (a,b)==(28,42): continue
    dd=(P[a][:LL]-P[b][:LL])%29; cs.append(float(np.corrcoef(fold(dd[:LL//2]),fold(dd[LL//2:]))[0,1]))
cs=np.array(cs); print("null split-half corr over %d pairs: mean %.3f sd %.3f; frac >= obs: %.4f"%(len(cs),cs.mean(),cs.std(),(cs>=np.corrcoef(h1,h2)[0,1]).mean()))
# (b) third pages: matched filter with the (28,42)-learned folded shape, leave-one-out not possible; score other pairs involving 28 or 42 and all pairs
w=np.log((F+1)/((F+1).sum()/15))   # smoothed log-ratio weights per folded bin (bin0 already doubled)
def score(dd):
    c=np.bincount(dd,minlength=29).astype(float); f=np.concatenate([[c[0]],c[1:15]+c[28:14:-1]]); return float((f*w).sum())
# null calibration per length: mean/var per rune
probs=np.concatenate([[1/29],np.full(14,2/29)]); mu=float((probs*w).sum()); var=float((probs*w*w).sum()-mu*mu)
rows=[]
for a,b in itertools.combinations(range(55),2):
    for off in range(-3,4):
        A=P[a][max(0,off):]; B=P[b][max(0,-off):]; LL=min(len(A),len(B))
        if LL<100: continue
        s=score((A[:LL]-B[:LL])%29); rows.append(((s-mu*LL)/math.sqrt(var*LL),a,b,off,LL))
rows.sort(reverse=True)
zs=np.array([r[0] for r in rows]); print("shape-matched scan over %d (pair,offset) cells: z mean %.3f sd %.3f"%(len(rows),zs.mean(),zs.std()))
print("top 10:",[(round(z,2),a,b,off) for z,a,b,off,LL in rows[:10]])
print("cells involving seg 28 or 42 in top 40:",[(round(z,2),a,b,off) for z,a,b,off,LL in rows[:40] if a in (28,42) or b in (28,42)])
