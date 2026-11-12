# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
"""Null calibration for the full-harmonic drift-aware periodicity detector, p in [50,2000] (vectorised weights)."""
import sys, math, random, time
import numpy as np
sys.path.insert(0,_PROBES)
from lpdata import *
RUN="ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
txt=open(REPO+'/data/krisyotam_runes.txt',encoding='utf-8').read()
segs=[s for s in txt.split('%') if any(c in RUN for c in s)][:-2]
C=np.array([RUN.index(c) for s in segs for c in s if c in RUN]); N=len(C); M=N-60
LAM=373.6/12956
LG=np.array([math.lgamma(k+1) for k in range(3000)])
def weights(p,lam=LAM):
    Ls=[];Ws=[];h=1
    while True:
        mu=lam*p*h; lo=max(0,int(mu-5*math.sqrt(mu)-3)); hi=int(mu+5*math.sqrt(mu)+3)
        if p*h-hi>M: break
        ks=np.arange(lo,hi+1); L=p*h-ks; ok=(L>=2)&(L<=M)
        w=np.exp(-mu+ks*math.log(mu)-LG[ks])
        Ls.append(L[ok]); Ws.append(w[ok]); h+=1
    return np.concatenate(Ls),np.concatenate(Ws)
PS=list(range(50,2001))
t=time.time(); WT=[weights(p) for p in PS]; print("weights built %.1fs, terms %d"%(time.time()-t,sum(len(a) for a,_ in WT)),flush=True)
T=np.array([0,0]+[N-L for L in range(2,M+1)],dtype=float); V=T*(1/29)*(28/29)
DEN=np.array([math.sqrt(np.sum(w*w*V[L])) for L,w in WT])
def zs(Cx):
    D=np.zeros(M+1)
    for L in range(2,M+1): D[L]=np.count_nonzero(Cx[L:]==Cx[:-L])-T[L]/29.0
    return np.array([np.dot(w,D[L]) for L,w in WT])/DEN
zr=zs(C); o=np.argsort(-zr)[:6]
print("REAL: max",[(PS[i],round(float(zr[i]),2)) for i in o], "sd %.3f"%zr.std(),flush=True)
mx=[]; rng=np.random.default_rng(3301)
for rep in range(200):
    S=C.copy(); rng.shuffle(S); zn=zs(S); mx.append(float(zn.max()))
    if rep in (19,49,99,199):
        a=np.sort(mx); print(f"NULL n={rep+1}: median max {np.median(a):.2f} q90 {np.quantile(a,.9):.2f} q95 {np.quantile(a,.95):.2f} max {a[-1]:.2f}; P(max>=real {zr.max():.2f}) = {np.mean(a>=zr.max()):.3f}",flush=True)
