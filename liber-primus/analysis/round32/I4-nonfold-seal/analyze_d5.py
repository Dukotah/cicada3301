"""analyze_d5.py -- D5 pmax-margin gate (PREREG ADDENDUM A). m is frozen on the tuning split, then
scored on the seen held-out split (contaminated) and the VIRGIN split (decisive). Writes catch_surface_d5.json."""
import json
import os

import numpy as np

import analyze as A

HERE = A.HERE
BAR = A.D["tune_nv"]["bar"]


def loadv(n):
    return json.load(open(os.path.join(HERE, f"feat_{n}.json")))


V = {n: loadv(n) for n in ("virg_nv", "virg_en", "virg_sp")}


def pick(pop, label):
    return [c for c in V[pop]["cases"] if c["label"] == label]


VS = {"H": pick("virg_nv", "halluc"), "G": pick("virg_en", "genuine"),
      "R_nv": pick("virg_nv", "genuine"), "R_sp": pick("virg_sp", "genuine")}
VS["R"] = VS["R_nv"] + VS["R_sp"]


def marg(c):
    return c["feat"]["pmax"] - BAR


def k5(c):
    return A.fold_stat(c, 5, "min") >= 0.90


def rate(acc, cases):
    rej = sum(1 for c in cases if not acc(c))
    return rej, len(cases), round(rej / len(cases), 3) if cases else None


def summarise(acc):
    t = {"catch": rate(acc, A.SETS["H_t"]), "fr_EN": rate(acc, A.SETS["G_t"]), "fr_reg": rate(acc, A.SETS["R_t"])}
    h = {"catch": rate(acc, A.SETS["H_h"]), "fr_EN": rate(acc, A.SETS["G_h"]), "fr_reg": rate(acc, A.SETS["R_h"])}
    v = {"catch": rate(acc, VS["H"]), "fr_EN": rate(acc, VS["G"]), "fr_reg": rate(acc, VS["R"]),
         "fr_reg_novowel": rate(acc, VS["R_nv"]), "fr_reg_spread": rate(acc, VS["R_sp"])}
    return {"tuning": t, "seen_heldout": h, "virgin": v}


def wil(t):
    return A.wilson(t[0], t[1])


