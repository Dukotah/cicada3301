"""L6 / sub-lane A POSITIVE CONTROL — plant and recover through the SAME pipeline.

PREREG s3.4.  Round 18 rule 2 / AGENTS.md s4 lesson 1: a null from an unvalidated
instrument is not a negative.  So before sub-lane A's silence means anything, a known
signal is planted at a deep, unknown offset in a REAL derived keystream (a real B-04
dictionary seed, a real generator, a real reduction - not a synthetic hash chain) and
pushed through the identical dense_scan -> tier-1 beam path at ms=8.

Reported:
  recovery  fraction of trials the beam recovers >95% of RUNE INDICES at the true offset
            (AGENTS.md s4 lesson 4: rune indices, not the transliteration string)
  survival  fraction of trials the dense prefilter keeps the true offset at all
            -- this lane's MEASURED coverage discount.  No 0.625 constant is used
            anywhere; R17 measured 0.375-0.875, non-monotone.
  pipeline  fraction of trials where the true offset also comes FIRST out of tier-1 beam

GATE (PREREG s3.4): recovery >= 0.95.  Below that sub-lane A reports INCONCLUSIVE.
"""
import os, sys, json, random, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import lib_l6 as X
import lib_padsweep as L
import skipdecode as sk

N_TRIALS = 40
KEEP = 1000
TOP = 40          # identical to the sweep's escalation depth, so the control
                  # measures the pipeline the sweep actually runs
SEED = 3301

PLAIN = ("THE PRIMES ARE SACRED AND THE TOTIENT FUNCTION IS SACRED ALL THINGS SHOULD BE "
         "ENCRYPTED KNOW THIS THAT THE INSTAR EMERGENCE IS AT HAND AND THE PILGRIM WHO "
         "SOLVES THE DEEP WEB SHALL FIND THE TRUTH WITHIN THE SACRED GEOMETRY OF THE "
         "CIRCUMFERENCE A WARNING BELIEVE NOTHING FROM THIS BOOK EXCEPT WHAT YOU KNOW TO "
         "BE TRUE TEST THE KNOWLEDGE FIND YOUR TRUTH EXPERIENCE YOUR DEATH DO NOT EDIT OR "
         "CHANGE THIS BOOK OR THE MESSAGE CONTAINED WITHIN EITHER THE WORDS OR THEIR "
         "NUMBERS FOR ALL IS SACRED")


def main():
    L.trigram_model()
    cfgs = [c for c in X.mine_configs() if c["kind"] == "b04"]
    # 8 distinct real configs, spread across generator families and reductions
    picked, seen_g = [], set()
    for c in cfgs:
        g = (c["gen"], c["red"])
        if g in seen_g:
            continue
        seen_g.add(g)
        picked.append(c)
        if len(picked) >= 8:
            break
    assert len(picked) >= 8, f"only {len(picked)} distinct real configs available"

    P = sk.eng_to_idx(PLAIN)
    nsym = X.OFF_MAX_A1 + X.SPAN + len(P) * (X.MS + 2) + 1024
    rng = random.Random(SEED)
    rows = []
    t0 = time.time()
    # Trials are GROUPED BY CONFIG so each (expensive) derived keystream is built once.
    per = N_TRIALS // len(picked)
    order = [picked[i // per] for i in range(per * len(picked))]
    while len(order) < N_TRIALS:
        order.append(picked[len(order) % len(picked)])
    K = Kl = None
    last = None
    for t in range(N_TRIALS):
        cfg = order[t]
        ck = (cfg["gen"], cfg["red"], cfg["seed_hex"], cfg.get("dir", "fwd"))
        if ck != last:
            K = X.derived_keystream(cfg, nsym)
            Kl = [int(x) for x in K]
            last = ck
        o_true = rng.randrange(1000, X.OFF_MAX_A1)
        C, skips, used = sk.encipher_keyskip(P, Kl[o_true:], sign=cfg["sign"], supp=0.83)

        hits = L.dense_scan(K, C, sign=cfg["sign"], keep=KEEP)
        rank = next((i for i, (s, o) in enumerate(hits) if int(o) == o_true), None)

        esc = X.escalate(hits, Kl, C, cfg["sign"], top=TOP,
                         head=min(X.HEAD, len(C)), ms=X.MS, beam_w=X.BEAM_W)
        first_is_true = bool(esc and int(esc[0]["offset"]) == o_true)

        bd = sk.beam_decode([int(x) for x in C], Kl, sign=cfg["sign"], o=o_true,
                            beam_w=X.BEAM_W2, max_skip=X.MS)
        match = sum(1 for a, b in zip(bd["plain_idx"], P) if a == b) / len(P)
        rows.append({"trial": t, "gen": cfg["gen"], "red": cfg["red"],
                     "seed": cfg.get("label"), "sign": cfg["sign"],
                     "o_true": o_true, "dense_rank": rank,
                     "pipeline_first": first_is_true,
                     "beam_score": bd["score"], "rune_match": match,
                     "skips_planted": int(sum(skips))})
        print(f"  t{t:>2} {cfg['gen']:>16}|{cfg['red']:<6} o={o_true:>8d} "
              f"rank={rank} first={first_is_true} beam={bd['score']:+.3f} "
              f"match={match:.3f}", flush=True)

    rec = sum(1 for r in rows if r["rune_match"] > 0.95)
    sur = sum(1 for r in rows if r["dense_rank"] is not None)
    pipe = sum(1 for r in rows if r["pipeline_first"])
    out = {"lane": "round18/L6 sub-lane A (OFFSET)", "n_trials": N_TRIALS,
           "max_skip": X.MS, "keep": KEEP, "escalate_top": TOP,
           "off_max": X.OFF_MAX_A1, "plaintext_runes": len(P),
           "configs_used": [{k: v for k, v in c.items() if k != "prior_score"}
                            for c in picked],
           "recovery": rec / N_TRIALS, "recovered": rec,
           "survival": sur / N_TRIALS, "dense_found": sur,
           "pipeline_first": pipe / N_TRIALS,
           "GATE_recovery_ge_0.95": rec / N_TRIALS >= 0.95,
           "elapsed_s": time.time() - t0, "rows": rows}
    out["PASS"] = out["GATE_recovery_ge_0.95"]
    X.jdump(out, os.path.join(X.OUT, "control_offset.json"))
    print(f"\nrecovery {rec}/{N_TRIALS} = {rec/N_TRIALS:.3f}   "
          f"survival {sur}/{N_TRIALS} = {sur/N_TRIALS:.3f}   "
          f"pipeline-first {pipe}/{N_TRIALS} = {pipe/N_TRIALS:.3f}")
    print("CONTROL A:", "PASS" if out["PASS"] else "FAIL")
    return 0 if out["PASS"] else 1


if __name__ == "__main__":
    sys.exit(main())
