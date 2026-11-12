# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
"""Fork D probe (seconds): are the 86 surviving doublets positioned like occurrences of ONE plaintext rune?
Model family tested ('intrinsic escape'): a deterministic repeat-avoiding cipher in which c_i==c_{i-1} happens exactly
when the plaintext rune at i is a particular rune r (or a class).  Word structure is cleartext in LP2, so under H_r the
doublets' (word length, in-word index) cells must follow English positional frequencies of r.  H_0 = filter model:
doublets land uniformly over rune positions.  LLR_r = sum log p_r(cell)/p_0(cell) over the 86 doublets."""
import sys, re, glob, math, collections, random
sys.dont_write_bytecode=True
sys.path.insert(0,_PROBES)
from lpdata import *
GP=[('ING','NG'),('OE','OE'),('EO','EO'),('IA','IA'),('IO','IA'),('EA','EA'),('AE','AE'),('TH','TH'),('NG','NG'),
    ('F','F'),('U','U'),('V','U'),('O','O'),('R','R'),('C','C'),('K','C'),('G','G'),('W','W'),('H','H'),('N','N'),('I','I'),
    ('J','J'),('P','P'),('X','X'),('S','S'),('Z','S'),('T','T'),('B','B'),('E','E'),('M','M'),('L','L'),('D','D'),('A','A'),('Y','Y'),('Q','C')]
def word2runes(w):
    out=[];i=0
    while i<len(w):
        for e,r in GP:
            if w.startswith(e,i): out.append(TR.index(r)); i+=len(e); break
        else: i+=1
    return out
# --- English corpus: the repo's own prose docs (markdown stripped crudely) + LP1 solved plaintext register is tiny, skip
txt=''
for f in glob.glob(_ROOT+'/research/*.md')+glob.glob(_ROOT+'/puzzles/*.md')+glob.glob(_ROOT+'/identity/*.md')+[_ROOT+'/PAPER.md']:
    t=open(f,encoding='utf-8',errors='ignore').read()
    t=re.sub(r'```.*?```',' ',t,flags=re.S); t=re.sub(r'`[^`]*`',' ',t); t=re.sub(r'https?://\S+',' ',t); t=re.sub(r'\[[^\]]*\]\([^)]*\)',' ',t)
    txt+=' '+t
words=[w for w in re.findall(r"[A-Za-z]+",txt.upper()) if 1<=len(w)<=20]
ew=[word2runes(w) for w in words]; ew=[w for w in ew if w]
print('english words',len(ew),'runes',sum(map(len,ew)))
cnt_all=collections.Counter(); cnt_r=collections.defaultdict(collections.Counter)
WMAX=12
for w in ew:
    L=min(len(w),WMAX)
    for k,r in enumerate(w):
        cell=(L,min(k,WMAX-1)); cnt_all[cell]+=1; cnt_r[r][cell]+=1
# --- LP2 cells
P=unsolved_pages()
Ncell=collections.Counter(); dcells=[]
for p in P:
    # word segmentation: boundary if '-' or '.' (or any marker) in pre
    wid=[];cur=-1
    for r in p:
        if cur<0 or any(ch in r['pre'] for ch in '-.&$§'): cur+=1; 
        wid.append(cur)
    wl=collections.Counter(wid); pos={}; seen=collections.Counter()
    for i,r in enumerate(p):
        k=seen[wid[i]]; seen[wid[i]]+=1
        cell=(min(wl[wid[i]],WMAX),min(k,WMAX-1))
        if i>0:
            Ncell[cell]+=1
            if r['i']==p[i-1]['i']: dcells.append(cell)
print('LP2 pairs',sum(Ncell.values()),'doublets',len(dcells))
tot=sum(Ncell.values()); p0={c:n/tot for c,n in Ncell.items()}
def prof(r):
    f={c:(cnt_r[r].get(c,0)+0.5*0.0345)/(cnt_all.get(c,0)+0.5) for c in Ncell}
    z=sum(Ncell[c]*f[c] for c in Ncell); return {c:Ncell[c]*f[c]/z for c in Ncell}
rng=random.Random(1)
cells=list(Ncell)
res=[]
for r in range(29):
    pr=prof(r)
    llr=sum(math.log(pr[c]/p0[c]) for c in dcells)
    # expected LLR under H_r and under H_0 for n=86, with sd by simulation
    def sim(dist,n=400):
        ws=[dist[c] for c in cells]; out=[]
        for _ in range(n):
            s=rng.choices(cells,weights=ws,k=len(dcells)); out.append(sum(math.log(pr[c]/p0[c]) for c in s))
        m=sum(out)/n; sd=(sum((x-m)**2 for x in out)/n)**.5; return m,sd,out
    mr,sr,outr=sim(pr); m0,s0,out0=sim(p0)
    # power: fraction of H_r sims above the 99th pct of H_0 sims ; p-value of observed under H_r
    thr=sorted(out0)[int(0.99*len(out0))]; power=sum(x>thr for x in outr)/len(outr)
    p_under_r=sum(x<=llr for x in outr)/len(outr)
    freq=sum(cnt_r[r].values())/sum(cnt_all.values())
    res.append((TR[r],freq,llr,mr,sr,m0,s0,power,p_under_r))
print('rune  engfreq   obsLLR   E[LLR|H_r]±sd    E[LLR|H_0]±sd   power@1%  P(LLR<=obs | H_r)')
for t in sorted(res,key=lambda x:-x[2]):
    print(f"{t[0]:3s}  {100*t[1]:5.2f}%  {t[2]:8.1f}   {t[3]:7.1f}±{t[4]:4.1f}   {t[5]:7.1f}±{t[6]:4.1f}    {t[7]:.2f}     {t[8]:.3f}")
