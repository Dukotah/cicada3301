"""L6 - LANGUAGE-AGNOSTIC re-scoring of this lane's survivors.

Why this exists.  Round 18 lane L7-A established that every negative in this repository is
an ENGLISH-ONLY negative: handed the CORRECT key, the beam recovers 100% of runes for
Latin, Old English, German, Welsh and abbreviated English, and the English quadgram
adjudicator then scores the result as noise (measured power 0.33 for Latin, 0.00 for
vowel-dropped English).  ARMADA-DOCTRINE R2/R3 make the consequence a requirement: a sweep
must report its power over the REGISTER axis, and must persist language-agnostic statistics.

This lane's sweeps were pre-registered and launched before that doctrine was written, so
full R3 compliance (every row, at sweep time) is not available retroactively - the decodes
are gone.  What IS available, and is done here, is the same measurement on every SURVIVOR:
the top rows of each stage are re-decoded at their recorded offsets and scored under

  * a REGISTER PANEL of rune-index trigram models (EN / LP1's own plaintext / Latin /
    Old English / German / Welsh / vowel-dropped English), built from lane L7's panels, and
  * three language-free statistics: decrypt IoC*N, minimum distinct symbols over a 32-rune
    window, and zlib compressibility.

Each is compared against a matched null band (shuffled-ciphertext decodes through the same
path), so "no register anomaly" is a measured statement rather than an absence of looking.
"""
import os, sys, json, math, random, zlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import lib_l6 as X
import lib_padsweep as L
import skipdecode as sk

N = 29
TOPK = 20
NULL_N = 60
L7 = os.path.join(X.ANALYSIS, "round18", "L7-redteam")


