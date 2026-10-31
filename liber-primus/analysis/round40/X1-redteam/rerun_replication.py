import sys, os, json, time
B1='C:/Users/Jeff/cicada3301/liber-primus/analysis/round40/B1-bash-versions'
sys.path.insert(0,B1)
import importlib.util
sp=importlib.util.spec_from_file_location('b1sweep',B1+'/sweep.py'); m=importlib.util.module_from_spec(sp); sys.modules['b1sweep']=m; sp.loader.exec_module(m)
import numpy as np
S=m.S
chunks=[(1329,786432),(1306,262144)]
mine={}; t=time.time(); ns=0
for p,s in chunks:
    seeds=np.arange((p<<20)|s,((p<<20)|s)+S.SUB,dtype=np.uint64)
    n,rows=m.chunk_bash(seeds,'bash4.1',S.C_SCREEN,None); ns+=n
    for r in rows: mine[(r['seed'],r['rel'])]=r['pmax']
los=[((p<<20)|s,((p<<20)|s)+S.SUB) for p,s in chunks]
theirs={}
with open(os.path.join(m.R37,'sweep_rows.jsonl')) as f:
    f.readline()
    for line in f:
        r=json.loads(line); k=r[0].split(':')
        if k[1]=='bash4.2':
            sd=int(k[2])
            if any(a<=sd<b for a,b in los): theirs[(sd,k[3])]=r[3]
md=max(abs(mine[k]-theirs[k]) for k in mine if k in theirs)
res={'chunks':chunks,'survivors':ns,'rows_mine':len(mine),'rows_R37':len(theirs),'same_keys':set(mine)==set(theirs),'max_abs_pmax_diff':md,'zero_events':m.G.ZERO_EVENTS,'elapsed_s':round(time.time()-t,1)}
json.dump(res,open('rerun_replication.json','w'),indent=1); print(res)
