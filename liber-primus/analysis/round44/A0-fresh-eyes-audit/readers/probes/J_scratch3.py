# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
# Fork J scratch: what does the R42/R43 "rigid decode vs free bar" glue score on a CORRECT key, under the repo's own pinned
# constructions (M1 key-skip, skip_by_two, M2 rewrite, no filter)?  Not a registered lane; a power probe of existing glue.
import os, sys, random, statistics as st
LP=_ROOT+'/liber-primus'
for p in ("analysis","src","analysis/round19/I2","analysis/round34/I1-v3-null","analysis/round19/I1"):
    sys.path.insert(0, os.path.join(LP,p))
import adjudicate as A, bars_v3 as B, constructions as C
PAN=A.Panel(os.path.join(LP,"data","panels","panel-r36.npz"))
N=29
def rigid(Cx,K,sign=-1): return [(Cx[i]+sign*K[i])%N for i in range(len(Cx))]
out={}
for mech in ("nofilter","keyskip","skip_by_two","rewrite"):
    for L in (120,265):
        ps=[]; frac=[]
        for seed in range(12):
            P=C.long_plain(L,seed=seed)
            K=C.key_sha(L*6, seed=("K%d"%seed).encode())
            if mech=="nofilter": Cx=[(P[i]+K[i])%N for i in range(L)]
            elif mech=="keyskip": Cx=C.enc_keyskip(P,K,supp=0.83,seed=seed)
            elif mech=="skip_by_two": Cx=C.enc_skip_by_two(P,K,supp=0.83,seed=seed)
            else: Cx=C.enc_rewrite(P,K,supp=0.83,seed=seed)
            if isinstance(Cx,tuple): Cx=Cx[0]
            Cx=list(Cx)[:L]
            D=rigid(Cx,K)
            r=A.adjudicate(D,pan=PAN)
            ps.append(float(r["pmax"])); frac.append(sum(1 for a,b in zip(D,P) if a==b)/L)
        out[(mech,L)]=(st.mean(ps),min(ps),max(ps),st.mean(frac))
        print(f"{mech:12s} L={L:3d} rigid-correct-key pmax mean {st.mean(ps):6.2f} min {min(ps):6.2f} max {max(ps):6.2f} | rune match {st.mean(frac):.2f}")
for Ngrid in (7200,13800,34668):
    print("free bar N=%d: L120 %.2f  L240 %.2f"%(Ngrid,B.bar_v3(Ngrid,120,"free"),B.bar_v3(Ngrid,240,"free")))
