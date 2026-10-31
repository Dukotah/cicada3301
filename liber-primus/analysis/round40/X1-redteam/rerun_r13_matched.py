"""X1 R13 DIRECTION positional-structure-matched nulls. Imports C1 machinery (c1common/lib) unchanged; writes only here (lib.py appends to C1's c1.log at import: unavoidable side effect)."""
import sys, os, json, random, time
C1='C:/Users/Jeff/cicada3301/liber-primus/analysis/round40/C1-rescore-46'
sys.path.insert(0,C1); os.chdir(C1)
from c1common import *
from lib import _load
Dm=_load("direction_mod_x1", os.path.join(AN,"direction","direction.py"))
OUT='C:/Users/Jeff/cicada3301/liber-primus/analysis/round40/X1-redteam/'
def streams_of(stream):
    stream=np.asarray(stream,dtype=np.int64); out={}
    for sname,f in Dm.STEPS.items():
        for start in range(0,64):
            for back in (False,True):
                for skipF in (True,False): out["A:%s:s%d:b%d:f%d"%(sname,start,back,skipF)]=np.array(Dm.walk(stream,f,start,back=back,skipF=skipF),dtype=np.int64)
        for start in range(0,32): out["B:%s:s%d"%(sname,start)]=np.array(Dm.cumwalk(stream,f,start),dtype=np.int64)
    for stride in (1,2,3,5,7,11,13,29,33,133,331):
        for start in range(0,16):
            for mode in ("parity","half"): out["C:%d:s%d:%s"%(stride,start,mode)]=np.array(Dm.signwalk(stream,stride,start,mode=mode),dtype=np.int64)
    for k,v in Dm.sieves(stream).items(): out["D:"+k]=np.asarray(v,dtype=np.int64)
    return out
Ua=np.array(U); L=len(Ua)
obs=streams_of(Ua)
best='A:idx:s60:b1:f1'; so=obs[best]
res={'L':L,'best_stream':best,'len':int(len(so))}
res['obs_pmax_best']=pm_many({best:so})[best]
# --- path positions of the best walk
def path(stream,start,maxlen=400,back=True,skipF=True):
    out=[];seen=set();p=start;sgn=-1 if back else 1
    while len(out)<maxlen:
        if p in seen: break
        seen.add(p); v=int(stream[p]); out.append((p,v)); d=v if v else 1; p=(p+sgn*d)%len(stream)
    return out
pp=path(Ua,60); P=np.array([a for a,_ in pp]); res['path_len_visits']=len(P)
# --- (1) stream-permutation null (preserves multiset)
rs=np.random.RandomState(7)
perm=[pm_many({'p':rs.permutation(so)})['p'] for _ in range(1000)]
res['perm_null']={'n':1000,'mean':float(np.mean(perm)),'sd':float(np.std(perm)),'max':float(np.max(perm)),'exceed_ge_obs':int(sum(x>=res['obs_pmax_best'] for x in perm))}
# --- (2) shifted-path null: same spacing structure, other positions of the real text
sh=[]
for d in range(L):
    idx=(P+d)%L; s=Ua[idx]; s=s[s!=0]
    if len(s)>=32: sh.append((d,pm_many({'p':s})['p']))
a=np.array([x for _,x in sh])
res['shift_null']={'n':len(a),'mean':float(a.mean()),'sd':float(a.std()),'q99':float(np.quantile(a,.99)),'max':float(a.max()),'exceed_ge_obs':int((a>=res['obs_pmax_best']).sum()),'p_single_stream':float((1+(a>=res['obs_pmax_best']).sum())/(len(a)+1)),'shift0_val':[v for d,v in sh if d==0][:1]}
# family-correction: 2274 correlated streams -> report p x effective independent reads is not computed; report the single-stream p only
# --- (3) block-permutation family null (preserves local order and lag structure, permutes block order)
BS=int(os.environ.get('BS','100')); D=int(os.environ.get('DRAWS','500'))
def blockperm(j):
    r=random.Random(60000+j); blocks=[list(U[i:i+BS]) for i in range(0,L,BS)]; r.shuffle(blocks)
    return streams_of(np.array([v for b in blocks for v in b]))
wait_mem()
t=time.time(); out=eval_family(obs,blockperm,D,'X1_R13_blockperm%d'%BS,part=None,raw_best=True)
res['blockperm_family']={k:v for k,v in out.items() if not k.startswith('_')}; res['blockperm_family']['BS']=BS; res['blockperm_family']['elapsed']=round(time.time()-t,1)
json.dump(res,open(OUT+'rerun_r13_matched_BS%d.json'%BS,'w'),indent=1,default=float)
print(json.dumps(res,indent=1,default=float))
