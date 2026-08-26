"""R1 / sub-attack B — I2's register panel as a register-shopping machine.

Pre-registered in PREREG.md §4 (+ ADDENDUM 1 for B-iv). Own instrument (r1_lib.py).

    python3 b_panel.py          -> out_b.json
    python3 b_panel.py --quick
"""
import json
import math
import os
import random
import statistics as st
import sys
import time
from multiprocessing import Pool

import r1_lib as R

HERE = os.path.dirname(os.path.abspath(__file__))
L = 120
SEED0 = 44011
PANEL = ["EN", "EN_KJV", "LP1", "LA", "OE", "DE", "CY", "EN_HALF", "EN_NOVOW"]

_REG = None
_LM = None


def regs():
    global _REG
    if _REG is None:
        _REG = R.build_registers()
    return _REG


def lms():
    """Train each register LM on the FIRST 80 % of its stream; test slices come from the last 20 %."""
    global _LM
    if _LM is None:
        _LM = {}
        for k in PANEL:
            s = regs()[k]
            cut = int(len(s) * 0.8)
            _LM[k] = R.RuneLM(s[:cut])
    return _LM


def test_slice(k, rng, n=L):
    s = regs()[k]
    cut = int(len(s) * 0.8)
    tail = s[cut:]
    if len(tail) < n + 2:
        tail = s
    a = rng.randrange(0, len(tail) - n - 1)
    return tail[a:a + n]


def panel_scores(stream):
    return {k: m.score(stream) for k, m in lms().items()}


# ---------------------------------------------------------------- PC-B1
def pcb1(nrep=20):
    rng = random.Random(SEED0)
    rows = {}
    uni = [[rng.randrange(29) for _ in range(L)] for _ in range(nrep)]
    for k in PANEL:
        m = lms()[k]
        real = st.median(m.score(test_slice(k, rng)) for _ in range(nrep))
        noise = st.median(m.score(u) for u in uni)
        rows[k] = {"own_register": real, "uniform_runes": noise, "margin": real - noise}
    npass = sum(1 for v in rows.values() if v["margin"] >= 1.0)
    return {"rows": rows, "n_pass": npass, "n_panel": len(PANEL),
            "verdict": "PASS" if npass >= 6 else "ABANDON"}


# ---------------------------------------------------------------- B-i correlation / M_eff
def m_eff(nsim=2000):
    rng = random.Random(SEED0 + 1)
    mat = []
    for _ in range(nsim):
        s = [rng.randrange(29) for _ in range(L)]
        sc = panel_scores(s)
        mat.append([sc[k] for k in PANEL])
    p = len(PANEL)
    cols = list(zip(*mat))
    means = [st.mean(c) for c in cols]
    sds = [st.pstdev(c) for c in cols]
    corr = [[0.0] * p for _ in range(p)]
    for i in range(p):
        for j in range(p):
            cov = sum((mat[t][i] - means[i]) * (mat[t][j] - means[j]) for t in range(nsim)) / nsim
            corr[i][j] = cov / (sds[i] * sds[j]) if sds[i] and sds[j] else 0.0
    try:
        import numpy as np
        ev = sorted(np.linalg.eigvalsh(np.array(corr)), reverse=True)
        ev = [max(0.0, float(e)) for e in ev]
    except Exception:                                             # noqa: BLE001
        ev = None
    out = {"corr": corr, "eigenvalues": ev, "panel": PANEL,
           "sds": sds, "means": means, "nsim": nsim}
    if ev:
        # Nyholt / Cheverud
        var_ev = st.pvariance(ev)
        out["M_eff_nyholt"] = 1 + (p - 1) * (1 - var_ev / p)
        # Li & Ji (2005)
        out["M_eff_liji"] = sum((1.0 if e >= 1 else 0.0) + (e - math.floor(e)) for e in ev)
    return out


# ---------------------------------------------------------------- B-ii naive panel FPR
def panel_fpr(ncal=3000, ntest=3000):
    """Per-register alpha=0.01 bars from a calibration set of uniform-rune strings, then the
    fraction of a fresh noise set for which the MAX over the panel clears its own register's bar."""
    rng = random.Random(SEED0 + 2)
    cal = [[rng.randrange(29) for _ in range(L)] for _ in range(ncal)]
    calsc = [panel_scores(s) for s in cal]
    bars = {}
    for k in PANEL:
        v = sorted(x[k] for x in calsc)
        bars[k] = v[int(0.99 * len(v))]
    test = [[rng.randrange(29) for _ in range(L)] for _ in range(ntest)]
    hits_any, hits_en = 0, 0
    per_reg = {k: 0 for k in PANEL}
    for s in test:
        sc = panel_scores(s)
        any_hit = False
        for k in PANEL:
            if sc[k] >= bars[k]:
                per_reg[k] += 1
                any_hit = True
        if any_hit:
            hits_any += 1
        if sc["EN"] >= bars["EN"]:
            hits_en += 1
    return {"bars": bars, "alpha_per_register": 0.01,
            "fpr_max_over_panel": hits_any / ntest,
            "fpr_english_only": hits_en / ntest,
            "naive_independent_expectation": 1 - 0.99 ** len(PANEL),
            "per_register_hits": {k: v / ntest for k, v in per_reg.items()},
            "ncal": ncal, "ntest": ntest}


