import json, os, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); AN = os.path.abspath(os.path.join(HERE, "..", ".."))
B = os.path.join(AN, "round40", "B2-offsets")
sys.path.insert(0, os.path.join(AN, "round34", "I1-v3-null")); import bars_v3
s = json.load(open(os.path.join(B, "sweep_summary.json")))["cells"]
rows = []
for k, c in s.items():
    cell, rel = k.split("|"); N = c["N_actual"]
    rec = bars_v3.bar_v3(N, 120, rel, family="survivor12"); r1e6 = bars_v3.bar_v3(1e6, 120, rel, family="survivor12")
    rows.append({"cell": cell, "offset": c["offset"], "sign": c["sign"], "rel": rel, "chunks_done": c["chunks_done"], "N_actual": N, "best_pmax": c["best_pmax"], "best_seed": c["best_seed"], "best_preg": c["best_preg"],
                 "null12_bar_actualN_stored": c["bar120_actualN"], "null12_bar_1e6_stored": c["bar120_declN"], "bar_of_record_actualN": round(rec, 4), "bar_of_record_1e6": round(r1e6, 4),
                 "margin_actualN": round(c["best_pmax"] - rec, 3), "margin_1e6": round(c["best_pmax"] - r1e6, 3), "crosses_actualN": c["best_pmax"] >= rec, "crosses_1e6": c["best_pmax"] >= r1e6})
rows.sort(key=lambda r: -r["best_pmax"])
for r in rows: print(r["cell"], r["rel"], r["N_actual"], r["best_pmax"], "stored", r["null12_bar_actualN_stored"], "record", r["bar_of_record_actualN"], "margin", r["margin_actualN"], r["margin_1e6"])
# controls vs the bar of record at 1e6
ctl = {}
for cn in ("o0_sp", "o1_sm", "o2_sm", "o3_sm", "o28_sm"):
    d = json.load(open(os.path.join(B, "control_%s.json" % cn))); n = rec_n = 0; below = []
    for p in d["plants"]:
        if p["prefilter_pass"]:
            n += 1; b1 = bars_v3.bar_v3(1e6, 120, p["rel"], family="survivor12"); b2_ = bars_v3.bar_v3(1e6, 240, p["rel"], family="survivor12")
            ok = p["pmax120"] >= b1 and p["pmax240"] >= b2_ and p["recovery240"] >= 0.90
            rec_n += ok
            if p["recover"] != ok: below.append((p["rel"], p["register"], p["pmax120"], p["pmax240"], p["recover"], ok))
    ctl[cn] = {"plants": len(d["plants"]), "prefilter": n, "recover_stored": d["recover_total"], "recover_vs_record_bars": rec_n, "changed": below,
               "min_pmax120": min(p["pmax120"] for p in d["plants"] if p["prefilter_pass"]), "min_pmax240": min(p["pmax240"] for p in d["plants"] if p["prefilter_pass"])}
    # gate (>=3 per register x skip split pooled) recomputed under record bars
    sp = {}
    for p in d["plants"]:
        b1 = bars_v3.bar_v3(1e6, 120, p["rel"], family="survivor12"); b2_ = bars_v3.bar_v3(1e6, 240, p["rel"], family="survivor12")
        ok = bool(p["prefilter_pass"] and p["pmax120"] >= b1 and p["pmax240"] >= b2_ and p["recovery240"] >= 0.90)
        key = "%s|%s" % (p["register"], "skip" if p["with_skip_head24"] else "free"); sp.setdefault(key, [0, 0]); sp[key][0] += ok; sp[key][1] += 1
    ctl[cn]["splits_recover_n"] = sp; ctl[cn]["gate_ge3_record_bars"] = all(v[0] >= 3 for v in sp.values())
d = json.load(open(os.path.join(B, "control_misaligned_o1_sm.json"))); k = 0
for p in d["plants"]:
    if p["prefilter_pass"]:
        b1 = bars_v3.bar_v3(1e6, 120, p["rel"], family="survivor12"); b2_ = bars_v3.bar_v3(1e6, 240, p["rel"], family="survivor12")
        k += bool(p["pmax120"] >= b1 and p["pmax240"] >= b2_ and p["recovery240"] >= 0.90)
ctl["misaligned_o1"] = {"n": len(d["plants"]), "prefilter": d["prefilter_total"], "recover_stored": d["recover_total"], "recover_vs_record_bars": k,
                         "pmax_of_recovered": [(p["pmax120"], p["pmax240"], p["recovery240"]) for p in d["plants"] if p["recover"]],
                         "by_split": d["pooled_by_register_skip"]}
for k_, v in ctl.items(): print(k_, {a: b for a, b in v.items() if a != "splits_recover_n"})
json.dump({"rows": rows, "controls": ctl}, open(os.path.join(HERE, "x1a_b2_rejudge.json"), "w"), indent=1)
