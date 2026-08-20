"""P0 skip-budget control: is A1's `max_skip=3` adequate ON THESE PADS?

Lane P1 found that `max_skip=3` FAILS on a pad containing long constant byte runs (its pad
was 18.4% zero bytes): a constant key symbol means a forced skip does not change the key
value, so the filter burns several skips in a row and the true path falls outside a budget
of 3. At `max_skip=8` P1 recovered 60/60.

That is a property of the PAD, not of the decoder, so it has to be measured on this lane's
own pads rather than inherited. This script plants a known keystream at a random deep offset
in each REAL pad, enciphers under the anti-repeat filter, and reports beam recovery at
max_skip=3 (A1's, for comparability) and max_skip=8 (P1's powered setting), plus the skip
distribution that drives the difference.

    python control_skip.py [--trials 12] [--pads 560.13,_560.00_auth,...]

Writes control_skip.json incrementally, one pad at a time.
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


def pad_stats(b):
    a = np.frombuffer(b, dtype=np.uint8)
    d = np.flatnonzero(a[1:] != a[:-1])
    runs = np.diff(np.concatenate(([-1], d, [len(a) - 1])))
    return {"bytes": int(len(a)), "zero_frac": float((a == 0).mean()),
            "adj_equal_frac": float((a[1:] == a[:-1]).mean()),
            "max_const_run": int(runs.max()),
            "frac_bytes_in_runs_ge8": float(runs[runs >= 8].sum() / len(a))}


def run_pad(label, trials, ms_list, supp, seed):
    path = os.path.join(PADDIR, FILES[label])
    blob = open(path, "rb").read()
    st = pad_stats(blob)
    K = L.ks_mod29(blob)
    P = sk.eng_to_idx(PLAIN)
    need = len(P) * (max(ms_list) + 4)
    rng = random.Random(seed)
    rows = []
    for t in range(trials):
        o = rng.randrange(1000, len(K) - need - 8)
        W = [int(x) for x in K[o:o + need]]
        C, skips, used = sk.encipher_keyskip(P, W, sign=-1, supp=supp)
        row = {"trial": t, "o_true": o, "total_skips": int(sum(skips)),
               "max_consecutive_skip": int(max(skips)) if len(skips) else 0}
        for ms in ms_list:
            bd = sk.beam_decode(C, W, sign=-1, o=0, beam_w=500, max_skip=ms)
            row["match_ms%d" % ms] = sum(a == b for a, b in zip(bd["plain_idx"], P)) / len(P)
            row["score_ms%d" % ms] = bd["score"]
        rows.append(row)
        print("  %-14s t%-2d o=%-11d skips=%-3d maxrun=%d  %s" % (
            label, t, o, row["total_skips"], row["max_consecutive_skip"],
            "  ".join("ms%d match=%.3f" % (ms, row["match_ms%d" % ms]) for ms in ms_list)),
            flush=True)
    out = {"pad": label, "file": FILES[label], "pad_stats": st,
           "trials": trials, "supp": supp, "beam_w": 500, "rows": rows}
    for ms in ms_list:
        r = sum(1 for x in rows if x["match_ms%d" % ms] > 0.95)
        out["recovered_ms%d" % ms] = r
        out["recovery_rate_ms%d" % ms] = r / trials
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=12)
    ap.add_argument("--pads", default=",".join(FILES))
    ap.add_argument("--ms", default="3,8")
    ap.add_argument("--supp", type=float, default=0.83)
    ap.add_argument("--seed", type=int, default=3301)
    ap.add_argument("--out", default=os.path.join(HERE, "control_skip.json"))
    a = ap.parse_args()
    ms_list = [int(x) for x in a.ms.split(",")]
    res = {"note": "beam recovery of a PLANTED keystream in each real pad, at A1's "
                   "max_skip=3 and P1's max_skip=8",
           "ms_list": ms_list, "pads": []}
    t0 = time.time()
    for lab in [x.strip() for x in a.pads.split(",") if x.strip()]:
        res["pads"].append(run_pad(lab, a.trials, ms_list, a.supp, a.seed))
        json.dump(res, open(a.out, "w"), indent=2)     # incremental
    res["elapsed_s"] = round(time.time() - t0, 1)
    json.dump(res, open(a.out, "w"), indent=2)
    print("\n=== skip-budget control ===")
    for p in res["pads"]:
        print("%-14s zero=%.3f maxrun=%-3d  %s" % (
            p["pad"], p["pad_stats"]["zero_frac"], p["pad_stats"]["max_const_run"],
            "  ".join("ms%d %d/%d" % (ms, p["recovered_ms%d" % ms], p["trials"])
                      for ms in ms_list)))
