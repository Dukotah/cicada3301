"""I1 R40: re-plant R37-C3 controls (beam: N1ct,N4ks,N5,X3b,X4; direct Z test per family). python -I drv_c3.py beam|direct REG.."""
import os, sys, json, time, random
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); AN = os.path.abspath(os.path.join(HERE, "..", ".."))
D3 = os.path.join(AN, "round37", "C3-rescore-reopened"); sys.path.insert(0, D3)
import rescore as R
R.log = lambda *a: None          # keep the original lane directory untouched
import numpy as np
OUT = os.path.join(HERE, "results_raw.jsonl")
def emit(d): open(OUT, "a").write(json.dumps(d) + "\n")
def beam(regs):
    n5 = R.n5_mod(); n1c, FUNCS = R.n1_ct_cfgs()
    fam_keys = {"N1ct": [c[2] for c in n1c], "N4ks": [c[2] for c in R.n4_cfgs()], "N5": [c[2] for c in R.n5_cfgs(n5) if len(c[2]) > 5000][::31], "X3b": [R._key_english()],
                "X4": [[v % R.N for v in R.NC.v_totient(R.U)], [v % R.N for v in R.NC.v_prime(R.U)], [v % R.N for v in R.NC.v_prime_index(R.U)]]}
    b = {r: {"L120": R.bar12(1e6, 120, r), "L240": R.bar12(1e6, 240, r)} for r in R.RELS}
    for reg in regs:
        rng = random.Random(7001 + sum(map(ord, reg))); t0 = time.time()
        for fam, Ks in fam_keys.items():
            for rel in R.RELS:
                for j in range(5):
                    K = Ks[rng.randrange(len(Ks))]; s0 = rng.randrange(0, max(1, min(4000, len(K) - 1024))); Kw = K[s0:s0 + 1024]
                    C, P = R.plant_beam(reg, rel, Kw, rng)
                    d1, a1 = R.v3dec(C[:120], Kw, rel); d2, a2 = R.v3dec(C, Kw, rel); rec = float(R.B2.recovery(d2["plain_idx"], P))
                    e = {"grp": "R37-C3-beam-" + fam, "reg": reg, "cell": "%s|%d" % (rel, j), "pmax120": round(float(a1["pmax"]), 3), "pmax240": round(float(a2["pmax"]), 3), "recovery240": round(rec, 4),
                         "bar120_N1e6": round(b[rel]["L120"], 3), "bar240_N1e6": round(b[rel]["L240"], 3), "preg240": R.REGS[a2["preg"]]}
                    e["recover"] = bool(e["pmax120"] >= b[rel]["L120"] and e["pmax240"] >= b[rel]["L240"] and rec >= 0.9); emit(e)
        print(reg, "beam %.0fs" % (time.time() - t0), flush=True)
def direct(regs, nplant, D):
    s = json.load(open(os.path.join(D3, "rescore_summary.json")))["families"]
    fams = {k: v for k, v in s.items() if v.get("kind") == "direct" and isinstance(v.get("control"), dict) and "EN_MODERN" in v["control"]}
    for reg in regs:
        t0 = time.time()
        for fam, v in fams.items():
            c0 = v["control"]["EN_MODERN"]
            if "n" not in c0: continue          # structural control (R22C): handled by the beam X3b/X4 families
            n, q99 = c0["n"], v["null_max_Z_q99"]
            for sd in range(nplant):
                P = R.plant_stream(reg, n, 7 + sd); obs = R.pm_many({"p": P})["p"]
                a = np.array([R.pm_many({"p": np.random.RandomState(1000 + j).permutation(P)})["p"] for j in range(D)])
                Zp = float((obs - a.mean()) / (a.std(ddof=1) or 1e-9))
                emit({"grp": "R37-C3-direct-" + fam, "reg": reg, "cell": "seed%d" % (7 + sd), "n": n, "Z_plant": round(Zp, 2), "q99": round(q99, 3), "recover": bool(Zp > q99 + 1.0)})
            print(reg, fam, "%.0fs" % (time.time() - t0), flush=True)
if __name__ == "__main__":
    what = sys.argv[1]; regs = sys.argv[2:]
    for r_ in regs:
        g = R.free_gb(); print("free GB", g, flush=True)
    if what == "beam": beam(regs)
    else: direct(regs, int(os.environ.get("NP", "10")), int(os.environ.get("DN", "60")))
