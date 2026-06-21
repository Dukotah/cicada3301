import sys; sys.path.insert(0,'src')
from lp import gematria as gp, score as sc
N=gp.N; Q=sc.default()
pages=open('data/krisyotam_runes.txt',encoding='utf-8').read().split('%')
def page_idxs(p):
    return [gp.RUNE_TO_IDX[c] for c in p if c in gp.RUNE_TO_IDX and c!='ᚠ']
def tl(i): return gp.indices_to_translit(i)

# Hypothesis: shift_i = (key[i] + value_of_previous_PLAINTEXT_rune) -- this is autokey, eliminated.
# NEW variant: shift_i = (key[i] XOR-ish combine with index position via gematria) 
# Test "progressive key": shift_i = key[i%len] + i (running offset) mod 29  -- a documented LP1 trick on some pages
def prog_sub(idxs,key,off=1):
    k=gp.keyword_to_indices(key)
    return [(c-(k[i%len(k)]+off*i))%N for i,c in enumerate(idxs)]
def prog_sub_neg(idxs,key,off=1):
    k=gp.keyword_to_indices(key)
    return [(c-(k[i%len(k)]-off*i))%N for i,c in enumerate(idxs)]

keys=['DIVINITY','CIRCUMFERENCE','WELCOME','PILGRIM','ADHERENCE','CABAL','WISDOM','INSTAR','MOBIUS','PRESERVATION','SHADOWS','CONSUMPTION','THESEEKER']
best=(-999,None)
for key in keys:
    for off in [1,-1,2,3]:
        for fn in (prog_sub,prog_sub_neg):
            for pi,p in enumerate(pages):
                idxs=page_idxs(p)
                if len(idxs)<20: continue
                out=fn(idxs,key,off)
                s=Q.score_norm(tl(out))
                if s>best[0]:
                    best=(s,(key,off,fn.__name__,pi,tl(out)[:50]))
print('progressive-key best:',best)
