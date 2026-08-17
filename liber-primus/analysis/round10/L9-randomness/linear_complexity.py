"""L9 / T2 + T4 — LINEAR COMPLEXITY, the headline test of this lane.

Berlekamp-Massey over GF(29) directly, and over GF(2) on the binary mappings.
This is the GENERATOR-AGNOSTIC version of Round 8's SEED axis: it asks whether
the stream is the output of ANY finite-state linear device, without guessing a
seed or naming a generator.

T4 (the validity gate) runs FIRST and is pass/fail on the INSTRUMENT. If BM does
not recover a planted LFSR's degree, the null on the real stream means nothing.
The gate also measures what the documented anti-repeat filter does to linear
complexity, which is the scope limit of the whole test.
"""
import os, sys, json, time
import numpy as np
from lib import (load_ct, build_streams, MAPS, MAP_NOTE, N_SYM, P_KEEP,
                 gen_urand, gen_arfilt, doublet_rate)

HERE = os.path.dirname(os.path.abspath(__file__))
INV29 = [0] + [pow(i, N_SYM - 2, N_SYM) for i in range(1, N_SYM)]


# ------------------------------------------------- Berlekamp-Massey over GF(p)
def bm_gfp(s, p=N_SYM, want_profile=False):
    n = len(s)
    s = np.asarray(s, np.int64) % p
    inv = INV29 if p == N_SYM else [0] + [pow(i, p - 2, p) for i in range(1, p)]
    C = np.zeros(n + 1, np.int64); C[0] = 1
    B = np.zeros(n + 1, np.int64); B[0] = 1
    L = 0; m = -1; b = 1
    prof = np.zeros(n, np.int32) if want_profile else None
    njump = 0
    for k in range(n):
        if L > 0:
            d = int((s[k] + int(np.dot(C[1:L + 1], s[k - L:k][::-1]))) % p)
        else:
            d = int(s[k]) % p
        if d != 0:
            T = C.copy()
            coef = (d * inv[b]) % p
            sh = k - m
            C[sh:] = (C[sh:] - coef * B[:len(C) - sh]) % p
            if 2 * L <= k:
                L = k + 1 - L; B = T; b = d; m = k
                njump += 1
        if want_profile:
            prof[k] = L
    return L, prof, njump


# ------------------------------------------------- Berlekamp-Massey over GF(2)
def bm_gf2(bits):
    """Bit-packed BM. bits: 0/1 array. Returns (LC, n_jumps)."""
    n = len(bits)
    C = 1; B = 1
    L = 0; m = -1
    R = 0                      # R bit i == s[k-i]
    njump = 0
    bl = bits.tolist()
    for k in range(n):
        R = (R << 1) | bl[k]
        d = (C & R).bit_count() & 1
        if d:
            T = C
            C ^= (B << (k - m))
            if 2 * L <= k:
                L = k + 1 - L; B = T; m = k
                njump += 1
    return L, njump


# ------------------------------------------------------------------ T4 GATE
def lfsr_gf29(n, deg, seed=7):
    rng = np.random.default_rng(seed)
    taps = rng.integers(1, N_SYM, size=deg, dtype=np.int64)
    st = list(rng.integers(0, N_SYM, size=deg, dtype=np.int64))
    out = []
    for _ in range(n):
        v = int(sum(int(taps[i]) * int(st[-1 - i]) for i in range(deg)) % N_SYM)
        out.append(v); st.append(v)
    return np.array(out, np.int64), taps


def lcg_stream(n, seed=12345):
    x = seed; out = []
    for _ in range(n):
        x = (1103515245 * x + 12345) & 0x7FFFFFFF
        out.append(x % N_SYM)
    return np.array(out, np.int64)


def antirepeat_rewrite(a, rng, p_keep=P_KEEP):
    """Apply the DOCUMENTED soft anti-repeat rule to an existing stream by
    re-drawing from the generator's own continuation (encoder-side rejection)."""
    out = []
    prev = -1
    i = 0
    keep = rng.random(size=len(a)) < p_keep
    for _ in range(len(a)):
        while i < len(a):
            c = int(a[i]); k = bool(keep[i]); i += 1
            if c != prev or k:
                break
        else:
            break
        out.append(c); prev = c
    return np.array(out, np.int64)


