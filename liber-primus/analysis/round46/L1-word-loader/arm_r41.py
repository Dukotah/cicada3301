"""R46-L1 arm R41: R41-C1 R14 wordsum_selfkey (campaign7 W1..W5, sign x atbash) through words.py.

  probe   : 20-draw timing probe -> chooses D per PREREG s4
  null    : matched blockperm null (blocks 100/250/1000, Random(60000+j)) on the real LP2 stream, re-cut each draw to
            words.py's segmentation (2,896 words, grouped by the page each word starts on); units W (whole stream,
            per-page key reset) and P (each page decode, len >= 32); pmax via panel-R36 AD.adjudicate
  judge   : real LP2 through words.py (and, for comparison only, through camp7's legacy loader) -> R41 decision rule
  plants  : English laid over LP2's real layout, regimes a / b / bp, decoded through words.py (L) and camp7 legacy (O)
python -I arm_r41.py probe|null|judge|plants"""
import os, sys, json, time, random
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import numpy as np
import l1lib as G
import words as W
C7 = G._load("camp7", G.AN("round41", "C1-r14-r15", "camp7.py"))
sys.path.insert(0, G.AN("round37", "C1-composed-clue-readings"))
import c1lib  # panel-R36 set-up (sha asserted inside)
AD, PAN = c1lib.AD, c1lib.PAN
BM = G._load("bars_matched", os.path.join(G.LP, "benchmark", "bars_matched.py"))
F = lambda n: os.path.join(HERE, n)
VARS = [(v, s, a) for v in ("W1", "W2", "W3", "W4", "W5") for s in (-1, 1) for a in (False, True)]
BLOCKS = (100, 250, 1000)
ALPHA = 0.0025
vname = lambda v, s, a: "%s|s%+d|a%d" % (v, s, int(a))

REAL = W.lp2()
PAGES_W = REAL.pages_of_words()                     # 55 pages of words (word -> page it starts on)
assert len(PAGES_W) == 55
WLEN = [[len(w) for w in pg] for pg in PAGES_W]
U = list(REAL.runes)


def enc_words(plain_words, variant, sign, atb):          # verbatim from round41/C1-r14-r15/run_c1.py
    tf = (lambda c: (C7.N - 1 - c) if atb else c)
    N = C7.N; out = []
    if variant == "W5":
        flat = [x for w in plain_words for x in w]; prev = 0; cf = []
        for p in flat:
            c = tf((p - sign * (C7.gp.PRIMES[prev] % N)) % N); cf.append(c); prev = c
        pos = 0
        for w in plain_words: out.append(cf[pos:pos + len(w)]); pos += len(w)
        return out
    k, cum = 0, 0
    for w in plain_words:
        cw = [tf((p - sign * k) % N) for p in w]; out.append(cw)
        if variant == "W1": k = C7.primesum(cw) % N
        elif variant == "W2": k = C7.primesum(w) % N
        elif variant == "W3": cum += C7.primesum(cw); k = cum % N
        elif variant == "W4": k = C7._totient(C7.primesum(cw)) % N
    return out


def recut(flat):
    out, pos = [], 0
    for wl in WLEN:
        pg = []
        for L in wl: pg.append(flat[pos:pos + L]); pos += L
        out.append(pg)
    return out


def units(pw):
    out = {}
    for (v, s, a) in VARS:
        parts = [C7.decrypt_variant(words, v, s, a) for words in pw]
        flat = [x for p in parts for x in p]
        out["W:" + vname(v, s, a)] = flat
        for pi, p in enumerate(parts):
            if len(p) >= 32: out["P:%s|p%02d" % (vname(v, s, a), pi)] = p
    return out


def pm(u):
    return {k: float(AD.adjudicate(x)["pmax"]) for k, x in u.items()}


def probe():
    t = time.time()
    for j in range(20):
        pm(units(recut(BM.matched_shuffle(U, 250, random.Random(BM.SEED_BASE + j)))))
    per = (time.time() - t) / 20
    D = 1000 if per * 1000 < 25 * 60 else 400
    r = {"sec_per_draw": round(per, 3), "projected_min_per_block_D1000": round(per * 1000 / 60, 1), "D": D}
    json.dump(r, open(F("r41_probe.json"), "w"), indent=1); print(r)


