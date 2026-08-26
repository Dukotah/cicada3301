"""I2 / measurement — G-POWER, G-FP, G-LP1.

Protocol is L7-A's, unchanged (round18/L7-redteam/a1_scorer_language.py):

    plant sha256_ctr(seed=CICADA3301)
      -> encipher_keyskip(supp=0.83)
      -> beam_decode(beam_w=400, max_skip=3) with the CORRECT key
      -> adjudicate the decode's RUNE INDICES

with two additions this lane pre-registered (PREREG.md §2.1, §3):

  * plant windows are drawn from the corpus TEST half only, never from LM training text
    (LP1_REAL uses leave-one-page-out instead, since 1,769 runes cannot be halved);
  * 24 replicates per cell instead of 12, so the 0.90 bar has 1/24 resolution.

The wrong-key null is measured on the REAL LP2 ciphertext — a random window of the 12,956
unsolved runes decoded under a random key — because that is literally what a sweep does.

    python3 power.py --smoke     # PREREG §1 Q5 kill-condition checkpoint (12 reps, L=240)
    python3 power.py --null      # wrong-key null only            -> out_null.json
    python3 power.py             # full grid                      -> out_power.json
"""
import json
import os
import random
import statistics
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
B6 = os.path.join(LP, "analysis", "round10b", "B6-non-english-plaintext")
for _p in (os.path.join(LP, "src"), os.path.join(LP, "benchmark"),
           os.path.join(LP, "analysis", "campaign18_skip"),
           os.path.join(LP, "analysis", "round11"), B6):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import skipdecode as sk                      # noqa: E402
import plant as PL                           # noqa: E402
import detectors as D                        # noqa: E402
import adjudicate as AJ                      # noqa: E402

N = 29
BEAM_W, MAX_SKIP, SUPP = 400, 3, 0.83
SEED0 = 33010
LENGTHS = [120, 240, 400]
NREP = 24
REGISTERS = ["EN_MODERN", "EN_KJV", "LP1_REAL", "LATIN", "OE", "DE", "CY",
             "EN_HALFVOWEL", "EN_NOVOWEL"]
ALPHA_REF = 1e-3          # pre-registered per-decode false-positive rate
LEGACY_BAR = -5.5         # the repo-wide English bar the panel must not regress from


# ------------------------------------------------------------------ test material
def load_test():
    d = np.load(os.path.join(HERE, "models", "testhalves.npz"))
    T = {r: d[r].astype(np.int64) for r in REGISTERS}
    pages = [d[f"LP1PAGE{i}"].astype(np.int64) for i in range(5)]
    return T, pages


def lp1_loo_panels(pan):
    """Panel variants with the LP1_REAL row replaced by each leave-one-page-out model."""
    out = []
    i = pan.registers.index("LP1_REAL")
    for k in range(pan.LP1_LOO.shape[0]):
        M = pan.LMF.copy()
        M[i] = pan.LP1_LOO[k].reshape(-1)
        out.append(M)
    return out


# ------------------------------------------------------------------ one plant trial
def plant_trial(P_src, L, rep, pan, lm_override=None, seed_off=0):
    rng = random.Random(SEED0 + rep * 977 + L + seed_off)
    if len(P_src) < L + 3:
        return None
    start = rng.randrange(0, len(P_src) - L)
    P = [int(v) for v in P_src[start:start + L]]

    need = L * (MAX_SKIP + 1) + 512
    K = PL.make_key("sha256_ctr", length=need, seed=b"CICADA3301")
    C, skips, _ = sk.encipher_keyskip(P, K, sign=-1, supp=SUPP, seed=SEED0 + rep + seed_off)

    bd = sk.beam_decode(C, K, sign=-1, o=0, beam_w=BEAM_W, max_skip=MAX_SKIP)
    dec = bd["plain_idx"]
    rec = sum(1 for a, b in zip(dec, P) if a == b) / len(P)
    res = AJ.adjudicate(dec, pan=pan, lm_override=lm_override)
    res["recovery"] = rec
    res["beam_score"] = bd["score"]
    res["n_skips"] = int(sum(skips))
    return res


# ------------------------------------------------------------------ the wrong-key null
def _wk_chunk(arg):
    L, n, seed = arg
    pan = AJ.panel()
    _pages, stream = D.load_unsolved()
    stream = np.asarray(stream, dtype=np.int64)
    rng = np.random.default_rng(seed)
    need = L * (MAX_SKIP + 1) + 512
    out = []
    for _ in range(n):
        s = int(rng.integers(0, len(stream) - L))
        C = [int(v) for v in stream[s:s + L]]
        K = [int(v) for v in rng.integers(0, N, size=need)]
        bd = sk.beam_decode(C, K, sign=-1, o=0, beam_w=BEAM_W, max_skip=MAX_SKIP)
        out.append(AJ.adjudicate(bd["plain_idx"], pan=pan))
    return out


