"""C2 — THE PREFILTER'S REGISTER POWER, measured on the real Marsaglia bytes.

round18/L7-redteam/RESULTS.md §A.7 says, of the ~1.45e10 offsets Round 17 scored and the
2.3e8 Round 18/L6 scored:

    "R17's own measured prefilter survival (0.375-0.875, non-monotone in pad size) is a
     survival rate FOR ENGLISH PLANTS ONLY; no non-English survival rate was ever
     measured, so R17's coverage discount does not apply to a non-English plaintext at
     all."

This script measures it.  L7-A measured the ADJUDICATOR's register power (the English
quadgram beam).  Nobody measured the PREFILTER's -- and the prefilter runs first, so a
register it discards never reaches the beam at all and L7-A's numbers never apply.

Design (PREREG §3): paired.  The same 30 (pad, true-offset) pairs are used for every
register, so the register contrast is not confounded with pad statistics or offset.

Alongside the English trigram prefilter, three LANGUAGE-AGNOSTIC screens are computed on
the identical offsets in the same pass -- doctrine R3's mandatory statistics, which no
sweep in this repository has ever persisted:  decrypt IoC*N, distinct symbols in the
24-rune window, max unigram count in that window.

    python3 prefilter_register_power.py --nproc 6 [--ntrials 30] [--registers A,B]
"""
import os, sys, json, random, time, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
ANALYSIS = os.path.abspath(os.path.join(HERE, "..", "..", ".."))    # liber-primus/analysis
LP = os.path.abspath(os.path.join(ANALYSIS, ".."))                  # liber-primus/
L6 = os.path.join(ANALYSIS, "round18", "L6-offset-marsaglia")
for p in (os.path.join(ANALYSIS, "round17"), os.path.join(L6, "scripts"),
          os.path.join(ANALYSIS, "round18", "L7-redteam"),
          os.path.join(LP, "src"), os.path.join(LP, "benchmark"),
          os.path.join(ANALYSIS, "campaign18_skip")):
    if p not in sys.path:
        sys.path.insert(0, p)

import numpy as np                                    # noqa: E402
import lib_padsweep as L                              # noqa: E402
import skipdecode as sk                               # noqa: E402

N = 29
PLEN = L.PREFILTER_LEN            # 24 -- dense_scan's own prefilter window, unchanged
KEEP = 1000                       # L6 sub-lane B's own keep, unchanged
PLANT_LEN = 120                   # L7-A's headline length
SUPP = 0.83                       # the pinned filter
SEED0 = 33019
OUT = os.path.abspath(os.path.join(HERE, ".."))
DATA = os.path.join(L6, "data")

REGISTERS = ["EN_KJV", "EN_MODERN", "LP1_REAL", "LATIN", "OE", "DE", "CY",
             "EN_HALFVOWEL", "EN_NOVOWEL", "RAND"]
ENGLISH_ARMS = {"EN_KJV", "EN_MODERN", "LP1_REAL"}

_G = {}


# --------------------------------------------------------------------------- the scan
def multistat_scan(K, C, sign=-1, keep=KEEP, chunk=1 << 18):
    """dense_scan's trigram prefilter PLUS three language-agnostic screens, one pass.

    The trigram half is line-for-line `lib_padsweep.dense_scan` (verified identical by
    `--selftest`); the rest is free, because the plaintext matrix P is already built.

    Returns {screen: [(stat, offset)] best-first} for
        tri     English rune-index trigram log10 P/symbol  (THE R17/L6 PREFILTER)
        ioc     decrypt IoC*N over the 24-rune window      (language-agnostic)
        maxc    max unigram count in the window            (language-agnostic)
        ndist   -distinct symbols in the window (negated so 'bigger is better' holds)
    """
    T = L.trigram_model()
    K = np.ascontiguousarray(np.asarray(K, dtype=np.int16))
    C = np.asarray(C[:PLEN], dtype=np.int16)
    n_off = len(K) - PLEN
    if n_off <= 0:
        return {}, 0
    best = {k: (np.full(0, -np.inf, np.float32), np.zeros(0, np.int64))
            for k in ("tri", "ioc", "maxc", "ndist")}
    denom = PLEN * (PLEN - 1)
    for start in range(0, n_off, chunk):
        stop = min(start + chunk, n_off)
        m = stop - start
        Kw = np.lib.stride_tricks.sliding_window_view(K[start:stop + PLEN], PLEN)[:m]
        P = (C[None, :] + sign * Kw) % N
        # --- the R17 prefilter, unchanged -------------------------------------
        sc = np.zeros(m, dtype=np.float32)
        for j in range(2, PLEN):
            sc += T[P[:, j - 2], P[:, j - 1], P[:, j]]
        sc /= (PLEN - 2)
        # --- language-agnostic screens, from one bincount ---------------------
        flat = (P.astype(np.int64) + N * np.arange(m, dtype=np.int64)[:, None]).ravel()
        cnt = np.bincount(flat, minlength=N * m).reshape(m, N).astype(np.int16)
        ioc = (cnt.astype(np.int32) * (cnt.astype(np.int32) - 1)).sum(1) * (N / denom)
        maxc = cnt.max(1).astype(np.float32)
        ndist = -(cnt > 0).sum(1).astype(np.float32)
        offs = np.arange(start, stop, dtype=np.int64)
        for name, v in (("tri", sc), ("ioc", ioc.astype(np.float32)),
                        ("maxc", maxc), ("ndist", ndist)):
            bs, bo = best[name]
            cs = np.concatenate([bs, v])
            co = np.concatenate([bo, offs])
            k = min(keep, len(cs))
            top = np.argpartition(-cs, k - 1)[:k]
            order = top[np.argsort(-cs[top])]
            best[name] = (cs[order], co[order])
        del P, cnt, flat
    return {k: list(zip(v[0].tolist(), v[1].tolist())) for k, v in best.items()}, n_off


