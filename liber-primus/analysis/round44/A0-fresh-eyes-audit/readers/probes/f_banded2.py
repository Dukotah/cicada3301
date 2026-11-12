# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
"""Full-harmonic drift-aware periodicity detector (matched filter over all returns h*p - k, k~Poisson(lam*h*p))."""
import sys, math, random, time
import numpy as np
sys.path.insert(0,_PROBES)
from lpdata import *
RUN="ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
txt=open(REPO+'/data/krisyotam_runes.txt',encoding='utf-8').read()
segs=[s for s in txt.split('%') if any(c in RUN for c in s)][:-2]
C=np.array([RUN.index(c) for s in segs for c in s if c in RUN]); N=len(C)
LAM=373.6/12956
def eqD(C):
    n=len(C); M=n-60
    D=np.zeros(M+1); V=np.zeros(M+1)
    for L in range(2,M+1):
        T=n-L; D[L]=np.count_nonzero(C[L:]==C[:-L])-T/29.0; V[L]=T*(1/29)*(28/29)
    return D,V,M
LG=[math.lgamma(k+1) for k in range(2000)]
def stat(D,V,M,p,lam=LAM,hmax=None):
    num=den=0.0; h=1
    while True:
        mu=lam*p*h; lo=int(mu-5*math.sqrt(mu)-3); hi=int(mu+5*math.sqrt(mu)+3)
        lo=max(lo,0)
        if p*h-hi>M or (hmax and h>hmax): break
        for k in range(lo,hi+1):
            L=p*h-k
            if L<2 or L>M: continue
            w=math.exp(-mu+k*math.log(mu)-LG[k]) if mu>0 else (1.0 if k==0 else 0.0)
            num+=w*D[L]; den+=w*w*V[L]
        h+=1
    return num/math.sqrt(den) if den>0 else 0.0
t=time.time(); D,V,M=eqD(C); print("lags computed %.1fs"%(time.time()-t))
ps=list(range(2,3001))+list(range(3002,6401,2))
z={p:stat(D,V,M,p) for p in ps}
arr=np.array([z[p] for p in ps])
order=np.argsort(-arr)[:10]
print("REAL full-harmonic: sd %.3f  top:"%arr.std(),[(ps[i],round(float(arr[i]),2)) for i in order])
print("   selected: ",{p:round(stat(D,V,M,p),2) for p in (8,13,29,59,107,200,400,800,1200,1600,1033,3301,3299)})
# plants
rng=random.Random(5)
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
for p in (400,800,1500,3000,5000):
    zs=[]
    for s in range(3):
        Dp,Vp,Mp=eqD(plant(p,100*p+s)); zs.append(stat(Dp,Vp,Mp,p))
    print(f"   PLANT period {p}: full-harmonic z at true p over 3 plants = {[round(x,2) for x in zs]}")
mx=[];z400=[];z800=[]
for rep in range(30):
    r=random.Random(1000+rep); S=C.copy(); r.shuffle(S)
    Ds,Vs,Ms=eqD(np.array(S)); zn=np.array([stat(Ds,Vs,Ms,p) for p in ps]); mx.append(float(zn.max())); z400.append(stat(Ds,Vs,Ms,400)); z800.append(stat(Ds,Vs,Ms,800))
mx.sort(); print("   NULL max over p grid, 30 shuffles: median %.2f  q90 %.2f  max %.2f ; real max 3.70 -> exceed frac %.2f"%(mx[15],mx[27],mx[-1],sum(m>=3.70 for m in mx)/30))
print("   null sd of z(400) %.2f z(800) %.2f"%(np.std(z400),np.std(z800)))
# where does the p=400 signal sit? per-harmonic contributions
for p in (400,800):
    parts=[]
    for h in range(1,9):
        mu=LAM*p*h; num=den=0
        for k in range(max(0,int(mu-5*mu**.5-3)),int(mu+5*mu**.5+3)+1):
            L=p*h-k
            if 2<=L<=M:
                w=math.exp(-mu+k*math.log(mu)-LG[k]); num+=w*D[L]; den+=w*w*V[L]
        parts.append(round(num/math.sqrt(den),2))
    print("   p=%d per-harmonic z (h=1..8):"%p,parts)
