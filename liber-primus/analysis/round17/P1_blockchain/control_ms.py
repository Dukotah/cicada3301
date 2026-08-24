"""Lane P1 control, part 3: the skip-budget sweep and the END-TO-END detection power.

`control_ext.py` showed the beam loses recovery on the zero-run-heavy block-hash pad at
A1's `max_skip=3`.  This script (a) measures recovery across max_skip on both a zero-run
pad (`hash_display`) and a full-entropy blockchain pad (`merkle_display`), and (b) measures
the number that the lane's coverage bound is actually discounted by:

    P(dense prefilter retains the planted offset  AND  the escalated beam at that offset
      scores >= the -5.5 HIT bar)

which is the probability this lane would have SEEN a true pad had one been there.

  python control_ms.py     # -> control_ms.json
"""
import os, sys, json, random
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))
import lib_padsweep as L                                    # noqa: E402

PLAIN = ("THE PRIMES ARE SACRED AND THE TOTIENT FUNCTION IS SACRED ALL THINGS "
         "SHOULD BE ENCRYPTED KNOW THIS THAT THE INSTAR EMERGENCE IS AT HAND AND "
         "THE PILGRIM WHO SOLVES THE DEEP WEB SHALL FIND THE TRUTH WITHIN THE "
         "SACRED GEOMETRY OF THE CIRCUMFERENCE")
BAR = -5.5


def load(name):
    return open(os.path.join(HERE, "data", name), "rb").read()


def skip_sweep(blob, label, n=60, seed=3301, beam_w=500):
    P = L.sk.eng_to_idx(PLAIN)
    Kl = [int(x) for x in L.ks_mod29(blob)]
    res = {}
    for ms in (3, 5, 8):
        rng = random.Random(seed)
        sc, mt = [], []
        for _ in range(n):
            o = rng.randrange(1000, len(Kl) - len(P) * 10)
            C, _s, _u = L.sk.encipher_keyskip(P, Kl[o:], sign=-1, supp=0.83)
            bd = L.sk.beam_decode(C, Kl, sign=-1, o=o, beam_w=beam_w, max_skip=ms)
            sc.append(bd["score"])
            mt.append(sum(a == b for a, b in zip(bd["plain_idx"], P)) / len(P))
        sc, mt = np.array(sc), np.array(mt)
        res[str(ms)] = {"n": n, "recovered_0.95": float((mt > 0.95).mean()),
                        "score_clears_bar": float((sc >= BAR).mean()),
                        "median_score": float(np.median(sc))}
        print("  %-18s max_skip=%d  recovered@0.95=%.3f  score>=%.1f=%.3f"
              % (label, ms, res[str(ms)]["recovered_0.95"], BAR,
                 res[str(ms)]["score_clears_bar"]), flush=True)
    return res


def end_to_end(blob, label, n=24, seed=90210, max_skip=8):
    P = L.sk.eng_to_idx(PLAIN)
    K = L.ks_mod29(blob)
    Kl = [int(x) for x in K]
    rows = []
    for t in range(n):
        rng = random.Random(seed + t)
        o = rng.randrange(1000, len(Kl) - len(P) * 10)
        C, _s, _u = L.sk.encipher_keyskip(P, Kl[o:], sign=-1, supp=0.83)
        hits = L.dense_scan(K, C[:L.PREFILTER_LEN], sign=-1)
        rank = next((i for i, (s, oo) in enumerate(hits) if int(oo) == o), None)
        bd = L.sk.beam_decode(C[:L.HEAD], Kl, sign=-1, o=o,
                              beam_w=L.BEAM_W, max_skip=max_skip)
        seen = (rank is not None) and (bd["score"] >= BAR)
        rows.append({"offset": o, "rank": rank, "score": bd["score"], "seen": bool(seen)})
        print("    %s t=%d o=%d rank=%s score=%.3f seen=%s"
              % (label, t, o, rank, bd["score"], seen), flush=True)
    det = sum(r["seen"] for r in rows) / n
    surv = sum(r["rank"] is not None for r in rows) / n
    print("  %-18s END-TO-END detection power = %d/%d = %.3f "
          "(dense survival %.3f)" % (label, sum(r["seen"] for r in rows), n, det, surv),
          flush=True)
    return {"n": n, "max_skip": max_skip, "detection_power": det,
            "dense_survival": surv, "rows": rows}


if __name__ == "__main__":
    out = {"bar": BAR}
    print("skip-budget sweep:")
    out["skip_sweep_hash_display"] = skip_sweep(load("hash_display.bin"), "hash_display")
    out["skip_sweep_merkle_display"] = skip_sweep(load("merkle_display.bin"),
                                                  "merkle_display")
    print("end-to-end detection power (dense retained AND beam clears the bar):")
    out["e2e_hash_display"] = end_to_end(load("hash_display.bin"), "hash_display")
    out["e2e_merkle_display"] = end_to_end(load("merkle_display.bin"), "merkle_display")
    with open(os.path.join(HERE, "control_ms.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: (v if not isinstance(v, dict) else
                          {kk: vv for kk, vv in v.items() if kk != "rows"})
                      for k, v in out.items()}, indent=2))
