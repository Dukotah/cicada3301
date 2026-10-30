import sys, json, re, numpy as np
sys.dont_write_bytecode=True
src=open("C:/Users/Jeff/cicada3301/liber-primus/analysis/round37/C2-recognizer-index-readings/U4-prime-line-sums/measure.py",encoding="utf-8").read()
cut=src.index("ctrl_pages = ")
G={"__file__":"C:/Users/Jeff/cicada3301/liber-primus/analysis/round37/C2-recognizer-index-readings/U4-prime-line-sums/measure.py","__name__":"m"}
exec(compile(src[:cut],"measure_head","exec"),G)
data=G["data"]; PR=G["PR"]; sv=G["sv"]; val=G["val"]
rng=np.random.default_rng(910304); NS=10000
res={}
R=json.load(open("C:/Users/Jeff/cicada3301/liber-primus/analysis/round37/C2-recognizer-index-readings/U4-prime-line-sums/results.json"))
pooled_obs=0; pooled_n=0; pool=0; n5=0
for lab,d in data.items():
    # true physical lines on the full position array (interrupters are 0-valued positions)
    lines=G["lines_of"](lab)
    full_lens=[len(l) for l in lines]
    vals=d["plain"]  # length n incl. interrupters as 0
    assert len(vals)==sum(full_lens)
    b=np.concatenate([[0],np.cumsum(full_lens)[:-1]]).astype(int)
    s=np.add.reduceat(vals,b); k=int(sv[s].sum())
    # as-run (misaligned) for comparison
    b2=np.concatenate([[0],np.cumsum(d["plens"])[:-1]]).astype(int)
    k_asrun=int(sv[np.add.reduceat(vals,b2)].sum())
    # null A: shuffle all positions (interrupter zeros move too) with the TRUE boundaries
    # null B: shuffle only the rune values among non-interrupter positions, interrupters stay in place
    nz=np.nonzero(vals)[0]; isint=(vals==0)
    nu=np.empty(NS); nuB=np.empty(NS)
    for a in range(NS):
        v=vals[rng.permutation(len(vals))]; nu[a]=sv[np.add.reduceat(v,b)].sum()
        v2=vals.copy(); v2[nz]=vals[nz][rng.permutation(len(nz))]; nuB[a]=sv[np.add.reduceat(v2,b)].sum()
    r={"lines":len(full_lens),"n_interrupters":d["n_interrupters"],"passing_true_alignment":k,"passing_as_run":k_asrun,"as_run_reported":R["plaintext"]["per_page"][lab]["passing"],
       "p_shuffle_all_positions":float((1+(nu>=k).sum())/(NS+1)),"p_shuffle_runes_only":float((1+(nuB>=k).sum())/(NS+1)),
       "lens_as_run":d["plens"],"lens_true":full_lens}
    res[lab]=r; print(lab,r["lines"],"intr",r["n_interrupters"],"true",k,"asrun",k_asrun,"reported",r["as_run_reported"],"pA",r["p_shuffle_all_positions"],"pB",r["p_shuffle_runes_only"],flush=True)
    pooled_obs+=k; pooled_n+=len(full_lens); pool=pool+nuB
    n5+= r["p_shuffle_runes_only"]<0.05
res["pooled"]={"passing":pooled_obs,"lines":pooled_n,"p_shuffle_runes_only":float((1+(pool>=pooled_obs).sum())/(NS+1)),"pages_p_lt_0.05":int(n5)}
print(res["pooled"])
json.dump(res,open("C:/Users/Jeff/cicada3301/liber-primus/analysis/round37/X1-redteam/rerun_u4.json","w"),indent=1)
