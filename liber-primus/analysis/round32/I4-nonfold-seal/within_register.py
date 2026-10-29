"""within_register.py -- EXPLORATORY (post-hoc, not part of the pre-registered verdict).
The pre-registered learned gates separate REGISTERS (EN_MODERN vs EN_NOVOWEL), not hallucination vs
genuine. The honest hard test is within the EN_NOVOWEL stream: 109 correct-key hallucinations vs 13
correct-key genuine decodes (recovery>=0.95). Per-statistic AUC + a CV'd within-register LR."""
import json, numpy as np, analyze as A
H = A.SETS["H_t"] + A.SETS["H_h"]; G = A.SETS["R_t"] + A.SETS["R_nv_h"]
def auc(pos, neg):  # P(genuine score > halluc score)
    pos=np.array(pos); neg=np.array(neg)
    return float(np.mean([(p>n)+0.5*(p==n) for p in pos for n in neg]))
stats = {}
for k in (2,3,4,5,6,7,8):
    stats[f"fold_k{k}_min"]=lambda c,k=k:A.fold_stat(c,k,"min"); stats[f"fold_k{k}_mean"]=lambda c,k=k:A.fold_stat(c,k,"mean")
for h in A.HEADS: stats[f"cut_h{h}"]=lambda c,h=h:A.cutv(c,h) or 0
for nm in ("ms8","pair","bw100"): stats[f"cons_{nm}"]=lambda c,nm=nm:c["cons"][nm]
for h in ("64","120","180"): stats[f"headp{h}"]=lambda c,h=h:c["headp"][h]
for f in ("pmax","ioc","mds","h2","zl","pmax_ne","pcon","en"): stats[f]=lambda c,f=f:c["feat"][f]
stats["n_skips"]=lambda c:c["n_skips"]; stats["n_unexpl"]=lambda c:c["n_unexpl"]; stats["beam_score"]=lambda c:c["beam_score"]
rows = {}
for n,f in stats.items():
    a=auc([f(c) for c in G],[f(c) for c in H]); rows[n]=round(a,3)
top = sorted(rows.items(), key=lambda x:-abs(x[1]-0.5))[:12]
print("within-EN_NOVOWEL AUC (genuine>halluc), top |AUC-.5|:", top)
# CV'd within-register LR (leave-one-out on the 122), register-blind features
X=np.array([A.fvec(c,False) for c in H+G]); y=np.array([0.]*len(H)+[1.]*len(G))
mu,sd=X.mean(0),X.std(0)+1e-9; Z=(X-mu)/sd
out={}
for lam in (1.0,10.0,100.0):
    loo=np.zeros(len(y))
    for i in range(len(y)):
        m=np.arange(len(y))!=i; w=A.fit_lr(Z[m],y[m],lam); loo[i]=A.predict(w,Z[i:i+1])[0]
    # best catch s.t. FR<=0.10 on LOO scores
    best=(0,None)
    for t in sorted(set(loo)):
        fr=float(np.mean(loo[y==1]<t)); cr=float(np.mean(loo[y==0]<t))
        if fr<=0.10 and cr>best[0]: best=(cr,(float(t),fr))
    out[f"lam{lam}"]={"loo_auc":auc(loo[y==1],loo[y==0]),"best_loo_catch_at_FR<=0.10":best[0],"op":best[1]}
print(json.dumps(out,indent=1))
json.dump({"n_halluc":len(H),"n_genuine_novowel":len(G),"auc_by_stat":rows,"loo_lr":out,
           "caveat":"post-hoc exploratory; 13 genuine NOVOWEL decodes is an under-powered positive class; LOO pools tuning+held-out"},
          open("within_register.json","w"),indent=1)
