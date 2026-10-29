import json, os, math, numpy as np
H = os.path.dirname(os.path.abspath(__file__)); M = 14.0128
def wil(k, n, z=1.96):
    if n == 0: return [None, None]
    p = k/n; d = 1+z*z/n; c = p+z*z/(2*n); r = z*math.sqrt(p*(1-p)/n+z*z/(4*n*n)); return [round((c-r)/d,3), round((c+r)/d,3)]
out = {"key": "CICADA-X1R33", "m_NV_frozen": M, "gate": "accept iff pmax-bar >= m_NV for EN_NOVOWEL-argmax decodes, >=0 otherwise"}
for L in (240, 120):
    W = {p: json.load(open(f"{H}/feat_x1_{p}_{L}.json")) for p in ("nv", "en", "sp")}
    bar = W["nv"]["bar"]
    mg = lambda c: c["feat"]["pmax"]-bar
    nv = lambda c: c["feat"]["preg_name"] == "EN_NOVOWEL"
    acc = lambda c: mg(c) >= (M if nv(c) else 0.0)
    pick = lambda p, l: [c for c in W[p]["cases"] if c["label"] == l]
    Hh, Rn, G, S = pick("nv","halluc"), pick("nv","genuine"), pick("en","genuine"), pick("sp","genuine")
    rej = lambda cs: [sum(1 for c in cs if not acc(c)), len(cs)]
    ca, fe, fn, fs = rej(Hh), rej(G), rej(Rn), rej(S)
    fp = [fn[0]+fs[0], fn[1]+fs[1]]
    dist = lambda cs: ({"n": len(cs), "min": round(min(map(mg,cs)),2), "median": round(float(np.median(list(map(mg,cs)))),2), "max": round(max(map(mg,cs)),2)} if cs else {"n": 0})
    out[f"L{L}"] = {"bar": bar, "draws": {p: W[p]["n_draws"] for p in W},
      "catch_[caught=rejected_halluc]": [ca[1]-0 and ca[0], ca[1]], "catch_rate": round(ca[0]/ca[1],3) if ca[1] else None, "catch_wilson": wil(ca[0], ca[1]),
      "FR_EN_MODERN": fe, "FR_NOVOWEL_genuine": fn, "FR_NV_wilson": wil(*fn), "FR_spread_genuine": fs, "FR_pooled_register_spread": fp, "FR_pooled_wilson": wil(*fp),
      "margin_halluc": dist(Hh), "margin_NV_genuine": dist(Rn),
      "meets_catch>=0.90_and_FRpooled<=0.10_point": bool(ca[1] and ca[0]/ca[1] >= .90 and fe[0]/max(fe[1],1) <= .10 and fp[0]/max(fp[1],1) <= .10)}
out["SEAL_PASS"] = False; out["note"] = "replication only; SEAL_PASS stays false by instruction"
json.dump(out, open(f"{H}/d5c_replication.json", "w"), indent=1); print(json.dumps(out, indent=1))
