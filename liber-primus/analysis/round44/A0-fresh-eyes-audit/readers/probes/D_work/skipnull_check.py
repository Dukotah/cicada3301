# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
"""Fork D check: is L2 sec.4.3's 'two nulls agree at z=0.32 => decoder-level confirmation of the cipher model'
informative?  Measure wrong-key n_skips on (a) UNFILTERED uniform-random ciphertext (M0: no anti-repeat at all)
and (b) HARD-filtered ciphertext (M5).  If both also give ~297, the agreement cannot confirm the filter model."""
import sys, os, random, statistics as st, time
sys.dont_write_bytecode = True
sys.path.insert(0,_ROOT+'/liber-primus/analysis/round18/L2-filter-leak')
import fastbeam as fb
N=29; n=12956
def wrong_key(seed): 
    r=random.Random(seed); return [r.randrange(N) for _ in range(n+2000)]
def m0(seed):
    r=random.Random(seed); return [r.randrange(N) for _ in range(n)]
def m5(seed):
    r=random.Random(seed); C=[]; prev=None
    while len(C)<n:
        c=r.randrange(N)
        if c==prev: continue
        C.append(c); prev=c
    return C
t0=time.time(); out={}
for name,mk in (('M0_unfiltered',m0),('M5_hard',m5)):
    C=mk(101 if name[1]=='0' else 202); sk=[]
    for s in range(5):
        r=fb.beam_decode(C, wrong_key(900+s), sign=-1, o=0, beam_w=400, max_skip=3, want_path=False)
        sk.append(r['n_skips'])
    out[name]=sk
    print(name, sk, 'mean %.1f'%st.mean(sk), 'doublets', sum(1 for a,b in zip(C,C[1:]) if a==b), '%.0fs'%(time.time()-t0), flush=True)
print('L2 published: wrong keys on plant 296.3+-21.4, on real LP2 297.8+-19.8')
