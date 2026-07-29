#!/usr/bin/env python3
"""LATERAL-FIELD TRANSPLANT (bioinformatics / sequence alignment).

The project's kappa autocorrelation only sees EXACT repeats at rigid lags.
A filtered/gapped keystream that desyncs on repeat (skip-on-repeat) would leave
APPROXIMATE long repeats -- the same subsequence recurring with a handful of
substitutions or 1-2 indels, at variable offsets. That signature is invisible to
exact autocorrelation but is exactly what genomics maximal-repeat / local-
alignment tooling is built to find.

Method (BLAST-style seed-and-extend over a 29-letter alphabet):
  1. Index every exact w-mer seed (w=6) -> list of positions.
  2. For each seed shared by >=2 positions, take each pair (i,j), i<j, and run a
     banded Needleman-Wunsch-style gapless+gapped extension in BOTH directions to
     grow the seed into a maximal local alignment tolerating up to K mismatches
     and up to G indels, using an X-drop stopping rule.
  3. Record the maximal approximate repeat: (len, identity, #mismatch, #indel).
  4. Report all approximate repeats with alignment length >= LMIN and edit
     distance <= EDIT within that length.

Control: shuffle the stream 200x preserving the empirical symbol frequencies
(0-order) AND separately preserving the 1st-order (bigram) transition structure,
run the identical pipeline, and compare the count of significant approximate
repeats and the max repeat length. A real gapped-keystream signature beats BOTH
controls; matching the controls hardens the OTP verdict.

Bounded pure-Python. ~13k symbols; seeds are sparse in a near-random 29-ary
stream so the pair set is small.
"""
import sys, os, random, collections

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..",
                                "liber-primus", "src"))
from lp import gematria as gp

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..",
                                    "liber-primus"))

# ------------------------------------------------------------------ load stream
data = open(os.path.join(ROOT, "data/krisyotam_runes.txt"), encoding="utf-8").read()
segs = data.split("%")
S = []
for p in range(55):
    for ch in segs[p]:
        if ch in gp.RUNE_TO_IDX:
            S.append(gp.RUNE_TO_IDX[ch])
N = len(S)
print(f"[setup] pages 0-54 rune stream length = {N}")

# ------------------------------------------------------------------ parameters
W = 4         # exact seed length (w=4 has 127 collision classes; w>=7 has ZERO
              # exact repeats in the real stream, so long approx repeats can only
              # be grown from short seeds by tolerant extension)
K = 3         # max mismatches allowed in an extension
G = 2         # max indels (gaps) allowed
LMIN = 9      # min maximal alignment length to REPORT (> ~8 runes as tasked)
EDIT = 3      # max total edits (mismatch+indel) within the reported alignment
XDROP = 4     # x-drop: stop extending when score falls XDROP below best
MIN_SEP = W   # require the two occurrences to be non-trivially separated
GAP_PEN = 1   # cost of an indel (in the affine-free simple model)
MM_PEN = 1    # cost of a mismatch
MATCH = 1     # reward of a match (score units)


# --------------------------------------------------- banded gapped extension
def extend(seq, i, j, direction):
    """Extend an alignment starting just past the seed, from positions i,j.
    direction = +1 (rightward) or -1 (leftward).
    Returns (aln_len, matches, mismatches, indels) of the best-scoring extension
    using an X-drop banded DP over gap width <= G.
    We use a simple edit-distance-style DP restricted to band |di-dj|<=G.
    """
    # Collect the two subsequences we can consume in this direction.
    if direction == +1:
        a = seq[i:]           # from i forward
        b = seq[j:]
    else:
        a = seq[i::-1]        # from i backward (reversed)
        b = seq[j::-1]
    maxa = min(len(a), 200)   # cap extension length for boundedness
    maxb = min(len(b), 200)

    # Full banded DP over grid (x,y) = symbols consumed from a,b.
    # dp[(x,y)] = (score, mism, indel) of the best path reaching that cell.
    # Score = +MATCH per match, -MM_PEN per mismatch, -GAP_PEN per indel.
    # Band restricted to |x-y| <= G. Cells exceeding the edit budget are dropped.
    # The extension = the best-scoring reachable cell (x-drop pruned).
    dp = {(0, 0): (0, 0, 0)}
    best = (0, 0, 0, 0, 0)     # (score, x, y, mism, indel)
    best_score = 0
    for x in range(0, maxa + 1):
        row_best = None
        for y in range(max(0, x - G), min(maxb, x + G) + 1):
            if x == 0 and y == 0:
                continue
            cand = None
            # diagonal: match/mismatch (consume a[x-1], b[y-1])
            if x >= 1 and y >= 1 and (x - 1, y - 1) in dp:
                sc, mm, ind = dp[(x - 1, y - 1)]
                if a[x - 1] == b[y - 1]:
                    c = (sc + MATCH, mm, ind)
                else:
                    c = (sc - MM_PEN, mm + 1, ind)
                cand = c
            # up: gap in b (consume a[x-1])
            if x >= 1 and (x - 1, y) in dp and abs((x) - y) <= G:
                sc, mm, ind = dp[(x - 1, y)]
                c2 = (sc - GAP_PEN, mm, ind + 1)
                if cand is None or c2[0] > cand[0]:
                    cand = c2
            # left: gap in a (consume b[y-1])
            if y >= 1 and (x, y - 1) in dp and abs(x - (y)) <= G:
                sc, mm, ind = dp[(x, y - 1)]
                c3 = (sc - GAP_PEN, mm, ind + 1)
                if cand is None or c3[0] > cand[0]:
                    cand = c3
            if cand is None:
                continue
            if cand[1] > K or cand[2] > G:
                continue
            dp[(x, y)] = cand
            if row_best is None or cand[0] > row_best:
                row_best = cand[0]
            if cand[0] > best_score:
                best_score = cand[0]
                best = (cand[0], x, y, cand[1], cand[2])
        # x-drop: stop once no cell in this row is within XDROP of the global best
        if row_best is None or row_best < best_score - XDROP:
            break
    _, bx, by, bmm, bind = best
    L = max(bx, by)
    matches = max(bx, by) - bmm - bind   # matched columns in the alignment
    return L, matches, bmm, bind


