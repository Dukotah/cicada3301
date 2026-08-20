"""P0's own survival measurement: the dense prefilter's retention AT EACH PAD'S REAL SIZE.

Why this exists
---------------
Round 16's PREREG carries a single survival constant, 0.625, measured by
`lib_padsweep.control()` by planting in a 1 MB blob. Retention of the true offset inside a
fixed keep window is a RANK statistic, so it must fall as the number of competing offsets
grows. Lane P2 measured exactly that: 0.875 on a 6.4 MB pad, 0.500 on a 95 MB pad. This
lane's largest pad, `DATA_560.13`, is 118.8 MB — bigger than either — so inheriting 0.625
would overstate its effective coverage.

So: plant in each real pad and measure that pad's own rate.

Two criteria are reported, because they are not the same number:
  * `rank_lt_400` - the true offset is inside `dense_scan`'s keep window. Directly
    comparable to the round constant and to P2's figures.
  * `rank_lt_40`  - the true offset is inside the top 40 that `sweep.py` actually
    beam-escalates. THIS is the operative discount on this lane's coverage claim, and it
    is the stricter of the two.

    python control_at_scale.py [--trials 20] [--pads 560.13,...]

Writes control_at_scale.json incrementally, one pad at a time.
"""
import argparse, json, os, random, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))
import numpy as np                                        # noqa: E402
import lib_padsweep as L                                  # noqa: E402
from lib_padsweep import sk                               # noqa: E402

PADDIR = os.path.join(L.ROOT, "analysis", "round12", "A1", "pads")
FILES = {
    "560.13": "DATA_560.13",
    "_560.00_auth": "DATA__560.00.iso-authoritative",
    "560.17": "DATA_560.17",
    "prime_echo": "usr_local_bin_prime_echo",
    "tmp_folly": "tmp_folly",
}
PLAIN = ("THE PRIMES ARE SACRED AND THE TOTIENT FUNCTION IS SACRED ALL THINGS "
         "SHOULD BE ENCRYPTED KNOW THIS THAT THE INSTAR EMERGENCE IS AT HAND AND "
         "THE PILGRIM WHO SOLVES THE DEEP WEB SHALL FIND THE TRUTH WITHIN THE "
         "SACRED GEOMETRY OF THE CIRCUMFERENCE")
MAX_SKIP = L.MAX_SKIP


def run_pad(label, trials, seed, supp=0.83):
    path = os.path.join(PADDIR, FILES[label])
    blob = open(path, "rb").read()
    K = L.ks_mod29(blob)                       # numpy; never materialised as a list
    P = sk.eng_to_idx(PLAIN)
    need = len(P) * (MAX_SKIP + 4)
    n_off = len(K) - L.PREFILTER_LEN
    rng = random.Random(seed)
    rows = []
    for t in range(trials):
        o = rng.randrange(1000, len(K) - need - 8)
        W = [int(x) for x in K[o:o + need]]
        C, skips, used = sk.encipher_keyskip(P, W, sign=-1, supp=supp)
        hits = L.dense_scan(K, C, sign=-1, keep=400)
        rank = next((i for i, (s, oo) in enumerate(hits) if int(oo) == o), None)
        bd = sk.beam_decode(C, W, sign=-1, o=0, beam_w=500, max_skip=MAX_SKIP)
        match = sum(a == b for a, b in zip(bd["plain_idx"], P)) / len(P)
        rows.append({"trial": t, "o_true": o, "dense_rank": rank,
                     "beam_score": bd["score"], "match": match})
        print("  %-14s t%-2d o=%-11d rank=%-6s beam=%.3f match=%.3f"
              % (label, t, o, rank, bd["score"], match), flush=True)
    r400 = sum(1 for x in rows if x["dense_rank"] is not None)
    r40 = sum(1 for x in rows if x["dense_rank"] is not None and x["dense_rank"] < 40)
    rec = sum(1 for x in rows if x["match"] > 0.95)
    return {"pad": label, "file": FILES[label], "pad_bytes": len(blob),
            "competing_offsets": int(n_off), "trials": trials,
            "rank_lt_400": r400, "survival_rank_lt_400": r400 / trials,
            "rank_lt_40": r40, "survival_rank_lt_40": r40 / trials,
            "beam_recovered": rec, "beam_recovery_rate": rec / trials,
            "rows": rows}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=20)
    ap.add_argument("--pads", default=",".join(FILES))
    ap.add_argument("--seed", type=int, default=3301)
    ap.add_argument("--out", default=os.path.join(HERE, "control_at_scale.json"))
    a = ap.parse_args()
    res = {"note": "dense-prefilter survival measured IN EACH REAL PAD, not inherited from "
                   "the round's 1 MB constant. rank_lt_40 is the operative discount because "
                   "sweep.py escalates the top 40 per sign.",
           "keep": 400, "escalate_top": 40, "max_skip": MAX_SKIP, "pads": []}
    t0 = time.time()
    for lab in [x.strip() for x in a.pads.split(",") if x.strip()]:
        res["pads"].append(run_pad(lab, a.trials, a.seed))
        json.dump(res, open(a.out, "w"), indent=2)
    res["elapsed_s"] = round(time.time() - t0, 1)
    json.dump(res, open(a.out, "w"), indent=2)
    print("\n=== measured survival by pad size ===")
    print("%-14s %13s %8s %10s %10s %9s" % ("pad", "bytes", "trials", "surv<400",
                                            "surv<40", "beam"))
    for p in res["pads"]:
        print("%-14s %13s %8d %10.3f %10.3f %9s"
              % (p["pad"], format(p["pad_bytes"], ","), p["trials"],
                 p["survival_rank_lt_400"], p["survival_rank_lt_40"],
                 "%d/%d" % (p["beam_recovered"], p["trials"])))
