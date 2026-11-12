# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
import sys, itertools, math
sys.path.insert(0,_PROBES)
import numpy as np
from lpdata import load, TR
from math import lgamma
P=[np.array([r['i'] for r in p],dtype=np.int16) for p in load()]
def chi2(x):
    L=len(x); c=np.bincount(x,minlength=29).astype(float); e=L/29
    return float(((c-e)**2/e).sum()), c
def chi2_sf(x,k=28):
    # upper tail via series for regularized gamma Q(k/2,x/2) (k even -> closed form)
    m=k//2; s=0.0; term=1.0
    for i in range(m):
        if i>0: term*= (x/2)/i
        s+=term
    return math.exp(-x/2)*s
rows=[]
n=len(P)
for a,b in itertools.combinations(range(n),2):
    L=min(len(P[a]),len(P[b]))
    if L<60: continue
    for s in (1,-1):
        x,c=chi2((P[a][:L]+s*P[b][:L])%29); rows.append((chi2_sf(x),x,L,a,b,s))
rows.sort()
print("pairs tested",len(rows)); print("top 6 by exact chi2 p:")
for p,x,L,a,b,s in rows[:6]: print("  p=%.2e chi2=%.1f L=%d seg(%d,%d) sign %+d  bonf=%.3f"%(p,x,L,a,b,s,min(1,p*len(rows))))
# detail for (28,42,-1)
a,b,s=28,42,-1
L=min(len(P[a]),len(P[b])); d=(P[a][:L]+s*P[b][:L])%29
x,c=chi2(d); print("delta histogram seg28-seg42:",c.astype(int).tolist())
print("top deltas:",sorted([(int(c[i]),i) for i in range(29)],reverse=True)[:5], "expected per bin %.1f"%(L/29))
# windowed
for w0 in range(0,L,60):
    xx,_=chi2(d[w0:w0+60]); print("  window %3d-%3d chi2=%.1f"%(w0,min(L,w0+60),xx), end='')
print()
# shifts: relative offsets -12..12
out=[]
for off in range(-15,16):
    A=P[a][max(0,off):]; B=P[b][max(0,-off):]; LL=min(len(A),len(B)); xx,_=chi2((A[:LL]-B[:LL])%29); out.append((round(xx,1),off))
print("chi2 by relative offset:",out)
# what would in-depth English look like? difference of two English-rune texts
E=np.concatenate([P[-1]])  # PARABLE only is tiny; build from solved plaintext pages via repo loader is out of scope; estimate with PARABLE vs itself shifted
