# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
"""Fork D probe: 'identical key restart per unit' kill-check (informs R44-R1; extends R18-L4 Arm A beyond index 0).
If the keystream restarted identically at each page / line / sentence / word, runes at the same in-unit index would share
one key symbol (up to filter drift), so the column IoC at small indices would be English-like (~1.7x) instead of 1.0x."""
import sys, math, collections
sys.dont_write_bytecode=True
sys.path.insert(0,_PROBES)
from lpdata import *
P=unsolved_pages()
units={'page':[], 'line':[], 'sentence':[], 'word':[]}
for p in P:
    units['page'].append([r['i'] for r in p])
    cur={'line':[], 'sentence':[], 'word':[]}
    for k,r in enumerate(p):
        pre=r['pre']
        if k>0:
            if '/' in pre: units['line'].append(cur['line']); cur['line']=[]
            if '.' in pre: units['sentence'].append(cur['sentence']); cur['sentence']=[]
            if any(ch in pre for ch in '-.&$§'): units['word'].append(cur['word']); cur['word']=[]
        for u in cur: cur[u].append(r['i'])
    for u in cur: units[u].append(cur[u])
def col_ioc(us, idx):
    col=[u[idx] for u in us if len(u)>idx]; n=len(col)
    if n<30: return None
    c=collections.Counter(col); ioc=sum(v*(v-1) for v in c.values())/(n*(n-1))
    # z under uniform: var of IoC*29 approx 2*28/(n*(n-1)) *... use chi2
    chi=sum((c.get(i,0)-n/29)**2/(n/29) for i in range(29))
    return n, 29*ioc, (chi-28)/math.sqrt(56)
for name in ('page','line','sentence','word'):
    us=units[name]; out=[]
    for idx in range(0,12):
        r=col_ioc(us,idx)
        if r: out.append(f"{idx}:{r[1]:.2f}(z{r[2]:+.1f},n{r[0]})")
    print(name, len(us), ' '.join(out))
# reverse-indexed (from unit end)
for name in ('page','line','word'):
    us=[u[::-1] for u in units[name]]; out=[]
    for idx in range(0,6):
        r=col_ioc(us,idx)
        if r: out.append(f"-{idx+1}:{r[1]:.2f}(z{r[2]:+.1f})")
    print(name+' (from end)', ' '.join(out))
