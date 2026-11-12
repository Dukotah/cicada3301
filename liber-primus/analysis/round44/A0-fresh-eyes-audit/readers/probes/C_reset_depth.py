# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
"""Generic test for 'key resets to the SAME state at each unit start' (unit = page, line, sentence, word, &/$ section):
if so, column j of all units shares key K_j -> column coincidence rate ~ plaintext IoC (0.06+) instead of 1/29,
at least for the early columns before skip-desync.  Also end-anchored columns (reset counted from unit end)."""
import sys, math, collections, re
sys.path.insert(0,'.')
from lpdata import *
pages=unsolved_pages()
def units(kind):
    out=[]
    for p in pages:
        cur=[]
        for r in p:
            pre=r['pre']
            cut = (kind=='page' and False) or (kind=='line' and '/' in pre) or (kind=='sentence' and '.' in pre) \
                  or (kind=='word' and ('-' in pre or '.' in pre)) or (kind=='section' and ('&' in pre or '$' in pre or '§' in pre))
            if cut and cur: out.append(cur); cur=[]
            cur.append(r['i'])
        if cur: out.append(cur)
    return out
def col_stats(U, cols, from_end=False):
    pairs=co=0
    for j in cols:
        col=[(u[-1-j] if from_end else u[j]) for u in U if len(u)>j]
        n=len(col); c=collections.Counter(col)
        pairs+=n*(n-1)//2; co+=sum(v*(v-1)//2 for v in c.values())
    if pairs==0: return None
    e=pairs/29; z=(co-e)/math.sqrt(pairs*(1/29)*(28/29))
    return pairs,co,co/pairs,z
print("unit      n_units  cols        pairs    coinc   rate    z(vs 1/29)   [English-in-depth would be ~0.06]")
for kind,colsets in (("page",[range(0,10),range(10,30),range(30,80)]),("section",[range(0,10),range(10,30)]),("line",[range(0,5),range(5,15),range(15,22)]),
                     ("sentence",[range(0,5),range(5,15)]),("word",[range(0,1),range(1,2),range(2,3),range(3,5)])):
    U=units(kind)
    for cols in colsets:
        for fe in (False,True):
            s=col_stats(U,cols,fe)
            if s: print(f"{kind:9s} {len(U):6d}  {('end-' if fe else '')+str(cols.start)+'..'+str(cols.stop-1):10s} {s[0]:8d} {s[1]:7d}  {s[2]:.4f}  {s[3]:+.2f}")
