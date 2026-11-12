# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
"""Is LP2 flatter (under-dispersed) than a soft-filtered uniform stream? (follow-up of R17-P4 page_homog_z=-2.93 vs
machine -1.46+-1.02 and chi2W290 0.8747 vs 0.9273+-0.0386).  Null: uniform draws + soft anti-repeat (keep=0.1925),
same page lengths.  Statistics: per-page chi2 sum; windowed chi2/df on the flat stream for several W."""
import sys, random, collections
sys.path.insert(0,'.')
from lpdata import *
P=[[r['i'] for r in p] for p in unsolved_pages()]
def page_chi(pages):
    t=0
    for p in pages:
        c=collections.Counter(p); e=len(p)/29
        t+=sum((c.get(i,0)-e)**2/e for i in range(29))
    return t/(28*len(pages))
def win_chi(flat,W):
    t=0;n=0
    for a in range(0,len(flat)-W+1,W):
        c=collections.Counter(flat[a:a+W]); e=W/29
        t+=sum((c.get(i,0)-e)**2/e for i in range(29)); n+=1
    return t/(28*n)
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
Ws=[29,58,116,232,290,464,928,1856]
real={'page':page_chi(P)}; F=[x for p in P for x in p]
for W in Ws: real[W]=win_chi(F,W)
rng=random.Random(2026); NS=3000
null={k:[] for k in real}
for _ in range(NS):
    S=sim(rng); null['page'].append(page_chi(S)); G=[x for p in S for x in p]
    for W in Ws: null[W].append(win_chi(G,W))
print("stat      real     null_mean  null_sd    z      P(null<=real)")
for k in real:
    v=null[k]; mu=sum(v)/NS; sd=(sum((x-mu)**2 for x in v)/NS)**.5
    print(f"{str(k):8s} {real[k]:.4f}   {mu:.4f}    {sd:.4f}  {(real[k]-mu)/sd:+.2f}   {sum(1 for x in v if x<=real[k])/NS:.4f}")