def _rank(hits, o_true):
    return next((i for i, (_s, o) in enumerate(hits) if int(o) == o_true), None)


# --------------------------------------------------------------------------- workers
def _init(pairs, panels):
    import lib_padsweep as _L
    _L.trigram_model()
    _G["pairs"] = pairs
    _G["panels"] = panels
    _G["pads"] = {}


def _pad(name):
    if name not in _G["pads"]:
        a = np.fromfile(os.path.join(DATA, "iso", name), dtype=np.uint8)
        _G["pads"][name] = (a.astype(np.int16) % N)      # mod29, the modal builder
    return _G["pads"][name]


def _unit(job):
    reg, ti = job
    pad_name, o_true, pstart = _G["pairs"][ti]
    K = _pad(pad_name)
    panel = _G["panels"][reg]
    P = panel[pstart:pstart + PLANT_LEN]
    Kl = [int(x) for x in K]
    C, skips, _used = sk.encipher_keyskip(P, Kl[o_true:], sign=-1, supp=SUPP,
                                          seed=SEED0 + ti)
    hits, n_off = multistat_scan(K, C, sign=-1, keep=KEEP)
    row = {"register": reg, "trial": ti, "pad": pad_name, "o_true": o_true,
           "n_offsets": int(n_off), "skips_planted": int(sum(skips))}
    for name, h in hits.items():
        r = _rank(h, o_true)
        row[f"rank_{name}"] = r
        row[f"surv_{name}"] = r is not None
        row[f"surv40_{name}"] = (r is not None and r < 40)
    return row


