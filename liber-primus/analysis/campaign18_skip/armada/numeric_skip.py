"""Campaign XVIII -- NUMERIC-KEYSTREAM skip-tolerant attack (LP2).

DESIGN RATIONALE
----------------
Prior rigid-alignment tests of numeric keystreams (primes, totient, Fibonacci,
PRNG) were UNSOUND because the ~83% doublet-suppression filter DESYNCHRONISES
the keystream from the plaintext after the first skip (~1 per 35 runes). A key
that IS correct scores as noise under a rigid decoder. Campaign XVIII's
skip-tolerant beam (sweep.beam, validated in skipdecode.py) re-opens this class.

KEYSTREAMS GENERATED (all mod 29)
----------------------------------
A. Pure number-theoretic:
   primes          -- consecutive primes mod 29
   prime_gaps      -- consecutive prime gaps mod 29
   totient_n       -- phi(n) for n=2,3,4,... mod 29
   iter_totient_d2 -- phi(phi(n)) mod 29
   iter_totient_d3 -- phi(phi(phi(n))) mod 29

B. Transcendental constants (decimal digits mod 29, two encodings each):
   pi, e, phi, sqrt2, ln2
   Encoding A: individual decimal digits (0-9) -> trivially mod 29
   Encoding B: overlapping 2-digit windows (00-99) mod 29 -- denser keystream

C. Fibonacci sequences mod 29:
   ALL 29x29 = 841 seed pairs (a, b) -> F(n) where F(0)=a, F(1)=b, F(n)=F(n-1)+F(n-2) mod 29.
   Pisano period mod 29 = 14 so each seed is verified distinct.
   Seeds include Cicada constants as first-pair: (3301%29, n), (n, 3301%29), etc.
   [Smoke test uses all 841 seeds with a fast screen.]

D. PRNG-seeded streams (6 Cicada seeds: 3301, 1595277641, 761, 509, 503, 311):
   lcg_<seed>   -- Linear Congruential Generator (Knuth params) mod 29
   bbs_<seed>   -- Blum-Blum-Shub (p=503, q=311, both Blum primes ≡ 3 mod 4)
   mt_<seed>    -- Python Mersenne Twister

SWEEP LOGIC
-----------
For each keystream K and each (sign, atbash, offset):
  sign   ∈ {-1, +1}   (decrement vs increment key; LP1 always -1 but +1 tested for completeness)
  atbash ∈ {0, 1}     (pre-reflect ciphertext: c -> 28-c mod 29; LP1 pattern)
  offset ∈ {0, 1, 2, 3, 4}  (small shift into the keystream; full offset sweep = orchestrator job)

Two-tier:
  SCREEN: beam(len=50, beam_w=60)  -- very fast, filter to score > SCREEN_THR
  CONFIRM: beam(len=full, beam_w=200) -- only for survivors

Thresholds (from robustness.py / Campaign XVIII):
  null-max = -6.82  |  confirm = -5.5  |  English solve ~ -4.0 to -4.35

RUN MODES
---------
Smoke test (default):  3 pages, all keystreams, report best score.
Full run (--full):     All 55 unsolved pages.  Run by orchestrator only.
"""

import os
import sys
import time
import argparse
import random
from decimal import Decimal, getcontext

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "analysis"))
sys.path.insert(0, os.path.join(ROOT, "analysis", "campaign18_skip"))

from lp import gematria as gp, score as sc   # noqa: E402
from run_stats import load_pages             # noqa: E402
from skipdecode import idx_to_trans          # noqa: E402
from sweep import beam                       # noqa: E402

N = gp.N   # 29
Q = sc.default()

SCREEN_LEN = 50
SCREEN_THR = -6.5       # generous screen; tighten at confirm
CONFIRM_THR = -5.5      # threshold for reporting a hit
SCREEN_BW = 60
FULL_BW = 200
OFFSETS = [0, 1, 2, 3, 4]
CICADA_SEEDS = [3301, 1595277641, 761, 509, 503, 311]


# ============================================================
# SECTION 1 -- PRIME UTILITIES
# ============================================================

def _primes(count):
    out, cand = [], 2
    while len(out) < count:
        if all(cand % p for p in out if p * p <= cand):
            out.append(cand)
        cand += 1
    return out


def _totient(n):
    r, m, p = n, n, 2
    while p * p <= m:
        if m % p == 0:
            while m % p == 0:
                m //= p
            r -= r // p
        p += 1
    if m > 1:
        r -= r // m
    return r