def find_repeats(seq, w=W, report=True):
    """Seed-and-extend approximate maximal repeat finder."""
    n = len(seq)
    seed_pos = collections.defaultdict(list)
    for p in range(n - w + 1):
        seed_pos[tuple(seq[p:p + w])].append(p)
    hits = []
    seen_pairs = set()
    for kmer, positions in seed_pos.items():
        if len(positions) < 2:
            continue
        for a_i in range(len(positions)):
            for b_i in range(a_i + 1, len(positions)):
                i, j = positions[a_i], positions[b_i]
                if j - i < MIN_SEP:
                    continue
                # dedup: skip if this seed is inside an already-extended repeat
                key = (i, j)
                if key in seen_pairs:
                    continue
                # extend right from end-of-seed, left from start-of-seed
                rL, rM, rmm, rind = extend(seq, i + w, j + w, +1)
                lL, lM, lmm, lind = extend(seq, i - 1, j - 1, -1)
                total_len = w + rL + lL
                total_mm = rmm + lmm
                total_ind = rind + lind
                total_edit = total_mm + total_ind
                if total_len >= LMIN and total_edit <= EDIT:
                    # region signature to dedup overlapping seed hits
                    lo_i = i - lL
                    lo_j = j - lL
                    sig = (lo_i, lo_j, total_len)
                    if sig in seen_pairs:
                        continue
                    seen_pairs.add(sig)
                    hits.append({
                        "i": lo_i, "j": lo_j, "len": total_len,
                        "mism": total_mm, "indel": total_ind,
                        "edit": total_edit, "sep": lo_j - lo_i,
                    })
    # dedup nested hits (keep the longest per (start-pair region))
    hits.sort(key=lambda h: (-h["len"], h["edit"]))
    kept = []
    covered = []
    for h in hits:
        redundant = False
        for c in kept:
            # same pair region, shorter -> nested
            if (abs(h["i"] - c["i"]) <= 3 and abs(h["j"] - c["j"]) <= 3
                    and h["len"] <= c["len"]):
                redundant = True
                break
        if not redundant:
            kept.append(h)
    return kept


# ------------------------------------------------------------------ observed
print(f"[params] seed w={W}  max_mism K={K}  max_indel G={G}  "
      f"report L>={LMIN} edit<={EDIT}")
obs = find_repeats(S)
n_obs = len(obs)
max_len_obs = max((h["len"] for h in obs), default=0)
# count of "notable" repeats: len>=12 and >=1 edit (genuinely approximate, not
# just a long exact repeat which autocorrelation already sees)
approx_obs = [h for h in obs if h["edit"] >= 1 and h["len"] >= 12]
exact_obs = [h for h in obs if h["edit"] == 0]
print(f"\n[OBSERVED] total maximal repeats (len>={LMIN}): {n_obs}")
print(f"           of which EXACT (edit=0): {len(exact_obs)}")
print(f"           of which APPROX (edit>=1, len>=12): {len(approx_obs)}")
print(f"           max repeat length: {max_len_obs}")
if obs:
    print("\n[top 15 by length]")
    for h in sorted(obs, key=lambda x: -x["len"])[:15]:
        frag = gp.indices_to_translit(S[h["i"]:h["i"] + min(h["len"], 30)])
        print(f"  len={h['len']:3d} sep={h['sep']:5d} mism={h['mism']} "
              f"indel={h['indel']} @({h['i']},{h['j']})  {frag}")

