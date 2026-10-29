import json,sys,os
sys.dont_write_bytecode=True
import numpy as np
H=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,os.path.join(H,'..','..','..','benchmark')); sys.path.insert(0,os.path.join(H,'..','..','round20','P3'))
import null as NL, panelmax20 as PM
g={d:json.load(open(f'out_grid_{d}.json')) for d in ('base','panel_max')}
nl={d:json.load(open(f'out_null_{d}.json')) for d in ('base','panel_max')}
r32={}
for f in ('out_reg_L120.json','out_reg_L400.json','out_en_L120.json','out_en_L400.json'):
    p=os.path.join(H,'..','..','round32','I1-skipbytwo-decoder',f)
    for k,v in json.load(open(p)).items(): r32[k]=v['median_recovery']
REG=['EN_MODERN','EN_KJV','LP1_REAL','LATIN','OE','DE','CY','EN_HALFVOWEL','EN_NOVOWEL']
PAIRS=[('keyskip1',1),('skip_by_two',2),('free_q05','free')]
tab=[];ok=True;viol=[]
for L in (120,400):
  for reg in REG:
    for enc,adv in PAIRS:
      kb=f'base|{reg}|{enc}|dec={adv}|L{L}'; kv=f'panel_max|{reg}|{enc}|dec={adv}|L{L}'
      b,v=g['base'][kb],g['panel_max'][kv]
      p32=r32.get(f'{reg}|{enc}|dec={adv}|L{L}')
      d=v['median_recovery']-b['median_recovery']
      row=dict(L=L,reg=reg,enc=enc,dec=adv,base_med=round(b['median_recovery'],3),base_mean=round(b['mean_recovery'],3),
        r32_med=None if p32 is None else round(p32,3),v3_med=round(v['median_recovery'],3),v3_mean=round(v['mean_recovery'],3),v3_min=round(v['min_recovery'],3),
        v3_pmax=round(v['median_pmax'],2),frac_over_null=v['frac_over_null_pmax'],base_frac_over_null=b['frac_over_null_pmax'],delta=round(d,3),
        v3_R=bool(v['median_recovery']>=0.85 and v['frac_over_null_pmax']>=0.8),base_R=bool(b['median_recovery']>=0.85 and b['frac_over_null_pmax']>=0.8))
      tab.append(row)
      if d<-0.05: viol.append(row)
      if p32 is not None and v['median_recovery']<p32-0.05: viol.append(dict(row,vs='r32'))
json.dump(tab,open('table.json','w'),indent=0)
print('L reg enc | base R32 | v3 med/mean min | pmax fracnull | R(base->v3)')
for r in tab:
    print(r['L'],r['reg'][:11].ljust(11),r['enc'][:8].ljust(8),'|',r['base_med'],r['r32_med'],'|',r['v3_med'],r['v3_mean'],r['v3_min'],'|',r['v3_pmax'],r['frac_over_null'],'|',r['base_R'],'->',r['v3_R'])
print('VIOLATIONS',len(viol)); [print(v) for v in viol]
print('NULLS')
for d in nl:
  for k,v in nl[d].items(): print(d,k,'max_pmax',v['max_pmax'],'max_en',v['max_en'],'q95',round(v['q95_pmax'],2),v['sec'])
for L in (120,400):
  print('threshold_for N=100,1e6 L',L,NL.threshold_for(100,segment_len=L),NL.threshold_for(10**6,segment_len=L))
for pr,adv in (('exact',1),('pair',2),('drift','free')):
  print('panelmax_bar',pr,PM.panelmax_bar(pr,100),PM.panelmax_bar(pr,10**6))
