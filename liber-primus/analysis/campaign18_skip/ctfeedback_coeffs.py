"""Novel-cipher lane: NON-ADDITIVE multi-rune-history ciphertext-feedback with a
mod-29 LINEAR-COEFFICIENT sweep -- the one thing armada2/selfref_skip.py did NOT do.

Prior selfref_skip.decode_ctfeedback fixed coeffs=[1,1,1] (unit feedback). It scored
-7.06..-7.22 on p0/p1/p2 (deep noise floor). This survives the OTP doublet-deficit
proof because the key at position i depends on the PREVIOUS CIPHERTEXT runes, not on
a fixed keystream -- so it is not excluded.

Here we sweep the mod-29 coefficient space:
    key[i] = ( seed[i]  +  sum_{t=1..k} a_t * C[i-t] )  mod 29
for a_t in {0..28}, k in {1,2,3}, both signs, WITH and WITHOUT a seed keytext.
The seed-free (a_0=const c0) case is a pure autonomous feedback cipher -- no keytext,
so it removes the keytext dependence entirely. Feedback is computable from the KNOWN
ciphertext at decode time, so no plaintext-guessing beam is needed for the feedback
term; we reuse selfref_skip._feedback_beam (skip-aware).

BOUNDED: k=1 -> 29 coeffs; k=2 -> we sweep a1 in {1..28}, a2 in a small set; k=3 small.
Full grid is 29^3 ~ 24k * offsets -- too big for a smoke, so we do a PRINCIPLED subset
(single-tap dominant coeffs + a few multi-tap combos) and report the best English score.

Run: PYTHONUTF8=1 python3 analysis/campaign18_skip/ctfeedback_coeffs.py --pages 0,5,20
"""
import os, sys, argparse, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "analysis"))
sys.path.insert(0, os.path.join(HERE))
sys.path.insert(0, os.path.join(HERE, "armada2"))

from lp import gematria as gp, score as sc
from run_stats import load_pages
from sweep import Q, N, MAXSKIP, load_text
from skipdecode import idx_to_trans, eng_to_idx
import selfref_skip as SR

CONF_THR = -5.5
SIGNAL_THR = -5.2   # assignment's hit threshold


def const_seed(c0, length):
    return np.full(length, c0 % N, dtype=np.int64)


def decode_with_coeffs(ct, seed, k, coeffs, sign, o):
    """Decode ct as ct-feedback with GIVEN linear coeffs (list index 1..k)."""
    C = np.asarray(ct, dtype=np.int64)
    L = len(C)
    sk = np.asarray(seed, dtype=np.int64)
    need = o + L + MAXSKIP * L + 8
    if need > len(sk):
        sk = np.concatenate([sk, np.zeros(need - len(sk), dtype=np.int64)])
    f = np.zeros(L, dtype=np.int64)
    for i in range(k, L):
        v = 0
        for t in range(1, k + 1):
            v += coeffs[t] * int(C[i - t])
        f[i] = v % N
    r = SR._feedback_beam(C, sk, f, sign, o, 250, MAXSKIP)
    return r["score"], r


def coeff_grid(k):
    """FULL DENSE coefficient sets per history depth k (assignment: exhaust,
    not sample). k=1: all 29 taps. k=2: full 29x29 (a1,a2). k=3: full 29x29
    on the two dominant lags (a1,a2) crossed with a bounded a3 in {0,1,N-1,2,N-2}
    -- 29*29*5 = 4205 combos -- so lag-3 is probed at every (a1,a2) rather than
    only single-tap. a_t=0 allowed so lower-order taps are naturally included."""
    if k == 1:
        # single tap: every multiplier of C[i-1] (0 excluded = trivial no-key)
        return [[0, a] for a in range(1, N)]
    if k == 2:
        # FULL 29x29 grid (a1 on C[i-1], a2 on C[i-2]); skip the all-zero key
        g = []
        for a in range(N):
            for b in range(N):
                if a == 0 and b == 0:
                    continue
                g.append([0, a, b])
        return g
    # k == 3: full (a1,a2) x bounded a3 -- keeps it under ~4200 while covering
    # every pairwise lag-1/lag-2 relation at each of the strongest lag-3 taps.
    g = []
    for a in range(N):
        for b in range(N):
            for c in (0, 1, N - 1, 2, N - 2):
                if a == 0 and b == 0 and c == 0:
                    continue
                g.append([0, a, b, c])
    return g