def _rr_chunk(arg):
    L, n, seed = arg
    pan = AJ.panel()
    rng = np.random.default_rng(seed)
    return [AJ.adjudicate(rng.integers(0, N, size=L), pan=pan) for _ in range(n)]


def _parallel(fn, L, n, seed, nproc=5):
    import multiprocessing as mp
    per = (n + nproc - 1) // nproc
    args = [(L, min(per, n - i * per), seed + 7919 * i) for i in range(nproc)]
    args = [a for a in args if a[1] > 0]
    if nproc <= 1:
        return [r for a in args for r in fn(a)]
    with mp.get_context("fork").Pool(len(args)) as p:
        return [r for chunk in p.map(fn, args) for r in chunk]


def wrongkey_null(pan, L, n, seed=90210, nproc=5):
    """Decode a random window of the REAL LP2 ciphertext under a random key.

    This is exactly the operation a sweep performs on a wrong key, so it is the null the
    thresholds must be set from.  Returns a list of adjudication dicts.
    """
    return _parallel(_wk_chunk, L, n, seed, nproc)


def random_rune_null(pan, L, n, seed=4242, nproc=5):
    """The cheap null: uniform random runes, no beam.  Used for tail extrapolation only if
    it is measured to agree with `wrongkey_null` (PREREG §3 G-FP)."""
    return _parallel(_rr_chunk, L, n, seed, nproc)


# ------------------------------------------------------------------ smoke / kill check
def smoke():
    """PREREG §1 Q5 checkpoint: does a matched, HELD-OUT LM lift EN_NOVOWEL's correct-key
    statistic to z >= +3.0 against its own wrong-key null at L=240?  12 replicates."""
    pan = AJ.panel()
    T, _pages = load_test()
    L, nrep = 240, 12
    print("wrong-key null (200 beam decodes on real LP2, random keys) ...")
    t0 = time.time()
    nullrows = wrongkey_null(pan, L, 200)
    dt = (time.time() - t0) / 200
    print(f"  {dt*1000:.1f} ms per beam decode+adjudicate at L={L}")
    nz = np.array([r["z"] for r in nullrows])
    nmu, nsd = nz.mean(axis=0), nz.std(axis=0, ddof=1)
    npmax = np.array([r["pmax"] for r in nullrows])
    nen = np.array([r["en"] for r in nullrows])
    print(f"  null: en {nen.mean():.3f}+-{nen.std():.3f}   pmax {npmax.mean():.3f}"
          f"+-{npmax.std():.3f}  max {npmax.max():.3f}")

    print(f"\n{'register':14s} {'en':>7s} {'z_own':>7s} {'zwk_own':>8s} {'pmax':>7s} "
          f"{'pcon':>7s} {'rec':>6s}")
    res = {}
    for reg in REGISTERS:
        j = pan.registers.index(reg)
        rows = [plant_trial(T[reg], L, rep, pan) for rep in range(nrep)]
        rows = [r for r in rows if r]
        zown = statistics.median(r["z"][j] for r in rows)
        # standardise against the wrong-key null of the SAME model
        zwk = (zown - nmu[j]) / nsd[j]
        res[reg] = {"en": statistics.median(r["en"] for r in rows),
                    "z_own_model": zown, "z_own_vs_wrongkey_null": zwk,
                    "pmax": statistics.median(r["pmax"] for r in rows),
                    "pcon": statistics.median(r["pcon"] for r in rows),
                    "recovery": statistics.median(r["recovery"] for r in rows)}
        r_ = res[reg]
        print(f"{reg:14s} {r_['en']:7.3f} {zown:7.2f} {zwk:8.2f} {r_['pmax']:7.2f} "
              f"{r_['pcon']:7.2f} {r_['recovery']:6.1%}")

    kill = res["EN_NOVOWEL"]["z_own_vs_wrongkey_null"]
    print(f"\nPREREG Q5 kill condition: EN_NOVOWEL z vs wrong-key null = {kill:.2f} "
          f"(need >= +3.0)  ->  {'PROCEED' if kill >= 3.0 else 'KILLED for this register'}")
    json.dump({"lane": "round19/I2/smoke", "L": L, "nrep": nrep,
               "ms_per_beam_decode": dt * 1000, "rows": res,
               "kill_condition": {"stat": "EN_NOVOWEL median z vs wrong-key null at L=240",
                                  "value": kill, "threshold": 3.0,
                                  "verdict": "PROCEED" if kill >= 3.0 else "KILLED"}},
              open(os.path.join(HERE, "out_smoke.json"), "w"), indent=1)
    print("wrote out_smoke.json")


