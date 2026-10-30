import sys, os, json
sys.dont_write_bytecode=True
sys.path.insert(0, os.path.abspath('../O3-nearmiss-1354603465'))
import autopsy as A
import numpy as np
d, r = A.decode("bash4.2", A.SEED, "keyskip2", -1, 729)
x = np.asarray(d["plain_idx"], dtype=np.int64)
out={"L729_pmax9":r["pmax9"],"segments":[]}
for k in (0,1):
    sg=x[k*120:(k+1)*120]; p9,r9,_=A.zs(A.PAN9,sg); p12,r12,_=A.zs(A.PAN12,sg)
    out["segments"].append({"seg":k,"p9":p9,"r9":r9,"p12":p12,"r12":r12})
d0,r0=A.decode("bash4.2",A.SEED,"keyskip2",-1,120,o=0,c0=0)
d1,r1=A.decode("bash4.2",A.SEED,"keyskip2",-1,120,o=d0["ptr_end"]+1,c0=120)
out["chained"]=[{"win":0,"p9":r0["pmax9"]},{"win":1,"p9":r1["pmax9"],"r9":r1["reg9"]}]
ref=json.load(open('../O3-nearmiss-1354603465/verifiers.json'))['B_register_consistency']
out["lane_segments_0_1"]=[(s["p9"],s["r9"]) for s in ref["candidate_segments_L729_ks2"][:2]]
out["lane_chained_0_1"]=[(s["p9"],s["r9"]) for s in ref["candidate_chained_120_windows"][:2]]
print(json.dumps(out,indent=1)); json.dump(out,open('rerun_o3_verifB.json','w'),indent=1)
