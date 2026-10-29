"""eval400.py -- ADDENDUM 1: L=400 held-out re-evaluation with enlarged NV sample, frozen threshold. Updates m_nv_curve.json."""
import json, os, io, contextlib, sys
H = os.path.dirname(os.path.abspath(__file__))
with contextlib.redirect_stdout(io.StringIO()):
    import calibrate as C
J = json.load(open(f"{H}/m_nv_curve.json")); thr = J["recipes"]["R1_per_L_fit"]["400"]["m_NV"]
S = C.pool(C.HELD, 400); per = {}
for k in C.HELD:
    d = json.load(open(f"{H}/feat_add_{k}_400.json")); bar = d["bar"]; n = 0
    for c in d["cases"]:
        mg = c["pmax"] - bar; nv = c["preg_name"] == "EN_NOVOWEL"
        if c["label"] == "halluc": S["H"].append((mg, nv))
        elif c["label"] == "genuine": S["NV"].append((mg, nv)); n += 1
    per[k] = {"added_draws": d["draws"]["nv"], "added_genuine": n}
r = C.score(S, thr)
pk = {}
for k in C.HELD:
    T = C.load(k, 400); d = json.load(open(f"{H}/feat_add_{k}_400.json")); bar = d["bar"]
    g = [(c["pmax"] - bar, c["preg_name"] == "EN_NOVOWEL") for c in d["cases"] if c["label"] == "genuine"] + T["NV"]
    pk[k] = [C.rej(g, thr), len(g)]
J["addendum1_L400"] = {"frozen_threshold": thr, "added": per, "held": r, "NV_rejects_per_key": pk}
J["pass_R1"]["400"] = r["PASS"]; J["R1_all_L"] = all(J["pass_R1"].values())
json.dump(J, open(f"{H}/m_nv_curve.json", "w"), indent=1, default=float)
print(json.dumps(J["addendum1_L400"], indent=1))
