import os, sys, json
import numpy as np
sys.dont_write_bytecode=True
R36=os.path.abspath('..'); sys.path.insert(0, os.path.join(R36,'..','round32','I2-multiregister-readjudication'))
import power as P; AJ=P.AJ
pan=AJ.Panel(os.path.join(R36,'P1-panel-r36','build1','panel12.npz')); AJ._PANEL=pan
d=np.load(os.path.join(R36,'P1-panel-r36','build1','testhalves12.npz'))
bar=json.load(open(os.path.join(R36,'P1-panel-r36','gate_proof_r36.json')))['bars_pmax12']['120']
out={}
for reg in ('EN_NOVOWEL','EN_HALFVOWEL','CY'):
    T=d[reg].astype(np.int64); h=0; pm=[]
    for rep in range(24):
        r=P.plant_trial(T,120,rep,pan); m=float(max(r['z'])); pm.append(m); h+= m>=bar
    out[reg]={'hits':h,'n':24,'min_pmax':min(pm)}
print(out); json.dump(out,open('rerun_nine.json','w'))
