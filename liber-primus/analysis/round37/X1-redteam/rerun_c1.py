import sys, json, random, itertools, time
sys.dont_write_bytecode=True
C1="C:/Users/Jeff/cicada3301/liber-primus/analysis/round37/C1-composed-clue-readings"
sys.path.insert(0,C1)
import sweep as S
E=S.E; np=S.np
rng=random.Random(910301); out={"seed":910301,"U1":[],"U3":[]}
t0=time.time()
lens0=E.word_lens_from(0)
# U3 cells: literal rho1/M29/A3 (ks1, ks2) and rho3/M28/A2 direct
for (rho,Mm,mode,rel) in [(1,29,"A3","keyskip1"),(1,29,"A3","keyskip2"),(3,28,"A2","direct")]:
    s=rng.randrange(29); sigma=rng.choice((-1,1)); P=S.held(rng=rng,L=240)
    Cc=E.enc_u3(P,lens0,rho,Mm,s,sigma,mode,rel if mode=="A3" else None,rng.randrange(1,10**9))[:240]
    j={"sub":"U3","rho":rho,"M":Mm,"mode":mode,"s":s,"sigma":sigma,"rel":rel,"sign":sigma,"o":0,"page":0}
    p1,a1=S.plant_run(j,Cc,120); p2,a2=S.plant_run(j,Cc,240); rec=S.rec_of(p2,P)
    # wrong-s control: wrong start must NOT recover
    j2=dict(j); j2["s"]=(s+5)%29
    q1,b1=S.plant_run(j2,Cc,120)
    e={"rho":rho,"M":Mm,"mode":mode,"rel":rel,"s":s,"sigma":sigma,"wrong_s_pmax120":round(float(b1["pmax"]),3)}; e.update(S.judge(float(a1["pmax"]),float(a2["pmax"]),rec,rel)); out["U3"].append(e); print(e,flush=True)
plant_ids={"direct":"U1-001","sha256ctr":"U1-002","pbkdf2":"U1-003"}
for route,rel in [("direct","keyskip2"),("sha256ctr","keyskip1")]:
    pj=[j for j in S.u1_jobs((route,)) if j["cid"]==plant_ids[route] and j["form"]=="UP"][0]
    K=S.u1_key(route,pj["cid"],"UP",pj["text"]); jobs=S.u1_jobs((route,))
    o=rng.randrange(8); P=S.held(rng=rng,L=240); Cc=E.encipher_with_key(P,K[o:],rel,rng.randrange(1,10**9))[:240]
    best={}
    for j in jobs:
        Kj=S.u1_key(route,j["cid"],j["form"],j["text"]); d,a=S.v3dec(Cc[:120],Kj,j["rel"],j["sign"],j["o"])
        kk="%s|%s"%(j["cid"],j["form"])
        if float(a["pmax"])>best.get(kk,(-9,))[0]: best[kk]=(float(a["pmax"]),)
    rank=sorted(best.items(),key=lambda t:-t[1][0]); pk="%s|UP"%plant_ids[route]
    pos=[i for i,(k,v) in enumerate(rank) if k==pk][0]+1
    d2,a2=S.v3dec(Cc,K,rel,-1,o); rec=S.rec_of(d2["plain_idx"],P)
    e={"route":route,"rel":rel,"offset":o,"rank":pos,"n":len(rank),"planted_pmax120":round(best[pk][0],3),"runner_up":round(rank[1][1][0],3) if pos==1 else round(rank[0][1][0],3),"pmax240":round(float(a2["pmax"]),3),"recovery240":round(rec,4)}
    out["U1"].append(e); print(e,flush=True)
out["elapsed_s"]=round(time.time()-t0,1)
json.dump(out,open("rerun_c1.json","w"),indent=1)
