"""R32/I2: re-score stored survivors of historical negatives through the rebuilt 9-register panel."""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "..", "round19", "I3"))
import adjudicate as AJ
import skipdecode as sk
from nullcurve19 import threshold_for
from collect import collect
NTRIALS = {"B-04": 6224300, "R16-KDF": 692064, "R16-PRNG": 52556, "R17-PUBLIC-PAD": 14522916046}
REG = "I19:vecbeam.keyskip1+I2"
pan = AJ.panel()
regs = pan.registers
out = {"panel": "rebuilt in round32/I2 (models/panel.npz)", "registers": regs, "bar_source": "round19/I3 calib19.json cells %s (nearest-L, 1/sqrt(L) rescaled, strict=False)" % REG, "lanes": {}}
for lane, rows in collect().items():
    res = []
    N = NTRIALS[lane]
    for r in rows:
        idx = sk.eng_to_idx(r["text"])
        a = AJ.adjudicate(idx, translit=r["text"], pan=pan)
        n = a["n"]
        bars = {}
        for stat in ("pmax_ne", "pcon"):
            bars[stat] = {"escalate": threshold_for(N, n, alpha=0.05, register=REG, statistic=stat, strict=False),
                          "claim": threshold_for(N, n, alpha=0.01, register=REG, statistic=stat, strict=False)}
        res.append({"src": r["src"], "path": r["path"], "legacy_score": r["legacy_score"], "n_runes": n,
                    "pmax_ne": a["pmax_ne"], "ne_reg": regs[a["ne_reg"]], "pcon": a["pcon"], "pcreg": regs[a["pcreg"]],
                    "pmax": a["pmax"], "preg": regs[a["preg"]], "en": a["en"], "z": dict(zip(regs, [round(float(v),3) for v in a["z"]])),
                    "bars": bars,
                    "flag_claim": bool(a["pmax_ne"] >= bars["pmax_ne"]["claim"] or a["pcon"] >= bars["pcon"]["claim"]),
                    "flag_escalate": bool(a["pmax_ne"] >= bars["pmax_ne"]["escalate"] or a["pcon"] >= bars["pcon"]["escalate"]),
                    "text": r["text"]})
    best_ne = max(res, key=lambda r: r["pmax_ne"]) if res else None
    best_pc = max(res, key=lambda r: r["pcon"]) if res else None
    out["lanes"][lane] = {"N_trials": N, "n_survivor_texts": len(res),
        "n_flag_claim": sum(r["flag_claim"] for r in res), "n_flag_escalate": sum(r["flag_escalate"] for r in res),
        "best_pmax_ne": best_ne and {k: best_ne[k] for k in ("pmax_ne","ne_reg","n_runes","src","legacy_score","text","bars")},
        "best_pcon": best_pc and {k: best_pc[k] for k in ("pcon","pcreg","n_runes","src","legacy_score","text","bars")},
        "best_per_register_z": {g: max((r["z"][g] for r in res)) for g in regs} if res else None,
        "median_pmax_ne": float(np.median([r["pmax_ne"] for r in res])) if res else None,
        "flagged": [r for r in res if r["flag_escalate"]][:25]}
    print(lane, len(res), "claim", out["lanes"][lane]["n_flag_claim"], "esc", out["lanes"][lane]["n_flag_escalate"],
          "best pmax_ne", best_ne and round(best_ne["pmax_ne"],2), "bar", best_ne and round(best_ne["bars"]["pmax_ne"]["claim"],2), flush=True)
json.dump(out, open(os.path.join(HERE, "readjudication_table.json"), "w"), indent=1)