def main():
    # ---- tune m on tuning only: max catch s.t. FR over G_t U R_t <= 0.10 ; ties -> midpoint of tied interval
    Ht = [marg(c) for c in A.SETS["H_t"]]
    Gt = [marg(c) for c in A.SETS["G_t"] + A.SETS["R_t"]]
    pts = sorted(set(Ht + Gt))
    cands = [pts[0] - 1e-6] + [(a + b) / 2 for a, b in zip(pts, pts[1:])] + [pts[-1] + 1e-6]
    best = []
    for m in cands:
        catch = np.mean([x < m for x in Ht])
        fr = np.mean([x < m for x in Gt])
        if fr <= 0.10:
            best.append((catch, m))
    top = max(b[0] for b in best)
    tied = [m for c, m in best if abs(c - top) < 1e-12]
    m_star = float((min(tied) + max(tied)) / 2)
    out = {"bar": BAR, "m_star": m_star, "m_tied_interval": [min(tied), max(tied)],
           "tuning_catch_at_m": float(top),
           "virgin_sizes": {k: len(v) for k, v in VS.items()},
           "virgin_draws": {n: V[n]["n_draws"] for n in V},
           "virgin_labels": {n: {f"{s}/{l}": sum(1 for c in V[n]["cases"] if c["stream"] == s and c["label"] == l)
                                 for s in {c["stream"] for c in V[n]["cases"]}
                                 for l in ("halluc", "genuine", "gray")} for n in V}}
    d5a = lambda c, m=m_star: marg(c) >= m
    d5b = lambda c, m=m_star: marg(c) >= m and k5(c)
    out["D5a_pmargin"] = summarise(d5a)
    out["D5b_pmargin_AND_fold5"] = summarise(d5b)
    out["CTRL_fold5_min0.90"] = summarise(k5)
    # margin distributions (virgin + seen), per stream/label
    dist = {}
    for nm, cases in (("seen_halluc", A.SETS["H_t"] + A.SETS["H_h"]), ("virgin_halluc", VS["H"]),
                      ("seen_novowel_genuine", A.SETS["R_t"] + A.SETS["R_nv_h"]), ("virgin_novowel_genuine", VS["R_nv"]),
                      ("seen_EN_genuine", A.SETS["G_t"] + A.SETS["G_h"]), ("virgin_EN_genuine", VS["G"]),
                      ("seen_spread_genuine", A.SETS["R_sp_h"]), ("virgin_spread_genuine", VS["R_sp"])):
        x = np.array([marg(c) for c in cases])
        dist[nm] = {"n": len(x), "min": round(float(x.min()), 2), "p10": round(float(np.quantile(x, .1)), 2),
                    "median": round(float(np.median(x)), 2), "p90": round(float(np.quantile(x, .9)), 2),
                    "max": round(float(x.max()), 2)}
    for st in ("LATIN", "DE", "OE", "EN_KJV"):
        x = np.array([marg(c) for c in VS["R_sp"] if c["stream"] == st])
        if len(x):
            dist[f"virgin_{st}_genuine"] = {"n": len(x), "min": round(float(x.min()), 2),
                                            "median": round(float(np.median(x)), 2)}
    out["pmax_minus_bar_distributions"] = dist
    # ROC on virgin over m grid (for the table; m_star is the only frozen operating point)
    roc = []
    for m in [0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30, 40]:
        a = lambda c, m=m: marg(c) >= m
        roc.append({"m": m, "virgin_catch": rate(a, VS["H"])[2], "virgin_fr_EN": rate(a, VS["G"])[2],
                    "virgin_fr_reg": rate(a, VS["R"])[2], "seen_catch": rate(a, A.SETS["H_t"] + A.SETS["H_h"])[2],
                    "seen_fr_EN": rate(a, A.SETS["G_t"] + A.SETS["G_h"])[2],
                    "seen_fr_reg": rate(a, A.SETS["R_t"] + A.SETS["R_h"])[2]})
    out["roc_virgin_vs_seen_pooled"] = roc
    # verdict on virgin only
    for nm in ("D5a_pmargin", "D5b_pmargin_AND_fold5"):
        v = out[nm]["virgin"]
        cr = 1 - v["catch"][2] if False else v["catch"][2]
        out[nm]["virgin_verdict"] = {
            "catch": v["catch"][2], "catch_wilson95": wil(v["catch"]),
            "fr_EN": v["fr_EN"][2], "fr_EN_wilson95": wil(v["fr_EN"]),
            "fr_reg_pooled": v["fr_reg"][2], "fr_reg_wilson95": wil(v["fr_reg"]),
            "PASS": bool(v["catch"][2] >= 0.90 and v["fr_EN"][2] <= 0.10 and v["fr_reg"][2] <= 0.10),
            "PASS_lower_bounds_ok": bool(wil(v["catch"])[0] >= 0.80)}
    json.dump(out, open(os.path.join(HERE, "catch_surface_d5.json"), "w"), indent=1, default=float)
    print("m*", m_star, "tied", out["m_tied_interval"], "tuning catch", top)
    for k in ("D5a_pmargin", "D5b_pmargin_AND_fold5", "CTRL_fold5_min0.90"):
        print(k, json.dumps(out[k]["tuning"]), "\n   seen", json.dumps(out[k]["seen_heldout"]), "\n   virgin", json.dumps(out[k]["virgin"]))
        if "virgin_verdict" in out[k]:
            print("   VERDICT", out[k]["virgin_verdict"])
    print(json.dumps(dist, indent=0))
    print(json.dumps(roc))
    print(out["virgin_sizes"], out["virgin_labels"])


if __name__ == "__main__":
    main()
