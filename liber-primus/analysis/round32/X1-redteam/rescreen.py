"""X1 re-screen of ONE seed under pair (keyskip2) and exact (keyskip1), with the round32/I2 nine-register panel,
round19/I1 driftbeam, round20 hitfn20 gate. Usage: rescreen.py <py27mt|bash4.2|bash4.2_i32> <seed> <out.json>
Pattern copied from round32/B1-bash-random/sweep.py (screen/stage2). Single seed, tiny RAM."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
I2DIR = os.path.join(LP, "analysis", "round32", "I2-multiregister-readjudication")
for p in ("analysis/round19/G1", "analysis/round19/G3", "analysis/round20/S-G3", "analysis/round19/I1", "analysis/round20/P3", "analysis/round20/HITFN",
          "analysis/round11", "analysis/campaign18_skip", "src"):
    sys.path.insert(0, os.path.join(LP, p))
sys.path.insert(0, I2DIR)
import adjudicate as AD
assert os.path.dirname(os.path.abspath(AD.__file__)) == os.path.abspath(I2DIR)
import driftbeam as DB, hitfn20 as H, lib_numchannel as nc
assert H.AD is AD
gen, seed, outp = sys.argv[1], int(sys.argv[2]), sys.argv[3]
U = list(nc.unsolved()); C_S, C_H = U[:120], U[:240]
if gen == "py27mt":
    import gen_py27 as G
    def ks(n):
        r = G.MT19937(); r.init_by_array([seed] if seed else [0]); return G.REDUCERS["random29"](r, n)
else:
    import gen_bash as GB
    def ks(n): return [r % 29 for r in GB.raws(seed, n, gen)]
res = {"generator": gen, "seed": seed, "panel": "round32/I2 models/panel.npz", "N_adjudicated": 10**6, "relations": {}}
for rel, pre in (("keyskip2", "pair"), ("keyskip1", "exact")):
    K = ks(240 * 4 + 64 if gen != "py27mt" else 240 * 6 + 64)
    d = DB.beam_decode(C_S, K, sign=-1, o=0, beam_w=64, **DB.PRESETS[pre])
    a = AD.adjudicate(d["plain_idx"], translit=d.get("translit"))
    r = {"preset": pre, "screen_pmax": float(a["pmax"]), "screen_pmax_repr": repr(float(a["pmax"])),
         "screen_register": AD.panel().registers[a["preg"]], "beam_score": float(d["score"]), "n_skips": d["n_skips"]}
    v = H.evaluate(H.HitDecode(C=C_H, K=K, o=0, preset=pre, n_round_adjudicated=10**6))
    r["L240_gate"] = {"hit": bool(v.hit), "reason": v.reason, "stage_b_pmax": float(v.pmax), "bar": float(v.bar),
                      "recovery": float(v.recovery), "heldout": float(v.heldout_recovery)}
    res["relations"][rel] = r
json.dump(res, open(outp, "w"), indent=1); print(json.dumps(res, indent=1))
