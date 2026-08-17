"""B2 lane, Stage 2 — DRIFT-TOLERANT DECODER for the hand-cipher hypothesis.

Model: ciphertext c[i] = pt[j] + K[(i + d_i) mod k], where d_i is a monotone
non-decreasing drift counter that increments at the author's local no-repeat
corrections.  The key phase is therefore piecewise constant with occasional +1
jumps — a hidden-Markov decode over k phase states.

Given a candidate key K, the plaintext at position i is FULLY DETERMINED by the
phase state, so the HMM state space collapses to the k phase offsets and exact
bigram Viterbi is cheap.  The key itself is searched by simulated annealing.

Run order (mandatory):
  1. POSITIVE CONTROL — plant known English enciphered exactly this way and
     require the decoder to recover it.  If this fails, nothing else is
     interpretable and we report a detection limit instead of a result.
  2. Real LP2 segments.

Usage: PYTHONUTF8=1 python3 b2_decode.py   Writes results_stage2.json
"""
import io
import json
import math
import os
import random
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
LP = os.path.join(REPO, "liber-primus")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(LP, "src"))
from b2_sim import load_lp2, load_english_runes, encipher, N  # noqa: E402
from lp import gematria as gp, score as _score  # noqa: E402


def bigram_model(pt):
    """log P(next | prev) over the 29 runes, from English runeglish."""
    cnt = np.ones((N, N)) * 0.5
    a = np.asarray(pt, dtype=np.int64)
    np.add.at(cnt, (a[:-1], a[1:]), 1.0)
    return np.log(cnt / cnt.sum(axis=1, keepdims=True))


def viterbi(c, key, B, log_stay, log_move):
    """Best drift path for a fixed key. Returns (score, plaintext indices)."""
    n = len(c)
    k = len(key)
    idx = (np.arange(n)[:, None] + np.arange(k)[None, :]) % k
    P = (c[:, None] - np.asarray(key)[idx]) % N          # (n, k) plaintext per phase
    # per-position emission for stay / move transitions
    stay = B[P[:-1, :], P[1:, :]] + log_stay             # (n-1, k)  delta -> delta
    prevroll = np.roll(P[:-1, :], 1, axis=1)             # P[i-1, delta-1]
    move = B[prevroll, P[1:, :]] + log_move              # (n-1, k)  delta-1 -> delta
    dp = np.zeros(k)
    bp = np.empty((n - 1, k), dtype=np.int8)
    for i in range(n - 1):
        a = dp + stay[i]
        b = np.roll(dp, 1) + move[i]
        take = b > a
        dp = np.where(take, b, a)
        bp[i] = take
    end = int(np.argmax(dp))
    path = np.empty(n, dtype=np.int64)
    path[n - 1] = end
    for i in range(n - 2, -1, -1):
        path[i] = (path[i + 1] - 1) % k if bp[i][path[i + 1]] else path[i + 1]
    return float(dp[end]) / (n - 1), P[np.arange(n), path]


def anneal(c, k, B, rho, rng, iters=6000, restarts=2):
    log_stay, log_move = math.log(1 - rho), math.log(rho)
    best = (-1e18, None, None)
    for _ in range(restarts):
        key = [rng.randrange(N) for _ in range(k)]
        s, pt = viterbi(c, key, B, log_stay, log_move)
        T0, T1 = 0.06, 0.002
        for t in range(iters):
            T = T0 * (T1 / T0) ** (t / iters)
            i = rng.randrange(k)
            old = key[i]
            key[i] = rng.randrange(N)
            s2, pt2 = viterbi(c, key, B, log_stay, log_move)
            if s2 > s or rng.random() < math.exp((s2 - s) / T):
                s, pt = s2, pt2
            else:
                key[i] = old
            if s > best[0]:
                best = (s, list(key), pt)
    return best