def null():
    D = json.load(open(F("r41_probe.json")))["D"]
    for b in BLOCKS:
        path = F("r41_null_b%d.npz" % b)
        if os.path.exists(path): continue
        keys = None; t0 = time.time()
        for j in range(D):
            r = pm(units(recut(BM.matched_shuffle(U, b, random.Random(BM.SEED_BASE + j)))))
            if keys is None:
                keys = sorted(r); M = np.full((len(keys), D), np.nan, dtype=np.float32)
            M[:, j] = [r[k] for k in keys]
            if j % 50 == 0:
                G.heartbeat("r41", "null block %d draw %d/%d %.0fs" % (b, j, D, time.time() - t0))
        np.savez_compressed(path, keys=np.array(keys), pm=M)
        print("block", b, "done %.0fs" % (time.time() - t0), flush=True)
    G.heartbeat("r41", "null done")


def judge_level(obs, A, keys, level):
    sel = [i for i, k in enumerate(keys) if k.startswith(level + ":")]
    ks = [keys[i] for i in sel]; X = A[sel].astype(np.float64)
    mu = X.mean(1); sd = X.std(1, ddof=1); sd[sd == 0] = 1e-9
    Z = np.array([(obs[k] - m) / s for k, m, s in zip(ks, mu, sd)])
    ZN = ((X - mu[:, None]) / sd[:, None]).max(0)
    ib = int(Z.argmax()); nb = X.max(0); bo = max(obs[k] for k in ks); bk = max(ks, key=lambda k: obs[k])
    D = X.shape[1]
    return {"n_units": len(ks), "D": D, "best_Z": round(float(Z[ib]), 3), "best_Z_unit": ks[ib], "p_Z": (1 + int((ZN >= Z[ib]).sum())) / (D + 1),
            "obs_best_pmax": round(bo, 3), "obs_best_unit": bk, "p_raw": (1 + int((nb >= bo).sum())) / (D + 1),
            "null_best_max": round(float(nb.max()), 3), "null_best_q99": round(float(np.quantile(nb, .99)), 3)}


def load_null():
    out = {}
    for b in BLOCKS:
        z = np.load(F("r41_null_b%d.npz" % b)); out[b] = ([str(k) for k in z["keys"]], z["pm"])
    return out


def judge():
    NB = load_null()
    obs = pm(units(PAGES_W))
    res = {"segmentation": "words.py (2,896 words; page = page the word starts on)", "blocks": {}, "decision": {}}
    for b, (keys, A) in NB.items():
        res["blocks"][str(b)] = {lv: judge_level(obs, A, keys, lv) for lv in ("W", "P")}
    for lv in ("W", "P"):
        pz = [res["blocks"][str(b)][lv]["p_Z"] for b in BLOCKS]; pr = [res["blocks"][str(b)][lv]["p_raw"] for b in BLOCKS]
        res["decision"][lv] = {"p_Z_by_block": pz, "p_raw_by_block": pr, "decision_p_Z": max(pz), "decision_p_raw": max(pr),
                               "alpha": ALPHA, "crosses": bool(max(pz) <= ALPHA and max(pr) <= ALPHA)}
    res["null_max"] = {lv: max(res["blocks"][str(b)][lv]["null_best_max"] for b in BLOCKS) for lv in ("W", "P")}
    res["obs_top5_P"] = sorted(((round(v, 3), k) for k, v in obs.items() if k.startswith("P:")), reverse=True)[:5]
    res["obs_W"] = {k: round(v, 3) for k, v in obs.items() if k.startswith("W:")}
    # comparison only: the same scorer on R41's legacy camp7 segmentation
    leg = pm(units(C7.word_pages()[:55]))
    res["legacy_camp7_same_scorer"] = {"best_W": round(max(v for k, v in leg.items() if k.startswith("W:")), 3),
                                       "best_P": round(max(v for k, v in leg.items() if k.startswith("P:")), 3)}
    # R3 language-agnostic stats for the top units
    res["top_units_stats"] = []
    U_obs = units(PAGES_W)
    for v, k in res["obs_top5_P"]:
        x = U_obs[k]; res["top_units_stats"].append({"unit": k, "pmax": v, "ioc_n": round(float(AD.ioc_n(np.asarray(x))), 4), "min_distinct32": int(AD.min_distinct(np.asarray(x)))})
    res["flagged_for_oracle"] = [lv for lv in ("W", "P") if res["decision"][lv]["crosses"]]
    json.dump(res, open(F("r41_judge.json"), "w"), indent=1)
    print(json.dumps(res["decision"]), res["null_max"], res["legacy_camp7_same_scorer"], res["obs_top5_P"][:2])


