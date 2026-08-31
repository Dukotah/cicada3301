"""P3a — the ONE panel-max direct null every Phase-S lane adjudicates against.

I3's G-PANEL FAILED as pre-registered: the two per-register M_eff estimators disagreed
2.06-2.45x, so no single effective-test count describes the 9-register panel (the registers
are not on commensurable per-draw scales -- I3 RESULTS.md S6). R1's B-i/B-ii recommendation,
which I3 independently reached (S6.2/S6.4), is: STOP correcting for a number of tests and
calibrate a DIRECT null on the panel maximum instead. That is exactly what the
`I19:...+I2|pmax|L120` cells in calib19.json already are -- M wrong-key beam decodes fed
through I1's driftbeam and I2's 9-register adjudicate(), with an extreme-value curve fitted to
the panel-max statistic directly. The curve needs no multiplicity model.

This lane's job (P3a) is to:
  1. LIFT that direct panel-max null into ONE canonical, self-describing bar object
     (`panelmax20.json`) -- the single bar the S-lanes call, per I1 preset, with all three
     conditionals attached, so no S-lane has to re-derive it or accidentally quote -5.5.
  2. Re-run the PLANT-RECOVERY positive control (I3 P3-recover) on the repaired instrument and
     report the measured correct-key power at THIS bar vs a wrong key -- the recognizer that
     proves the bar can tell a planted correct key from noise (doctrine Q1/mechanic 2).
  3. Freshly generate a panel-max null (seed 3301, order-preserving) and run G-CAL on it, an
     independent re-verification that the adopted bar controls its false-positive rate.

Run:
  python3 p3a_panelmax.py build          # emit panelmax20.json from calib19 (instant)
  python3 p3a_panelmax.py plant  [nrep]  # plant-recovery positive control (~2-6 min)
  python3 p3a_panelmax.py gcal   [M]     # fresh panel-max null + G-CAL (~2-4 min)
  python3 p3a_panelmax.py all    [nrep] [M]
"""
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
R19 = os.path.join(LP, "analysis", "round19")
I3 = os.path.join(R19, "I3")
for _p in (I3, os.path.join(R19, "I1"), os.path.join(R19, "I2"),
           os.path.join(LP, "src"), os.path.join(LP, "benchmark"),
           os.path.join(LP, "analysis", "campaign18_skip"),
           os.path.join(LP, "analysis", "round10b", "B6-non-english-plaintext"),
           os.path.join(LP, "analysis", "round18", "L7-redteam")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import nullcurve19 as NC          # noqa: E402

N = 29
ALPHA_CLAIM = NC.ALPHA_ROUND19    # 0.01
ALPHA_ESC = NC.ALPHA_ESCALATE     # 0.05

# The canonical panel-max cell per I1 preset. `pmax` is I2's max-over-9-registers on I2's own
# z scale; these curves are fitted on the DECODER-OUTPUT null (wrong-key beam decodes), not on
# random runes -- so the bar is on the right scale even though I2's nominal z is not (I3 R-I2-2).
PRESET_CELLS = {
    "exact":     "I19:vecbeam.keyskip1+I2|pmax|L120",   # keyskip1 baseline  (CALIBRATED M=1e6)
    "pair":      "I19:driftbeam.pair+I2|pmax|L120",      # keyskip2 exact     (PROVISIONAL M=6e4)
    "exact_ms8": "I19:driftbeam.exact_ms8+I2|pmax|L120", # keyskip1 ms=8      (PROVISIONAL M=6e4)
    "drift":     "I19:driftbeam.drift+I2|pmax|L120",     # drift_rec channel  (PROVISIONAL M=1.5e4)
}
PRESET_DECODER = {
    "exact":     "keyskip1 (repo relation; max_skip=3, max_free=0, lam=0)",
    "pair":      "keyskip2 (pair-constrained; max_skip=8, max_free=0) -- covers L7-B skip_by_two",
    "exact_ms8": "keyskip1 max_skip=8",
    "drift":     "permissive drift_rec (max_skip=40, max_free=2, lam=12, start_slack=2)",
}


# ------------------------------------------------------------------ 1. build the canonical bar
def build(n_round_default=10 ** 6):
    """Emit panelmax20.json: the single bar object, per preset, with conditionals attached."""
    cells = NC.calib()["cells"]
    out = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "lane": "round20/P3 (P3a)",
        "what_this_is": ("THE single panel-max direct null every Round-20 Phase-S lane "
                         "adjudicates against. Resolves I3's G-PANEL failure by adopting a "
                         "directly-fitted panel-max curve (R1 B-i/B-ii) instead of a per-register "
                         "bar with a disputed effective-test count."),
        "claim_statistic": "pmax  (I2 max-over-9-registers, z scale; NEVER en, NEVER -5.5)",
        "alpha_claim": ALPHA_CLAIM, "alpha_escalate": ALPHA_ESC,
        "why_not_keff": ("I3 G-PANEL FAILED: the two per-register M_eff estimators disagree "
                         "2.06-2.45x (I3 S6.2); the panel penalty is not a constant of the panel "
                         "(it shrinks with N: 2.27 z-units at N=1, 1.02 at N=1e6, 0.39 at N=1e9). "
                         "A directly-fitted panel-max null needs no multiplicity model at all."),
        "how_to_call": ("from panelmax20 import panelmax_bar; "
                        "panelmax_bar(preset='exact', n_round_adjudicated=N, alpha=0.01)"),
        "presets": {},
    }
    for preset, key in PRESET_CELLS.items():
        c = cells.get(key)
        if c is None:
            out["presets"][preset] = {"cell": key, "status": "MISSING"}
            continue
        mu, beta, M = c["mu"], c["beta"], c["M"]
        bars = {}
        for n in (10 ** 4, 10 ** 5, 10 ** 6, 10 ** 8):
            bars[str(n)] = {
                "claim_bar": NC._fw(n, mu, beta, ALPHA_CLAIM),
                "escalate_bar": NC._fw(n, mu, beta, ALPHA_ESC)}
        out["presets"][preset] = {
            "cell": key, "mu": mu, "beta": beta, "M": M,
            "status": c.get("status"),
            "decoder_relation": PRESET_DECODER[preset],
            "adjudicator_register": ("I2 9-register panel {EN_MODERN,EN_KJV,LP1_REAL,LATIN,OE,"
                                     "DE,CY,EN_HALFVOWEL,EN_NOVOWEL}; pmax = max z. "
                                     "EN_NOVOWEL recovery 67-81% => a hit there is DETECTION, "
                                     "not readable plaintext (I2)."),
            "null_generator": ("uniform-random rune ciphertext x uniform-random keystream, "
                               "wrong-key beam decode (decoder-output null, NOT random runes); "
                               "validated vs LP2 histogram-shuffle in I3 S1.2"),
            "bars_by_n_round": bars,
        }
    json.dump(out, open(os.path.join(HERE, "panelmax20.json"), "w", encoding="utf-8"),
              indent=1, default=float)
    print("wrote panelmax20.json")
    for preset, d in out["presets"].items():
        if "mu" in d:
            print(f"  {preset:10s} {d['cell']}: mu={d['mu']:.4f} beta={d['beta']:.5f} "
                  f"M={d['M']:>9,} [{d['status']}]  claim@1e6={d['bars_by_n_round']['1000000']['claim_bar']:.3f}")
    return out


