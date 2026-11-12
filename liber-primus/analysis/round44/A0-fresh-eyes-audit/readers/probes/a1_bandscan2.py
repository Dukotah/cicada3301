# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
import sys, math, time
import numpy as np
sys.path.insert(0,_PROBES)
from lpdata import unsolved_pages, flat
U=np.array(flat(unsolved_pages()),dtype=np.int16); N=len(U)
LMAX=6500
def zlags(x):
    n=len(x); z=np.zeros(LMAX+1)
    for L in range(2,LMAX+1):
        tot=n-L; eq=np.count_nonzero(x[L:]==x[:-L]); z[L]=(eq-tot/29)/math.sqrt(tot*28/841)
    return z
def bands(z):
    cs=np.concatenate([[0],np.cumsum(z)]); out=[]
    for L in range(2,LMAX-200):
        for mult in (2.0,4.0,6.0):
            w=max(1,int(round(mult*math.sqrt(0.028*L))))
            if L+w>LMAX: continue
            out.append(((cs[L+w]-cs[L])/math.sqrt(w),L,w))
    return out
zr=zlags(U); b=sorted(bands(zr),reverse=True)
top=[]
for s,L,w in b:
    if all(abs(L-l2)>60 for _,l2,_ in top): top.append((round(s,2),L,w))
    if len(top)>=12: break
print("REAL top non-overlapping bands (z,L,w):",top)
L0,w0=5425,25
print("coincidences in lags %d..%d:"%(L0,L0+w0-1), [int(np.count_nonzero(U[L:]==U[:-L])) for L in range(L0,L0+w0)], "expected per lag ~%.1f"%((N-L0)/29))
# calibrate with 300 surrogates
rng=np.random.default_rng(7); d=(U[1:]-U[:-1])%29; mx=[]
t=time.time()
for r in range(300):
    dd=rng.permutation(d); x=(np.concatenate([[rng.integers(29)],dd]).cumsum()%29).astype(np.int16)
    mx.append(max(bands(zlags(x)))[0])
    if time.time()-t>100: break
mx=np.array(mx); real=b[0][0]
print("surrogates",len(mx),"null band-max: mean %.3f sd %.3f  95%% %.2f  99%% %.2f  max %.2f"%(mx.mean(),mx.std(),np.quantile(mx,.95),np.quantile(mx,.99),mx.max()))
print("REAL %.2f  -> empirical p = %.4f"%(real,(1+np.count_nonzero(mx>=real))/(len(mx)+1)))
