"""W2-C6 real read 1 (after Addendum 1) — direct 116-grid on p49/p54/p50/p55 -> direct.json.

p55 added per Addendum 1 Disclosure A (its grid numbers were frozen at the checkpoint;
recomputed here identically for the record — same glue, same stream, deterministic).
"""
import json
import time

import numpy as np

import glue as S
import adjudicate as A

t0 = time.time()
pan = S.panel()
c = S.canon()
P = S.pages()
nulls = json.load(open("nulls.json"))
power = json.load(open("power.json"))

out = {"N_budget": S.N_DIRECT, "pages": {}, "n_total": 0, "n_crossers": 0, "crossers": []}
for pg in (49, 54, 50, 55):
    st, L = P[pg]
    x = c[st:st + L]
    pm, r, X, meta = S.grid_pmax(x, pan)
    bar = nulls["nodes"][str(L)]["bar_of_record_N600"]
    j = int(pm.argmax())
    full = A.adjudicate(X[j], pan=pan)
    rec = {"L": L, "bar": bar,
           "EN_power": power["node_power"][str(L)]["N600"]["EN_power"],
           "LA_power": power["node_power"][str(L)]["N600"]["LA_power"],
           "best_pmax": round(float(pm[j]), 4), "best_map": meta[j],
           "best_stats": {k: (round(full[k], 4) if isinstance(full[k], float) else full[k])
                          for k in ("en", "pmax", "preg", "pmax_ne", "pcon", "ioc",
                                    "mds", "h2", "zl", "degenerate")},
           "best_translit": A.idx_to_trans(X[j]),
           "n_crossers": int((pm >= bar).sum())}
    out["pages"]["p%d" % pg] = rec
    out["n_total"] += len(pm)
    out["n_crossers"] += rec["n_crossers"]
    if rec["n_crossers"]:
        for i in np.where(pm >= bar)[0]:
            fr = A.adjudicate(X[i], pan=pan)
            out["crossers"].append({"page": pg, "pmax": round(float(pm[i]), 4),
                                    "map": meta[i], "degenerate": fr["degenerate"],
                                    "translit": A.idx_to_trans(X[i])})
    print("p%d" % pg, "L=%d" % L, "best %.4f vs bar %.4f crossers %d" %
          (pm[j], bar, rec["n_crossers"]), flush=True)

out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open("direct.json", "w"), indent=1)
print("TOTAL", out["n_total"], "crossers", out["n_crossers"])
