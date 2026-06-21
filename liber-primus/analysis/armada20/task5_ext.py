import sys, json
sys.path.insert(0, "/mnt/c/Users/dukot/projects/cicada3301/liber-primus/src")
sys.path.insert(0, "/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis")
from lp import gematria as gp
from lp import score as _score
from run_stats import load_pages
N=gp.N; SC=_score.default(); UNS=load_pages()[:-2]
KW=["DIVINITY","PRIMES","CIRCUMFERENCE","FIRFUMFERENFE","CICADA","TOTIENT","SACRED","WISDOM","TRUTH"]
def primes(k):
    o,n=[],2
    while len(o)<k:
        if all(n%p for p in o if p*p<=n): o.append(n)
        n+=1
    return o
def vig(ix,ki,sg): L=len(ki); return [(c+sg*ki[i%L])%N for i,c in enumerate(ix)]
best={"score":-999}
kwi={w:gp.keyword_to_indices(w) for w in KW}
for pi,pg in enumerate(UNS):
    n=len(pg)
    for nc in range(2,14):
        nr=(n+nc-1)//nc
        pr=primes(nc)
        # column read order by raw prime value rank (identity) AND by prime-derived perm
        for perm_name,order in [("rank",sorted(range(nc),key=lambda c:pr[c])),
                                ("revrank",sorted(range(nc),key=lambda c:-pr[c])),
                                ("primemodn",sorted(range(nc),key=lambda c:(pr[c]%n,c)))]:
            # write COLUMN-wise (fill down columns), read ROW-wise in col order -> classic columnar transposition
            # build grid row-major then read columns in 'order'
            for mode in ("rowwrite_colread","colwrite_rowread"):
                if mode=="rowwrite_colread":
                    out=[]
                    for c in order:
                        j=c
                        while j<n: out.append(pg[j]); j+=nc
                else:
                    # column-write: place sequentially down columns
                    grid=[[None]*nc for _ in range(nr)]
                    k=0
                    for c in order:
                        for r in range(nr):
                            if k<n: grid[r][c]=pg[k]; k+=1
                    out=[grid[r][c] for r in range(nr) for c in range(nc) if grid[r][c] is not None]
                for atb in (False,True):
                    base=[(N-1-c) if atb else c for c in out]
                    for w in KW:
                        for sg in (-1,1):
                            d=vig(base,kwi[w],sg)
                            s=SC.score_norm(gp.indices_to_translit(d))
                            if s>best["score"]:
                                best={"score":round(s,4),"page":pi,"ncols":nc,"perm":perm_name,"mode":mode,"key":w,"sign":sg,"atb":atb,"pt":gp.indices_to_translit(d)[:90]}
print("EXT best:",json.dumps(best))
print("baseline=-6.23")
