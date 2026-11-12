# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
import sys, math, collections, random
sys.path.insert(0,_PROBES)
from lpdata import *
P=unsolved_pages(); U=flat(P); N=len(U)
def ioc29(xs):
    c=collections.Counter(xs); n=len(xs)
    return 29*sum(v*(v-1) for v in c.values())/(n*(n-1))
# (1) column IoC at page starts and page ends
print("(1) page-start column IoC*29 (n=55 each; noise sd ~0.136):")
print("   start:", [round(ioc29([p[j]['i'] for p in P if len(p)>j]),2) for j in range(0,24)])
pool=[]; 
for j in range(0,12): pool+= [ (j,p[j]['i']) for p in P]
# pooled: sum over columns of coincidences
def pooled(cols):
    num=0; den=0
    for col in cols:
        c=collections.Counter(col); n=len(col)
        num+=sum(v*(v-1) for v in c.values()); den+=n*(n-1)
    return 29*num/den, den/2
for a,b in ((0,6),(0,12),(0,24),(24,48)):
    v,npairs=pooled([[p[j]['i'] for p in P if len(p)>j] for j in range(a,b)])
    sd=math.sqrt(28)/math.sqrt(npairs)   # sd of 29*coinc rate ~ sqrt(29*28/29... ) approx
    print(f"   pooled cols {a}..{b-1}: IoC*29={v:.3f}  pairs={npairs:.0f}  approx z={(v-1)/ (math.sqrt(28)/math.sqrt(npairs)):+.2f}")
# line-start columns (604 lines)
lines=[]
for p in P:
    cur=[]
    for r in p:
        if '/' in r['pre'] and cur: lines.append(cur); cur=[]
        cur.append(r['i'])
    if cur: lines.append(cur)
print("   n lines",len(lines))
for a,b in ((0,1),(0,4),(0,8)):
    v,npairs=pooled([[l[j] for l in lines if len(l)>j] for j in range(a,b)])
    print(f"   line-start cols {a}..{b-1}: IoC*29={v:.3f} pairs={npairs:.0f} z={(v-1)/(math.sqrt(28)/math.sqrt(npairs)):+.2f}")
# sentence-start and word-start first runes
ss=[r['i'] for p in P for k,r in enumerate(p) if k==0 or '.' in r['pre']]
ws=[r['i'] for p in P for k,r in enumerate(p) if k==0 or '-' in r['pre'] or '.' in r['pre']]
we=[p[k-1]['i'] for p in P for k,r in enumerate(p) if k>0 and ('-' in r['pre'] or '.' in r['pre'])]
for nm,x in (("sentence-initial",ss),("word-initial",ws),("word-final",we)):
    c=collections.Counter(x); n=len(x); chi=sum((c.get(i,0)-n/29)**2/(n/29) for i in range(29))
    print(f"   {nm}: n={n} IoC*29={ioc29(x):.3f} chi2={chi:.1f}/28df")
# (2) per-page lag-11 equality
obs=[];exp=[]
for p in P:
    x=[r['i'] for r in p]
    obs.append(sum(1 for k in range(11,len(x)) if x[k]==x[k-11])); exp.append((len(x)-11)/29)
chi=sum((o-e)**2/e for o,e in zip(obs,exp))
print("(2) lag-11 per-page obs:",obs)
print("    total %d exp %.1f ; dispersion chi2 %.1f on %d df; pages with 0-2: %d"%(sum(obs),sum(exp),chi,len(P),sum(1 for o in obs if o<=2)))
# (3) repeated n-grams within flat stream vs expectation (uniform w/ doublet hole approx via shuffle of deltas)
def rep_pairs(x,n):
    c=collections.Counter(tuple(x[i:i+n]) for i in range(len(x)-n+1))
    return sum(v*(v-1)//2 for v in c.values())
rng=random.Random(1)
def surrogate():
    # preserve delta multiset (keeps doublet count), random order, random start
    d=[(U[i]-U[i-1])%29 for i in range(1,N)]; rng.shuffle(d)
    x=[rng.randrange(29)]
    for v in d: x.append((x[-1]+v)%29)
    return x
for n in (2,3,4,5,6):
    o=rep_pairs(U,n); s=[rep_pairs(surrogate(),n) for _ in range(60)]
    m=sum(s)/len(s); sd=(sum((v-m)**2 for v in s)/len(s))**.5
    print(f"(3) repeated {n}-gram pairs: obs {o}  surrogate {m:.1f} +- {sd:.1f}  z={(o-m)/sd if sd else 0:+.2f}")
