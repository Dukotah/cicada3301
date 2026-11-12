"""R44 / W2-A1 step 3 — the real short-stream reads (PREREG §4) -> results.json.

Gate: plant_power.json glue_plant_L120.passed must be True.
Streams x the FIXED 116 grid vs the Addendum-1 bars of record; verdicts obey the power floor
(L=13 and the 2-symbol dot stream are measured-only by PREREG).  Any crosser at a
verdict-capable node: full adjudicate + degenerate guard -> FLAGGED-FOR-ORACLE, never certified.
"""
import json

import numpy as np

import shortnull as S
import adjudicate as A

pp = json.load(open("plant_power.json"))
assert pp["glue_plant_L120"]["passed"], "glue plant gate failed"
bars = {int(k): v for k, v in pp["bars"].items()}
capable = {int(k): v["verdict_capable"] for k, v in pp["nodes"].items()}

pan = S.panel()
c = S.canon()

ch = json.load(open("../P1-red-ink/channel.json"))
dc_pos = [d["pos"] for d in ch["full"]["dropcaps"]]
dropcaps13 = c[np.asarray(dc_pos)]
assert S.gp.indices_to_translit(dropcaps13) == "SLPAXLUMDNGIAFA"
title9 = c[3603:3612]
urpn4 = c[12644:12648]
assert S.gp.indices_to_translit(title9) == "FULMAEAYOEA"
assert S.gp.indices_to_translit(urpn4) == "URPN"
titleURPN13 = np.concatenate([title9, urpn4])
grand_pos = sorted(dc_pos + list(range(3603, 3612)) + list(range(12644, 12648)))
grand26 = c[np.asarray(grand_pos)]
fb = json.load(open("../P1-red-ink/results.json"))["families"]["B"]
dotvals30 = np.asarray([b["n"] for b in fb["blocks_13_or_10"]], dtype=np.int64)
assert len(dotvals30) == 30 and set(dotvals30.tolist()) == {13, 10}

STREAMS = [("dropcaps13", dropcaps13, 13),
           ("titleURPN13", titleURPN13, 13),
           ("grand26", grand26, 26),
           ("dotvals30", dotvals30 % S.N, 30)]

out = {"bars": bars, "streams": {}, "crossers": [], "n_total": 0}
for name, x, L in STREAMS:
    pm, r, X, meta = S.grid_pmax(x, pan)
    i = int(pm.argmax())
    full = A.adjudicate(np.asarray(X[i], dtype=np.int64), pan=pan)
    rec = {"L": L, "bar": bars[L], "verdict_capable_node": capable[L],
           "stream_translit": S.gp.indices_to_translit(x),
           "n_decodes": int(len(pm)),
           "best": {"pmax": round(float(pm[i]), 4), "map": meta[i],
                    "preg": pan.registers[int(r["preg"][i])],
                    "decode_translit": S.gp.indices_to_translit(X[i]),
                    "en": round(full["en"], 4), "ioc": round(full["ioc"], 4),
                    "mds": int(full["mds"]), "h2": round(full["h2"], 4),
                    "zl": round(full["zl"], 4), "pmax_ne": round(full["pmax_ne"], 3),
                    "pcon": round(full["pcon"], 3),
                    "degenerate": bool(full["degenerate"])}}
    nc = 0
    for j in np.nonzero(pm >= bars[L])[0]:
        fj = A.adjudicate(np.asarray(X[int(j)], dtype=np.int64), pan=pan)
        if fj["pmax"] >= bars[L] and not fj["degenerate"]:
            nc += 1
            out["crossers"].append({"stream": name, "map": meta[int(j)],
                                    "pmax": round(float(fj["pmax"]), 4), "bar": bars[L],
                                    "decode_translit": S.gp.indices_to_translit(X[int(j)]),
                                    "FLAGGED_FOR_ORACLE": True})
    rec["n_crossers"] = nc
    if nc > 0:
        rec["verdict"] = "FLAGGED-FOR-ORACLE"
    elif capable[L] and not (name == "dotvals30"):
        rec["verdict"] = "negative (at measured power %.2f EN / %.2f LA)" % (
            pp["nodes"][str(L)]["EN"]["power"], pp["nodes"][str(L)]["LA"]["power"])
    else:
        why = ("2-symbol alphabet: degenerate by construction" if name == "dotvals30"
               else "EN power %.2f < floor %.1f" % (pp["nodes"][str(L)]["EN"]["power"],
                                                    S.POWER_FLOOR))
        rec["verdict"] = "measured-only (" + why + ")"
    out["streams"][name] = rec
    out["n_total"] += int(len(pm))
    print(name, rec["verdict"], "best", rec["best"]["pmax"], "vs bar", bars[L], flush=True)

out["n_budget"] = S.N_BUDGET
assert out["n_total"] <= S.N_BUDGET
json.dump(out, open("results.json", "w"), indent=1)
print("TOTAL", out["n_total"], "crossers", len(out["crossers"]))
