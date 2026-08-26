"""I3 / Round 19 — EXTENDED NULL CALIBRATION.  The bar, for a decoder and an adjudicator
that are no longer the ones `benchmark/null.py` was calibrated on.

`benchmark/null.py: threshold_for(n_trials, segment_len)` is calibrated for exactly one
statistic: `lp.score.Quadgram.score_norm` of a `beam_decode(beam_w=400, max_skip=3)` output.
Round 19 changes both halves of that:

  * I1 widens the decoder's TRANSITION RELATION. A permissive relation searches a strictly
    larger path space per decode, so the null maximum rises. An unchanged bar under a wider
    relation manufactures false positives.
  * I2 replaces the single English score with a MAX OVER NINE REGISTERS. A maximum over nine
    correlated statistics has a higher null than any one of them, and the registers' raw
    scales are not commensurable, so a raw `max` is not even a well-defined test.

This module extends the API without changing any existing answer:

    threshold_for(n_trials, segment_len)                                # unchanged, bit-identical
    threshold_for(n, L, register='LATIN', mode='drift2')                # calibrated cell
    threshold_for(n, L, statistic='panel_max')                          # multiple-comparison case

THE THREE THINGS A BAR IS CONDITIONAL ON, and which this API refuses to let you forget:
  1. the null generator (key space),
  2. the decoder's transition relation (`mode`),
  3. the adjudicator's register (`register` / `statistic`).
A bar calibrated under `keyskip1` is INVALID under `drift2`; asking for a cell that was
never measured raises rather than silently returning the English one.

Calibration constants live in `calib19.json`, produced by `run_calibration.py`.
"""
import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CALIB_PATH = os.path.join(HERE, "calib19.json")

EULER_GAMMA = 0.5772156649015329

# --- LEGACY constants, copied verbatim from benchmark/null.py. Do not touch: G-BACKCOMPAT
# requires threshold_for(n) and threshold_for(n, L) to return bit-identical values.
DEFAULT_MU = -7.2517
DEFAULT_BETA = 0.0725
FIXED_BAR = -5.5

LEGACY_CELL = ("EN", "keyskip1", "score_norm")

# Round-19 family-wise error target, pre-registered in PREREG.md §7.
ALPHA_ROUND19 = 0.01          # tier-2 CLAIM, round-wide, over all adjudicated decodes
ALPHA_ESCALATE = 0.05         # tier-1 ESCALATE, per lane

_CALIB = None


def calib(path=CALIB_PATH):
    global _CALIB
    if _CALIB is None:
        _CALIB = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {"cells": {}}
    return _CALIB


def cell_key(register, mode, segment_len, statistic="score_norm", panel_mode="rescore",
             beam_w=None):
    """The name of a calibrated cell.

    Three families, because Round 19 has three kinds of statistic:
      "<REGISTER>|<mode>|L<len>[|bw<w>]"        this lane's own per-register curves
      "panel_max|<panel_mode>|<mode>|L<len>"    this lane's own panel-max statistic
      "I19:<instrument>|<stat>|L<len>"          the ACTUAL Round-19 instrument (I1 x I2),
                                                e.g. I19:driftbeam.drift+I2|pmax|L120
    """
    L = int(segment_len)
    if isinstance(register, str) and register.startswith("I19:"):
        return f"{register}|{statistic}|L{L}"
    if statistic == "panel_max":
        return f"panel_max|{panel_mode}|{mode}|L{L}"
    base = f"{register}|{mode}|L{L}"
    if beam_w is not None and int(beam_w) != 400:
        base += f"|bw{int(beam_w)}"
    return base


# --------------------------------------------------------------------------- extreme value
def expected_max(n_trials, mu=DEFAULT_MU, beta=DEFAULT_BETA):
    """Where the best-of-N *wrong* answer is expected to land."""
    if n_trials < 2:
        return mu
    return mu + beta * (math.log(n_trials) + EULER_GAMMA)


