# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
import random, math, time, numpy as np
from drift_kappa import *
t0=time.time()
rng=random.Random(777)
nb=[];nr=[]
for t in range(300):
    z=zlags(null_stream(rng)); b,r=scan(z); nb.append((round(b[0],2),b[1])); nr.append(round(r[0],2))
nb.sort(); nr.sort()
print("NULL n=300 drift-matched: median %.2f p95 %.2f p99 %.2f max %s"%(nb[150][0],nb[285][0],nb[297][0],nb[-3:]))
print("NULL n=300 rigid: median %.2f p95 %.2f p99 %.2f max %.2f"%(nr[150],nr[285],nr[297],nr[-1]))
thr=nb[297][0]; thr_r=nr[297]
zr=zlags(U); br,rr=scan(zr)
print("REAL: drift T=%.2f (null pct %.0f%%)  rigid T=%.2f (null pct %.0f%%)"%(br[0],100*sum(1 for x in nb if x[0]<br[0])/300, rr[0],100*sum(1 for x in nr if x<rr[0])/300))
Pt=english_runes(N,11)
for per in (300,450,600,800,1000,1300,1700):
    det=0;detr=0;vals=[]
    for rep in range(8):
        key=np.array([rng.randrange(29) for _ in range(per)],dtype=np.uint8)
        C=encipher(Pt,key,'KEYADV',rng=rng)
        b,r=scan(zlags(C)); vals.append(round(b[0],1)); det+= b[0]>thr; detr+= r[0]>thr_r
    print("PLANT KEYADV period %4d: drift-matched detect %d/8 (rigid-scan detect %d/8) T=%s"%(per,det,detr,vals))
for per in (1000,3000):
    key=np.array([rng.randrange(29) for _ in range(per)],dtype=np.uint8)
    C=encipher(Pt,key,'REPICK',rng=rng); b,r=scan(zlags(C)); print("PLANT REPICK(no drift) period",per,"rigid T=%.1f at p=%s"%(r[0],r[1]))
print("elapsed %.0fs"%(time.time()-t0))
