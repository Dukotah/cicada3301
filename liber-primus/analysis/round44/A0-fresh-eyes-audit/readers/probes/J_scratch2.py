# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
# Fork J scratch: alignment-free matched-filter test for "key uniform on 28 of 29 residues" (totient/prime-stream family)
import sys, collections, math, random
sys.path.insert(0,_ROOT+'/liber-primus/src'); sys.path.insert(0,'.')
from lp import gematria as gp
from lpdata import *
U=flat(unsolved_pages()); N=len(U)
O=[collections.Counter(U)[i] for i in range(29)]
def dist(path):
    t=open(path,encoding='utf-8',errors='ignore').read().upper()
    idx=gp.keyword_to_indices(''.join(ch for ch in t if 'A'<=ch<='Z'))
    c=collections.Counter(idx); n=len(idx); return [c.get(i,0)/n for i in range(29)]
K=_ROOT+'/liber-primus/data/keys/'
for name,pl in (("LP-voice solved plaintext",dist(K+'solved_plaintext.txt')),("Self-Reliance",dist(K+'self_reliance.txt'))):
    print("==",name,"IoC29 %.3f"%(29*sum(x*x for x in pl)))
    res=[]
    for sign in (+1,-1):
        for m in range(29):
            # C = P + sign*K, K uniform on residues != m  -> q_c = (1 - p[(c - sign*m) %29])/28
            q=[(1-pl[(c-sign*m)%29])/28 for c in range(29)]
            # matched filter: T = sum O_c*(q_c-1/29); var under H0 (multinomial uniform)
            w=[qc-1/29 for qc in q]
            T=sum(O[c]*w[c] for c in range(29))
            var=N*(sum(x*x for x in w)/29 - (sum(w)/29)**2)
            z=T/math.sqrt(var); ez=N*sum(x*x for x in w)*29/math.sqrt(N*29*sum(x*x for x in w))  # expected z under H1 ~ sqrt(N*29*sum w^2)
            res.append((z,sign,m,ez))
    res.sort(reverse=True)
    print(" expected z under H1 ~ %.2f"%res[0][3])
    print(" top5 (z, sign, missing residue m):",[(round(z,2),s,m) for z,s,m,_ in res[:5]])
    print(" bottom3:",[(round(z,2),s,m) for z,s,m,_ in res[-3:]])
    named={(1,28):"phi(p)=p-1 mod29, C=P+K",(-1,28):"phi(p), C=P-K",(1,0):"p mod29, C=P+K",(-1,0):"p mod29, C=P-K"}
    for z,s,m,_ in res:
        if (s,m) in named: print("   %-26s z=%+.2f"%(named[(s,m)],z))
print("observed counts:",O)