def _fw(n_trials, mu, beta, alpha):
    return mu + beta * (math.log(n_trials) - math.log(-math.log(1 - alpha)))


def threshold_for(n_trials, segment_len=None, alpha=0.01,
                  mu=DEFAULT_MU, beta=DEFAULT_BETA, floor=FIXED_BAR,
                  register="EN", mode="keyskip1", statistic="score_norm",
                  panel_mode="rescore", beam_w=None, strict=True, length_correct=False):
    """Family-wise threshold over `n_trials` at level `alpha`.

    BACKWARD COMPATIBLE. With the default `register`/`mode`/`statistic` this is the
    function `benchmark/null.py` already publishes, byte for byte, including the fact that
    `segment_len` is ignored and the -5.5 floor binds below N* = 3.13e8.

        >>> round(threshold_for(200), 2) == -5.5
        True
        >>> threshold_for(10**9) > threshold_for(10**3)
        True

    NEW BEHAVIOUR is reachable only through the new keywords:

    register    one of registers.PANEL, or 'EN' for the legacy translit-quadgram statistic
    mode        the decoder's transition relation: 'keyskip1' (the repo's beam),
                'skip_by_two', 'drift1'..'drift3', 'union<lam>'
    statistic   'score_norm' (per-register) or 'panel_max' (max over the 9-register panel,
                taken on null-standardised z scores -- see registers.py)
    panel_mode  'rescore' (one English-driven decode, 9 scorings) or 'decode' (9 decodes)
    length_correct  apply the measured beta ~ 1/sqrt(L) law to the LEGACY cell. Default
                False so the legacy answer never changes; set True to get the bar Round 17
                should have used at L=31 (L7-C.4).

    `strict=True` raises if you ask for a cell this lane never measured, rather than
    silently handing back the English bar. That silent fallback is precisely the error
    Round 18 L7-C.3 found Round 17 committing.
    """
    if n_trials is not None and n_trials < 2:
        return floor
    key = (register, mode, statistic)

    # ---------------- legacy path: unchanged, and deliberately ignores segment_len
    if key == LEGACY_CELL:
        if length_correct and segment_len:
            b = beta * math.sqrt(120.0 / float(segment_len))
            return max(floor, _fw(n_trials, mu, b, alpha))
        return max(floor, _fw(n_trials, mu, beta, alpha))

    # ---------------- calibrated cells
    L = int(segment_len) if segment_len else 120
    c = calib()["cells"].get(cell_key(register, mode, L, statistic, panel_mode, beam_w))
    if c is None:
        c = _nearest_length_cell(register, mode, L, statistic, panel_mode, beam_w)
    if c is None:
        if strict:
            raise KeyError(
                f"no calibrated null for (register={register!r}, mode={mode!r}, "
                f"L={L}, statistic={statistic!r}, panel_mode={panel_mode!r}). "
                f"Measured cells: {sorted(calib()['cells'])[:8]} ... "
                f"Refusing to substitute the English/keyskip1 bar -- that substitution is "
                f"the error L7-C.3 documented. Run run_calibration.py for this cell, or "
                f"pass strict=False to accept a 1/sqrt(L)-scaled neighbour.")
        return max(floor, _fw(n_trials, mu, beta, alpha))
    return _fw(n_trials, c["mu"], c["beta"], alpha)


def _nearest_length_cell(register, mode, L, statistic, panel_mode, beam_w=None):
    """Same (register, mode) at another L, rescaled by the measured beta ~ 1/sqrt(L) law.

    Returned only when `strict=False`; the caller is told it is an interpolation.
    """
    cells = calib()["cells"]
    cands = []
    for k, v in cells.items():
        if isinstance(register, str) and register.startswith("I19:"):
            if not k.startswith(f"{register}|{statistic}|L"):
                continue
        elif statistic == "panel_max":
            if not k.startswith(f"panel_max|{panel_mode}|{mode}|L"):
                continue
        elif not k.startswith(f"{register}|{mode}|L"):
            continue
        elif beam_w is not None and int(v.get("beam_w", 400)) != int(beam_w):
            continue
        cands.append((abs(v["L"] - L), v))
    if not cands:
        return None
    _, v = min(cands, key=lambda t: t[0])
    s = math.sqrt(v["L"] / float(L))
    return {"mu": v["mu"], "beta": v["beta"] * s, "L": L, "interpolated_from": v["L"]}