# ---------------------------------------------------------------- B-iii selection correction power
def _decode_one(args):
    """One noise decode: random wrong key against real LP2 -> (score, plain_idx)."""
    k, model, ms = args
    uns = R.unsolved()
    rng = random.Random(880000 + k)
    off = rng.randrange(0, len(uns) - L - 1)
    C = uns[off:off + L]
    K = R.random_key(rng, L * 10 + 512)
    bd = R.beam_decode(C, K, beam_w=400, max_skip=ms, model=model)
    return bd["score"], bd["plain_idx"]


def selection_correction(n_pool=1200, topk=120, pool=None):
    """Rebuild L7-A.4's statistic and measure its POWER against a genuine true positive.

    L7-A.4 corrected for selection with contrast = score_M - score_EN, standardised against the
    archive's own spread, and reported 0 of 340 archived candidates at z >= 3.  The archive is
    the English-argmax of its sweep.  Here: build the same kind of reference set (top-`topk` by
    English quadgram score out of `n_pool` noise decodes), compute its contrast distribution,
    then plant a GENUINE non-English plaintext, decode with the CORRECT key, and see what z the
    same statistic gives it.
    """
    args = [(k, "exact", 3) for k in range(n_pool)]
    res = pool.map(_decode_one, args, chunksize=8) if pool else [_decode_one(a) for a in args]
    res.sort(key=lambda x: x[0], reverse=True)
    top = res[:topk]
    ref = {}
    for k in PANEL:
        if k in ("EN", "EN_KJV"):
            continue
        vals = [lms()[k].score(p) - lms()["EN"].score(p) for _s, p in top]
        ref[k] = {"mean": st.mean(vals), "sd": st.pstdev(vals)}

    # --- true positives: genuine register, correct key, exact construction ---
    rng = random.Random(SEED0 + 3)
    tp = {}
    for k in PANEL:
        if k in ("EN", "EN_KJV"):
            continue
        zs, raw = [], []
        for rep in range(7):
            P = test_slice(k, rng)
            K = R.sha_key(b"CICADA3301" + bytes([rep]), L * 10 + 512)
            C, _ = R.encipher_keyskip(P, K, supp=0.83, seed=SEED0 + rep)
            bd = R.beam_decode(C, K, beam_w=400, max_skip=3, model="exact")
            p = bd["plain_idx"]
            c = lms()[k].score(p) - lms()["EN"].score(p)
            raw.append(c)
            zs.append((c - ref[k]["mean"]) / ref[k]["sd"] if ref[k]["sd"] else 0.0)
        tp[k] = {"median_contrast": st.median(raw), "median_z": st.median(zs),
                 "max_z": max(zs), "z_values": zs,
                 "ref_mean": ref[k]["mean"], "ref_sd": ref[k]["sd"],
                 "reaches_z3": st.median(zs) >= 3.0}
    return {"reference_set_size": topk, "pool": n_pool, "true_positives": tp,
            "note": "reference set = top-k by ENGLISH score out of noise decodes, i.e. the same "
                    "selection L7-A.4's archive underwent"}


# ---------------------------------------------------------------- B-iv I1 x I2 interaction
def interaction(nrep=7):
    rng = random.Random(SEED0 + 4)
    out = {}
    for k in ("LA", "CY", "OE", "EN_HALF", "LP1", "EN"):
        rows = {"exact/ms3": {"lm": [], "rec": [], "q": []},
                "free/ms3": {"lm": [], "rec": [], "q": []},
                "union2/ms3": {"lm": [], "rec": [], "q": []}}
        for rep in range(nrep):
            P = test_slice(k, rng)
            K = R.sha_key(b"CICADA3301" + bytes([rep]), L * 10 + 512)
            C, _ = R.encipher_skip2(P, K, supp=0.83, seed=SEED0 + rep)
            for label, (model, ms) in (("exact/ms3", ("exact", 3)),
                                       ("free/ms3", ("free", 3)),
                                       ("union2/ms3", ("union2", 3))):
                bd = R.beam_decode(C, K, beam_w=400, max_skip=ms, model=model)
                p = bd["plain_idx"]
                rows[label]["lm"].append(lms()[k].score(p))
                rows[label]["rec"].append(R.recovery(p, P))
                rows[label]["q"].append(bd["score"])
        summ = {lab: {"own_lm": st.median(v["lm"]), "recovery": st.median(v["rec"]),
                      "quadgram": st.median(v["q"])} for lab, v in rows.items()}
        summ["truth_own_lm"] = st.median(
            lms()[k].score(test_slice(k, random.Random(SEED0 + 99 + i))) for i in range(nrep))
        summ["delta_lm_free_minus_exact"] = summ["free/ms3"]["own_lm"] - summ["exact/ms3"]["own_lm"]
        summ["delta_rec_free_minus_exact"] = (summ["free/ms3"]["recovery"]
                                              - summ["exact/ms3"]["recovery"])
        summ["delta_lm_union2_minus_exact"] = (summ["union2/ms3"]["own_lm"]
                                               - summ["exact/ms3"]["own_lm"])
        summ["delta_rec_union2_minus_exact"] = (summ["union2/ms3"]["recovery"]
                                                - summ["exact/ms3"]["recovery"])
        out[k] = summ
    return out


