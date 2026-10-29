import json, math
H='C:/Users/Jeff/cicada3301/liber-primus/analysis/round34/I3-d5c-calibration/'
def wil(k,n,z=1.959964):
    p=k/n; d=1+z*z/n; c=p+z*z/(2*n); r=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n)); return round((c-r)/d,4),round((c+r)/d,4)
def cp_upper(k,n,a=0.05):   # exact Clopper-Pearson upper via bisection on binomial cdf
    from math import comb
    def cdf(p): return sum(comb(n,i)*p**i*(1-p)**(n-i) for i in range(k+1))
    lo,hi=0.0,1.0
    for _ in range(80):
        mid=(lo+hi)/2
        if cdf(mid)>a/2: lo=mid
        else: hi=mid
    return round(hi,4)
m=json.load(open(H+'m_nv_curve.json'))
thr_tune=m['recipes']['R1_per_L_fit']['400']['m_NV']
print('threshold in curve:',thr_tune)
keys=['CICADA-I4b','CICADA-I4c','CICADA-R34I3']
out={'threshold':thr_tune,'per_key':{}}
tot=[0,0]; origtot=[0,0]
for k in keys:
    o=json.load(open(H+f'feat_{k}_400.json')); a=json.load(open(H+f'feat_add_{k}_400.json'))
    def nvg(d): return [(c['pmax']-d['bar']) for c in d['cases'] if c['pop']=='nv' and c['label']=='genuine' and c['preg_name']=='EN_NOVOWEL']
    g0=nvg(o); g1=[(c['pmax']-a['bar']) for c in a['cases'] if c['label']=='genuine' and c['preg_name']=='EN_NOVOWEL']
    r0=sum(x<thr_tune for x in g0); r1=sum(x<thr_tune for x in g1)
    out['per_key'][k]={'orig_n':len(g0),'orig_rej':r0,'add_n':len(g1),'add_rej':r1,'overlap_reps':len(set(c['rep'] for c in o['cases'])&set(c['rep'] for c in a['cases']))}
    tot[0]+=r0+r1; tot[1]+=len(g0)+len(g1); origtot[0]+=r0; origtot[1]+=len(g0)
out['pooled_orig']={'k':origtot[0],'n':origtot[1],'wilson':wil(*origtot)}
out['pooled_total']={'k':tot[0],'n':tot[1],'wilson':wil(*tot),'clopper_pearson_upper':cp_upper(*tot)}
# only the NEW draws (independent of the n=44 look)
nk=sum(v['add_rej'] for v in out['per_key'].values()); nn=sum(v['add_n'] for v in out['per_key'].values())
out['added_only']={'k':nk,'n':nn,'wilson':wil(nk,nn)}
# was the threshold re-tuned? compare against thr in feat-only tuning fit
print(json.dumps(out,indent=1))
json.dump(out,open('C:/Users/Jeff/cicada3301/liber-primus/analysis/round34/X1-redteam/rerun_i3_wilson.json','w'),indent=1)