# ============================================================
# SECTION 2 -- KEYSTREAM GENERATORS (all return list[int] mod 29)
# ============================================================

def ks_primes(length):
    """Consecutive primes mod 29."""
    ps = _primes(length)
    return [p % N for p in ps]


def ks_prime_gaps(length):
    """Consecutive prime gaps mod 29: p[i+1] - p[i]."""
    ps = _primes(length + 1)
    return [(ps[i + 1] - ps[i]) % N for i in range(length)]


def ks_totient_n(length, start=2):
    """Euler totient of consecutive integers phi(2), phi(3), ... mod 29."""
    out = []
    n = start
    while len(out) < length:
        out.append(_totient(n) % N)
        n += 1
    return out


def ks_iter_totient(length, depth, start=2):
    """Iterated totient phi^depth(n) mod 29 for n=start, start+1, ..."""
    def iter_phi(x, d):
        for _ in range(d):
            x = _totient(x)
            if x <= 1:
                return x
        return x
    out = []
    n = start
    while len(out) < length:
        out.append(iter_phi(n, depth) % N)
        n += 1
    return out


def _constant_decimal_digits(name, n_digits):
    """Return decimal digits of a named mathematical constant, mod 29."""
    getcontext().prec = n_digits + 100

    if name == "pi":
        a = Decimal(1)
        b = Decimal(1) / Decimal(2).sqrt()
        t = Decimal("0.25")
        p = Decimal(1)
        for _ in range(25):
            a1 = (a + b) / 2
            b = (a * b).sqrt()
            t -= p * (a - a1) ** 2
            a = a1
            p *= 2
        val = (a + b) ** 2 / (4 * t)
    elif name == "e":
        val = Decimal(0)
        term = Decimal(1)
        for k in range(1, 300):
            val += term
            term /= k
    elif name == "phi":
        val = (Decimal(1) + Decimal(5).sqrt()) / 2
    elif name == "sqrt2":
        val = Decimal(2).sqrt()
    elif name == "ln2":
        # ln(2) = 2*atanh(1/3) = 2*sum_{k=0}^inf (1/3)^(2k+1)/(2k+1)
        x = Decimal(1) / 3
        x2 = x * x
        term = x
        total = x
        k = 1
        while True:
            term *= x2
            delta = term / (2 * k + 1)
            total += delta
            if delta < Decimal(10) ** (-(n_digits + 50)):
                break
            k += 1
        val = 2 * total
    else:
        raise ValueError(f"Unknown constant: {name}")

    s = str(val).replace(".", "").replace("-", "")
    return [int(c) for c in s if c.isdigit()][:n_digits]


def ks_constant_single(name, length):
    """Encoding A: each decimal digit d -> d mod 29 (0-9 all < 29, so identity)."""
    digits = _constant_decimal_digits(name, length + 10)
    return [d % N for d in digits[:length]]


def ks_constant_pairs(name, length):
    """Encoding B: sliding 2-digit windows -> 2-digit number mod 29. Denser info."""
    digits = _constant_decimal_digits(name, length + 20)
    out = []
    for i in range(length):
        out.append((digits[i] * 10 + digits[i + 1]) % N)
    return out


def ks_fibonacci(a, b, length):
    """Fibonacci-like sequence mod 29 with seed (F0=a, F1=b)."""
    if length == 0:
        return []
    out = [a % N]
    if length == 1:
        return out
    out.append(b % N)
    for _ in range(length - 2):
        out.append((out[-1] + out[-2]) % N)
    return out


def ks_lcg(seed, length, a=1664525, c=1013904223, m=2 ** 32):
    """Linear Congruential Generator (Knuth params) mod 29."""
    x = seed % m
    out = []
    for _ in range(length):
        x = (a * x + c) % m
        out.append(x % N)
    return out


def ks_bbs(seed, length, p=503, q=311):
    """Blum-Blum-Shub CSPRNG. p=503, q=311 are both Blum primes (≡ 3 mod 4)."""
    M = p * q
    x = seed % M
    if x < 2:
        x = 2
    x = (x * x) % M
    out = []
    for _ in range(length):
        x = (x * x) % M
        out.append(x % N)
    return out


def ks_mt(seed, length):
    """Python Mersenne Twister seeded with a Cicada constant, output mod 29."""
    rng = random.Random(seed)
    return [rng.randint(0, N - 1) for _ in range(length)]


# ============================================================
# SECTION 3 -- KEYSTREAM CATALOG
# ============================================================

