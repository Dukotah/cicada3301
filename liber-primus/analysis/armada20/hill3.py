"""Bounded 3x3 Hill search: random sampling + hill-climb. id=16."""
import sys, time, random
sys.path.insert(0, '/mnt/c/Users/dukot/projects/cicada3301/liber-primus/src')
from lp.gematria import runes_to_indices, indices_to_translit
from lp.score import default

MOD = 29
q = default()

def egcd(a,b):
    if b==0: return (a,1,0)
    g,x,y=egcd(b,a%b); return (g,y,x-(a//b)*y)
def modinv(a,m=MOD):
    a%=m; g,x,_=egcd(a,m); return x%m if g==1 else None

def det3(m):
    a,b,c,d,e,f,g,h,i = m
    return (a*(e*i-f*h)-b*(d*i-f*g)+c*(d*h-e*g))%MOD

def invertible3(m):
    return modinv(det3(m)) is not None

def hill_dec3(idx, m):
    a,b,c,d,e,f,g,h,i = m
    out=[]; n=len(idx)-(len(idx)%3)
    for k in range(0,n,3):
        x,y,z=idx[k],idx[k+1],idx[k+2]
        out.append((a*x+b*y+c*z)%MOD)
        out.append((d*x+e*y+f*z)%MOD)
        out.append((g*x+h*y+i*z)%MOD)
    return out

def load_pages():
    t=open('/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/krisyotam_runes.txt').read()
    return [runes_to_indices(p) for p in t.split('%')]

def score_idx(idx):
    return q.score_norm(indices_to_translit(idx))

def rand_inv3():
    while True:
        m=[random.randrange(MOD) for _ in range(9)]
        if invertible3(m): return m

if __name__=="__main__":
    random.seed(1)
    pages=load_pages()
    target=pages[0]
    t0=time.time()
    N_RANDOM=40000
    best=(-999,None)
    for _ in range(N_RANDOM):
        m=rand_inv3()
        s=score_idx(hill_dec3(target,m))
        if s>best[0]: best=(s,m)
    print(f"random {N_RANDOM}: best {best[0]:.3f} in {time.time()-t0:.0f}s")
    # hill-climb from best
    cur=best[1][:]; cs=best[0]
    improved=True; iters=0
    while improved and iters<200:
        improved=False; iters+=1
        for pos in range(9):
            orig=cur[pos]
            for v in range(MOD):
                if v==orig: continue
                cur[pos]=v
                if not invertible3(cur): cur[pos]=orig; continue
                s=score_idx(hill_dec3(target,cur))
                if s>cs: cs=s; orig=v; improved=True
                else: cur[pos]=orig
            cur[pos]=orig
    print(f"after climb {iters} sweeps: {cs:.3f}")
    tr=indices_to_translit(hill_dec3(target,cur))
    cribs=["THE","AND","THAT","WITHIN","DIVINITY","WELCOME","WISDOM","PRIMES","SACRED"]
    print("cribs:", sum(tr.count(c) for c in cribs), "mat:", cur)
    print(tr[:80])
