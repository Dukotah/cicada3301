# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
import sys, collections, math, random
sys.path.insert(0,_PROBES)
from lpdata import *
P=unsolved_pages()
# words per page (word = maximal run without '-' or '.'; line breaks do not split words)
words=[]  # (page, wordidx, tuple runes, sentence_end_after?)
for pi,p in enumerate(P):
    cur=[]; 
    for k,r in enumerate(p):
        if k>0 and (('-' in r['pre']) or ('.' in r['pre'])):
            words.append((pi,tuple(cur),'.' in r['pre'])); cur=[]
        cur.append(r['i'])
    words.append((pi,tuple(cur),True))
W=[w for _,w,_ in words]
print("words",len(W),"mean len %.2f"%(sum(map(len,W))/len(W)))
lenhist=collections.Counter(map(len,W)); print("len hist",sorted(lenhist.items()))
# single-word repeats by length: observed pairs vs expected pairs under uniform (29^-L)
print("\nSINGLE-WORD repeats: L  nwords  obs_pairs  exp_pairs(29^-L)  ")
for L in range(1,9):
    ws=[w for w in W if len(w)==L]; c=collections.Counter(ws)
    obs=sum(v*(v-1)//2 for v in c.values()); n=len(ws); exp=n*(n-1)/2*29.0**(-L)
    z=(obs-exp)/math.sqrt(exp) if exp>0 else 0
    print(f"  {L}  {n:5d}  {obs:6d}  {exp:10.3f}  z={z:+.2f}")
    if L>=4 and obs:
        print("      repeats:",[("".join(TR[x]+"." for x in w),v) for w,v in c.items() if v>1])
# word-bigram repeats (consecutive words within a page, no restriction on sentence boundary)
bg=[]  # (sig, content, page, idx)
idx=0
for i in range(len(words)-1):
    if words[i][0]==words[i+1][0]:
        bg.append(((len(words[i][1]),len(words[i+1][1])), words[i][1]+words[i+1][1], words[i][0], i))
sigc=collections.Counter(s for s,_,_,_ in bg)
print("\nWORD-BIGRAM repeats by total length T: obs pairs vs expected")
obsT=collections.Counter(); expT=collections.Counter()
bysig=collections.defaultdict(list)
for s,c,pg,i in bg: bysig[s].append((c,pg,i))
found=[]
for s,lst in bysig.items():
    T=s[0]+s[1]; n=len(lst); expT[T]+=n*(n-1)/2*29.0**(-T)
    cc=collections.defaultdict(list)
    for c,pg,i in lst: cc[c].append((pg,i))
    for c,v in cc.items():
        if len(v)>1:
            obsT[T]+=len(v)*(len(v)-1)//2
            if T>=5: found.append((T,s,"".join(TR[x]+"." for x in c),v))
for T in range(2,13):
    print(f"  T={T:2d} obs {obsT[T]:5d}  exp {expT[T]:10.4f}")
print("  repeats with T>=5:",found)
print("  expected total for T>=6: %.5f ; for T>=5: %.5f"%(sum(v for t,v in expT.items() if t>=6), sum(v for t,v in expT.items() if t>=5)))
# probability that the LAST word-bigram of the book recurs elsewhere
last=bg[-1]; n33=sigc[last[0]]
print("\nlast word-bigram sig",last[0],"content","".join(TR[x]+'.' for x in last[1]),"; # bigrams w/ same sig:",n33," P(recurs)=%.2e"%((n33-1)*29.0**(-sum(last[0]))))
# words total check and sections
