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
C=np.array([RUN.index(c) for s in segs for c in s if c in RUN]); N=len(C)
LAM=373.6/12956
LG=[math.lgamma(k+1) for k in range(3000)]
def full(Cx,p,lam=LAM):
    n=len(Cx); M=n-60; num=den=0;h=1
    while True:
        mu=lam*p*h; hi=int(mu+5*mu**.5+3)
        if p*h-hi>M: break
        for k in range(max(0,int(mu-5*mu**.5-3)),hi+1):
            L=p*h-k
            if 2<=L<=M:
                w=math.exp(-mu+k*math.log(mu)-LG[k]); T=n-L
                num+=w*(np.count_nonzero(Cx[L:]==Cx[:-L])-T/29.0); den+=w*w*T*(1/29)*(28/29)
        h+=1
    return num/math.sqrt(den) if den>0 else float('nan')
for name,sl in (("half A",slice(0,N//2)),("half B",slice(N//2,N)),("third 1",slice(0,N//3)),("third 2",slice(N//3,2*N//3)),("third 3",slice(2*N//3,N))):
    print(name, {p:round(full(C[sl],p),2) for p in (200,400,800)})
# cross-half only (pairs straddling the midpoint) = total minus within-halves is implicit; instead report whole again
print("whole", {p:round(full(C,p),2) for p in (200,400,800)})
# by $-section (8 sections; only p=400 has >=2 harmonics inside a ~1600-rune section)
units=[];cur=[]
for s in segs:
    for c in s:
        if c in RUN: cur.append(RUN.index(c))
        elif c=='$':
            if cur: units.append(np.array(cur)); cur=[]
if cur: units.append(np.array(cur))
print("section lengths",[len(u) for u in units])
print("per-section z(400):",[round(full(u,400),2) for u in units], " z(800):",[round(full(u,800),2) if len(u)>1000 else None for u in units])
