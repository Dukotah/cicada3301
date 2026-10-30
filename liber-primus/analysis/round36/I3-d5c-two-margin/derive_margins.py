import json,glob
def load35(L,s):
    o=[]
    for k in ["a","b"]:
        d=json.load(open(f"round35/I3-d5c-prereg/feat/CICADA-R35I3{k}_{L}_{s}.json"))
        o+=[(c["pmax"]-d["bar"],c["preg_name"],c["label"],s) for c in d["cases"]]
    return o
def load34(L):
    o=[]
    for k in ["X1R33","I4b","I4c","R34I3"]:
        d=json.load(open(f"round34/I3-d5c-calibration/feat_CICADA-{k}_{L}.json"))
        o+=[(c["pmax"]-d["bar"],c["preg_name"],c["label"],c["stream"]) for c in d["cases"] if c["pop"]=="nv"]
    return o
def an(L,data,reg,gen):
    h=[x[0] for x in data if x[2]=="halluc" and x[1]==reg]
    g=[x[0] for x in data if x[2]=="genuine" and x[1]==reg and x[3] in gen]
    return h,g
def best(h,g):
    # smallest m with catch>=.9 ; report FR there
    if not h: return None
    hs=sorted(h); import math
    n=len(h); need=math.ceil(.9*n)
    m=hs[need-1]  # catch = frac(h<m)... reject if mg<m ; need >=need below m
    # smallest m s.t. count(h<m)>=need -> just above hs[need-1]
    m=hs[need-1]+1e-9
    fr=sum(1 for x in g if x<m)/len(g) if g else None
    return dict(m=round(m,3),nh=n,ng=len(g),FR=None if fr is None else round(fr,3))
for L in (150,300):
    d=load35(L,"EN_NOVOWEL")+load35(L,"EN_HALFVOWEL")
    print(L,"NV",best(*an(L,d,"EN_NOVOWEL",["EN_NOVOWEL"])),"HV",best(*an(L,d,"EN_HALFVOWEL",["EN_HALFVOWEL"])))
d=load34(240);print(240,"NV",best(*an(240,d,"EN_NOVOWEL",["EN_NOVOWEL"])),"HV",best(*an(240,d,"EN_HALFVOWEL",["EN_NOVOWEL"])))
h,g=an(240,d,"EN_HALFVOWEL",[]);print(sorted(h))
