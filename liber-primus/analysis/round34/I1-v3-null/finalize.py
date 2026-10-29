import json, collections, math, sys
sys.dont_write_bytecode = True
from bars_v3 import bar_v3
rows = [json.loads(l) for l in open("control_plants.jsonl")]
g = collections.defaultdict(list)
for r in rows: g[(r["L"], r["rel"], r["register"])].append(r)
cells = {}; fails = []
for (L, rel, reg), rs in sorted(g.items()):
    d = {"n": len(rs), "median_pmax": sorted(x["pmax"] for x in rs)[len(rs)//2], "min_pmax": min(x["pmax"] for x in rs), "median_rec": sorted(x["rec"] for x in rs)[len(rs)//2]}
    for fam in ("lp2", "register"):
        if rel == "free" and fam == "register": continue
        b = bar_v3(1e6, L, rel, family=fam)
        d["bar1e6_" + fam] = round(b, 3)
        d["clear_" + fam] = sum(x["pmax"] >= b for x in rs)
        d["pass_" + fam] = d["clear_" + fam] >= 19
    d["clear_gpd_lp2"] = sum(x["pmax"] >= bar_v3(1e6, L, rel, method="gpd") for x in rs)
    cells["%d|%s|%s" % (L, rel, reg)] = d
    if not d["pass_lp2"]: fails.append(("%d|%s|%s" % (L, rel, reg), d["clear_lp2"], d["bar1e6_lp2"], d["median_pmax"]))
allp = all(c["pass_lp2"] for c in cells.values()); allr = all(c.get("pass_register", True) for c in cells.values())
tab = {}
for fam in ("lp2", "register"):
    for rel in ("keyskip1", "keyskip2"):
        for L in (31, 120, 240, 400):
            tab["%s|%s|L%d" % (fam, rel, L)] = {("N%g" % N): round(bar_v3(N, L, rel, family=fam), 2) for N in (1e5, 2e5, 1e6, 1e9)}
tab["free|L120"] = {("N%g" % N): round(bar_v3(N, 120, "free"), 2) for N in (1e5, 2e5, 1e6, 1e9)}
gp = {"%s|L%d" % (rel, L): {("N%g" % N): round(bar_v3(N, L, rel, method="gpd"), 2) for N in (2e5, 1e6, 1e9)} for rel in ("keyskip1", "keyskip2") for L in (31, 120, 240, 400)}
json.dump({"n_plants": len(rows), "rule": ">=19/20 seeds with pmax >= bar(N=1e6, alpha=.01) per (L, relation, register)", "all_pass_lp2": allp, "all_pass_register": allr,
           "failures_lp2": fails, "cells": cells, "bar_table": tab, "gpd_sensitivity_table": gp}, open("control.json", "w"), indent=1)
print(len(rows), "allp", allp, "allr", allr, "nfail", len(fails))
for f in fails: print(f)
for k, v in tab.items(): print(k, v)
