# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
"""Power table: periodic key + key-skip (83%) filter over fresh English-in-runes; rigid single-lag (Campaign XIV P1 style) vs lag-band scan."""
import sys, math, random
import numpy as np
sys.path.insert(0,_ROOT+'/liber-primus/src'); sys.path.insert(0,_ROOT+'/liber-primus/analysis')
from lp import gematria as gp
import run_stats
N=12956; LMAX=6500
P=np.array(gp.keyword_to_indices(run_stats._english_from_quadgrams(60000))[:N],dtype=np.int16)
assert len(P)==N
def zlags(x):
    n=len(x); z=np.zeros(LMAX+1)
    for L in range(2,LMAX+1):
        tot=n-L; eq=np.count_nonzero(x[L:]==x[:-L]); z[L]=(eq-tot/29)/math.sqrt(tot*28/841)
    return z
def bandmax(z):
    cs=np.concatenate([[0],np.cumsum(z)]); best=-9
    for L in range(2,LMAX-200):
        for mult in (2.0,4.0,6.0):
            w=max(1,int(round(mult*math.sqrt(0.028*L))))
            if L+w<=LMAX:
                s=(cs[L+w]-cs[L])/math.sqrt(w)
                if s>best: best=s
    return best
def plant(p,seed,supp=0.83,skip=True):
    r=random.Random(seed); K=[r.randrange(29) for _ in range(p)]; out=[]; j=0; prev=-1
    for x in P:
        while True:
            c=(int(x)+K[j%p])%29
            if c==prev and r.random()<supp:
                if skip: j+=1; continue
                else: c=(int(x)+r.randrange(29))%29   # rewrite: resample in place, key stays synced
            break
        out.append(c); prev=c; j+=1
    return np.array(out,dtype=np.int16)
print("null (from earlier 300 surrogates): band-max 95%=4.11 99%=4.46 ; single-lag 5-sigma rule as in Campaign XIV P1")
print("period | key-SKIP: single-lag max z (5 seeds) | band max z (5 seeds) | detect@95%(band) | P1 >5sigma hits")
for p in (41,60,100,200,400,800,1200,1500,2000,3000):
    sl=[];bm=[]
    for s in range(5):
        z=zlags(plant(p,1000*p+s)); sl.append(z[2:].max()); bm.append(bandmax(z))
    print(f"{p:6d} | {' '.join('%.1f'%v for v in sl)} | {' '.join('%.1f'%v for v in bm)} | {sum(v>4.11 for v in bm)}/5 | {sum(v>5 for v in sl)}/5")
z=zlags(plant(800,5,skip=False)); print("control: period 800 with REWRITE filter (no desync): single-lag max z=%.1f at L=%d"%(z[2:].max(),int(z[2:].argmax())+2))
