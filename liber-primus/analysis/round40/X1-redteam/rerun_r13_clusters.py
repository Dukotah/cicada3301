"""X1: collapse the all-starts ensemble of A:idx:b1:f1 into distinct TRAJECTORIES (walks merge in the functional graph), then rank the observed trajectory among them."""
import sys, os, json
C1='C:/Users/Jeff/cicada3301/liber-primus/analysis/round40/C1-rescore-46'
sys.path.insert(0,C1); os.chdir(C1)
from c1common import *
OUT='C:/Users/Jeff/cicada3301/liber-primus/analysis/round40/X1-redteam/'
Ua=np.array(U); L=len(Ua)
def walkpos(start, maxlen=400):
    out=[]; seen=set(); p=start
    while len(out)<maxlen:
        if p in seen: break
        seen.add(p); v=int(Ua[p]); out.append(p); d=v if v else 1; p=(p-d)%L
    return out
paths={st:walkpos(st) for st in range(L)}
# trajectory id = the position visited at index 150 (merged walks share it); shorter walks keep their own last position
tid={}
for st,pp in paths.items(): tid[st]=pp[150] if len(pp)>150 else ('short',pp[-1])
clusters={}
for st,t in tid.items(): clusters.setdefault(t,[]).append(st)
def stream_of(st):
    pp=paths[st]; v=Ua[pp]; return v[v!=0].astype(np.int64)
reps={}; 
for t,sts in clusters.items():
    best=max(sts,key=lambda s:len(stream_of(s)))   # longest stream as representative
    s=stream_of(best)
    if len(s)>=32: reps[t]=(best,s)
pms=pm_many({str(t):v[1] for t,v in reps.items()})
vals=np.array(list(pms.values()))
obs_t=tid[60]; obs_pm=pms[str(obs_t)] if str(obs_t) in pms else None
# also: max over members of the observed cluster (the 4.733 stream is a member)
res={'starts':L,'trajectories_total':len(clusters),'trajectories_scorable':len(reps),'cluster_of_s60_size':len(clusters[obs_t]),
 'cluster_rep_pmax_of_s60_cluster':obs_pm,'n_traj_ge_rep_pm':int((vals>=obs_pm).sum()) if obs_pm is not None else None,
 'traj_pmax_mean':float(vals.mean()),'traj_pmax_sd':float(vals.std()),'traj_pmax_q99':float(np.quantile(vals,.99)),'traj_pmax_max':float(vals.max()),
 'n_traj_ge_4.0':int((vals>=4.0).sum()),'n_traj_ge_4.5':int((vals>=4.5).sum()),
 'sizes_of_top_clusters':sorted(((len(c),t if not isinstance(t,tuple) else -1) for t,c in clusters.items()),reverse=True)[:5],
 'how_many_starts_0_63_in_cluster':sum(1 for s in clusters[obs_t] if s<64),
 'pm_of_s60_stream_full':None}
res['top5_traj']=sorted(((round(float(v),3),k,len(clusters[next(iter([t for t in clusters if str(t)==k]))])) for k,v in pms.items()),reverse=True)[:5]
# in-cluster spread: pmax of every member stream of the s60 cluster
mem=pm_many({str(s):stream_of(s) for s in clusters[obs_t] if len(stream_of(s))>=32})
mv=np.array(list(mem.values())); res['s60_cluster_members']={'n':len(mv),'min':float(mv.min()),'median':float(np.median(mv)),'max':float(mv.max())}
json.dump(res,open(OUT+'rerun_r13_clusters.json','w'),indent=1,default=float); print(json.dumps(res,indent=1,default=float))
