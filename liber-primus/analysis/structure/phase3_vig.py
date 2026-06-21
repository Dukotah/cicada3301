import sys, itertools, json
sys.path.insert(0, '/mnt/c/Users/dukot/projects/cicada3301/liber-primus')
import src.lp.gematria as g, src.lp.score as sc
scorer = sc.default()
raw = open('/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/krisyotam_runes.txt', encoding='utf-8').read()
pages = raw.split('%')
N=29
TR = g.IDX_TO_TRANS  # index -> latin translit string

# Precompute per-page decode without interrupters (fast): work on index list,
# score via building translit string. For speed we score using a custom quadgram
# directly on the translit. But multi-char translits make positions tricky;
# we'll just join translits and use scorer.score_norm.

# For length 1-4 exhaustive we need speed. Build a fast scorer on the joined translit.
def decode_score(idx, key):
    kl=len(key)
    out=[]
    ap=out.append
    for i,c in enumerate(idx):
        ap(TR[(c-key[i%kl])%N])
    t=''.join(out)
    return scorer.score_norm(t), t

best={}
for pg in range(0,14):
    idx = g.runes_to_indices(pages[pg])
    bscore=-999; bkey=None; btext=''
    # length 1,2,3
    for L in (1,2,3):
        for key in itertools.product(range(N), repeat=L):
            s,t=decode_score(idx,list(key))
            if s>bscore:
                bscore=s;bkey=key;btext=t
    best[pg]=(bscore,bkey,btext)
    print('page %d L1-3 best: %.3f key=%s'%(pg,bscore,bkey), btext[:40])

with open('/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/structure/phase3_vig123.json','w') as f:
    json.dump({str(k):[round(v[0],4),list(v[1]),v[2][:120]] for k,v in best.items()},f,indent=1)
print("VIG L1-3 DONE")
