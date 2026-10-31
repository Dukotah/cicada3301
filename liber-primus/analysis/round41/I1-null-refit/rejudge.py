"""R41 I1: re-judge every Round 36-40 best row against the refit (survivor12) bar at its actual N and at N=1e6.  python rejudge.py
Reads stored summaries only (no decoding).  A row 'crosses' iff best_pmax >= refit bar at that N."""
import json, math, os, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); AN = os.path.abspath(os.path.join(HERE, "..", ".."))
S = json.load(open(os.path.join(HERE, "null_survivor12.json")))["cells"]
A = -math.log1p(-0.01)


sys.path.insert(0, os.path.join(AN, "round34", "I1-v3-null"))
from bars_v3 import bar_v3


def bar(L, rel, N): return bar_v3(N, L, rel, family="survivor12")      # bar of record (see fit.json bar_of_record)


def bar_refit(L, rel, N):
    c = S["L%d|%s" % (L, rel)]; return c["mu"] + c["beta"] * math.log(N / A)


def J(*p): return json.load(open(os.path.join(AN, *p)))


rows = []


def add(lane, label, rel, N, best, stored_actual=None, L=120, extra=None, N_alt=None):
    r = {"lane": lane, "cell": label, "rel": rel, "L": L, "N_actual": N, "best_pmax": best, "stored_bar_actualN_null12": stored_actual,
         "refit_bar_actualN": round(bar(L, rel, N), 3), "refit_bar_1e6": round(bar(L, rel, 1e6), 3), "gumbel_refit_only_actualN": round(bar_refit(L, rel, N), 3)}
    r["margin_to_refit_actualN"] = round(best - r["refit_bar_actualN"], 3); r["margin_to_refit_1e6"] = round(best - r["refit_bar_1e6"], 3)
    r["crosses_actualN"] = bool(best >= r["refit_bar_actualN"]); r["crosses_1e6"] = bool(best >= r["refit_bar_1e6"])
    if N_alt:
        r["N_screened_sensitivity"] = N_alt; r["refit_bar_screenedN"] = round(bar(L, rel, N_alt), 3); r["crosses_screenedN"] = bool(best >= bar(L, rel, N_alt))
    if extra: r.update(extra)
    rows.append(r)


d = J("round36", "B1-orbit-12reg", "readjud_summary.json")
for k, v in d["cells"].items():
    cell, rel = k.split("|"); add("R36-B1", cell, rel, v["N_actual"], v["best_pmax"], v.get("bar120_actualN") or {"keyskip1": 8.130, "keyskip2": 8.044}[rel])
d = J("round37", "I2-pfv4-12reg", "sweep_summary_final.json")
for k, v in d["cells"].items():
    cell, rel = k.split("|"); add("R37-I2", cell, rel, v["N_actual"], v["best_pmax"], v["bar120_actualN"])
d = J("round40", "B1-bash-versions", "sweep_summary_final.json")
for k, v in d["cells"].items():
    cell, rel = k.split("|"); add("R40-B1", cell, rel, v["N_actual"], v["best_pmax"], v["bar120_actualN"])
for g in ("B04", "KDF", "R17PAD", "COSPAD"):
    d = J("round40", "B3-english-era-grids", "final_%s.json" % g)
    for rel, v in d["rels"].items():
        add("R40-B3", g, rel, v["N_actual"], v["best_pmax"], v["bar120_actualN"], N_alt=v["N_screened"], extra={"best_kid": v.get("best_kid"), "best_degenerate": v.get("best_degenerate")})
d = J("round40", "C1-rescore-46", "rescore_summary.json")["families"]
for fam, v in d.items():
    if v["kind"] == "direct": continue
    b = v["best_nondegenerate"]
    if isinstance(b, str): b = eval(b)
    for rel in ("keyskip1", "keyskip2"):
        N = v["rows"][rel]
        add("R40-C1", fam, rel, N, b[rel]["pmax"], v["bars"][rel].get("actualN") or v["bars"][rel].get("N_survivors"),
            N_alt=v.get("heads_screened"), extra={"stored_bar_screenedN_null12": v["bars"][rel].get("actualN_screened"), "kind": v["kind"], "best_kid": b[rel].get("kid")})
direct = {fam: {"best_pmax": v["best_pmax"], "p_family_lane_null": v.get("p_family"), "note": "direct (non-key) family: the survivor bar does not apply; see matched nulls (bars_matched.py)"} for fam, v in d.items() if v["kind"] == "direct"}
out = {"bar_of_record": "see fit.json (bar_of_record) -- refit POT bar of the survivor12 population; N=1e6 and actual N both reported",
       "R38-B2": "no R38-B2 lane exists in round38/ (lanes: C1, C2, I1, I2, S1, S2, X1); R38-S2-PHP-SANDBOX persisted zero rows; nothing to re-judge",
       "R40-B2": "key-offset sweep was still running at Round 40 close and had no RESULTS.md; not re-judged here (filed to B2 audit)",
       "rows": rows, "direct_families_not_rejudged": direct,
       "any_cross_actualN": [r for r in rows if r["crosses_actualN"]], "any_cross_1e6": [r for r in rows if r["crosses_1e6"]],
       "min_margin_actualN": min(r["margin_to_refit_actualN"] for r in rows) if rows else None, "n_rows": len(rows)}
out["min_margin_actualN_row"] = min(rows, key=lambda r: -r["margin_to_refit_actualN"] * -1) if False else max(rows, key=lambda r: r["margin_to_refit_actualN"])
json.dump(out, open(os.path.join(HERE, "rejudged_rounds36_40.json"), "w"), indent=1, default=float)
print("rows", len(rows), "cross_actualN", len(out["any_cross_actualN"]), "cross_1e6", len(out["any_cross_1e6"]))
for r in sorted(rows, key=lambda r: -r["margin_to_refit_actualN"])[:8]:
    print(r["lane"], r["cell"], r["rel"], r["N_actual"], r["best_pmax"], r["refit_bar_actualN"], r["margin_to_refit_actualN"], r["refit_bar_1e6"])
