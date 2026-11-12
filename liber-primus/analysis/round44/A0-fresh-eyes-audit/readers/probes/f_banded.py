# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
"""Fork F verification snippets (language-agnostic, seconds):
 (1) drift-aware ("banded") periodicity scan: periodic key of period p under a key-SKIP anti-repeat filter (skip rate lam/rune)
     re-uses a key symbol at ciphertext lag p-k, k~Poisson(lam*p). Matched-filter z over lags; with plant to measure power.
 (2) contextual kappa, orders 1..3: keyless ciphertext-feedback of ANY form => same k-rune context -> same key -> next runes coincide
     at plaintext kappa. Null rate accounts for the doublet filter.
 (3) banded cross-section / cross-page depth (same key restarted, independent skip drift)."""
import sys, math, random, collections
import numpy as np
sys.path.insert(0,_PROBES)
from lpdata import *
RUN="ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
txt=open(REPO+'/data/krisyotam_runes.txt',encoding='utf-8').read()
segs=[s for s in txt.split('%') if any(c in RUN for c in s)][:-2]
C=np.array([RUN.index(c) for s in segs for c in s if c in RUN]); N=len(C)
LAM=373.6/12956
def eqcounts(C,maxlag):
    n=len(C); E=np.zeros(maxlag+1); T=np.zeros(maxlag+1)
    for L in range(1,maxlag+1):
        E[L]=np.count_nonzero(C[L:]==C[:-L]); T[L]=n-L
    return E,T
def banded(C,pmax,lam=LAM,harm=1):
    n=len(C); maxlag=min(n-50,pmax*harm)
    E,T=eqcounts(C,maxlag)
    D=E-T/29.0; V=T*(1/29)*(28/29)
    out=np.zeros(pmax+1)
    for p in range(2,pmax+1):
        num=0.0; den=0.0
        for h in range(1,harm+1):
            mu=lam*p*h
            kmax=int(mu+6*math.sqrt(mu)+6)
            ks=np.arange(0,kmax+1)
            w=np.exp(-mu+ks*math.log(mu)-np.array([math.lgamma(k+1) for k in ks])) if mu>0 else np.array([1.0])
            lags=p*h-ks; ok=(lags>=2)&(lags<=maxlag)      # lag 1 excluded (the doublet hole)
            num+=np.sum(w[ok]*D[lags[ok]]); den+=np.sum(w[ok]**2*V[lags[ok]])
        out[p]=num/math.sqrt(den) if den>0 else 0
    return out
z=banded(C,6000)
top=np.argsort(-z)[:8]; bot=np.argsort(z)[:3]
print("(1) banded periodicity, flat stream, p=2..6000: max z",[(int(p),round(float(z[p]),2)) for p in top]," min",[(int(p),round(float(z[p]),2)) for p in bot], " sd %.3f"%z[2:].std())
z3=banded(C,2000,harm=3)
print("    with 3 harmonics p<=2000: top",[(int(p),round(float(z3[p]),2)) for p in np.argsort(-z3)[:6]])
# plant: English-like plaintext (unigram-lumpy, from quadgram markov) + periodic key + keyskip filter supp .83
sys.path.insert(0,REPO+'/analysis'); sys.path.insert(0,REPO+'/src')
def english_runes(n,seed):
    # crude: sample rune indices from an English rune-unigram distribution with lag-1 structure irrelevant for kappa test
    import run_stats
    s=run_stats._english_from_quadgrams(n*2)
    from lp import gematria as gp
    idx=gp.runes_to_indices(gp.latin_to_runes(s)) if hasattr(gp,'latin_to_runes') else None
    return idx
try:
    P=english_runes(14000,1)
except Exception as e:
    P=None; print("english plant unavailable:",e)
if P is None or len(P)<N:
    # fallback: iid from an English-like rune unigram (kappa ~0.06)
    rng=random.Random(1)
    freq=[2.2,2.8,3.5,7.0,5.8,2.8,1.8,2.2,5.5,6.7,6.5,0.2,0.6,1.8,0.2,6.0,8.5,1.5,12.0,2.4,4.0,1.0,0.3,4.0,7.5,0.5,1.9,0.6,1.0]
    P=rng.choices(range(29),weights=freq,k=N+10)
P=np.array(P[:N+10]); 
kap=sum((np.bincount(P,minlength=29)/len(P))**2); print("    plant plaintext kappa %.4f (1/29=%.4f)"%(kap,1/29))
def plant(P,p,seed,supp=0.83):
    rng=random.Random(seed); K=[rng.randrange(29) for _ in range(p)]
    out=[]; j=0; prev=None
    for x in P[:N]:
        while True:
            c=(int(x)+K[j%p])%29
            if prev is not None and c==prev and rng.random()<supp: j+=1; continue
            break
        out.append(c); j+=1; prev=c
    return np.array(out)
for p in (13,60,150,400,800,1500,3000):
    zz=banded(plant(P,p,7+p),min(6000,max(2*p,200)))
    best=int(np.argmax(zz)); print(f"    plant period {p}: z at p = {zz[p]:.2f}; argmax p={best} z={zz[best]:.2f}")
# (2) contextual kappa
delta=86/12901; r0=(1-delta)**2/28+delta**2
print("(2) contextual kappa; null rate with doublet filter r0=%.5f"%r0)
for k in (1,2,3):
    ctx=collections.defaultdict(list)
    # do not cross page boundaries: build per-page
    pos=0
    for s in segs:
        pg=[RUN.index(c) for c in s if c in RUN]
        for i in range(k,len(pg)): ctx[tuple(pg[i-k:i])].append(pg[i])
    pairs=eq=0
    for v in ctx.values():
        n=len(v); 
        if n<2: continue
        cnt=collections.Counter(v); pairs+=n*(n-1)//2; eq+=sum(c*(c-1)//2 for c in cnt.values())
    zc=(eq-pairs*r0)/math.sqrt(pairs*r0*(1-r0))
    print(f"    order {k}: same-context pairs {pairs}, next-rune coincidences {eq} = {100*eq/pairs:.3f}%  z vs r0 = {zc:+.2f}   (H1 keyless feedback: rate ~5.5-6%, z ~ {(0.058-r0)*pairs/math.sqrt(pairs*r0*(1-r0)):.0f})")
# (3) banded depth between units restarted with the same key
def units(sep):
    out=[]; cur=[]
    for s in segs:
        for c in s:
            if c in RUN: cur.append(RUN.index(c))
            elif c in sep:
                if cur: out.append(np.array(cur)); cur=[]
        if sep=='%' and cur: out.append(np.array(cur)); cur=[]
    if cur: out.append(np.array(cur))
    return out
def banded_depth(U,L,lam=LAM):
    num=den=0.0
    for a in range(len(U)):
        for b in range(a+1,len(U)):
            A,B=U[a][:L],U[b][:L]
            n=min(len(A),len(B))
            for i in range(n):
                sd=math.sqrt(2*lam*i)+1e-9; w_=int(3*sd)+1
                for d in range(-w_,w_+1):
                    j=i+d
                    if 0<=j<len(B):
                        wgt=math.exp(-0.5*(d/max(sd,0.6))**2)
                        num+=wgt*((A[i]==B[j])-1/29); den+=wgt*wgt*(1/29)*(28/29)
    return num/math.sqrt(den)
for name,sep,L in (("$-sections","$",400),("&/$-paragraphs","&$",300)):
    U=units(sep); print(f"(3) banded depth {name}: units {len(U)} L={L}: z = {banded_depth(U,L):+.2f}")