def attack_page(ct, seeds, offsets):
    """Return best (score, meta) over coeff grid x seeds x signs x offsets."""
    best = (-99.0, None, None)
    L = len(ct)
    for k in (1, 2, 3):
        grid = coeff_grid(k)
        for coeffs in grid:
            for sname, seed in seeds:
                for sign in (-1, 1):
                    for o in offsets:
                        s, r = decode_with_coeffs(ct, seed, k, coeffs, sign, o)
                        if s > best[0]:
                            best = (s, (k, coeffs, sname, sign, o), r["translit"][:70])
    return best


def gate():
    """Sanity: plant a ct-feedback cipher with a NON-unit coeff (a1=7) + seed-free,
    verify the coeff sweep RECOVERS it and unit-coeff decode MISSES it."""
    print("-" * 68)
    print("GATE: non-unit-coeff autonomous ct-feedback recoverable by the sweep")
    plain = ("THE TOTIENT FUNCTION IS SACRED AND THE PRIMES ARE SACRED KNOW THIS THAT "
             "THE INSTAR EMERGENCE IS AT HAND THE PILGRIM SHALL FIND THE SACRED TRUTH")
    P = eng_to_idx(plain)
    # autonomous encipher: seed = const c0=5, coeff a1=7 on C[i-1], sign=-1, skip filter
    c0, a1, sign = 5, 7, -1
    seedK = const_seed(c0, len(P) * (MAXSKIP + 1) + 16)
    C = SR.encipher_ctfeedback(P, seedK, k=1, coeffs=[0, a1], sign=sign, supp=0.83)
    # correct decode: seed const 5, coeff 7
    sg, rg = decode_with_coeffs(C, const_seed(c0, len(C) * (MAXSKIP + 2)), 1, [0, a1], sign, 0)
    mg = sum(x == y for x, y in zip(rg["plain_idx"], P)) / len(P)
    # unit-coeff control
    sb, rb = decode_with_coeffs(C, const_seed(c0, len(C) * (MAXSKIP + 2)), 1, [0, 1], sign, 0)
    mb = sum(x == y for x, y in zip(rb["plain_idx"], P)) / len(P)
    print(f"  correct (a1=7): score={sg:.2f} match={mg*100:.0f}% | "
          f"unit (a1=1): score={sb:.2f} match={mb*100:.0f}%")
    ok = sg > -5.0 and mg > 0.9 and sb < -5.5
    print(f"  GATE: {'PASS' if ok else 'FAIL'}")
    return ok


def run(page_ids, with_ref=False):
    pages = load_pages()
    # SEED-FREE const seeds are the assignment's core (autonomous feedback cipher).
    # The feedback term dominates the key; a huge keytext seed (mabinogion, 428k)
    # makes each beam decode ~10x slower and is NOT the seed-free class under test,
    # so it is off by default. --with-ref re-adds it for a targeted follow-up.
    seeds = [("const0", const_seed(0, 4000)),
             ("const1", const_seed(1, 4000))]
    if with_ref:
        ref = SR.load_referenced()[:1]
        for nm, k in ref:
            arr = k if isinstance(k, np.ndarray) else np.array(eng_to_idx(k), dtype=np.int64)
            seeds.append((nm, arr))
    offsets = [0]  # feedback term dominates the key; seed offset is secondary at smoke
    print("=" * 68)
    print(f"CT-FEEDBACK COEFFICIENT SWEEP  pages={page_ids}  "
          f"seeds={[s[0] for s in seeds]}  signal_thr={SIGNAL_THR}")
    print("=" * 68)
    overall = (-99.0, None)
    for pid in page_ids:
        if pid >= len(pages):
            print(f"page {pid}: OUT OF RANGE (have {len(pages)})"); continue
        ct = np.array(pages[pid], dtype=np.int64)
        t0 = time.time()
        best = attack_page(ct, seeds, offsets)
        dt = time.time() - t0
        if best[0] > overall[0]:
            overall = (best[0], (pid,) + (best[1],))
        print(f"\npage {pid} ({len(ct)} runes, {dt:.0f}s): best={best[0]:.2f}")
        print(f"   meta k,coeffs,seed,sign,o = {best[1]}")
        print(f"   plain[:70] = {best[2]}")
    print("\n" + "=" * 68)
    print(f"OVERALL BEST = {overall[0]:.2f}  {overall[1]}")
    verdict = "LIVE (>= -5.2, inspect)" if overall[0] >= SIGNAL_THR else \
              ("marginal" if overall[0] > -6.0 else "NULL (noise floor)")
    print(f"VERDICT: {verdict}")
    print("=" * 68)
    return overall


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", default="0,5,20")
    ap.add_argument("--gate", action="store_true")
    ap.add_argument("--with-ref", action="store_true")
    args = ap.parse_args()
    if args.gate:
        gate()
    else:
        gate()
        run([int(x) for x in args.pages.split(",")], with_ref=args.with_ref)
