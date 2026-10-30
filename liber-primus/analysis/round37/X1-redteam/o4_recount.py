import re, json, collections
L=open('../../round36/O4-clue-coverage/matrix.md',encoding='utf-8').read().splitlines()
fam=["F%d"%i for i in range(1,12)]
cells={}
for ln in L:
    m=re.match(r"\| ([HLS]\d+) \|(.*)\|\s*$",ln)
    if m and not ln.startswith("| row"):
        rid=m.group(1); parts=[p.strip() for p in ln.split("|")[3:-1]]
        for f,p in zip(fam,parts): cells[(rid,f)]=p
def cnt():
    c=collections.Counter()
    for v in cells.values():
        k='NEVER' if v.startswith('NEVER') else 'T-EN' if v.startswith('T-EN') else 'T-LEG' if v.startswith('T-LEG') else 'PART' if v.startswith('PART') else 'T' if v.startswith('T') else None
        if k: c[k]+=1
    return c
out={"matrix_as_filed":dict(cnt())}
# Round 36 X1 correction
for k in (("H7","F2"),("H12","F2")): assert cells[k]=="NEVER"; cells[k]="T-LEG R10b,c18 (X1/R36)"
out["after_R36_X1_correction"]=dict(cnt())
steps={
 "C1 U3 literal composed rule (H2,H3,H4 x F1)":[("H2","F1"),("H3","F1"),("H4","F1")],
 "C1 U2 LP1 number schedules (H4 x F7)":[("H4","F7")],
 "C2 U7 book-code indices (H12 x F6)":[("H12","F6")],
 "C2 U4 prime line sums (L16 x F2)":[("L16","F2")],
}
for nm,ks in steps.items():
    for k in ks: assert cells[k]=="NEVER",(k,cells[k]); cells[k]="T R37 "+nm[:2]
up={"C1 U1 clue strings (H1..H5 x F4)":[("H%d"%i,"F4") for i in range(1,6)],
    "C3 re-score (H2xF3, H4xF2, L2xF2, S1xF2)":[("H2","F3"),("H4","F2"),("L2","F2"),("S1","F2")]}
for nm,ks in up.items():
    for k in ks: assert cells[k].startswith(("T-EN","T-LEG")),(k,cells[k]); cells[k]="T R37"
out["after_R37"]=dict(cnt())
nev=collections.Counter(f for (r,f),v in cells.items() if v=="NEVER")
out["NEVER_by_family_after"]=dict(sorted(nev.items(),key=lambda t:int(t[0][1:])))
out["NEVER_cells_after"]=[f"{r} x {f}" for (r,f),v in cells.items() if v=="NEVER"]
out["F5_never"]=[f"{r}" for (r,f),v in cells.items() if v=="NEVER" and f=="F5"]
out["F1_never"]=[f"{r}" for (r,f),v in cells.items() if v=="NEVER" and f=="F1"]
print(json.dumps({k:v for k,v in out.items() if k!="NEVER_cells_after"},indent=1))
json.dump(out,open("o4_recount.json","w"),indent=1)
