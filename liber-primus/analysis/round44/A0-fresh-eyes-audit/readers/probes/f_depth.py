# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
"""Fork F quick check: 'in-depth' (same key restarted) kappa tests at page / section / paragraph / line / word alignment.
Language-agnostic: if two units share a key from their start, P(C1_i==C2_i)=kappa_plain(~0.06) instead of 1/29."""
import math, itertools, sys
sys.path.insert(0,_PROBES)
from lpdata import *
RUN="ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
txt=open(REPO+'/data/krisyotam_runes.txt',encoding='utf-8').read()
segs=[s for s in txt.split('%') if any(c in RUN for c in s)][:-2]   # unsolved 55
def units(kind):
    out=[]
    if kind=='page':
        for s in segs: out.append([RUN.index(c) for c in s if c in RUN])
    elif kind in('dollar','amp','line','sentence','word'):
        sep={'dollar':'$','amp':'&$','line':'/','sentence':'.&$','word':'-./&$'}[kind]   # note line: '/' ; pages always break
        cur=[]
        for s in segs:
            for c in s:
                if c in RUN: cur.append(RUN.index(c))
                elif c in sep:
                    if cur: out.append(cur); cur=[]
            if kind in('line','word') and cur: out.append(cur); cur=[]
        if cur: out.append(cur)
    return out
def kappa(U, L, rev=False):
    eq=tot=0
    for a,b in itertools.combinations(U,2):
        if rev: a=a[::-1]; b=b[::-1]
        n=min(len(a),len(b),L)
        for i in range(n):
            tot+=1; eq+= a[i]==b[i]
    if tot==0: return None
    z=(eq-tot/29)/math.sqrt(tot*(1/29)*(28/29))
    return eq,tot,round(100*eq/tot,3),round(z,2)
for kind in ('page','dollar','amp','sentence','line','word'):
    U=units(kind)
    print(kind,'units',len(U),'median len',sorted(len(u) for u in U)[len(U)//2])
    for L in (5,10,20,40,80,300):
        if kind=='word' and L>10: continue
        print('   L=%3d fwd %s   rev(end-aligned) %s'%(L,kappa(U,L),kappa(U,L,True)))
