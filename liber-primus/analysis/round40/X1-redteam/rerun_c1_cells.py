"""X1: re-score two C1 cells myself (no C1 parts/rows written): R33 semantic seed zoo (all 2,137 keystreams, sign -1, L=120 window 0) and R47 F-01 LP2-as-pad (cell S2xF7)."""
import sys, os, json, random, time
C1='C:/Users/Jeff/cicada3301/liber-primus/analysis/round40/C1-rescore-46'
sys.path.insert(0,C1); os.chdir(C1)
from c1common import *
from lib import _load, _dec_sign
OUT='C:/Users/Jeff/cicada3301/liber-primus/analysis/round40/X1-redteam/'
res={}
def score(Cw,Kw,sg):
    out={}
    for rel in RELS:
        d=_dec_sign(Cw,Kw,rel,sg); a=AD.adjudicate(d["plain_idx"],pan=PAN); r=AD.to_row(a,"x",with_degenerate=True)
        out[rel]=(float(a["pmax"]),bool(r[13]),REGS[a["preg"]])
    return out
# ---- R33
sw=_load("r26c_sweep_x1",os.path.join(R(26),"C","sweep.py")); seeds=json.load(open(os.path.join(R(26),"C","seeds.json")))["seeds"]
cfgs=[]
for s in seeds:
    for gname,(gfn,acc) in sw.ZOO.items():
        if s["is_str"] and not acc: continue
        try: K=gfn(s["value"])
        except Exception: continue
        if len(K)<sw.NEED: continue
        cfgs.append(("%s|%s|%s"%(s["kind"],str(s["label"])[:40],gname),np.array(K,dtype=np.int64)))
t=time.time(); best={r:(-1,None) for r in RELS}; n=0
for cn,K in cfgs:
    sc=score(U[:120],list(K[:1024]),-1); n+=1
    for rel in RELS:
        if not sc[rel][1] and sc[rel][0]>best[rel][0]: best[rel]=(sc[rel][0],cn)
res['R33']={'keystreams':len(cfgs),'best':{r:(round(v[0],3),v[1]) for r,v in best.items()},'lane_best':{'keyskip1':4.812,'keyskip2':4.901},'bar_actualN_lane':{'keyskip1':6.87,'keyskip2':6.80},'bar_declared':{r:round(bar12(1e6,120,r),3) for r in RELS},'elapsed':round(time.time()-t,1)}
print(res['R33'],flush=True)
# ---- R47
f01=os.path.join(R(16),"F-01"); sys.path.insert(0,f01); f=_load("f01_sweep_x1",os.path.join(f01,"sweep.py"))
LP2=list(f.load_lp2()); variants={"lp2_fwd":LP2,"lp2_rev":LP2[::-1],"lp2_atbash":[28-x for x in LP2],"lp2_neg":[(-x)%29 for x in LP2]}
targets={"T1":list(f.load_cicada_2012_2013())[:500],"T2":list(f.load_lp1_runes())[:500],"T3":list(f.load_pgp_messages())[:500],"T6":LP2[:200]}
best={r:(-1,None) for r in RELS}; nrow=0; ndeg=0
for tn,T in targets.items():
    starts=[s for s in range(0,len(T)-119,120)] if len(T)>=240 else [0,80]
    starts=[s for s in starts if s+120<=len(T)]
    for vn,K in variants.items():
        for sg in (-1,1):
            for s in starts:
                Kw=K[s:s+1024] if len(K)>=s+1024 else list(K[s:])+[0]*(s+1024-len(K))
                sc=score(T[s:s+120],Kw,sg); nrow+=1
                for rel in RELS:
                    if sc[rel][1]: ndeg+=1; continue
                    if sc[rel][0]>best[rel][0]: best[rel]=(sc[rel][0],"%s|%s|s%+d|w%d"%(tn,vn,sg,s))
res['R47']={'rows_per_rel':nrow,'degenerate_row_decodes_excluded':ndeg,'best':{r:(round(v[0],3),v[1]) for r,v in best.items()},'lane_best':{'keyskip1':4.184,'keyskip2':4.464},'bar_declared':{r:round(bar12(1e6,120,r),3) for r in RELS}}
print(res['R47'])
json.dump(res,open(OUT+'rerun_c1_cells.json','w'),indent=1)
