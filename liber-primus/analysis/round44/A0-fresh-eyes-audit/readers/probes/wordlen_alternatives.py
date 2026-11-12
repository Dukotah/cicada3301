# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
"""Fork I: can nulls explain LP2's word-length shape instead of an unfolded-TH orthography?
(i) strip all 458 F runes from LP2 (the 'every F is a null' reading) and re-test against O1-folded English windows.
(ii) take O1-folded English windows and insert nulls uniformly per rune slot at rate q; best q by G against LP2."""
import re, sys, math, glob, os, unicodedata, random
import numpy as np
sys.path.insert(0,_PROBES)
from lpdata import *
M1=('ING','EA','IA','IO','AE','OE','NG','EO','TH')
def runelen(w,multi=M1):
    w=w.upper().replace('QU','CW').replace('Q','C').replace('K','C').replace('V','U').replace('Z','S')
    n=i=0
    while i<len(w):
        for m in multi:
            if w.startswith(m,i): i+=len(m); break
        else: i+=1
        n+=1
    return n
P=unsolved_pages(); words=[]
for p in P:
    cur=[]
    for k,r in enumerate(p):
        if k>0 and (('-' in r['pre']) or ('.' in r['pre'])): words.append(cur); cur=[]
        cur.append(r['i'])
    words.append(cur)
W=len(words)
def prof(lens): return np.bincount(np.minimum(lens,12),minlength=13)[1:].astype(float)
lp2=prof(np.array([len(w) for w in words]))
strip=[len([x for x in w if x!=0]) for w in words]; strip=np.array([s for s in strip if s>0])
lp2s=prof(strip)
print("LP2 raw      n=%d f1=%.3f f2=%.3f f3=%.3f mean=%.3f"%(W,lp2[0]/W,lp2[1]/W,lp2[2]/W,sum(len(w) for w in words)/W))
print("LP2 F-strip  n=%d f1=%.3f f2=%.3f f3=%.3f mean=%.3f"%(len(strip),lp2s[0]/len(strip),lp2s[1]/len(strip),lp2s[2]/len(strip),strip.mean()))
def G2(a,b):
    g=0; na=a.sum(); nb=b.sum()
    for x,y in zip(a,b):
        t=x+y
        if t==0: continue
        ea=t*na/(na+nb); eb=t*nb/(na+nb)
        if x>0: g+=2*x*math.log(x/ea)
        if y>0: g+=2*y*math.log(y/eb)
    return g
K=_ROOT+'/liber-primus/data/keys/'
files=sorted(glob.glob(K+'armada18/*.txt')+glob.glob(K+'armada19/*.txt'))+[K+'self_reliance.txt']
rng=np.random.default_rng(3301)
tot=0; okS=0; minS=1e9; f2S=0
qs=[0.02,0.04,0.06,0.08,0.10,0.12,0.14]; okQ={q:0 for q in qs}; minQ={q:1e9 for q in qs}; totQ=0
for f in files:
    b=os.path.basename(f)
    if any(s in b for s in ('latin','lp1_','cicada_','runes')): continue
    t=open(f,encoding='utf-8',errors='ignore').read()
    t=unicodedata.normalize('NFKD',t); t=''.join(ch for ch in t if not unicodedata.combining(ch))
    ws=[w.replace("'",'') for w in re.findall(r"[A-Za-z']+",t)]; ws=[w for w in ws if w][1500:]
    if len(ws)<W+800: continue
    Ls=np.array([runelen(w) for w in ws])
    for s in range(0,len(Ls)-W,400):
        win=Ls[s:s+W]; pr=prof(win); tot+=1
        g=G2(pr,lp2s); minS=min(minS,g); okS+=(g<=22.4); f2S+=(pr[1]/W<=lp2s[1]/len(strip))
        if (s//400)%4==0:     # subsample for the null-insertion model
            totQ+=1
            for q in qs:
                # nulls: each word of length L gains Binomial(L+1? , q) -> use L slots (null placed before each rune w.p. q)
                add=rng.binomial(win,q); g2=G2(prof(win+add),lp2); minQ[q]=min(minQ[q],g2); okQ[q]+=(g2<=22.4)
print(f"(i) F-stripped LP2 vs O1 windows: {tot} windows; compatible (G<=22.4): {okS}; min G {minS:.1f}; windows with f2<=stripped-LP2 f2: {f2S}")
print(f"(ii) O1 English + uniform nulls at rate q vs raw LP2 ({totQ} windows each):")
for q in qs: print(f"     q={q:.2f}: compatible {okQ[q]:5d} ({100*okQ[q]/totQ:.1f}%), min G {minQ[q]:.1f}")
