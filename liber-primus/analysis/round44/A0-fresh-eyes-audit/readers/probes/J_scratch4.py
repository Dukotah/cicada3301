# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
# Fork J scratch: positive control for the monogram matched filter (totient-stream family), through the repo's own filter construction.
import os, sys, collections, math, random, statistics as st
LP=_ROOT+'/liber-primus'
for p in ("src","analysis/round19/I1"): sys.path.insert(0, os.path.join(LP,p))
sys.path.insert(0,'.')
from lp import gematria as gp
import constructions as C
from lpdata import *
N=29; n=12956
def primes(k):
    out=[];c=2
    while len(out)<k:
        if all(c%q for q in out if q*q<=c): out.append(c)
        c+=1
    return out
PR=primes(16000)
def dist(path):
    t=open(path,encoding='utf-8',errors='ignore').read().upper()
    idx=gp.keyword_to_indices(''.join(ch for ch in t if 'A'<=ch<='Z')); return idx
K=LP+'/data/keys/'
lpv=dist(K+'solved_plaintext.txt'); sr=dist(K+'self_reliance.txt')
c=collections.Counter(lpv); pl=[c.get(i,0)/len(lpv) for i in range(29)]   # filter weights from LP-voice ONLY
def z_of(Cx,sign,m):
    O=collections.Counter(Cx); L=len(Cx)
    w=[(1-pl[(cc-sign*m)%29])/28-1/29 for cc in range(29)]
    T=sum(O.get(cc,0)*w[cc] for cc in range(29)); var=L*sum(x*x for x in w)/29
    return T/math.sqrt(var)
res={"tot_cont":[], "tot_pagerestart":[], "uniform_pad":[]}
rng=random.Random(7)
pages=[len(p) for p in unsolved_pages()]
for rep in range(20):
    off=rng.randrange(0,len(sr)-n-1); P=sr[off:off+n]            # plaintext = Self-Reliance window (independent of weights)
    Kc=[(q-1)%29 for q in PR]                                     # phi(prime) continuous
    Cx=C.enc_keyskip(P,Kc,supp=0.83,seed=rep); Cx=list(Cx[0] if isinstance(Cx,tuple) else Cx)[:n]
    res["tot_cont"].append(z_of(Cx,+1,28))
    out=[];pos=0
    for L in pages:                                               # per-page restart at prime index 0
        seg=P[pos:pos+L]; pos+=L
        cx=C.enc_keyskip(seg,Kc,supp=0.83,seed=rep*100+L); out+=list(cx[0] if isinstance(cx,tuple) else cx)[:L]
    res["tot_pagerestart"].append(z_of(out,+1,28))
    Ku=[rng.randrange(29) for _ in range(n*2)]
    Cx=C.enc_keyskip(P,Ku,supp=0.83,seed=rep); Cx=list(Cx[0] if isinstance(Cx,tuple) else Cx)[:n]
    res["uniform_pad"].append(z_of(Cx,+1,28))
for k,v in res.items(): print(f"{k:16s} z mean {st.mean(v):+.2f} sd {st.pstdev(v):.2f} min {min(v):+.2f} max {max(v):+.2f}")
U=flat(unsolved_pages()); print("REAL LP2: z(phi stream, C=P+K) = %+.2f ; z(C=P-K) = %+.2f"%(z_of(U,+1,28),z_of(U,-1,28)))
print("fraction of H1 plants (continuous) with z <= real+: %.2f"%(sum(1 for x in res['tot_cont'] if x<=z_of(U,+1,28))/20))
