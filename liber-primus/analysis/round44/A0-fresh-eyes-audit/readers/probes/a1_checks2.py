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
# lines per page
PL=[]
for p in P:
    L=[];cur=[]
    for r in p:
        if '/' in r['pre'] and cur: L.append(cur); cur=[]
        cur.append(r['i'])
    if cur: L.append(cur)
    PL.append(L)
lines=[l for L in PL for l in L]
print("lines",len(lines),"mean len %.1f"%(sum(map(len,lines))/len(lines)))
li=collections.Counter(l[0] for l in lines); lf=collections.Counter(l[-1] for l in lines)
n=len(lines)
print("line-initial counts (exp %.1f):"%(n/29))
print("  "+" ".join(f"{TR[i]}:{li.get(i,0)}" for i in sorted(range(29),key=lambda i:-li.get(i,0))))
print("line-final counts:")
print("  "+" ".join(f"{TR[i]}:{lf.get(i,0)}" for i in sorted(range(29),key=lambda i:-lf.get(i,0))))
chi_i=sum((li.get(i,0)-n/29)**2/(n/29) for i in range(29)); chi_f=sum((lf.get(i,0)-n/29)**2/(n/29) for i in range(29))
print("chi2 initial %.1f final %.1f (28 df)"%(chi_i,chi_f))
# second rune of line, last-but-one
for j,name in ((1,"2nd"),(2,"3rd")):
    c=collections.Counter(l[j] for l in lines if len(l)>j); m=sum(c.values())
    print(name,"chi2 %.1f"%sum((c.get(i,0)-m/29)**2/(m/29) for i in range(29)))
# vertical equality: same index in previous line (within page), offsets -3..3
for off in range(-3,4):
    eq=tot=0
    for L in PL:
        for a,b in zip(L,L[1:]):
            for j in range(len(b)):
                k=j+off
                if 0<=k<len(a):
                    tot+=1; eq+= (a[k]==b[j])
    z=(eq-tot/29)/math.sqrt(tot*28/841)
    print(f"vertical off {off:+d}: eq {eq}/{tot} = {100*eq/tot:.3f}%  z={z:+.2f}")
# right-aligned vertical
eq=tot=0
for L in PL:
    for a,b in zip(L,L[1:]):
        for j in range(1,min(len(a),len(b))+1):
            tot+=1; eq+=(a[-j]==b[-j])
print(f"vertical right-aligned: {eq}/{tot} = {100*eq/tot:.3f}% z={(eq-tot/29)/math.sqrt(tot*28/841):+.2f}")
# per-page lag-11 with poisson tail
def pois_cdf(k,mu): return sum(math.exp(-mu)*mu**i/math.factorial(i) for i in range(k+1))
out=[]
for pi,p in enumerate(P):
    x=[r['i'] for r in p]; o=sum(1 for k in range(11,len(x)) if x[k]==x[k-11]); mu=(len(x)-11)/29
    out.append((pois_cdf(o,mu),pi,len(x),o,round(mu,1)))
out.sort(); print("lowest-tail pages for lag-11 (P(<=obs), page, len, obs, exp):",[(round(a,4),b,c,d,e) for a,b,c,d,e in out[:6]])
# line lengths distribution; pages w/ line length 11?
print("line length histogram:",sorted(collections.Counter(map(len,lines)).items()))
