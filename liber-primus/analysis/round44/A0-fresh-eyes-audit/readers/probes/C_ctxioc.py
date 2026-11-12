# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
"""Generic CT-feedback test (fork C): if P_i = C_i - f(C_{i-1..i-k}) for ANY f, then within each k-context the
distribution of C_i is a shifted copy of the plaintext unigram distribution -> context-conditional coincidence excess.
Null: soft-filtered uniform stream (MC), same page lengths."""
import collections, math, random, sys
sys.path.insert(0,'.')
from lpdata import *
P=[[r['i'] for r in p] for p in unsolved_pages()]
def ctx_coinc(pages, lags):
    m=max(lags); d=collections.defaultdict(collections.Counter)
    for p in pages:
        for i in range(m,len(p)):
            d[tuple(p[i-l] for l in lags)][p[i]]+=1
    pairs=co=0
    for c,cnt in d.items():
        n=sum(cnt.values()); pairs+=n*(n-1)//2; co+=sum(v*(v-1)//2 for v in cnt.values())
    return pairs,co
def sim(rng,keep=0.1925):
    out=[]
    for p in P:
        q=[]; prev=None
        for _ in p:
            while True:
                x=rng.randrange(29)
                if x!=prev or rng.random()<keep: break
            q.append(x); prev=x
        out.append(q)
    return out
tests=[(1,),(2,),(3,),(1,2),(1,3),(2,3),(1,2,3),(1,2,4),(1,3,4),(2,3,4),(1,2,3,4)]
rng=random.Random(11)
null={t:[] for t in tests}
for k in range(300):
    S=sim(rng)
    for t in tests:
        pr,co=ctx_coinc(S,t); null[t].append(co/pr)
print("lags      pairs   coinc   rate     null_mean  null_sd   z     (rate if English-shifted ~0.06+)")
for t in tests:
    pr,co=ctx_coinc(P,t); v=null[t]; mu=sum(v)/len(v); sd=(sum((x-mu)**2 for x in v)/len(v))**.5
    print(f"{str(t):12s} {pr:8d} {co:6d} {co/pr:.5f}  {mu:.5f}  {sd:.5f}  {(co/pr-mu)/sd:+.2f}")
