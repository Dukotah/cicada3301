import sys, json, time, os, subprocess
sys.dont_write_bytecode=True
LP="C:/Users/Jeff/cicada3301/liber-primus"
sys.path.insert(0, LP+'/analysis/round19/I2'); sys.path.insert(0, LP+'/analysis/round33/I1-register-aware-beam'); sys.path.insert(0, LP+'/analysis/handoff')
import adjudicate as A
out={}
for nm,p in [("R35_B1_9wide_full",LP+"/analysis/round35/B1-bash-orbit-pfv4/sweep_rows.jsonl"),("R36_B1_12wide_full",LP+"/analysis/round36/B1-orbit-12reg/readjud_rows.jsonl")]:
    t=time.time()
    try:
        r=A.validate_store(p); out[nm]={"ok":True,"rows_validated":r["rows_validated"],"n_registers_header":len(r["header"]["registers"]),"s":round(time.time()-t,1)}
    except Exception as e:
        out[nm]={"ok":False,"err":repr(e)[:300]}
    print(nm,out[nm],flush=True)
import validate_ledger as VL
for nm,p in [("R35",LP+"/analysis/round35/B1-bash-orbit-pfv4/sweep_rows.jsonl"),("R36",LP+"/analysis/round36/B1-orbit-12reg/readjud_rows.jsonl")]:
    out["check_r3_store_"+nm]=VL.check_r3_store(p); print("check_r3_store",nm,out["check_r3_store_"+nm])
# derive_clusters
import beam_v3 as V
import numpy as np
for nm,p in [("panel-R36",LP+"/data/panels/panel-r36.npz"),("round32_panel",None)]:
    try:
        if p is None:
            import glob
            c=glob.glob(LP+"/analysis/round32/I2-multiregister-readjudication/*.npz")+glob.glob(LP+"/analysis/round32/**/panel*.npz",recursive=True)
            p=c[0] if c else None
        regs=list(np.load(p,allow_pickle=True)["registers"]) if p else None
        out["derive_"+nm]={"path":p,"n_regs":len(regs),"clusters":V.derive_clusters(regs)}
    except Exception as e: out["derive_"+nm]={"err":repr(e)[:300],"path":p}
    print(nm,json.dumps(out["derive_"+nm],default=str)[:600])
json.dump(out,open(LP+"/analysis/round37/X1-redteam/rerun_t1.json","w"),indent=1,default=str)
