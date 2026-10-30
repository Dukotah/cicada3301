import sys; from common import *
rng=random.Random(3801); out={"date":time.strftime("%Y-%m-%dT%H:%M:%S"),"method":"C_i=g^-1(P_i); K=f(C) re-derived from the planted ciphertext; family decoder (beam_v3 panel_max keyskip1/2, family sign)","cells":[],"image":{}}
def gmap(tn,vn,sg):
    tf=dict(TF)[tn]; f=[tf([c])[0]%N for c in range(N)]
    return [(((c if vn=="none" else N-1-c))+sg*f[c])%N for c in range(N)]
bars={(L,r):bar12(1e6,L,r) for L in (120,240) for r in RELS}
def plant(reg,g,L,proj):
    arr=TEST[reg].astype(np.int64); st=rng.randrange(0,len(arr)-L-5); P=arr[st:st+L].tolist()
    img=sorted(set(g))
    if proj: P=[p if p in img else min(img,key=lambda q:min((p-q)%N,(q-p)%N)) for p in P]
    pre={}
    for c,p in enumerate(g): pre.setdefault(p,[]).append(c)
    C=[rng.choice(pre[p]) for p in P]; return C,P
for tn,tf in TF:
  for vn in ("none","atbash_pre"):
    for sg in (-1,1):
      cn="X4_%s_%s_sign%+d"%(tn,vn,sg); g=gmap(tn,vn,sg); im=len(set(g)); out["image"][cn]=im
      if im==1: continue
      bij=(im==N)
      for reg in ("EN_MODERN","LATIN","GREEK"):
        for j in range(2):
          for L in (120,240):
            C,P=plant(reg,g,L,not bij); 
            letters=C if vn=="none" else [(N-1-c)%N for c in C]
            K=[v%N for v in tf(C)]
            # sanity: exact inverse
            assert [(l+sg*k)%N for l,k in zip(letters,K)]==P
            for rel in RELS:
              d=dec(letters,K[:1024],rel,sg); a=AD.adjudicate(d["plain_idx"],pan=PAN)
              rec=float(B2.recovery(d["plain_idx"],P))
              out["cells"].append({"cfg":cn,"gate":bij,"reg":reg,"j":j,"L":L,"rel":rel,"recovery":round(rec,4),"pmax":round(float(a["pmax"]),3),"preg":REGS[a["preg"]],"bar_declared":round(bars[(L,rel)],3)})
    print(cn,im,flush=True)
G=[c for c in out["cells"] if c["gate"]]
for L in (120,240):
    q=[c for c in G if c["L"]==L]; out["gate_L%d"%L]={"n":len(q),"recovered_ge_0.90":sum(c["recovery"]>=0.90 for c in q),"min_recovery":min(c["recovery"] for c in q)}
out["gate_pass"]=all(out["gate_L%d"%L]["recovered_ge_0.90"]>=out["gate_L%d"%L]["n"]-1 for L in (120,240))
S={}
for c in out["cells"]:
    if not c["gate"]:
        s=S.setdefault(c["cfg"],[]); s.append(c["recovery"])
out["supplementary_image_limited"]={k:{"n":len(v),"mean_recovery":round(float(np.mean(v)),3),"min":min(v),"ge0.90":sum(x>=0.9 for x in v)} for k,v in S.items()}
json.dump(out,open(F("control.json"),"w"),indent=1)
print(out["gate_L120"],out["gate_L240"],out["gate_pass"]); print(json.dumps(out["supplementary_image_limited"],indent=0))
