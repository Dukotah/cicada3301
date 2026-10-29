"""analyze_l120.py -- EXPLORATORY length-dependence probe (NOT part of the verdict). Applies the L=240-frozen
D5c (m_NV=14.0128) to fresh L=120 data and shows how the margin distributions move."""
import json, os, numpy as np, analyze as A
HERE=A.HERE; BAR=A.D["tune_nv"]["bar"]; M=json.load(open(os.path.join(HERE,"catch_surface_d5c.json")))["m_NV"]
def lv(n): return json.load(open(os.path.join(HERE,f"feat_{n}.json")))
W={n:lv(n) for n in ("l120_nv","l120_en","l120_sp")}
def pk(p,l): return [c for c in W[p]["cases"] if c["label"]==l]
H=pk("l120_nv","halluc"); Rn=pk("l120_nv","genuine"); G=pk("l120_en","genuine"); S=pk("l120_sp","genuine")+[c for c in W["l120_sp"]["cases"] if False]
marg=lambda c:c["feat"]["pmax"]-BAR
isnv=lambda c:c["feat"]["preg_name"]=="EN_NOVOWEL"
acc=lambda c:marg(c)>=(M if isnv(c) else 0.0)
def rate(cs): r=sum(1 for c in cs if not acc(c)); return [r,len(cs),round(r/len(cs),3) if cs else None]
def dist(cs): x=np.array([marg(c) for c in cs]); return {"n":len(x),"min":round(float(x.min()),2),"p10":round(float(np.quantile(x,.1)),2),"median":round(float(np.median(x)),2),"p90":round(float(np.quantile(x,.9)),2),"max":round(float(x.max()),2)} if len(x) else {"n":0}
def auc(p,n): return round(float(np.mean([(a>b)+.5*(a==b) for a in p for b in n])),3) if p and n else None
out={"L":120,"m_NV_from_L240":M,"sizes":{"halluc":len(H),"novowel_genuine":len(Rn),"EN_genuine":len(G),"spread_genuine":len(S)},
 "labels":{n:{f"{c['stream']}/{c['label']}":1 for c in W[n]["cases"]} and {k:sum(1 for c in W[n]["cases"] if f"{c['stream']}/{c['label']}"==k) for k in {f"{c['stream']}/{c['label']}" for c in W[n]["cases"]}} for n in W},
 "draws":{n:W[n]["n_draws"] for n in W},
 "D5c_at_L240_m":{"catch":rate(H),"fr_EN":rate(G),"fr_NV_genuine":rate(Rn),"fr_spread":rate(S)},
 "margin_dists":{"halluc":dist(H),"novowel_genuine":dist(Rn),"EN_genuine":dist(G),"spread_genuine":dist(S)},
 "within_NV_AUC_margin":auc([marg(c) for c in Rn],[marg(c) for c in H])}
# best in-sample (optimistic) separation at L=120: max catch s.t. NV-genuine FR<=0.10 using a fresh m
hm=[marg(c) for c in H if isnv(c)]; gm=[marg(c) for c in Rn if isnv(c)]
best=None
for m in sorted(set(hm+gm)):
    fr=np.mean([x<m for x in gm]) if gm else 0
    if fr<=0.10:
        cr=np.mean([x<m for x in hm]); best=(round(float(cr),3),round(float(m),2),round(float(fr),3))
out["insample_best_catch_at_NV_FR<=0.10 (m,fr)"]=best
json.dump(out,open("l120_probe.json","w"),indent=1)
print(json.dumps(out,indent=1))
