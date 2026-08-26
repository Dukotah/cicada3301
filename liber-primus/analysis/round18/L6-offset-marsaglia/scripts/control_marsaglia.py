"""L6 / sub-lane B POSITIVE CONTROL — planted and recovered ON THE REAL MARSAGLIA BYTES.

PREREG s5.4.  Round 17 / lane P1 found `max_skip=3` underpowered on pads with constant
byte runs: its strict control FAILED ON ITS REAL PAD (6/8 plants) and passed 60/60 at
ms=8.  A control that only passes on a synthetic pad proves nothing about this pad, so
every plant below goes into bytes that came off the verified CDROM.

ms=3 is run alongside ms=8 as a DIAGNOSTIC, so whether the constant-run defect bites on
Marsaglia is measured here rather than assumed either way (P0 found it does not bite on
high-entropy ISO-carved blobs; the ISO also carries filesystem padding, so it is measured).

GATE: rune recovery > 0.95 on 16/16 trials at ms=8.  Below that sub-lane B reports
INCONCLUSIVE, never NEGATIVE.
"""
import os, sys, json, random, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import lib_l6 as X
import lib_padsweep as L
import skipdecode as sk

N_TRIALS = 16
KEEP = 1000
TOP = 40
SEED = 3301
PLAIN = ("THE PRIMES ARE SACRED AND THE TOTIENT FUNCTION IS SACRED ALL THINGS SHOULD BE "
         "ENCRYPTED KNOW THIS THAT THE INSTAR EMERGENCE IS AT HAND AND THE PILGRIM WHO "
         "SOLVES THE DEEP WEB SHALL FIND THE TRUTH WITHIN THE SACRED GEOMETRY OF THE "
         "CIRCUMFERENCE A WARNING BELIEVE NOTHING FROM THIS BOOK EXCEPT WHAT YOU KNOW TO "
         "BE TRUE TEST THE KNOWLEDGE FIND YOUR TRUTH EXPERIENCE YOUR DEATH")


def pad_stats(a):
    """The statistic that decides whether ms=3 is safe: constant-run structure."""
    d = np.diff(a.astype(np.int32)) != 0
    idx = np.flatnonzero(d)
    runs = np.diff(np.concatenate(([-1], idx, [a.size - 1])))
    return {"bytes": int(a.size), "zero_byte_pct": float(100.0 * np.count_nonzero(a == 0) / a.size),
            "longest_constant_run": int(runs.max()), "mean_run": float(runs.mean()),
            "distinct_bytes": int(np.unique(a).size)}


def main():
    man = json.load(open(os.path.join(X.DATA, "MANIFEST.json")))
    assert man.get("all_gates_pass"), "hash gates did not pass - refusing to sweep"
    pads = man["verified_pads"]
    L.trigram_model()
    P = sk.eng_to_idx(PLAIN)
    rng = random.Random(SEED)
    out = {"lane": "round18/L6 sub-lane B (MARSAGLIA)", "n_trials": N_TRIALS,
           "keep": KEEP, "escalate_top": TOP, "plaintext_runes": len(P),
           "pads_available": len(pads), "by_ms": {}, "pad_stats": {}}

    # one big real chunk, taken from the verified random-data files, plus the ISO itself
    sources = []
    for nm in ("BITS.01", "CALIF.BIT", "BITS.30", "GERMANY.BIT"):
        m = next((p for p in pads if p["name"] == nm), None)
        if m:
            fp = os.path.join(X.DATA, "iso", m["extracted"])
            sources.append((nm, np.fromfile(fp, dtype=np.uint8)))
    iso = np.fromfile(os.path.join(X.DATA, "MARSAGLIA_CDROM.iso"), dtype=np.uint8,
                      count=1 << 24)
    sources.append(("MARSAGLIA_CDROM.iso[0:16MiB]", iso))
    for nm, a in sources:
        out["pad_stats"][nm] = pad_stats(a)
        print(f"  {nm}: {out['pad_stats'][nm]}", flush=True)

    for ms in (8, 3):
        rows = []
        for t in range(N_TRIALS):
            nm, a = sources[t % len(sources)]
            K = X.build_full(a, "mod29")
            Kl = [int(x) for x in K]
            o_true = rng.randrange(1000, len(Kl) - len(P) * (ms + 2) - 16)
            C, skips, used = sk.encipher_keyskip(P, Kl[o_true:], sign=-1, supp=0.83)
            hits = L.dense_scan(K, C, sign=-1, keep=KEEP)
            rank = next((i for i, (s, o) in enumerate(hits) if int(o) == o_true), None)
            bd = sk.beam_decode([int(x) for x in C], Kl, sign=-1, o=o_true,
                                beam_w=X.BEAM_W2, max_skip=ms)
            match = sum(1 for x, y in zip(bd["plain_idx"], P) if x == y) / len(P)
            rows.append({"trial": t, "pad": nm, "o_true": o_true, "dense_rank": rank,
                         "beam_score": bd["score"], "rune_match": match,
                         "skips_planted": int(sum(skips))})
            print(f"  ms={ms} t{t:>2} {nm:<28} o={o_true:>9d} rank={rank} "
                  f"beam={bd['score']:+.3f} match={match:.3f}", flush=True)
            del K, Kl
        rec = sum(1 for r in rows if r["rune_match"] > 0.95)
        sur = sum(1 for r in rows if r["dense_rank"] is not None)
        sur40 = sum(1 for r in rows if r["dense_rank"] is not None and r["dense_rank"] < TOP)
        out["by_ms"][str(ms)] = {"recovered": rec, "recovery": rec / N_TRIALS,
                                 "dense_found": sur, "survival": sur / N_TRIALS,
                                 "survival_at_top40": sur40 / N_TRIALS, "rows": rows}
        print(f"  == ms={ms}: recovery {rec}/{N_TRIALS}  survival(keep={KEEP}) "
              f"{sur}/{N_TRIALS}  survival(top{TOP}) {sur40}/{N_TRIALS}", flush=True)

    out["PASS"] = out["by_ms"]["8"]["recovery"] >= 0.95
    out["ms3_bites_here"] = out["by_ms"]["3"]["recovery"] < out["by_ms"]["8"]["recovery"]
    X.jdump(out, os.path.join(X.OUT, "control_marsaglia.json"))
    print("CONTROL B:", "PASS" if out["PASS"] else "FAIL",
          "| ms=3 underpowered on this pad:", out["ms3_bites_here"])
    return 0 if out["PASS"] else 1


if __name__ == "__main__":
    sys.exit(main())
