# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
"""Fork F: does the R19-R24 decoder family recover a CORRECT key under constructions the plants never represented?
(a) filterless additive  (b) haplography = DELETE 2nd rune of a ciphertext doublet (plaintext rune lost, key element consumed)
(c) null-insertion (a null rune inserted before a would-be doublet, no key consumed)   (ref) keyskip, rewrite."""
import sys, random, time
sys.path.insert(0,'.')
import driftbeam as DB, constructions as CN
N=29
def enc_plain(P,K,**_):
    return [(p+K[j])%N for j,p in enumerate(P)], list(P)
def enc_haplo(P,K,supp=0.83,seed=1,**_):
    r=random.Random(seed); C=[];T=[];prev=None
    for j,p in enumerate(P):
        c=(p+K[j])%N
        if prev is not None and c==prev and r.random()<supp:
            continue                      # rune not written: ciphertext AND plaintext rune vanish, key element j consumed
        C.append(c); T.append(p); prev=c
    return C,T
def enc_nullins(P,K,supp=0.83,seed=1,**_):
    r=random.Random(seed); C=[];T=[];prev=None
    for j,p in enumerate(P):
        c=(p+K[j])%N
        if prev is not None and c==prev and r.random()<supp:
            nul=r.choice([x for x in range(N) if x!=c]); C.append(nul); T.append(-1)   # null, no key consumed
        C.append(c); T.append(p); prev=c
    return C,T
def run(name,enc,L=240,seeds=range(5),presets=("exact","drift")):
    for pre in presets:
        recs=[];scs=[]
        for s in seeds:
            P=CN.long_plain(L+40,s); K=CN.key_sha(L*6+2048)
            C,T=enc(P,K,seed=3301+s); C=C[:L]; T=T[:L]
            kw=dict(DB.PRESETS[pre]); out=DB.beam_decode(C,K,sign=-1,o=0,beam_w=400,want_path=True,**kw)
            recs.append(DB.recovery(out["plain_idx"],T)); scs.append(out["score"])
        print(f"{name:28s} {pre:6s} recovery {['%.2f'%x for x in recs]}  score {['%.2f'%x for x in scs]}",flush=True)
t=time.time()
def mech(m):
    return lambda P,K,seed=0,**_: (CN.MECH[m](P,K,seed=seed)[0], list(P))
run("ref keyskip (repo plant)",mech("keyskip"))
run("ref rewrite (repo plant)",mech("rewrite"))
run("(a) filterless additive",enc_plain)
run("(b) haplography deletion",enc_haplo)
run("(c) null insertion",enc_nullins)
print("elapsed %.0fs"%(time.time()-t))
