# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
import re, glob, os, numpy as np
from wl_check import enc
n=2928; LO=4.268442; HI=4.424863
D=_ROOT+'/liber-primus/data/keys/armada18/'
def wl(t): return np.array([x for x in (enc(w) for w in re.findall(r"[A-Za-z']+",t)) if x])
def win(v):
    cs=np.concatenate([[0],np.cumsum(v)]); wm=(cs[n:]-cs[:-n])/n; return wm
rows=[]
for p in sorted(glob.glob(D+'*.txt')):
    t=open(p,encoding='utf-8',errors='ignore').read()
    has='project gutenberg' in t.lower()
    v=wl(t)
    if len(v)<2*n: continue
    wm=win(v); am=int(wm.argmax())
    # strip: keep between START OF and END OF markers if present
    s=re.search(r"\*\*\*\s*START OF.*?\*\*\*",t,flags=re.S|re.I); e=re.search(r"\*\*\*\s*END OF",t,flags=re.I)
    core=t[(s.end() if s else 0):(e.start() if e else len(t))]
    v2=wl(core); wm2=win(v2) if len(v2)>n else np.array([float('nan')])
    rows.append((os.path.basename(p)[:34],has,len(v),v.mean(),wm.max(),am/len(wm),(wm>=LO).mean(),v2.mean(),wm2.max(),(wm2>=LO).mean(),(wm2>=HI).mean()))
print("%-34s %3s %7s | RAW mean  maxwin  argmax-pos  frac>=4.268 | STRIPPED mean  maxwin  frac>=4.268  frac>=4.425"%("text","PG","words"))
for r in rows: print("%-34s %3s %7d |  %.3f   %.3f    %.3f       %.3f    |   %.3f      %.3f     %.3f       %.3f"%(r[0],'Y' if r[1] else '-',r[2],r[3],r[4],r[5],r[6],r[7],r[8],r[9],r[10]))
pg=[r for r in rows if r[1]]
print("\nPG files: %d ; RAW reach>=4.268: %d ; STRIPPED reach>=4.268: %d ; STRIPPED reach>=4.425: %d"%(len(pg),sum(r[4]>=LO for r in pg),sum(r[8]>=LO for r in pg),sum(r[8]>=HI for r in pg)))
print("ALL files: %d ; STRIPPED reach>=4.268: %d ; >=4.425: %d"%(len(rows),sum(r[8]>=LO for r in rows),sum(r[8]>=HI for r in rows)))
