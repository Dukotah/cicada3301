# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
"""Fork I probe (read-only on repo): does the panel-R36 instrument (beam_v3 panel_max + 12-register adjudicator)
recognise a CORRECT key when the English plaintext is written WITHOUT digraph runes?
O1 = LP1 folding (what every plant so far used); O2 = TH unfolded (T,H); O3 = all digraph runes unfolded."""
import os, sys, random, json, statistics as st
sys.dont_write_bytecode=True
C1DIR=_ROOT+'/liber-primus/analysis/round37/C1-composed-clue-readings'
sys.path.insert(0,C1DIR)
import numpy as np
from c1lib import V, AD, PAN, B2, bar_v3, v3dec, LP
TEST=np.load(os.path.join(LP,'data','panels','testhalves-r36.npz'))
UNF={2:(16,8),12:(18,3),21:(9,6),22:(3,18),25:(24,18),27:(10,24),28:(18,24)}
def o2(seq): 
    out=[]
    for x in seq: out.extend(UNF[2] if x==2 else (x,))
    return out
def o3(seq):
    out=[]
    for x in seq: out.extend(UNF.get(x,(x,)))
    return out
ENC={'keyskip1':B2.encipher_keyskip1,'keyskip2':B2.encipher_skip_by_two}
rng=random.Random(20261112)
NREP=int(sys.argv[1]) if len(sys.argv)>1 else 10
res={}
for reg in ('EN_MODERN','LP1_REAL'):
    arr=TEST[reg].astype(int).tolist()
    for L in (120,240):
        for rel in ('keyskip1','keyskip2'):
            for name,fn in (('O1',lambda s:s),('O2',o2),('O3',o3)):
                pm=[];rc=[];am=[]
                r2=random.Random(hash((reg,L,rel))&0xffff)   # same windows/keys for O1/O2/O3
                for rep in range(NREP):
                    if len(arr)<L+400: st0=0
                    else: st0=r2.randrange(0,len(arr)-L-200)
                    P=fn(arr[st0:st0+L+40])[:L]
                    K=[r2.randrange(29) for _ in range(1100)]
                    Cc,info=ENC[rel](P,K,0.83,r2.randrange(1,10**9))
                    d,a=v3dec(Cc,K,rel)
                    pm.append(float(a['pmax'])); rc.append(float(B2.recovery(d['plain_idx'],P)))
                    am.append(str(a.get('argmax', a.get('argmax_register','?'))))
                bar=bar_v3(1e6,L,rel)
                res[(reg,L,rel,name)]=(st.mean(pm),min(pm),sum(p>=bar for p in pm)/NREP,st.mean(rc),bar,max(set(am),key=am.count))
                print(f"{reg:9s} L={L} {rel} {name}: pmax mean {st.mean(pm):6.2f} min {min(pm):6.2f} | >=bar_v3(1e6)={bar:.2f}: {sum(p>=bar for p in pm)}/{NREP} | recovery mean {st.mean(rc):.3f} | modal argmax {max(set(am),key=am.count)}",flush=True)