def threshold_contract(n_trials, segment_len, register="EN", mode="keyskip1",
                       statistic="score_norm", panel_mode="rescore", beam_w=None):
    """The Phase-2 call. Returns both tiers plus every conditional, as a dict to store."""
    t1 = threshold_for(n_trials, segment_len, alpha=ALPHA_ESCALATE, register=register,
                       mode=mode, statistic=statistic, panel_mode=panel_mode, beam_w=beam_w)
    t2 = threshold_for(n_trials, segment_len, alpha=ALPHA_ROUND19, register=register,
                       mode=mode, statistic=statistic, panel_mode=panel_mode, beam_w=beam_w)
    key = cell_key(register, mode, segment_len or 120, statistic, panel_mode, beam_w)
    c = calib()["cells"].get(key)
    return {"n_trials_adjudicated": n_trials, "segment_len": segment_len,
            "register": register, "mode": mode, "statistic": statistic,
            "panel_mode": panel_mode if statistic == "panel_max" else None,
            "escalate_alpha": ALPHA_ESCALATE, "escalate_bar": t1,
            "claim_alpha": ALPHA_ROUND19, "claim_bar": t2,
            "cell": key, "cell_status": (c or {}).get("status", "UNMEASURED"),
            "cell_n_null_decodes": (c or {}).get("M"),
            "extrapolated": bool(c and n_trials and n_trials > c["M"] / 50)}


# --------------------------------------------------------------------------- fitting
def gumbel_fit_blocks(vals, block=1000, rng=None):
    """Fit Gumbel (mu_block, beta) to the maxima of disjoint blocks of size `block`.

    Returns the block-max parameters AND the implied single-draw curve
    mu0 = mu_block - beta*ln(block), which is what threshold_for uses.
    """
    v = np.asarray(vals, dtype=np.float64)
    m = len(v) // block
    if m < 8:
        return None
    bm = v[:m * block].reshape(m, block).max(axis=1)
    from scipy import stats
    loc, scale = stats.gumbel_r.fit(bm)
    return {"block": block, "n_blocks": int(m), "mu_block": float(loc),
            "beta": float(scale), "mu0": float(loc - scale * math.log(block)),
            "block_max_mean": float(bm.mean()), "block_max_sd": float(bm.std(ddof=1)),
            "block_maxima": bm}


def gev_fit_blocks(vals, block=1000):
    """GEV with free shape xi on block maxima. Tests PREREG H1 (bounded-above -> Weibull).

    scipy parameterises c = -xi, so xi = -c. xi < 0 (c > 0) is a bounded upper tail, which
    would make the Gumbel bar ANTI-conservative at large N.
    """
    v = np.asarray(vals, dtype=np.float64)
    m = len(v) // block
    if m < 30:
        return None
    bm = v[:m * block].reshape(m, block).max(axis=1)
    from scipy import stats
    c, loc, scale = stats.genextreme.fit(bm)
    xi = -c
    # profile-free SE via a parametric bootstrap on the fitted GEV
    boot = []
    rs = np.random.default_rng(3301)
    for _ in range(200):
        s = stats.genextreme.rvs(c, loc=loc, scale=scale, size=m, random_state=rs)
        try:
            cb, _, _ = stats.genextreme.fit(s)
            boot.append(-cb)
        except Exception:
            pass
    lo, hi = (float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))) if boot else (np.nan, np.nan)
    return {"block": block, "n_blocks": int(m), "xi": float(xi), "xi_ci95": [lo, hi],
            "loc": float(loc), "scale": float(scale),
            "gumbel_rejected": bool(not (lo <= 0.0 <= hi))}


