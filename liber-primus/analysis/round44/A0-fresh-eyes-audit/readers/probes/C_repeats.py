# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
"""Repeated n-gram pair counts in LP2 vs soft-filter-uniform null (fork C). A keyless sliding-block cipher
C_i = g(P_i, P_{i-1..i-k}) or g(P_i, C_{i-1..i-k}) maps repeated plaintext (n+k)-grams to repeated ciphertext n-grams."""
import collections, random, sys
sys.path.insert(0,'.')
from lpdata import *
P=[[r['i'] for r in p] for p in unsolved_pages()]
def reps(pages,n):
    c=collections.Counter()
    for p in pages:
        for i in range(len(p)-n+1): c[tuple(p[i:i+n])]+=1
    return sum(v*(v-1)//2 for v in c.values())
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
rng=random.Random(5)
N=200
null={n:[] for n in range(2,9)}
for _ in range(N):
    S=sim(rng)
    for n in null: null[n].append(reps(S,n))
print(" n  real_pairs  null_mean  null_sd    z   null_max")
for n in null:
    v=null[n]; mu=sum(v)/N; sd=(sum((x-mu)**2 for x in v)/N)**.5
    r=reps(P,n); print(f"{n:2d} {r:10d} {mu:10.1f} {sd:8.2f} {(r-mu)/sd if sd else 0:+6.2f} {max(v)}")
