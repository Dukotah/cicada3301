"""Fast experiment A: doublet-prior vs no-prior short-Vigenere, head-to-head.
For each page and key length, compare best score achieved WITH the doublet prior
(several lambdas) vs WITHOUT it. If the prior helps, prior-on should win.
Lean: fewer restarts, all pages, reports both."""
import sys, os, math, random, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from lp import gematria as gp, score as _score
N=gp.N; Q=_score.default(); ENGLISH_DOUBLET=0.0297

def load():
    t=open(os.path.join(os.path.dirname(__file__),"..","..","data","krisyotam_runes.txt")).read()
    return [(i,gp.runes_to_indices(p)) for i,p in enumerate(t.split("%")) if len(gp.runes_to_indices(p))>=40]

def dprior(p):
    n=len(p)-1
    if n<=0: return 0.0
    d=sum(1 for i in range(n) if p[i]==p[i+1])
    return (d*math.log(ENGLISH_DOUBLET)+(n-d)*math.log(1-ENGLISH_DOUBLET))/n

def vig(idxs,key):
    L=len(key); return [(idxs[i]-key[i%L])%N for i in range(len(idxs))]

def hillclimb(idxs,L,lam,restarts,seed):
    rng=random.Random(seed); best=(-99,)
    for _ in range(restarts):
        key=[rng.randrange(N) for _ in range(L)]
        def obj(k):
            p=vig(idxs,k); return Q.score_norm(gp.indices_to_translit(p))+lam*dprior(p)
        cur=obj(key); imp=True
        while imp:
            imp=False
            for pos in range(L):
                bv,bval=key[pos],cur
                for v in range(N):
                    if v==key[pos]: continue
                    key[pos]=v; val=obj(key)
                    if val>bval: bval,bv=val,v
                key[pos]=bv
                if bval>cur: cur=bval; imp=True
        p=vig(idxs,key); qs=Q.score_norm(gp.indices_to_translit(p))
        if qs>best[0]: best=(qs,list(key),gp.indices_to_translit(p)[:50])
    return best

if __name__=="__main__":
    pages=load(); L=3; restarts=12
    agg={"prior_off":-99,"prior_on":-99}
    rows=[]
    for pageno,idxs in pages:
        boff=hillclimb(idxs,L,0.0,restarts,100+pageno)
        bon=(-99,)
        for lam in (10.0,30.0):
            b=hillclimb(idxs,L,lam,restarts,200+pageno)
            if b[0]>bon[0]: bon=b
        agg["prior_off"]=max(agg["prior_off"],boff[0])
        agg["prior_on"]=max(agg["prior_on"],bon[0])
        rows.append((pageno,boff[0],bon[0],boff[2]))
        print(f"p{pageno:2d} off={boff[0]:.3f} on={bon[0]:.3f} | {boff[2][:40]}")
    print("\nAGG best prior_off=%.3f  prior_on=%.3f"%(agg["prior_off"],agg["prior_on"]))
    json.dump({"agg":agg,"rows":rows},open(os.path.join(os.path.dirname(__file__),"fast_A.json"),"w"),indent=2)
