"""Campaign XVIII / armada2 -- EXTENDED NUMERIC KEYS, skip-tolerant (LP2).

WHAT THIS FILE COVERS (new, never tested skip-aware)
====================================================
  1. pp49-51 256-byte payload as a KEY at ALL offsets (sliding-window), both
     canonical variants, forward + reversed -- not just offset 0.
  2. Onion-trail hex / Cicada numeric artifacts grep'd from analysis/:
       - canon_256.hex nibble stream (each hex nibble 0-15 -> mod 29)
       - AN END 512-bit hash bytes mod 29 as a keystream
  3. 2012 Mayan rotation key [10,2,14,7,19,6,18,12,7,8,17,0,19] (period-13)
     and the end-of-puzzle P.S. digit string, skip-aware with full offset sweep.
  4. Page-number-seeded keys (per-page shift from page index via primes/totient),
     magic-square derived streams, extended constant set (all primes to 109,
     3301 digit expansions of pi/e/phi to higher precision).
  5. Catalan / triangular / Lucas / partition sequences mod 29.

ALREADY COVERED (do NOT redo):
  - numeric_skip.py: primes, prime_gaps, totient_n, iter_totient, pi/e/phi/sqrt2/ln2
    single-digit + pair-digit encodings, all 841 Fibonacci seeds (fib_a_b), PRNG
    streams (LCG/BBS/MT) with 6 Cicada seeds -- all at offsets 0-4 -- full 55 pages.
  - payload_skip.py: payload bytes mod 29 at offset 0 over each page.

THIS FILE adds the ALL-OFFSET payload sweep plus the sequences listed above.

DECODER: sweep.beam (validated skip-tolerant beam, Campaign XVIII / skipdecode.py).
THRESHOLDS: null-max -6.82 | CONFIRM -5.5 | English solve ~-4.0 to -4.35.

Run modes:
  smoke (default): 3 pages, fast beam widths.
  full (--full):   55 pages -- orchestrator only.
"""

import os
import sys
import time
import argparse
import math

import numpy as np

# ---- path setup ---------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "analysis"))
sys.path.insert(0, os.path.join(ROOT, "analysis", "campaign18_skip"))

from lp import gematria as gp, score as sc  # noqa: E402
from run_stats import load_pages             # noqa: E402
from skipdecode import idx_to_trans          # noqa: E402
from sweep import beam                       # noqa: E402

N = gp.N   # 29
Q = sc.default()

# ---- tuning -------------------------------------------------------------------
SCREEN_LEN   = 50
SCREEN_THR   = -6.5
CONFIRM_THR  = -5.5
NULL_MAX     = -6.82
SCREEN_BW    = 60
FULL_BW      = 300
MAXSKIP      = 3


# =============================================================================
# SECTION 1 -- UTILITY NUMBER-THEORY
# =============================================================================

