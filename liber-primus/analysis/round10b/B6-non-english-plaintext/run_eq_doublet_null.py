"""B6 run 6 (resume) — adjudicate the D6 equality-pattern channel against a
DOUBLET-MATCHED null.

run_lang.token_search reported two channels but gated HIT on the difference
channel only.  The equality channel (invariant under ALL 29! monoalphabetic
substitutions, hence the broadest token instrument in the lane) showed 21 of 44
tokens above the shuffle-null maximum, which read naively would be 21 "hits".

Inspection says that is the known anti-repeat rewrite, not tokens: every token
whose spelling contains a REPEATED rune (HTTP, ADDRESS, HIDDEN, MESSAGE, DEGREE,
THREE) comes in far BELOW the shuffle null, and every token spelled with all
DISTINCT runes comes in above it.  A shuffle null is therefore the wrong null for
this channel.

This script re-runs the equality channel against a doublet-matched null (soft
anti-repeat, p_keep = 0.18 over a memoryless base, the characterisation in
research/ROUND-7-GATE1-SYNTHESIS.md), which reproduces LP2's 0.66% doublet rate.
Under that null the confound is charged to the null, and a surviving token would
be a genuine hit.

This TIGHTENS the pre-registered rule (same statistic, strictly better null); it
does not relax it.  Pre-registered gate is unchanged: HIT iff the real count
exceeds the null ensemble maximum at the same corpus size.
"""
import json
import os
import sys
import time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import detectors as D
import run_lang as RL

HERE = os.path.dirname(os.path.abspath(__file__))
RNG = np.random.default_rng(1337)
NREP = 40


def doublet_suppressed(n, rng, pkeep=0.18):
    x = np.empty(n, dtype=np.int64)
    x[0] = rng.integers(D.N)
    for i in range(1, n):
        v = int(rng.integers(D.N))
        while v == x[i - 1] and rng.random() > pkeep:
            v = int(rng.integers(D.N))
        x[i] = v
    return x


def main():
    pages, stream = D.load_unsolved()
    toks = RL._tokens()
    t0 = time.time()

    real = RL.eq_pattern_hits(stream, toks)
    real_rev = RL.eq_pattern_hits(stream[::-1], toks)
    print("real eq done %.1fs" % (time.time() - t0), flush=True)

    nd = {}
    rates = []
    for rep in range(NREP):
        s = doublet_suppressed(len(stream), RNG)
        rates.append(float((s[1:] == s[:-1]).mean()))
        for k, v in RL.eq_pattern_hits(s, toks).items():
            nd.setdefault(k, []).append(v)
        if rep % 10 == 0:
            print("  null %d  %.1fs" % (rep, time.time() - t0), flush=True)

    obs = float((stream[1:] == stream[:-1]).mean())
    print("doublet rate: real %.4f%%  null mean %.4f%%" %
          (100 * obs, 100 * np.mean(rates)), flush=True)

    out, hits = {}, []
    for cls, t, r in toks:
        if t not in nd:
            continue
        a = np.array(nd[t], dtype=float)
        rv = max(real.get(t, 0), real_rev.get(t, 0))
        z = (rv - a.mean()) / a.std(ddof=1) if a.std(ddof=1) > 0 else 0.0
        hit = bool(rv > a.max())
        out[t] = {"class": cls, "len": int(len(r)),
                  "has_repeat": bool(len(set(r.tolist())) < len(r)),
                  "eq_fwd": int(real.get(t, 0)), "eq_rev": int(real_rev.get(t, 0)),
                  "null_mean": float(a.mean()), "null_sd": float(a.std(ddof=1)),
                  "null_max": float(a.max()), "z": float(z), "HIT": hit}
        if hit:
            hits.append(t)

    json.dump({"doublet_rate_real": obs, "doublet_rate_null": float(np.mean(rates)),
               "nrep": NREP, "tokens": out, "hits": hits},
              open(os.path.join(HERE, "eq_doublet_null.json"), "w"), indent=1)

    print("\nHITS under doublet-matched null: %d / %d  %s" %
          (len(hits), len(out), hits), flush=True)
    for t in sorted(out, key=lambda k: -out[k]["z"])[:12]:
        v = out[t]
        print("%-22s rep=%-5s real=%-7d null_mean=%-10.1f null_max=%-8.0f z=%+.2f %s" %
              (t, v["has_repeat"], max(v["eq_fwd"], v["eq_rev"]), v["null_mean"],
               v["null_max"], v["z"], "HIT" if v["HIT"] else ""), flush=True)
    print("total %.1fs" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
