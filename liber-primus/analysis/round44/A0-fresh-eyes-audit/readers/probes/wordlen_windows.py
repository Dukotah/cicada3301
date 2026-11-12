# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
"""Fork I: like-sized-passage test of LP2's cleartext word-length SHAPE (not just the mean).
For every local English text: slide a 2,928-word window; record 2-rune-word fraction f2, mean length, and the
two-sample G statistic against LP2's profile, under three plaintext orthographies:
  O1 = LP1 convention (greedy digraph folding ING,EA,IA,IO,AE,OE,NG,EO,TH)   [what every panel register assumes]
  O2 = same but TH NOT folded
  O3 = no folding at all (one rune per letter)"""
import re, sys, math, collections, glob, os, unicodedata
import numpy as np
sys.path.insert(0,_PROBES)
from lpdata import *
M1=('ING','EA','IA','IO','AE','OE','NG','EO','TH'); M2=tuple(m for m in M1 if m!='TH'); M3=()
def runelen(w,multi):
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
L2=np.array([min(len(w),12) for w in words]); W=len(L2)
lp2=np.bincount(L2,minlength=13)[1:].astype(float)
f2_lp2=lp2[1]/W; mean_lp2=sum(len(w) for w in words)/W
print("LP2 W=%d f1=%.3f f2=%.3f f3=%.3f mean=%.3f"%(W,lp2[0]/W,f2_lp2,lp2[2]/W,mean_lp2))
K=_ROOT+'/liber-primus/data/keys/'
files=sorted(glob.glob(K+'armada18/*.txt')+glob.glob(K+'armada19/*.txt'))+[K+'self_reliance.txt']
skipnames=('latin','lp1_','cicada_','runes')
def G2(a,b):
    # two-sample G over bins with pooled expectation
    g=0; na=a.sum(); nb=b.sum()
    for x,y in zip(a,b):
        t=x+y
        if t==0: continue
        ea=t*na/(na+nb); eb=t*nb/(na+nb)
        if x>0: g+=2*x*math.log(x/ea)
        if y>0: g+=2*y*math.log(y/eb)
    return g
res={}
for name,multi in (('O1-folded',M1),('O2-noTH',M2),('O3-letters',M3)):
    tot_w=0; n_f2=0; n_joint=0; minG=(1e9,None); allG=[]; nt=0; nt_f2=0; per=[]
    for f in files:
        b=os.path.basename(f)
        if any(s in b for s in skipnames): continue
        t=open(f,encoding='utf-8',errors='ignore').read()
        t=unicodedata.normalize('NFKD',t); t=''.join(ch for ch in t if not unicodedata.combining(ch))
        ws=[w.replace("'",'') for w in re.findall(r"[A-Za-z']+",t)]
        ws=[w for w in ws if w][1500:]           # skip licence/front matter
        if len(ws)<W+800: continue
        Ls=np.array([min(runelen(w,multi),12) for w in ws])
        onehot=np.zeros((len(Ls)+1,13)); onehot[np.arange(1,len(Ls)+1),Ls]=1; cs=onehot.cumsum(0)
        raw=np.array([runelen(w,multi) for w in ws]); cr=np.concatenate([[0],raw.cumsum()])
        nt+=1; hit=False; gs=[]
        for s in range(0,len(Ls)-W,400):
            prof=(cs[s+W]-cs[s])[1:]; f2=prof[1]/W; mean=(cr[s+W]-cr[s])/W
            g=G2(prof,lp2); gs.append(g); tot_w+=1
            if f2<=f2_lp2: n_f2+=1; hit=True
            if f2<=f2_lp2 and mean>=mean_lp2: n_joint+=1
            if g<minG[0]: minG=(g,b,round(f2,3),round(mean,3))
        nt_f2+=hit; allG+=gs; per.append((min(gs),b))
    allG=np.array(allG)
    print(f"{name}: texts {nt}, windows {tot_w}; windows with f2<=LP2: {n_f2} ({100*n_f2/tot_w:.2f}%) in {nt_f2} texts; "
          f"f2<=LP2 & mean>=LP2: {n_joint}; min G {minG}; median G {np.median(allG):.0f}; G<=22.4 (p>0.05 @13df approx): {(allG<=22.4).sum()} windows")
    per.sort(); print("    closest texts:",[(round(g,1),b[:28]) for g,b in per[:6]])
