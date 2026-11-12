# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
import sys, itertools, math, collections
sys.path.insert(0,_PROBES)
import numpy as np
from lpdata import load, TR
PG=load()
P=[np.array([r['i'] for r in p],dtype=np.int16) for p in PG]
def chi2(x):
    L=len(x); c=np.bincount(x,minlength=29).astype(float); e=L/29
    return float(((c-e)**2/e).sum())
n=55
# 1. family by page distance d (difference at offset 0), unsolved segments only
print("mean chi2 of (k,k+d) differences by d (expect 28; sd of mean ~ 7.5/sqrt(npairs)):")
fam=[]
for d in range(1,40):
    xs=[chi2((P[k][:min(len(P[k]),len(P[k+d]))]-P[k+d][:min(len(P[k]),len(P[k+d]))])%29) for k in range(n-d) if min(len(P[k]),len(P[k+d]))>=100]
    m=sum(xs)/len(xs); z=(m-28)/(7.48/math.sqrt(len(xs))); fam.append((round(z,2),d,len(xs),round(m,1)))
print(sorted(fam,reverse=True)[:6]); print([f for f in fam if f[1]==14])
# kappa (delta=0) for all pairs: rank of (28,42)
kap=[]
for a,b in itertools.combinations(range(n),2):
    L=min(len(P[a]),len(P[b]))
    if L<100: continue
    m=int((P[a][:L]==P[b][:L]).sum()); kap.append(((m-L/29)/math.sqrt(L/29*28/29),m,L,a,b))
kap.sort(reverse=True); print("top kappa pairs:",[(round(z,2),m,L,a,b) for z,m,L,a,b in kap[:6]]); 
zs=[k[0] for k in kap]; print("kappa z mean %.3f sd %.3f n=%d"%(np.mean(zs),np.std(zs),len(zs)))
# 2. aligned view of seg 28 vs seg 42
a,b=28,42
A=PG[a];B=PG[b];L=min(len(A),len(B))
co=[i for i in range(L) if A[i]['i']==B[i]['i']]
print("coincidence positions:",co)
print("coincident runes:",[TR[A[i]['i']] for i in co])
gaps=[y-x for x,y in zip(co,co[1:])]; print("gaps:",gaps)
# word boundary alignment: do the two pages share word-break positions?
wa={i for i in range(1,len(A)) if ('-' in A[i]['pre'] or '.' in A[i]['pre'])}
wb={i for i in range(1,len(B)) if ('-' in B[i]['pre'] or '.' in B[i]['pre'])}
print("word starts A",len(wa),"B",len(wb),"shared",len(wa&wb),"expected if indep %.1f"%(len(wa)*len(wb)/L))
la=[i for i in range(1,len(A)) if '/' in A[i]['pre']]; lb=[i for i in range(1,len(B)) if '/' in B[i]['pre']]
print("line starts A:",la); print("line starts B:",lb)
# 3. windowed chi2 by relative offset
print("windowed (80-rune windows) best offset in -6..6:")
for w0 in range(0,L-40,40):
    best=[]
    for off in range(-6,7):
        ia=range(max(w0,0),min(w0+80,len(A)))
        d=[(A[i]['i']-B[i+off]['i'])%29 for i in ia if 0<=i+off<len(B)]
        if len(d)>=60: best.append((round(chi2(np.array(d)),1),off,sum(1 for v in d if v==0)))
    best.sort(reverse=True); print("  win %3d:"%w0,best[:3])