# ------------------------------------------------------------------ nulls (G-FP part 1)
def gpd_quantile(v, alpha, pu=0.05):
    """Extreme-value estimate of the (1-alpha) quantile.

    `benchmark/null.py` states this repo's own hard-won lesson: calibrate an extreme-value
    bar from EXTREME VALUES, never from the bulk sd.  Fit a Generalized Pareto (method of
    moments) to the exceedances over the (1-pu) quantile and extrapolate.
    """
    v = np.sort(np.asarray(v, dtype=float))
    u = float(np.quantile(v, 1 - pu))
    y = v[v > u] - u
    if len(y) < 30:
        return float("nan")
    m, s2 = float(y.mean()), float(y.var(ddof=1))
    if s2 <= 0:
        return float("nan")
    xi = 0.5 * (1.0 - m * m / s2)
    sig = 0.5 * m * (m * m / s2 + 1.0)
    r = alpha / pu
    if abs(xi) < 1e-6:
        return u + sig * (-np.log(r))
    return float(u + sig / xi * (r ** (-xi) - 1.0))


NULLPATH = os.path.join(HERE, "out_null.json")


def run_nulls(n240=20000, n_other=8000, n_rand=200000, nproc=4):
    """Measure the wrong-key null at each length.  CHECKPOINTED: `out_null.json` is
    rewritten after every length, and an existing length is not recomputed, so a killed
    run resumes instead of starting over."""
    pan = AJ.panel()
    if os.path.exists(NULLPATH):
        out = json.load(open(NULLPATH, encoding="utf-8"))
        print("resuming; already have lengths:", sorted(out["lengths"]))
    else:
        out = {"lane": "round19/I2/null", "alpha_ref": ALPHA_REF,
               "beam": {"beam_w": BEAM_W, "max_skip": MAX_SKIP},
               "wrongkey_null_source": (
                   "random L-window of the real 12,956-rune unsolved LP2 stream, decoded "
                   "under a uniform random 29-ary key by the same beam — literally what a "
                   "sweep does"),
               "lengths": {}}
    for L in LENGTHS:
        if str(L) in out["lengths"]:
            continue
        n = n240 if L == 240 else n_other
        t0 = time.time()
        wk = wrongkey_null(pan, L, n, nproc=nproc)
        tw = time.time() - t0
        rr = random_rune_null(pan, L, n_rand, nproc=nproc)
        out["lengths"][str(L)] = summarise_null(pan, wk, rr, L, tw)
        s = out["lengths"][str(L)]
        print(f"L={L:3d}  wrongkey n={n} ({tw:.0f}s)  en {s['wrongkey']['en']['mean']:.3f} "
              f"pmax {s['wrongkey']['pmax']['mean']:.3f}  |  rand n={n_rand} "
              f"en {s['random_rune']['en']['mean']:.3f} pmax {s['random_rune']['pmax']['mean']:.3f}"
              f"  k_eff={s['k_eff']:.2f}", flush=True)
        json.dump(out, open(NULLPATH, "w"), indent=1)
        print(f"  checkpointed out_null.json ({len(out['lengths'])}/{len(LENGTHS)} lengths)",
              flush=True)
    print("wrote out_null.json")
    return out


def _dist(v):
    v = np.asarray(v, dtype=float)
    return {"n": int(len(v)), "mean": float(v.mean()), "sd": float(v.std(ddof=1)),
            "q": {str(q): float(np.quantile(v, q))
                  for q in (0.5, 0.9, 0.99, 0.999, 0.9999, 1.0)}}


