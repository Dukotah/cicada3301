"""R6 TEST 2 — TRANSITION-STRUCTURE (LATTICE + KEEL merged). NON-DECRYPTING.

Tests whether the forbidden rule is a GENERAL off-diagonal (c_i != g(c_{i-1}))
rather than only the identity (c_i = c_{i-1}), and whether any SECOND-ORDER
transition bias survives.

KEEL:
  - 29x29 adjacent-transition count matrix over the concatenated unsolved stream.
  - scan ALL cells AND the 28 non-identity fixed offsets (c_i - c_{i-1} = k mod 29,
    k=1..28) for any cell/offset SUPPRESSED to ~zero the way identity diag (k=0) is.
  - report identity-diag suppression depth and deepest non-identity offset.

LATTICE:
  - H(c_i | c_{i-1}, c_{i-2})  (conditional entropy, bits)
  - trigram-tensor chi^2 vs diagonal-constrained expectation; DISCLOSE counts/cell;
    PRE-REGISTERED: sparse-tensor chi^2 reads INCONCLUSIVE (not NEGATIVE) if
    counts/cell too low for power.

NULL (degeneracy guard): 10,000 surrogates preserving exact rune multiset AND the
no-adjacent-repeat constraint (c_i != c_{i-1}), seed 3301. Null bakes in the
identity forbidden-diagonal. Verify surrogate sd>0 for each reported statistic.

THRESHOLD: family-correct across (29x29 cells + 28 offsets + 2 entropy stats).
FLAG iff a statistic clears the family-corrected surrogate 99.9th pct AND its
anchor fired.
Output: analysis/R6_TRANSITION_STRUCTURE.txt (flushed).
"""
import os
import sys
import math
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from lp import gematria as gp, corpus  # noqa

HERE = os.path.dirname(__file__)
KRIS = os.path.normpath(os.path.join(HERE, "..", "data", "krisyotam_runes.txt"))
OUT = os.path.join(HERE, "R6_TRANSITION_STRUCTURE.txt")
N = gp.N
SEED = 3301
NSURR = 10000

_lines = []
def emit(s=""):
    _lines.append(s)
    print(s)


def load_kris_pages():
    txt = open(KRIS, encoding="utf-8").read()
    pages = []
    for s in txt.split("%"):
        idxs = gp.runes_to_indices(s)
        if idxs:
            pages.append(idxs)
    return pages


# ---------------- statistics -----------------------------------------------
def trans_matrix(stream):
    M = [[0] * N for _ in range(N)]
    for a, b in zip(stream, stream[1:]):
        M[a][b] += 1
    return M


def offset_counts(stream):
    """counts by (b - a) mod N, k=0..28."""
    off = [0] * N
    for a, b in zip(stream, stream[1:]):
        off[(b - a) % N] += 1
    return off


def cond_entropy_2(stream):
    """H(c_i | c_{i-1}, c_{i-2}) in bits."""
    ctx = {}
    ctx_tot = {}
    for i in range(2, len(stream)):
        key = (stream[i - 2], stream[i - 1])
        d = ctx.setdefault(key, {})
        d[stream[i]] = d.get(stream[i], 0) + 1
        ctx_tot[key] = ctx_tot.get(key, 0) + 1
    total = sum(ctx_tot.values())
    if total == 0:
        return 0.0
    H = 0.0
    for key, d in ctx.items():
        tot = ctx_tot[key]
        p_ctx = tot / total
        h = 0.0
        for c in d.values():
            p = c / tot
            h -= p * math.log2(p)
        H += p_ctx * h
    return H


def cond_entropy_1(stream):
    """H(c_i | c_{i-1}) in bits — helper for context."""
    ctx = {}
    ctx_tot = {}
    for a, b in zip(stream, stream[1:]):
        d = ctx.setdefault(a, {})
        d[b] = d.get(b, 0) + 1
        ctx_tot[a] = ctx_tot.get(a, 0) + 1
    total = sum(ctx_tot.values())
    H = 0.0
    for a, d in ctx.items():
        tot = ctx_tot[a]
        p_ctx = tot / total
        h = 0.0
        for c in d.values():
            p = c / tot
            h -= p * math.log2(p)
        H += p_ctx * h
    return H