# ------------------------------------------------------------------ 2. plant-recovery control
def plant(nrep=8, presets=("exact", "drift"), L=120):
    """The positive control: plant the correct key over each register, read pmax power at THIS
    lane's published bar vs a wrong key. Re-uses I3's validated plant machinery (plants.p3_recover)
    on the repaired instrument. Doctrine mechanic 2: prove recovery before trusting silence."""
    import plants as PL
    t0 = time.time()
    rows = PL.p3_recover(L=L, nrep=nrep, presets=presets)
    el = time.time() - t0
    cells = NC.calib()["cells"]
    # bar at N=1e6 (a representative Phase-S per-lane adjudicated count) for each preset
    result = {"generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "nrep": nrep, "L": L, "seconds": el, "n_trials_bar": 10 ** 6,
              "by_preset": {}}
    for preset in presets:
        cell = PRESET_CELLS[preset]
        c = cells[cell]
        claim = NC._fw(10 ** 6, c["mu"], c["beta"], ALPHA_CLAIM)
        esc = NC._fw(10 ** 6, c["mu"], c["beta"], ALPHA_ESC)
        # en bar (the OLD English statistic) for the same preset, for the contrast
        en_key = cell.replace("|pmax|", "|en|")
        ce = cells.get(en_key)
        en_claim = NC._fw(10 ** 6, ce["mu"], ce["beta"], ALPHA_CLAIM) if ce else None
        tbl = {}
        for reg in sorted({r["register"] for r in rows}):
            cor = [r for r in rows if r["preset"] == preset and r["register"] == reg
                   and r["arm"] == "correct"]
            wro = [r for r in rows if r["preset"] == preset and r["register"] == reg
                   and r["arm"] == "wrong"]
            if not cor:
                continue
            pv = np.array([r["pmax"] for r in cor])
            wv = np.array([r["pmax"] for r in wro]) if wro else np.array([])
            ev = np.array([r["en"] for r in cor])
            tbl[reg] = {
                "median_recovery": float(np.median([r["recovery"] for r in cor])),
                "pmax_power_claim": float((pv >= claim).mean()),
                "pmax_power_escalate": float((pv >= esc).mean()),
                "pmax_wrong_power_claim": (float((wv >= claim).mean()) if len(wv) else None),
                "en_power_claim": (float((ev >= en_claim).mean()) if en_claim is not None else None),
                "en_power_fixed_-5.5": float((ev >= -5.5).mean()),
                "median_pmax_correct": float(np.median(pv)),
                "median_pmax_wrong": (float(np.median(wv)) if len(wv) else None),
            }
        result["by_preset"][preset] = {
            "cell": cell, "mu": c["mu"], "beta": c["beta"], "M": c["M"],
            "status": c.get("status"), "claim_bar": claim, "escalate_bar": esc,
            "en_claim_bar": en_claim, "by_register": tbl}
    json.dump(result, open(os.path.join(HERE, "out_plant_recovery.json"), "w",
                           encoding="utf-8"), indent=1, default=float)
    print(f"wrote out_plant_recovery.json  ({el/60:.1f} min, nrep={nrep})")
    # headline the four gate registers
    gate = ["LP1_REAL", "LATIN", "OE", "EN_HALFVOWEL"]
    for preset in presets:
        print(f"\n  === preset={preset}  claim_bar(pmax)={result['by_preset'][preset]['claim_bar']:.3f} ===")
        print(f"  {'register':14s} {'recov':>6s} {'pmax_pow':>8s} {'wrong_pmax':>10s} "
              f"{'en_pow':>7s} {'en@-5.5':>8s}")
        for reg in gate + ["EN_NOVOWEL", "RAND"]:
            t = result["by_preset"][preset]["by_register"].get(reg)
            if not t:
                continue
            print(f"  {reg:14s} {t['median_recovery']:6.2f} {t['pmax_power_claim']:8.2f} "
                  f"{str(t['pmax_wrong_power_claim']):>10s} "
                  f"{str(round(t['en_power_claim'],2) if t['en_power_claim'] is not None else None):>7s} "
                  f"{t['en_power_fixed_-5.5']:8.2f}")
    return result


