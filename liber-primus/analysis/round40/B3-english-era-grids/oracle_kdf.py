#!/usr/bin/env python3
"""R40-B3: evidence bundle for the one flagged row (KDF rev iter_md5_1000, secret 03000000, salt self, mod29, atbash 0, sign +1, keyskip2)."""
import sys, os, json, math
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as E, grids as G
import skipdecode as _sk
E.G = type('x', (), {'sk': _sk})
import numpy as np
keep = json.load(open(E.F("keep_KDF.json")))
row = [r for r in keep if r["rel"] == "keyskip2" and r["pmax"] >= 6.5][0]
m = row["meta"]; g = G.KdfGrid()
Kf = g.keyfull(m)
out = {"kid": row["kid"], "meta": m, "reproduce": "python -c \"import engine,grids; g=grids.KdfGrid(); K=g.keyfull(%r)\" (cwd = analysis/round40/B3-english-era-grids)" % (m,),
       "buffer_len": len(Kf), "decodes": {}}
for L in (120, 150, 170, 183):
    Lc = min(L, len(Kf) - 10)
    C, Ke = E.apply_variant(U := E.U[:Lc], Kf, m["atb"], m["sg"])
    for rel in E.RELS:
        d, a = E.v3dec(C, Ke, rel)
        out["decodes"]["L%d|%s" % (Lc, rel)] = {"pmax": round(float(a["pmax"]), 3), "preg": E.PAN.registers[a["preg"]], "ioc": round(float(a["ioc"]), 4), "mds": int(a["mds"]),
                                                "pmax_ne": round(float(a["pmax_ne"]), 3), "zl": round(float(a["zl"]), 3), "z": [round(float(v), 2) for v in a["z"]], "degenerate": bool(a.get("degenerate", False)),
                                                "plain_idx": d["plain_idx"], "translit": E.G.sk.idx_to_trans(d["plain_idx"]) if hasattr(E.G, "sk") else ""}
# same secret/kdf/salt/red in the other variants and the fwd twin
twin = dict(m); twin["dir"] = "fwd"
Kt = g.keyfull(twin); C, Ke = E.apply_variant(E.U[:120], Kt, m["atb"], m["sg"]); d, a = E.v3dec(C, Ke, "keyskip2"); out["fwd_twin_L120_keyskip2_pmax"] = round(float(a["pmax"]), 3)
# exceedance probability under the fitted POT null at this N
cell = E.S.NULL12["L120|keyskip2"]; N = json.load(open(E.F("final_KDF.json")))["rels"]["keyskip2"]["N_actual"]
x = row["pmax"]; out["null12_cell"] = {"mu": cell["mu"], "beta": cell["beta"]}; out["N_decodes"] = N
t = math.exp(-(x - cell["mu"]) / cell["beta"])   # per-draw exceedance probability implied by bar(N)=mu+beta*ln(N/-ln0.99)
out["P_max_ge_x_under_fit"] = 1 - math.exp(-N * t)
out["tests_run_in_lane_for_family_wise"] = {"grids": 4, "relations": 2, "tests": 8, "expected_crossers_at_p_each": 0.01}
json.dump(out, open(os.path.join(E.HERE, "ORACLE-KDF-iter_md5_1000-rev", "bundle.json"), "w"), indent=1)
print(json.dumps({k: (v if k != "decodes" else {kk: (vv["pmax"], vv["preg"], vv["translit"][:80]) for kk, vv in v.items()}) for k, v in out.items()}, indent=1))
