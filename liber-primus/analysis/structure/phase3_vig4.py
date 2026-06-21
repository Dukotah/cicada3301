import sys, itertools, json, time
sys.path.insert(0, '/mnt/c/Users/dukot/projects/cicada3301/liber-primus')
import src.lp.gematria as g, src.lp.score as sc
scorer = sc.default()
raw = open('/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/krisyotam_runes.txt', encoding='utf-8').read()
pages = raw.split('%')
N=29
# Build single-char translit for fast scoring. Many translits are multichar (TH, NG, EO, IA, OE, AE, EA).
# Use score directly. To make 707k*14 tractable, precompute per-position decoded translit lists.
TR = g.IDX_TO_TRANS
sf = scorer.score_norm

best={}
t0=time.time()
for pg in range(0,14):
    idx = g.runes_to_indices(pages[pg])
    n=len(idx)
    # Precompute, for each key index value v (0..28) and position phase, the translit char.
    # decoded char at pos i with key k = TR[(idx[i]-k)%N]
    # Build table[v][i] = TR string
    table=[[TR[(idx[i]-v)%N] for i in range(n)] for v in range(N)]
    bscore=-999;bkey=None;btext=''
    for k0,k1,k2,k3 in itertools.product(range(N),repeat=4):
        # build string by phase
        parts=[]
        ap=parts.append
        ks=(k0,k1,k2,k3)
        t0v=table[k0];t1v=table[k1];t2v=table[k2];t3v=table[k3]
        s=''.join(t0v[i] if i%4==0 else t1v[i] if i%4==1 else t2v[i] if i%4==2 else t3v[i] for i in range(n))
        sc_=sf(s)
        if sc_>bscore:
            bscore=sc_;bkey=ks;btext=s
    best[pg]=(bscore,bkey,btext)
    print('page %d L4 best: %.3f key=%s elapsed=%.0fs'%(pg,bscore,bkey,time.time()-t0))
    sys.stdout.flush()

with open('/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/structure/phase3_vig4.json','w') as f:
    json.dump({str(k):[round(v[0],4),list(v[1]),v[2][:120]] for k,v in best.items()},f,indent=1)
print("VIG L4 DONE")
