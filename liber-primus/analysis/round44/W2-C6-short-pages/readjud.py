"""W2-C6 real read 2 — re-adjudicate the standing sweeps' stored short-page bests under
the bespoke matched-length bars -> readjud.json. ZERO new decodes (PREREG §5): stored
bests reused verbatim; bars from nulls.json; power from power.json; bars_v3 keyskip
cross-check reported alongside.
"""
import json

import glue as S

nulls = json.load(open("nulls.json"))
power = json.load(open("power.json"))
PAGE_L = {49: 66, 50: 92, 54: 76}

out = {"cells": [], "n_crossers": 0,
       "note_p55": "p55 (85 runes, the B-24 AN-END body) is ABSENT from all four standing "
                   "per-page sweeps (pages 0-54 only); no stored best exists to re-adjudicate. "
                   "Its first per-page adjudication is this cell's direct read (direct.json)."}

for lane, d in S.LANES.items():
    for pg, best in d["best"].items():
        L = PAGE_L[pg]
        node = nulls["nodes"][str(L)]
        cell = {"lane": lane, "page": pg, "L": L, "stored_best_pmax": best,
                "lane_bar_used_originally": d["lane_bar"], "lane_bar_node": "L=120"}
        for tag, NN in (("page", d["N_page"]), ("lane", d["N_lane"])):
            key = "%s|%s|N=%d" % (lane, tag, NN)
            bar = node["readj_bars"][key]
            pw = power["node_power"][str(L)][key]
            cell["bespoke_%s" % tag] = {
                "N": NN, "bar": bar, "crosses": bool(best >= bar),
                "EN_power": pw["EN_power"], "LA_power": pw["LA_power"],
                "margin": round(bar - best, 4)}
            out["n_crossers"] += int(best >= bar)
        cell["bars_v3_keyskip_crosscheck"] = node["bars_v3_keyskip_crosscheck"][
            "%s|N=%d" % (lane, d["N_page"])]
        out["cells"].append(cell)
        print(lane, "p%d" % pg, "stored %.3f vs bespoke page-N bar %.3f (power EN %.2f) -> %s"
              % (best, cell["bespoke_page"]["bar"], cell["bespoke_page"]["EN_power"],
                 "CROSSES" if cell["bespoke_page"]["crosses"] else "under"), flush=True)

json.dump(out, open("readjud.json", "w"), indent=1)
print("cells", len(out["cells"]), "crossers", out["n_crossers"])
