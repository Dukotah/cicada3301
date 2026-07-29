"""Follow-up: chase the only two apparent LP2 residuals from probe.py:
  (1) lag-11 autocorrelation z = -2.91  (all other non-trivial lags |z|<1.6)
  (2) diff-histogram cell 0 = 86 (the known doublet hole) — is anything ELSE off?

A true random pad (post doublet-filter) should show NOTHING at lag 11. If LP2's
lag-11 dip is real structure, it would repeat across independent pads far less
often than in LP2. We test it as a multiple-comparison artifact: scan MANY lags
on MANY true filtered pads and ask how often |z|>=2.91 appears by chance.
"""
import os, sys, math, random, collections
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
from lp import gematria as gp  # noqa
N = gp.N

def load_unsolved():
    txt = open(os.path.join(ROOT, "data", "krisyotam_runes.txt"), encoding="utf-8").read()
    pages = [gp.runes_to_indices(s) for s in txt.split("%")]
    pages = [p for p in pages if p]
    return [i for p in pages[:-2] for i in p], pages

def filler(n, rng, p=0.83):
    out=[]; prev=None
    for _ in range(n):
        c=rng.randrange(N)
        if prev is not None and c==prev and rng.random()<p:
            c=rng.choice([j for j in range(N) if j!=prev])
        out.append(c); prev=c
    return out

def ac_z(idxs, L):
    n=len(idxs); eq=sum(1 for i in range(L,n) if idxs[i]==idxs[i-L]); m=n-L
    p=1/N
    return (eq/m - p)/math.sqrt(p*(1-p)/m)

def main():
    un,pages=load_unsolved(); n=len(un)
    LAGS=list(range(2,120))  # skip lag1 (the known doublet rule)
    lp_z={L:ac_z(un,L) for L in LAGS}
    extreme=[(L,round(z,2)) for L,z in lp_z.items() if abs(z)>=2.5]
    print(f"LP2 lags 2..119 with |z|>=2.5:  {extreme}")
    print(f"LP2 max |z| over 118 lags: {max(abs(z) for z in lp_z.values()):.2f} "
          f"at lag {max(lp_z,key=lambda L:abs(lp_z[L]))}")

    # Multiple-comparison null: on true filtered pads, how big does the MAX |z|
    # across the same 118 lags get, and how often does ANY lag hit |z|>=2.91?
    TR=300; maxes=[]; hit291=0; hit_lag11=[]
    for t in range(TR):
        rng=random.Random(20000+t); f=filler(n,rng)
        zs=[ac_z(f,L) for L in LAGS]
        mx=max(abs(z) for z in zs); maxes.append(mx)
        if mx>=2.91: hit291+=1
        hit_lag11.append(ac_z(f,11))
    maxes.sort()
    import statistics as st
    print(f"\nTrue-pad control ({TR} pads), MAX|z| across 118 lags each:")
    print(f"  mean {st.mean(maxes):.2f}  p50 {maxes[len(maxes)//2]:.2f}  "
          f"p95 {maxes[int(.95*TR)]:.2f}  max {maxes[-1]:.2f}")
    print(f"  fraction of pads whose MAX|z| >= 2.91 (LP2's lag-11 value): "
          f"{hit291/TR:.3f}")
    print(f"  lag-11 alone on pads: mean z {st.mean(hit_lag11):.2f}  "
          f"|z|>=2.91 in {sum(1 for z in hit_lag11 if abs(z)>=2.91)/TR:.3f} of pads")

    # Per-page: does any single unsolved page depart from the flat profile?
    print("\nPer-page fingerprint (looking for an outlier page):")
    print(f"{'pg':>3} {'n':>5} {'ioc*N':>7} {'dbl%':>6} {'H':>7}")
    import collections as C
    def ioc(x):
        c=C.Counter(x); return sum(v*(v-1) for v in c.values())/(len(x)*(len(x)-1))*N
    def dbl(x): return 100*sum(1 for a,b in zip(x,x[1:]) if a==b)/(len(x)-1)
    def H(x):
        c=C.Counter(x); nn=len(x)
        return -sum((v/nn)*math.log2(v/nn) for v in c.values())
    for i,p in enumerate(pages[:-2]):
        if len(p)<30:
            print(f"{i:>3} {len(p):>5}   (short)"); continue
        print(f"{i:>3} {len(p):>5} {ioc(p):>7.3f} {dbl(p):>6.2f} {H(p):>7.3f}")

if __name__=="__main__":
    main()