def summarise_null(pan, wk, rr, L, secs):
    out = {"L": L, "seconds_for_wrongkey": round(secs, 1)}
    for tag, rows in (("wrongkey", wk), ("random_rune", rr)):
        z = np.array([r["z"] for r in rows])
        d = {"en": _dist([r["en"] for r in rows]),
             "pmax": _dist([r["pmax"] for r in rows]),
             "pmax_ne": _dist([r["pmax_ne"] for r in rows]),
             "pcon": _dist([r["pcon"] for r in rows]),
             "ioc": _dist([r["ioc"] for r in rows]),
             "mds": _dist([r["mds"] for r in rows]),
             "h2": _dist([r["h2"] for r in rows]),
             "zl": _dist([r["zl"] for r in rows]),
             "z_per_register": {reg: _dist(z[:, i]) for i, reg in enumerate(pan.registers)},
             "z_corr_vs_EN": {reg: float(np.corrcoef(z[:, pan.i_en], z[:, i])[0, 1])
                              for i, reg in enumerate(pan.registers)}}
        out[tag] = d

    # --- how much does max-over-9-correlated-models inflate the null? ------------
    zr = np.array([r["z"] for r in rr])
    pm = zr.max(axis=1)
    zen = zr[:, pan.i_en]
    keff = {}
    for q in (0.99, 0.999, 0.9999):
        t = float(np.quantile(pm, q))
        p_en = float((zen > t).mean())
        keff[str(q)] = {"t": t, "P_pmax_gt_t": 1 - q, "P_zEN_gt_t": p_en,
                        "k_eff": (1 - q) / p_en if p_en > 0 else float("inf")}
    out["k_eff_by_quantile"] = keff
    out["k_eff"] = keff["0.999"]["k_eff"] if np.isfinite(keff["0.999"]["k_eff"]) else \
        keff["0.99"]["k_eff"]

    # --- thresholds at the pre-registered matched FP rate -------------------------
    q = 1.0 - ALPHA_REF
    th = {"alpha_ref": ALPHA_REF, "legacy_bar": LEGACY_BAR,
          "legacy_bar_fp_rate_wrongkey": float(np.mean([r["en"] >= LEGACY_BAR for r in wk])),
          "legacy_bar_fp_rate_random": float(np.mean([r["en"] >= LEGACY_BAR for r in rr]))}
    for stat in ("en", "pmax", "pcon", "pmax_ne"):
        vw = [r[stat] for r in wk]
        vr = [r[stat] for r in rr]
        emp_w = float(np.quantile(vw, q))
        gpd_w = gpd_quantile(vw, ALPHA_REF)
        th[f"{stat}_wrongkey_empirical"] = emp_w
        th[f"{stat}_wrongkey_gpd"] = gpd_w
        th[f"{stat}_random_empirical"] = float(np.quantile(vr, q))
        th[f"{stat}_random_gpd"] = gpd_quantile(vr, ALPHA_REF)
        # OPERATIVE bar: the most conservative of the wrong-key empirical and GPD
        # estimates.  Conservative = higher = harder to clear, so this can only cost
        # power, never buy it.
        cands = [x for x in (emp_w, gpd_w) if x == x]
        th[f"t_{stat}"] = float(max(cands)) if cands else emp_w
    th["t_EN_wrongkey"] = th["t_en"]        # aliases used by run_power
    th["t_pmax_wrongkey"] = th["t_pmax"]
    th["t_pcon_wrongkey"] = th["t_pcon"]
    out["thresholds_at_alpha_ref"] = th
    return out


