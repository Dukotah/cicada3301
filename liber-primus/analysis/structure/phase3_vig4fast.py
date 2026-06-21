import sys, json, time, itertools
import numpy as np
sys.path.insert(0,'/mnt/c/Users/dukot/projects/cicada3301/liber-primus')
import src.lp.gematria as g, src.lp.score as sc
scorer=sc.default()
raw=open('/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/krisyotam_runes.txt',encoding='utf-8').read()
pages=raw.split('%')
N=29
# Map each rune index -> a single letter code 0..25 for fast quadgram.
# Use first char of translit. Build a dense 26^4 quadgram float array from the KJV dict
# by collapsing multi-char and re-summing. We approximate using single first-letter.
TR=g.IDX_TO_TRANS
A2I={c:i for i,c in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}
idx_letter=[A2I[TR[i][0]] for i in range(N)]  # 0..25

# Build dense quadgram array over 26 letters from scorer dict (which keys are 4-letter latin).
floor=scorer.floor
qd=scorer.d
arr=np.full((26,26,26,26),floor,dtype=np.float32)
for k,v in qd.items():
    if len(k)==4 and all(c in A2I for c in k):
        arr[A2I[k[0]],A2I[k[1]],A2I[k[2]],A2I[k[3]]]=v

def fast_score(codes):
    # codes: int array of letter codes; quadgram sum
    if len(codes)<4: return -999
    c=codes
    s=arr[c[:-3],c[1:-2],c[2:-1],c[3:]].sum()
    return s/(len(codes)-3)

best={}
t0=time.time()
for pg in range(0,14):
    ridx=np.array(g.runes_to_indices(pages[pg]))
    n=len(ridx)
    # decoded rune index for key value v at pos i: (ridx - v) %29 -> letter code
    # table[v] = letter codes array
    table=np.array([[idx_letter[(ridx[i]-v)%N] for i in range(n)] for v in range(N)])  # 29 x n
    bscore=-999;bkey=None
    phase=np.arange(n)%4
    for k0,k1,k2,k3 in itertools.product(range(N),repeat=4):
        codes=np.where(phase==0,table[k0],np.where(phase==1,table[k1],np.where(phase==2,table[k2],table[k3])))
        s=fast_score(codes)
        if s>bscore:
            bscore=s;bkey=(k0,k1,k2,k3)
    # recompute true multichar score for best key
    kl=bkey
    t=''.join(TR[(ridx[i]-kl[i%4])%N] for i in range(n))
    best[pg]=(round(scorer.score_norm(t),4),list(bkey),t[:120])
    print('page %d L4 best fast=%.3f true=%.3f key=%s elapsed=%.0fs'%(pg,bscore,best[pg][0],bkey,time.time()-t0),t[:30])
    sys.stdout.flush()
with open('/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/structure/phase3_vig4.json','w') as f:
    json.dump({str(k):v for k,v in best.items()},f,indent=1)
print("VIG L4 DONE")
