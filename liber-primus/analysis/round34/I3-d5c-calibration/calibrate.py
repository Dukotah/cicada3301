"""calibrate.py -- I3 m_NV(L) calibration per PREREG.md. Reads feat_<key>_<L>.json from ext.py. Writes m_nv_curve.json."""
import json, math, os, numpy as np
H = os.path.dirname(os.path.abspath(__file__))
LS = [120, 180, 240, 400]; TUNE = "CICADA-X1R33"; HELD = ["CICADA-I4b", "CICADA-I4c", "CICADA-R34I3"]
beta = lambda L: 0.07194 * (L / 120) ** -0.5463
def wil(k, n, z=1.96):
    if n == 0: return [None, None]
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); r = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return [round((c - r) / d, 3), round((c + r) / d, 3)]
def load(key, L):
    d = json.load(open(f"{H}/feat_{key}_{L}.json")); bar = d["bar"]; S = {"H": [], "EN": [], "NV": [], "SP": []}
    for c in d["cases"]:
        mg = c["pmax"] - bar; nv = c["preg_name"] == "EN_NOVOWEL"
        if c["pop"] == "nv" and c["label"] == "halluc": S["H"].append((mg, nv))
        elif c["pop"] == "nv" and c["label"] == "genuine": S["NV"].append((mg, nv))
        elif c["pop"] == "en" and c["label"] == "genuine": S["EN"].append((mg, nv))
        elif c["pop"] == "sp" and c["label"] == "genuine": S["SP"].append((mg, nv))
    return S
def pool(keys, L):
    out = {"H": [], "EN": [], "NV": [], "SP": []}
    for k in keys:
        for n, v in load(k, L).items(): out[n] += v
    return out
rej = lambda cs, m: sum(1 for mg, nv in cs if mg < (m if nv else 0.0))
def fit(sets):
    """sets: list of S dicts (one per L, thresholds t_i = scale_i*m). Returns m (midpoint of tied optimum s.t. tuning NV-genuine FR<=0.05)."""
    pts = sorted({mg / sc for S, sc in sets for n in ("H", "NV") for mg, nv in S[n] if nv})
    cands = [pts[0] - 1e-6] + [(a + b) / 2 for a, b in zip(pts, pts[1:])] + [pts[-1] + 1e-6]
    ok = []
    for m in cands:
        g = sum(rej(S["NV"], m * sc) for S, sc in sets); gn = sum(len(S["NV"]) for S, sc in sets)
        if g / gn <= 0.05:
            h = sum(rej(S["H"], m * sc) for S, sc in sets); hn = sum(len(S["H"]) for S, sc in sets)
            ok.append((h / hn, m))
    top = max(o[0] for o in ok); tied = [m for c, m in ok if abs(c - top) < 1e-12]
    return float((min(tied) + max(tied)) / 2), top, [min(tied), max(tied)]
def score(S, thr):
    R = lambda n: [rej(S[n], thr), len(S[n])]
    ca = R("H"); en = R("EN"); nv = R("NV"); sp = R("SP"); po = [nv[0] + sp[0], nv[1] + sp[1]]
    rate = lambda a: round(a[0] / a[1], 3) if a[1] else None
    r = {"thr": round(thr, 4), "catch": [ca[0], ca[1], rate(ca)], "catch_w": wil(*ca), "FR_EN": [en[0], en[1], rate(en)], "FR_EN_w": wil(*en),
         "FR_pooled": [po[0], po[1], rate(po)], "FR_pooled_w": wil(*po), "FR_NV": [nv[0], nv[1], rate(nv)], "FR_NV_w": wil(*nv),
         "FR_spread": [sp[0], sp[1], rate(sp)]}
    r["underpowered_NV"] = nv[1] < 37
    r["PASS"] = bool(ca[1] and ca[0] / ca[1] >= .9 and en[0] / max(en[1], 1) <= .1 and po[0] / max(po[1], 1) <= .1
                     and nv[1] and r["FR_NV_w"][1] <= .10)
    return r
def ceiling(S):
    """optimistic held-out-oracle bound: best catch over m with NV Wilson upper<=0.10 and pooled FR<=0.10 and EN FR<=0.10."""
    best = None
    for m in sorted({mg for n in ("H", "NV") for mg, nv in S[n] if nv}) + [1e9]:
        r = score(S, m)
        if r["FR_NV"][1] and r["FR_NV_w"][1] <= .10 and r["FR_pooled"][2] <= .10 and r["FR_EN"][2] <= .10:
            if best is None or r["catch"][2] > best[0]: best = (r["catch"][2], round(m, 3))
    return best
def main():
    T = {L: load(TUNE, L) for L in LS}; Hd = {L: pool(HELD, L) for L in LS}
    out = {"tune_key": TUNE, "held_keys": HELD, "recipes": {}, "sizes": {}}
    for L in LS: out["sizes"][L] = {"tune": {k: len(v) for k, v in T[L].items()}, "held": {k: len(v) for k, v in Hd[L].items()}}
    r1 = {}; allpass = True
    for L in LS:
        m, top, iv = fit([(T[L], 1.0)])
        r1[L] = {"m_NV": m, "tied_interval": iv, "tune_catch": top, "tune": score(T[L], m), "held": score(Hd[L], m)}
    c, top, iv = fit([(T[L], beta(L)) for L in LS])
    r2 = {"c": c, "tied_interval": iv, "pooled_tune_catch": top, "per_L": {}}
    for L in LS:
        r2["per_L"][L] = {"beta": beta(L), "m_NV_eff": c * beta(L), "tune": score(T[L], c * beta(L)), "held": score(Hd[L], c * beta(L))}
    out["recipes"]["R1_per_L_fit"] = r1; out["recipes"]["R2_beta_normalised"] = r2
    out["ceiling_heldout_oracle_m"] = {L: ceiling(Hd[L]) for L in LS}
    # diagnostic: per-key (not verdict)
    out["per_key_R1"] = {L: {k: score(load(k, L), r1[L]["m_NV"]) for k in HELD} for L in LS}
    out["m_NV_all_keys_diag"] = {L: {k: fit([(load(k, L), 1.0)])[0] for k in [TUNE] + HELD} for L in LS}
    out["pass_R1"] = {L: r1[L]["held"]["PASS"] for L in LS}; out["pass_R2"] = {L: r2["per_L"][L]["held"]["PASS"] for L in LS}
    out["R1_all_L"] = all(out["pass_R1"].values()); out["R2_all_L"] = all(out["pass_R2"].values())
    out["SEAL_PASS"] = False
    json.dump(out, open(f"{H}/m_nv_curve.json", "w"), indent=1, default=float)
    for nm, rr in (("R1", {L: r1[L]["held"] for L in LS}), ("R2", {L: r2["per_L"][L]["held"] for L in LS})):
        for L in LS:
            h = rr[L]; print(nm, L, "thr", h["thr"], "catch", h["catch"], h["catch_w"], "FR_EN", h["FR_EN"][:3], "FR_pool", h["FR_pooled"], "FR_NV", h["FR_NV"], h["FR_NV_w"], "PASS", h["PASS"])
    print("m_NV", {L: round(r1[L]["m_NV"], 3) for L in LS}, "c", c); print("ceiling", out["ceiling_heldout_oracle_m"]); print("diag m", out["m_NV_all_keys_diag"])
main()
