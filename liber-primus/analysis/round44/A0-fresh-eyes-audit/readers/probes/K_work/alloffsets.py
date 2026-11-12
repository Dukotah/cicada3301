# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
"""EXPLORATORY: all ordered page pairs x all relative offsets, folded-|d| chi2 (14 df) on overlaps >= 120 runes."""
import sys, itertools, math, time
import numpy as np
from lpdata import load
PG=load(); P=[np.array([r['i'] for r in pg],dtype=np.int64) for pg in PG][:55]
e_unit=np.concatenate([[1/29],np.full(14,2/29)])
def sf14(x):
    s=0.0; term=1.0
    for i in range(7):
        if i>0: term*=(x/2)/i
        s+=term
    return math.exp(-x/2)*s
t=time.time(); rows=[]; ncell=0
for a,b in itertools.combinations(range(55),2):
    A,B=P[a],P[b]
    for off in range(-(len(B)-120),len(A)-120+1):
        i0=max(0,off); j0=max(0,-off); L=min(len(A)-i0,len(B)-j0)
        if L<120: continue
        c=np.bincount((A[i0:i0+L]-B[j0:j0+L])%29,minlength=29).astype(float)
        f=np.concatenate([[c[0]],c[1:15]+c[28:14:-1]]); e=e_unit*L
        x=float(((f-e)**2/e).sum()); ncell+=1
        if x>40: rows.append((sf14(x),x,L,a,b,off))
rows.sort()
print("cells",ncell,"time %.0fs"%(time.time()-t)," bonferroni threshold p<%.1e"%(0.05/ncell))
for p,x,L,a,b,off in rows[:12]: print("  p=%.2e chi2=%.1f L=%d seg(%d,%d) off=%d  bonf=%.3g"%(p,x,L,a,b,off,min(1,p*ncell)))
print("expected count with chi2>40 under null: %.1f ; observed %d"%(ncell*sf14(40),len(rows)))
