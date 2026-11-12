# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
import re, sys, numpy as np
sys.path.insert(0,_PROBES)
from lpdata import unsolved_pages
MULTI = ('ING', 'EA', 'IA', 'IO', 'AE', 'OE', 'NG', 'EO', 'TH')
def enc(w):
    w = w.upper(); i = n = 0
    while i < len(w):
        for m in MULTI:
            if w.startswith(m, i):
                i += len(m); n += 1; break
        else:
            if 'A' <= w[i] <= 'Z': n += 1
            i += 1
    return n
# LP2 word lengths from my independent loader
P=unsolved_pages(); wl=[]; 
for p in P:
    cur=0; last=None
    for r in p:
        if r['word']!=last and last is not None:
            wl.append(cur); cur=0
        cur+=1; last=r['word']
    wl.append(cur)
wl=np.array(wl); print("LP2 words",len(wl),"mean %.4f sd %.3f"%(wl.mean(),wl.std()))
import collections
h=collections.Counter(wl); print("LP2 length hist:",[(k,h[k]) for k in sorted(h)])
def prof(name,path):
    t=open(path,encoding='utf-8',errors='ignore').read()
    v=np.array([x for x in (enc(w) for w in re.findall(r"[A-Za-z']+",t)) if x])
    print("%-22s words %6d mean %.4f sd %.3f"%(name,len(v),v.mean(),v.std()), "PG-boilerplate" if 'gutenberg' in t.lower() else "")
    return v
K=_ROOT+'/liber-primus/data/keys/'
sp=prof('solved_plaintext',K+'solved_plaintext.txt'); sr=prof('self_reliance',K+'self_reliance.txt')
# passage-level: self_reliance windows of 2928
n=len(wl)
for name,v in (('self_reliance',sr),('solved_plaintext',sp)):
    if len(v)>n:
        cs=np.concatenate([[0],np.cumsum(v)]); wm=(cs[n:]-cs[:-n])/n
        print(name,"2928-word window means: min %.3f max %.3f ; frac>=4.268: %.3f ; frac>=4.425: %.3f"%(wm.min(),wm.max(),(wm>=4.268).mean(),(wm>=4.425).mean()))
# block bootstrap SE for LP2 mean (blocks of 50 words)
rng=np.random.default_rng(1); B=50; nb=len(wl)//B; blocks=wl[:nb*B].reshape(nb,B).mean(1)
print("LP2 block(50)-bootstrap SE of mean: %.4f"%(blocks.std(ddof=1)/np.sqrt(nb)))
bs=sp[:(len(sp)//B)*B].reshape(-1,B).mean(1); print("solved_plaintext block SE: %.4f (n blocks %d)"%(bs.std(ddof=1)/np.sqrt(len(bs)),len(bs)))
h2=collections.Counter(sp); tot=len(sp)
print("len: LP2%  solved%")
for k in range(1,15): print(" %2d  %5.1f  %5.1f"%(k,100*h[k]/len(wl),100*h2[k]/tot))
