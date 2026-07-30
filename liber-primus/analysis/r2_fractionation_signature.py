"""R2-H1 — Fractionation coordinate-plane dispersion signature (pre-registered).

NON-DECRYPTING structural discriminator. We decompose each rune into coordinate
sub-streams under three fixed grid packings and measure the maximum normalized
autocorrelation over lags L in [2,40] across all sub-streams (A_max). A trifid /
Polybius-class fractionation cipher with a period injects a period-locked peak
into at least one coordinate sub-stream; a full-length (OTP-class) keystream does
not. We decrypt nothing and search no keys.

Utilities reused verbatim from the rig:
  - analysis/run_stats.py  load_pages()  (krisyotam transcription, '%' page split)
  - src/lp/gematria.py     N=29, canonical GP index order 0..28 (ᚠ=0)
  - src/lp/stats.py        ioc_norm

Fixed RNG seed 3301. Run: PYTHONUTF8=1 python analysis/r2_fractionation_signature.py
"""
import os
import sys
import math
import random
import collections

import numpy as np

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)                                   # run_stats
sys.path.insert(0, os.path.join(HERE, "..", "src"))        # lp package

from run_stats import load_pages                            # noqa: E402
from lp import gematria as gp, stats                        # noqa: E402

N = gp.N                                                    # 29
assert N == 29
SEED = 3301
LAGS = range(2, 41)                                         # [2,40] inclusive
N_SURR = 10_000
ABS_FLOOR = 0.05                                            # fixed decision threshold

# ---------------------------------------------------------------------------
# GRID PACKINGS — canonical GP index order 0..28 for all variants.
# Each returns a dict variant_name -> {substream_name: [coord per rune]}.
# The exact packing math is documented inline (pre-registered; no other packings
# are tried beyond these three).
# ---------------------------------------------------------------------------

