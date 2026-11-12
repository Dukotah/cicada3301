# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
"""EXPLORATORY: under 'depth with a mixed plaintext alphabet' (C = pi(P) + K), d = pi(Pa)-pi(Pb).
(1) fixed natural maps; (2) hill-climb pi on unigram likelihood, calibrated against control pairs."""
import sys, math, itertools, random, time
import numpy as np
from lpdata import load, PRIMES
sys.path.insert(0,_ROOT+'/liber-primus/src')
from lp import corpus, gematria as gp
PG=load(); P=[np.array([r['i'] for r in pg],dtype=np.int64) for pg in PG]
pages={p['label']:p for p in corpus.parse()}
def idx(lbl):
    for kx,p in pages.items():
        if kx.startswith(lbl): return gp.runes_to_indices(p['runes'])
atb=lambda x:[28-i for i in x]
pt=[]
for l in ['05.jpg','10.jpg','13.jpg','16.jpg','74.jpg']: pt+=idx(l)
pt+=atb(idx('Runes - 01.jpg')); pt+=[(i+3)%29 for i in atb(idx('06.jpg'))]; pt+=[(i+3)%29 for i in atb(idx('09.jpg'))]
p=np.bincount(np.array(pt),minlength=29)/len(pt)
def qmap(pi):
    q=np.zeros(29)
    for x in range(29):
        for y in range(29): q[(pi[x]-pi[y])%29]+=p[x]*p[y]
    return q
def llr(c,pi):
    q=qmap(pi); return float((c*np.log(29*np.maximum(q,1e-9))).sum())
def hist(a,b):
    L=min(len(P[a]),len(P[b])); return np.bincount((P[a][:L]-P[b][:L])%29,minlength=29).astype(float),L
c,L=hist(28,42)
maps={'index':list(range(29)),'prime mod 29':[x%29 for x in PRIMES],'totient mod 29':[(x-1)%29 for x in PRIMES],
      'prime mod 28':[x%28 for x in PRIMES]}
for n,pi in maps.items(): print("map %-16s LLR=%.2f corr=%.3f"%(n,llr(c,pi),np.corrcoef(c,qmap(pi))[0,1]))
def climb(c,seed,iters=4000):
    rng=random.Random(seed); pi=list(range(29)); rng.shuffle(pi); best=llr(c,pi)
    for t in range(iters):
        i,j=rng.sample(range(29),2); pi[i],pi[j]=pi[j],pi[i]; v=llr(c,pi)
        if v>=best: best=v
        else: pi[i],pi[j]=pi[j],pi[i]
    return best,pi
t=time.time()
b1=max(climb(c,s,2500) for s in range(3))
print("(28,42) best mixed-alphabet unigram LLR over 3 restarts: %.2f  (%.0fs)"%(b1[0],time.time()-t))
ctrl=[]
rng=random.Random(5)
prs=[pr for pr in itertools.combinations(range(55),2) if min(len(P[pr[0]]),len(P[pr[1]]))>=255 and pr!=(28,42)]
for pr in rng.sample(prs,10):
    cc,LL=hist(*pr); ctrl.append(max(climb(cc,s,2500) for s in range(2))[0]*269/LL)
    if time.time()-t>120: break
print("control pairs best LLR (scaled to L=269):",np.round(ctrl,2).tolist()," mean %.2f sd %.2f"%(np.mean(ctrl),np.std(ctrl)))
print("best pi for (28,42) [rune index -> value]:",b1[1])