def _sieve(limit):
    """Sieve of Eratosthenes, returns sorted list of primes up to limit."""
    is_p = bytearray([1]) * (limit + 1)
    is_p[0] = is_p[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if is_p[i]:
            is_p[i*i::i] = bytearray(len(is_p[i*i::i]))
    return [i for i, v in enumerate(is_p) if v]


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


def _primes_up_to(limit):
    return _sieve(limit)


# =============================================================================
# SECTION 2 -- KEYSTREAM GENERATORS (all return list[int] mod 29)
# =============================================================================

# ---- 2a. Payload at ALL offsets ------------------------------------------------

def load_payload_bytes():
    """Return two canonical payload variants: majority vote and decimal-preference."""
    p1 = os.path.join(ROOT, "analysis", "pp49_51", "canon_256.bin")
    p2 = os.path.join(ROOT, "analysis", "pp49_51", "canon_256_decpref.bin")
    variants = {}
    for path, label in ((p1, "payload_majority"), (p2, "payload_decpref")):
        if os.path.exists(path):
            b = np.frombuffer(open(path, "rb").read(), dtype=np.uint8).astype(np.int64)
            variants[label] = b
            variants[label + "_rev"] = b[::-1].copy()
    return variants


# ---- 2b. Onion-trail hex / AN END hash as keystreams ---------------------------

ANEND_HEX = ("36367763ab73783c7af284446c59466b4cd653239a311cb7116d4618dee09a84"
              "25893dc7500b464fdaf1672d7bef5e891c6e2274568926a49fb4f45132c2a8b4")

def ks_anend_bytes(length):
    """AN END 512-bit hash bytes mod 29."""
    b = bytes.fromhex(ANEND_HEX)
    base = [x % N for x in b]
    # tile to length
    out = []
    while len(out) < length:
        out.extend(base)
    return out[:length]


def ks_anend_bytes_rev(length):
    """AN END hash bytes, reversed, mod 29."""
    b = bytes.fromhex(ANEND_HEX)
    base = [x % N for x in reversed(b)]
    out = []
    while len(out) < length:
        out.extend(base)
    return out[:length]


def ks_anend_nibbles(length):
    """AN END hash nibbles (each hex digit 0-15 -> mod 29 = itself, all < 16 < 29)."""
    base = [int(c, 16) % N for c in ANEND_HEX]
    out = []
    while len(out) < length:
        out.extend(base)
    return out[:length]


def ks_payload_hex_nibbles(length):
    """canon_256.hex nibble stream from the pp49-51 payload."""
    hex_path = os.path.join(ROOT, "analysis", "pp49_51", "canon_256.hex")
    if not os.path.exists(hex_path):
        return None
    hexstr = open(hex_path).read().strip()
    base = [int(c, 16) % N for c in hexstr if c in "0123456789abcdefABCDEF"]
    if not base:
        return None
    out = []
    while len(out) < length:
        out.extend(base)
    return out[:length]


# ---- 2c. Mayan + P.S. digit string (skip-aware, full offset sweep) -------------

MAYAN = [10, 2, 14, 7, 19, 6, 18, 12, 7, 8, 17, 0, 19]

PS_DIGITS_STR = ("1041279065891998535982789873959431895640"
                 "442510695567564373922695237268242385295908173"
                 "9834390370374475764863415203423499357108713631")


def tile_to(base, length):
    out = []
    while len(out) < length:
        out.extend(base)
    return out[:length]


def ks_mayan(length):
    base = [x % N for x in MAYAN]
    return tile_to(base, length)


def ks_mayan_rev(length):
    base = [x % N for x in reversed(MAYAN)]
    return tile_to(base, length)


def ks_ps_single(length):
    """P.S. digits, each digit 0-9 -> mod 29 (identity, all < 29)."""
    base = [int(c) % N for c in PS_DIGITS_STR]
    return tile_to(base, length)


def ks_ps_pairs(length):
    """P.S. digits in overlapping 2-digit windows mod 29."""
    base = [int(PS_DIGITS_STR[i:i+2]) % N for i in range(len(PS_DIGITS_STR)-1)]
    return tile_to(base, length)


def ks_ps_rev(length):
    base = [int(c) % N for c in reversed(PS_DIGITS_STR)]
    return tile_to(base, length)


# ---- 2d. Page-number-seeded keys (for per-page use) ---------------------------

_PRIMES_109 = _primes_up_to(109)   # all primes ≤ 109

def page_seeded_stream(page_idx, length, mode="prime"):
    """Per-page key seeded by page_idx.
    mode 'prime': shift sequence by nth prime (page_idx-th prime) mod 29.
    mode 'totient': shift sequence by phi(page_idx+2) mod 29.
    mode '3301xor': stream = [(i * 3301 + page_idx) mod 29 for i in range(length)].
    """
    if mode == "prime":
        pr = _PRIMES_109[page_idx % len(_PRIMES_109)]
        return [(pr + i) % N for i in range(length)]
    elif mode == "totient":
        t = _totient(page_idx + 2)  # +2 so no trivial inputs
        return [(t + i) % N for i in range(length)]
    elif mode == "3301xor":
        return [(i * 3301 + page_idx) % N for i in range(length)]
    else:
        raise ValueError(mode)


# ---- 2e. Magic-square derived streams -----------------------------------------

# Known Cicada magic-square numbers from the KNOW THIS page (LP2 solved section)
MAGIC_SQ = [
    434, 1311, 312, 278, 966, 204, 812, 934, 280,
    1071, 626, 620, 809, 620, 626, 1071, 280, 934,
    812, 204, 966, 278, 312, 1311, 434
]

def ks_magic_sq_mod29(length):
    base = [n % N for n in MAGIC_SQ]
    return tile_to(base, length)


def ks_magic_sq_digits(length):
    """Each decimal digit of the magic square numbers, mod 29."""
    base = [int(d) % N for n in MAGIC_SQ for d in str(n)]
    return tile_to(base, length)


def ks_magic_sq_rowsums(length):
    """Row sums of a 5x5 view of the magic square, mod 29 (each sum ≡ some value)."""
    sq5 = MAGIC_SQ[:25]
    rows = [sum(sq5[i*5:(i+1)*5]) % N for i in range(5)]
    return tile_to(rows, length)


# ---- 2f. Extended constants: all primes to 109, 3301 digit expansions ----------

def ks_primes_to_109(length):
    """All primes ≤ 109, mod 29, tiled."""
    base = [p % N for p in _PRIMES_109]
    return tile_to(base, length)


def ks_3301_decimal(length):
    """Decimal digits of 3301 repeated (3, 3, 0, 1, 3, 3, 0, 1, ...) mod 29."""
    base = [int(c) % N for c in "3301"]
    return tile_to(base, length)


def ks_3301_powers_mod29(length):
    """Powers of 3301 mod 29: 3301^0, 3301^1, 3301^2, ... mod 29."""
    # 3301 mod 29 = 3301 - 29*113 = 3301 - 3277 = 24
    base_val = 3301 % N  # = 24
    out, v = [], 1
    while len(out) < length:
        out.append(v % N)
        v = (v * base_val) % N
        if v == 1 and len(out) >= 28:  # period detected
            # tile the period
            period = out[:]
            while len(out) < length:
                out.extend(period)
            break
    return out[:length]


def ks_3301_phi_multiples(length):
    """phi(3301 * k) mod 29 for k=1,2,3,...  (3301 is prime so phi(3301*k)=3300*phi(k))."""
    out = []
    k = 1
    while len(out) < length:
        out.append((_totient(3301 * k)) % N)
        k += 1
    return out[:length]


# ---- 2g. Catalan / triangular / Lucas / partition sequences mod 29 -------------

def ks_catalan(length):
    """Catalan numbers C_n mod 29."""
    out = []
    c = 1  # C_0 = 1
    n = 0
    while len(out) < length:
        out.append(c % N)
        n += 1
        # C_n = C_{n-1} * 2*(2n-1) / (n+1)
        c = c * 2 * (2*n - 1) // (n + 1)
    return out[:length]


def ks_triangular(length):
    """Triangular numbers T_n = n*(n+1)/2 mod 29."""
    return [(n * (n+1) // 2) % N for n in range(length)]


def ks_lucas(length):
    """Lucas numbers: L_0=2, L_1=1, L_n=L_{n-1}+L_{n-2} mod 29."""
    out = [2 % N, 1 % N]
    while len(out) < length:
        out.append((out[-1] + out[-2]) % N)
    return out[:length]


def ks_partition(length):
    """Partition function p(n) mod 29, n=0,1,..."""
    # Euler's recursive formula: p(n) = sum_{k!=0} (-1)^{k+1} p(n - k*(3k-1)/2)
    # p(0)=1, p(n<0)=0
    p = [0] * (length + 1)
    p[0] = 1
    for n in range(1, length + 1):
        k = 1
        while True:
            pent1 = k * (3*k - 1) // 2
            pent2 = k * (3*k + 1) // 2
            if pent1 > n:
                break
            sign = (-1)**(k+1)
            p[n] += sign * (p[n - pent1])
            if pent2 <= n:
                p[n] += sign * (p[n - pent2])
            k += 1
    return [p[n] % N for n in range(length)]


def ks_partition_rev(length):
    base = ks_partition(length)
    return list(reversed(base))


# =============================================================================
# SECTION 3 -- KEYSTREAM CATALOG (non-payload)
# =============================================================================

def build_fixed_catalog(length):
    """All non-payload keystreams, returned as (name, np.int64 array)."""
    catalog = []

    def add(name, ks):
        if ks is not None and len(ks) >= length:
            catalog.append((name, np.array(ks[:length], dtype=np.int64)))

    # 2b. Onion/hash artifact streams
    add("anend_bytes",       ks_anend_bytes(length))
    add("anend_bytes_rev",   ks_anend_bytes_rev(length))
    add("anend_nibbles",     ks_anend_nibbles(length))
    nh = ks_payload_hex_nibbles(length)
    if nh:
        add("payload_hex_nibbles", nh)

    # 2c. Mayan + P.S.
    add("mayan",         ks_mayan(length))
    add("mayan_rev",     ks_mayan_rev(length))
    add("ps_single",     ks_ps_single(length))
    add("ps_pairs",      ks_ps_pairs(length))
    add("ps_rev",        ks_ps_rev(length))

    # 2e. Magic-square streams
    add("magic_sq_mod29",     ks_magic_sq_mod29(length))
    add("magic_sq_digits",    ks_magic_sq_digits(length))
    add("magic_sq_rowsums",   ks_magic_sq_rowsums(length))

    # 2f. Extended constants
    add("primes_to_109",       ks_primes_to_109(length))
    add("3301_decimal",        ks_3301_decimal(length))
    add("3301_powers_mod29",   ks_3301_powers_mod29(length))
    add("3301_phi_multiples",  ks_3301_phi_multiples(length))

    # 2g. Catalan / triangular / Lucas / partition
    add("catalan",       ks_catalan(length))
    add("triangular",    ks_triangular(length))
    add("lucas",         ks_lucas(length))
    add("partition",     ks_partition(length))
    add("partition_rev", ks_partition_rev(length))

    return catalog


# =============================================================================
# SECTION 4 -- SWEEP HELPERS
# =============================================================================

def _atbash(ct):
    return (N - 1 - ct) % N


def _score_page(ct_np, K_np, sign, offset, slen, screen_bw, full_bw, L):
    """Run screen beam then (if above threshold) confirm beam.
    Returns (screen_score, confirm_score_or_None, translit_or_None).
    """
    ct2 = ct_np  # already atbashed or not by caller
    pi_s = beam(ct2, K_np, sign, offset, min(slen, L), screen_bw)
    sc_s = Q.score_norm(idx_to_trans(pi_s))
    if sc_s <= SCREEN_THR:
        return sc_s, None, None
    pi_f = beam(ct2, K_np, sign, offset, L, full_bw)
    sc_f = Q.score_norm(idx_to_trans(pi_f))
    tl = idx_to_trans(pi_f) if sc_f > CONFIRM_THR else None
    return sc_s, sc_f, tl


def sweep_fixed_key(name, K_np, pages_np, offsets):
    """Sweep one fixed keystream over all pages x {sign, atbash, offsets}.

    Returns (hits list, best_screen float).
    """
    hits = []
    best = -99.0
    L_ks = len(K_np)
    for pg_idx, ct in enumerate(pages_np):
        L = len(ct)
        for sign in (-1, 1):
            for atb in (0, 1):
                ct2 = _atbash(ct) if atb else ct
                for off in offsets:
                    need = off + L + MAXSKIP * L + 8
                    if need > L_ks:
                        # not enough key material
                        break
                    sc_s, sc_f, tl = _score_page(ct2, K_np, sign, off,
                                                  SCREEN_LEN, SCREEN_BW, FULL_BW, L)
                    if sc_s > best:
                        best = sc_s
                    if tl is not None:
                        hits.append((sc_f, name, sign, atb, off, pg_idx, tl))
    return hits, best


def sweep_payload_all_offsets(payload_variants, pages_np):
    """Payload as key at ALL valid offsets (sliding window).

    For each page of length L and each payload variant of length 256:
      offset range is [0, 256-L) so the key window covers exactly the page.
    Both signs, atbash; for reversed variants the same offset range applies.

    Returns (hits list, best_screen float).
    """
    hits = []
    best = -99.0

    for vname, K_raw in payload_variants.items():
        # Build the keystream: payload mod 29, repeated just enough for
        # worst-case MAXSKIP expansion of the longest page.
        K_mod = (K_raw % N).astype(np.int64)
        # We need to tile it for the beam's max-skip look-ahead
        max_L = max(len(ct) for ct in pages_np)
        need_total = 256 + max_L * (MAXSKIP + 1) + 16
        # tile enough times
        reps = (need_total // len(K_mod)) + 2
        K_np = np.tile(K_mod, reps)

        for pg_idx, ct in enumerate(pages_np):
            L = len(ct)
            # Sliding-window: offset can range so that a rigid window covers
            # the page within the 256 bytes; skip allows a few extra so we
            # expand the range slightly.
            max_off = max(1, len(K_mod) - L + MAXSKIP * 4)
            for sign in (-1, 1):
                for atb in (0, 1):
                    ct2 = _atbash(ct) if atb else ct
                    for off in range(max_off):
                        sc_s, sc_f, tl = _score_page(ct2, K_np, sign, off,
                                                      SCREEN_LEN, SCREEN_BW, FULL_BW, L)
                        if sc_s > best:
                            best = sc_s
                        if tl is not None:
                            hits.append((sc_f, vname, sign, atb, off, pg_idx, tl))
    return hits, best


def sweep_page_seeded(pages_np, page_indices):
    """Per-page seeded keys: each page gets a unique key seeded by its index.

    For each mode and each page, only the CORRECT page is swept (offset 0 only,
    both signs, both atbash).

    Returns (hits list, best_screen float).
    """
    hits = []
    best = -99.0
    max_L = max(len(ct) for ct in pages_np)
    ks_len = max_L * (MAXSKIP + 1) + 16

    for mode in ("prime", "totient", "3301xor"):
        for real_idx, (pg_idx, ct) in enumerate(zip(page_indices, pages_np)):
            L = len(ct)
            ks = page_seeded_stream(pg_idx, ks_len, mode=mode)
            K_np = np.array(ks, dtype=np.int64)
            name = f"pgseed_{mode}_pg{pg_idx}"
            for sign in (-1, 1):
                for atb in (0, 1):
                    ct2 = _atbash(ct) if atb else ct
                    sc_s, sc_f, tl = _score_page(ct2, K_np, sign, 0,
                                                  SCREEN_LEN, SCREEN_BW, FULL_BW, L)
                    if sc_s > best:
                        best = sc_s
                    if tl is not None:
                        hits.append((sc_f, name, sign, atb, 0, pg_idx, tl))
    return hits, best


# =============================================================================
# SECTION 5 -- MAIN
# =============================================================================

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--full", action="store_true",
                    help="Run on all 55 unsolved pages (orchestrator mode).")
    ap.add_argument("--pages", default="",
                    help="Page range override, e.g. '0-9' (inclusive).")
    ap.add_argument("--report-above", type=float, default=-6.0)
    args = ap.parse_args()

    print("=" * 72)
    print("NUMERIC2 EXTENDED KEYSTREAM sweep (Campaign XVIII / numeric2_skip.py)")
    print("=" * 72)
    print(f"Screen: len={SCREEN_LEN} bw={SCREEN_BW} thr={SCREEN_THR}  |  "
          f"Confirm: bw={FULL_BW} thr={CONFIRM_THR}")
    print(f"Null-max={NULL_MAX}  |  English solve ~-4.0 to -4.35  |  MAXSKIP={MAXSKIP}")
    print()

    pages_all = load_pages()[:-2]   # 55 unsolved pages

    if args.pages:
        a, b = args.pages.split("-")
        sel = list(range(int(a), int(b) + 1))
    elif args.full:
        sel = list(range(len(pages_all)))
    else:
        sel = [0, 1, 2]   # smoke: first 3 pages

    pages_sel = [pages_all[i] for i in sel]
    pages_np  = [np.array(p, dtype=np.int64) for p in pages_sel]
    page_indices = sel

    max_L = max(len(p) for p in pages_sel)
    ks_len = max_L * (MAXSKIP + 1) + 64
    print(f"Pages: {sel[0]}..{sel[-1]}  ({len(sel)} pages)  |  max_len={max_L}  |  ks_len={ks_len}")
    print()

    all_hits = []
    best_score_seen = -99.0
    best_label = None

    # --- PART A: fixed keystreams (small offset sweep) -------------------------
    print("[A] Building fixed-length keystream catalog ...")
    fixed_offsets = list(range(5))   # 0..4; orchestrator can extend
    catalog = build_fixed_catalog(ks_len)
    print(f"    {len(catalog)} keystreams.  Offsets: {fixed_offsets}")
    print()
    t0 = time.time()

    for i, (name, K_np) in enumerate(catalog):
        h, bg = sweep_fixed_key(name, K_np, pages_np, fixed_offsets)
        all_hits.extend(h)
        if bg > best_score_seen:
            best_score_seen = bg
            best_label = name
        show = (bg > args.report_above) or (i % 10 == 0) or (i == len(catalog)-1)
        if show:
            flag = "  <== NOTABLE" if bg > args.report_above else ""
            print(f"  [{i:3d}] {name:<32}  screen_best={bg:7.3f}  {time.time()-t0:6.1f}s{flag}")
        if h:
            for hh in sorted(h, reverse=True)[:2]:
                print(f"          HIT score={hh[0]:.3f} sign={hh[2]} atb={hh[3]} "
                      f"off={hh[4]} pg={hh[5]}: {hh[6][:60]}")

    print(f"\n  [A] done in {time.time()-t0:.1f}s.  "
          f"Best so far: {best_score_seen:.3f} via '{best_label}'")
    print()

    # --- PART B: payload at ALL offsets (sliding window) -----------------------
    print("[B] Payload (pp49-51) at ALL offsets (sliding window) ...")
    payload_variants = load_payload_bytes()
    if not payload_variants:
        print("    WARNING: no payload .bin files found -- skipping Part B.")
    else:
        print(f"    {len(payload_variants)} variants: {list(payload_variants.keys())}")
        t1 = time.time()
        h, bg = sweep_payload_all_offsets(payload_variants, pages_np)
        all_hits.extend(h)
        if bg > best_score_seen:
            best_score_seen = bg
            best_label = "payload_all_offsets"
        print(f"  [B] done in {time.time()-t1:.1f}s.  Best screen: {bg:.3f}")
        if h:
            for hh in sorted(h, reverse=True)[:3]:
                print(f"       HIT score={hh[0]:.3f} {hh[1]} sign={hh[2]} atb={hh[3]} "
                      f"off={hh[4]} pg={hh[5]}: {hh[6][:60]}")
    print()

    # --- PART C: page-number-seeded keys --------------------------------------
    print("[C] Page-number-seeded keys (prime/totient/3301xor per page) ...")
    t2 = time.time()
    h, bg = sweep_page_seeded(pages_np, page_indices)
    all_hits.extend(h)
    if bg > best_score_seen:
        best_score_seen = bg
        best_label = "page_seeded"
    print(f"  [C] done in {time.time()-t2:.1f}s.  Best screen: {bg:.3f}")
    if h:
        for hh in sorted(h, reverse=True)[:3]:
            print(f"       HIT score={hh[0]:.3f} {hh[1]} sign={hh[2]} atb={hh[3]} "
                  f"off={hh[4]} pg={hh[5]}: {hh[6][:60]}")
    print()

    # ---- SUMMARY --------------------------------------------------------------
    elapsed = time.time() - t0
    print("=" * 72)
    print("SUMMARY")
    print("=" * 72)
    print(f"Parts A+B+C elapsed       : {elapsed:.1f}s")
    print(f"Best screen score seen    : {best_score_seen:.3f}  via '{best_label}'")
    print(f"Hits above CONFIRM_THR    : {len(all_hits)}")
    print(f"Scale: English ~-4.0 | CONFIRM -5.5 | null-max -6.82")
    print()

    if all_hits:
        print("CONFIRMED HITS (score > -5.5):")
        for h in sorted(all_hits, reverse=True):
            print(f"  score={h[0]:.3f}  ks={h[1]}  sign={h[2]}  atb={h[3]}  "
                  f"off={h[4]}  pg={h[5]}")
            print(f"  {h[6][:100]}")
        print()
        print("NOTE: run full 55-page sweep before declaring a hit confirmed.")
    else:
        print("NO hits above confirm threshold.")
        if best_score_seen > -7.0:
            print(f"  Best {best_score_seen:.3f} is in the noise band "
                  f"(-7.5 floor, null-max -6.82, no signal).")
        print("  Result: NULL -- consistent with OTP-class / skip-decoder confirms no signal.")

    return {"best_score_seen": best_score_seen,
            "hits": len(all_hits),
            "elapsed": elapsed}


if __name__ == "__main__":
    main()
