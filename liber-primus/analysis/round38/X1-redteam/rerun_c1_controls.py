import sys,os,json,random,importlib.util,time
sys.dont_write_bytecode=True
H=os.path.dirname(os.path.abspath(__file__)); C1=os.path.join(H,"..","C1-semantic-road")
sys.path.insert(0,os.path.join(H,"..","..","round37","C1-composed-clue-readings"))
sys.path.insert(0,C1)
spec=importlib.util.spec_from_file_location("c1sweep",os.path.join(C1,"sweep.py")); M=importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
S,EN=M.S,M.EN
rng=random.Random(424242); out=[]
for var,mode in [("A-R29","A3"),("B-R28","A1")]:
    for sigma in (-1,1):
        s=rng.randrange(29) if mode!="A3" else rng.randrange(726)
        P=S.held(rng=rng,L=240); seed=rng.randrange(1,10**9); lens0=M.lens_p(0)
        Cc=EN.enc(P,lens0,var,s,sigma,mode,"keyskip1" if mode=="A3" else None,seed)[:240]
        j={"var":var,"mode":mode,"s":s,"sigma":sigma,"page":0}
        U0=list(S.U); s0=S.page_start(0); S.U[s0:s0+len(Cc)]=Cc
        try:
            p1,a1=M.run(j,120); p2,a2=M.run(j,240)
        finally: S.U[:]=U0
        rec=S.rec_of(p2,P); e={"var":var,"mode":mode,"s":s,"sigma":sigma}; e.update(S.judge(float(a1["pmax"]),float(a2["pmax"]),rec,"keyskip1")); out.append(e); print(e,flush=True)
        # negative: wrong s must not recover
        j2=dict(j); j2["s"]=(s+1)%(726 if mode=="A3" else 29)
        U0=list(S.U); S.U[s0:s0+len(Cc)]=Cc
        try: q1,b1=M.run(j2,120)
        finally: S.U[:]=U0
        out.append({"wrong_s_pmax120":round(float(b1["pmax"]),3)}); print(out[-1])
json.dump(out,open(os.path.join(H,"rerun_c1_controls.json"),"w"),indent=1)
