"""analyze_d5c.py -- D5c per-register pmax-margin gate (PREREG ADDENDUM B). m_NV is frozen on ALL data seen
before virgin-2 (tuning + seen held-out + virgin-1), then scored ONCE on virgin-2. Writes catch_surface_d5c.json."""
import json
import os

import numpy as np

import analyze as A
import analyze_d5 as D5

HERE = A.HERE
BAR = A.D["tune_nv"]["bar"]
NV = "EN_NOVOWEL"


def lv(n):
    return json.load(open(os.path.join(HERE, f"feat_{n}.json")))


W = {n: lv(n) for n in ("virg2_nv", "virg2_en", "virg2_sp")}


def pick(pop, label):
    return [c for c in W[pop]["cases"] if c["label"] == label]


V2 = {"H": pick("virg2_nv", "halluc"), "G": pick("virg2_en", "genuine"),
      "R_nv": pick("virg2_nv", "genuine"), "R_sp": pick("virg2_sp", "genuine")}
V2["R"] = V2["R_nv"] + V2["R_sp"]
marg = D5.marg


def isnv(c):
    return c["feat"]["preg_name"] == NV


def rate(acc, cases):
    rej = sum(1 for c in cases if not acc(c))
    return [rej, len(cases), round(rej / len(cases), 3) if cases else None]


def main():
    # ---- freeze m_NV on everything seen before virgin-2
    Hs = [c for c in (A.SETS["H_t"] + A.SETS["H_h"] + D5.VS["H"]) if isnv(c)]
    Gs = [c for c in (A.SETS["R_t"] + A.SETS["R_nv_h"] + D5.VS["R_nv"]) if isnv(c)]
    hm = sorted(marg(c) for c in Hs)
    gm = sorted(marg(c) for c in Gs)
    pts = sorted(set(hm + gm))
    cands = [pts[0] - 1e-6] + [(a + b) / 2 for a, b in zip(pts, pts[1:])] + [pts[-1] + 1e-6]
    ok = []
    for m in cands:
        fr = np.mean([x < m for x in gm])
        if fr <= 0.05:
            ok.append((float(np.mean([x < m for x in hm])), m))
    top = max(o[0] for o in ok)
    tied = [m for c, m in ok if abs(c - top) < 1e-12]
    m_nv = float((min(tied) + max(tied)) / 2)
    out = {"m_NV": m_nv, "m_NV_tied_interval": [min(tied), max(tied)], "fit_catch": top,
           "fit_sizes": {"halluc": len(Hs), "novowel_genuine": len(Gs)},
           "virgin2_sizes": {k: len(v) for k, v in V2.items()},
           "virgin2_draws": {n: W[n]["n_draws"] for n in W},
           "virgin2_labels": {n: {f"{s}/{l}": sum(1 for c in W[n]["cases"] if c["stream"] == s and c["label"] == l)
                                  for s in {c["stream"] for c in W[n]["cases"]} for l in ("halluc", "genuine", "gray")}
                              for n in W}}

    def d5c(c, m=m_nv):
        return marg(c) >= (m if isnv(c) else 0.0)

    d5a = lambda c: marg(c) >= 14.758052134222897      # frozen on tuning (Addendum A); second look
    fold5 = D5.k5
    gates = {"D5c_perreg_margin": d5c, "D5a_global_margin(frozen m*=14.758)": d5a,
             "CTRL_fold5_min0.90": fold5,
             "D5c_AND_fold5": lambda c: d5c(c) and fold5(c)}
    for nm, acc in gates.items():
        v = {"catch": rate(acc, V2["H"]), "fr_EN": rate(acc, V2["G"]), "fr_reg_pooled": rate(acc, V2["R"]),
             "fr_reg_novowel": rate(acc, V2["R_nv"]), "fr_reg_spread": rate(acc, V2["R_sp"])}
        for st in ("LATIN", "DE", "OE", "EN_KJV"):
            v[f"fr_{st}"] = rate(acc, [c for c in V2["R_sp"] if c["stream"] == st])
        W_ = A.wilson
        v["wilson95"] = {"catch": W_(v["catch"][0] if False else v["catch"][1] - v["catch"][0], v["catch"][1]) if False else
                         W_(v["catch"][0], v["catch"][1]),
                         "fr_EN": W_(v["fr_EN"][0], v["fr_EN"][1]),
                         "fr_reg_pooled": W_(v["fr_reg_pooled"][0], v["fr_reg_pooled"][1]),
                         "fr_reg_novowel": W_(v["fr_reg_novowel"][0], v["fr_reg_novowel"][1])}
        v["PASS"] = bool(v["catch"][2] >= 0.90 and v["fr_EN"][2] <= 0.10 and v["fr_reg_pooled"][2] <= 0.10)
        v["PASS_point_and_wilson_upper_le_0.10"] = bool(v["PASS"] and v["wilson95"]["fr_reg_pooled"][1] <= 0.10
                                                        and v["wilson95"]["fr_EN"][1] <= 0.10)
        out[nm] = v
    # ROC on virgin-2 over m_NV
    roc = []
    for m in [10, 11, 12, 13, 13.5, 14, 14.5, 15, 15.5, 16, 17, 18]:
        a = lambda c, m=m: marg(c) >= (m if isnv(c) else 0.0)
        roc.append({"m_NV": m, "catch": rate(a, V2["H"])[2], "fr_EN": rate(a, V2["G"])[2],
                    "fr_NV_genuine": rate(a, V2["R_nv"])[2], "fr_reg_pooled": rate(a, V2["R"])[2]})
    out["roc_virgin2"] = roc
    x = np.array([marg(c) for c in V2["H"]])
    y = np.array([marg(c) for c in V2["R_nv"]])
    out["margin_dists_virgin2"] = {
        "halluc": {"n": len(x), "p50": round(float(np.median(x)), 2), "p99": round(float(np.quantile(x, .99)), 2),
                   "max": round(float(x.max()), 2), "n_above_14": int((x >= 14).sum())},
        "novowel_genuine": {"n": len(y), "min": round(float(y.min()), 2), "p10": round(float(np.quantile(y, .1)), 2),
                            "median": round(float(np.median(y)), 2)}}
    # preg of hallucinations / genuine (for the register-conditional scope statement)
    from collections import Counter
    out["preg_counts_virgin2"] = {"halluc": dict(Counter(c["feat"]["preg_name"] for c in V2["H"])),
                                  "spread_genuine": dict(Counter(c["feat"]["preg_name"] for c in V2["R_sp"])),
                                  "novowel_genuine": dict(Counter(c["feat"]["preg_name"] for c in V2["R_nv"]))}
    json.dump(out, open(os.path.join(HERE, "catch_surface_d5c.json"), "w"), indent=1, default=float)
    print("m_NV", m_nv, out["m_NV_tied_interval"], "fit catch", top, out["fit_sizes"])
    print(out["virgin2_sizes"], out["virgin2_labels"])
    for nm in gates:
        print(nm, json.dumps(out[nm]))
    print(json.dumps(out["roc_virgin2"]))
    print(json.dumps(out["margin_dists_virgin2"]), json.dumps(out["preg_counts_virgin2"]))


if __name__ == "__main__":
    main()
