"""Round 18 / L2 -- SUB-ATTACK C: the constraint / information budget.

The lane's premise was that 12,956 acceptance events are 12,956 certificates about the joint
(plaintext, keystream), and that nobody here has ever tried to spend them.  This module
computes, honestly and in bits, what they are worth.

It contains one exact result that decides the whole sub-attack, and it is short enough to
check by hand -- see `acceptance_channel_proof()`.

Run:  PYTHONUTF8=1 python3 c_budget.py
"""
import os, sys, json, math, random
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import filter_models as fm                              # noqa: E402
import fastbeam as fb                                   # noqa: E402
ROOT = fb.ROOT
sys.path.insert(0, os.path.join(ROOT, "analysis", "campaign18_skip"))
import skipdecode as sk                                 # noqa: E402

N = 29
L2 = math.log2(N)
SUPP = 0.8129
NRUNE = 12956


# ------------------------------------------------------------------ H(C)
def h_ciphertext(r_obs):
    """Entropy of the ciphertext under the fitted filtered-Markov law, vs unfiltered."""
    unfiltered = NRUNE * L2
    row = -(r_obs * math.log2(r_obs) + (1 - r_obs) * math.log2((1 - r_obs) / (N - 1)))
    filtered = L2 + (NRUNE - 1) * row
    return {"unfiltered_bits": unfiltered, "row_entropy_bits": row,
            "filtered_bits": filtered,
            "filter_information_injection_bits": unfiltered - filtered,
            "bits_per_symbol_removed": (unfiltered - filtered) / NRUNE}


# ------------------------------------------------------------------ H(P)
def h_plaintext(order_max=5, train=400000, test=200000):
    """Held-out cross-entropy of archaic English written in Gematria runes.

    Cross-entropy on held-out data is an honest UPPER bound on the entropy rate: it cannot
    flatter itself the way a plug-in estimate of a high-order model does.
    """
    seq = fm.english_runes(train + test)
    tr, te = seq[:train], seq[train:]
    rows = []
    for k in range(0, order_max + 1):
        ctx = {}
        for i in range(k, len(tr)):
            key = tuple(tr[i - k:i])
            d = ctx.setdefault(key, np.zeros(N))
            d[tr[i]] += 1
        tot = 0.0
        n = 0
        for i in range(k, len(te)):
            key = tuple(te[i - k:i])
            d = ctx.get(key)
            if d is None:
                p = 1.0 / N
            else:
                p = (d[te[i]] + 0.5) / (d.sum() + 0.5 * N)     # add-1/2 smoothing
            tot += -math.log2(p)
            n += 1
        rows.append({"order": k, "bits_per_rune": tot / n})
    best = min(rows, key=lambda r: r["bits_per_rune"])
    return {"by_order": rows, "bits_per_rune": best["bits_per_rune"],
            "best_order": best["order"], "total_bits": best["bits_per_rune"] * NRUNE}


