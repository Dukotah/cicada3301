import sys; from common import *
L=int(sys.argv[1]); D=int(sys.argv[2]); BUDGET=float(sys.argv[3])*60
CONST=("X4_v_prime_index_none_sign-1","X4_v_prime_index_atbash_pre_sign+1")
path=F("null_rows_L%d.jsonl"%L); done=0
if os.path.exists(path): done=sum(1 for _ in open(path))
f=open(path,"a"); t0=time.time(); nd=0
def free():
    import subprocess
    try: return float(subprocess.run(["powershell","-NoProfile","-Command","(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB"],capture_output=True,text=True,timeout=30).stdout)
    except Exception: return 9.9
for j in range(done,D):
    if time.time()-t0>BUDGET: break
    if j%100==0:
        w=0
        while free()<0.4 and w<20: time.sleep(60); w+=1
    S=dfshuffle(U,random.Random(3301+j)); rec={"j":j,"rows":[]}
    for cn,C,K,sg in x4_cfgs(S):
        if cn in CONST and j>=20: continue
        for s in STARTS:
            Cw,Kw=window(C,K,s,L)
            for rel in RELS:
                d=dec(Cw,Kw,rel,sg); a=AD.adjudicate(d["plain_idx"],pan=PAN)
                rec["rows"].append([cn,s,rel,round(float(a["pmax"]),3),int(a["mds"]),round(float(a["ioc"]),3)])
    f.write(json.dumps(rec)+"\n"); f.flush(); nd+=1
print("L",L,"done",done+nd,"elapsed",time.time()-t0)
