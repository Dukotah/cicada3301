import sys, os, json, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "I1-register-aware-beam"))
import beam_v3 as V, rep
B = rep.B
out = os.path.join(HERE, "representability_v3.json"); res = json.load(open(out)) if os.path.exists(out) else {}
for kind in ["reset_per_line","reset_per_page","skip_by_3","skip_by_4","skip_by_5","keyskip1","skip_by_two"]:
  for reg in ["EN_MODERN","EN_NOVOWEL"]:
    for mode in ["L120","page"]:
      if kind=="reset_per_page" and mode=="L120": continue
      if f"{kind}|{reg}|{mode}" in res: continue
      t0=time.time(); cell={d:[] for d in rep.DECS}
      for s in range(20):
        P,C,K,_=rep.plant(kind,reg,mode,s)
        for d in rep.DECS:
            bd=V.beam_decode_v3(C,K,d); cell[d].append(round(float(B.recovery(bd["plain_idx"],P)),4))
      key=f"{kind}|{reg}|{mode}"
      res[key]={"design":"panel_max","median_recovery":{str(k):float(np.median(v)) for k,v in cell.items()},
                "frac_ge_085":{str(k):float(np.mean([x>=.85 for x in v])) for k,v in cell.items()},"sec":round(time.time()-t0,1)}
      print(key,res[key]["median_recovery"],res[key]["sec"],flush=True); json.dump(res,open(out,"w"),indent=1)