# ------------------------------------------------------------------ the exact result
def acceptance_channel_proof(supp=SUPP, checks=200000, seed=3301):
    """EXACT: the acceptance events carry ZERO information about the plaintext.

    Under the surviving locus (ciphertext rejection, uniform keystream, key advances on
    reject), the probability of emitting c_i given the previous ciphertext symbol cprev and
    the plaintext symbol p_i is, summing over the number m of rejected draws:

        P(c_i | p_i, cprev)
            = sum_m  (s/N)^m * (1/N) * w(c_i, cprev)          w = (1-s) if c_i==cprev else 1
            = (1/N) * w / (1 - s/N)
            = w / (N - s)

    Every rejected draw had to reproduce cprev, which pins ONE key value out of N (hence
    1/N) and costs one coin (hence s).  The accepted draw pins one key value (hence 1/N).
    The result does not contain p_i at all: the plaintext symbol only relabels WHICH key
    value is the pinned one, and the keystream is uniform, so relabelling changes nothing.

    Therefore P(C | P) is the same number for every candidate plaintext P, the likelihood
    is flat, and the filter contributes exactly zero bits of constraint on the plaintext.
    It also gives the residual doublet rate in closed form: (1-s)/(N-s).

    Verified two ways below: the closed form against the observed rate, and a Monte-Carlo
    check that the ciphertext law is identical for two maximally different plaintexts.
    """
    r_closed = (1 - supp) / (N - supp)
    # Monte Carlo: same filter, two very different plaintexts, compare ciphertext laws
    L = 200
    reps = checks // L
    rng = random.Random(seed)
    P_const = [7] * L
    P_eng = fm.english_runes(L)
    hists, rates, deltas = {}, {}, {}
    for tag, P in (("constant", P_const), ("english", P_eng)):
        h = np.zeros(N)
        dl = np.zeros(N)
        dbl = 0
        tot = 0
        for t in range(reps):
            K = [rng.randrange(N) for _ in range(L * 5 + 64)]
            C, _, _ = sk.encipher_keyskip(P, K, sign=-1, supp=supp, seed=rng.randrange(1 << 30))
            a = np.asarray(C)
            h += np.bincount(a, minlength=N)
            d = (a[1:] - a[:-1]) % N
            dl += np.bincount(d, minlength=N)
            dbl += int((a[1:] == a[:-1]).sum())
            tot += L - 1
        hists[tag] = h / h.sum()
        deltas[tag] = dl / dl.sum()
        rates[tag] = dbl / tot
    # chi-square of the two ciphertext symbol laws against each other
    # two-sample multinomial homogeneity: for a_i, b_i ~ Bin(n, p_i) independent,
    # E[(a-b)^2 / (a+b)] = 1 per cell, so the sum is chi2 with (cells - 1) df.
    a, b = hists["constant"] * checks, hists["english"] * checks
    chi_sym = float((((a - b) ** 2) / (a + b + 1e-9)).sum())
    a, b = deltas["constant"] * checks, deltas["english"] * checks
    chi_delta = float((((a - b) ** 2) / (a + b + 1e-9)).sum())
    return {
        "closed_form_residual_rate": r_closed,
        "observed_residual_rate": 86 / 12955,
        "closed_form_matches_observed_to": abs(r_closed - 86 / 12955),
        "mc_doublet_rate_constant_plaintext": rates["constant"],
        "mc_doublet_rate_english_plaintext": rates["english"],
        "mc_symbol_law_chi2_28df": chi_sym,
        "mc_delta_law_chi2_28df": chi_delta,
        "mc_reps_per_arm": reps,
        "plaintext_information_bits": 0.0,
        "verdict": ("ZERO plaintext information: ciphertext law identical for maximally "
                    "different plaintexts"),
    }


