"""audit_catch.py -- real_mode_catch audit harness for the strengthened k-fold no-oracle proxy.

Procedure (pre-registered in PREREG.md):

  0. POSITIVE CONTROLS FIRST (gate everything):
     - reproduce the S-RESCOPE 45 EN_NOVOWEL hallucinations BIT-IDENTICALLY (same recipe) and
       confirm the hitfn20 single-cut baseline catch == 15/45 (the leak we are fixing).
     - a GENUINE-DECODE PANEL (correct key over English, true recovery ~1.0) to measure the
       strengthened proxy's false-reject rate.

  1. TUNE on the FROZEN planted-45: sweep (k_folds x agree_rule), record catch + genuine
     false-reject for each cell -> catch_surface.json. Choose the winning cell by the
     pre-registered rule (max catch subject to genuine false-reject <= 0.10, tie-break smaller k).

  2. FREEZE that cell, then AUDIT it on a HELD-OUT SURROGATE SET: a fresh EN_NOVOWEL
     hallucination population drawn under a FRESH key (seed 3301, order-preserving) + fresh rng
     offsets, disjoint from the tuning draws. PASS requires the frozen cell to hold >=0.90 catch
     on the surrogate AND keep genuine false-reject <= 0.10.

Score on rune INDICES throughout (driftbeam.recovery). No plaintext oracle in the fold proxy.
"""
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _p in (HERE, os.path.join(LP, "analysis", "round19", "I1"),
           os.path.join(LP, "analysis", "round19", "I2"),
           os.path.join(LP, "analysis", "round19", "I3"),
           os.path.join(LP, "analysis", "round20", "P3"),
           os.path.join(LP, "analysis", "round20", "HITFN"),
           os.path.join(LP, "analysis", "round13", "B04"),
           os.path.join(LP, "src"), os.path.join(LP, "analysis", "campaign18_skip")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import driftbeam as DB          # noqa: E402
import adjudicate as AD         # noqa: E402
import panelmax20 as PM         # noqa: E402
import hitfn20 as H             # noqa: E402
import plants as PL3            # noqa: E402
import skipdecode as sk         # noqa: E402
import ks                       # noqa: E402
import hitfn21_folds as F       # noqa: E402

L = 240
SUPP = 0.83
PRESET = "exact"
N_CANON = 10 ** 6
K_GRID = [2, 3, 4, 5, 6]
RULES = ["min", "mean", "frac_pass"]
FALSE_REJECT_MAX = 0.10       # PREREG P-c
CATCH_BAR = 0.90              # PREREG P-a/P-b


# --------------------------------------------------------------------------- populations
def build_hallucinations(key_seed=b"CICADA", n_reps=60, rep0=0, seed0=5000, csd0=600,
                         gen="sha256_ctr", red="mod29"):
    """Reproduce the EN_NOVOWEL bar-clearing hallucinations. With key_seed=b'CICADA',
    rep0=0, seed0=5000, csd0=600 this is BIT-IDENTICAL to S-RESCOPE's heldout_proxy_audit
    (the 45-case tuning population). Different key_seed / offsets -> the held-out surrogate set."""
    panels = PL3._panels()
    stream = panels["EN_NOVOWEL"]
    Kfull = ks.make_ks(gen, red, key_seed, L * 4 + 1024)
    bar = PM.panelmax_bar(PRESET, N_CANON, 0.01)
    cases = []
    for rep in range(rep0, rep0 + n_reps):
        rng = random.Random(seed0 + rep)
        s = rng.randrange(0, len(stream) - L - 1)
        P = list(stream[s:s + L])
        C, _n, _ = sk.encipher_keyskip(P, Kfull, sign=-1, supp=SUPP, seed=csd0 + rep)
        d = DB.beam_decode(C, list(Kfull), sign=-1, o=0, beam_w=400, **DB.PRESETS[PRESET])
        a = AD.adjudicate(d["plain_idx"], translit=d["translit"])
        rec = DB.recovery(d["plain_idx"], P)
        if float(a["pmax"]) >= bar and rec < 0.90:
            cases.append({"C": C, "K": list(Kfull), "P": P, "pmax": float(a["pmax"]),
                          "true_recovery": float(rec)})
    return cases, float(bar)


def build_genuine_panel(key_seed=b"CICADA", n_reps=20, seed0=7000, csd0=99,
                        gen="sha256_ctr", red="mod29"):
    """Genuine decodes: correct key over EN_MODERN English, true recovery ~1.0, pmax >> bar.
    Used to measure the strengthened proxy's genuine-decode FALSE-REJECT rate."""
    panels = PL3._panels()
    stream = panels["EN_MODERN"]
    Kfull = ks.make_ks(gen, red, key_seed, L * 4 + 1024)
    bar = PM.panelmax_bar(PRESET, N_CANON, 0.01)
    cases = []
    for rep in range(n_reps):
        rng = random.Random(seed0 + rep)
        s = rng.randrange(0, len(stream) - L - 1)
        P = list(stream[s:s + L])
        C, _n, _ = sk.encipher_keyskip(P, Kfull, sign=-1, supp=SUPP, seed=csd0 + rep)
        d = DB.beam_decode(C, list(Kfull), sign=-1, o=0, beam_w=400, **DB.PRESETS[PRESET])
        a = AD.adjudicate(d["plain_idx"], translit=d["translit"])
        rec = DB.recovery(d["plain_idx"], P)
        if float(a["pmax"]) >= bar and rec >= 0.95:
            cases.append({"C": C, "K": list(Kfull), "P": P, "pmax": float(a["pmax"]),
                          "true_recovery": float(rec)})
    return cases


# --------------------------------------------------------------------------- catch measures
def _hd(case):
    return H.HitDecode(C=case["C"], K=case["K"], o=0, sign=-1, preset=PRESET,
                       n_round_adjudicated=N_CANON)   # NO truth -> deployable no-oracle path


def single_cut_catch(cases):
    """hitfn20 baseline: real-mode single 1/4->3/4 proxy. Catch = fraction is_hit==False."""
    caught = 0
    heldouts = []
    for c in cases:
        v = H.evaluate(_hd(c))
        heldouts.append(round(v.heldout_recovery, 3))
        if not v.hit:
            caught += 1
    return caught, len(cases), heldouts


def kfold_catch(cases, k, rule):
    """Strengthened proxy catch on a hallucination population under cell (k, rule)."""
    caught = 0
    heldouts = []
    for c in cases:
        v = F.evaluate_folds(_hd(c), k_folds=k, agree_rule=rule)
        heldouts.append(round(v.heldout_recovery, 3))
        if not v.hit:
            caught += 1
    return caught, len(cases), heldouts


def kfold_false_reject(genuine, k, rule):
    """Fraction of GENUINE decodes the cell wrongly REJECTS (is_hit==False)."""
    rejected = 0
    heldouts = []
    for c in genuine:
        v = F.evaluate_folds(_hd(c), k_folds=k, agree_rule=rule)
        heldouts.append(round(v.heldout_recovery, 3))
        if not v.hit:
            rejected += 1
    return rejected, len(genuine), heldouts


# --------------------------------------------------------------------------- main audit
def run():
    out = {}

    # ---- 0. positive controls -----------------------------------------------------------
    halluc, bar = build_hallucinations()          # the frozen 45
    genuine = build_genuine_panel()

    sc_caught, sc_n, sc_heldouts = single_cut_catch(halluc)
    baseline = {"n_hallucinations": sc_n, "single_cut_caught": sc_caught,
                "single_cut_catch_rate": sc_caught / sc_n if sc_n else None,
                "reproduces_S_RESCOPE_15_45": (sc_n == 45 and sc_caught == 15)}

    genuine_true_rec = [round(c["true_recovery"], 3) for c in genuine]

    out["controls"] = {
        "panelmax_bar_exact_1e6": bar,
        "hallucination_population_n": sc_n,
        "single_cut_baseline": baseline,
        "genuine_panel_n": len(genuine),
        "genuine_true_recoveries": genuine_true_rec,
        "genuine_all_recover_1.0": all(c["true_recovery"] >= 0.95 for c in genuine),
    }
    controls_ok = (sc_n == 45 and sc_caught == 15 and len(genuine) >= 10
                   and all(c["true_recovery"] >= 0.95 for c in genuine))
    out["controls"]["PASS"] = controls_ok
    if not controls_ok:
        out["ABORT"] = ("positive controls failed: could not reproduce the S-RESCOPE 45/15 baseline "
                        "or the genuine panel -- instrument not trusted (doctrine: a null from an "
                        "unvalidated instrument is not a negative)")
        json.dump(out, open(os.path.join(HERE, "catch_surface.json"), "w"), indent=1, default=float)
        return out

    # ---- 1. TUNE: catch surface over (k, rule) on the FROZEN 45 -------------------------
    surface = []
    for k in K_GRID:
        for rule in RULES:
            c_caught, c_n, c_ho = kfold_catch(halluc, k, rule)
            g_rej, g_n, g_ho = kfold_false_reject(genuine, k, rule)
            surface.append({
                "k_folds": k, "agree_rule": rule,
                "catch": c_caught, "catch_n": c_n,
                "catch_rate": c_caught / c_n if c_n else None,
                "genuine_false_reject": g_rej, "genuine_n": g_n,
                "genuine_false_reject_rate": g_rej / g_n if g_n else None,
                "meets_catch_bar": (c_caught / c_n) >= CATCH_BAR if c_n else False,
                "meets_false_reject_cap": (g_rej / g_n) <= FALSE_REJECT_MAX if g_n else False,
            })
    out["catch_surface"] = surface

    # ---- choose winning cell: max catch s.t. false_reject <= cap, tie-break smaller k ----
    eligible = [row for row in surface if row["meets_false_reject_cap"]]
    winner = None
    if eligible:
        winner = sorted(eligible, key=lambda r: (-r["catch_rate"], r["k_folds"],
                                                 RULES.index(r["agree_rule"])))[0]
    out["tuning_winner"] = winner

    tuning_pass = bool(winner and winner["meets_catch_bar"])
    out["tuning_meets_0.90_catch"] = tuning_pass

    # ---- 2. FREEZE + AUDIT on held-out surrogate (fresh key seed 3301, fresh offsets) ----
    if winner is not None:
        k_w, rule_w = winner["k_folds"], winner["agree_rule"]
        # fresh order-preserving surrogate: DIFFERENT key (seed 3301) + disjoint rng offsets.
        surr_halluc, surr_bar = build_hallucinations(key_seed=b"CICADA3301", n_reps=90,
                                                     seed0=8000, csd0=2600)
        surr_caught, surr_n, surr_ho = kfold_catch(surr_halluc, k_w, rule_w)
        surr_genuine = build_genuine_panel(key_seed=b"CICADA3301", n_reps=24, seed0=9100, csd0=770)
        sg_rej, sg_n, sg_ho = kfold_false_reject(surr_genuine, k_w, rule_w)
        # also report the SINGLE-CUT catch on the surrogate for contrast
        sc_surr_caught, sc_surr_n, _ = single_cut_catch(surr_halluc)
        out["heldout_surrogate_audit"] = {
            "frozen_cell": {"k_folds": k_w, "agree_rule": rule_w},
            "surrogate_key_seed": "CICADA3301 (fresh, order-preserving)",
            "surrogate_hallucination_n": surr_n,
            "single_cut_catch_on_surrogate": (sc_surr_caught / sc_surr_n) if sc_surr_n else None,
            "kfold_catch": surr_caught, "kfold_catch_n": surr_n,
            "kfold_catch_rate": surr_caught / surr_n if surr_n else None,
            "surrogate_genuine_n": sg_n,
            "surrogate_genuine_false_reject": sg_rej,
            "surrogate_genuine_false_reject_rate": sg_rej / sg_n if sg_n else None,
            "meets_catch_bar": (surr_caught / surr_n) >= CATCH_BAR if surr_n else False,
            "meets_false_reject_cap": (sg_rej / sg_n) <= FALSE_REJECT_MAX if sg_n else False,
        }
        heldout_pass = bool(surr_n >= 20
                            and (surr_caught / surr_n) >= CATCH_BAR
                            and (sg_n >= 10 and (sg_rej / sg_n) <= FALSE_REJECT_MAX))
    else:
        out["heldout_surrogate_audit"] = {"skipped": "no eligible cell met the false-reject cap"}
        heldout_pass = False

    # ---- final verdict ------------------------------------------------------------------
    out["VERDICT"] = {
        "tuning_pass": tuning_pass,
        "heldout_surrogate_pass": heldout_pass,
        "SEAL_PASS": bool(tuning_pass and heldout_pass),
        "rule": ("SEAL PASS iff a frozen (k,rule) cell reaches >=0.90 catch on the planted-45 AND "
                 "holds >=0.90 catch on the held-out surrogate AND keeps genuine false-reject "
                 "<=0.10 on both. Else the no-oracle gate is provably leaky -> bar-clearing "
                 "survivors are flagged-for-oracle, never auto-certified."),
    }
    json.dump(out, open(os.path.join(HERE, "catch_surface.json"), "w"), indent=1, default=float)
    return out


if __name__ == "__main__":
    o = run()
    v = o.get("VERDICT", {})
    print(json.dumps({"controls": o.get("controls", {}).get("single_cut_baseline"),
                      "winner": o.get("tuning_winner"),
                      "heldout": o.get("heldout_surrogate_audit"),
                      "VERDICT": v}, indent=1, default=float))
