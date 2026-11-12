# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
import sys, math, random
import numpy as np
sys.path.insert(0,_PROBES)
from lpdata import *
RUN="ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
txt=open(REPO+'/data/krisyotam_runes.txt',encoding='utf-8').read()
segs=[s for s in txt.split('%') if any(c in RUN for c in s)][:-2]
C=np.array([RUN.index(c) for s in segs for c in s if c in RUN]); N=len(C); M=N-60
LAM=373.6/12956
LG=[math.lgamma(k+1) for k in range(3000)]
def DV(Cx):
    D=np.zeros(M+1);V=np.zeros(M+1)
    for L in range(2,M+1):
        T=N-L; D[L]=np.count_nonzero(Cx[L:]==Cx[:-L])-T/29.0; V[L]=T*(1/29)*(28/29)
    return D,V
def perh(D,V,p,lam=LAM,H=15):
    out=[]
    for h in range(1,H+1):
        mu=lam*p*h; num=den=0
        for k in range(max(0,int(mu-5*mu**.5-3)),int(mu+5*mu**.5+3)+1):
            L=p*h-k
            if 2<=L<=M:
                w=math.exp(-mu+k*math.log(mu)-LG[k]); num+=w*D[L]; den+=w*w*V[L]
        out.append(round(num/math.sqrt(den),1) if den>0 else None)
    return out
D,V=DV(C)
for p in (200,400,800,1600): print("REAL p=%d per-harmonic z:"%p, perh(D,V,p))
freq=[2.2,2.8,3.5,7.0,5.8,2.8,1.8,2.2,5.5,6.7,6.5,0.2,0.6,1.8,0.2,6.0,8.5,1.5,12.0,2.4,4.0,1.0,0.3,4.0,7.5,0.5,1.9,0.6,1.0]
def plant(p,seed,supp=0.83):
    r=random.Random(seed); P=r.choices(range(29),weights=freq,k=N); K=[r.randrange(29) for _ in range(p)]
    out=[]; j=0; prev=None
    for x in P:
        while True:
            c=(x+K[j%p])%29
            if prev is not None and c==prev and r.random()<supp: j+=1; continue
            break
        out.append(c); j+=1; prev=c
    return np.array(out)
for p in (400,800):
    Dp,Vp=DV(plant(p,100*p+2)); print("PLANT p=%d per-harmonic z:"%p, perh(Dp,Vp,p))
# drift-rate robustness for the real stream (NOT a new search: lam is the repo's 373.6 estimate; show neighbours only)
def full(D,V,p,lam):
    num=den=0;h=1
    while True:
        mu=lam*p*h; hi=int(mu+5*mu**.5+3)
        if p*h-hi>M: break
        for k in range(max(0,int(mu-5*mu**.5-3)),hi+1):
            L=p*h-k
            if 2<=L<=M:
                w=math.exp(-mu+k*math.log(mu)-LG[k]); num+=w*D[L]; den+=w*w*V[L]
        h+=1
    return num/math.sqrt(den)
for p in (400,800):
    print("REAL p=%d z vs assumed total drift:"%p,{d:round(full(D,V,p,d/12956),2) for d in (250,300,340,373.6,410,450,500)})
# rigid (no-drift) column kappa for p=400/800 for contrast
for p in (400,800):
    eq=tot=0
    for r in range(p):
        col=C[r::p]; n=len(col); cnt=np.bincount(col,minlength=29); eq+=int(np.sum(cnt*(cnt-1)//2)); tot+=n*(n-1)//2
    print("rigid column kappa p=%d: %.4f z=%.2f"%(p,eq/tot,(eq-tot/29)/math.sqrt(tot/29*28/29)))
