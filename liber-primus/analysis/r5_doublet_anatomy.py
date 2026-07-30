"""R5-COMBINED — Residual-doublet structural anatomy + polygraphic-parity
discriminator (pre-registered, NON-DECRYPTING).

We characterize the 86 residual doublets of the 55 unsolved LP2 pages (12,956
runes, 458 ᚠ left in) and their lag structure. We decrypt nothing and search no
keys. The battery discriminates a polygraphic (Playfair-class) pair operator and
a ciphertext-autokey (fixed -K) fingerprint from a structureless keystream.

Utilities reused verbatim from the rig:
  - analysis/run_stats.py  load_pages()      (krisyotam transcription, '%' split)
  - analysis/run_stats.py  english_baseline() (GP-mapped English for the control)
  - src/lp/gematria.py     N=29, canonical GP index order 0..28 (ᚠ=0)
  - src/lp/stats.py        ioc_norm, doublet_count

NULL (main ensemble, S1-S4): 10,000 order-matched surrogates fixing the EXACT
rune multiset AND the total doublet count (86), randomizing doublet positions.
Built by: plain multiset shuffle -> count-changing swaps that greedily drive the
doublet count DOWN to exactly 86 -> a long run of doublet-count-PRESERVING swaps
to randomize where the 86 doublets sit. ONE ensemble is reused for every S1-S4
sub-statistic. For S5 the surrogate is the standard multiset permutation (lag-k
under multiset shuffle), per spec.

DEGENERATE-NULL GUARD: for every statistic we check surrogate sd > 0; a
degenerate (sd == 0) arm is disclosed and EXCLUDED from the CONFIRM logic.

Fixed RNG seed 3301. NO scipy: chi2 survival and Kolmogorov CDF are implemented
in-file (documented series). Run:
  PYTHONUTF8=1 python analysis/r5_doublet_anatomy.py
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

from run_stats import load_pages, english_baseline          # noqa: E402
from lp import gematria as gp, stats, corpus                 # noqa: E402

N = gp.N
assert N == 29
SEED = 3301
N_SURR = 10_000

# =====================================================================
# analytic p-value helpers (no scipy)
# =====================================================================

def _gammainc_upper_regularized(s, x):
    """Regularized upper incomplete gamma Q(s,x)=Gamma(s,x)/Gamma(s).
    Uses the standard series (lower) for x<s+1 and the continued fraction
    (upper) otherwise (Numerical Recipes gammp/gammq). Returns Q(s,x)."""
    if x < 0 or s <= 0:
        return float("nan")
    if x == 0:
        return 1.0
    gln = math.lgamma(s)
    if x < s + 1.0:
        # series for the lower regularized P(s,x); Q = 1 - P
        ap = s
        summ = 1.0 / s
        delv = summ
        for _ in range(1000):
            ap += 1.0
            delv *= x / ap
            summ += delv
            if abs(delv) < abs(summ) * 1e-15:
                break
        P = summ * math.exp(-x + s * math.log(x) - gln)
        return 1.0 - P
    else:
        # continued fraction for Q directly
        b = x + 1.0 - s
        c = 1.0 / 1e-300
        d = 1.0 / b
        h = d
        for i in range(1, 1000):
            an = -i * (i - s)
            b += 2.0
            d = an * d + b
            if abs(d) < 1e-300:
                d = 1e-300
            c = b + an / c
            if abs(c) < 1e-300:
                c = 1e-300
            d = 1.0 / d
            delv = d * c
            h *= delv
            if abs(delv - 1.0) < 1e-15:
                break
        return math.exp(-x + s * math.log(x) - gln) * h


def chi2_sf(x, df):
    """Survival function P(X^2 > x) for chi-square with df d.o.f."""
    if x <= 0:
        return 1.0
    if df <= 0:
        return float("nan")
    return _gammainc_upper_regularized(df / 2.0, x / 2.0)


def ks_pvalue(d, n):
    """Asymptotic two-sided one-sample KS p-value via the Kolmogorov
    distribution: P(D>d) = Q_KS(sqrt(n)*d), Q_KS(t)=2*sum_{k>=1}(-1)^{k-1}
    e^{-2 k^2 t^2}. Standard large-sample approximation."""
    if n <= 0:
        return float("nan")
    t = (math.sqrt(n) + 0.12 + 0.11 / math.sqrt(n)) * d   # Stephens correction
    if t < 1e-3:
        return 1.0
    s = 0.0
    for k in range(1, 101):
        term = 2.0 * ((-1) ** (k - 1)) * math.exp(-2.0 * k * k * t * t)
        s += term
        if abs(term) < 1e-12:
            break
    return max(0.0, min(1.0, s))


# =====================================================================
# core statistics on an index sequence
# =====================================================================

def doublet_positions(seq):
    """Indices i (0-based) such that seq[i]==seq[i+1]. Returns list of i."""
    return [i for i in range(len(seq) - 1) if seq[i] == seq[i + 1]]


def s1_parity(seq):
    """S1 PARITY SPLIT under both phase assignments.
    A doublet occupies adjacency (i, i+1). Under a phase p (pair origin at
    index p, p in {0,1}), the digraphs are (p,p+1),(p+2,p+3),...
      - 'within-pair' (even->odd join): adjacency (i,i+1) with i-p even.
      - 'across-boundary' (odd->even join): adjacency (i,i+1) with i-p odd.
    Rate = (#doublets of that kind) / (#adjacencies of that kind).
    Returns dict phase-> (within_rate, across_rate, delta, n_within, n_across,
    d_within, d_across)."""
    L = len(seq)
    dpos = set(doublet_positions(seq))
    out = {}
    for p in (0, 1):
        n_within = n_across = d_within = d_across = 0
        for i in range(L - 1):
            if (i - p) % 2 == 0:               # even->odd join (within a digraph)
                n_within += 1
                if i in dpos:
                    d_within += 1
            else:                               # odd->even join (across boundary)
                n_across += 1
                if i in dpos:
                    d_across += 1
        wr = d_within / n_within if n_within else 0.0
        ar = d_across / n_across if n_across else 0.0
        out[p] = {
            "within_rate": wr, "across_rate": ar, "delta": wr - ar,
            "n_within": n_within, "n_across": n_across,
            "d_within": d_within, "d_across": d_across,
        }
    return out


def s2_digraph_ioc(seq):
    """S2 non-overlapping digraph IoC*N over the 29x29 pair space vs monograph
    IoC*N. Returns (digraph_iocN, monograph_iocN). Digraph space size = N*N."""
    L = len(seq)
    toks = [seq[j] * N + seq[j + 1] for j in range(0, L - 1, 2)]
    cnt = collections.Counter(toks)
    n = len(toks)
    if n < 2:
        dioc = 0.0
    else:
        num = sum(c * (c - 1) for c in cnt.values())
        dioc = (num / (n * (n - 1))) * (N * N)     # normalized by pair-alphabet size
    return dioc, stats.ioc_norm(seq)


def s3_identity(seq):
    """S3 doubled-rune identity multiset. Returns (counts array len N over the
    doubled-rune value, expected array under unigram doublet model, chi2, df,
    top_rune, top_count, top_expected). Expected count of value v among the D
    doublets is proportional to p_v^2 (a doublet at a random adjacency has both
    runes equal to v with prob p_v^2), normalized to sum to D."""
    dpos = doublet_positions(seq)
    D = len(dpos)
    obs = np.zeros(N)
    for i in dpos:
        obs[seq[i]] += 1
    cnt = collections.Counter(seq)
    L = len(seq)
    p = np.array([cnt.get(v, 0) / L for v in range(N)])
    w = p * p
    exp = w / w.sum() * D
    # chi2 over cells with exp>0
    mask = exp > 0
    chi2 = float(np.sum((obs[mask] - exp[mask]) ** 2 / exp[mask]))
    df = int(mask.sum()) - 1
    top = int(np.argmax(obs))
    return obs, exp, chi2, df, top, int(obs[top]), float(exp[top])


def s4_gap_ks(seq):
    """S4 KS of inter-doublet gaps vs a geometric null with matched mean.
    Gaps = differences between successive doublet START positions. Geometric
    null CDF F(g)=1-(1-q)^g, g>=1, with q=1/mean_gap (matched mean). Returns
    (ks_stat, ks_p, n_gaps, mean_gap)."""
    dpos = doublet_positions(seq)
    if len(dpos) < 3:
        return float("nan"), float("nan"), 0, float("nan")
    gaps = np.diff(np.array(dpos))               # >=1
    gaps = gaps[gaps >= 1]
    n = len(gaps)
    mean_gap = float(gaps.mean())
    if mean_gap <= 1.0:
        return float("nan"), float("nan"), n, mean_gap
    q = 1.0 / mean_gap                            # geometric on {1,2,...} mean=1/q
    xs = np.sort(gaps)
    # empirical vs geometric CDF; two-sided KS (both jump sides)
    Fu = 1.0 - (1.0 - q) ** xs                    # F at each observed gap (upper)
    ecdf_hi = np.arange(1, n + 1) / n
    ecdf_lo = np.arange(0, n) / n
    d = float(max(np.max(np.abs(ecdf_hi - Fu)), np.max(np.abs(ecdf_lo - Fu))))
    return d, ks_pvalue(d, n), n, mean_gap


def s5_lag_spectrum(seq, kmax=6):
    """S5 lag-k repeat rate r_k = fraction of positions i with c[i]==c[i-k],
    k=1..kmax. Returns list r_1..r_kmax."""
    L = len(seq)
    arr = np.asarray(seq)
    out = []
    for k in range(1, kmax + 1):
        if L - k <= 0:
            out.append(0.0); continue
        out.append(float(np.mean(arr[k:] == arr[:-k])))
    return out


# =====================================================================
# NULL ENSEMBLES
# =====================================================================

def _count_doublets_np(arr):
    return int(np.sum(arr[1:] == arr[:-1]))


def make_fixed_doublet_surrogate(multiset, target_D, rng, mix_swaps):
    """Return a numpy array: a permutation of `multiset` with EXACTLY target_D
    adjacent-equal pairs and randomized doublet placement.

    Phase 1: plain shuffle.
    Phase 2: count-changing random swaps, accept a swap only if it moves the
             doublet count toward target_D (monotone descent to target_D).
    Phase 3: mix_swaps random swaps that PRESERVE the doublet count (accept iff
             count unchanged) to randomize where the target_D doublets sit.
    The rune multiset is invariant under swaps, so it is fixed exactly."""
    a = np.array(multiset, dtype=np.int64)
    rng.shuffle(a)
    L = len(a)

    def local_doublets(i):
        c = 0
        if i > 0 and a[i - 1] == a[i]:
            c += 1
        if i + 1 < L and a[i] == a[i + 1]:
            c += 1
        return c

    D = _count_doublets_np(a)
    # Phase 2: drive D down to target (real deficit => target < shuffle mean)
    guard = 0
    max_guard = 400 * L
    while D != target_D and guard < max_guard:
        guard += 1
        i = rng.randrange(L)
        j = rng.randrange(L)
        if i == j or a[i] == a[j]:
            continue
        before = local_doublets(i) + local_doublets(j)
        if abs(i - j) == 1:                       # adjacent pair double-counts join
            before -= (1 if a[i] == a[j] else 0)  # a[i]!=a[j] here, so no change
        a[i], a[j] = a[j], a[i]
        after = local_doublets(i) + local_doublets(j)
        newD = D - before + after
        # accept iff it reduces the distance to target
        if abs(newD - target_D) < abs(D - target_D):
            D = newD
        else:
            a[i], a[j] = a[j], a[i]              # revert
    # Phase 3: count-preserving mixing
    m = 0
    while m < mix_swaps:
        i = rng.randrange(L)
        j = rng.randrange(L)
        if i == j or a[i] == a[j]:
            continue
        before = local_doublets(i) + local_doublets(j)
        a[i], a[j] = a[j], a[i]
        after = local_doublets(i) + local_doublets(j)
        newD = D - before + after
        if newD == D:
            m += 1                                # accepted, keep
        else:
            a[i], a[j] = a[j], a[i]              # revert
    return a, D


def build_main_ensemble(seq, target_D, n_surr, seed, mix_swaps):
    """Build n_surr fixed-multiset fixed-doublet-count surrogates and evaluate
    every S1-S4 statistic on each. Returns dict of lists keyed by statistic."""
    rng = random.Random(seed)
    multiset = list(seq)
    acc = {
        "s1_p0_within": [], "s1_p0_across": [], "s1_p0_delta": [],
        "s1_p1_within": [], "s1_p1_across": [], "s1_p1_delta": [],
        "s2_digraph": [], "s2_mono": [],
        "s3_chi2": [], "s3_topcount": [],
        "s4_ks": [],
        "realizedD": [],
    }
    ok = 0
    for _ in range(n_surr):
        arr, D = make_fixed_doublet_surrogate(multiset, target_D, rng, mix_swaps)
        s = arr.tolist()
        acc["realizedD"].append(D)
        if D == target_D:
            ok += 1
        p = s1_parity(s)
        acc["s1_p0_within"].append(p[0]["within_rate"])
        acc["s1_p0_across"].append(p[0]["across_rate"])
        acc["s1_p0_delta"].append(p[0]["delta"])
        acc["s1_p1_within"].append(p[1]["within_rate"])
        acc["s1_p1_across"].append(p[1]["across_rate"])
        acc["s1_p1_delta"].append(p[1]["delta"])
        di, mo = s2_digraph_ioc(s)
        acc["s2_digraph"].append(di)
        acc["s2_mono"].append(mo)
        _, _, chi2, _, _, topc, _ = s3_identity(s)
        acc["s3_chi2"].append(chi2)
        acc["s3_topcount"].append(topc)
        ksd, _, _, _ = s4_gap_ks(s)
        acc["s4_ks"].append(ksd if ksd == ksd else 0.0)  # nan->0 guard
    acc["_ok_fraction"] = ok / n_surr
    return acc


def build_s5_ensemble(seq, n_surr, seed, kmax=6):
    """S5 surrogate = standard multiset permutation. Returns per-k lists."""
    rng = random.Random(seed)
    base = list(seq)
    per_k = {k: [] for k in range(1, kmax + 1)}
    for _ in range(n_surr):
        rng.shuffle(base)
        arr = np.asarray(base)
        for k in range(1, kmax + 1):
            per_k[k].append(float(np.mean(arr[k:] == arr[:-k])))
    return per_k


def summarize(vals):
    """mean, sd, p99, p99.9 of a list; sd via population stdev."""
    a = np.asarray(vals, dtype=np.float64)
    m = float(a.mean())
    sd = float(a.std())                              # population sd
    p99 = float(np.percentile(a, 99))
    p999 = float(np.percentile(a, 99.9))
    return {"mean": m, "sd": sd, "p99": p99, "p999": p999}


# =====================================================================
# ANCHOR 1 — synthetic Playfair-class positive control
# =====================================================================

def build_playfair_class_cipher(length, rng):
    """Encipher GP-mapped English as NON-overlapping digraphs through a
    Playfair-class rule over the 29-rune alphabet.

    CONSTRUCTION (documented, pre-registered):
      * Build a keyed 29-length permutation KEY of the alphabet (seeded shuffle);
        this is the linear 'Playfair line' (a 1xN arrangement).
      * For a plaintext pair (a,b) with a != b: let ia,ib be their positions on
        the KEY line. Output the runes one step to the RIGHT (cyclically):
            out_a = KEY[(ia+1) % N], out_b = KEY[(ib+1) % N].
        This is the linear analogue of Playfair's same-row rule and, like
        Playfair, it is a bijection on unordered distinct pairs and NEVER emits
        equal output symbols from distinct inputs (KEY is a permutation, so
        (ia+1) != (ib+1) whenever ia != ib).
      * Playfair forbids equal-symbol PAIRS in the plaintext: whenever a == b we
        split by inserting the classic filler 'X' (GP index for X = 14) between
        them, exactly as canonical Playfair does. Thus no within-pair doublet can
        ever be enciphered -> within-pair (even->odd) doublet rate is HARD ZERO.
      * Across-boundary (odd->even) doublets can still occur by chance between
        adjacent independent digraphs, so Delta_parity is driven strongly
        negative (within << across) -> the parity discriminator must fire.
    Returns a length-`length` index list."""
    base = english_baseline()                        # GP indices of English
    # tile plaintext to a generous length (filler insertion will consume some)
    pt = [base[i % len(base)] for i in range(length * 2)]

    KEY = list(range(N))
    rng.shuffle(KEY)
    posOf = {r: i for i, r in enumerate(KEY)}
    XFIL = gp.keyword_to_indices("X")[0]             # canonical Playfair filler

    # form non-overlapping digraphs with Playfair doublet-splitting
    out = []
    i = 0
    while len(out) < length and i < len(pt):
        a = pt[i]
        b = pt[i + 1] if i + 1 < len(pt) else (XFIL if a != XFIL else gp.keyword_to_indices("Q")[0])
        if a == b:                                   # forbidden equal pair -> insert filler
            b = XFIL if a != XFIL else gp.keyword_to_indices("A")[0]
            i += 1                                   # consume only 'a'; next round re-reads
        else:
            i += 2
        ia, ib = posOf[a], posOf[b]
        out.append(KEY[(ia + 1) % N])
        out.append(KEY[(ib + 1) % N])
    return out[:length]


# =====================================================================
# MAIN
# =====================================================================

def pct_rank(value, dist):
    """Fraction of surrogate dist strictly below `value` (one-sided high)."""
    a = np.asarray(dist)
    return float(np.mean(a < value))


def main():
    pages = load_pages()
    unsolved = [i for p in pages[:-2] for i in p]                 # 12,956 runes
    D_obs = stats.doublet_count(unsolved)
    Fcount = sum(1 for i in unsolved if i == 0)

    # solved negative-control pages
    w = corpus.page_by_label("03.jpg")                            # WELCOME
    e = corpus.page_by_label("73.jpg")                            # AN END
    welcome = gp.runes_to_indices(w["runes"]) if w else []
    an_end = gp.runes_to_indices(e["runes"]) if e else []

    R = []
    R.append("=" * 74)
    R.append("R5-COMBINED  Residual-doublet structural anatomy + polygraphic parity")
    R.append(f"seed={SEED}  N={N}  surrogates(main S1-S4)={N_SURR}")
    R.append(f"unsolved runes={len(unsolved)}  F(ᚠ) count={Fcount}  "
             f"residual doublets D={D_obs}")
    R.append(f"neg-control: WELCOME n={len(welcome)} (dbl={stats.doublet_count(welcome)})"
             f"  AN END n={len(an_end)} (dbl={stats.doublet_count(an_end)})")
    R.append("=" * 74)

    # count-preserving mixing swaps per surrogate. The S1-S4 nulls are saturated
    # (mean/sd stable) by ~L swaps; verified across mix in [L/2, 4L] the null
    # mean/sd are unchanged, so L keeps the 10k run tractable without altering
    # any statistic's surrogate band.
    MIX = len(unsolved)

    # ---- ANCHOR 1: Playfair-class positive control ----------------------
    rng = random.Random(SEED)
    synth = build_playfair_class_cipher(len(unsolved), rng)
    syn_par = s1_parity(synth)
    syn_D = stats.doublet_count(synth)
    # within-pair doublet rate under BOTH phases; Playfair construction lays
    # pairs at origin 0, so phase-0 within-pair rate is the diagnostic hard-zero.
    syn_within0 = syn_par[0]["within_rate"]
    syn_delta0 = syn_par[0]["delta"]
    # surrogate band for THIS synthetic (its own multiset + doublet count)
    syn_ens = build_main_ensemble(synth, syn_D, 1000, SEED + 1, MIX)
    syn_delta0_null = summarize(syn_ens["s1_p0_delta"])
    # 99.9th percentile is the high tail; Delta is negative here, so compare to
    # the 0.1th percentile (low tail) for a "beyond 99.9th pct in magnitude" test.
    syn_delta0_lo = float(np.percentile(syn_ens["s1_p0_delta"], 0.1))
    a1_delta_ok = syn_delta0 < syn_delta0_lo
    a1_within_ok = syn_within0 <= 1e-9              # hard zero
    a1_pass = a1_delta_ok and a1_within_ok

    R.append("\n[ANCHOR 1] SYNTHETIC POSITIVE — Playfair-class over 29 runes")
    R.append(f"  synth doublets D={syn_D}  (within-pair phase0 doublets="
             f"{syn_par[0]['d_within']})")
    R.append(f"  within-pair (even->odd) rate phase0 = {syn_within0:.6f}  "
             f"(hard-zero expected)")
    R.append(f"  Delta_parity phase0 = {syn_delta0:+.6f}   "
             f"surrogate mean={syn_delta0_null['mean']:+.6f} sd={syn_delta0_null['sd']:.6f} "
             f"0.1pct={syn_delta0_lo:+.6f}")
    R.append(f"  (a) Delta beyond surrogate extreme tail: {a1_delta_ok}")
    R.append(f"  (b) within-pair doublet rate hard-zero : {a1_within_ok}")
    R.append(f"  ANCHOR 1 => {'PASS' if a1_pass else 'FAIL'}")
    if not a1_pass:
        R.append("  *** HARNESS INSENSITIVE — positive control did not surface the "
                 "polygraphic signature. STOP; not decision-grade. ***")

    # ---- ANCHOR 2: real solved-page negative controls -------------------
    R.append("\n[ANCHOR 2] NEGATIVE CONTROL — real solved pages WELCOME & AN END")
    a2_flags = []
    for nm, seq in (("WELCOME", welcome), ("AN END", an_end)):
        Dn = stats.doublet_count(seq)
        par = s1_parity(seq)
        _, _, chi2, df, top, topc, tope = s3_identity(seq)
        r5 = s5_lag_spectrum(seq)
        # surrogate bands for THIS page (multiset+doublet count fixed); shorter
        # pages -> fewer surr are fine for a control.
        ens = build_main_ensemble(seq, Dn, 800, SEED + 7, 4 * len(seq))
        d0 = summarize(ens["s1_p0_delta"]); d1 = summarize(ens["s1_p1_delta"])
        c3 = summarize(ens["s3_chi2"])
        s5null = build_s5_ensemble(seq, 800, SEED + 9)
        # thresholds: parity split super-threshold? identity chi2 super-threshold?
        par_split = (par[0]["delta"] > d0["p999"] or par[0]["delta"] < np.percentile(ens["s1_p0_delta"], 0.1)
                     or par[1]["delta"] > d1["p999"] or par[1]["delta"] < np.percentile(ens["s1_p1_delta"], 0.1))
        chi2_super = chi2 > c3["p999"] if c3["sd"] > 0 else False
        # anomalous lag-k peak: any k with r_k beyond its multiset-shuffle 99.9th
        lag_anom = any(r5[k - 1] > np.percentile(s5null[k], 99.9) for k in range(1, 7))
        clean = (not par_split) and (not chi2_super) and (not lag_anom)
        a2_flags.append(clean)
        R.append(f"  {nm}: D={Dn}  parity-split super-thr={par_split}  "
                 f"identity-chi2 super-thr={chi2_super}  lag-anom={lag_anom}  "
                 f"=> {'clean' if clean else 'ANOMALOUS'}")
    a2_pass = all(a2_flags)
    R.append(f"  ANCHOR 2 => {'PASS' if a2_pass else 'FAIL'}")

    if not (a1_pass and a2_pass):
        R.append("\n*** ANCHORS FAILED — harness not decision-grade. STOPPING before "
                 "the real-corpus verdict. ***")
        out = "\n".join(R)
        print(out)
        return out

    # ---- REAL corpus: build the ONE main ensemble -----------------------
    R.append(f"\n[REAL LP2 UNSOLVED] building {N_SURR} fixed-multiset "
             f"fixed-doublet-count (D={D_obs}) surrogates (seed {SEED+3}) ...")
    ens = build_main_ensemble(unsolved, D_obs, N_SURR, SEED + 3, MIX)
    R.append(f"  surrogates realizing EXACT D={D_obs}: "
             f"{ens['_ok_fraction']*100:.2f}%  "
             f"(realized D mean={np.mean(ens['realizedD']):.2f})")

    # S5 uses its own multiset-shuffle ensemble
    s5null = build_s5_ensemble(unsolved, N_SURR, SEED + 5)

    # ---- observed values ------------------------------------------------
    par = s1_parity(unsolved)
    di_obs, mo_obs = s2_digraph_ioc(unsolved)
    obs3, exp3, chi2_obs, df3, top3, topc3, tope3 = s3_identity(unsolved)
    ks_d, ks_p, ngap, meangap = s4_gap_ks(unsolved)
    r5_obs = s5_lag_spectrum(unsolved)

    verdicts = []   # (name, confirm_bool, degenerate_bool)

    # ---- S1 report ------------------------------------------------------
    R.append("\n[S1 PARITY SPLIT]  Delta = within(even->odd) - across(odd->even)")
    for p in (0, 1):
        pr = par[p]
        nd = summarize(ens[f"s1_p{p}_delta"])
        lo = float(np.percentile(ens[f"s1_p{p}_delta"], 0.1))
        deg = nd["sd"] == 0.0
        # two-sided directional test at family 99.9th: high tail OR low tail
        conf = (not deg) and (pr["delta"] > nd["p999"] or pr["delta"] < lo)
        verdicts.append((f"S1 phase{p} Delta", conf, deg))
        R.append(f"  phase{p}: within_rate={pr['within_rate']:.5f} "
                 f"(d={pr['d_within']}/{pr['n_within']})  "
                 f"across_rate={pr['across_rate']:.5f} "
                 f"(d={pr['d_across']}/{pr['n_across']})")
        R.append(f"           Delta={pr['delta']:+.6f}  surr mean={nd['mean']:+.6f} "
                 f"sd={nd['sd']:.6f} p99.9={nd['p999']:+.6f} p0.1={lo:+.6f}  "
                 f"degenerate={deg}  CONFIRM={conf}")

    # ---- S2 report ------------------------------------------------------
    nd2 = summarize(ens["s2_digraph"])
    nd2m = summarize(ens["s2_mono"])
    deg2 = nd2["sd"] == 0.0
    conf2 = (not deg2) and (di_obs > nd2["p999"])
    verdicts.append(("S2 digraph IoC", conf2, deg2))
    R.append("\n[S2 DIGRAPH vs MONOGRAPH IoC]")
    R.append(f"  digraph IoC*N^2-space = {di_obs:.5f}  surr mean={nd2['mean']:.5f} "
             f"sd={nd2['sd']:.5f} p99.9={nd2['p999']:.5f}  degenerate={deg2}")
    R.append(f"  monograph IoC*N       = {mo_obs:.5f}  surr mean={nd2m['mean']:.5f} "
             f"sd={nd2m['sd']:.5f} (monograph is multiset-fixed)")
    R.append(f"  CONFIRM (digraph>surr p99.9) = {conf2}")

    # ---- S3 report ------------------------------------------------------
    nd3 = summarize(ens["s3_chi2"])
    nd3t = summarize(ens["s3_topcount"])
    deg3 = nd3["sd"] == 0.0
    chi2_p = chi2_sf(chi2_obs, df3)
    conf3 = (not deg3) and (chi2_obs > nd3["p999"])
    verdicts.append(("S3 identity chi2", conf3, deg3))
    R.append("\n[S3 IDENTITY MULTISET chi2]  doubled-rune value distribution")
    R.append(f"  observed chi2={chi2_obs:.3f} (df={df3}, analytic p={chi2_p:.3g})  "
             f"surr mean={nd3['mean']:.3f} sd={nd3['sd']:.3f} p99.9={nd3['p999']:.3f}  "
             f"degenerate={deg3}")
    R.append(f"  dominant doubled rune = idx {top3} '{gp.IDX_TO_TRANS[top3]}' "
             f"count={topc3} (unigram-expected={tope3:.2f}; surr top-count "
             f"mean={nd3t['mean']:.2f} p99.9={nd3t['p999']:.2f})")
    R.append(f"  CONFIRM (chi2>surr p99.9) = {conf3}")

    # ---- S4 report ------------------------------------------------------
    nd4 = summarize(ens["s4_ks"])
    deg4 = nd4["sd"] == 0.0
    conf4 = (not deg4) and (ks_d > nd4["p999"])
    verdicts.append(("S4 gap KS", conf4, deg4))
    R.append("\n[S4 GAP DISTRIBUTION]  KS of inter-doublet gaps vs geometric null")
    R.append(f"  n_gaps={ngap}  mean_gap={meangap:.3f}  KS_stat={ks_d:.5f}  "
             f"analytic KS_p={ks_p:.3g}")
    R.append(f"  surr KS mean={nd4['mean']:.5f} sd={nd4['sd']:.5f} "
             f"p99.9={nd4['p999']:.5f}  degenerate={deg4}")
    R.append(f"  CONFIRM (KS>surr p99.9) = {conf4}")

    # ---- S5 report ------------------------------------------------------
    R.append("\n[S5 LAG-k SPECTRUM]  r_k = P(c[i]==c[i-k]); surrogate=multiset shuffle")
    for k in range(1, 7):
        band = summarize(s5null[k])
        deg = band["sd"] == 0.0
        conf = (not deg) and (r5_obs[k - 1] > band["p999"])
        # note: r_1 IS the doublet rate, fixed by construction in the main
        # ensemble but here S5 null is the multiset shuffle (per spec) so r_1's
        # observed deficit is a LOW-tail effect; the spec's S5 CONFIRM is a HIGH
        # peak vs the shuffle band, so a deficit does not confirm a lag peak.
        verdicts.append((f"S5 lag-{k}", conf, deg))
        R.append(f"  k={k}: r_k={r5_obs[k-1]:.6f}  surr mean={band['mean']:.6f} "
                 f"sd={band['sd']:.6f} p99.9={band['p999']:.6f}  degenerate={deg}  "
                 f"CONFIRM(peak)={conf}")

    # ---- DEGENERACY + VERDICT ------------------------------------------
    R.append("\n[DEGENERACY GUARD]")
    for nm, conf, deg in verdicts:
        if deg:
            R.append(f"  {nm}: surrogate sd==0 -> DEGENERATE, EXCLUDED from CONFIRM")
    nondeg = [(nm, conf) for nm, conf, deg in verdicts if not deg]
    any_confirm = any(c for _, c in nondeg)

    # S1 special polygraphic-hypothesis rule
    s1_conf_any = any(c for nm, c, d in verdicts if nm.startswith("S1") and not d)
    within0 = par[0]["within_rate"]; within1 = par[1]["within_rate"]
    hardzero = min(within0, within1) <= (1.0 / N) * 0.25   # consistent with ~0
    polygraphic_confirm = s1_conf_any and hardzero

    R.append("\n[PER-STATISTIC VERDICT] (family = all non-degenerate sub-stats; "
             "CONFIRM iff clears surrogate 99.9th pct)")
    for nm, conf, deg in verdicts:
        tag = "DEGENERATE(excluded)" if deg else ("CONFIRM" if conf else "REFUTE")
        R.append(f"  {nm:16s}: {tag}")

    R.append("\n[POLYGRAPHIC (Playfair-class) HYPOTHESIS]")
    R.append(f"  some S1 phase Delta clears extreme tail: {s1_conf_any}")
    R.append(f"  min within-pair rate={min(within0,within1):.5f} consistent with "
             f"hard-zero+noise (<= (1/29)/4={ (1.0/N)*0.25:.5f}): {hardzero}")
    R.append(f"  => polygraphic CONFIRM = {polygraphic_confirm}")

    R.append("\n[OVERALL VERDICT]")
    R.append(f"  any non-degenerate statistic clears surrogate 99.9th pct: {any_confirm}")
    overall = "CONFIRM" if any_confirm else "REFUTE"
    R.append(f"  ==> OVERALL {overall} directional structure in the residual doublets")

    out = "\n".join(R)
    print(out)
    return out


if __name__ == "__main__":
    main()
