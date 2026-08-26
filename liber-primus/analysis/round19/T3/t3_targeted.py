"""T3 — the TARGETED arm. The realistic transcription error, not a uniform one.

Three models, all pre-registered in PREREG §3:
  P-OAE450   the 450 located disagreements, flipped to the clusterer's OWN alternative
  P-OAE450R  the 450 located disagreements, random direction inside {O,A,AE}
  P-OAEFAM   any O/A/AE position in the stream, random direction inside the family
plus the ALL-450 point (k=450, the whole located set, which is a single deterministic
stream) and P-COLLAPSE (the published maximum-damage case), both exact.

Run: python3 t3_targeted.py     (writes out_targeted.json)
"""
import json, os, random, statistics, collections
import t3_lib as T
from t3_sensitivity import band, crossings, run_model, FLOORS

HERE = os.path.dirname(os.path.abspath(__file__))
TRIALS = 400
KGRID_450 = [1, 2, 5, 10, 20, 50, 100, 200, 300, 450]


def main():
    C = T.stream()
    recs = T.oae450()
    fam = T.oae_family_positions(C)
    out = {"baseline_sha256": T.sha_of(C), "trials": TRIALS, "floors": FLOORS,
           "n_located": len(recs), "n_family": len(fam)}

    # --- how much doublet potential does the located set even have? ---
    # A flip at position p can add a doublet only if a NEIGHBOUR is the rune it becomes.
    pot = {"gain2": 0, "gain1": 0, "gain0": 0, "loses": 0}
    per = []
    for r in recs:
        p, cur, alt = r["pos"], r["canon_idx"], r["alt_idx"]
        L = C[p - 1] if p > 0 else None
        R = C[p + 1] if p < len(C) - 1 else None
        before = (L == cur) + (R == cur)
        after = (L == alt) + (R == alt)
        g = after - before
        per.append(g)
        if g == 2:
            pot["gain2"] += 1
        elif g == 1:
            pot["gain1"] += 1
        elif g <= -1:
            pot["loses"] += 1
        else:
            pot["gain0"] += 1
    pot["net_if_all_450_flipped"] = sum(per)
    pot["neighbour_is_OAE"] = sum(1 for r in recs
                                  if (r["pos"] > 0 and C[r["pos"] - 1] in T.OAE_IDX)
                                  or (r["pos"] < len(C) - 1 and C[r["pos"] + 1] in T.OAE_IDX))
    print("located-set doublet potential:", json.dumps(pot))
    out["located_doublet_potential"] = pot

    # --- the whole located set flipped, exactly (one deterministic stream) ---
    Call = list(C)
    for r in recs:
        Call[r["pos"]] = r["alt_idx"]
    b_all = T.bundle(Call)
    print("ALL-450 (clusterer's own alternative):",
          json.dumps({k: b_all[k] for k in T.CHEAP_KEYS}))
    out["ALL450_exact"] = b_all

    # --- adversarial WITHIN the located set: choose the direction that maximises doublets
    Cadv = list(C)
    for r in recs:
        p, cur = r["pos"], r["canon_idx"]
        L = Cadv[p - 1] if p > 0 else -1
        R = Cadv[p + 1] if p < len(C) - 1 else -1
        best, bg = cur, 0
        for alt in T.OAE_IDX:
            if alt == cur:
                continue
            g = ((L == alt) + (R == alt)) - ((L == cur) + (R == cur))
            if g > bg:
                best, bg = alt, g
        Cadv[p] = best
    b_adv = T.bundle(Cadv)
    print("ALL-450 adversarial-within-family:",
          json.dumps({k: b_adv[k] for k in T.CHEAP_KEYS}))
    out["ALL450_adversarial_within_family"] = b_adv

    # --- adversarial over the WHOLE family (worst case a pure O/A/AE confusion can do)
    Cfam = list(C)
    for p in fam:
        cur = Cfam[p]
        L = Cfam[p - 1] if p > 0 else -1
        R = Cfam[p + 1] if p < len(C) - 1 else -1
        best, bg = cur, 0
        for alt in T.OAE_IDX:
            if alt == cur:
                continue
            g = ((L == alt) + (R == alt)) - ((L == cur) + (R == cur))
            if g > bg:
                best, bg = alt, g
        Cfam[p] = best
    b_fam = T.bundle(Cfam)
    print("ALL-FAMILY adversarial-within-family:",
          json.dumps({k: b_fam[k] for k in T.CHEAP_KEYS}))
    out["ALLFAMILY_adversarial_within_family"] = b_fam

    # --- P-COLLAPSE (published max-damage), on the pinned stream, full bundle
    col = T.p_collapse(C)
    out["P-COLLAPSE"] = {k: v for k, v in T.bundle(col).items()}
    print("P-COLLAPSE:", json.dumps({k: out['P-COLLAPSE'][k] for k in T.CHEAP_KEYS}))

    # --- the sampled curves ---
    print("P-OAE450")
    r1 = run_model(C, "P-OAE450", T.p_oae450, KGRID_450, TRIALS, 5501,
                   pool_kw={"recs": recs})
    out["P-OAE450"] = {"rows": r1, "crossings": crossings(r1)}

    print("P-OAE450R")
    r2 = run_model(C, "P-OAE450R", T.p_oae450r, KGRID_450, TRIALS, 5502,
                   pool_kw={"recs": recs})
    out["P-OAE450R"] = {"rows": r2, "crossings": crossings(r2)}

    print("P-OAEFAM")
    kf = [k for k in [1, 2, 5, 10, 20, 50, 100, 200, 450, 800, 1200] if k <= len(fam)]
    kf.append(len(fam))
    r3 = run_model(C, "P-OAEFAM", T.p_oaefam, sorted(set(kf)), TRIALS, 5503,
                   pool_kw={"pool": fam})
    out["P-OAEFAM"] = {"rows": r3, "crossings": crossings(r3)}

    json.dump(out, open(os.path.join(HERE, "out_targeted.json"), "w"), indent=1)
    print("wrote out_targeted.json")


if __name__ == "__main__":
    main()