def main():
    rng = random.Random(424242)
    q = _score.default()
    real = load_lp2()
    pt_en = load_english_runes(60000)
    B = bigram_model(pt_en)
    SEG = 800
    RHO = 0.03
    ITERS, RESTARTS = 2000, 2
    STAGE = sys.argv[1] if len(sys.argv) > 1 else "all"
    out = {"segment_len": SEG, "rho": RHO, "iters": ITERS, "restarts": RESTARTS,
           "stage": STAGE}

    # ---- scorer calibration on this scale
    cal = {
        "english_plain": q.score_norm(gp.indices_to_translit(pt_en[:SEG])),
        "uniform_random": q.score_norm(gp.indices_to_translit(
            [rng.randrange(N) for _ in range(SEG)])),
        "real_lp2_raw": q.score_norm(gp.indices_to_translit(real[:SEG])),
    }
    print("scorer calibration (score_norm, log10/quadgram):",
          {a: round(b, 3) for a, b in cal.items()})
    out["calibration"] = cal

    # ---- 1. POSITIVE CONTROL
    pos = []
    if STAGE in ("all", "controls"):
      print("\n=== POSITIVE CONTROL: planted short-key Vigenere + correction drift ===")
      for k in (4, 6, 8, 12):
        key = [rng.randrange(N) for _ in range(k)]
        ct, ncorr, ndrift = encipher(pt_en, key, "R2_KEYADV", 0.82, SEG + 200, rng)
        ct = np.asarray(ct[:SEG], dtype=np.int64)
        s, kfound, dec = anneal(ct, k, B, RHO, rng, ITERS, RESTARTS)
        # R2_KEYADV consumes exactly one plaintext rune per output rune, so the
        # ground-truth plaintext for output j is pt_en[j] — exact recovery test.
        truth = np.asarray(pt_en[:SEG], dtype=np.int64)
        recov = float(np.mean(truth == dec))
        txt = gp.indices_to_translit(dec)
        sc = q.score_norm(txt)
        keyhit = max(sum(1 for a, b in zip(key, kfound[r:] + kfound[:r]) if a == b)
                     for r in range(k))  # keys are equivalent up to cyclic rotation
        pos.append({"k": k, "viterbi": s, "quadgram": sc,
                    "recovery_rate": recov,
                    "key_true": key, "key_found": kfound,
                    "key_positions_exact": keyhit,
                    "drift_rate": ndrift / len(ct),
                    "text": txt[:160],
                    "truth_text": gp.indices_to_translit(truth)[:160]})
        print(f"  k={k:2d}: RECOVERY {recov:.1%}  quadgram {sc:+.3f}  "
              f"key positions exact {keyhit}/{k}  drift {ndrift/len(ct):.2%}")
        print(f"        got   {txt[:110]}")
        print(f"        truth {gp.indices_to_translit(truth)[:110]}")
    out["positive_control"] = pos

    # ---- 2. NEGATIVE CONTROL: the incumbent model (memoryless + soft filter)
    print("\n=== NEGATIVE CONTROL: memoryless base + soft anti-repeat (no key) ===")
    neg = []
    base = []
    prev = -1
    for _ in range(SEG):
        v = rng.randrange(N)
        if v == prev and rng.random() < 0.82:
            v = rng.randrange(N - 1)
            if v >= prev:
                v += 1
        base.append(v)
        prev = v
    base = np.asarray(base, dtype=np.int64)
    for k in (4, 8, 12):
        s, kf, dec = anneal(base, k, B, RHO, rng, ITERS, RESTARTS)
        sc = q.score_norm(gp.indices_to_translit(dec))
        neg.append({"k": k, "viterbi": s, "quadgram": sc,
                    "text": gp.indices_to_translit(dec)[:160]})
        print(f"  k={k:2d}: quadgram {sc:+.3f}   {gp.indices_to_translit(dec)[:100]}")
    out["negative_control"] = neg

    # ---- 3. REAL LP2
    print("\n=== REAL LP2 (pages 0-54 concatenation, 3 segments) ===")
    res = []
    if STAGE in ("all", "real"):
     for off in (0, 6000):
        seg = np.asarray(real[off:off + SEG], dtype=np.int64)
        for k in range(4, 13):
            s, kf, dec = anneal(seg, k, B, RHO, rng, ITERS, RESTARTS)
            txt = gp.indices_to_translit(dec)
            sc = q.score_norm(txt)
            res.append({"offset": off, "k": k, "viterbi": s, "quadgram": sc,
                        "key_found": kf, "text": txt[:160]})
            print(f"  off={off:5d} k={k:2d}: quadgram {sc:+.3f}  {txt[:80]}")
    out["real"] = res

    if not res:
        json.dump(out, io.open(os.path.join(HERE, "results_stage2_%s.json" % STAGE),
                               "w", encoding="utf-8"))
        print("wrote results_stage2_%s.json (controls only)" % STAGE)
        return
    best = max(res, key=lambda r: r["quadgram"])
    print(f"\nBEST REAL: off={best['offset']} k={best['k']} "
          f"quadgram {best['quadgram']:+.3f}")
    print(f"  vs positive-control mean "
          f"{np.mean([p['quadgram'] for p in pos]):+.3f}, "
          f"negative-control mean {np.mean([p['quadgram'] for p in neg]):+.3f}, "
          f"English plaintext {cal['english_plain']:+.3f}")
    out["best_real"] = best

    json.dump(out, io.open(os.path.join(HERE, "results_stage2_%s.json" % STAGE), "w",
                           encoding="utf-8"))
    print("wrote results_stage2.json")


if __name__ == "__main__":
    main()