def run_gate():
    print('=' * 74)
    print('T4 VALIDITY GATE  (pass/fail on the INSTRUMENT, not on the ciphertext)')
    print('=' * 74)
    res = {}
    n = 12956
    rng = np.random.default_rng(99)

    for deg in (10, 40, 120):
        s, _ = lfsr_gf29(n, deg)
        L, _, _ = bm_gfp(s)
        ok = (L == deg)
        print('  GF(29) LFSR degree %-4d -> BM recovers LC = %-6d  %s'
              % (deg, L, 'PASS' if ok else 'FAIL'))
        res['lfsr_gf29_deg%d' % deg] = {'true_degree': deg, 'bm_lc': int(L), 'pass': bool(ok)}

    # LCG mod 29 (nonlinear over GF(29) but finite state -> should NOT be n/2)
    s = lcg_stream(n)
    L, _, _ = bm_gfp(s)
    print('  32-bit LCG %% 29         -> LC = %-6d  (n/2 = %d)' % (L, n // 2))
    res['lcg_mod29'] = {'bm_lc': int(L), 'n_over_2': n // 2}

    # THE SCOPE QUESTION: what does the anti-repeat filter do to LC?
    s40, _ = lfsr_gf29(int(n * 1.5), 40)
    f = antirepeat_rewrite(s40, rng)[:n]
    Lf, _, _ = bm_gfp(f)
    print('  GF(29) LFSR deg 40 THROUGH the anti-repeat filter -> LC = %-6d '
          '(doublet %.3f%%)' % (Lf, 100 * doublet_rate(f)))
    res['lfsr40_antirepeat'] = {'bm_lc': int(Lf), 'doublet': doublet_rate(f)}

    # GF(2) gate
    for deg in (16, 64):
        rng2 = np.random.default_rng(deg)
        taps = rng2.integers(0, 2, size=deg)
        st = list(rng2.integers(0, 2, size=deg))
        while sum(st) == 0:
            st = list(rng2.integers(0, 2, size=deg))
        bits = []
        for _ in range(20000):
            v = int(sum(int(taps[i]) * int(st[-1 - i]) for i in range(deg)) % 2)
            bits.append(v); st.append(v)
        L2, _ = bm_gf2(np.array(bits, np.uint8))
        ok = (L2 <= deg)
        print('  GF(2)  LFSR degree %-4d -> BM recovers LC = %-6d  %s'
              % (deg, L2, 'PASS' if ok else 'FAIL'))
        res['lfsr_gf2_deg%d' % deg] = {'true_degree': deg, 'bm_lc': int(L2), 'pass': bool(ok)}

    allpass = all(v.get('pass', True) for v in res.values())
    print('  GATE VERDICT: %s' % ('PASS - instrument is valid' if allpass else 'FAIL'))
    res['gate_pass'] = bool(allpass)
    return res


# ------------------------------------------------------------------ T2 MAIN
def run_t2(n_rep=20):
    print()
    print('=' * 74)
    print('T2  LINEAR COMPLEXITY over GF(29) — REAL vs matched controls')
    print('=' * 74)
    S = build_streams(n_rep=n_rep)
    n = 12956
    out = {'n': n, 'n_over_2': n / 2, 'n_rep': n_rep, 'gf29': {}}

    t0 = time.time()
    Lreal, prof, jreal = bm_gfp(S['REAL'][0], want_profile=True)
    print('  REAL    LC = %6d   jumps = %4d   (%.1fs)' % (Lreal, jreal, time.time() - t0))
    out['gf29']['REAL'] = {'lc': int(Lreal), 'jumps': int(jreal)}
    np.save(os.path.join(HERE, 'lc_profile_real.npy'), prof)

    for name in ('SHUF', 'URAND', 'ARFILT'):
        Ls, Js = [], []
        for a in S[name]:
            L, _, j = bm_gfp(a)
            Ls.append(L); Js.append(j)
        Ls = np.array(Ls)
        out['gf29'][name] = {'lc_mean': float(Ls.mean()), 'lc_sd': float(Ls.std(ddof=1)),
                             'lc_min': int(Ls.min()), 'lc_max': int(Ls.max()),
                             'lc_all': [int(x) for x in Ls],
                             'jumps_mean': float(np.mean(Js))}
        print('  %-7s LC mean %8.1f sd %5.2f  range [%d, %d]   jumps~%.0f'
              % (name, Ls.mean(), Ls.std(ddof=1), Ls.min(), Ls.max(), np.mean(Js)))

    ar = np.array(out['gf29']['ARFILT']['lc_all'])
    z = (Lreal - ar.mean()) / ar.std(ddof=1)
    inband = ar.min() <= Lreal <= ar.max()
    hit = (Lreal < 0.45 * n) or (Lreal < ar.min() - 3 * ar.std(ddof=1))
    out['gf29']['decision'] = {'z_vs_arfilt': float(z), 'in_arfilt_range': bool(inband),
                               'threshold_045n': 0.45 * n, 'HIT': bool(hit)}
    print('  --> REAL z vs ARFILT = %+.2f ; in ARFILT range: %s ; 0.45n = %.0f'
          % (z, inband, 0.45 * n))
    print('  --> T2 GF(29) VERDICT: %s' % ('HIT' if hit else 'NULL (no finite-state signature)'))

    # ---- GF(2) on the binary mappings
    print()
    print('  GF(2) linear complexity on binary mappings (REAL vs ARFILT x %d)' % min(n_rep, 5))
    out['gf2'] = {}
    for mk in ('M1', 'M2', 'M3'):
        fn = MAPS[mk]
        b = fn(S['REAL'][0])
        t0 = time.time()
        Lr, jr = bm_gf2(b)
        ctrl = []
        for a in S['ARFILT'][:min(n_rep, 5)]:
            bb = fn(a)
            Lc, _ = bm_gf2(bb[:len(b)])
            ctrl.append(Lc)
        ctrl = np.array(ctrl)
        nb = len(b)
        hit2 = Lr < 0.45 * nb or Lr < ctrl.min() - 3 * max(ctrl.std(ddof=1), 1e-9)
        out['gf2'][mk] = {'nbits': int(nb), 'lc_real': int(Lr),
                          'lc_ctrl_mean': float(ctrl.mean()), 'lc_ctrl_min': int(ctrl.min()),
                          'lc_ctrl_max': int(ctrl.max()), 'n_over_2': nb / 2,
                          'HIT': bool(hit2)}
        print('    %s nbits=%6d  REAL LC=%6d (n/2=%7.0f)  ARFILT LC %6.0f..%6d  -> %s  (%.0fs)'
              % (mk, nb, Lr, nb / 2, ctrl.min(), ctrl.max(),
                 'HIT' if hit2 else 'NULL', time.time() - t0))
    return out


if __name__ == '__main__':
    res = {'gate': run_gate(), 't2': run_t2(n_rep=int(sys.argv[1]) if len(sys.argv) > 1 else 20)}
    with open(os.path.join(HERE, 'results_linear_complexity.json'), 'w') as f:
        json.dump(res, f, indent=2)
    print('\nwrote results_linear_complexity.json')
