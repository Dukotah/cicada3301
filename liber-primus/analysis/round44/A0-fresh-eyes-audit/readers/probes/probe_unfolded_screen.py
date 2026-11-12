# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
"""Fork I probe: pf_v4_12 head-screen pass rate for TRUE keys when the English plaintext is unfolded (O2/O3) vs LP1-folded (O1)."""
import os, sys, random
sys.dont_write_bytecode=True
import numpy as np, importlib.util as u
LP=_ROOT+'/liber-primus'
sp=u.spec_from_file_location('pf12',LP+'/analysis/round37/I2-pfv4-12reg/pf_v4_12.py'); pf=u.module_from_spec(sp); sp.loader.exec_module(pf)
sp=u.spec_from_file_location('b2',LP+'/analysis/round32/I1-skipbytwo-decoder/beam_v2.py'); 
sys.path.insert(0,LP+'/analysis/round32/I1-skipbytwo-decoder'); import beam_v2 as B2
TEST=np.load(LP+'/data/panels/testhalves-r36.npz')
UNF={2:(16,8),12:(18,3),21:(9,6),22:(3,18),25:(24,18),27:(10,24),28:(18,24)}
def o2(s):
    o=[]
    for x in s: o.extend(UNF[2] if x==2 else (x,))
    return o
def o3(s):
    o=[]
    for x in s: o.extend(UNF.get(x,(x,)))
    return o
ENC={1:B2.encipher_keyskip1,2:B2.encipher_skip_by_two}
B=int(sys.argv[1]) if len(sys.argv)>1 else 1500
thr=pf.FROZEN['thr']; k=pf.FROZEN['k']; pen=pf.FROZEN['pen']; m=24
for reg in ('EN_MODERN','EN_KJV'):
    arr=TEST[reg].astype(int).tolist()
    for a in (1,2):
        out={}
        for name,fn in (('O1',lambda s:s),('O2',o2),('O3',o3)):
            r=random.Random(7700+a)        # identical windows/keys across orthographies
            Cc=np.zeros((m,B),dtype=np.int32); KK=np.zeros((m+a*k+8,B),dtype=np.int32); nsk=0
            for b in range(B):
                st=r.randrange(0,len(arr)-200); P=fn(arr[st:st+60])[:m]
                K=[r.randrange(29) for _ in range(m+a*k+40)]
                C,info=ENC[a](P,K,0.83,r.randrange(1,10**9)); nsk+=info['n_skips']>0
                Cc[:,b]=C; KK[:,b]=K[:m+a*k+8]
            lse=pf.dp_cols(Cc,KK,k,a,pen,m)
            out[name]=(float((lse>thr['a%d'%a]).mean()), float(np.median(lse)))
        print(reg,'advance',a,'thr %.3f'%thr['a%d'%a],' pass-rate / median lse:',{n:(round(p,3),round(md,2)) for n,(p,md) in out.items()}, 'B=%d'%B, flush=True)
