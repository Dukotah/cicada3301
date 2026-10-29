import json, analyze as A
from collections import defaultdict
# reuse analyze internals; re-run D3 to get acceptors
res = {}
for aware, nm in ((False,"D3a"),(True,"D3b")):
    cells, meta, thr = A.run_D3(aware)
    acc = cells[thr][0]
    d = defaultdict(lambda:[0,0])
    for key in ("R_t","R_nv_h","R_sp_h","G_t","G_h"):
        for c in A.SETS[key]:
            k=(key,c["stream"]); d[k][1]+=1; d[k][0]+= (not acc(c))
    res[nm]={f"{k[0]}/{k[1]}":f"{v[0]}/{v[1]} rejected" for k,v in d.items()}
    print(nm,thr,meta); print(json.dumps(res[nm],indent=0))
# frozen fold-family control stream breakdown
for nm,(cells) in (("fold_k5_min_0.90",A.design_fold_control()),):
    acc=cells["fold_k5_min_tau0.9"][0]; d=defaultdict(lambda:[0,0])
    for key in ("R_t","R_nv_h","R_sp_h","G_t","G_h"):
        for c in A.SETS[key]:
            k=(key,c["stream"]); d[k][1]+=1; d[k][0]+= (not acc(c))
    print(nm,{f"{k[0]}/{k[1]}":f"{v[0]}/{v[1]}" for k,v in d.items()})
    print("catch tune", sum(not acc(c) for c in A.SETS["H_t"]), len(A.SETS["H_t"]), "held", sum(not acc(c) for c in A.SETS["H_h"]), len(A.SETS["H_h"]))
    sc = cells["cut_h60_tau0.9"] if False else A.design_D1()["cut_h60_tau0.9"][0]
    print("single-cut(1/4) catch tune", sum(not sc(c) for c in A.SETS["H_t"]), "/",len(A.SETS["H_t"]), "held", sum(not sc(c) for c in A.SETS["H_h"]),"/",len(A.SETS["H_h"]),
          "FR G_t", sum(not sc(c) for c in A.SETS["G_t"]), "G_h", sum(not sc(c) for c in A.SETS["G_h"]))
json.dump(res, open("breakdown.json","w"), indent=1)