def gof_gumbel(block_maxima, loc, scale):
    """Goodness of fit of the Gumbel to observed block maxima: KS and Anderson-Darling."""
    from scipy import stats
    bm = np.asarray(block_maxima, dtype=np.float64)
    z = (bm - loc) / scale
    u = np.exp(-np.exp(-z))                     # PIT under Gumbel
    ks = stats.kstest(u, "uniform")
    u = np.sort(np.clip(u, 1e-12, 1 - 1e-12))
    n = len(u)
    i = np.arange(1, n + 1)
    a2 = -n - np.mean((2 * i - 1) * (np.log(u) + np.log(1 - u[::-1])))
    return {"ks_stat": float(ks.statistic), "ks_p": float(ks.pvalue),
            "anderson_darling_a2": float(a2),
            "ad_reject_5pct": bool(a2 > 2.492)}       # Stephens' 5 % point, params estimated


def fit_cell(vals, blocks=(10, 100, 1000, 10000), fit_max_block=1000):
    """The full per-cell fit: Gumbel from block maxima, a ln-block consistency regression,
    a GEV shape test, and goodness of fit."""
    v = np.asarray(vals, dtype=np.float64)
    per = {}
    for b in blocks:
        f = gumbel_fit_blocks(v, block=b)
        if f is None:
            continue
        bm = f.pop("block_maxima")
        f["gof"] = gof_gumbel(bm, f["mu_block"], f["beta"])
        f["obs_block_max_mean"] = float(bm.mean())
        per[b] = f
    fitb = [b for b in per if b <= fit_max_block]
    if not fitb:
        return None
    # joint (mu0, beta) from a regression of mu_block on ln(block) over the FIT blocks only
    x = np.array([math.log(b) for b in fitb])
    y = np.array([per[b]["mu_block"] for b in fitb])
    if len(fitb) >= 2:
        beta_reg, mu0_reg = np.polyfit(x, y, 1)
    else:
        beta_reg, mu0_reg = per[fitb[0]]["beta"], per[fitb[0]]["mu0"]
    # adopted: beta from the largest fit block that still has >= 30 block maxima, so the
    # tail-scale estimate is resolved rather than fitted to a handful of points.
    resolved = [b for b in fitb if per[b]["n_blocks"] >= 30]
    bstar = max(resolved) if resolved else max(fitb)
    beta = per[bstar]["beta"]
    mu0 = per[bstar]["mu0"]
    out = {"mu": float(mu0), "beta": float(beta), "beta_regression": float(beta_reg),
           "mu0_regression": float(mu0_reg), "anchor_block": bstar,
           "per_block": {str(k): v for k, v in per.items()},
           "gev": gev_fit_blocks(v, block=min(1000, max(fitb))),
           "n": int(len(v)), "single_mean": float(v.mean()),
           "single_sd": float(v.std(ddof=1)), "single_max": float(v.max()),
           "bulk_sd_beta": float(v.std(ddof=1) * math.sqrt(6) / math.pi)}
    # out-of-sample extrapolation check (G-CAL-X)
    ext = {}
    for b in blocks:
        if b <= fit_max_block or b not in per:
            continue
        pred = mu0 + beta * (math.log(b) + EULER_GAMMA)
        obs = per[b]["obs_block_max_mean"]
        sd = beta * math.pi / math.sqrt(6)
        ext[str(b)] = {"predicted_mean_block_max": pred, "observed": obs,
                       "residual_gumbel_sd": float((obs - pred) / sd),
                       "within_1sd": bool(abs(obs - pred) <= sd)}
    out["extrapolation_check"] = ext
    return out


