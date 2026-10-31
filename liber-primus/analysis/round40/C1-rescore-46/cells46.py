import re,json,collections
L=open('../../round36/O4-clue-coverage/matrix.md',encoding='utf-8').read().splitlines()
fam=["F%d"%i for i in range(1,12)]
cells={}
for ln in L:
    m=re.match(r"\| ([HLS]\d+) \|(.*)\|\s*$",ln)
    if m and not ln.startswith("| row"):
        rid=m.group(1); parts=[p.strip() for p in ln.split("|")[3:-1]]
        for f,p in zip(fam,parts): cells[(rid,f)]=p
for k in (("H7","F2"),("H12","F2")): cells[k]="T-LEG R10b,c18 (X1/R36)"
for k in [("H2","F1"),("H3","F1"),("H4","F1"),("H4","F7"),("H12","F6"),("L16","F2")]+[("H%d"%i,"F4") for i in range(1,6)]+[("H2","F3"),("H4","F2"),("L2","F2"),("S1","F2")]: cells[k]="T R37"
for k in [("H5","F1")]: pass
json.dump({f"{r}x{f}":v for (r,f),v in cells.items() if v.startswith(("T-EN","T-LEG"))},open('cells_raw.json','w'),indent=1)
