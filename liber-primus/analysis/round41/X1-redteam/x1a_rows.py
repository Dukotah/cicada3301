import json, math, os, sys
sys.dont_write_bytecode = True
AN = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
I1 = os.path.join(AN, "round41", "I1-null-refit")
f = json.load(open(os.path.join(I1, "fit.json"))); rj = json.load(open(os.path.join(I1, "rejudged_rounds36_40.json")))
A = -math.log1p(-0.01)
def mubeta(c): return c["u"] + c["beta"] * math.log(c["p_u"]), c["beta"]
def bar(par, N): return par[0] + par[1] * math.log(N / A)
sys.path.insert(0, os.path.join(AN, "round34", "I1-v3-null"))
import bars_v3
rows = rj["rows"]
idx = [0, 7, 11, 19, 28, len(rows) - 1]
# choose rows spread: also the closest margin one
mm = min(range(len(rows)), key=lambda i: rows[i]["margin_to_refit_actualN"])
chk = []
for i in sorted(set(idx + [mm])):
    r = rows[i]; rel = r["rel"]; L = r["L"]
    cg = f["cells"]["L%d|%s" % (L, rel)]; g = bar(mubeta(cg), r["N_actual"])
    pl = f["real_stores"]["pooled"][rel]; p = bar(mubeta(pl), r["N_actual"]) if L == 120 else None
    rec = max(g, p) if p else g
    rec1e6 = max(bar(mubeta(cg), 1e6), bar(mubeta(pl), 1e6)) if L == 120 else bar(mubeta(cg), 1e6)
    bv = bars_v3.bar_v3(r["N_actual"], L, rel, family="survivor12")
    chk.append({"i": i, "lane": r["lane"], "cell": r["cell"], "rel": rel, "L": L, "N": r["N_actual"], "best": r["best_pmax"],
                "mine_gumbel": round(g, 4), "mine_pooled": None if p is None else round(p, 4), "mine_record": round(rec, 4), "bars_v3": round(bv, 4),
                "stored_record": r["refit_bar_actualN"], "mine_1e6": round(rec1e6, 4), "stored_1e6": r["refit_bar_1e6"],
                "margin_mine": round(r["best_pmax"] - rec, 3), "crosses": r["best_pmax"] >= rec})
for c in chk: print(c)
print("n rows", len(rows), "any cross stored:", rj["any_cross_actualN"], rj["any_cross_1e6"])
print("R38/R40-B2 notes:", rj["R38-B2"], "|", str(rj["R40-B2"])[:300])
# all rows recompute
bad = 0; allc = 0
for r in rows:
    rel = r["rel"]; L = r["L"]; cg = f["cells"]["L%d|%s" % (L, rel)]
    g = bar(mubeta(cg), r["N_actual"]); p = bar(mubeta(f["real_stores"]["pooled"][rel]), r["N_actual"]) if L == 120 else g
    rec = max(g, p); allc += 1
    if abs(rec - r["refit_bar_actualN"]) > 0.003 or (r["best_pmax"] >= rec): bad += 1; print("MISMATCH", r["lane"], r["cell"], rel, rec, r["refit_bar_actualN"])
print("all rows checked", allc, "mismatch/cross", bad)
json.dump(chk, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "x1a_rows_out.json"), "w"), indent=1)
