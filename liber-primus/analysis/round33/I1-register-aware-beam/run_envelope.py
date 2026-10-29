"""Round 33 / I1 harness.  One process, incremental JSON, nothing outside this directory is written.

  python run_envelope.py ckpt                       # Q5 checkpoint: design 1, L=120, MODERN+NOVOWEL, 2 relations
  python run_envelope.py tune                       # tuning seeds 500..509 (PREREG s5)
  python run_envelope.py grid DESIGN L REGS [tau lam_u]   # matched-relation cells; DESIGN in base|panel_max|register_cond|agnostic
  python run_envelope.py null DESIGN L [tau lam_u]
  python run_envelope.py speed
"""
import os
import sys
import json
import time
import random

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np                      # noqa: E402
import beam_v3 as V                    # noqa: E402
import beam_v2 as B2                   # noqa: E402
import adjudicate as A                 # noqa: E402

PAN = V.panel()
TEST = np.load(os.path.join(V.R32, "I2-multiregister-readjudication", "models", "testhalves.npz"))
LITE = np.load(os.path.join(V.R32, "I1-skipbytwo-decoder", "models", "testhalves_lite.npz"))
REGS9 = list(PAN.registers)
PAIRS = [("keyskip1", 1), ("skip_by_two", 2), ("free_q05", "free")]
SUPP = 0.83


def plain(reg, L, s, src=TEST):
    a = src[reg].astype(np.int64)
    r = random.Random(9000 + s)
    st = r.randrange(0, len(a) - L - 1)
    return a[st:st + L].tolist()


def key(L):
    return B2.sha_ctr_key(L * 12 + 2048)


def adj(idx):
    r = A.adjudicate(idx, pan=PAN)
    d = {k: round(float(r[k]), 4) for k in ("en", "pmax", "pmax_ne", "pcon", "ioc")}
    d["preg"] = PAN.registers[r["preg"]]
    return d


def decode(design, C, K, adv, tau, lam_u):
    if design == "base":
        return B2.beam_decode_v2(C, K, adv)
    return V.beam_decode_v3(C, K, adv, design, tau=tau, lam_u=lam_u)


def run_cell(design, reg, enc, adv, L, seeds, tau=0.0, lam_u=4.0, null=None):
    K = key(L)
    rows = []
    t0 = time.time()
    tdec = 0.0
    for s in seeds:
        P = plain(reg, L, s)
        C, info = B2.ENCIPHER[enc](P, K, SUPP, 3301 + s)
        t1 = time.time()
        bd = decode(design, C, K, adv, tau, lam_u)
        tdec += time.time() - t1
        rec = B2.recovery(bd["plain_idx"], P)
        a = adj(bd["plain_idx"])
        row = {"seed": s, "recovery": round(rec, 4), **info, **a}
        if design == "register_cond":
            row["merge_pick"] = bd["merge_pick"]
        if null:
            row["over_null_pmax"] = bool(a["pmax"] > null["max_pmax"])
        rows.append(row)
    rec_ = [r["recovery"] for r in rows]
    return {"design": design, "register": reg, "enc": enc, "dec": adv, "L": L, "n": len(rows),
            "tau": tau, "lam_u": lam_u, "sec_total": round(time.time() - t0, 2),
            "sec_decode_per": round(tdec / len(rows), 4),
            "median_recovery": float(np.median(rec_)), "mean_recovery": float(np.mean(rec_)),
            "min_recovery": min(rec_), "frac_recovery_ge_085": float(np.mean([x >= 0.85 for x in rec_])),
            "median_pmax": float(np.median([r["pmax"] for r in rows])),
            "median_en": float(np.median([r["en"] for r in rows])),
            "frac_over_null_pmax": (float(np.mean([r["over_null_pmax"] for r in rows])) if null else None),
            "rows": rows}


def load(path):
    return json.load(open(path)) if os.path.exists(path) else {}


def save(path, obj):
    json.dump(obj, open(path, "w"))


def ckey(c):
    return "%s|%s|%s|dec=%s|L%d" % (c["design"], c["register"], c["enc"], c["dec"], c["L"])