# --------------------------------------------------------------------------- main
def build_pairs(pad_names, n, panels):
    rng = random.Random(SEED0)
    pairs = []
    minlen = min(len(v) for v in panels.values())
    for t in range(n):
        pn = pad_names[t % len(pad_names)]
        # 10,000,000 bytes -> 10,000,000 mod29 symbols; leave room for the escalation span
        o = rng.randrange(1000, 10_000_000 - PLANT_LEN * 10 - 64)
        ps = rng.randrange(0, minlen - PLANT_LEN - 1)
        pairs.append((pn, o, ps))
    return pairs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nproc", type=int, default=6)
    ap.add_argument("--ntrials", type=int, default=30)
    ap.add_argument("--registers", default=",".join(REGISTERS))
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    t0 = time.time()

    if a.selftest:
        # multistat_scan's trigram half must equal lib_padsweep.dense_scan EXACTLY
        K = (np.fromfile(os.path.join(DATA, "iso", "BITS.01"), dtype=np.uint8,
                         count=2_000_000).astype(np.int16) % N)
        Cq = [int(x) for x in L.nc.unsolved()[:PLEN]]
        h1, _ = multistat_scan(K, Cq, sign=-1, keep=50)
        h2 = L.dense_scan(K, Cq, sign=-1, keep=50)
        d = max(abs(x[0] - y[0]) for x, y in zip(h1["tri"], h2))
        same = [int(x[1]) for x in h1["tri"]] == [int(y[1]) for y in h2]
        print(f"[selftest] offsets identical={same}  max|dscore|={d:.3e}  "
              f"({time.time()-t0:.1f}s for 2e6 offsets x 4 screens)")
        assert same and d < 1e-6, "multistat_scan diverged from lib_padsweep.dense_scan"
        return 0

    # --- the data gate: only PASS pads are used ----------------------------------
    v = json.load(open(os.path.join(OUT, "out_verify.json")))
    assert v["all_gates_pass"], "hash gates did not pass - refusing to plant in these bytes"
    pad_names = v["random_data_pads"]

    # --- the register panel: L7-A's own builder, imported ------------------------
    import a1_scorer_language as A1
    panels = {k: vv for k, vv in A1.build_panels().items()}

    regs = [r for r in a.registers.split(",") if r in panels]
    pairs = build_pairs(pad_names, a.ntrials, {k: panels[k] for k in regs})

    if a.selftest:
        # multistat_scan's trigram half must equal lib_padsweep.dense_scan EXACTLY
        K = (np.fromfile(os.path.join(DATA, "iso", pad_names[0]), dtype=np.uint8,
                         count=2_000_000).astype(np.int16) % N)
        Cq = [int(x) for x in L.nc.unsolved()[:PLEN]]
        h1, _ = multistat_scan(K, Cq, sign=-1, keep=50)
        h2 = L.dense_scan(K, Cq, sign=-1, keep=50)
        d = max(abs(x[0] - y[0]) for x, y in zip(h1["tri"], h2))
        same = [int(x[1]) for x in h1["tri"]] == [int(y[1]) for y in h2]
        print(f"[selftest] offsets identical={same}  max|dscore|={d:.3e}")
        assert same and d < 1e-6, "multistat_scan diverged from lib_padsweep.dense_scan"
        return 0

    jobs = [(r, t) for r in regs for t in range(a.ntrials)]
    print(f"[C2] {len(jobs)} units ({len(regs)} registers x {a.ntrials} trials) "
          f"nproc={a.nproc}", flush=True)
    rows = []
    from multiprocessing import Pool
    with Pool(a.nproc, initializer=_init, initargs=(pairs, panels)) as pool:
        for k, r in enumerate(pool.imap_unordered(_unit, jobs, chunksize=1)):
            rows.append(r)
            if (k + 1) % 10 == 0 or k == 0:
                print(f"  [C2] {k+1}/{len(jobs)} {time.time()-t0:.0f}s", flush=True)

    # --- summarise ----------------------------------------------------------------
    n_off = rows[0]["n_offsets"]
    p_chance = KEEP / n_off
    summ = {}
    for r in regs:
        rr = [x for x in rows if x["register"] == r]
        s = {"n": len(rr), "n_offsets": n_off}
        for name in ("tri", "ioc", "maxc", "ndist"):
            k = sum(1 for x in rr if x[f"surv_{name}"])
            s[f"survival_{name}"] = k / len(rr)
            s[f"survived_{name}"] = k
            s[f"survival40_{name}"] = sum(1 for x in rr if x[f"surv40_{name}"]) / len(rr)
            rk = [x[f"rank_{name}"] for x in rr if x[f"rank_{name}"] is not None]
            s[f"median_rank_{name}"] = float(np.median(rk)) if rk else None
        summ[r] = s

    eng = max((summ[r]["survival_tri"] for r in regs if r in ENGLISH_ARMS), default=0.0)
    non_eng = {r: summ[r]["survival_tri"] for r in regs
               if r not in ENGLISH_ARMS and r != "RAND"}
    gap = [r for r, v2 in non_eng.items() if v2 <= 0.20]
    if not (0.47 <= eng <= 0.81):
        verdict = "INCONCLUSIVE (English arm did not reproduce L6 Control A survival 0.650)"
    elif gap and eng >= 0.50:
        verdict = "FOUND-GAP"
    else:
        verdict = "NO-GAP" if not gap else "INCONCLUSIVE"

    out = {"lane": "round19/C2", "measures": "prefilter register power on real Marsaglia bytes",
           "instrument": "round17/lib_padsweep.dense_scan (plen=24, keep=1000, sign=-1), "
                         "trigram model trained on kjv/moby/pride/war; plants via "
                         "skipdecode.encipher_keyskip(supp=0.83); panels from "
                         "round18/L7-redteam/a1_scorer_language.build_panels()",
           "builder": "mod29", "plant_len": PLANT_LEN, "keep": KEEP, "plen": PLEN,
           "n_trials": a.ntrials, "paired": True, "pads_used": sorted({p[0] for p in pairs}),
           "n_offsets_per_scan": n_off, "p_chance": p_chance,
           "english_arm_best_survival": eng,
           "registers_at_or_below_0.20": sorted(gap),
           "verdict": verdict, "summary": summ, "rows": rows,
           "wall_s": round(time.time() - t0, 1)}
    with open(os.path.join(OUT, "out_prefilter_register_power.json"), "w") as f:
        json.dump(out, f, indent=1)

    print(f"\n  {'register':<14} {'tri':>6} {'ioc':>6} {'maxc':>6} {'ndist':>6}   "
          f"(survival in top-{KEEP} of {n_off:,} offsets; chance {p_chance:.2e})")
    for r in regs:
        s = summ[r]
        print(f"  {r:<14} {s['survival_tri']:>6.3f} {s['survival_ioc']:>6.3f} "
              f"{s['survival_maxc']:>6.3f} {s['survival_ndist']:>6.3f}")
    print(f"\n[C2] VERDICT: {verdict}   ({out['wall_s']}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
