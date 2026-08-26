"""I3 / Round 19 — the three plants the PREREG requires, run before any cell is believed.

A calibration lane's "hit" is a MIS-CALIBRATION, so its recognizer has to be built and
planted before the search, exactly like any other lane (doctrine Q1).

    P1  synthetic-Gumbel plant   -- hand the fitter a distribution with KNOWN (mu, beta) and
                                    require it back. A fitter that cannot recover what it was
                                    handed makes every cell downstream meaningless.
    P2  mis-calibrated-bar plant -- hand G-CAL a bar that is KNOWN to be wrong (the legacy
                                    L=120 constants applied at L=31, which L7-C.4 measured as
                                    ~2x too tight in beta) and require G-CAL to FAIL. A gate
                                    that can only pass is decoration.
    P3  correct-key plant        -- G-RECOVER. Plant a known key over each plaintext register,
                                    decode with that key, adjudicate, and read the power at
                                    the NEW bars. If the correction is so conservative it
                                    kills the power I1 and I2 just bought, that is the finding.

    python3 plants.py            # all three -> out_plants.json
"""
import json
import math
import os
import random
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
R19 = os.path.abspath(os.path.join(HERE, ".."))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
for _p in (os.path.join(R19, "I1"), os.path.join(R19, "I2"),
           os.path.join(LP, "src"), os.path.join(LP, "benchmark"),
           os.path.join(LP, "analysis", "campaign18_skip"),
           os.path.join(LP, "analysis", "round10b", "B6-non-english-plaintext"),
           os.path.join(LP, "analysis", "round18", "L7-redteam")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import nullcurve19 as NC          # noqa: E402
import vecbeam as V               # noqa: E402

N = 29
SUPP = 0.83
SEED0 = 190319


# ---------------------------------------------------------------------------- P1
def p1_synthetic_gumbel(mu=-7.25, beta=0.0725, M=1_000_000, seed=3301):
    """Can the fitter recover a Gumbel it was handed? PREREG: |dmu| <= 0.02, |dbeta|/beta <= 5 %."""
    from scipy import stats
    v = stats.gumbel_r.rvs(loc=mu, scale=beta, size=M,
                           random_state=np.random.default_rng(seed))
    f = NC.fit_cell(v)
    dmu = f["mu"] - mu
    dbeta = (f["beta"] - beta) / beta
    g = NC.gcal(v, f["mu"], f["beta"], alpha=0.01)
    return {"truth": {"mu": mu, "beta": beta}, "M": M,
            "fitted_mu": f["mu"], "fitted_beta": f["beta"],
            "d_mu": dmu, "rel_d_beta": dbeta,
            "bulk_sd_beta": f["bulk_sd_beta"],
            "gev_xi": f["gev"]["xi"] if f["gev"] else None,
            "gev_xi_ci95": f["gev"]["xi_ci95"] if f["gev"] else None,
            "gcal_on_own_fit": g,
            "passed": bool(abs(dmu) <= 0.02 and abs(dbeta) <= 0.05 and g["passed"]),
            "why": "a fitter that cannot recover a distribution it was handed is not a fitter"}


# ---------------------------------------------------------------------------- P2
def p2_miscalibrated_bar(cell_key="EN_QUAD|keyskip1|L31"):
    """Feed G-CAL a bar known to be wrong and require it to FAIL.

    The wrong bar: `benchmark/null.py`'s L~120 constants (mu=-7.2517, beta=0.0725) used at
    L=31, which is the substitution L7-C.4 measured as the R17 error. If G-CAL passes this,
    G-CAL cannot detect a mis-calibration and every PASS it reports is worthless.
    """
    c = NC.calib()["cells"].get(cell_key)
    if c is None:
        return {"skipped": "cell not calibrated yet", "cell": cell_key}
    bm = c["block_maxima"].get("100")
    if not bm:
        return {"skipped": "no block maxima stored", "cell": cell_key}
    bm = np.asarray(bm)
    rows = {}
    for name, (mu, beta) in {
            "legacy_L120_constants_applied_at_L31": (NC.DEFAULT_MU, NC.DEFAULT_BETA),
            "this_lane_measured_cell": (c["mu"], c["beta"])}.items():
        bar = NC._fw(100, mu, beta, 0.01)
        p = float((bm > bar).mean())
        rows[name] = {"mu": mu, "beta": beta, "bar_at_n100_a01": bar,
                      "empirical_exceedance": p, "nominal": 0.01,
                      "ratio": p / 0.01, "within_20pct": bool(abs(p / 0.01 - 1) <= 0.20)}
    wrong = rows["legacy_L120_constants_applied_at_L31"]
    right = rows["this_lane_measured_cell"]
    return {"cell": cell_key, "n_block_maxima": int(len(bm)), "rows": rows,
            "passed": bool((not wrong["within_20pct"]) and right["within_20pct"]),
            "why": ("G-CAL must reject a bar known to be wrong and accept the measured one; "
                    "otherwise it is decoration")}


# ---------------------------------------------------------------------------- P3
def _panels():
    from a1_scorer_language import build_panels
    return build_panels()


def p3_recover(L=120, nrep=12, presets=("exact", "drift"), n_trials_bar=10 ** 6,
               alpha=NC.ALPHA_ROUND19):
    """G-RECOVER. Plant the correct key over each register; read power at the NEW bars."""
    import skipdecode as sk
    import plant as PL
    import adjudicate as AD
    import driftbeam as DB

    panels = _panels()
    K = PL.make_key("sha256_ctr", length=L * 12 + 1024, seed=b"CICADA3301")
    rows = []
    for reg, stream in panels.items():
        if len(stream) < L + 32:
            continue
        for rep in range(nrep):
            rng = random.Random(SEED0 + rep * 977 + L)
            s = rng.randrange(0, len(stream) - L - 1)
            P = list(stream[s:s + L])
            C, skips, _ = sk.encipher_keyskip(P, K, sign=-1, supp=SUPP, seed=SEED0 + rep)
            WK = [(i * 7 + 13) % N for i in range(len(K))]
            for preset in presets:
                for arm, key in (("correct", K), ("wrong", WK)):
                    d = DB.beam_decode(C, key, sign=-1, o=0, beam_w=400,
                                       **DB.PRESETS[preset])
                    a = AD.adjudicate(d["plain_idx"], translit=d["translit"])
                    rec = sum(1 for x, y in zip(d["plain_idx"], P) if x == y) / len(P)
                    rows.append({"register": reg, "rep": rep, "preset": preset, "arm": arm,
                                 "L": L, "en": a["en"], "pmax": a["pmax"],
                                 "pmax_ne": a["pmax_ne"], "pcon": a["pcon"],
                                 "preg": a["preg"], "recovery": rec,
                                 "ioc": a["ioc"], "mds": a["mds"]})
    return rows


def p3_power(rows, n_trials_bar=10 ** 6, alpha=NC.ALPHA_ROUND19):
    """Turn P3's rows into a power table against the newly calibrated bars."""
    cells = NC.calib()["cells"]
    out = {}
    for preset in sorted({r["preset"] for r in rows}):
        tag = f"driftbeam.{preset}+I2" if preset != "exact" else "vecbeam.keyskip1+I2"
        bars = {}
        for stat in ("en", "pmax", "pmax_ne", "pcon"):
            for cand in (f"I19:driftbeam.{preset}+I2|{stat}|L120",
                         f"I19:vecbeam.keyskip1+I2|{stat}|L120"):
                c = cells.get(cand)
                if c is None:
                    continue
                if preset == "exact" and "driftbeam" in cand:
                    continue
                bars[stat] = {"cell": cand,
                              "bar": NC._fw(n_trials_bar, c["mu"], c["beta"], alpha),
                              "bar_escalate": NC._fw(n_trials_bar, c["mu"], c["beta"],
                                                     NC.ALPHA_ESCALATE),
                              "mu": c["mu"], "beta": c["beta"], "M": c["M"],
                              "status": c["status"]}
                break
        tbl = {}
        for reg in sorted({r["register"] for r in rows}):
            sub = [r for r in rows if r["preset"] == preset and r["register"] == reg
                   and r["arm"] == "correct"]
            wsub = [r for r in rows if r["preset"] == preset and r["register"] == reg
                    and r["arm"] == "wrong"]
            if not sub:
                continue
            e = {"n_rep": len(sub),
                 "median_recovery": float(np.median([r["recovery"] for r in sub]))}
            for stat, b in bars.items():
                v = np.array([r[stat] for r in sub])
                w = np.array([r[stat] for r in wsub]) if wsub else np.array([])
                e[stat] = {
                    "median_correct": float(np.median(v)),
                    "median_wrong": float(np.median(w)) if len(w) else None,
                    "power_new_claim_bar": float((v >= b["bar"]).mean()),
                    "power_new_escalate_bar": float((v >= b["bar_escalate"]).mean()),
                    "bar": b["bar"], "bar_escalate": b["bar_escalate"]}
            # the OLD instrument's power, for the tradeoff statement
            v = np.array([r["en"] for r in sub])
            e["power_old_fixed_-5.5_bar"] = float((v >= -5.5).mean())
            e["power_old_threshold_for_1e6"] = float(
                (v >= NC.threshold_for(n_trials_bar)).mean())
            tbl[reg] = e
        out[preset] = {"bars": bars, "by_register": tbl, "instrument": tag}
    return out


def main():
    res = {"generated": __import__("time").strftime("%Y-%m-%dT%H:%M:%S")}
    print("P1 synthetic-Gumbel plant ...", flush=True)
    res["P1"] = p1_synthetic_gumbel()
    print(f"   fitted mu={res['P1']['fitted_mu']:.4f} beta={res['P1']['fitted_beta']:.5f} "
          f"-> {'PASS' if res['P1']['passed'] else 'FAIL'}")
    print("P2 mis-calibrated-bar plant ...", flush=True)
    res["P2"] = p2_miscalibrated_bar()
    print(f"   -> {res['P2'].get('passed')}")
    print("P3 correct-key plant (G-RECOVER) ...", flush=True)
    rows = p3_recover()
    res["P3_rows"] = rows
    res["P3_power"] = p3_power(rows)
    json.dump(res, open(os.path.join(HERE, "out_plants.json"), "w", encoding="utf-8"),
              indent=1, default=float)
    print("-> out_plants.json")


if __name__ == "__main__":
    main()
