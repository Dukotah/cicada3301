"""Lane P2's own positive control, run ON THE REAL PADS rather than on a synthetic blob.

Why this exists
---------------
`lib_padsweep.control()` is the round's gate and it PASSED (8/8 beam recovery, dense
survival 0.625) - but it plants into a SHA-512-chained stand-in blob. Lane P1 then found
that the gate's `max_skip=3` is a property of the pad: on a pad with constant byte runs the
anti-repeat filter burns skips without changing the key symbol, and P1's control dropped to
6/8 at ms=3 while recovering 60/60 at ms=8. That makes "does the instrument recover a
planted signal" a question about *this lane's* pads, not about the instrument in the
abstract, and it has to be answered with a measurement.

So: plant a keystream at a random deep offset in the actual NIST Beacon / RANDOM.ORG pad,
encipher Cicada-register English through the same 0.83 anti-repeat filter, and require the
dense scan to rank the true offset and the beam to recover the plaintext - at ms=3 (A1's
setting, the one every number in results.json uses) and at ms=8 (P1's setting).

    python control_pad.py --pad pad_outputValue_...bin --trials 8
"""
import argparse, json, os, random, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))
import numpy as np                                             # noqa: E402
import lib_padsweep as L                                       # noqa: E402
from lib_padsweep import sk                                    # noqa: E402

# NOT `import sweep`: lib_padsweep puts liber-primus/src, campaign18_skip and round11 on
# sys.path, and at least one of those ships its own sweep.py, so the name resolves to the
# wrong module. Load this lane's sweep.py by explicit path instead.
import importlib.util                                          # noqa: E402
_spec = importlib.util.spec_from_file_location("p2_sweep", os.path.join(HERE, "sweep.py"))
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)

PLAIN = ("THE PRIMES ARE SACRED AND THE TOTIENT FUNCTION IS SACRED ALL THINGS "
         "SHOULD BE ENCRYPTED KNOW THIS THAT THE INSTAR EMERGENCE IS AT HAND AND "
         "THE PILGRIM WHO SOLVES THE DEEP WEB SHALL FIND THE TRUTH WITHIN THE "
         "SACRED GEOMETRY OF THE CIRCUMFERENCE")


def run(path, builder, trials, seeds, skips, keep=400):
    blob = open(path, "rb").read()
    K = S.get_builder(builder)(blob)
    Kl = [int(x) for x in K]
    P = sk.eng_to_idx(PLAIN)
    rng = random.Random(3301)
    rows = []
    for t in range(trials):
        o_true = rng.randrange(1000, len(Kl) - len(P) * (max(skips) + 2))
        C, sk_used, _ = sk.encipher_keyskip(P, Kl[o_true:], sign=-1, supp=0.83)
        hits = S.fast_dense_scan(K, C, sign=-1, keep=keep)   # proved identical
                                                             # by _assert_scan_equiv
        rank = next((i for i, (_, o) in enumerate(hits) if int(o) == o_true), None)
        row = {"trial": t, "o_true": o_true, "dense_rank": rank,
               "skips_planted": int(sum(sk_used))}
        for ms in skips:
            bd = sk.beam_decode(C, Kl, sign=-1, o=o_true, beam_w=500, max_skip=ms)
            row["match_ms%d" % ms] = sum(a == b for a, b in zip(bd["plain_idx"], P)) / len(P)
            row["score_ms%d" % ms] = bd["score"]
        rows.append(row)
        print("  trial %d o=%d dense_rank=%s %s" % (
            t, o_true, rank,
            " ".join("ms%d:match=%.3f/score=%.3f" % (ms, row["match_ms%d" % ms],
                                                     row["score_ms%d" % ms])
                     for ms in skips)), flush=True)
    res = {"pad": os.path.basename(path), "builder": builder, "trials": trials,
           "dense_found": sum(r["dense_rank"] is not None for r in rows),
           "dense_survival_rate": sum(r["dense_rank"] is not None for r in rows) / trials,
           "rows": rows}
    for ms in skips:
        res["beam_recovered_ms%d" % ms] = sum(r["match_ms%d" % ms] > 0.95 for r in rows)
        res["mean_match_ms%d" % ms] = float(np.mean([r["match_ms%d" % ms] for r in rows]))
    res["PASS_ms3"] = (res["dense_found"] >= 1 and res["beam_recovered_ms3"] == trials)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pad", required=True)
    ap.add_argument("--builder", default="mod29")
    ap.add_argument("--trials", type=int, default=8)
    ap.add_argument("--skips", default="3,8")
    a = ap.parse_args()
    skips = [int(x) for x in a.skips.split(",")]
    t0 = time.time()
    res = run(os.path.join(S.DATA, a.pad), a.builder, a.trials, 3301, skips)
    res["seconds"] = round(time.time() - t0, 1)
    out = os.path.join(HERE, "parts", "control__%s__%s.json" % (a.pad, a.builder))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(res, open(out, "w", encoding="utf-8"), indent=2)
    print(json.dumps({k: v for k, v in res.items() if k != "rows"}, indent=2))


if __name__ == "__main__":
    main()