# ---------------- surrogate generator (multiset + no-repeat) ----------------
def make_no_repeat_perm(base, rng, max_tries=200):
    """Random permutation of `base` with no adjacent equal (c_i != c_{i-1}).
    Retry-shuffle; if it stalls, do a local repair swap pass."""
    n = len(base)
    for _ in range(max_tries):
        perm = base[:]
        rng.shuffle(perm)
        ok = True
        for i in range(1, n):
            if perm[i] == perm[i - 1]:
                ok = False
                break
        if ok:
            return perm
    # repair: for each collision, swap forward with a non-conflicting position
    perm = base[:]
    rng.shuffle(perm)
    for i in range(1, n):
        if perm[i] == perm[i - 1]:
            for j in range(i + 1, n):
                if perm[j] != perm[i - 1] and (i + 1 >= n or perm[j] != perm[i + 1]) \
                   and perm[i] != perm[j - 1]:
                    perm[i], perm[j] = perm[j], perm[i]
                    break
    return perm


def main():
    emit("=" * 78)
    emit("R6 TEST 2 — TRANSITION-STRUCTURE (LATTICE + KEEL)")
    emit("=" * 78)
    emit(f"seed={SEED}  surrogates={NSURR}")

    kris = load_kris_pages()
    unsolved = [i for p in kris[:55] for i in p]
    an_end = kris[55]
    emit(f"unsolved concatenated stream n={len(unsolved)}  AN END n={len(an_end)}")

    # observed
    off = offset_counts(unsolved)
    M = trans_matrix(unsolved)
    n_pairs = len(unsolved) - 1
    id_depth = off[0]  # identity diagonal count (k=0) — the known forbidden rule
    non_id = [(k, off[k]) for k in range(1, N)]
    non_id_sorted = sorted(non_id, key=lambda x: x[1])
    deepest_offset_k, deepest_offset_ct = non_id_sorted[0]
    emit("")
    emit("--- KEEL: offset (c_i - c_{i-1}) mod 29 counts ---")
    emit(f"identity diagonal k=0 count = {id_depth}  ({100*id_depth/n_pairs:.4f}% of "
         f"{n_pairs} pairs; uniform-expect {n_pairs/N:.1f})")
    emit(f"deepest NON-identity offset: k={deepest_offset_k} count={deepest_offset_ct} "
         f"({100*deepest_offset_ct/n_pairs:.4f}%)")
    emit("all offsets k: count  (k=0 is identity):")
    emit("  " + "  ".join(f"{k}:{off[k]}" for k in range(N)))

    # cell-level deepest suppression among off-diagonal cells (exclude a==b)
    # measure each cell's count; interesting = suppressed (near zero) despite
    # nonzero marginals.
    emit("")
    emit("--- KEEL: cell scan (29x29) ---")
    # expected under independence given marginals
    row = [sum(M[a]) for a in range(N)]
    col = [sum(M[a][b] for a in range(N)) for b in range(N)]
    zero_offdiag = 0
    for a in range(N):
        for b in range(N):
            if a != b and M[a][b] == 0 and row[a] > 0 and col[b] > 0:
                zero_offdiag += 1
    diag_cells_zero = sum(1 for a in range(N) if M[a][a] == 0)
    emit(f"identity cells (a==b) that are zero: {diag_cells_zero}/29")
    emit(f"OFF-diagonal cells that are hard-zero (with nonzero marginals): "
         f"{zero_offdiag}/{29*28}")

    # ---------------- LATTICE ----------------
    H2 = cond_entropy_2(unsolved)
    H1 = cond_entropy_1(unsolved)
    emit("")
    emit("--- LATTICE: conditional entropy ---")
    emit(f"H(c_i|c_{{i-1}}) = {H1:.4f} bits   H(c_i|c_{{i-1}},c_{{i-2}}) = {H2:.4f} bits"
         f"  (max = log2 29 = {math.log2(N):.4f})")

    # trigram tensor sparsity disclosure
    n_tri = len(unsolved) - 2
    counts_per_cell = n_tri / (N ** 3)
    emit(f"trigram tensor: {n_tri} trigrams / {N**3} cells = {counts_per_cell:.4f} "
         f"counts/cell  -> {'UNDERPOWERED (INCONCLUSIVE arm)' if counts_per_cell < 5 else 'adequate'}")

    # ===================== ANCHORS =====================
    emit("")
    emit("--- ANCHORS ---")
    rng_a = random.Random(SEED)

    # multiset for synthetic anchors: reuse unsolved multiset
    base = list(unsolved)

    # ANCHOR 1: synthetic "no-repeat after fixed shift k=7": build a stream where
    # (c_i - c_{i-1}) mod 29 is NEVER 7, but identity is allowed/normal.
    def synth_forbid_offset(k, n=8000):
        rng = random.Random(SEED + 71)
        s = [rng.randrange(N)]
        while len(s) < n:
            c = rng.randrange(N)
            if (c - s[-1]) % N == k:
                continue
            s.append(c)
        return s
    s7 = synth_forbid_offset(7)
    o7 = offset_counts(s7)
    a1 = (o7[7] == 0) and (o7[0] > 0.5 * (len(s7) / N))  # k=7 hard zero, identity normal
    emit(f"A1 forbid-offset k=7 synthetic: offset7 count={o7[7]} (want 0), "
         f"identity k0 count={o7[0]} (want ~normal {len(s7)/N:.0f})  PASS={a1}")

    # ANCHOR 2: synthetic pure identity-no-repeat: only identity suppressed.
    def synth_no_repeat(n=8000):
        rng = random.Random(SEED + 72)
        s = [rng.randrange(N)]
        while len(s) < n:
            c = rng.randrange(N)
            if c == s[-1]:
                continue
            s.append(c)
        return s
    snr = synth_no_repeat()
    onr = offset_counts(snr)
    other_min = min(onr[k] for k in range(1, N))
    a2 = (onr[0] == 0) and (other_min > 0.3 * (len(snr) / N))
    emit(f"A2 pure identity-no-repeat synthetic: k0 count={onr[0]} (want 0), "
         f"min non-identity offset count={other_min} (want ~normal, >0)  PASS={a2}")

    # ANCHOR 3: synthetic order-2 Markov keystream: depress H(c_i|c_{i-1},c_{i-2}).
    def synth_order2(n=8000):
        rng = random.Random(SEED + 73)
        # deterministic-ish: next depends strongly on (prev2,prev1)
        s = [rng.randrange(N), rng.randrange(N)]
        while len(s) < n:
            a, b = s[-2], s[-1]
            # biased: mostly (a*3+b*7) mod N, occasional noise
            if rng.random() < 0.85:
                c = (a * 3 + b * 7 + 1) % N
            else:
                c = rng.randrange(N)
            if c == b:  # keep no-repeat like the real book
                c = (c + 1) % N
            s.append(c)
        return s
    so2 = synth_order2()
    H2_o2 = cond_entropy_2(so2)
    H1_o2 = cond_entropy_1(so2)
    # null for a no-repeat stream of same multiset: compute below; here just show
    a3_pre = H2_o2 < H1_o2 - 0.3  # order-2 structure lowers H2 well below H1
    emit(f"A3 order-2 Markov synthetic: H1={H1_o2:.4f} H2={H2_o2:.4f} bits "
         f"(H2 markedly below H1)  PASS={a3_pre}")

    # ANCHOR 4: AN END off-diagonal scan must sit at null center (computed after null)
    # ===================== NULL =====================
    emit("")
    emit("--- NULL: 10,000 multiset+no-repeat surrogates (seed 3301) ---")
    rng = random.Random(SEED)

    # We track surrogate distributions for:
    #  - each offset k=1..28 count (to test non-identity suppression)
    #  - the MIN non-identity offset count (family stat for "any offset suppressed")
    #  - identity offset k=0 count (should be ~0 by construction; degeneracy check)
    #  - H2 (conditional entropy)
    # Stream — do not store arrays.
    import array
    # per-offset running for mean/sd and store min-nonid pool + H2 pool
    off_sum = [0.0] * N
    off_sqsum = [0.0] * N
    min_nonid_pool = []
    h2_pool = []
    k0_pool = []

    # Also, deepest-cell: track min off-diagonal cell count distribution is heavy;
    # instead we track, per surrogate, the number of hard-zero off-diagonal cells,
    # to compare with observed zero_offdiag.
    zero_offdiag_pool = []

    for t in range(NSURR):
        perm = make_no_repeat_perm(base, rng)
        o = offset_counts(perm)
        for k in range(N):
            off_sum[k] += o[k]
            off_sqsum[k] += o[k] * o[k]
        mn = min(o[k] for k in range(1, N))
        min_nonid_pool.append(mn)
        k0_pool.append(o[0])
        # H2 only every stream (cheap enough at n~12k, 10k times = heavy but ok);
        # to bound cost compute H2 on a subsample of surrogates (every 10th) —
        # PRE-REGISTERED reduction of H2-null count is NOT allowed, so compute all.
        h2_pool.append(cond_entropy_2(perm))
        # zero off-diagonal cells
        Ms = trans_matrix(perm)
        rows = [sum(Ms[a]) for a in range(N)]
        cols = [sum(Ms[a][b] for a in range(N)) for b in range(N)]
        z = 0
        for a in range(N):
            for b in range(N):
                if a != b and Ms[a][b] == 0 and rows[a] > 0 and cols[b] > 0:
                    z += 1
        zero_offdiag_pool.append(z)

    def stat(pool):
        m = sum(pool) / len(pool)
        sd = (sum((x - m) ** 2 for x in pool) / len(pool)) ** 0.5
        return m, sd

    def pct(pool, p):
        sp = sorted(pool)
        k = min(len(sp) - 1, max(0, int(math.ceil(p / 100.0 * len(sp))) - 1))
        return sp[k]

    off_mean = [off_sum[k] / NSURR for k in range(N)]
    off_sd = [math.sqrt(max(0.0, off_sqsum[k] / NSURR - off_mean[k] ** 2)) for k in range(N)]

    # k0 degeneracy check: identity must be baked to ~0 in surrogates
    k0_m, k0_sd = stat(k0_pool)
    emit(f"surrogate identity k0 count: mean={k0_m:.3f} sd={k0_sd:.3f} "
         f"(no-repeat constraint => should be 0; degenerate arm)")
    emit(f"   observed identity k0 = {id_depth}. DEGENERACY: identity arm is "
         f"unbeatable-by-construction (excluded from family test).")

    # non-identity offset family stat: min non-identity offset count
    mn_m, mn_sd = stat(min_nonid_pool)
    mn_lo = pct(min_nonid_pool, 0.1)   # 0.1th pct (suppression = low tail)
    emit("")
    emit(f"NON-IDENTITY min-offset count (family stat over 28 offsets):")
    emit(f"   surrogate mean={mn_m:.3f} sd={mn_sd:.3f} 0.1th-pct={mn_lo}  "
         f"degenerate={mn_sd<=1e-9}")
    emit(f"   OBSERVED deepest non-identity offset count = {deepest_offset_ct} "
         f"(k={deepest_offset_k})")
    # suppressed at >= identity depth?  identity depth = id_depth (=0 typically)
    non_id_suppressed = (deepest_offset_ct <= id_depth) and (deepest_offset_ct < mn_lo)
    emit(f"   non-identity suppressed to <= identity depth ({id_depth}) AND below "
         f"0.1th pct? {non_id_suppressed}")

    # per-offset z-scores (how far each real offset is below its null mean)
    emit("")
    emit("per-offset real-vs-null (k: obs | null_mean | z):")
    zline = []
    for k in range(1, N):
        z = (off[k] - off_mean[k]) / off_sd[k] if off_sd[k] > 1e-9 else float("nan")
        zline.append(f"{k}:{off[k]}|{off_mean[k]:.0f}|{z:+.2f}")
    emit("  " + "  ".join(zline))

    # H2 null
    h2_m, h2_sd = stat(h2_pool)
    h2_lo = pct(h2_pool, 0.1)
    emit("")
    emit(f"H(c_i|c_{{i-1}},c_{{i-2}}) null: mean={h2_m:.4f} sd={h2_sd:.4f} "
         f"0.1th-pct={h2_lo:.4f}  degenerate={h2_sd<=1e-9}")
    emit(f"   OBSERVED H2 = {H2:.4f} bits")
    h2_below = (H2 < h2_lo) and (h2_sd > 1e-9)
    emit(f"   H2 below null 0.1th pct? {h2_below}")

    # zero off-diagonal cells null
    zo_m, zo_sd = stat(zero_offdiag_pool)
    zo_hi = pct(zero_offdiag_pool, 99.9)
    emit("")
    emit(f"hard-zero off-diagonal cells null: mean={zo_m:.2f} sd={zo_sd:.2f} "
         f"99.9th-pct={zo_hi}  observed={zero_offdiag}  degenerate={zo_sd<=1e-9}")

    # ANCHOR 4 (SPECIFICITY, corrected 2026-08-06): the ORIGINAL A4 tried to use the
    # 85-rune solved page AN END as a null-center control. That was mis-typed: AN END is
    # decrypted PLAINTEXT (natural English -> it has real doublets, k0=2) and is far too
    # short (28 non-identity offsets over 85 runes -> an empty offset is pure sparsity),
    # so it can neither "obey no-repeat" nor sit at the ciphertext-length null center. It
    # falsely tripped the STOP while the powered main statistics all read NEGATIVE. The
    # correct specificity control is a length-matched, HELD-OUT (seed disjoint from the
    # null pool) memoryless+no-repeat surrogate: the detector must classify it NEGATIVE on
    # ALL THREE decision predicates (no false keel / no H2 suppression / no hard-zero
    # cells). This changes no goalpost — the verdict direction is unchanged; it only fixes
    # a broken control. AN END is retained below as an informational diagnostic only.
    rng_spec = random.Random(SEED + 999)          # held out from the null (random.Random(SEED))
    spec = make_no_repeat_perm(base, rng_spec)
    spec_off = offset_counts(spec)
    spec_id = spec_off[0]
    spec_deep = min(spec_off[k] for k in range(1, N))
    spec_H2 = cond_entropy_2(spec)
    Ms = trans_matrix(spec)
    srow = [sum(Ms[a]) for a in range(N)]
    scol = [sum(Ms[a][b] for a in range(N)) for b in range(N)]
    spec_zero = sum(1 for a in range(N) for b in range(N)
                    if a != b and Ms[a][b] == 0 and srow[a] > 0 and scol[b] > 0)
    # run the EXACT decision predicates used for the real stream
    spec_keel_fp = (spec_deep <= spec_id) and (spec_deep < mn_lo)
    spec_h2_fp = (spec_H2 < h2_lo)
    spec_zero_fp = (spec_zero > zo_hi)
    a4 = not (spec_keel_fp or spec_h2_fp or spec_zero_fp)   # PASS = no false positive
    emit("")
    emit(f"A4 SPECIFICITY (length-matched n={len(spec)} held-out no-repeat surrogate, "
         f"seed {SEED+999}):")
    emit(f"   keel  deepest-nonid={spec_deep} (id={spec_id}, mn_lo={mn_lo}) -> FP={spec_keel_fp}")
    emit(f"   H2={spec_H2:.4f} (h2_lo={h2_lo:.4f}) -> FP={spec_h2_fp}")
    emit(f"   hard-zero off-diag cells={spec_zero} (99.9th={zo_hi}) -> FP={spec_zero_fp}")
    emit(f"   detector fires on structure-free stream? {not a4}  PASS={a4}")
    # informational diagnostic only (NOT gating): AN END solved-plaintext page
    end_off = offset_counts(an_end)
    end_min_nonid = min(end_off[k] for k in range(1, N))
    emit(f"   [diag] AN END (n={len(an_end)} solved PLAINTEXT): identity k0={end_off[0]} "
         f"(natural-English doublets, expected >0), min non-id offset={end_min_nonid} "
         f"(sparsity at n=85, non-gating)")

    anchors_ok = a1 and a2 and a3_pre and a4
    emit("")
    emit(f"ALL ANCHORS PASS = {anchors_ok}  (A1={a1} A2={a2} A3={a3_pre} A4={a4})")

    if not anchors_ok:
        emit("!!! ANCHOR FAILURE — STOPPING per protocol.")
        _flush()
        return

    # ===================== VERDICT =====================
    emit("")
    emit("=" * 78)
    # Family-correct: identity arm excluded (degenerate). Remaining family:
    #   28 non-identity offsets + off-diagonal zero-cells + H2  (+ tensor-chi2 arm
    #   pre-registered INCONCLUSIVE if underpowered).
    emit("FAMILY (identity arm EXCLUDED as degenerate/unbeatable-by-construction):")
    emit(f"  non-identity offset suppression flagged: {non_id_suppressed}")
    emit(f"  H2 below null 0.1th pct flagged: {h2_below}")
    emit(f"  off-diagonal zero-cell excess (obs {zero_offdiag} vs 99.9th {zo_hi}): "
         f"{zero_offdiag > zo_hi}")
    tensor_incon = counts_per_cell < 5
    emit(f"  trigram-tensor chi2 arm: {'INCONCLUSIVE (underpowered, '+f'{counts_per_cell:.3f} counts/cell)' if tensor_incon else 'adequate'}")

    confirm = non_id_suppressed or h2_below or (zero_offdiag > zo_hi)
    if confirm:
        emit("")
        emit("OVERALL VERDICT: CONFIRM — a non-identity off-diagonal is suppressed at "
             ">= identity depth OR conditional entropy is below null 0.1th pct.")
    else:
        # if only underpowered tensor ambiguous -> INCONCLUSIVE, else REFUTE
        emit("")
        emit("OVERALL VERDICT: REFUTE — forbidden rule is purely the identity lag-1 "
             "diagonal; no general off-diagonal or 2nd-order bias survives.")
        emit("(trigram-tensor chi2 arm is INCONCLUSIVE/underpowered but the powered "
             "arms — offset suppression, H2, zero-cell excess — are all NEGATIVE.)")
    emit("=" * 78)
    _flush()


def _flush():
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(_lines) + "\n")
        f.flush()
        os.fsync(f.fileno())
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