# ------------------------------------------------------------------ controls
def shuffle0(seq, rng):
    """0-order: preserve symbol frequencies only (full permutation)."""
    s = seq[:]
    rng.shuffle(s)
    return s


def shuffle1(seq, rng):
    """1st-order: preserve bigram transition structure via Eulerian-ish local
    resampling. Simple Markov resample from empirical transition table."""
    trans = collections.defaultdict(list)
    for a, b in zip(seq, seq[1:]):
        trans[a].append(b)
    out = [rng.choice(seq)]
    for _ in range(len(seq) - 1):
        nxts = trans.get(out[-1])
        out.append(rng.choice(nxts) if nxts else rng.choice(seq))
    return out


rng = random.Random(3301)
CTRL_ITERS = 200
ctrl0_counts, ctrl0_maxlen, ctrl0_approx = [], [], []
ctrl1_counts, ctrl1_maxlen, ctrl1_approx = [], [], []
for t in range(CTRL_ITERS):
    r0 = find_repeats(shuffle0(S, rng))
    ctrl0_counts.append(len(r0))
    ctrl0_maxlen.append(max((h["len"] for h in r0), default=0))
    ctrl0_approx.append(sum(1 for h in r0 if h["edit"] >= 1 and h["len"] >= 12))
    r1 = find_repeats(shuffle1(S, rng))
    ctrl1_counts.append(len(r1))
    ctrl1_maxlen.append(max((h["len"] for h in r1), default=0))
    ctrl1_approx.append(sum(1 for h in r1 if h["edit"] >= 1 and h["len"] >= 12))


def stats(xs):
    xs = sorted(xs)
    n = len(xs)
    mean = sum(xs) / n
    p95 = xs[int(0.95 * n)]
    return mean, p95, max(xs)


c0m, c0p95, c0max = stats(ctrl0_counts)
c1m, c1p95, c1max = stats(ctrl1_counts)
l0m, l0p95, l0max = stats(ctrl0_maxlen)
l1m, l1p95, l1max = stats(ctrl1_maxlen)
a0m, a0p95, a0max = stats(ctrl0_approx)
a1m, a1p95, a1max = stats(ctrl1_approx)


def pval(obs_val, ctrl):
    return sum(1 for c in ctrl if c >= obs_val) / len(ctrl)


print("\n" + "=" * 68)
print("CONTROL COMPARISON (200 iters each, seed 3301)")
print("=" * 68)
print(f"{'metric':<28}{'observed':>10}{'0ord mean/p95/max':>22}"
      f"{'1ord mean/p95/max':>22}")
print(f"{'total repeats (L>=10)':<28}{n_obs:>10}"
      f"{f'{c0m:.1f}/{c0p95}/{c0max}':>22}{f'{c1m:.1f}/{c1p95}/{c1max}':>22}")
print(f"{'max repeat length':<28}{max_len_obs:>10}"
      f"{f'{l0m:.1f}/{l0p95}/{l0max}':>22}{f'{l1m:.1f}/{l1p95}/{l1max}':>22}")
print(f"{'approx repeats(edit>=1,L>=12)':<28}{len(approx_obs):>10}"
      f"{f'{a0m:.1f}/{a0p95}/{a0max}':>22}{f'{a1m:.1f}/{a1p95}/{a1max}':>22}")

p_count0 = pval(n_obs, ctrl0_counts); p_count1 = pval(n_obs, ctrl1_counts)
p_len0 = pval(max_len_obs, ctrl0_maxlen); p_len1 = pval(max_len_obs, ctrl1_maxlen)
p_apx0 = pval(len(approx_obs), ctrl0_approx); p_apx1 = pval(len(approx_obs), ctrl1_approx)
print("\n[empirical p-values: P(control >= observed)]")
print(f"  total-count:  vs0={p_count0:.3f}  vs1={p_count1:.3f}")
print(f"  max-length:   vs0={p_len0:.3f}  vs1={p_len1:.3f}")
print(f"  approx-count: vs0={p_apx0:.3f}  vs1={p_apx1:.3f}")

# A real gapped-keystream desync signal must beat BOTH controls on at least one
# axis (p<0.05 on max-length or approx-count). Total-count alone is weak.
signal = ((p_len0 < 0.05 and p_len1 < 0.05) or
          (p_apx0 < 0.05 and p_apx1 < 0.05))
print("\n" + "=" * 68)
print(f"VERDICT: {'SIGNAL -- approximate repeat structure beats both controls'
                  if signal else 'CLEAN NULL -- indistinguishable from filtered OTP'}")
print("=" * 68)