def plants(nplant=2):
    """raw stage: per-page (recovery, pmax) for every plant; recognition applied in plants_summary() after judge."""
    rows = []; t0 = time.time()
    for regime in ("a", "b", "bp"):
        for vi, (v, s, a) in enumerate(VARS):
            for rep in range(nplant):
                rng = random.Random(46410 + 1000 * "a b bp".split().index(regime) + 10 * vi + rep)
                P = G.make_plant(regime, rng)
                groups = {}
                for w, pg in zip(P.words, P.word_page): groups.setdefault(pg, []).append(w)
                cflat = [x for pg in sorted(groups) for cw in enc_words(groups[pg], v, s, a) for x in cw]
                text = G.render_cipher(cflat, P.printed_lens, P.sent_ends)
                for loader in ("L", "O"):
                    if loader == "L":
                        wl, wp, _ = G.new_parse(text)
                    else:
                        wl, wp = G.legacy_parse(text, "camp7")
                    pw = G.by_page(wl, wp)
                    dec = [x for pg in pw for x in C7.decrypt_variant(pg, v, s, a)]
                    assert len(dec) == W.N_LP2
                    pages = []
                    for p in range(55):
                        lo, hi = G.PAGE_BOUNDS[p], G.PAGE_BOUNDS[p + 1]
                        if hi - lo < 32: continue
                        d = dec[lo:hi]; t = P.flat[lo:hi]
                        pages.append([round(sum(x == y for x, y in zip(d, t)) / len(t), 4), round(float(AD.adjudicate(d)["pmax"]), 3)])
                    wrec = sum(x == y for x, y in zip(dec, P.flat)) / len(dec)
                    rows.append({"regime": regime, "variant": vname(v, s, a), "W": v, "rep": rep, "loader": loader, "pages": pages,
                                 "W_recovery": round(wrec, 4), "W_pmax": round(float(AD.adjudicate(dec)["pmax"]), 3)})
            G.heartbeat("r41p", "plants %s %s %.0fs" % (regime, vname(v, s, a), time.time() - t0))
    json.dump({"rows": rows}, open(F("r41_plants_raw.json"), "w"))


def plants_summary():
    nmax = json.load(open(F("r41_judge.json")))["null_max"]
    rows = json.load(open(F("r41_plants_raw.json")))["rows"]
    summ = {}
    for regime in ("a", "b", "bp"):
        for loader in ("L", "O"):
            for Wv in ("W1", "W2", "W3", "W4", "W5", "W1-W4"):
                rr = [r for r in rows if r["regime"] == regime and r["loader"] == loader and (r["W"] == Wv or (Wv == "W1-W4" and r["W"] != "W5"))]
                pg = [q for r in rr for q in r["pages"]]
                k = sum(1 for rec, pm in pg if rec == 1.0 and pm > nmax["P"]); n = len(pg)
                kw = sum(1 for r in rr if r["W_recovery"] == 1.0 and r["W_pmax"] > nmax["W"])
                summ["%s|%s|%s" % (regime, loader, Wv)] = {"P_power": round(k / n, 4), "P_k": k, "P_n": n, "P_wilson": G.wilson(k, n),
                                                           "W_power": round(kw / len(rr), 3), "W_k": kw, "W_n": len(rr),
                                                           "mean_page_recovery": round(sum(q[0] for q in pg) / n, 4),
                                                           "median_page_pmax": sorted(q[1] for q in pg)[n // 2],
                                                           "median_W_pmax": sorted(r["W_pmax"] for r in rr)[len(rr) // 2]}
    out = {"null_max_used": nmax, "rule": "page recognised = exact page recovery AND page pmax > P-level null max (max over blocks 100/250/1000); W = whole stream exact AND pmax > W null max",
           "summary": summ}
    json.dump(out, open(F("r41_plants.json"), "w"), indent=1)
    for k, v in summ.items():
        if k.endswith("W1-W4") or k.endswith("W5"): print(k, v["P_power"], v["W_power"], v["mean_page_recovery"], v["median_page_pmax"])


if __name__ == "__main__":
    {"probe": probe, "null": null, "judge": judge, "plants": plants, "summary": plants_summary}[sys.argv[1]]()