def coords_P(i):
    """Variant P — Polybius 6x5=30 grid, row-major fill. Index 0..28 placed at
    (row, col) = (i // 5, i % 5); the 30th cell (i=29) is unused. 6 rows (0..5),
    5 cols (0..4). Two sub-streams: rows, cols."""
    return {"row": i // 5, "col": i % 5}


def coords_T(i):
    """Variant T — trifid 3x3x3=27 cube, LAYER-MAJOR fill (the standard trifid
    packing): index = layer*9 + row*3 + col, so
        layer = i // 9, row = (i // 3) % 3, col = i % 3.
    Leftover indices 27,28 (> 26) are assigned to a documented SPARE layer 3
    (the two Gematria extra/null slots): 27 -> (3,0,0), 28 -> (3,0,1). This keeps
    every coordinate numeric and deterministic. Three sub-streams: layer,row,col."""
    if i < 27:
        return {"layer": i // 9, "row": (i // 3) % 3, "col": i % 3}
    # spare layer for the two leftover indices
    return {"layer": 3, "row": 0, "col": i - 27}            # 27->col0, 28->col1


def coords_T2(i):
    """Variant T2 — trifid 3x3x3=27 cube, alternative packing with fill order
    TRANSPOSED (layer-major -> col-major / layer fastest-varying):
        index = col*9 + row*3 + layer, so
        layer = i % 3, row = (i // 3) % 3, col = i // 9.
    Same spare handling: leftover 27,28 -> spare col 3: 27 -> (0,0,3),
    28 -> (1,0,3). Three sub-streams: layer,row,col."""
    if i < 27:
        return {"layer": i % 3, "row": (i // 3) % 3, "col": i // 9}
    return {"layer": i - 27, "row": 0, "col": 3}            # 27->layer0, 28->layer1


VARIANTS = {"P": coords_P, "T": coords_T, "T2": coords_T2}

# Per-variant lookup tables: substream_name -> np.array of length 29 giving the
# coordinate value for rune index 0..28. A stream's sub-stream is then just
# LUT[stream_indices]; a surrogate is LUT[perm]. Semantics identical to coords_*.
_LAGS = np.array(list(LAGS))


def _build_luts():
    luts = {}
    for v, fn in VARIANTS.items():
        names = list(fn(0).keys())
        tab = {nm: np.empty(N, dtype=np.float64) for nm in names}
        for i in range(N):
            for nm, val in fn(i).items():
                tab[nm][i] = val
        luts[v] = tab
    return luts


_LUTS = _build_luts()


def _autocorr_all_lags(seq):
    """Vectorized Pearson autocorrelation for every lag in _LAGS. Returns array
    parallel to _LAGS. Identical math to autocorr() (constant window -> 0)."""
    x = seq
    n_tot = len(x)
    out = np.empty(len(_LAGS), dtype=np.float64)
    for k, lag in enumerate(_LAGS):
        a = x[:n_tot - lag]
        b = x[lag:]
        n = a.shape[0]
        if n < 3:
            out[k] = 0.0
            continue
        ma = a.mean(); mb = b.mean()
        da_ = a - ma; db_ = b - mb
        num = float(np.dot(da_, db_))
        da = math.sqrt(float(np.dot(da_, da_)))
        db = math.sqrt(float(np.dot(db_, db_)))
        out[k] = 0.0 if (da == 0.0 or db == 0.0) else num / (da * db)
    return out


def _a_max_variant_np(idx_arr, v):
    """A_max over lags and sub-streams for variant v, using LUTs. Returns
    (a_max, substream, lag). Signed-max convention (matches a_max_variant)."""
    best_a, best_ss, best_lag = -2.0, None, None
    for nm, lut in _LUTS[v].items():
        seq = lut[idx_arr]
        rr = _autocorr_all_lags(seq)
        j = int(np.argmax(rr))
        if rr[j] > best_a:
            best_a, best_ss, best_lag = float(rr[j]), nm, int(_LAGS[j])
    return best_a, best_ss, best_lag


def decompose(idxs, coord_fn):
    """Return {substream_name: [values]} for a rune-index stream."""
    streams = collections.defaultdict(list)
    for i in idxs:
        for name, v in coord_fn(i).items():
            streams[name].append(v)
    return dict(streams)


def autocorr(x, lag):
    """Normalized (Pearson) autocorrelation rho(lag) = corr(x_i, x_{i+lag}).
    Returns 0.0 for a degenerate (constant) window."""
    a = x[:len(x) - lag]
    b = x[lag:]
    n = len(a)
    if n < 3:
        return 0.0
    ma = sum(a) / n
    mb = sum(b) / n
    num = sum((ai - ma) * (bi - mb) for ai, bi in zip(a, b))
    da = math.sqrt(sum((ai - ma) ** 2 for ai in a))
    db = math.sqrt(sum((bi - mb) ** 2 for bi in b))
    if da == 0 or db == 0:
        return 0.0
    return num / (da * db)


def a_max_variant(idxs, coord_fn):
    """A_max over lags [2,40] and all sub-streams of ONE variant (pure-Python
    reference implementation; kept for auditability). Returns (a_max, sub, lag).
    Tracks the max of signed rho: a period-locked structure appears as a large
    positive autocorrelation, which is the fractionation signature."""
    best = (-2.0, None, None)
    for name, seq in decompose(idxs, coord_fn).items():
        for L in LAGS:
            r = autocorr(seq, L)
            if r > best[0]:
                best = (r, name, L)
    return best


def a_max_all(idxs):
    """Vectorized A_max per variant. Equivalent to a_max_variant for all variants
    (numpy path; verified against the pure-Python reference in __main__ self-test)."""
    arr = np.asarray(idxs, dtype=np.intp)
    return {v: _a_max_variant_np(arr, v) for v in VARIANTS}


# ---------------------------------------------------------------------------
# ANCHOR 1 — synthetic trifid positive control with a KNOWN injected period.
# ---------------------------------------------------------------------------

def build_synthetic_trifid(length, period, rng):
    """Encipher GP-mapped English through a classic trifid with a known period.

    Plaintext: deterministic English-like stream from the rig's quadgram model,
    mapped to GP indices (english_baseline path). Trifid steps:
      1. map each plaintext rune -> (layer,row,col) via the standard cube
         (coords_T packing, restricted to the 27-cube; indices 27,28 are remapped
         into the cube via i%27 for the synthetic PLAINTEXT so all coords are
         0..2 and the cube is invertible).
      2. write coords into three rows, read them off in PERIOD-length blocks
         (the canonical trifid fractionation step) -> this is what injects the
         period.
      3. regroup triples -> output runes.
    A key permutation of the 27 cube cells is applied (seeded) so output is not
    trivially the input. The injected structure lives at lag == period in the
    coordinate sub-streams."""
    from run_stats import english_baseline
    base = english_baseline()                               # GP indices of English
    # tile to requested length
    pt = [base[i % len(base)] % 27 for i in range(length)]

    # seeded cube-cell permutation (the 'key square'): 0..26 -> 0..26
    perm = list(range(27))
    rng.shuffle(perm)
    pt = [perm[v] for v in pt]

    def to_coords(v):
        return (v // 9, (v // 3) % 3, v % 3)

    def from_coords(l, r, c):
        return l * 9 + r * 3 + c

    out = []
    for s in range(0, len(pt), period):
        block = pt[s:s + period]
        if len(block) < 3:
            out.extend(block)                               # tail passthrough
            continue
        Ls, Rs, Cs = [], [], []
        for v in block:
            l, r, c = to_coords(v)
            Ls.append(l); Rs.append(r); Cs.append(c)
        seq = Ls + Rs + Cs                                  # fractionate: rows read serially
        # regroup into triples and rebuild cube values
        for k in range(0, len(seq) - 2, 3):
            out.append(from_coords(seq[k], seq[k + 1], seq[k + 2]))
        # any remainder passthrough
        rem = len(seq) - (len(seq) // 3) * 3
        for k in range(len(seq) - rem, len(seq)):
            out.append(seq[k] % 27)
    # scatter back over full 29-symbol alphabet deterministically (embed cube)
    out29 = [(v % 27) for v in out][:length]
    return out29


# ---------------------------------------------------------------------------
# NULL MODEL — order-matched surrogates (permute the exact rune multiset).
# ---------------------------------------------------------------------------

def surrogate_null(idxs, n_surr, rng):
    """For each variant, distribution of surrogate A_max over n_surr uniform
    random permutations of the EXACT rune multiset (rune counts fixed)."""
    dists = {v: [] for v in VARIANTS}
    base = list(idxs)                       # rng.shuffle drives the fixed seed stream
    for _ in range(n_surr):
        rng.shuffle(base)
        arr = np.asarray(base, dtype=np.intp)
        for v in VARIANTS:
            dists[v].append(_a_max_variant_np(arr, v)[0])
    stats_out = {}
    for v, arr in dists.items():
        arr_s = sorted(arr)
        m = sum(arr) / len(arr)
        sd = math.sqrt(sum((x - m) ** 2 for x in arr) / len(arr))
        def pct(p):
            k = min(len(arr_s) - 1, int(math.ceil(p / 100 * len(arr_s))) - 1)
            return arr_s[max(0, k)]
        stats_out[v] = {"mean": m, "sd": sd, "p99": pct(99), "p999": pct(99.9)}
    return stats_out


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    pages = load_pages()
    unsolved = [i for p in pages[:-2] for i in p]           # 12,956 runes
    an_end = pages[-2]                                       # index 55 = AN END (totient)

    report = []
    report.append("=" * 72)
    report.append("R2-H1  Fractionation coordinate-plane dispersion signature")
    report.append(f"seed={SEED}  N={N}  lags=[2,40]  surrogates={N_SURR}  "
                  f"abs_floor={ABS_FLOOR}")
    report.append(f"unsolved runes={len(unsolved)}  AN END runes={len(an_end)}")
    report.append("=" * 72)

    # ---- ANCHOR 1: synthetic positive -------------------------------------
    rng = random.Random(SEED)
    INJECTED = 13
    synth = build_synthetic_trifid(len(unsolved), INJECTED, rng)
    syn_res = a_max_all(synth)
    # report per-variant; the injected period should surface as a peak
    syn_best_v = max(syn_res, key=lambda v: syn_res[v][0])
    syn_a, syn_ss, syn_lag = syn_res[syn_best_v]
    # surrogate 99.9th for synthetic (same multiset) for a fair threshold
    rng_s = random.Random(SEED + 1)
    syn_null = surrogate_null(synth, 1000, rng_s)            # 1k is ample for a control
    syn_thr = syn_null[syn_best_v]["p999"]
    syn_peak_matches = abs(syn_lag - INJECTED) <= 1 or (syn_lag % INJECTED == 0) \
        or (INJECTED % syn_lag == 0 if syn_lag else False)
    syn_pass = (syn_a > syn_thr) and (syn_a >= ABS_FLOOR) and syn_peak_matches

    report.append("\n[ANCHOR 1] SYNTHETIC POSITIVE (known trifid, injected period)")
    report.append(f"  injected period            : {INJECTED}")
    for v in ("P", "T", "T2"):
        a, ss, lag = syn_res[v]
        report.append(f"  variant {v:2s} A_max={a:+.4f}  (sub={ss}, lag={lag})")
    report.append(f"  best variant={syn_best_v}  A_max={syn_a:+.4f} at lag={syn_lag} "
                  f"(sub={syn_ss})")
    report.append(f"  surrogate 99.9th (best var): {syn_thr:.4f}")
    report.append(f"  peak recovers injected period (lag == k*{INJECTED} +-1): "
                  f"{syn_peak_matches}")
    report.append(f"  ANCHOR 1 => {'PASS' if syn_pass else 'FAIL'}")
    if not syn_pass:
        report.append("  *** HARNESS BROKEN — synthetic positive did not surface the "
                       "injected period. STOP. ***")

    # ---- ANCHOR 2: AN END real-page negative control ----------------------
    ae_res = a_max_all(an_end)
    rng_ae = random.Random(SEED + 2)
    ae_null = surrogate_null(an_end, 2000, rng_ae)          # shorter page -> more surr ok
    ae_best_v = max(ae_res, key=lambda v: ae_res[v][0])
    ae_a, ae_ss, ae_lag = ae_res[ae_best_v]
    ae_thr = ae_null[ae_best_v]["p999"]
    ae_below = (ae_a <= ae_thr) or (ae_a < ABS_FLOOR)
    report.append("\n[ANCHOR 2] REAL-PAGE NEGATIVE CONTROL — AN END (totient keystream)")
    for v in ("P", "T", "T2"):
        a, ss, lag = ae_res[v]
        report.append(f"  variant {v:2s} A_max={a:+.4f}  (sub={ss}, lag={lag})  "
                      f"surr99.9={ae_null[v]['p999']:.4f}")
    report.append(f"  best variant={ae_best_v}  A_max={ae_a:+.4f}  "
                  f"surr99.9={ae_thr:.4f}  abs_floor={ABS_FLOOR}")
    report.append(f"  NO period peak (below threshold OR below abs floor): {ae_below}")
    report.append(f"  ANCHOR 2 => {'PASS' if ae_below else 'FAIL'}")

    # ---- ANCHOR 3: aggregate-IoC coherence --------------------------------
    iocn = stats.ioc_norm(unsolved)
    report.append("\n[ANCHOR 3] AGGREGATE-IoC COHERENCE")
    report.append(f"  observed unsolved IoC*N    : {iocn:.4f}  (random ~ 1.00)")
    report.append(f"  bifid fractionation floor  : 1.39  (repo-measured)")
    report.append(f"  IoC*N below fractionation floor 1.39: {iocn < 1.39}")

    # ---- REAL LP2: A_max per variant + surrogate null ---------------------
    real_res = a_max_all(unsolved)
    rng_r = random.Random(SEED + 3)
    report.append(f"\n[REAL LP2 UNSOLVED]  computing {N_SURR} surrogates per variant "
                  f"(seed {SEED+3}) ...")
    real_null = surrogate_null(unsolved, N_SURR, rng_r)

    report.append("\n[REAL LP2 UNSOLVED — RESULTS]")
    conf_variants = []
    peak_lags = {}
    for v in ("P", "T", "T2"):
        a, ss, lag = real_res[v]
        nd = real_null[v]
        peak_lags[v] = lag
        super_thr = a > nd["p999"]
        conf_variants.append(super_thr and a >= ABS_FLOOR)
        report.append(f"  variant {v:2s}: A_max={a:+.4f}  (sub={ss}, lag={lag})")
        report.append(f"            surrogate null: mean={nd['mean']:.4f} "
                      f"sd={nd['sd']:.4f} p99={nd['p99']:.4f} p99.9={nd['p999']:.4f}")
        report.append(f"            A_max > surr p99.9? {super_thr}   "
                      f"A_max >= {ABS_FLOOR}? {a >= ABS_FLOOR}")

    # peak-lag reproducibility across >=2 of 3 variants (within +-1)
    lags = list(peak_lags.values())
    reproduces = False
    for i in range(len(lags)):
        cnt = sum(1 for j in range(len(lags)) if abs(lags[i] - lags[j]) <= 1)
        if cnt >= 2:
            reproduces = True
            break

    # ---- VERDICT (fixed pre-registered threshold) -------------------------
    cond_super = any(conf_variants)   # at least one variant super-threshold + abs floor
    # Strict reading: CONFIRM iff (A_max(real) > p99.9 AND >=0.05) for the deciding
    # variant AND peak lag reproduces within +-1 across >=2 variants.
    confirm = cond_super and reproduces
    report.append("\n[VERDICT]")
    report.append(f"  any variant A_max>surr_p99.9 AND >=0.05 : {cond_super}")
    report.append(f"  peak lag reproduces +-1 across >=2 vars : {reproduces} "
                  f"(lags P={peak_lags['P']}, T={peak_lags['T']}, T2={peak_lags['T2']})")
    if not (syn_pass and ae_below):
        report.append("  ANCHORS INVALID — harness precondition failed; verdict "
                      "not decision-grade.")
    report.append(f"  ==> {'CONFIRM' if confirm else 'REFUTE'} fractionation-signature")

    out = "\n".join(report)
    print(out)
    return out


def _selftest():
    """Confirm the vectorized path reproduces the pure-Python reference exactly
    on a small stream (guards against an optimization changing the statistic)."""
    rng = random.Random(SEED)
    sample = [rng.randrange(N) for _ in range(400)]
    for v, fn in VARIANTS.items():
        ref = a_max_variant(sample, fn)
        arr = np.asarray(sample, dtype=np.intp)
        got = _a_max_variant_np(arr, v)
        assert abs(ref[0] - got[0]) < 1e-9 and ref[1] == got[1] and ref[2] == got[2], \
            f"selftest mismatch variant {v}: ref={ref} got={got}"


if __name__ == "__main__":
    _selftest()
    main()
