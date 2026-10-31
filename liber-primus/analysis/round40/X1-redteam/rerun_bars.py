import json, math
R='../B3-english-era-grids/'
nl=json.load(open('../../round36/B1-orbit-12reg/null12.json'))['cells']
def bar(N,L,rel):
    c=nl[f'L{L}|{rel}']; return c['mu']+c['beta']*math.log(N/-math.log(0.99))
def tail(x,L,rel):
    c=nl[f'L{L}|{rel}']; return math.exp(-(x-c['mu'])/c['beta'])   # per-draw exceedance implied by POT-exp tail
out={}; bad=[]
for g in ['B04','KDF','R17PAD','COSPAD']:
    f=json.load(open(R+f'final_{g}.json')); out[g]={}
    rows=[json.loads(l) for l in open(R+f'rows_{g}.jsonl')][1:]
    for rel,v in f['rels'].items():
        Na,Ns=v['N_actual'],v['N_screened']
        mine={'actual':bar(Na,120,rel),'decl':bar(1e6,120,rel),'screened':bar(Ns,120,rel)}
        st={'actual':v['bar120_actualN'],'decl':v['bar120_declN'],'screened':v['bar120_screenedN']}
        d={k:abs(mine[k]-st[k]) for k in mine}
        if max(d.values())>6e-4: bad.append((g,rel,d))
        pm=[r[3] for r in rows if r[0].endswith(rel) and r[1]==120]
        best=max(pm); u=nl[f'L120|{rel}']['u']
        # empirical survivor tail vs implied tail at levels
        cmp={}
        for x in (u+0.5,u+1.0,u+1.5,u+2.0,u+2.5):
            emp=sum(1 for p in pm if p>=x)/len(pm); cmp[round(x,2)]=(round(emp,5),round(tail(x,120,rel),5))
        out[g][rel]={'N_actual':Na,'N_screened':Ns,'bars_mine':{k:round(x,3) for k,x in mine.items()},'bars_stored':st,'max_abs_diff':max(d.values()),
          'best':best,'P_max_ge_best_actualN':1-math.exp(-Na*tail(best,120,rel)),'P_max_ge_best_screenedN':1-math.exp(-Ns*tail(best,120,rel)),
          'n_rows_L120':len(pm),'emp_vs_null_tail(x:(emp,null))':cmp}
json.dump(out,open('rerun_bars.json','w'),indent=1)
print('bar mismatches >6e-4:',bad)
for g in out:
    for rel,v in out[g].items(): print(g,rel,v['bars_mine'],'best',v['best'],'P_act %.4f P_scr %.3g'%(v['P_max_ge_best_actualN'],v['P_max_ge_best_screenedN']),v['emp_vs_null_tail(x:(emp,null))'])
