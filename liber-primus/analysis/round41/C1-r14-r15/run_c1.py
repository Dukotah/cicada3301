"""Round 41 C1: R14 / R15 re-score under panel-R36 (direct machinery, lib.py = round40 C1 lib copied unchanged) with the standing
matched null (benchmark/bars_matched.py blockperm, blocks 100/250/1000, Random(60000+j)).  python -I run_c1.py [D]
Stages (checkpointed, resumable): plants-recovery -> null (per family x block, npz) -> judge (observed + plants + p-values).
Writes only in this directory."""
import os, sys, json, math, random, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
import lib
from lib import U, TEST, PAN, REGS, pm_many, wait_mem, free_gb, log, AD, bar12, wilson
import camp7 as C
sys.path.insert(0, os.path.join(C.LPD, "benchmark"))
import bars_matched as BM

D = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
BLOCKS = (100, 250, 1000)
TAG = "" if D == 1000 else "_D%d" % D
F = lambda *a: os.path.join(HERE, *a)
PLANT_REGS = ("EN_MODERN", "LATIN", "EN_NOVOWEL")
R14_VARS = [(v, s, a) for v in ("W1", "W2", "W3", "W4", "W5") for s in (-1, 1) for a in (False, True)]
HILL = C.hill_variants()                    # (mname, vn) -> mat
HILL_KEYS = list(HILL.keys())
HILL_ARR = {k: np.array(m, dtype=np.int64) for k, m in HILL.items()}
NPAGES = 55

pages_w = C.word_pages()[:-2]               # list of pages, each list of words (rune idx)
assert len(pages_w) == NPAGES
page_len = [sum(len(w) for w in pg) for pg in pages_w]
word_len = [[len(w) for w in pg] for pg in pages_w]
UN = [i for pg in pages_w for w in pg for i in w]
assert len(UN) == 12956 and UN == list(U), "unsolved stream != LP2 U"
assert [i for pg in C.load_pages()[:-2] for i in pg] == UN


def recut_words(flat):
    out, pos = [], 0
    for wl in word_len:
        pg = []
        for L in wl:
            pg.append(flat[pos:pos + L]); pos += L
        out.append(pg)
    return out


def recut_pages(flat):
    out, pos = [], 0
    for L in page_len:
        out.append(flat[pos:pos + L]); pos += L
    return out


def vname(v, s, a): return "%s|s%+d|a%d" % (v, s, int(a))
def hname(k): return "%s.%s" % k


# ---------------------------------------------------------------- unit builders
def r14_units(pw):
    """pw: pages of words.  Level W: concat of per-page decrypts per variant; level P: each page decrypt."""
    out = {}
    for (v, s, a) in R14_VARS:
        parts = [C.decrypt_variant(words, v, s, a) for words in pw]
        out["W:" + vname(v, s, a)] = np.array([x for p in parts for x in p], dtype=np.int64)
        for pi, p in enumerate(parts):
            if len(p) >= 32: out["P:%s|p%02d" % (vname(v, s, a), pi)] = np.array(p, dtype=np.int64)
    return out


