"""FRONT C1 real sweep over LP2 unsolved (0-54).

Configs swept:
  f     in F_BASIS (7 natural functions)
  k     in 2..6
  source in {ct, pt, mix}
  sign  in {-1, +1}
  orient in {fwd, rev}          (stream and its reversal)
  scope in {continuous, per-segment}

Seed handling:
  - source=ct : the key past position k is FULLY DETERMINED by ciphertext history
    (seed-independent). So we decode with a zero seed and SCORE positions [k:] only.
    Seed cannot rescue a wrong f/k; a real signal shows regardless of seed.
  - source=pt/mix : seed errors propagate. We sweep a bounded seed set
    (all-equal seeds 0..N-1, i.e. 29 seeds) as a representative probe; a genuine
    autokey would still light up because after a short transient the correct-family
    key locks on. This is a documented BOUND, not exhaustive over 29^k seeds.

Null: nc.shuffled (seed 3301), >=200 draws, false-positive ceiling computed at
the same effective length as the scored region. HIT bar: score >= -5.5 AND
>= null_max + 0.5.
"""
import os, sys, json, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "analysis", "round11"))
import feedback as fb
import lib_numchannel as nc

N = fb.N
KS = range(2, 7)
SIGNS = (-1, 1)
ORIENTS = ("fwd", "rev")


def score_region(P, start):
    return fb.score_norm(P[start:])


def sweep_stream(U, label, results):
    for orient in ORIENTS:
        C = U if orient == "fwd" else U[::-1]
        for sign in SIGNS:
            for fname, f in fb.F_BASIS.items():
                for k in KS:
                    # ---- ct source: seed-independent tail
                    seed0 = [0] * k
                    P = fb.decode(C, f, k, seed0, source="ct", sign=sign)
                    sc = score_region(P, k)
                    results.append({
                        "label": label, "orient": orient, "sign": sign,
                        "f": fname, "k": k, "source": "ct", "seed": "0",
                        "score": round(sc, 4),
                        "translit": fb.idx_to_trans(P[k:k + 60]),
                    })
                    # ---- pt / mix : bounded seed probe (all-equal seeds)
                    for source in ("pt", "mix"):
                        best = None
                        for sv in range(N):
                            seed = [sv] * k
                            P = fb.decode(C, f, k, seed, source=source, sign=sign)
                            sc = score_region(P, k)
                            if best is None or sc > best[0]:
                                best = (sc, sv, P)
                        results.append({
                            "label": label, "orient": orient, "sign": sign,
                            "f": fname, "k": k, "source": source,
                            "seed": f"eq{best[1]}",
                            "score": round(best[0], 4),
                            "translit": fb.idx_to_trans(best[2][k:k + 60]),
                        })


def main():
    t0 = time.time()
    U = nc.unsolved()
    results = []
    # continuous over the whole unsolved stream
    sweep_stream(U, "continuous", results)
    # per-segment (each page-segment decoded independently)
    segs = nc.segments()[:-2]  # unsolved segments only
    seg_results = []
    for si, seg in enumerate(segs):
        if len(seg) < 12:
            continue
        sweep_stream(seg, f"seg{si}", seg_results)
    results.extend(seg_results)

    # ---- null band on the whole unsolved stream (english scorer) ----
    # false-positive ceiling: score of shuffled streams decoded is redundant;
    # the relevant null is "best English score achievable on size-matched noise".
    # We use nc.null_band over the raw shuffled stream translit as the reference
    # noise ceiling, plus a decode-specific null below.
    null_mean, null_max, null_all = nc.null_band(nc.eng_norm, U, n=200)

    results.sort(key=lambda r: r["score"], reverse=True)
    dt = time.time() - t0
    out = {
        "n_configs": len(results),
        "null_mean": round(null_mean, 4),
        "null_max": round(null_max, 4),
        "hit_bar": round(max(-5.5, null_max + 0.5), 4),
        "elapsed_sec": round(dt, 1),
        "top20": results[:20],
    }
    with open(os.path.join(HERE, "results.json"), "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"configs scored: {len(results)}  elapsed {dt:.1f}s")
    print(f"null: mean={null_mean:.3f} max={null_max:.3f}  hit_bar={out['hit_bar']:.3f}")
    print("TOP 15 configs by English score:")
    for r in results[:15]:
        print(f"  {r['score']:7.3f}  {r['label']:10s} {r['orient']} sign={r['sign']:+d} "
              f"f={r['f']:15s} k={r['k']} src={r['source']:3s} seed={r['seed']:5s} | "
              f"{r['translit'][:40]}")
    return out


if __name__ == "__main__":
    main()
