"""X1: does a shuffle null have the same TRAJECTORY-level spread of walk-stream pmax as real LP2? (A:idx:b1:f1, all 12,956 starts, collapsed to distinct trajectories)"""
import sys, os, json, random
C1='C:/Users/Jeff/cicada3301/liber-primus/analysis/round40/C1-rescore-46'
sys.path.insert(0,C1); os.chdir(C1)
from c1common import *
OUT='C:/Users/Jeff/cicada3301/liber-primus/analysis/round40/X1-redteam/'
L0=len(U)
def stats(txt):
    T=np.array(txt); L=len(T); paths={}
    for st in range(L):
        out=[];seen=set();p=st
        while len(out)<400:
            if p in seen: break
            seen.add(p); out.append(p); d=int(T[p]) or 1; p=(p-d)%L
        paths[st]=out
    cl={}
    for st,pp in paths.items(): cl.setdefault(pp[150] if len(pp)>150 else ('s',pp[-1]),[]).append(st)
    reps={}
    for t,sts in cl.items():
        b=max(sts,key=lambda s:len(paths[s])); v=T[paths[b]]; v=v[v!=0].astype(np.int64)
        if len(v)>=32: reps[str(t)]=v
    pm=np.array(list(pm_many(reps).values()))
    return {'n_traj':len(cl),'mean':float(pm.mean()),'sd':float(pm.std()),'max':float(pm.max()),'q99':float(np.quantile(pm,.99)),'n_ge_4':int((pm>=4).sum())}
res={}
res['real']=stats(U); print('real',res['real'],flush=True)
for j in range(3):
    res['dfshuffle_%d'%j]=stats(dfshuffle(U,random.Random(777+j))); print('df',j,res['dfshuffle_%d'%j],flush=True)
for BS in (100,1000):
    for j in range(2):
        r=random.Random(888+j); bl=[list(U[i:i+BS]) for i in range(0,L0,BS)]; r.shuffle(bl)
        res['block%d_%d'%(BS,j)]=stats([v for b in bl for v in b]); print('bp',BS,j,res['block%d_%d'%(BS,j)],flush=True)
json.dump(res,open(OUT+'rerun_r13_calib.json','w'),indent=1)
