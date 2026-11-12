# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
"""Fork I quick check: cleartext word-length profile of LP2 vs candidate plaintext registers (keyless).
Runic length of a word = number of Gematria-Primus runes after greedy digraph folding."""
import re, sys, math, collections, unicodedata
sys.path.insert(0,_PROBES)
from lpdata import *
K=_ROOT+'/liber-primus/data/keys/'
def runelen(w, ing=True):
    w=w.upper().replace('QU','CW').replace('Q','C').replace('K','C').replace('V','U').replace('Z','S')
    n=0;i=0
    while i<len(w):
        if ing and w.startswith('ING',i): n+=1;i+=3;continue
        if w[i:i+2] in ('TH','EO','NG','OE','AE','IA','IO','EA'): n+=1;i+=2;continue
        n+=1;i+=1
    return n
def prof(path, ing=True, maxw=200000, skip=2000):
    t=open(path,encoding='utf-8',errors='ignore').read()
    t=unicodedata.normalize('NFKD',t); t=''.join(ch for ch in t if not unicodedata.combining(ch))
    ws=re.findall(r"[A-Za-z']+",t)[skip:skip+maxw]
    ws=[w.replace("'",'') for w in ws]; ws=[w for w in ws if w]
    c=collections.Counter(min(runelen(w,ing),14) for w in ws)
    return c,len(ws)
P=unsolved_pages(); words=[];
for p in P:
    cur=[]
    for k,r in enumerate(p):
        if k>0 and (('-' in r['pre']) or ('.' in r['pre'])): words.append(cur); cur=[]
        cur.append(r['i'])
    words.append(cur)
lp2=collections.Counter(min(len(w),14) for w in words); n2=sum(lp2.values())
print("LP2: words %d mean %.3f  pct by len 1..10:"%(n2,sum(k*v for k,v in lp2.items())/n2),[round(100*lp2[k]/n2,1) for k in range(1,11)])
cands=[("LP1 plaintext (solved)",K+'solved_plaintext.txt',0),("LP1 english fwd",K+'armada18/lp1_english_forward.txt',0),
 ("EN Emerson essays",K+'armada18/emerson_essays_first_series.txt',2000),("EN KJV Genesis",K+'armada18/kjb_genesis.txt',2000),("EN KJV John",K+'armada18/kjb_gospel_john.txt',2000),
 ("EN Poe",K+'armada18/poe_complete_works.txt',2000),("EN Moby Dick",K+'armada18/melville_moby_dick.txt',2000),("EN Self-Reliance",K+'self_reliance.txt',200),
 ("EN Crowley Book of Law",K+'armada18/crowley_book_of_the_law_hermetic.txt',500),("EN koans+LP sections",K+'armada18/cicada_koans_and_lp_sections.txt',0),
 ("LATIN Virgil Aeneid",K+'armada19/virgil_aeneid_latin.txt',2000),("WELSH (frozen substitute)",_ROOT+'/liber-primus/analysis/round36/P1-panel-r36/inputs_frozen/welsh_mabinogion.txt',2000),
 ("OE rune poem",K+'runepoem_oe.txt',0)]
rows=[]
for name,path,skip in cands:
    try: c,n=prof(path,True,skip=skip)
    except Exception as e: print(name,'ERR',e); continue
    if n<150: print(name,'too short',n); 
    # G-test of LP2 counts against corpus proportions (add-0.5 smoothing)
    tot=n+0.5*14; G=0; 
    for k in range(1,15):
        pk=(c.get(k,0)+0.5)/tot; o=lp2.get(k,0)
        if o>0: G+=2*o*math.log(o/(n2*pk))
    mean=sum(k*v for k,v in c.items())/n
    rows.append((G,name,n,mean,[round(100*c.get(k,0)/n,1) for k in range(1,11)]))
for G,name,n,mean,pct in sorted(rows):
    print(f"G={G:8.1f} (13 df)  {name:28s} n={n:6d} mean={mean:.3f}  {pct}")