def build_catalog(length, include_fib=True):
    """Return ordered list of (name, keystream_list) pairs.

    Args:
        length: minimum keystream length in runes.
        include_fib: if False, skip the 841 Fibonacci seeds (for speed testing).
    """
    catalog = []

    # A. Pure number-theoretic
    catalog.append(("primes", ks_primes(length)))
    catalog.append(("prime_gaps", ks_prime_gaps(length)))
    catalog.append(("totient_n", ks_totient_n(length)))
    catalog.append(("iter_totient_d2", ks_iter_totient(length, depth=2)))
    catalog.append(("iter_totient_d3", ks_iter_totient(length, depth=3)))

    # B. Transcendental constants (two encodings each)
    for cname in ("pi", "e", "phi", "sqrt2", "ln2"):
        catalog.append((f"{cname}_digits", ks_constant_single(cname, length)))
        catalog.append((f"{cname}_pairs", ks_constant_pairs(cname, length)))

    # C. Fibonacci 29x29 (841 distinct; pisano period mod 29 = 14)
    if include_fib:
        for a in range(N):
            for b in range(N):
                catalog.append((f"fib_{a}_{b}", ks_fibonacci(a, b, length)))

    # D. PRNG with Cicada seeds
    for seed in CICADA_SEEDS:
        catalog.append((f"lcg_{seed}", ks_lcg(seed, length)))
        catalog.append((f"bbs_{seed}", ks_bbs(seed, length)))
        catalog.append((f"mt_{seed}", ks_mt(seed, length)))

    return catalog


# ============================================================
# SECTION 4 -- SWEEP ENGINE
# ============================================================

def _atbash(ct):
    """Reflect ciphertext indices: c -> (N-1-c) mod N."""
    return (N - 1 - ct) % N


def sweep_keystream(name, K_np, pages_np, verbose=False):
    """Sweep a single keystream K over all pages.

    Args:
        name: human-readable label for reporting.
        K_np: numpy int64 array, length >= max_page_len * (1 + MAXSKIP) + 5.
        pages_np: list of numpy int64 arrays (ciphertext pages).
        verbose: print per-page detail.

    Returns:
        list of (score, name, sign, atbash, offset, page_idx, translit) for
        anything that passes CONFIRM_THR.
    """
    hits = []
    best_global = -99.0

    for sign in (-1, 1):
        for atb in (0, 1):
            for pg_idx, ct in enumerate(pages_np):
                ct2 = _atbash(ct) if atb else ct
                L = len(ct2)
                for off in OFFSETS:
                    if off + L + 3 * L + 8 > len(K_np):
                        break   # not enough key material even for this offset

                    # --- SCREEN: fast short beam ---
                    slen = min(SCREEN_LEN, L)
                    pi_s = beam(ct2, K_np, sign, off, slen, SCREEN_BW)
                    sc_s = Q.score_norm(idx_to_trans(pi_s))

                    if sc_s > best_global:
                        best_global = sc_s

                    if sc_s <= SCREEN_THR:
                        continue

                    # --- CONFIRM: full-length beam ---
                    pi_f = beam(ct2, K_np, sign, off, L, FULL_BW)
                    sc_f = Q.score_norm(idx_to_trans(pi_f))
                    if sc_f > CONFIRM_THR:
                        tl = idx_to_trans(pi_f)
                        hits.append((sc_f, name, sign, atb, off, pg_idx, tl))
                        if verbose:
                            print(f"  HIT score={sc_f:.3f} ks={name} sign={sign} "
                                  f"atb={atb} off={off} pg={pg_idx}")
                            print(f"     {tl[:80]}")

    return hits, best_global


