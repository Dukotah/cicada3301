# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
"""Extension: positional LLR for plaintext-PATTERN-linked doublets:
 H_dbl : ct doublet at i  <=>  p_i == p_{i-1}       (e.g. a state cipher that maps equal neighbours to equal output)
 H_aba : ct doublet at i  <=>  p_i == p_{i-2}       (plaintext-autokey family c_i = p_i + p_{i-1})
 H_ab2 : ct doublet at i  <=>  p_i == p_{i-3}
Same machinery as doublet_plain_link.py (cells = (word length, in-word index) of the 2nd rune)."""
import sys, re, glob, math, collections, random
sys.dont_write_bytecode=True
exec(open('doublet_plain_link.py').read().split("tot=sum(Ncell.values())")[0].replace("print('english words'","pass #").replace("print('LP2 pairs'","pass #"))
tot=sum(Ncell.values()); p0={c:n/tot for c,n in Ncell.items()}
flat=[]; cellof=[]
for w in ew:
    L=min(len(w),WMAX)
    for k,r in enumerate(w): flat.append(r); cellof.append((L,min(k,WMAX-1)))
rng=random.Random(2); cells=list(Ncell)
for name,lag in (('H_dbl p_i==p_{i-1}',1),('H_aba p_i==p_{i-2}',2),('H_ab3 p_i==p_{i-3}',3)):
    hit=collections.Counter(); allc=collections.Counter()
    for i in range(lag,len(flat)):
        allc[cellof[i]]+=1
        if flat[i]==flat[i-lag]: hit[cellof[i]]+=1
    rate=sum(hit.values())/sum(allc.values())
    f={c:(hit.get(c,0)+0.5*rate)/(allc.get(c,0)+0.5) for c in Ncell}
    z=sum(Ncell[c]*f[c] for c in Ncell); pr={c:Ncell[c]*f[c]/z for c in Ncell}
    llr=sum(math.log(pr[c]/p0[c]) for c in dcells)
    def sim(dist,n=600):
        ws=[dist[c] for c in cells]; out=[]
        for _ in range(n):
            s=rng.choices(cells,weights=ws,k=len(dcells)); out.append(sum(math.log(pr[c]/p0[c]) for c in s))
        m=sum(out)/n; sd=(sum((x-m)**2 for x in out)/n)**.5; return m,sd,out
    mr,sr,outr=sim(pr); m0,s0,out0=sim(p0)
    thr=sorted(out0)[int(0.99*len(out0))]
    print(f"{name}: english rate {100*rate:.2f}% (expected ct doublets if 1:1 = {rate*12901:.0f}; observed 86) | obs LLR {llr:.1f} | E[LLR|H]={mr:.1f}±{sr:.1f} | E[LLR|H0]={m0:.1f}±{s0:.1f} | power@1% {sum(x>thr for x in outr)/len(outr):.2f} | P(LLR<=obs|H)={sum(x<=llr for x in outr)/len(outr):.3f}")
# descriptive: 4-class table for the observed doublets vs base
def cls(c):
    L,k=c
    if L==1: return 'single-rune word'
    if k==0: return 'word-initial'
    if k==L-1 and L<WMAX: return 'word-final'
    return 'interior'
ob=collections.Counter(cls(c) for c in dcells); ba=collections.Counter()
for c,n in Ncell.items(): ba[cls(c)]+=n
for k in ba: print(f"  {k:18s} doublets {ob[k]:3d}  expected-uniform {86*ba[k]/tot:5.1f}")