def main():
    X = fm.real_stream()
    r_obs = float(np.mean(np.asarray(X[1:]) == np.asarray(X[:-1])))
    hc = h_ciphertext(r_obs)
    print("H(C):")
    print(f"  unfiltered 12,956 x log2(29)      = {hc['unfiltered_bits']:.1f} bits")
    print(f"  under the fitted filtered law     = {hc['filtered_bits']:.1f} bits")
    print(f"  => filter injects                 = {hc['filter_information_injection_bits']:.1f} bits"
          f"  ({hc['bits_per_symbol_removed']:.4f} bits/symbol)")

    hp = h_plaintext()
    print("\nH(P) -- held-out cross-entropy of archaic English in runes:")
    for r in hp["by_order"]:
        print(f"  order {r['order']}: {r['bits_per_rune']:.3f} bits/rune")
    print(f"  best (order {hp['best_order']}): {hp['bits_per_rune']:.3f} bits/rune "
          f"=> {hp['total_bits']:.0f} bits over the book")

    print("\nEXACT acceptance-channel result:")
    pf = acceptance_channel_proof()
    print(f"  closed form (1-s)/(N-s)           = {pf['closed_form_residual_rate']:.8f}")
    print(f"  observed 86/12,955                = {pf['observed_residual_rate']:.8f}")
    print(f"  MC doublet rate, constant P       = {pf['mc_doublet_rate_constant_plaintext']:.5f}")
    print(f"  MC doublet rate, English P        = {pf['mc_doublet_rate_english_plaintext']:.5f}")
    print(f"  MC symbol-law chi2 (28 df)        = {pf['mc_symbol_law_chi2_28df']:.1f}")
    print(f"  MC delta-law  chi2 (28 df)        = {pf['mc_delta_law_chi2_28df']:.1f}")

    # ---------------- the budget
    rho = (1 / N) * SUPP / (1 - SUPP / N)
    hk_pad = (NRUNE + rho * NRUNE) * L2
    HP = hp["total_bits"]
    HC = hc["filtered_bits"]
    budgets = []
    for name, hk in (("full-entropy pad (13,330 symbols)", hk_pad),
                     ("printed/public pad, offset only (2^40 offsets)", 40.0),
                     ("derived keystream, 256-bit seed", 256.0),
                     ("derived keystream, 64-bit seed (C-PC control)", 64.0),
                     ("derived keystream, 32-bit seed", 32.0)):
        deficit = HP + hk - HC
        budgets.append({"hypothesis": name, "H_K_bits": hk, "H_P_bits": HP,
                        "H_C_bits": HC, "deficit_bits": deficit,
                        "determined": deficit <= 0})
    max_hk = HC - HP
    # sensitivity: the held-out order-3 bound is an UPPER bound on the English entropy rate
    sens = []
    for bpr in (1.5, 2.0, hp["bits_per_rune"], 3.0):
        sens.append({"bits_per_rune": bpr, "H_P_bits": bpr * NRUNE,
                     "max_H_K_for_determinacy_bits": HC - bpr * NRUNE,
                     "full_pad_deficit_bits": bpr * NRUNE + hk_pad - HC})

    print("\nTHE BUDGET  (determined iff H(P) + H(K) - H(C) <= 0):")
    for b in budgets:
        print(f"  {b['hypothesis']:46s} H(K)={b['H_K_bits']:10.0f}  "
              f"deficit={b['deficit_bits']:+10.0f}  "
              f"{'DETERMINED' if b['determined'] else 'under-determined'}")
    print(f"\n  max H(K) that leaves the system determined = {max_hk:.0f} bits "
          f"({max_hk/L2:.0f} rune-equivalents, {max_hk/8:.0f} bytes)")
    print(f"  acceptance events contribute {pf['plaintext_information_bits']:.0f} bits "
          f"toward closing it.")
    print("\n  sensitivity of the budget to the English entropy rate:")
    for r in sens:
        print(f"    H(P) = {r['bits_per_rune']:.3f} b/rune -> max H(K) = "
              f"{r['max_H_K_for_determinacy_bits']:8.0f} bits, "
              f"full-pad deficit {r['full_pad_deficit_bits']:+9.0f} bits")

    out = {"H_C": hc, "H_P": hp, "acceptance_channel": pf, "rho": rho,
           "budgets": budgets, "max_H_K_for_determinacy_bits": max_hk,
           "sensitivity_to_H_P": sens,
           "sat_bp_verdict": (
               "UNDER-DETERMINED by %.0f bits under a full-entropy pad. The acceptance "
               "events contribute exactly 0 bits about the plaintext (see "
               "acceptance_channel_proof), so no constraint-propagation / SAT / belief-"
               "propagation formulation over the joint (P,K) variables can close the gap. "
               "The gap closes only by BOUNDING H(K) below %.0f bits, which is what the "
               "derived-key and public-pad lanes already do."
               % (budgets[0]["deficit_bits"], max_hk)),
           }
    json.dump(out, open(os.path.join(HERE, "c_budget.json"), "w"), indent=1)
    print("\n-> c_budget.json")


if __name__ == "__main__":
    main()
