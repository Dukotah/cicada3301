# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
"""A1 audit: drift-tolerant periodicity / key-reuse scan (lag-BAND coincidence), with planted positive controls.
Tests the class Round 24 C3 killed 'by mechanism': long-period periodic key + key-skip anti-repeat filter."""
import sys, math, random, time
import numpy as np
sys.path.insert(0,_PROBES)
sys.path.insert(0,_ROOT+'/liber-primus/src'); sys.path.insert(0,_ROOT+'/liber-primus/analysis')
from lpdata import unsolved_pages, flat
U=np.array(flat(unsolved_pages()),dtype=np.int16); N=len(U)
LMAX=6500
def zlags(x):
    n=len(x); z=np.zeros(LMAX+1)
    for L in range(2,LMAX+1):
        tot=n-L; eq=np.count_nonzero(x[L:]==x[:-L]); z[L]=(eq-tot/29)/math.sqrt(tot*28/841)
    return z
def band_stat(z):
    """max over L of standardized sum of z over a band [L, L+w) with w ~ 4*sqrt(0.028 L) (>=1). Returns (max, argL, w)."""
    cs=np.concatenate([[0],np.cumsum(z)])
    best=(-9,0,0)
    for L in range(2,LMAX-200):
        for mult in (2.0,4.0,6.0):
            w=max(1,int(round(mult*math.sqrt(0.028*L))))
            if L+w>LMAX: continue
            s=(cs[L+w]-cs[L])/math.sqrt(w)
            if s>best[0]: best=(s,L,w)
    return best
t=time.time()
zr=zlags(U); br=band_stat(zr)
print("REAL: max single-lag z=%.2f at L=%d ; max band z=%.2f at L=%d w=%d  (%.1fs)"%(zr[2:].max(),int(zr[2:].argmax())+2,br[0],br[1],br[2],time.time()-t))
# null: delta-shuffle surrogates (keep doublet count)
rng=np.random.default_rng(3301)
d=(U[1:]-U[:-1])%29
nullmax=[]; nullsingle=[]
for r in range(40):
    dd=rng.permutation(d); x=np.concatenate([[rng.integers(29)],dd]).cumsum()%29
    z=zlags(x.astype(np.int16)); nullmax.append(band_stat(z)[0]); nullsingle.append(z[2:].max())
nullmax=np.array(nullmax)
print("NULL (40 surrogates): band max mean %.2f sd %.2f max %.2f ; single-lag max mean %.2f max %.2f"%(nullmax.mean(),nullmax.std(),nullmax.max(),np.mean(nullsingle),np.max(nullsingle)))
print("REAL band max percentile vs null: %.2f"%( (nullmax<br[0]).mean() ))
# positive controls: periodic key + keyskip filter over English-in-runes
from lp import gematria as gp
from run_stats import english_baseline
eng=english_baseline()
P=np.array((list(eng)*(N//len(eng)+2))[:N],dtype=np.int16) if not isinstance(eng,str) else None
if P is None:
    idx=gp.runes_to_indices(eng) if hasattr(gp,'runes_to_indices') else None
print("english_baseline type",type(eng), (len(eng) if hasattr(eng,'__len__') else ''))
def plant(P,p,supp=0.83,seed=1):
    r=random.Random(seed); K=[r.randrange(29) for _ in range(p)]; out=[]; j=0; prev=-1; skips=0
    for x in P:
        while True:
            c=(int(x)+K[j%p])%29
            if c==prev and r.random()<supp: j+=1; skips+=1; continue
            break
        out.append(c); prev=c; j+=1
    return np.array(out,dtype=np.int16),skips
if P is not None:
    for p in (400,800,1500,3000,5000):
        x,sk=plant(P,p,seed=p); z=zlags(x); b=band_stat(z)
        dbl=np.count_nonzero(x[1:]==x[:-1])/len(x)
        print("PLANT period %5d: skips %d doublet%% %.2f  max single z=%.2f@%d  band z=%.2f at L=%d w=%d  -> %s"%(p,sk,100*dbl,z[2:].max(),int(z[2:].argmax())+2,b[0],b[1],b[2],"DETECTED" if b[0]>nullmax.max() else "missed"))
