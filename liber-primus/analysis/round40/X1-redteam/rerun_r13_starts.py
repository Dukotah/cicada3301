"""X1: R13 near-miss, the matched null with the SAME rule and SAME text: every start position 0..L-1 of A:idx:b1:f1 (and the other A:* rules), not just starts 0..63; and the top translations of the observed path."""
import sys, os, json
C1='C:/Users/Jeff/cicada3301/liber-primus/analysis/round40/C1-rescore-46'
sys.path.insert(0,C1); os.chdir(C1)
from c1common import *
from lib import _load
Dm=_load("direction_mod_x1b", os.path.join(AN,"direction","direction.py"))
OUT='C:/Users/Jeff/cicada3301/liber-primus/analysis/round40/X1-redteam/'
Ua=np.array(U); L=len(Ua); res={}
obs=None
for sname in ('idx',):
    for back in (True,False):
        for skipF in (True,False):
            seen={}; pm={}
            for st in range(L):
                w=tuple(Dm.walk(Ua,Dm.STEPS[sname],st,back=back,skipF=skipF))
                if len(w)>=32 and w not in seen: seen[w]=st
            streams={('s%d'%st):np.array(w,dtype=np.int64) for w,st in seen.items()}
            pms=pm_many(streams)
            vals=np.array(list(pms.values())); ks=list(pms)
            key='%s:b%d:f%d'%(sname,back,skipF)
            res[key]={'starts':L,'distinct_scorable_streams':len(seen),'mean':float(vals.mean()),'sd':float(vals.std()),'q99':float(np.quantile(vals,.99)),'max':float(vals.max()),
              'n_ge_4.733':int((vals>=4.733).sum()),'top5':sorted(((round(float(v),3),k) for k,v in pms.items()),reverse=True)[:5],
              'frac_distinct':len(seen)/L}
            print(key,res[key],flush=True)
json.dump(res,open(OUT+'rerun_r13_starts.json','w'),indent=1,default=float)