def main():
    quick = "--quick" in sys.argv
    out = {"meta": {"L": L, "panel": PANEL, "seed0": SEED0,
                    "started": time.strftime("%Y-%m-%dT%H:%M:%S")}}

    print("== PC-B1: can the panel see its own registers? ==")
    out["PC_B1"] = pcb1(nrep=8 if quick else 20)
    for k, v in out["PC_B1"]["rows"].items():
        print(f"  {k:9s} own {v['own_register']:7.3f}  uniform {v['uniform_runes']:7.3f}  "
              f"margin {v['margin']:6.3f}")
    print("  ->", out["PC_B1"]["verdict"], f"({out['PC_B1']['n_pass']}/9 registers)")
    if out["PC_B1"]["verdict"] == "ABANDON":
        json.dump(out, open(os.path.join(HERE, "out_b.json"), "w"), indent=1)
        return

    print("\n== B-i: correlation and effective number of tests ==")
    out["B_i"] = m_eff(nsim=400 if quick else 2000)
    print(f"  M_eff (Nyholt) = {out['B_i'].get('M_eff_nyholt')}")
    print(f"  M_eff (Li-Ji)  = {out['B_i'].get('M_eff_liji')}")
    print("  correlation matrix (rows/cols =", PANEL, ")")
    for i, k in enumerate(PANEL):
        print("   ", f"{k:9s}", " ".join(f"{out['B_i']['corr'][i][j]:+.2f}"
                                         for j in range(len(PANEL))))
    me = out["B_i"].get("M_eff_liji") or 9
    out["B_i"]["verdict"] = "FOUND-ERROR" if (me < 6 or me > 13.5) else "NO-ERROR-FOUND"
    print("  B-i:", out["B_i"]["verdict"])

    print("\n== B-ii: naive max-over-panel false-positive rate ==")
    out["B_ii"] = panel_fpr(ncal=800 if quick else 3000, ntest=800 if quick else 3000)
    print(f"  english-only FPR      {out['B_ii']['fpr_english_only']:.4f}")
    print(f"  max-over-panel FPR    {out['B_ii']['fpr_max_over_panel']:.4f}"
          f"   (naive-independent expectation "
          f"{out['B_ii']['naive_independent_expectation']:.4f})")
    out["B_ii"]["verdict"] = ("FOUND-ERROR" if out["B_ii"]["fpr_max_over_panel"] >= 0.05
                              else "NO-ERROR-FOUND")
    print("  B-ii:", out["B_ii"]["verdict"])

    with Pool(6) as pool:
        print("\n== B-iii: does L7-A.4's selection correction have power? ==")
        out["B_iii"] = selection_correction(n_pool=200 if quick else 1200,
                                            topk=40 if quick else 120, pool=pool)
        for k, v in out["B_iii"]["true_positives"].items():
            print(f"  {k:9s} true-positive median z = {v['median_z']:6.2f}  "
                  f"(max {v['max_z']:5.2f})  reaches z>=3: {v['reaches_z3']}")
        fired = any((not v["reaches_z3"]) for k, v in out["B_iii"]["true_positives"].items()
                    if k in ("LA", "CY", "EN_HALF"))
        out["B_iii"]["verdict"] = "FOUND-ERROR" if fired else "NO-ERROR-FOUND"
        print("  B-iii:", out["B_iii"]["verdict"])

    print("\n== B-iv: I1 x I2 interaction (ADDENDUM 1) ==")
    out["B_iv"] = interaction(nrep=3 if quick else 7)
    fired = False
    for k, v in out["B_iv"].items():
        print(f"  {k:9s} exact lm {v['exact/ms3']['own_lm']:7.3f} rec {v['exact/ms3']['recovery']:.2f}"
              f" | free lm {v['free/ms3']['own_lm']:7.3f} rec {v['free/ms3']['recovery']:.2f}"
              f" | union2 lm {v['union2/ms3']['own_lm']:7.3f} rec {v['union2/ms3']['recovery']:.2f}"
              f" | dLM {v['delta_lm_free_minus_exact']:+.3f} dREC "
              f"{v['delta_rec_free_minus_exact']:+.3f}")
        if k in ("LA", "CY", "OE", "EN_HALF"):
            if v["delta_lm_free_minus_exact"] <= -0.10 or v["delta_rec_free_minus_exact"] <= -0.10:
                fired = True
    out["B_iv_verdict"] = "FOUND-ERROR" if fired else "NO-ERROR-FOUND"
    print("  B-iv:", out["B_iv_verdict"])

    out["meta"]["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    json.dump(out, open(os.path.join(HERE, "out_b.json"), "w"), indent=1)
    print("\nwrote out_b.json")


if __name__ == "__main__":
    main()
