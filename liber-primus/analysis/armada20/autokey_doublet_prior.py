"""Task 15 - Experiment C: doublet-prior over the ONE construction that
produces the deficit (ciphertext-autokey), with the doublet prior actively
selecting the offset K and sign, jointly with quadgram fitness.

ct-autokey decrypt:  p_i = (c_i - c_{i-1} - K) mod 29   (sign=-1)
                or   p_i = (c_{i-1} - c_i - K) ... etc.
We also try plaintext-autokey:  p_i = c_i - p_{i-1} - K  (chained).
The doublet prior rewards decodes whose plaintext doublet rate matches English.
This is the new combination: the open-avenue prior + the doublet-suppressing
family, rather than brute quadgram alone (which prior work did).
"""
import sys, os, re, math, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from lp import gematria as gp, score as _score
N = gp.N
Q = _score.default()
ENGLISH_DOUBLET = 0.0297

def load():
    t = open(os.path.join(os.path.dirname(__file__), "..", "..",
                          "data", "krisyotam_runes.txt")).read()
    out = []
    for i, p in enumerate(t.split("%")):
        idx = gp.runes_to_indices(p)
        if len(idx) >= 40: out.append((i, idx))
    return out

def doublet_rate(p):
    if len(p) < 2: return 0.0
    return sum(1 for i in range(len(p)-1) if p[i]==p[i+1])/(len(p)-1)

def dprior(p):
    n=len(p)-1
    if n<=0: return 0.0
    d=sum(1 for i in range(n) if p[i]==p[i+1])
    return (d*math.log(ENGLISH_DOUBLET)+(n-d)*math.log(1-ENGLISH_DOUBLET))/n

def ct_autokey(c, K, sign, rev=False):
    p=[]
    for i in range(len(c)):
        prev = c[i-1] if i>0 else 0
        if rev: p.append((prev - c[i] - K)%N)
        else:   p.append((c[i] + sign*prev - K)%N)
    return p

def pt_autokey(c, K, sign):
    p=[]; prev=0
    for i in range(len(c)):
        v=(c[i] + sign*prev - K)%N
        p.append(v); prev=v
    return p

if __name__ == "__main__":
    pages=load()
    best_overall=(-99,)
    rows=[]
    for pageno, c in pages:
        bestp=(-99,)
        for K in range(N):
            for sign in (-1,1):
                for rev in (False,True):
                    p=ct_autokey(c,K,sign,rev)
                    qs=Q.score_norm(gp.indices_to_translit(p))
                    comb=qs  # rank by raw English (honest); prior used only to flag
                    if comb>bestp[0]:
                        bestp=(comb,qs,K,sign,'ct',rev,doublet_rate(p),
                               gp.indices_to_translit(p)[:60])
                p=pt_autokey(c,K,sign)
                qs=Q.score_norm(gp.indices_to_translit(p))
                if qs>bestp[0]:
                    bestp=(qs,qs,K,sign,'pt',False,doublet_rate(p),
                           gp.indices_to_translit(p)[:60])
        rows.append((pageno,bestp))
        if bestp[0]>best_overall[0]: best_overall=(bestp[0],pageno,bestp)
        print(f"p{pageno:2d} best={bestp[1]:.3f} K={bestp[2]} sign={bestp[3]} {bestp[4]} dbl={bestp[6]*100:.2f}% {bestp[7][:40]}")
    print("\nBEST OVERALL:", best_overall[0], "page", best_overall[1])
    json.dump([{"page":r[0],"score_norm":r[1][1],"K":r[1][2],"sign":r[1][3],
                "fam":r[1][4],"rev":r[1][5],"dbl":r[1][6],"snip":r[1][7]} for r in rows],
              open(os.path.join(os.path.dirname(__file__),"autokey_doublet.json"),"w"),indent=2)
