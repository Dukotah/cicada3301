# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
"""Comb (all-harmonics) drift-tolerant test for 'periodic key + key-skip anti-repeat filter' (the class R24-C3 killed by mechanism)."""
import sys, math, random, time
import numpy as np
sys.path.insert(0,_PROBES)
sys.path.insert(0,_ROOT+'/liber-primus/src'); sys.path.insert(0,_ROOT+'/liber-primus/analysis')
from lpdata import unsolved_pages, flat
from lp import gematria as gp
import run_stats
U=np.array(flat(unsolved_pages()),dtype=np.int16); N=len(U); LMAX=6500; R=0.0288
def zlags(x):
    n=len(x); z=np.zeros(LMAX+2)
    for L in range(2,LMAX+1):
        tot=n-L; eq=np.count_nonzero(x[L:]==x[:-L]); z[L]=(eq-tot/29)/math.sqrt(tot*28/841)
    return z
PS=list(range(50,6401))
def comb(z):
    cs=np.concatenate([[0],np.cumsum(z)]); out=np.zeros(len(PS))
    for a,p in enumerate(PS):
        s=0.0; K=0; k=1
        while True:
            c=k*p/(1+R)
            hw=2*math.sqrt(R*c)+1; lo=int(round(c-hw)); hi=int(round(c+hw))
            if hi>LMAX: break
            lo=max(lo,2); s+=(cs[hi+1]-cs[lo])/math.sqrt(hi-lo+1); K+=1; k+=1
        out[a]=s/math.sqrt(K) if K else 0
    return out
t=time.time()
cr=comb(zlags(U)); order=np.argsort(-cr)
top=[]
for a in order:
    if all(abs(PS[a]-q)>15 for _,q in top): top.append((round(float(cr[a]),2),PS[a]))
    if len(top)>=8: break
print("REAL comb max: top (S,p):",top)
rng=np.random.default_rng(11); d=(U[1:]-U[:-1])%29; mx=[]
while time.time()-t<70 and len(mx)<160:
    dd=rng.permutation(d); x=(np.concatenate([[rng.integers(29)],dd]).cumsum()%29).astype(np.int16)
    mx.append(comb(zlags(x)).max())
mx=np.array(mx)
print("null comb-max over %d surrogates: mean %.2f sd %.2f 95%% %.2f 99%% %.2f max %.2f ; REAL p=%.3f"%(len(mx),mx.mean(),mx.std(),np.quantile(mx,.95),np.quantile(mx,.99),mx.max(),(1+np.count_nonzero(mx>=cr.max()))/(len(mx)+1)))
P=np.array(gp.keyword_to_indices(run_stats._english_from_quadgrams(60000))[:N],dtype=np.int16)
def plant(p,seed,supp=0.83):
    r=random.Random(seed); K=[r.randrange(29) for _ in range(p)]; out=[]; j=0; prev=-1
    for x in P:
        while True:
            c=(int(x)+K[j%p])%29
            if c==prev and r.random()<supp: j+=1; continue
            break
        out.append(c); prev=c; j+=1
    return np.array(out,dtype=np.int16)
thr=np.quantile(mx,.95)
for p in (400,800,1200,1500,2000,2500,3000,4000):
    res=[]
    for s in range(4):
        c=comb(zlags(plant(p,77*p+s))); a=int(c.argmax()); res.append((round(float(c.max()),1),PS[a]))
    print(f"PLANT p={p}: (S,argp) {res}  detect@95%: {sum(v>thr for v,_ in res)}/4")
print("elapsed %.0fs"%(time.time()-t))
