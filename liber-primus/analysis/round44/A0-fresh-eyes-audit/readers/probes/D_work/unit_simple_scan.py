# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
"""Fork D probe: is LP2 a MIXTURE?  Score every sentence unit and every line under the 58 keyless reads LP1 actually used
(shift 0..28 x {identity, atbash}) with English quadgrams, against a length-matched uniform-rune null of the same max-over-58
statistic.  A handful of simply-enciphered units hidden among OTP-class text would be invisible to every global statistic."""
import sys, math, random, collections
sys.dont_write_bytecode=True
sys.path.insert(0,_PROBES)
from lpdata import *
Q={}; tot=0
for ln in open(REPO+'/data/english_quadgrams.txt'):
    q,c=ln.split(); Q[q]=int(c); tot+=int(c)
floor=math.log10(0.01/tot); LQ={q:math.log10(c/tot) for q,c in Q.items()}
def score(idx):
    s=''.join(TR[i] for i in idx)
    if len(s)<4: return -99
    return sum(LQ.get(s[i:i+4],floor) for i in range(len(s)-3))/(len(s)-3)
def best58(u):
    b=-99;arg=None
    for atb in (0,1):
        v=[(28-x) for x in u] if atb else u
        for sh in range(29):
            sc=score([(x+sh)%29 for x in v])
            if sc>b: b=sc;arg=(atb,sh)
    return b,arg
P=unsolved_pages()
sent=[];lines=[]
for pi,p in enumerate(P):
    cs=[];cl=[]
    for k,r in enumerate(p):
        if k>0 and '.' in r['pre']: sent.append((pi,cs)); cs=[]
        if k>0 and '/' in r['pre']: lines.append((pi,cl)); cl=[]
        cs.append(r['i']); cl.append(r['i'])
    sent.append((pi,cs)); lines.append((pi,cl))
rng=random.Random(7)
nullcache={}
def nullq(L,n=300):
    Lb=min(L,60) if L<=60 else (80 if L<=100 else 150)
    if Lb not in nullcache:
        nullcache[Lb]=sorted(best58([rng.randrange(29) for _ in range(Lb)])[0] for _ in range(n))
    return nullcache[Lb]
for name,U in (('sentence',sent),('line',lines)):
    rows=[]
    for pi,u in U:
        if len(u)<8: continue
        b,arg=best58(u); nq=nullq(len(u)); mu=sum(nq)/len(nq); sd=(sum((x-mu)**2 for x in nq)/len(nq))**.5
        rows.append(((b-mu)/sd,b,pi,len(u),arg,''.join(TR[(( (28-x) if arg[0] else x)+arg[1])%29] for x in u)[:60]))
    rows.sort(reverse=True)
    zs=[r[0] for r in rows]
    print(name,'units scored',len(rows),'max z %.2f'%zs[0],'mean z %.2f'%(sum(zs)/len(zs)),'n z>3:',sum(z>3 for z in zs),'n z>4:',sum(z>4 for z in zs))
    for r in rows[:4]: print('   z=%.2f score=%.2f page=%d len=%d read=%s  %s'%(r[0],r[1],r[2],r[3],r[4],r[5]))
# positive control: plant a real English sentence under shift 11 + atbash
pt="THEPRIMESARESACREDTHETOTIENTFUNCTIONISSACRED"
import re
GPm=[('ING','NG'),('TH','TH'),('EO','EO'),('NG','NG'),('OE','OE'),('AE','AE'),('IA','IA'),('IO','IA'),('EA','EA')]
def w2r(w):
    out=[];i=0
    while i<len(w):
        for e,r in GPm:
            if w.startswith(e,i): out.append(TR.index(r)); i+=len(e); break
        else:
            ch={'K':'C','V':'U','Q':'C','Z':'S'}.get(w[i],w[i]); out.append(TR.index(ch)); i+=1
    return out
pr=w2r(pt); ct=[(28-((x-11)%29)) for x in pr]
b,arg=best58(ct); nq=nullq(len(ct)); mu=sum(nq)/len(nq); sd=(sum((x-mu)**2 for x in nq)/len(nq))**.5
print('control plant: len',len(ct),'z=%.1f'%((b-mu)/sd),'arg',arg)