# ------------------------------------------------------------------ full power grid
def run_power(nulls=None):
    pan = AJ.panel()
    T, pages = load_test()
    loo = lp1_loo_panels(pan)
    if nulls is None:
        p = os.path.join(HERE, "out_null.json")
        if os.path.exists(p):
            nulls = json.load(open(p, encoding="utf-8"))
        else:
            # The null run may still be in flight.  Every per-replicate row is stored, and
            # gates.py RECOMPUTES all powers from those rows against the final measured
            # thresholds, so the two runs are independent.  Provisional bars only affect
            # the console printout.
            print("out_null.json not present — using PROVISIONAL bars; gates.py will "
                  "recompute every power from the stored rows.")
            nulls = {"lengths": {str(L): {"thresholds_at_alpha_ref": {
                "t_en": -6.5, "t_pmax": 5.0, "t_pcon": 5.0,
                "t_EN_wrongkey": -6.5, "t_pmax_wrongkey": 5.0,
                "t_pcon_wrongkey": 5.0, "PROVISIONAL": True}} for L in LENGTHS}}
    powpath = os.path.join(HERE, "out_power.json")

    out = {"lane": "round19/I2/power",
           "protocol": ("L7-A verbatim: plant sha256_ctr(CICADA3301) -> "
                        "encipher_keyskip(supp=0.83) -> beam_decode(400,3) with the CORRECT "
                        "key -> adjudicate on rune indices; plant windows from held-out "
                        "corpus TEST halves (LP1_REAL: leave-one-page-out)"),
           "nrep": NREP, "lengths": LENGTHS, "registers": REGISTERS,
           "alpha_ref": ALPHA_REF, "legacy_bar": LEGACY_BAR,
           "cells": {}, "rows": []}
    if os.path.exists(powpath):                       # resume a killed run
        prev = json.load(open(powpath, encoding="utf-8"))
        if prev.get("nrep") == NREP:
            out["cells"], out["rows"] = prev.get("cells", {}), prev.get("rows", [])
            out["lp1_heldout_pages"] = prev.get("lp1_heldout_pages", {})
            print("resuming; already have cells:", sorted(out["cells"]))

    for L in LENGTHS:
        th = nulls["lengths"][str(L)]["thresholds_at_alpha_ref"]
        t_en, t_p, t_pc = th["t_EN_wrongkey"], th["t_pmax_wrongkey"], th["t_pcon_wrongkey"]
        print(f"\n--- L={L}   matched-FP bars: en>={t_en:.3f}  pmax>={t_p:.3f}  "
              f"pcon>={t_pc:.3f}   (legacy en>=-5.5)")
        print(f"{'register':14s} {'en':>7s} {'pow_en':>7s} {'pow_lgc':>8s} {'pmax':>7s} "
              f"{'pow_pm':>7s} {'pcon':>7s} {'pow_pc':>7s} {'z_own':>7s} {'rec':>6s}")
        for reg in REGISTERS:
            if f"{reg}|{L}" in out["cells"]:
                continue
            rows = []
            if reg == "LP1_REAL":
                usable = [i for i, p in enumerate(pages) if len(p) >= L + 3]
                if not usable:
                    continue
                for rep in range(NREP):
                    i = usable[rep % len(usable)]
                    r = plant_trial(pages[i], L, rep, pan, lm_override=loo[i],
                                    seed_off=i * 131)
                    if r:
                        r["fold"] = i
                        rows.append(r)
                out.setdefault("lp1_heldout_pages", {})[str(L)] = usable
            else:
                for rep in range(NREP):
                    r = plant_trial(T[reg], L, rep, pan)
                    if r:
                        rows.append(r)
            if not rows:
                continue
            j = pan.registers.index(reg)
            for r in rows:
                r["register"], r["L"] = reg, L
                out["rows"].append({k: r[k] for k in
                                    ("register", "L", "en", "pmax", "preg", "pmax_ne",
                                     "pcon", "pcreg", "ioc", "mds", "h2", "zl",
                                     "recovery", "z")})
            cell = {
                "register": reg, "L": L, "n": len(rows),
                "median_en": statistics.median(r["en"] for r in rows),
                "median_recovery": statistics.median(r["recovery"] for r in rows),
                "median_pmax": statistics.median(r["pmax"] for r in rows),
                "median_pcon": statistics.median(r["pcon"] for r in rows),
                "median_z_own_model": statistics.median(r["z"][j] for r in rows),
                "median_ioc": statistics.median(r["ioc"] for r in rows),
                "median_mds": statistics.median(r["mds"] for r in rows),
                "median_h2": statistics.median(r["h2"] for r in rows),
                "median_zl": statistics.median(r["zl"] for r in rows),
                "argmax_register_mode": statistics.mode(
                    [pan.registers[r["preg"]] for r in rows]),
                "power_legacy_bar": sum(r["en"] >= LEGACY_BAR for r in rows) / len(rows),
                "power_en_matchedFP": sum(r["en"] >= t_en for r in rows) / len(rows),
                "power_pmax_matchedFP": sum(r["pmax"] >= t_p for r in rows) / len(rows),
                "power_pcon_matchedFP": sum(r["pcon"] >= t_pc for r in rows) / len(rows),
                "power_panel_or": sum((r["pmax"] >= t_p) or (r["en"] >= t_en)
                                      for r in rows) / len(rows),
                "bars": {"t_en": t_en, "t_pmax": t_p, "t_pcon": t_pc},
            }
            out["cells"][f"{reg}|{L}"] = cell
            print(f"{reg:14s} {cell['median_en']:7.3f} {cell['power_en_matchedFP']:7.2f} "
                  f"{cell['power_legacy_bar']:8.2f} {cell['median_pmax']:7.2f} "
                  f"{cell['power_pmax_matchedFP']:7.2f} {cell['median_pcon']:7.2f} "
                  f"{cell['power_pcon_matchedFP']:7.2f} "
                  f"{cell['median_z_own_model']:7.2f} {cell['median_recovery']:6.1%}",
                  flush=True)
            json.dump(out, open(powpath, "w"), indent=1)

    json.dump(out, open(powpath, "w"), indent=1)
    print("\nwrote out_power.json")
    return out


if __name__ == "__main__":
    if "--smoke" in sys.argv:
        smoke()
    elif "--null" in sys.argv:
        run_nulls()
    elif "--power" in sys.argv:
        run_power()
    else:
        run_nulls()
        run_power()