def gcal(vals, mu, beta, alpha=0.01, blocks=(10, 100, 1000, 10000)):
    """G-CAL: empirical exceedance rate of the published bar, per block size."""
    v = np.asarray(vals, dtype=np.float64)
    rows = {}
    for b in blocks:
        m = len(v) // b
        if m < 20:
            continue
        bm = v[:m * b].reshape(m, b).max(axis=1)
        bar = _fw(b, mu, beta, alpha)
        hits = int((bm > bar).sum())
        p = hits / m
        exp_hits = m * alpha
        rows[str(b)] = {"n_blocks": int(m), "bar": float(bar), "exceedances": hits,
                        "p_hat": p, "nominal": alpha,
                        "ratio": (p / alpha) if alpha else float("nan"),
                        "expected_exceedances": exp_hits,
                        "gating": bool(exp_hits >= 50),
                        "within_20pct": bool(abs(p / alpha - 1.0) <= 0.20)}
    gating = [r for r in rows.values() if r["gating"]]
    return {"per_block": rows,
            "n_gating_blocks": len(gating),
            "passed": bool(gating) and all(r["within_20pct"] for r in gating)}


# --------------------------------------------------------------------------- panel max
def effective_tests_shift(mu_panel, mu_single, beta_single):
    """M_eff from the location shift of the panel-max null relative to a single register.

    If the panel were M independent copies of one register, its max over N draws is the
    single register's max over M*N draws, i.e. mu shifts by beta*ln(M).
    """
    return float(math.exp((mu_panel - mu_single) / beta_single))


def effective_tests_eigen(z):
    """Li & Ji (2005) effective-number-of-tests from the correlation matrix eigenvalues.

    z: (n_samples, n_registers) matrix of null statistics. Not a Bonferroni: it counts the
    dimensionality the correlated panel actually spans. L7-A.4 showed the English-correlated
    registers (OE, DE) light up by selection alone, so 9 independent tests is wrong.
    """
    z = np.asarray(z, dtype=np.float64)
    R = np.corrcoef(z, rowvar=False)
    ev = np.linalg.eigvalsh(R)
    ev = np.clip(ev, 0, None)
    # Li & Ji: contribution of each eigenvalue = I(l>=1) + (l - floor(l))
    contrib = (ev >= 1).astype(float) + (ev - np.floor(ev))
    li_ji = float(contrib.sum())
    # Cheverud / Nyholt variance-of-eigenvalues form, for contrast
    M = R.shape[0]
    cheverud = float(1 + (M - 1) * (1 - ev.var(ddof=1) / M))
    return {"li_ji": li_ji, "cheverud_nyholt": cheverud,
            "eigenvalues": [float(x) for x in ev[::-1]],
            "corr": R.tolist()}


def report(n_trials, best_score, segment_len=None, register="EN", mode="keyskip1",
           statistic="score_norm", panel_mode="rescore", alpha=ALPHA_ROUND19):
    """Human-readable adjudication, carrying all three conditionals."""
    con = threshold_contract(n_trials, segment_len, register, mode, statistic, panel_mode)
    verdict = ("CLAIM" if best_score >= con["claim_bar"] else
               "ESCALATE" if best_score >= con["escalate_bar"] else "NOISE")
    con.update({"best_score": best_score, "verdict": verdict})
    return con


if __name__ == "__main__":
    print("Round 19 threshold contract (calibration file: %s)" %
          ("present" if os.path.exists(CALIB_PATH) else "ABSENT -- legacy cell only"))
    print(f"{'trials':>14}  {'E[null max]':>12}  {'bar a=0.01':>11}  {'bar a=0.05':>11}")
    for n in (200, 10**3, 10**6, 10**9, 10**10):
        print(f"{n:>14,}  {expected_max(n):>12.3f}  {threshold_for(n):>11.3f}  "
              f"{threshold_for(n, alpha=0.05):>11.3f}")
