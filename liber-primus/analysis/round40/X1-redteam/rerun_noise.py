import json, numpy as np, math
R='../B3-english-era-grids/'; B1='../B1-bash-versions/sweep_rows.jsonl'
nl=json.load(open('../../round36/B1-orbit-12reg/null12.json'))['cells']
pool={'keyskip1':[], 'keyskip2':[]}; per={}
for g in ['B04','KDF','R17PAD','COSPAD']:
    for l in list(open(R+f'rows_{g}.jsonl'))[1:]:
        r=json.loads(l)
        if r[1]!=120: continue
        rel=r[0].rsplit('|',1)[1]; pool[rel].append((g,r[3],r[0]))
b1={'keyskip1':[], 'keyskip2':[]}
with open(B1) as f:
    f.readline()
    for l in f:
        r=json.loads(l)
        if r[1]!=120: continue
        rel=r[0].rsplit(':',1)[1] if ':' in r[0] else r[0].rsplit('|',1)[1]
        if rel in b1: b1[rel].append(r[3])
out={}
x=6.528; rel='keyskip2'
for rel in ('keyskip1','keyskip2'):
    kd=[p for g,p,k in pool[rel] if g=='KDF']; oth=[p for g,p,k in pool[rel] if g!='KDF']
    o=np.array(oth); b=np.array(b1[rel])
    lam_o=(o>=x).mean(); lam_b=(b>=x).mean()
    out[rel]={'n_other_grids':len(o),'n_bash_B1':len(b),
      'q50_other':float(np.median(o)),'q99_other':float(np.percentile(o,99)),'q50_bash':float(np.median(b)),'q99_bash':float(np.percentile(b,99)),
      'null12_p50':nl['L120|'+rel]['p50'],'null12_p99':nl['L120|'+rel]['p99'],
      'count_ge_6.528_other':int((o>=x).sum()),'count_ge_6.528_bash':int((b>=x).sum()),
      'P_KDF_ge_one_given_pooled_other_rate':1-(1-lam_o)**591 if lam_o>0 else None,
      'max_other':float(o.max()),'max_bash':float(b.max())}
    # empirical bar: exp-tail refit on pooled other grids above their own q90 -> 99% bar for N=591
    u=np.percentile(o,90); ex=o[o>u]-u; beta=ex.mean()
    out[rel]['pooled_POT']={'u':float(u),'beta':float(beta),'bar99_N591':float(u+beta*math.log(591*0.1/-math.log(0.99))) ,'P_max_ge_6.528_N591':float(1-math.exp(-591*0.1*math.exp(-(x-u)/beta)))}
# L-dependence: read the bundle
json.dump(out,open('rerun_noise.json','w'),indent=1)
print(json.dumps(out,indent=1))
