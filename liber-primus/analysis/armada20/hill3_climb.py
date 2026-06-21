"""3x3 multi-restart hill-climb, several pages. id=16."""
import sys, time, random
sys.path.insert(0,'/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/armada20')
from hill3 import rand_inv3, hill_dec3, score_idx, invertible3, load_pages, MOD
from lp.gematria import indices_to_translit

def climb(target, m):
    cur=m[:]; cs=score_idx(hill_dec3(target,cur))
    improved=True
    while improved:
        improved=False
        for pos in range(9):
            orig=cur[pos]; bestv=orig
            for v in range(MOD):
                if v==orig: continue
                cur[pos]=v
                if not invertible3(cur): continue
                s=score_idx(hill_dec3(target,cur))
                if s>cs: cs=s; bestv=v; improved=True
            cur[pos]=bestv
    return cs,cur

if __name__=="__main__":
    random.seed(7)
    pages=load_pages()
    RESTARTS=60
    for p in [0,2,4]:
        target=pages[p]
        best=(-999,None); t0=time.time()
        for _ in range(RESTARTS):
            s,m=climb(target, rand_inv3())
            if s>best[0]: best=(s,m)
        tr=indices_to_translit(hill_dec3(target,best[1]))
        cribs=["THE","AND","THAT","WITHIN","DIVINITY","WELCOME","WISDOM"]
        print(f"page {p}: best {best[0]:.3f} ({time.time()-t0:.0f}s) cribs={sum(tr.count(c) for c in cribs)}")
        print("  ",tr[:60])
