"""calibrate.py -- scores the frozen rule m(L)=0.055*L per PREREG.md. Reads feat/*.json from gen.py. Writes results.json, ledger.json."""
import json, math, os, glob
H = os.path.dirname(os.path.abspath(__file__))
LS = [150, 300, 400]; KEYS = ["CICADA-R35I3a", "CICADA-R35I3b"]; C = 0.055
SPREAD = ["LATIN", "DE", "OE", "EN_KJV"]
def wil(k, n, z=1.96):
    if n == 0: return [None, None]
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); r = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return [round((c - r) / d, 3), round((c + r) / d, 3)]
def cases(L, stream):
    out = []; draws = 0
    for k in KEYS:
        d = json.load(open(f"{H}/feat/{k}_{L}_{stream}.json")); draws += d["draws"]
        for c in d["cases"]: out.append((c["pmax"] - d["bar"], c["preg_name"], c["label"]))
    return out, draws
def rej(mg, reg, m, hv_zero=False):
    if reg == "EN_NOVOWEL" or (reg == "EN_HALFVOWEL" and not hv_zero): return mg < m
    return mg < 0.0
def cell(k, n):
    return {"n": n, "k": k, "rate": round(k / n, 4) if n else None, "wilson95": wil(k, n)}
res = {"rule": "m(L)=0.055*L on EN_NOVOWEL and EN_HALFVOWEL argmax; 0 otherwise", "per_L": {}}
allpass = True
for L in LS:
    m = C * L; nv, dnv = cases(L, "EN_NOVOWEL"); hv, dhv = cases(L, "EN_HALFVOWEL")
    sp = [x for s in SPREAD for x in cases(L, s)[0]]
    hNV = [x for x in nv if x[2] == "halluc" and x[1] == "EN_NOVOWEL"]
    hHV = [x for x in nv + hv if x[2] == "halluc" and x[1] == "EN_HALFVOWEL"]
    gNV = [x for x in nv if x[2] == "genuine" and x[1] == "EN_NOVOWEL"]
    gHV = [x for x in hv if x[2] == "genuine" and x[1] == "EN_HALFVOWEL"]
    gSP = [x for x in sp if x[2] == "genuine"]
    gP = [x for x in nv + hv if x[2] == "genuine"] + gSP
    catch = lambda S, z=False: cell(sum(1 for mg, r, _ in S if rej(mg, r, m, z)), len(S))
    fr = lambda S: cell(sum(1 for mg, r, _ in S if rej(mg, r, m)), len(S))
    r = {"m": m, "draws": {"EN_NOVOWEL": dnv, "EN_HALFVOWEL": dhv},
         "catch_H_NV": catch(hNV), "catch_H_HV": catch(hHV), "catch_H_pooled": catch(hNV + hHV),
         "diag_catch_H_HV_if_margin0": catch(hHV, True),
         "FR_NV_only": fr(gNV), "FR_HV_only": fr(gHV), "FR_spreadonly_other": fr(gSP), "FR_pooled": fr(gP),
         "n_gray_excluded": sum(1 for x in nv + hv if x[2] == "gray")}
    cl = {}
    cl["catch_NV>=.90"] = r["catch_H_NV"]["n"] > 0 and r["catch_H_NV"]["rate"] >= .90
    cl["catch_HV>=.90"] = r["catch_H_HV"]["n"] > 0 and r["catch_H_HV"]["rate"] >= .90
    cl["FR_pooled<=.10"] = r["FR_pooled"]["rate"] <= .10
    cl["NV_wilson_upper<=.10"] = r["FR_NV_only"]["n"] > 0 and r["FR_NV_only"]["wilson95"][1] <= .10
    cl["HV_wilson_upper<=.10"] = r["FR_HV_only"]["n"] > 0 and r["FR_HV_only"]["wilson95"][1] <= .10
    r["clauses"] = cl; r["PASS"] = all(cl.values()); allpass &= r["PASS"]
    r["per_key_FR_NV_HV"] = {}
    res["per_L"][L] = r
res["all_L_pass"] = allpass; res["SEAL_PASS"] = False
res["SEAL_note"] = "SEAL_PASS stays false by lane rule; all_L_pass=True would only RECOMMEND coordinator review"
json.dump(res, open(f"{H}/results.json", "w"), indent=1)
json.dump({"lane": "R35-I3", "SEAL_PASS": False, "all_L_pass": allpass, "recommend_adopt": allpass,
           "pass_by_L": {str(L): res["per_L"][L]["PASS"] for L in LS},
           "not_covered": ["wrong-key overfits", "non-exact relations (skip_by_two etc.)", "L other than 150/300/400",
                           "real (non-planted) pages", "Welsh/CY register", "only 2 keys (seeds of the two keys overlap at 7-rep offset)",
                           "H-HV class sourced only from NV-stream plants (HALFVOWEL stream yields ~0 hallucinations)"]},
          open(f"{H}/ledger.json", "w"), indent=1)
for L in LS:
    r = res["per_L"][L]
    print(L, r["m"], "PASS", r["PASS"], {k: (v["k"], v["n"], v["rate"], v["wilson95"]) for k, v in r.items() if isinstance(v, dict) and "k" in v})
    print("   clauses", r["clauses"])
