# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
# Fork J scratch checks (NOT a registered lane; verification snippets only)
import sys, collections, math
sys.path.insert(0,_ROOT+'/liber-primus/src')
sys.path.insert(0,'.')
from lp import gematria as gp
from lpdata import *
P=unsolved_pages(); U=flat(P); N=len(U)
# (1) analytic unigram IoC of C = P + K for natural-language P and K
def dist(path, cap=None):
    t=open(path,encoding='utf-8',errors='ignore').read().upper()
    idx=gp.keyword_to_indices(''.join(ch for ch in t if 'A'<=ch<='Z'))
    if cap: idx=idx[:cap]
    c=collections.Counter(idx); n=len(idx)
    return [c.get(i,0)/n for i in range(29)], n
def ioc(d): return 29*sum(x*x for x in d)
def conv(a,b,sign=1): return [sum(a[k]*b[(c-sign*k)%29] for k in range(29)) for c in range(29)]
K=_ROOT+'/liber-primus/data/keys/'
pl,n1=dist(K+'solved_plaintext.txt'); sr,n2=dist(K+'self_reliance.txt')
print("IoC29 LP-voice plaintext %.3f (n=%d); Self-Reliance %.3f (n=%d)"%(ioc(pl),n1,ioc(sr),n2))
print("IoC29 of C=P+K (LPvoice + SelfReliance): %.4f ; C=K-P: %.4f ; P+P: %.4f"%(ioc(conv(pl,sr)),ioc(conv(sr,pl,-1)),ioc(conv(pl,pl))))
# measured + sampling sd
mc=collections.Counter(U); chi=sum((mc[i]-N/29)**2/(N/29) for i in range(29))
print("measured IoC29 %.5f  (sd under uniform ~ %.5f)"%(29*sum(mc[i]*(mc[i]-1) for i in range(29))/(N*(N-1)), math.sqrt(2*28)/N))
# totient stream key: uniform on residues 0..27
tot=[1/28 if i<28 else 0 for i in range(29)]
print("IoC29 of C=P+phi-stream-like key (uniform on 28 residues): %.5f"%ioc(conv(pl,tot)))
# (2) doublets inside page heads
first=[]; h120=0; h240=0; h24=0
for pi,p in enumerate(P):
    pos=[k for k in range(1,len(p)) if p[k]['i']==p[k-1]['i']]
    if pos and pos[0]<120: h120+=1
    if pos and pos[0]<240: h240+=1
    if pos and pos[0]<24: h24+=1
    first.append(pos[0] if pos else None)
print("pages with >=1 doublet:",sum(1 for f in first if f is not None),"of",len(P))
print("pages with a doublet in first 24/120/240 runes:",h24,h120,h240)
print("first-doublet offset per page:",first)
# (3) D-stream kappa (lag) + periodic IoC on the 28-symbol step alphabet, doublets dropped and kept
D=[]; 
for p in P:
    D.append([(p[k]['i']-p[k-1]['i'])%29 for k in range(1,len(p))])
Dflat=[d for pg in D for d in pg]
nz=[d for d in Dflat if d!=0]
print("steps",len(Dflat),"nonzero",len(nz))
def kappa(seq,maxlag,alph):
    out=[]
    for lag in range(1,maxlag+1):
        eq=sum(1 for i in range(lag,len(seq)) if seq[i]==seq[i-lag]); tot=len(seq)-lag
        p0=1/alph; z=(eq-tot*p0)/math.sqrt(tot*p0*(1-p0)); out.append((lag,z))
    return out
for name,seq,alph in (("D nonzero-only (28 sym)",nz,28),):
    ks=kappa(seq,300,alph)
    big=[(l,round(z,2)) for l,z in ks if abs(z)>3]
    sd=(sum(z*z for l,z in ks)/len(ks))**.5
    print(name,"lags|z|>3:",big," sd of z over lags 1..300: %.3f"%sd, " lag1 z %.2f lag2 z %.2f"%(ks[0][1],ks[1][1]))
# periodic IoC of D (within-page positions), periods 1..60, 28-symbol
def perioc(seqs,m,alph):
    tot=0;w=0
    for r in range(m):
        col=[d for pg in seqs for i,d in enumerate(pg) if i%m==r and d!=0]
        n=len(col)
        if n<2: continue
        c=collections.Counter(col)
        tot+=alph*sum(v*(v-1) for v in c.values())/(n*(n-1))*n; w+=n
    return tot/w
best=sorted(((perioc(D,m,28),m) for m in range(1,61)),reverse=True)[:5]
print("D periodic IoC*28 (page-anchored) top5:",[(round(a,4),m) for a,m in best])
c=collections.Counter(nz); e=len(nz)/28
print("D nonzero chi2 (df27): %.1f ; counts"%sum((c[d]-e)**2/e for d in range(1,29)),[c[d] for d in range(1,29)])
