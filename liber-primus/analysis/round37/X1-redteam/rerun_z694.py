import sys, math, json, random
import numpy as np
sys.dont_write_bytecode=True
LP="C:/Users/Jeff/cicada3301/liber-primus"
sys.path.insert(0, LP+'/src'); sys.path.insert(0, LP+'/analysis/round19/I2'); sys.path.insert(0, LP+'/analysis/round10/L2-map')
import adjudicate as A, mapcommon as M
pan=A.Panel(LP+'/data/panels/panel-r36.npz'); REG=list(pan.registers)
W=M.parse()["words"]; assert len(W)==2928
def z_of(x):
    x=np.asarray(x,dtype=np.int64); n=len(x); mu,sd,_,_=pan.cal(n); sc=math.sqrt(n/1000.0) if n>1000 else 1.0
    return (pan.raw(x)-mu)/(sd/sc)
def reading(Wl):
    Wf=[[r for r in w if r!=0] or [w[0]] for w in Wl]
    s=np.array([w[0] for w in Wf]); return ((28-s)[::-1]+28)%29
obs=reading(W); zo=z_of(obs)
print("obs z by register",dict(zip(REG,[round(float(v),2) for v in zo])),"pmax",round(float(zo.max()),3),"argmax",REG[int(zo.argmax())])
# as an English-gated number: z of EN_MODERN
# nulls
flat=[r for w in W for r in w]; lens=[len(w) for w in W]
def dbl(x): return sum(1 for i in range(len(x)-1) if x[i]==x[i+1])
print("flat doublets (equal adjacent runes, flat stream):",dbl(flat))
rng=random.Random(910306)
def cut(x):
    out=[];k=0
    for L in lens: out.append(x[k:k+L]); k+=L
    return out
# null_A: shuffle content, boundaries fixed
nA=[];nD=[];nd=[]
def dfshuffle2(seq,rng,target):
    # independent implementation: shuffle, then repair adjacent equal pairs by swapping the second element with a random far element that creates no new pair
    x=list(seq); rng.shuffle(x); n=len(x)
    for _ in range(6):
        bad=[i for i in range(n-1) if x[i]==x[i+1]]
        if len(bad)<=target: break
        cnt=len(bad)
        for i in bad:
            if cnt<=target: break
            if x[i]!=x[i+1]: continue
            for _t in range(60):
                j=rng.randrange(2,n-2)
                if abs(j-i)<3: continue
                a,b=x[i+1],x[j]
                if i+2<n and b!=x[i] and b!=x[i+2] and a!=x[j-1] and a!=x[j+1]:
                    x[i+1],x[j]=b,a; cnt-=1; break
    return x
D=300
for j in range(D):
    x=list(flat); rng.shuffle(x); nA.append(float(z_of(reading(cut(x))).max()))
    y=dfshuffle2(flat,rng,86); nd.append(dbl(y)); nD.append(float(z_of(reading(cut(y))).max()))
nA=np.array(nA); nD=np.array(nD)
po=float(zo.max())
res={"observed_pmax":po,"obs_z_by_register":dict(zip(REG,[float(v) for v in zo])),"argmax":REG[int(zo.argmax())],
 "plain_shuffle_null_single_reading":{"draws":D,"mean":float(nA.mean()),"q99":float(np.quantile(nA,.99)),"max":float(nA.max()),"p":float((1+(nA>=po).sum())/(D+1))},
 "doublet_matched_null_single_reading":{"draws":D,"mean":float(nD.mean()),"q99":float(np.quantile(nD,.99)),"max":float(nD.max()),"p":float((1+(nD>=po).sum())/(D+1)),"doublets_mean":float(np.mean(nd)),"doublets_max":int(max(nd))},
 "flat_doublets_real":dbl(flat)}
print(json.dumps(res,indent=1)); json.dump(res,open(LP+'/analysis/round37/X1-redteam/rerun_z694.json','w'),indent=1)
