"""Extended control for lane P1.

`lib_padsweep.control()` on the REAL blockchain pad returned 6/8 beam recoveries, i.e.
PASS=False under its strict `recovered == n_trials` rule, where the PREREG run on the
synthetic stand-in pad returned 8/8.  Two explanations:

  (a) the instrument is weaker on THIS pad -> the lane must report INCONCLUSIVE;
  (b) the instrument recovers ~85-90 % of plants everywhere and PREREG's 8/8 was a small
      sample -> the lane's control is fine and the recovery rate is the honest discount.

This script separates them: the same plant-and-recover trial, many times, on the real
blockchain pad and on the PREREG synthetic pad, with the same seed sequence, and it
records the number of filter skips per trial so a failure can be attributed.

  python control_ext.py            # -> control_ext.json
"""
import os, sys, json, random, hashlib
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))
import lib_padsweep as L                                    # noqa: E402

PLAIN = ("THE PRIMES ARE SACRED AND THE TOTIENT FUNCTION IS SACRED ALL THINGS "
         "SHOULD BE ENCRYPTED KNOW THIS THAT THE INSTAR EMERGENCE IS AT HAND AND "
         "THE PILGRIM WHO SOLVES THE DEEP WEB SHALL FIND THE TRUTH WITHIN THE "
         "SACRED GEOMETRY OF THE CIRCUMFERENCE")


def synth_pad():
    b = hashlib.sha512(b"ROUND16-CONTROL-PAD").digest()
    while len(b) < (1 << 20):
        b += hashlib.sha512(b[-64:]).digest()
    return b


def recover_trials(blob, n=60, seed=3301, beam_w=500, label=""):
    rng = random.Random(seed)
    P = L.sk.eng_to_idx(PLAIN)
    K = L.ks_mod29(blob)
    Kl = [int(x) for x in K]
    rows = []
    for t in range(n):
        o = rng.randrange(1000, len(Kl) - len(P) * (L.MAX_SKIP + 2))
        C, skips, used = L.sk.encipher_keyskip(P, Kl[o:], sign=-1, supp=0.83)
        bd = L.sk.beam_decode(C, Kl, sign=-1, o=o, beam_w=beam_w, max_skip=L.MAX_SKIP)
        m = sum(a == b for a, b in zip(bd["plain_idx"], P)) / len(P)
        rows.append({"trial": t, "offset": o, "skips": int(sum(skips)),
                     "score": bd["score"], "match": m})
    r95 = sum(x["match"] > 0.95 for x in rows) / n
    r75 = sum(x["match"] > 0.75 for x in rows) / n
    print("  %-22s n=%d  recovered@0.95=%.3f  @0.75=%.3f  median match=%.3f"
          % (label, n, r95, r75, float(np.median([x["match"] for x in rows]))), flush=True)
    return {"label": label, "n": n, "rate_0.95": r95, "rate_0.75": r75,
            "median_match": float(np.median([x["match"] for x in rows])), "rows": rows}


def dense_survival(blob, n=24, seed=90210, label=""):
    """Fraction of planted offsets the dense prefilter retains in its keep window."""
    rng = random.Random(seed)
    P = L.sk.eng_to_idx(PLAIN)
    K = L.ks_mod29(blob)
    Kl = [int(x) for x in K]
    ranks = []
    for t in range(n):
        o = rng.randrange(1000, len(Kl) - len(P) * (L.MAX_SKIP + 2))
        C, skips, used = L.sk.encipher_keyskip(P, Kl[o:], sign=-1, supp=0.83)
        hits = L.dense_scan(K, C, sign=-1)
        rank = next((i for i, (s, oo) in enumerate(hits) if int(oo) == o), None)
        ranks.append(rank)
        print("    dense trial %d o=%d rank=%s" % (t, o, rank), flush=True)
    found = sum(r is not None for r in ranks)
    print("  %-22s dense survival = %d/%d = %.3f" % (label, found, n, found / n), flush=True)
    return {"label": label, "n": n, "found": found, "survival_rate": found / n,
            "ranks": ranks}


if __name__ == "__main__":
    real = open(os.path.join(HERE, "data", "hash_display.bin"), "rb").read()
    syn = synth_pad()
    out = {}
    print("beam recovery, 60 plants each:")
    out["recover_real"] = recover_trials(real, 60, label="blockchain hash_display")
    out["recover_synth"] = recover_trials(syn, 60, label="PREREG synthetic pad")
    print("beam recovery at beam_w=1500 (power check on the real pad):")
    out["recover_real_w1500"] = recover_trials(real, 60, beam_w=1500,
                                               label="blockchain, beam_w=1500")
    print("dense prefilter survival on the real pad:")
    out["dense_real"] = dense_survival(real, 24, label="blockchain hash_display")
    for k in out:
        out[k].pop("rows", None) if k.startswith("zz") else None
    with open(os.path.join(HERE, "control_ext.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk not in ("rows", "ranks")}
                      for k, v in out.items()}, indent=2))
