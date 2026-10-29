import sys,json,os
sys.dont_write_bytecode=True
D='C:/Users/Jeff/cicada3301/liber-primus/analysis/round33/I2-construction-axis'
sys.path.insert(0,D); os.chdir(D)
import rep
stored=json.load(open(D+'/representability.json'))
out={}
import numpy as np
for key in ['skip_by_4|EN_MODERN|L120','skip_by_3|EN_NOVOWEL|L120']:
    kind,reg,mode=key.split('|'); cell={d:[] for d in rep.DECS}
    for s in range(5):
        P,C,K,segs=rep.plant(kind,reg,mode,s)
        for d in rep.DECS:
            bd=rep.B.beam_decode_v2(C,K,d); cell[d].append(round(float(rep.B.recovery(bd['plain_idx'],P)),4))
    st=stored[key]['recoveries']
    out[key]={'rerun_5':{str(k):v for k,v in cell.items()},'stored_first5':{k:st[k][:5] for k in st},
      'identical':all(cell[d]==st[str(d)][:5] for d in rep.DECS),
      'stored_median20':stored[key]['median_recovery'],'rerun_median5':{str(k):float(np.median(v)) for k,v in cell.items()}}
    print(key,out[key],flush=True)
json.dump(out,open('C:/Users/Jeff/cicada3301/liber-primus/analysis/round34/X1-redteam/rerun_i2_rep.json','w'),indent=1)
