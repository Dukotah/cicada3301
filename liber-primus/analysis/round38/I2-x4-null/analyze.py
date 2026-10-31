import sys; from common import *
MDS_MAX=6; IOC_MIN=4.24
def degen(mds,ioc): return mds<=MDS_MAX or ioc>=IOC_MIN
def gumbel_bar(x,alpha=0.01):
    x=np.asarray(x); b=x.std(ddof=1)*math.sqrt(6)/math.pi; m=x.mean()-0.5772156649*b
    return m-b*math.log(-math.log(1-alpha)), m, b
nullj={}; rej={}; audit=[]; summ={}
for L in (120,240):
    p=F("null_rows_L%d.jsonl"%L); recs=[json.loads(l) for l in open(p)]
    fam={r:[] for r in RELS}; pool={r:[] for r in RELS}; nn=[]
    for rec in recs:
        for r in RELS:
            v=[x[3] for x in rec["rows"] if x[2]==r and not degen(x[4],x[5])]
            if rec["j"]<20 or True: pass
            fam[r].append(max(v)); pool[r]+=v
        nn.append(len([x for x in rec["rows"] if x[2]==RELS[0] and not degen(x[4],x[5])]))
    # degeneracy check on first 20 draws
    constchk=[x for rec in recs[:20] for x in rec["rows"] if x[0].startswith(("X4_v_prime_index_none_sign-1","X4_v_prime_index_atbash_pre_sign+1"))]
    const_all_degen=all(degen(x[4],x[5]) for x in constchk)
    real=[json.loads(l) for l in open(F("..","..","round37","C3-rescore-reopened","parts","U6b_R22C_keyed_L%d.jsonl"%L))][1:]
    real=[r for r in real if isinstance(r,list) and "X4_" in r[0]]
    Dn=len(recs); S={"draws":Dn,"const_configs_verified_degenerate_first20":const_all_degen,"null_rows_per_rel_nondegenerate":int(np.median(nn)),"real_rows_per_rel":len(real)//2}
    cell={}
    for r in RELS:
        fm=np.array(fam[r]); gb,m,b=gumbel_bar(fm)
        nr=int(np.median(nn))
        cell[r]={"family_max_mean":round(float(fm.mean()),3),"family_max_sd":round(float(fm.std(ddof=1)),3),"bar_empirical_q99":round(float(np.quantile(fm,0.99)),3),"bar_empirical_q95":round(float(np.quantile(fm,0.95)),3),"bar_gumbel_q99":round(gb,3),
                 "null_max":round(float(fm.max()),3),"row_pool_q99":round(float(np.quantile(pool[r],0.99)),3),"row_pool_max":round(float(max(pool[r])),3),
                 "transferred_bar_actualN_72rows":round(bar12(72,L,r),3),"transferred_bar_actualN_60nd":round(bar12(60,L,r),3),"transferred_bar_C3_N84":round(bar12(84,L,r),3),"transferred_bar_declared_1e6":round(bar12(1e6,L,r),3)}
    S["by_rel"]=cell; nullj[L]=S
    rows=[]
    for r in real:
        rel=r[0].split(":")[-1]; cfg=r[0].split(":")[1]; w=int(r[0].split(":")[2][1:]); pm=r[3]; mds=r[9]; ioc=r[8]; dg=degen(mds,ioc)
        fm=np.array(fam[rel]); p=(1+int((fm>=pm).sum()))/(len(fm)+1)
        bar=cell[rel]["bar_empirical_q99"]
        rows.append({"cfg":cfg,"window":w,"rel":rel,"pmax":pm,"preg":REGS[r[4]],"mds":mds,"ioc_n":ioc,"degenerate":dg,"familywise_p":round(p,5),"clears_bespoke_q99":bool(pm>=bar),"clears_bespoke_gumbel":bool(pm>=cell[rel]["bar_gumbel_q99"]),"clears_transferred_C3_N84":bool(pm>=cell[rel]["transferred_bar_C3_N84"])})
    nd=[x for x in rows if not x["degenerate"]]
    best={rel:max((x for x in nd if x["rel"]==rel),key=lambda x:x["pmax"]) for rel in RELS}
    rej[L]={"n_rows":len(rows),"n_nondegenerate":len(nd),"best_nondegenerate":best,"n_clear_bespoke":sum(x["clears_bespoke_q99"] for x in nd),"rows":rows}
    for x in rows:
        if x["degenerate"]: audit.append(dict(x,L=L))
json.dump(nullj,open(F("null_x4.json"),"w"),indent=1)
json.dump(rej,open(F("rejudged.json"),"w"),indent=1)
json.dump(audit,open(F("filter_audit.json"),"w"),indent=1)
for L in nullj:
    print(L,{k:v for k,v in nullj[L].items() if k!="by_rel"})
    for r in RELS: print(" ",r,nullj[L]["by_rel"][r])
    print("  best nd",{r:(rej[L]["best_nondegenerate"][r]["cfg"],rej[L]["best_nondegenerate"][r]["window"],rej[L]["best_nondegenerate"][r]["pmax"],rej[L]["best_nondegenerate"][r]["familywise_p"]) for r in RELS}, "n clear",rej[L]["n_clear_bespoke"],"nrows",rej[L]["n_rows"],rej[L]["n_nondegenerate"])
print("AUDIT")
for a in audit: print(a["L"],a["cfg"],a["window"],a["rel"],a["pmax"],a["mds"],a["ioc_n"],a["preg"],a["familywise_p"],a["clears_bespoke_q99"])