def run_null(design, L, tau, lam_u, nnull=100):
    out = os.path.join(HERE, "out_null_%s.json" % design)
    res = load(out)
    K = key(L)
    for enc, adv in PAIRS:       # null ciphertext is the R32 I1 one (planted skip_by_two, shuffled); decoded 3 ways
        rows = []
        t0 = time.time()
        for s in range(nnull):
            P = plain("EN_MODERN", L, s, src=LITE)
            C, _ = B2.ENCIPHER["skip_by_two"](P, K, SUPP, 3301 + s)
            C = list(C)
            random.Random(3301 + s).shuffle(C)
            bd = decode(design, C, K, adv, tau, lam_u)
            rows.append({"seed": s, **adj(bd["plain_idx"])})
        k = "%s|dec=%s|L%d" % (design, adv, L)
        res[k] = {"n": nnull, "sec": round(time.time() - t0, 1),
                  "max_pmax": max(r["pmax"] for r in rows), "max_en": max(r["en"] for r in rows),
                  "max_pmax_ne": max(r["pmax_ne"] for r in rows),
                  "q95_pmax": float(np.quantile([r["pmax"] for r in rows], 0.95)), "rows": rows}
        print("null", k, res[k]["max_pmax"], res[k]["max_en"], res[k]["sec"], flush=True)
        save(out, res)


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "ckpt":
        out = os.path.join(HERE, "out_ckpt.json")
        res = load(out)
        for design in ("base", "panel_max"):
            for reg in ("EN_MODERN", "EN_NOVOWEL"):
                for enc, adv in PAIRS[:2]:
                    c = run_cell(design, reg, enc, adv, 120, range(20))
                    res[ckey(c)] = c
                    print(ckey(c), c["median_recovery"], c["mean_recovery"], c["sec_decode_per"], flush=True)
                    save(out, res)
    elif mode == "tune":
        out = os.path.join(HERE, "out_tune.json")
        res = load(out)
        S = range(500, 510)
        for tau in (0.0, 5.0):
            for reg in ("EN_NOVOWEL", "EN_MODERN"):
                c = run_cell("panel_max", reg, "skip_by_two", 2, 120, S, tau=tau)
                res["tau=%s|%s|skip_by_two" % (tau, reg)] = c
                print("tune tau", tau, reg, c["mean_recovery"], flush=True)
                save(out, res)
        for lam in (2.0, 4.0, 8.0):
            for reg in ("EN_NOVOWEL", "EN_MODERN"):
                c = run_cell("panel_max", reg, "free_q05", "free", 120, S, lam_u=lam)
                res["lam=%s|%s|free_q05" % (lam, reg)] = c
                print("tune lam", lam, reg, c["mean_recovery"], c["sec_decode_per"], flush=True)
                save(out, res)
    elif mode == "grid":
        design, L, regs = sys.argv[2], int(sys.argv[3]), sys.argv[4].split(",")
        if regs == ["ALL"]:
            regs = REGS9
        tau = float(sys.argv[5]) if len(sys.argv) > 5 else 0.0
        lam_u = float(sys.argv[6]) if len(sys.argv) > 6 else 4.0
        nullp = os.path.join(HERE, "out_null_%s.json" % design)
        nulls = load(nullp)
        out = os.path.join(HERE, "out_grid_%s.json" % design)
        res = load(out)
        for reg in regs:
            for enc, adv in PAIRS:
                k = "%s|%s|%s|dec=%s|L%d" % (design, reg, enc, adv, L)
                if k in res:
                    continue
                nl = nulls.get("%s|dec=%s|L%d" % (design, adv, L))
                c = run_cell(design, reg, enc, adv, L, range(20), tau=tau, lam_u=lam_u, null=nl)
                res[ckey(c)] = c
                print(ckey(c), c["median_recovery"], c["mean_recovery"], c["sec_decode_per"], flush=True)
                save(out, res)
    elif mode == "null":
        run_null(sys.argv[2], int(sys.argv[3]),
                 float(sys.argv[4]) if len(sys.argv) > 4 else 0.0,
                 float(sys.argv[5]) if len(sys.argv) > 5 else 4.0)
    elif mode == "speed":
        out = os.path.join(HERE, "speed_raw.json")
        res = {}
        designs = sys.argv[2].split(",")
        nrep = int(sys.argv[3]) if len(sys.argv) > 3 else 5
        for design in designs:
            for L in (120, 400):
                K = key(L)
                for enc, adv in PAIRS:
                    ts = []
                    for s in range(nrep):
                        P = plain("EN_MODERN", L, 100 + s)
                        C, _ = B2.ENCIPHER[enc](P, K, SUPP, 3301 + s)
                        t = time.perf_counter()
                        decode(design, C, K, adv, 0.0, 4.0)
                        ts.append(time.perf_counter() - t)
                    res["%s|L%d|%s" % (design, L, adv)] = {"sec_per_decode_mean": float(np.mean(ts)),
                                                           "decodes_per_s": float(1 / np.mean(ts)), "n": nrep}
                    print(design, L, adv, round(float(np.mean(ts)), 4), flush=True)
        prev = load(out)
        prev.update(res)
        save(out, prev)
