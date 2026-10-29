import json, numpy as np, re
I1='round33/I1-register-aware-beam/'
pe=json.load(open(I1+'power_envelope.json')); r32=json.load(open('round32/I1-skipbytwo-decoder/power_envelope.json'))
gb=json.load(open(I1+'out_grid_base.json')); gp=json.load(open(I1+'out_grid_panel_max.json'))
nb=json.load(open(I1+'out_null_base.json')); npm=json.load(open(I1+'out_null_panel_max.json'))
res={'cells':len(pe['cells'])}; bad=[]; viol=[]; R3=R_b=0
for c in pe['cells']:
    adv=c['dec']; kb=f"base|{c['reg']}|{c['enc']}|dec={adv}|L{c['L']}"; kp=kb.replace('base','panel_max',1)
    mb=float(np.median([r['recovery'] for r in gb[kb]['rows']])); mp=float(np.median([r['recovery'] for r in gp[kp]['rows']]))
    if abs(mb-c['base_med'])>1e-3 or abs(mp-c['v3_med'])>1e-3: bad.append((kb,mb,c['base_med'],mp,c['v3_med']))
    # null-bar fractions recomputed
    nbm=nb[f"base|dec={adv}|L{c['L']}"]['max_pmax']; npm_=npm[f"panel_max|dec={adv}|L{c['L']}"]['max_pmax']
    fo=np.mean([r['pmax']>npm_ for r in gp[kp]['rows']]); fb=np.mean([r['pmax']>nbm for r in gb[kb]['rows']])
    if abs(fo-c['frac_over_null'])>1e-6 or abs(fb-c['base_frac_over_null'])>1e-6: bad.append(('fracnull',kb,fo,c['frac_over_null'],fb,c['base_frac_over_null']))
    R3+= (mp>=.85 and fo>=.8); R_b+=(mb>=.85 and fb>=.8)
    pub=r32['cells'].get(f"{c['reg']}|{c['enc']}|dec={adv}|L{c['L']}")
    pm=pub['median_recovery'] if pub and 'median_recovery' in pub else (pub.get('median') if pub else None)
    if c['r32_med'] is not None and pm is not None and abs(pm-c['r32_med'])>1e-3: bad.append(('r32pub',kb,pm,c['r32_med']))
    if mp< mb-0.05 or (c['r32_med'] is not None and mp<c['r32_med']-0.05): viol.append(kb)
res.update(mismatches=bad,v3_RECOVERED=int(R3),base_RECOVERED=int(R_b),V2_violations_recomputed=viol)
nrows=[r for c in pe['cells'] for r in [c]]
res['frac_over_null_min_v3']=min(c['frac_over_null'] for c in pe['cells'])
res['r32_cell_sample']=list(r32['cells'].items())[0][1].keys().__repr__()
print(json.dumps(res,indent=1,default=str))
json.dump(res,open('round33/X1-redteam/i1_envelope_audit.json','w'),indent=1,default=str)