# ============================================================
# SECTION 5 -- MAIN ENTRY POINT
# ============================================================

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--full", action="store_true",
                    help="Run on all 55 unsolved pages (orchestrator mode). "
                         "Default: 3-page smoke test.")
    ap.add_argument("--pages", default="",
                    help="Override page range, e.g. '0-9' (inclusive).")
    ap.add_argument("--no-fib", action="store_true",
                    help="Skip Fibonacci seeds (useful for fastest possible test).")
    ap.add_argument("--report-above", type=float, default=-6.0,
                    help="Print any screen score above this value (default -6.0).")
    args = ap.parse_args()

    pages_all = load_pages()[:-2]   # 55 unsolved pages as index lists

    if args.pages:
        a, b = args.pages.split("-")
        sel = list(range(int(a), int(b) + 1))
    elif args.full:
        sel = list(range(len(pages_all)))
    else:
        sel = [0, 1, 2]   # smoke test: first 3 pages

    pages_sel = [pages_all[i] for i in sel]
    pages_np = [np.array(p, dtype=np.int64) for p in pages_sel]

    max_len = max(len(p) for p in pages_sel)
    # worst-case key length: offset_max + page_len + max_skip * page_len + buffer
    ks_len = max(OFFSETS) + max_len + 3 * max_len + 64

    print("=" * 72)
    print("NUMERIC-KEYSTREAM skip-tolerant sweep  (Campaign XVIII / numeric_skip.py)")
    print("=" * 72)
    print(f"Pages: {[sel[0]]}..{[sel[-1]]}  ({len(sel)} pages)  |  "
          f"max_len={max_len}  |  ks_len={ks_len}")
    print(f"Signs: {{-1,+1}}  |  Atbash: {{0,1}}  |  Offsets: {OFFSETS}")
    print(f"Screen: len={SCREEN_LEN} beam_w={SCREEN_BW} thr={SCREEN_THR}  |  "
          f"Confirm: beam_w={FULL_BW} thr={CONFIRM_THR}")
    print(f"Null-max=-6.82  |  English solve ~-4.0 to -4.35  |  Threshold={CONFIRM_THR}")
    print()

    include_fib = not args.no_fib
    print(f"Building keystream catalog (ks_len={ks_len}, fib={'YES' if include_fib else 'NO'}) ...")
    t_cat = time.time()
    catalog = build_catalog(ks_len, include_fib=include_fib)
    print(f"  {len(catalog)} keystreams built in {time.time() - t_cat:.1f}s")
    print()

    # Pre-convert all keystreams to numpy once
    catalog_np = [(name, np.array(ks, dtype=np.int64)) for name, ks in catalog]

    all_hits = []
    best_score_seen = -99.0
    best_label = None
    t0 = time.time()

    print(f"{'#':>5}  {'name':<30}  {'best_screen':>12}  {'elapsed':>8}")
    print("-" * 60)

    for i, (name, K_np) in enumerate(catalog_np):
        hits, bg = sweep_keystream(name, K_np, pages_np, verbose=False)
        all_hits.extend(hits)
        if bg > best_score_seen:
            best_score_seen = bg
            best_label = name
        elapsed = time.time() - t0

        # Always print if above report_above or at report intervals
        show = (bg > args.report_above) or (i % 50 == 0) or (i == len(catalog_np) - 1)
        if show:
            flag = "  <== NOTABLE" if bg > args.report_above else ""
            print(f"{i:5d}  {name:<30}  {bg:12.3f}  {elapsed:8.1f}s{flag}")

        if hits:
            for h in sorted(hits, reverse=True)[:3]:
                print(f"       HIT: score={h[0]:.3f} sign={h[2]} atb={h[3]} "
                      f"off={h[4]} pg={h[5]}")
                print(f"            {h[6][:80]}")

    elapsed_total = time.time() - t0
    print()
    print("=" * 72)
    print("SUMMARY")
    print("=" * 72)
    print(f"Total keystreams tested : {len(catalog_np)}")
    print(f"Pages tested            : {len(sel)}")
    print(f"Total elapsed           : {elapsed_total:.1f}s")
    print(f"Best screen score seen  : {best_score_seen:.3f}  (via '{best_label}')")
    print(f"Hits above CONFIRM_THR={CONFIRM_THR} : {len(all_hits)}")
    print()
    print("Scale: English solve ~ -4.0 | CONFIRM threshold = -5.5 | null-max = -6.82")
    print()

    if all_hits:
        print("CONFIRMED HITS (score > -5.5):")
        for h in sorted(all_hits, reverse=True):
            print(f"  score={h[0]:.3f} ks={h[1]} sign={h[2]} atb={h[3]} "
                  f"off={h[4]} pg={h[5]}")
            print(f"  {h[6][:100]}")
    else:
        print("NO hits above confirm threshold.  Null result consistent with OTP-class.")
        if best_score_seen > -7.0:
            print(f"  Best score {best_score_seen:.3f} is in the noise band "
                  f"(-7.5 floor, null-max -6.82, no signal detected).")

    return {"best_score_seen": best_score_seen, "hits": len(all_hits),
            "n_keystreams": len(catalog_np), "elapsed": elapsed_total}


if __name__ == "__main__":
    main()
