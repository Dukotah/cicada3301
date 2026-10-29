import sys,json,os
sys.dont_write_bytecode=True
sys.path.insert(0,'.')
import run_envelope as R
out={}
for d in ('register_cond','agnostic'):
    for reg in ('EN_NOVOWEL','EN_MODERN'):
        for enc,adv in R.PAIRS:
            c=R.run_cell(d,reg,enc,adv,120,range(20))
            k=R.ckey(c); out[k]=c
            print(k,c['median_recovery'],c['mean_recovery'],c['sec_decode_per'],flush=True)
            json.dump(out,open('out_supp_designs23.json','w'))
