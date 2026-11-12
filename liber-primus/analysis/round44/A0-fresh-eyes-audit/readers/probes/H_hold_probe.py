# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
"""Fork H probe 2: one literal-F key hold inside the first 24 runes (the real page-0 head has F at index 7 and 17).
40 EN_MODERN windows chosen so plaintext has an F at index 4..20; correct key handed over; instrument of record."""
import sys, random, json
sys.dont_write_bytecode = True
sys.path.insert(0, _ROOT+"/liber-primus")
sys.path.insert(0, _PROBES)
import numpy as np
import verify_solution as VS
VS.load_instruments(quiet=True)
t = np.load(VS.PANEL_R36_TEST); EN = [int(v) for v in t["EN_MODERN"]]
N=29; L=120
def enc(P,K,hold,seed,supp=0.83):
    rng=random.Random(seed); C=[]; j=0; prev=None
    for i,p in enumerate(P):
        if i==hold: C.append(0); prev=0; continue
        while True:
            c=(p+K[j])%N
            if prev is not None and c==prev and rng.random()<supp: j+=1; continue
            break
        C.append(c); j+=1; prev=c
    return C
res={"keyskip1":[], "free":[]}; base={"keyskip1":[], "free":[]}; n=0; s=30000
while n<40 and s<len(EN)-L:
    P=EN[s:s+L]; fpos=[i for i in range(4,21) if P[i]==0]
    s+=131
    if not fpos: continue
    r=random.Random(n); K=[r.randrange(N) for _ in range(6*L)]
    for hold,store in ((fpos[0],res),(None,base)):
        C=enc(P,K,hold,seed=n)
        for rel in ("keyskip1","free"):
            row=VS.judge_register(K,[C],relations=(rel,))[0]
            rc=sum(1 for x,y in zip(row["plain_idx"],P) if x==y)/L
            store[rel].append((round(row["pmax"],2),round(rc,2)))
    n+=1
for name,st in (("WITH one literal-F hold in head",res),("control (same windows, no hold)",base)):
    for rel in ("keyskip1","free"):
        pm=[a for a,b in st[rel]]; rc=[b for a,b in st[rel]]
        print(name,rel,"n=%d"%len(pm),"median pmax %.2f"%sorted(pm)[len(pm)//2],"frac pmax>=9.4 (sweep-scale bar): %.2f"%(sum(1 for x in pm if x>=9.4)/len(pm)),"frac recovery>=0.9: %.2f"%(sum(1 for x in rc if x>=0.9)/len(rc)))
