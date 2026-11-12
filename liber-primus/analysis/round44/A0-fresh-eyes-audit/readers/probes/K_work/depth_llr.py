# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
"""EXPLORATORY: matched-filter depth test. q_d = distribution of (P1-P2) mod 29 for two independent draws from
Cicada's own solved-plaintext rune frequencies. LLR(pair) = sum log(29*q[d_i]) over aligned positions."""
import sys, itertools, math, collections
sys.path.insert(0,_PROBES)
sys.path.insert(0,_ROOT+'/liber-primus/src')
import numpy as np
from lpdata import load, TR
from lp import corpus, gematria as gp
pages={p['label']:p for p in corpus.parse()}
def idx(lbl):
    for k,p in pages.items():
        if k.startswith(lbl): return gp.runes_to_indices(p['runes'])
atb=lambda x:[28-i for i in x]
pt=[]
for l in ['05.jpg','10.jpg','13.jpg','16.jpg','74.jpg']: pt+=idx(l)
pt+=atb(idx('Runes - 01.jpg')); pt+=[(i+3)%29 for i in atb(idx('06.jpg'))]; pt+=[(i+3)%29 for i in atb(idx('09.jpg'))]
pt=np.array(pt); n=len(pt)
p=np.bincount(pt,minlength=29)/n
q=np.array([sum(p[x]*p[(x-d)%29] for x in range(29)) for d in range(29)])
print("plaintext runes",n,"sum p^2=%.4f (x29=%.3f)"%((p**2).sum(),29*(p**2).sum()))
print("theoretical English-minus-English IoC*29 = %.4f"%(29*(q**2).sum()))
print("q_d*29:",np.round(q*29,2).tolist())
# empirical: first half minus second half of the pooled plaintext
h=n//2; d=(pt[:h]-pt[h:2*h])%29; c=np.bincount(d,minlength=29); L=h
print("empirical half-vs-half IoC*29 = %.4f (L=%d)"%(29*float((c*(c-1)).sum())/(L*(L-1)),L))
PG=load(); P=[np.array([r['i'] for r in pg],dtype=np.int16) for pg in PG]
w=np.log(29*q)
# null mean/var of LLR per position under uniform d; and under depth
mu0=w.mean(); v0=w.var(); mu1=float((q*w).sum())
print("per-rune LLR: null mean %.4f sd %.4f ; depth mean %.4f  => at L=269 separation z=%.1f"%(mu0,math.sqrt(v0),mu1,(mu1-mu0)*269/math.sqrt(v0*269)))
rows=[]
for a,b in itertools.combinations(range(55),2):
    L=min(len(P[a]),len(P[b]))
    if L<100: continue
    dd=(P[a][:L]-P[b][:L])%29
    llr=float(w[dd].sum()); z=(llr-mu0*L)/math.sqrt(v0*L)
    c=np.bincount(dd,minlength=29).astype(float)
    x=float(((c-L/29)**2/(L/29)).sum())
    sx=c[1:15]; sy=c[28:14:-1]; r=float(np.corrcoef(sx,sy)[0,1])
    rq=float(np.corrcoef(c,q)[0,1])
    rows.append((z,llr,L,a,b,x,r,rq))
rows.sort(reverse=True)
zs=np.array([r[0] for r in rows]); print("pairs",len(rows),"LLR z: mean %.3f sd %.3f; expected null max ~%.2f"%(zs.mean(),zs.std(),math.sqrt(2*math.log(len(rows)))))
print("top 8 by matched-filter z: (z, L, a, b, chi2, r_sym, r_q)")
for z,llr,L,a,b,x,r,rq in rows[:8]: print("  z=%.2f L=%d seg(%d,%d) chi2=%.1f r_sym=%.2f r_q=%.2f"%(z,L,a,b,x,r,rq))
for z,llr,L,a,b,x,r,rq in rows:
    if (a,b)==(28,42): print("(28,42): matched z=%.2f rank %d chi2=%.1f r_sym=%.3f r_q=%.3f"%(z,rows.index((z,llr,L,a,b,x,r,rq))+1,x,r,rq))
rs=np.array([r[6] for r in rows]); print("r_sym over all pairs: mean %.3f sd %.3f; (28,42) percentile %.4f"%(rs.mean(),rs.std(),(rs< [r[6] for r in rows if (r[3],r[4])==(28,42)][0]).mean()))