# ------------------------------------------------------------------ 3. fresh null + G-CAL
def gcal(M=100000, L=120, mode="keyskip1", procs=6):
    """Freshly generate a panel-max null (seed 3301, order-preserving) through the fast
    vecbeam+I2 path and run G-CAL: an independent re-verification that the adopted
    panel-max bar controls its false-positive rate on data this lane generated itself."""
    import run_i1i2 as RI
    import run_calibration as RC
    # use the same fast worker I3 used for the keyskip1 panel (bit-identical to the repo beam)
    jobs, k, chunk = [], 0, 512
    while k < M:
        t = min(chunk, M - k)
        # seed base != I3's 770000 so this is a FRESH independent null, but deterministic
        jobs.append((3301 + len(jobs) * 7919, t, L, mode))
        k += t
    t0 = time.time()
    vals, el = RI.run(RI._work_fast, jobs, M, procs)
    pm = vals["pmax"]
    fit = NC.fit_cell(pm)
    g_claim = NC.gcal(pm, fit["mu"], fit["beta"], alpha=ALPHA_CLAIM)
    g_esc = NC.gcal(pm, fit["mu"], fit["beta"], alpha=ALPHA_ESC)
    # ALSO G-CAL the ADOPTED bar (the calib19 exact cell) against THIS fresh null -- the real test
    adopted = NC.calib()["cells"][PRESET_CELLS["exact"]]
    g_adopt_claim = NC.gcal(pm, adopted["mu"], adopted["beta"], alpha=ALPHA_CLAIM)
    g_adopt_esc = NC.gcal(pm, adopted["mu"], adopted["beta"], alpha=ALPHA_ESC)
    out = {"generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "M": M, "L": L, "mode": mode, "seconds": el, "seed_base": 3301,
           "fresh_fit": {"mu": fit["mu"], "beta": fit["beta"],
                         "gev_xi": fit["gev"]["xi"] if fit["gev"] else None,
                         "single_max": fit["single_max"]},
           "adopted_cell": {"cell": PRESET_CELLS["exact"], "mu": adopted["mu"],
                            "beta": adopted["beta"], "M": adopted["M"]},
           "gcal_fresh_fit_claim": g_claim, "gcal_fresh_fit_escalate": g_esc,
           "gcal_ADOPTED_bar_on_fresh_null_claim": g_adopt_claim,
           "gcal_ADOPTED_bar_on_fresh_null_escalate": g_adopt_esc}
    json.dump(out, open(os.path.join(HERE, "out_panelmax_gcal.json"), "w",
                        encoding="utf-8"), indent=1, default=float)
    print(f"wrote out_panelmax_gcal.json  ({el/60:.1f} min, M={M:,})")
    print(f"  fresh fit: mu={fit['mu']:.4f} beta={fit['beta']:.5f} "
          f"xi={out['fresh_fit']['gev_xi']}")
    print(f"  adopted  : mu={adopted['mu']:.4f} beta={adopted['beta']:.5f} (M={adopted['M']:,})")
    print(f"  G-CAL adopted-bar on fresh null @claim: passed={g_adopt_claim['passed']} "
          f"n_gating={g_adopt_claim['n_gating_blocks']}")
    for b, r in g_adopt_claim["per_block"].items():
        if r["gating"]:
            print(f"    block {b:>6s}: bar={r['bar']:.3f} ratio={r['ratio']:.3f} "
                  f"{'OK' if r['within_20pct'] else ('CONSERVATIVE' if r['ratio']<1 else 'ANTI-CONS')}")
    return out


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd == "build":
        build()
    elif cmd == "plant":
        nrep = int(sys.argv[2]) if len(sys.argv) > 2 else 8
        plant(nrep=nrep)
    elif cmd == "gcal":
        M = int(sys.argv[2]) if len(sys.argv) > 2 else 100000
        gcal(M=M)
    elif cmd == "all":
        nrep = int(sys.argv[2]) if len(sys.argv) > 2 else 8
        M = int(sys.argv[3]) if len(sys.argv) > 3 else 100000
        build()
        plant(nrep=nrep)
        gcal(M=M)
    else:
        raise SystemExit(f"unknown cmd {cmd}")
