# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
import sys, math, itertools
import numpy as np
from lpdata import load
sys.path.insert(0,_ROOT+'/liber-primus/src')
from lp import corpus, gematria as gp
PG=load(); P=[np.array([r['i'] for r in pg],dtype=np.int64) for pg in PG]
L=269; d=(P[28][:L]-P[42][:L])%29
c=np.bincount(d,minlength=29)/L
k=np.arange(1,15)
def spec(c): return np.array([sum(c[x]*math.cos(2*math.pi*kk*x/29) for x in range(29)) for kk in k]), np.array([sum(c[x]*math.sin(2*math.pi*kk*x/29) for x in range(29)) for kk in k])
re,im=spec(c); sd=math.sqrt(1/(2*L))
print("noise sd per coefficient under null: %.3f"%sd)
print("Re q^_k (k=1..14):",np.round(re,3).tolist())
print("Im q^_k (k=1..14):",np.round(im,3).tolist())
print("Re in sd units:",np.round(re/sd,1).tolist())
print("n negative Re: %d of 14; sum Re^2=%.4f sum Im^2=%.4f (null exp each %.4f)"%((re<0).sum(),(re**2).sum(),(im**2).sum(),14/(2*L)))
# English spectrum (Cicada solved plaintext)
pages={p['label']:p for p in corpus.parse()}
def idx(lbl):
    for kx,p in pages.items():
        if kx.startswith(lbl): return gp.runes_to_indices(p['runes'])
atb=lambda x:[28-i for i in x]
pt=[]
for l in ['05.jpg','10.jpg','13.jpg','16.jpg','74.jpg']: pt+=idx(l)
pt+=atb(idx('Runes - 01.jpg')); pt+=[(i+3)%29 for i in atb(idx('06.jpg'))]; pt+=[(i+3)%29 for i in atb(idx('09.jpg'))]
p=np.bincount(np.array(pt),minlength=29)/len(pt)
pr,pi=spec(p); pw=pr**2+pi**2
print("English |p^_k|^2 (k=1..14):",np.round(pw,3).tolist(), "sum=%.3f"%pw.sum())
# best frequency permutation k->m*k matching observed Re spectrum to English power
res=[]
for m in range(1,15):
    perm=[min((m*kk)%29,29-(m*kk)%29)-1 for kk in k]   # index of English freq that lands on k after multiplier
    res.append((round(float(np.corrcoef(re,pw[perm])[0,1]),3),m))
print("corr(observed Re spectrum, English power under freq multiplier m):",sorted(res,reverse=True)[:5])
# positivity test null distribution: for random pairs, statistic = min Re / sd and count negatives; compare
stats=[]
for a,b in itertools.combinations(range(55),2):
    LL=min(len(P[a]),len(P[b]))
    if LL<200: continue
    cc=np.bincount((P[a][:LL]-P[b][:LL])%29,minlength=29)/LL; r,_=spec(cc); stats.append(((r<0).sum(), float(r.sum()/math.sqrt(14/(2*LL))),a,b))
neg=np.array([s[0] for s in stats]); tot=np.array([s[1] for s in stats])
print("null pairs: mean #negative Re = %.2f; sum-Re z: mean %.2f sd %.2f max %.2f; (28,42) sumRe z = %.2f"%(neg.mean(),tot.mean(),tot.std(),tot.max(),re.sum()/math.sqrt(14/(2*L))))
