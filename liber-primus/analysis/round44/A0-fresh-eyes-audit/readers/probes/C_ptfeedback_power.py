# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
"""Power of the seed-free repeat statistic against keyless PT-/MIX-source k-history feedback (R12-C1 class).
Plaintext = quadgram-Markov English (repo's run_stats._english_from_quadgrams; conservative: order-3 Markov
under-produces long repeats vs real prose), 12,956 runes, cut into LP2's page lengths."""
import sys, collections, random
sys.path.insert(0,'.'); sys.path.insert(0,_ROOT+'/liber-primus/src'); sys.path.insert(0,_ROOT+'/liber-primus/analysis')
sys.path.insert(0,_ROOT+'/liber-primus/analysis/round12/C1')
from lpdata import *
import run_stats, feedback as fb
from lp import gematria as gp
LP=[[r['i'] for r in p] for p in unsolved_pages()]
lens=[len(p) for p in LP]
eng=gp.keyword_to_indices(run_stats._english_from_quadgrams(60000))[:sum(lens)]
print("english runes",len(eng))
def cut(S):
    out=[];a=0
    for L in lens: out.append(S[a:a+L]); a+=L
    return out
def reps(pages,n):
    c=collections.Counter()
    for p in pages:
        for i in range(len(p)-n+1): c[tuple(p[i:i+n])]+=1
    return sum(v*(v-1)//2 for v in c.values())
print("LP2 real      : rep3=%d rep4=%d rep5=%d rep6=%d"%tuple(reps(LP,n) for n in (3,4,5,6)), "(null mean 3539/122/4.0/0.1, sd 56/10.4/2.2/0.4)")
print("english plain : rep3=%d rep4=%d rep5=%d rep6=%d"%tuple(reps(cut(eng),n) for n in (3,4,5,6)))
rng=random.Random(1)
for src in ("pt","mix","ct"):
    for fname in ("sum","prime_of_gemsum","xor"):
        for k in (2,3,4,6):
            seed=[rng.randrange(29) for _ in range(k)]
            C=fb.encipher(eng, fb.F_BASIS[fname], k, seed, source=src, sign=-1)
            r=[reps(cut(C),n) for n in (3,4,5,6)]
            dbl=sum(1 for a,b in zip(C,C[1:]) if a==b)/len(C)
            print(f"src={src:3s} f={fname:15s} k={k}: rep3={r[0]:6d} rep4={r[1]:5d} rep5={r[2]:4d} rep6={r[3]:4d}  z4={(r[1]-122.1)/10.36:+7.1f}  doublet%={100*dbl:.2f}")
