# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
"""EXPLORATORY: folded (|d|) chi2 scan, 14 df, for all page pairs at offset 0 (the a-priori depth statistic when the
plaintext distribution is unknown: difference of two iid draws is symmetric)."""
import sys, itertools, math
import numpy as np
from lpdata import load, TR
PG=load(); P=[np.array([r['i'] for r in pg],dtype=np.int16) for pg in PG]
def sf14(x):  # chi2 sf, 14 df
    s=0.0; term=1.0
    for i in range(7):
        if i>0: term*=(x/2)/i
        s+=term
    return math.exp(-x/2)*s
def folded(dd):
    L=len(dd); c=np.bincount(dd,minlength=29).astype(float)
    f=np.concatenate([[c[0]],c[1:15]+c[28:14:-1]]); e=np.concatenate([[L/29],np.full(14,2*L/29)])
    sym=float(((f-e)**2/e).sum())
    anti=float((((c[1:15]-c[28:14:-1])**2)/(c[1:15]+c[28:14:-1]+1e-9)).sum())
    return sym,anti,f
rows=[]
for a,b in itertools.combinations(range(55),2):
    L=min(len(P[a]),len(P[b]))
    if L<100: continue
    sym,anti,f=folded((P[a][:L]-P[b][:L])%29); rows.append((sf14(sym),sym,anti,L,a,b))
rows.sort()
print("pairs:",len(rows))
for p,sym,anti,L,a,b in rows[:6]: print("  p=%.2e folded-chi2=%.1f antisym-chi2=%.1f L=%d seg(%d,%d) bonf=%.2e"%(p,sym,anti,L,a,b,min(1,p*len(rows))))
ps=np.array([r[0] for r in rows]); print("p-value calibration: frac p<0.05=%.3f p<0.01=%.4f p<0.001=%.4f"%((ps<0.05).mean(),(ps<0.01).mean(),(ps<0.001).mean()))
# same scan with SUMS as a control family (no symmetry expected)
rows2=[]
for a,b in itertools.combinations(range(55),2):
    L=min(len(P[a]),len(P[b]))
    if L<100: continue
    sym,anti,f=folded((P[a][:L]+P[b][:L])%29); rows2.append((sf14(sym),sym,L,a,b))
rows2.sort(); print("control (sums) best:",["p=%.1e (%d,%d)"%(r[0],r[3],r[4]) for r in rows2[:3]])
# offsets -3..3 scan for all pairs
best=[]
for a,b in itertools.combinations(range(55),2):
    for off in (-3,-2,-1,1,2,3):
        A=P[a][max(0,off):]; B=P[b][max(0,-off):]; L=min(len(A),len(B))
        if L<100: continue
        sym,anti,f=folded((A[:L]-B[:L])%29); best.append((sf14(sym),sym,L,a,b,off))
best.sort(); print("offset scan (+-1..3), n=%d, best:"%len(best),["p=%.1e (%d,%d,off %d)"%(r[0],r[3],r[4],r[5]) for r in best[:4]])
# multiplier analysis for (28,42): correlate folded hist with English q under d->m*d
sys.path.insert(0,_ROOT+'/liber-primus/src')
from lp import corpus, gematria as gp
pages={p['label']:p for p in corpus.parse()}
def idx(lbl):
    for k,p in pages.items():
        if k.startswith(lbl): return gp.runes_to_indices(p['runes'])
atb=lambda x:[28-i for i in x]
pt=[]
for l in ['05.jpg','10.jpg','13.jpg','16.jpg','74.jpg']: pt+=idx(l)
pt+=atb(idx('Runes - 01.jpg')); pt+=[(i+3)%29 for i in atb(idx('06.jpg'))]; pt+=[(i+3)%29 for i in atb(idx('09.jpg'))]
p=np.bincount(np.array(pt),minlength=29)/len(pt)
q=np.array([sum(p[x]*p[(x-d)%29] for x in range(29)) for d in range(29)])
L=269; dd=(P[28][:L]-P[42][:L])%29; c=np.bincount(dd,minlength=29).astype(float)
res=[]
for m in range(1,15):
    qm=np.zeros(29)
    for d in range(29): qm[(m*d)%29]=q[d]
    res.append((round(float(np.corrcoef(c[1:],qm[1:])[0,1]),3),m))
print("corr(observed nonzero-diff hist, English q under multiplier m):",sorted(res,reverse=True)[:5])
