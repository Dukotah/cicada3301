import json, math
d=json.load(open("/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/round19/C2/out_prefilter_register_power.json"))
rows=d["rows"]; regs=list(d["summary"].keys())
n=d["n_trials"]; pc=d["p_chance"]
print(f"{'register':<14}{'tri':>7}{'ioc':>7}{'maxc':>7}{'ndist':>7}{'anyLA':>7}{'union':>7}{'tri95lo':>9}{'tri95hi':>9}")
out={}
for r in regs:
    rr=[x for x in rows if x["register"]==r]
    tri=sum(x["surv_tri"] for x in rr)/len(rr)
    la=sum(1 for x in rr if x["surv_ioc"] or x["surv_maxc"] or x["surv_ndist"])/len(rr)
    un=sum(1 for x in rr if x["surv_tri"] or x["surv_ioc"] or x["surv_maxc"] or x["surv_ndist"])/len(rr)
    k=sum(x["surv_tri"] for x in rr)
    # Wilson 95%
    z=1.96; nn=len(rr); p=k/nn
    den=1+z*z/nn; c=(p+z*z/(2*nn))/den; h=z*math.sqrt(p*(1-p)/nn+z*z/(4*nn*nn))/den
    print(f"{r:<14}{tri:>7.3f}{d['summary'][r]['survival_ioc']:>7.3f}{d['summary'][r]['survival_maxc']:>7.3f}{d['summary'][r]['survival_ndist']:>7.3f}{la:>7.3f}{un:>7.3f}{max(0,c-h):>9.3f}{min(1,c+h):>9.3f}")
    out[r]={"tri":tri,"any_langagnostic":la,"union":un,"tri_wilson95":[max(0,c-h),min(1,c+h)]}
print("\nn per register:",n," offsets per scan:",d["n_offsets_per_scan"]," chance:",pc)
print("verdict:",d["verdict"],"wall_s",d["wall_s"])
json.dump(out,open("/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/round19/C2/out_prefilter_union.json","w"),indent=1)