def panels():
    sys.path.insert(0, L7)
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "l7a1", os.path.join(L7, "a1_scorer_language.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    P = mod.build_panels()
    return {k: v for k, v in P.items() if k not in ("RAND", "EN_KJV")}


def trigram(idx):
    a = np.asarray(idx, dtype=np.int64)
    c = np.ones((N, N, N), dtype=np.float64)
    np.add.at(c, (a[:-2], a[1:-1], a[2:]), 1.0)
    return np.log10(c / c.sum(axis=2, keepdims=True)).astype(np.float32)


def score_under(T, p):
    p = np.asarray(p, dtype=np.int64)
    if p.size < 3:
        return None
    return float(T[p[:-2], p[1:-1], p[2:]].mean())


def ioc_n(p):
    p = np.asarray(p)
    n = p.size
    if n < 2:
        return None
    cnt = np.bincount(p, minlength=N).astype(np.float64)
    return float((cnt * (cnt - 1)).sum() / (n * (n - 1)) * N)


def min_distinct(p, w=32):
    p = np.asarray(p)
    if p.size < w:
        return int(np.unique(p).size)
    return int(min(np.unique(p[i:i + w]).size for i in range(p.size - w + 1)))


def compress_ratio(p):
    b = bytes(int(x) for x in p)
    return round(len(zlib.compress(b, 9)) / max(1, len(b)), 4)


def stats_for(p, models):
    return {"ioc_times_n": round(ioc_n(p), 4), "min_distinct_32": min_distinct(p),
            "zlib_ratio": compress_ratio(p),
            "register": {k: round(score_under(T, p), 4) for k, T in models.items()}}


def main():
    L.trigram_model()
    print("building register panel models ...", flush=True)
    models = {k: trigram(v) for k, v in panels().items()}
    print("  panels:", list(models), flush=True)

    C0 = [int(x) for x in L.nc.unsolved()]
    C1 = [(N - 1) - c for c in C0]
    out = {"topk": TOPK, "null_n": NULL_N, "registers": list(models),
           "max_skip": X.MS, "head": X.HEAD, "rows": {}, "null_band": {}}

    # ---------- null band: shuffled ciphertext through the same path -----------
    cfgs = [c for c in X.mine_configs() if c["kind"] == "b04"]
    Kn = [int(x) for x in X.derived_keystream(cfgs[0], 1 << 17)]
    acc = {}
    for k in range(NULL_N):
        r = random.Random(9000 + k)
        s = list(C0[:X.HEAD]); r.shuffle(s)
        bd = sk.beam_decode(s, Kn, sign=-1, o=(k * 37) % (1 << 15),
                            beam_w=X.BEAM_W, max_skip=X.MS)
        st = stats_for(bd["plain_idx"], models)
        for key in ("ioc_times_n", "min_distinct_32", "zlib_ratio"):
            acc.setdefault(key, []).append(st[key])
        for rk, rv in st["register"].items():
            acc.setdefault("reg:" + rk, []).append(rv)
    for k, v in acc.items():
        v = np.array(v, dtype=float)
        out["null_band"][k] = {"mean": round(float(v.mean()), 4),
                               "sd": round(float(v.std()), 4),
                               "max": round(float(v.max()), 4),
                               "min": round(float(v.min()), 4)}
    print("  null band built", flush=True)

    man_p = os.path.join(X.DATA, "MANIFEST.json")
    man = json.load(open(man_p)) if os.path.exists(man_p) else {"verified_pads": []}
    padmap = {p["name"]: os.path.join(X.DATA, "iso", p["extracted"])
              for p in man["verified_pads"]}
    padmap["MARSAGLIA_CDROM.iso"] = os.path.join(X.DATA, "MARSAGLIA_CDROM.iso")

    # ---------- A1 / A2 --------------------------------------------------------
    for stage in ("A1", "A2"):
        p = os.path.join(X.OUT, f"results_{stage}.json")
        if not os.path.exists(p):
            continue
        rows = json.load(open(p))["top30"][:TOPK]
        res = []
        for r in rows:
            cfg = {"kind": r.get("kind", "b04"), "gen": r.get("gen"),
                   "red": r.get("red"), "seed_hex": r.get("seed_hex"),
                   "dir": r.get("dir", "fwd")}
            if cfg["kind"] == "kdf":
                cfg = {"kind": "kdf", "secret_hex": r.get("seed_hex"), "kdf": r.get("gen"),
                       "salt": r.get("salt"), "reduction": r.get("red"),
                       "dir": r.get("dir", "fwd")}
            elif cfg["kind"] == "prng":
                cfg = {"kind": "prng", "gen": r.get("gen"), "seed": int(r.get("seed")),
                       "dir": r.get("dir", "fwd")}
            need = int(r["offset"]) + X.SPAN + 256
            try:
                K = [int(x) for x in X.derived_keystream(cfg, need)]
            except Exception as e:
                res.append({"score": r["score"], "error": str(e)}); continue
            C = C1 if int(r.get("atbash", 0) or 0) else C0
            bd = sk.beam_decode(C[:X.HEAD], K, sign=int(r["sign"]), o=int(r["offset"]),
                                beam_w=X.BEAM_W, max_skip=X.MS)
            res.append({"english_score": round(r["score"], 4), "offset": r["offset"],
                        "gen": r.get("gen"), "red": r.get("red"), "seed": r.get("seed"),
                        **stats_for(bd["plain_idx"], models)})
        out["rows"][stage] = res
        print(f"  {stage}: {len(res)} survivors re-scored", flush=True)

    # ---------- Marsaglia ------------------------------------------------------
    p = os.path.join(X.OUT, "results_M.json")
    if os.path.exists(p):
        rows = json.load(open(p))["top30"][:TOPK]
        res = []
        for r in rows:
            fp = padmap.get(r["pad"])
            if not fp or not os.path.exists(fp):
                continue
            a = np.fromfile(fp, dtype=np.uint8)
            src = a[::-1] if r.get("rev") else a
            fn, spb = X.BUILDERS[r["builder"]]
            o = int(r["offset"]); b0 = o // spb
            b1 = min(a.size, b0 + (X.SPAN + 512) // spb + 64)
            K = [int(x) for x in fn(np.ascontiguousarray(src[b0:b1]))]
            loc = o - b0 * spb
            if loc + X.SPAN + 8 >= len(K):
                continue
            bd = sk.beam_decode(C0[:X.HEAD], K, sign=int(r["sign"]), o=loc,
                                beam_w=X.BEAM_W, max_skip=X.MS)
            res.append({"english_score": round(r["score"], 4), "pad": r["pad"],
                        "builder": r["builder"], "rev": r.get("rev"),
                        "offset": o, **stats_for(bd["plain_idx"], models)})
            del a, src, K
        out["rows"]["M"] = res
        print(f"  M: {len(res)} survivors re-scored", flush=True)

    # ---------- adjudication ---------------------------------------------------
    flags = []
    nb = out["null_band"]
    for stage, rr in out["rows"].items():
        for r in rr:
            if "register" not in r:
                continue
            for rk, rv in r["register"].items():
                band = nb.get("reg:" + rk)
                if band and rv > band["max"] + 0.10:
                    flags.append({"stage": stage, "register": rk, "score": rv,
                                  "null_max": band["max"], "row": r})
            for k in ("ioc_times_n", "min_distinct_32"):
                band = nb.get(k)
                if band and band["sd"] > 0 and abs(r[k] - band["mean"]) > 4 * band["sd"]:
                    flags.append({"stage": stage, "stat": k, "value": r[k],
                                  "null_mean": band["mean"], "null_sd": band["sd"],
                                  "row": r})
    out["anomalies"] = flags
    out["verdict"] = ("no survivor exceeds its matched null band on ANY register model or "
                      "language-free statistic" if not flags else
                      f"{len(flags)} survivor/statistic pairs outside the null band - INSPECT")
    X.jdump(out, os.path.join(X.OUT, "langagnostic.json"))
    print("\n" + out["verdict"])
    print("wrote", os.path.join(X.OUT, "langagnostic.json"))


if __name__ == "__main__":
    main()
