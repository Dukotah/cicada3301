# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
import re, glob, os, numpy as np, collections, sys, io
_o=sys.stdout; sys.stdout=io.StringIO()
from wl_check import enc, wl as LP
sys.stdout=_o
D=_ROOT+'/liber-primus/data/keys/armada18/'
def core(t):
    s=re.search(r"\*\*\*\s*START OF.*?\*\*\*",t,flags=re.S|re.I); e=re.search(r"\*\*\*\s*END OF",t,flags=re.I)
    return t[(s.end() if s else 0):(e.start() if e else len(t))]
def both(t):
    ws=[w.replace("'","") for w in re.findall(r"[A-Za-z']+",t)]; ws=[w for w in ws if w]
    return np.array([enc(w) for w in ws]), np.array([len(w) for w in ws])
def ks(x,y):
    m=16; cx=np.cumsum(np.bincount(np.minimum(x,m),minlength=m+1))/len(x); cy=np.cumsum(np.bincount(np.minimum(y,m),minlength=m+1))/len(y)
    return float(np.abs(cx-cy).max())
def fr(x): 
    h=np.bincount(np.minimum(x,9),minlength=10)/len(x); return " ".join("%4.1f"%(100*h[k]) for k in range(1,9))
print("X %-36s %6s  mean   KS    | pct of words with length 1..8"%("source/encoding","n"))
print("X %-36s %6d  %.3f  ----  | %s"%("LP2 unsolved (observed)",len(LP),LP.mean(),fr(LP)))
cic=""
for f in ('cicada_koans_and_lp_sections.txt','cicada_2012_2013_puzzle_texts.txt','cicada_pgp_messages.txt'): cic+=open(D+f,encoding='utf-8',errors='ignore').read()+"\n"
rows=[]
texts={'CICADA own prose (pooled)':cic}
for p in sorted(glob.glob(D+'*.txt')):
    b=os.path.basename(p)
    if b.startswith(('cicada','lp1')): continue
    texts[b[:30]]=core(open(p,encoding='utf-8',errors='ignore').read())
for name,t in texts.items():
    a,b=both(t)
    if len(a)<1400: continue
    rows.append((ks(LP,a),name+' [multigraph]',len(a),a.mean(),fr(a)))
    rows.append((ks(LP,b),name+' [letters]',len(b),b.mean(),fr(b)))
rows.sort()
for r in rows[:16]: print("X %-36s %6d  %.3f  %.4f | %s"%(r[1][:36],r[2],r[3],r[0],r[4]))
print("X ...")
for r in rows:
    if r[1].startswith('CICADA') or 'emerson_essays_first' in r[1]: print("X %-36s %6d  %.3f  %.4f | %s"%(r[1][:36],r[2],r[3],r[0],r[4]))
nl=sum(1 for r in rows[:16] if 'letters' in r[1]); print("X top-16 best fits: %d letters-encodings, %d multigraph-encodings; KS crit(.05) vs large corpus ~ %.4f"%(nl,16-nl,1.36/np.sqrt(len(LP))))
mg=[r for r in rows if 'multigraph' in r[1]]; print("X best multigraph fit:",mg[0][1],"KS %.4f mean %.3f"%(mg[0][0],mg[0][3]))
