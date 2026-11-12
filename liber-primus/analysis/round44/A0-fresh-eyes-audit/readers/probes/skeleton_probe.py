# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
"""Fork I EXPLORATORY PROBE (not a pre-registered lane; no ledger weight): word-length skeleton scan of the local
key-text corpus against LP2's cleartext word-length sequence under three orthographies.
O1 = LP1 greedy digraph folding (what Round 8 SKELETON used), O2 = TH unfolded, O3 = no digraph runes.
Exact n-gram match of consecutive word lengths; chance level calibrated by a shuffled LP2 sequence."""
import re, sys, glob, os, unicodedata, random, collections, time
sys.path.insert(0,_PROBES)
from lpdata import *
M1=('ING','EA','IA','IO','AE','OE','NG','EO','TH'); M2=tuple(m for m in M1 if m!='TH')
def runelen(w,multi):
    w=w.replace('QU','CW').replace('Q','C').replace('K','C').replace('V','U').replace('Z','S')
    n=i=0
    while i<len(w):
        for m in multi:
            if w.startswith(m,i): i+=len(m); break
        else: i+=1
        n+=1
    return n
P=unsolved_pages(); seq=[]
for p in P:
    cur=0
    for k,r in enumerate(p):
        if k>0 and (('-' in r['pre']) or ('.' in r['pre'])): seq.append(cur); cur=0
        cur+=1
    seq.append(cur)
N=int(sys.argv[1]) if len(sys.argv)>1 else 12
def grams(s): 
    d=collections.defaultdict(list)
    for i in range(len(s)-N+1): d[tuple(s[i:i+N])].append(i)
    return d
real=grams(seq); rnd=random.Random(3301); sh=seq[:]; rnd.shuffle(sh); null=grams(sh)
K=_ROOT+'/liber-primus/data/keys/'
files=sorted(set(glob.glob(K+'**/*.txt',recursive=True)))
t0=time.time(); tot_words=0
cache={}
for oname,multi in (('O1',M1),('O2',M2),('O3',())):
    hits=[]; nullhits=0; tw=0
    for f in files:
        b=os.path.relpath(f,K)
        if 'runes' in b or 'translit' in b: continue
        if f not in cache:
            t=open(f,encoding='utf-8',errors='ignore').read()
            t=unicodedata.normalize('NFKD',t); t=''.join(ch for ch in t if not unicodedata.combining(ch)).upper()
            cache[f]=[w.replace("'",'') for w in re.findall(r"[A-Z']+",t) if w.replace("'",'')]
        ws=cache[f]; memo={}
        L=[]
        for w in ws:
            v=memo.get(w)
            if v is None: v=memo[w]=runelen(w,multi)
            L.append(v)
        tw+=len(L)
        for i in range(len(L)-N+1):
            g=tuple(L[i:i+N])
            if g in real:
                for j in real[g]:
                    # extend
                    a,bb=i,j; run=N
                    while a+run<len(L) and bb+run<len(seq) and L[a+run]==seq[bb+run]: run+=1
                    back=0
                    while a-back-1>=0 and bb-back-1>=0 and L[a-back-1]==seq[bb-back-1]: back+=1
                    hits.append((run+back,b,i-back,j-back))
            if g in null: nullhits+=len(null[g])
    hits=sorted(set(hits),reverse=True)
    # dedupe overlapping (same diagonal)
    seen=set(); uniq=[]
    for r,b,i,j in hits:
        key=(b,i-j)
        if key in seen: continue
        seen.add(key); uniq.append((r,b,i,j))
    print(f"{oname}: {len(files)} files, {tw} words scanned, N={N}: distinct diagonal matches {len(uniq)} (shuffled-LP2 control raw hits {nullhits}); longest runs: {uniq[:6]}  [{time.time()-t0:.0f}s]",flush=True)
