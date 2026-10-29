"""Round 32 / I1 -- power-envelope harness.  One process, small memory, incremental JSON.

    python run_envelope.py null            # shuffle null per (decoder, L)       -> out_null.json
    python run_envelope.py en              # EN_MODERN full matrix               -> out_en.json
    python run_envelope.py reg             # other registers, reduced matrix     -> out_reg.json
    python run_envelope.py speed
"""
import os, sys, json, time, random
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import beam_v2 as B
import adjudicate as A

PAN = A.Panel(os.path.join(HERE, "models", "panel_lite.npz"))
TEST = np.load(os.path.join(HERE, "models", "testhalves_lite.npz"))
DECODERS = [1, 2, "free"]
ENCS = ["keyskip1", "skip_by_two", "free_q05"]
SUPP = 0.83


def plain(reg, L, s):
    a = TEST[reg].astype(np.int64)
    r = random.Random(9000 + s)
    st = r.randrange(0, len(a) - L - 1)
    return a[st:st + L].tolist()


def adj(idx):
    r = A.adjudicate(idx, pan=PAN)
    return {k: (round(float(r[k]), 4) if isinstance(r[k], (float, np.floating)) else r[k])
            for k in ("en", "pmax", "pmax_ne", "pcon", "ioc")} | {"preg": PAN.registers[r["preg"]]}


def key(L):
    return B.sha_ctr_key(L * 12 + 2048)


def run_null(Ls, nnull, out):
    res = json.load(open(out)) if os.path.exists(out) else {}
    for L in Ls:
        K = key(L)
        for dec in DECODERS:
            rows = []
            t0 = time.time()
            for s in range(nnull):
                # null ciphertext: uniform random runes (seed 3301 shuffle of a planted C is
                # distributionally equivalent for a pseudo-random key; we shuffle a real one)
                P = plain("EN_MODERN", L, s)
                C, _ = B.ENCIPHER["skip_by_two"](P, K, SUPP, 3301 + s)
                C = list(C)
                random.Random(3301 + s).shuffle(C)
                bd = B.beam_decode_v2(C, K, dec)
                rows.append({"seed": s, **adj(bd["plain_idx"])})
            res["%s|L%d" % (dec, L)] = {
                "n": nnull, "sec": round(time.time() - t0, 1),
                "max_pmax": max(r["pmax"] for r in rows), "max_en": max(r["en"] for r in rows),
                "max_pmax_ne": max(r["pmax_ne"] for r in rows),
                "q95_pmax": float(np.quantile([r["pmax"] for r in rows], 0.95)),
                "rows": rows}
            print("null", dec, L, res["%s|L%d" % (dec, L)]["max_pmax"], res["%s|L%d" % (dec, L)]["sec"], flush=True)
            json.dump(res, open(out, "w"))


def run_cells(regs, encs_decs, Ls, nseed, out, null):
    res = {}
    for reg in regs:
        for L in Ls:
            K = key(L)
            for enc, dec in encs_decs:
                rows = []
                t0 = time.time()
                for s in range(nseed):
                    P = plain(reg, L, s)
                    C, info = B.ENCIPHER[enc](P, K, SUPP, 3301 + s)
                    bd = B.beam_decode_v2(C, K, dec)
                    rec = B.recovery(bd["plain_idx"], P)
                    dbl = sum(1 for i in range(1, len(C)) if C[i] == C[i - 1]) / (len(C) - 1)
                    nl = null.get("%s|L%d" % (dec, L))
                    a = adj(bd["plain_idx"])
                    rows.append({"seed": s, "recovery": round(rec, 4), "dbl_pct": round(100 * dbl, 3),
                                 **info, **a,
                                 "over_null_pmax": bool(nl and a["pmax"] > nl["max_pmax"]),
                                 "over_null_en": bool(nl and a["en"] > nl["max_en"])})
                key_ = "%s|%s|dec=%s|L%d" % (reg, enc, dec, L)
                rec_ = [r["recovery"] for r in rows]
                res[key_] = {"register": reg, "enc": enc, "dec": dec, "L": L, "n": nseed,
                             "sec": round(time.time() - t0, 1),
                             "median_recovery": float(np.median(rec_)), "min_recovery": min(rec_),
                             "median_pmax": float(np.median([r["pmax"] for r in rows])),
                             "median_pmax_ne": float(np.median([r["pmax_ne"] for r in rows])),
                             "median_en": float(np.median([r["en"] for r in rows])),
                             "frac_over_null_pmax": float(np.mean([r["over_null_pmax"] for r in rows])),
                             "frac_recovery_ge_085": float(np.mean([x >= 0.85 for x in rec_])),
                             "rows": rows}
                print(key_, res[key_]["median_recovery"], res[key_]["median_pmax"], res[key_]["sec"], flush=True)
                json.dump(res, open(out, "w"))


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "speed":
        for L in (120, 400):
            K = key(L)
            for dec in DECODERS:
                P = plain("EN_MODERN", L, 0)
                C, _ = B.ENCIPHER["skip_by_two"](P, K, SUPP, 3301)
                t = time.time(); bd = B.beam_decode_v2(C, K, dec)
                print(L, dec, round(time.time() - t, 2), round(B.recovery(bd["plain_idx"], P), 3), flush=True)
    elif mode == "null":
        run_null([int(x) for x in sys.argv[2].split(",")], int(sys.argv[3]), os.path.join(HERE, "out_null.json"))
    else:
        null = json.load(open(os.path.join(HERE, "out_null.json")))
        Ls = [int(x) for x in sys.argv[2].split(",")]
        nseed = int(sys.argv[3])
        if mode == "en":
            run_cells(["EN_MODERN"], [(e, d) for e in ENCS for d in DECODERS], Ls, nseed,
                      os.path.join(HERE, "out_en_L%s.json" % sys.argv[2].replace(",", "_")), null)
        elif mode == "reg":
            pairs = [("skip_by_two", 2), ("skip_by_two", "free"), ("keyskip1", 1),
                     ("keyskip1", "free"), ("free_q05", "free")]
            run_cells(["LATIN", "EN_NOVOWEL", "OE", "DE"], pairs, Ls, nseed,
                      os.path.join(HERE, "out_reg_L%s.json" % sys.argv[2].replace(",", "_")), null)
