import json,sys,os
sys.dont_write_bytecode=True
import numpy as np
tab=json.load(open('table.json')); sp=json.load(open('speed_raw.json'))
nl={d:json.load(open(f'out_null_{d}.json')) for d in ('base','panel_max')}
strip=lambda v:{k:x for k,x in v.items() if k not in('rows','q95_pmax')}
env={"lane":"round33/I1","date":"2026-10-29","best_design":"panel_max (tau=0 hard max over 9 registers; lam_u=4 for free)",
 "baseline":"driftbeam via round32 beam_v2, re-run on the SAME plants (I2 testhalves), same panel",
 "recovered_rule":"median recovery>=0.85 AND >=80% seeds pmax > own shuffle-null max (same decoder, same relation, same L)",
 "cells":tab,
 "nulls":{d:{k:strip(v) for k,v in nl[d].items()} for d in nl},
 "bars":{"threshold_for_N100":{"120":-5.5,"400":-5.5},"threshold_for_N1e6":{"120":-5.5,"400":-5.5},
   "hitfn20_panelmax_bar_N100":{"exact(adv1)":4.995,"pair(adv2)":4.901,"drift(free)":9.870},
   "hitfn20_panelmax_bar_N1e6":{"exact(adv1)":7.634,"pair(adv2)":7.384,"drift(free)":13.842},
   "note":"hitfn20 cells exist at L=120 only and were fitted on driftbeam wrong-key decodes; v3 own null binds"},
 "checkpoint":json.load(open('out_ckpt.json')) and {k:{x:y for x,y in v.items() if x!='rows'} for k,v in json.load(open('out_ckpt.json')).items()},
 "tuning":{k:{x:y for x,y in v.items() if x!='rows'} for k,v in json.load(open('out_tune.json')).items()},
 "designs_2_3_supplementary_L120":{k:{x:y for x,y in v.items() if x!='rows'} for k,v in json.load(open('out_supp_designs23.json')).items()}}
json.dump(env,open('power_envelope.json','w'),indent=1)
S={"lane":"round33/I1","machine":"Win11 laptop, 1 process, nproc=1, beam_w=400, EN_MODERN plants s=100.., mean of 4","unit":"decodes_per_s",
   "cells":{}, "ratio_vs_driftbeam":{}}
for k,v in sp.items():
    S["cells"][k]=v
for k,v in sp.items():
    d,L,adv=k.split('|')
    if d!='base': S["ratio_vs_driftbeam"][k]=round(v['sec_per_decode_mean']/sp[f'base|{L}|{adv}']['sec_per_decode_mean'],2)
S["note"]="Q5 3x-cost clause: panel_max ratios all < 3 (see ratio_vs_driftbeam); register_cond is 8.6-11x; agnostic 1.4-3.1x."
json.dump(S,open('speed.json','w'),indent=1)
for k,v in S['ratio_vs_driftbeam'].items(): print(k,v,round(sp[k]['decodes_per_s'],1))