def hill_np(idxs, T):
    n = T.shape[0]; m = (len(idxs) // n) * n
    if m == 0: return np.zeros(0, dtype=np.int64)
    A = np.asarray(idxs[:m], dtype=np.int64).reshape(-1, n)
    return ((A @ T.T) % 29).reshape(-1)


def r15_units(pages):
    """pages: list of rune lists.  Level W: the WHOLE concat (blocks run across page boundaries); level P: each page."""
    whole = [i for pg in pages for i in pg]; out = {}
    for k in HILL_KEYS:
        T = HILL_ARR[k]
        out["W:" + hname(k)] = hill_np(whole, T)
        for pi, pg in enumerate(pages):
            o = hill_np(pg, T)
            if len(o) >= 32: out["P:%s|p%02d" % (hname(k), pi)] = o
    return out


def builder(fam):
    if fam == "R14": return lambda flat: r14_units(recut_words(flat))
    return lambda flat: r15_units(recut_pages(flat))


# ---------------------------------------------------------------- exactness of the numpy hill vs the archived apply_hill, on the real data
def check_numpy_hill():
    pages = [list(p) for p in recut_pages(UN)]; whole = UN
    for k in HILL_KEYS:
        assert list(hill_np(whole, HILL_ARR[k])) == C.apply_hill(whole, HILL[k]), k
        for pg in pages[:6]:
            assert list(hill_np(pg, HILL_ARR[k])) == C.apply_hill(pg, HILL[k]), k


# ---------------------------------------------------------------- plants
def plain_slice(reg, n, seed):
    arr = TEST[reg].astype(np.int64); st = random.Random(seed).randrange(0, len(arr) - n - 1); return [int(x) for x in arr[st:st + n]]


def enc_words(plain_words, variant, sign, atb):
    tf = (lambda c: (C.N - 1 - c) if atb else c)
    N = C.N; out = []
    if variant == "W5":
        flat = [x for w in plain_words for x in w]; prev = 0; cf = []
        for p in flat:
            c = tf((p - sign * (C.gp.PRIMES[prev] % N)) % N); cf.append(c); prev = c
        pos = 0
        for w in plain_words: out.append(cf[pos:pos + len(w)]); pos += len(w)
        return out
    k, cum = 0, 0
    for w in plain_words:
        cw = [tf((p - sign * k) % N) for p in w]; out.append(cw)
        if variant == "W1": k = C.primesum(cw) % N
        elif variant == "W2": k = C.primesum(w) % N
        elif variant == "W3": cum += C.primesum(cw); k = cum % N
        elif variant == "W4": k = C._totient(C.primesum(cw)) % N
    return out


def r14_plant(level, vi, reg_i):
    v, s, a = R14_VARS[vi]; reg = PLANT_REGS[reg_i]; seed = 41000 + 7 * vi + reg_i
    if level == "W":
        flat = plain_slice(reg, 12956, seed); pw = recut_words(flat)
        cw = [enc_words(pg, v, s, a) for pg in pw]
        dec = [C.decrypt_variant(pg, v, s, a) for pg in cw]
        rec = float(np.mean([d == p for d, p in zip(dec, [[x for w in pg for x in w] for pg in pw])]))
        units = r14_units(cw)
        return reg, v, s, a, rec, units, "W:" + vname(v, s, a)
    pg = (3 * (reg_i * len(R14_VARS) + vi)) % NPAGES
    flat = plain_slice(reg, page_len[pg], seed); pwords = []; pos = 0
    for L in word_len[pg]: pwords.append(flat[pos:pos + L]); pos += L
    cw = enc_words(pwords, v, s, a); dec = C.decrypt_variant(cw, v, s, a)
    rec = 1.0 if dec == flat else float(np.mean(np.array(dec) == np.array(flat)))
    return reg, v, s, a, rec, {"P:plant": np.array(dec, dtype=np.int64)}, "P:plant"


def r15_plant(level, ki, reg_i):
    k = HILL_KEYS[ki]; T = HILL[k]; Tinv = C.mat_inv_mod([r[:] for r in T]); reg = PLANT_REGS[reg_i]; n = len(T); seed = 42000 + 11 * ki + reg_i
    assert Tinv is not None
    if level == "W":
        m = (12956 // n) * n; plain = plain_slice(reg, m, seed)
        cipher = C.apply_hill(plain, Tinv); dec = C.apply_hill(cipher, T)
        rec = float(np.mean(np.array(dec) == np.array(plain)))
        # stream through the real builder: whole = cipher laid over 55 pages (page cuts are irrelevant to W)
        pages = recut_pages(cipher + [0] * (12956 - len(cipher)))
        units = r15_units(pages)
        return reg, k, rec, units, "W:" + hname(k), (units["W:" + hname(k)][:m] == np.array(plain)).all()
    pg = (3 * (reg_i * len(HILL_KEYS) + ki)) % NPAGES
    m = (page_len[pg] // n) * n; plain = plain_slice(reg, m, seed)
    cipher = C.apply_hill(plain, Tinv); dec = C.apply_hill(cipher, T)
    rec = float(np.mean(np.array(dec) == np.array(plain)))
    return reg, k, rec, {"P:plant": hill_np(cipher, HILL_ARR[k])}, "P:plant", True


def plants_recovery():
    """Q5(ii): the first six plants (W1 and M1_1033.M x 3 registers) must recover exactly before anything is scored."""
    out = {"R14": [], "R15": []}
    for reg_i in range(3):
        r = r14_plant("W", 0, reg_i); out["R14"].append({"reg": r[0], "variant": vname(r[1], r[2], r[3]), "recovery": r[4]})
        r = r15_plant("W", HILL_KEYS.index(("M1_1033", "M")), reg_i); out["R15"].append({"reg": r[0], "variant": hname(r[1]), "recovery": r[2]})
    ok = all(x["recovery"] == 1.0 for v in out.values() for x in v)
    json.dump({"first_six": out, "all_exact": ok}, open(F("plants_first6.json"), "w"), indent=1)
    log("Q5(ii) first-six exact recovery:", ok)
    return ok


# ---------------------------------------------------------------- null
def run_null(fam, block, build):
    path = F("null_%s_b%d%s.npz" % (fam, block, TAG))
    if os.path.exists(path): log(fam, block, "null exists"); return
    keys = None; rows = []; t0 = time.time(); store = None; jl = open(F("null_draws%s.jsonl" % TAG), "a")
    for j in range(D):
        sh = BM.matched_shuffle(UN, block, random.Random(BM.SEED_BASE + j))
        pm = pm_many(build(sh))
        if keys is None:
            keys = sorted(pm); store = np.full((len(keys), D), np.nan, dtype=np.float32)
        for ki, k in enumerate(keys): store[ki, j] = pm[k]
        wb = max(v for k, v in pm.items() if k.startswith("W:") and v == v); pb = max(v for k, v in pm.items() if k.startswith("P:") and v == v)
        jl.write(json.dumps({"fam": fam, "block": block, "j": j, "bestW": wb, "bestP": pb}) + "\n")
        if (j + 1) % 100 == 0:
            jl.flush(); log(fam, "b%d" % block, "draw", j + 1, "of", D, "%.0fs" % (time.time() - t0))
            if free_gb() < 0.4: wait_mem(0.4)
    jl.close()
    np.savez_compressed(path, keys=np.array(keys), pm=store)
    log(fam, "b%d" % block, "null saved", path)


# ---------------------------------------------------------------- judge
def judge_level(obs, nul, keys, level):
    """obs: key->pmax; nul: (K,D) matrix over `keys`; returns Z-family and raw p + details for keys of `level`."""
    sel = [i for i, k in enumerate(keys) if k.startswith(level + ":") and obs.get(k, float("nan")) == obs.get(k, float("nan"))]
    ks = [keys[i] for i in sel]; A = nul[sel].astype(np.float64)
    mu = np.nanmean(A, axis=1); sd = np.nanstd(A, axis=1, ddof=1); sd[sd == 0] = 1e-9
    Zobs = np.array([(obs[k] - m) / s for k, m, s in zip(ks, mu, sd)])
    ZN = (A - mu[:, None]) / sd[:, None]; M = np.nanmax(ZN, axis=0)
    ib = int(np.argmax(Zobs)); Mobs = float(Zobs[ib]); exc = int((M >= Mobs).sum()); Dn = A.shape[1]
    nb = np.nanmax(A, axis=0); bo_i = int(np.argmax([obs[k] for k in ks])); bo = float(obs[ks[bo_i]]); e2 = int((nb >= bo).sum())
    top = sorted(zip(Zobs.tolist(), [obs[k] for k in ks], ks), reverse=True)[:5]
    return {"n_units": len(ks), "D": Dn, "best_Z": Mobs, "best_Z_unit": ks[ib], "best_Z_unit_pmax": float(obs[ks[ib]]), "exceed_Z": exc, "p_Z": (1 + exc) / (Dn + 1),
            "null_famZ_q99": float(np.quantile(M, .99)), "null_famZ_max": float(M.max()),
            "obs_best_pmax": bo, "obs_best_pmax_unit": ks[bo_i], "exceed_raw": e2, "p_raw": (1 + e2) / (Dn + 1),
            "null_best_mean": float(nb.mean()), "null_best_q99": float(np.quantile(nb, .99)), "null_best_max": float(nb.max()),
            "top5_Z": [[round(a, 3), round(b, 3), c] for a, b, c in top]}


def judge(fam, build):
    obs = pm_many(build(UN)); res = {"family": fam, "n_units_total": len(obs), "blocks": {}}
    NB = {}
    for b in BLOCKS:
        z = np.load(F("null_%s_b%d%s.npz" % (fam, b, TAG))); keys = [str(k) for k in z["keys"]]; nul = z["pm"]; NB[b] = (keys, nul)
        res["blocks"][str(b)] = {lv: judge_level(obs, nul, keys, lv) for lv in ("W", "P")}
    res["obs_W"] = {k: v for k, v in obs.items() if k.startswith("W:")}
    res["obs_top_P"] = sorted(((v, k) for k, v in obs.items() if k.startswith("P:") and v == v), reverse=True)[:10]
    # decision
    alpha = 0.0025; dec = {}
    for lv in ("W", "P"):
        pz = [res["blocks"][str(b)][lv]["p_Z"] for b in BLOCKS]; pr = [res["blocks"][str(b)][lv]["p_raw"] for b in BLOCKS]
        dec[lv] = {"p_Z_by_block": pz, "p_raw_by_block": pr, "decision_p_Z": max(pz), "decision_p_raw": max(pr), "alpha": alpha, "crosses": bool(max(pz) <= alpha and max(pr) <= alpha)}
    res["decision"] = dec
    # plants
    pl = []
    nbmax = {lv: max(res["blocks"][str(b)][lv]["null_best_max"] for b in BLOCKS) for lv in ("W", "P")}
    for lv in ("W", "P"):
        if fam == "R14":
            for vi in range(len(R14_VARS)):
                for ri in range(3):
                    reg, v, s, a, rec, units, key = r14_plant(lv, vi, ri)
                    pmx = pm_many(units); p = pmx[key]
                    argmax_ok = None
                    if lv == "W":
                        wk = {k: x for k, x in pmx.items() if k.startswith("W:")}; argmax_ok = bool(max(wk, key=wk.get) == key)
                    pl.append({"level": lv, "register": reg, "variant": vname(v, s, a), "recovery": rec, "plant_pmax": round(p, 3), "null_best_max_allblocks": round(nbmax[lv], 3),
                               "recognised": bool(rec == 1.0 and p > nbmax[lv]), "argmax_is_planted_variant": argmax_ok})
        else:
            for ki in range(len(HILL_KEYS)):
                for ri in range(3):
                    r = r15_plant(lv, ki, ri); reg, k, rec, units, key, exact_stream = r
                    pmx = pm_many(units); p = pmx[key]
                    argmax_ok = None
                    if lv == "W":
                        wk = {kk: x for kk, x in pmx.items() if kk.startswith("W:")}; argmax_ok = bool(max(wk, key=wk.get) == key)
                    pl.append({"level": lv, "register": reg, "variant": hname(k), "recovery": rec, "stream_equals_plain": bool(exact_stream), "plant_pmax": round(p, 3),
                               "null_best_max_allblocks": round(nbmax[lv], 3), "recognised": bool(rec == 1.0 and p > nbmax[lv]), "argmax_is_planted_variant": argmax_ok})
    res["plants"] = pl
    cells = {}
    for x in pl:
        c = cells.setdefault("%s|%s" % (x["level"], x["register"]), [0, 0]); c[0] += int(x["recognised"]); c[1] += 1
    res["control_cells"] = {k: {"recognised": v[0], "n": v[1]} for k, v in cells.items()}
    res["control_passed"] = all(v[0] == v[1] for v in cells.values())
    # observed vs survivor12 bar of record (non-binding)
    res["obs_best_vs_bar_of_record_N1e6"] = {"best_W_pmax": max(res["obs_W"].values()), "best_P_pmax": res["obs_top_P"][0][0], "bar_N1e6_L120_ks1": 10.4645,
                                           "note": "non-binding; the survivor12 bar is for key-sweep survivors; W-level z is sqrt(n/1000)-rescaled"}
    # degenerate flags on the best units
    mds_min, ioc_max, _ = lib.degenerate_thresholds()
    deg = []; OB = build(UN)
    for k, v in sorted(((k, v) for k, v in obs.items() if v == v), key=lambda kv: -kv[1])[:10]:
        x = OB[k]; deg.append({"unit": k, "pmax": v, "mds": int(AD.min_distinct(x)), "ioc_n": float(AD.ioc_n(x)), "degenerate": bool(AD.min_distinct(x) <= mds_min or AD.ioc_n(x) >= ioc_max)})
    res["top10_units_with_degenerate_flag"] = deg
    json.dump(res, open(F("result_%s%s.json" % (fam, TAG)), "w"), indent=1, default=float)
    log(fam, "judged", json.dumps(dec), "control_passed", res["control_passed"])
    return res


if __name__ == "__main__":
    wait_mem(); check_numpy_hill(); log("numpy hill == archived apply_hill on all 24 variants (whole + 6 pages)")
    if not plants_recovery():
        log("Q5(ii) FAILED: aborting scoring"); sys.exit(2)
    for fam in ("R14", "R15"):
        bld = builder(fam)
        for b in BLOCKS: wait_mem(); run_null(fam, b, bld)
    for fam in ("R14", "R15"):
        judge(fam, builder(fam))
    log("ALL DONE")
