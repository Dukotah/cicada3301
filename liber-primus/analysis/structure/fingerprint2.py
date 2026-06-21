#!/usr/bin/env python3
"""Part 2: positional/periodic doublet structure, higher-order, mutual info, gematria."""
import sys, math, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from lp import gematria as g
import numpy as np
from collections import Counter

N = g.N
DATA = open(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'krisyotam_runes.txt')).read()
RAW = DATA.split('%')
def page_idx(p): return [g.RUNE_TO_IDX[ch] for ch in p if ch in g.RUNE_TO_IDX]
PAGES = [(i, page_idx(p)) for i, p in enumerate(RAW) if i <= 55 and page_idx(p)]
ALL = []
for i, idx in PAGES: ALL.extend(idx)
ALL = np.array(ALL)
Ntot = len(ALL)

out = open(os.path.join(os.path.dirname(__file__), 'RESULTS2.txt'), 'w')
def w(*a):
    s = ' '.join(str(x) for x in a); print(s); out.write(s + '\n')

# ===== 2. POSITIONAL / PERIODIC doublet structure =====
w("=== 2. POSITIONAL / PERIODIC DOUBLET STRUCTURE ===")
# global doublet positions (within concatenated page streams, gaps reset per page)
doub_positions = []  # absolute index in ALL
abs_pos = 0
for i, idx in PAGES:
    for j in range(len(idx) - 1):
        if idx[j] == idx[j+1]:
            doub_positions.append(abs_pos + j)
    abs_pos += len(idx)
doub_positions = np.array(doub_positions)
w(f"total doublets: {len(doub_positions)}")

# gaps between consecutive doublets
gaps = np.diff(doub_positions)
w(f"gap stats: mean={gaps.mean():.1f} median={np.median(gaps):.0f} std={gaps.std():.1f} min={gaps.min()} max={gaps.max()}")
# if doublets are a memoryless rare event, gaps ~ geometric -> std ~ mean
w(f"  (geometric/Poisson would give std ~= mean = {gaps.mean():.1f})")
# histogram of small gaps
gc = Counter(gaps.tolist())
w("  small-gap histogram (gap:count): " + ', '.join(f"{k}:{gc[k]}" for k in sorted(gc) if k <= 12))

# doublet position mod small N (within page)
w("\n-- doublet position-in-page mod M (chi-square vs uniform) --")
for M in [2, 3, 4, 5, 6, 7, 8, 11, 13]:
    buckets = Counter()
    tot = 0
    for i, idx in PAGES:
        for j in range(len(idx) - 1):
            if idx[j] == idx[j+1]:
                buckets[j % M] += 1; tot += 1
    exp = tot / M
    chi = sum((buckets[k] - exp) ** 2 / exp for k in range(M))
    w(f"  mod {M:2d}: chi={chi:6.2f} df={M-1}  counts={[buckets[k] for k in range(M)]}")

# ===== 3a. AUTOCORRELATION (IoC at lag k) =====
w("\n=== 3a. AUTOCORRELATION / KASISKI: IoC at lag k (within page) ===")
def ioc_lag(k):
    match = 0; tot = 0
    for i, idx in PAGES:
        for j in range(len(idx) - k):
            tot += 1
            if idx[j] == idx[j+k]: match += 1
    return match / tot * N, tot  # normalized IoC (1.0 = random)
w("  lag : IoC*N  (1.000=random; >1 suggests period)")
for k in list(range(1, 31)):
    v, tot = ioc_lag(k)
    flag = ' <--' if abs(v - 1) > 0.08 else ''
    w(f"  {k:3d} : {v:.3f}{flag}")

# ===== 3b. trigram IoC & repeated n-grams =====
w("\n=== 3b. TRIGRAM IoC & REPEATED N-GRAMS ===")
tri = Counter()
for i, idx in PAGES:
    for j in range(len(idx) - 2):
        tri[(idx[j], idx[j+1], idx[j+2])] += 1
ttot = sum(tri.values())
ioc_tri = sum(c * (c - 1) for c in tri.values()) / (ttot * (ttot - 1)) * (N ** 3)
w(f"trigram IoC*N^3 = {ioc_tri:.3f} (1.0=random)")
# longer repeats across the WHOLE corpus (concatenated) - Kasiski style
flat = ALL
for L in [4, 5, 6, 7, 8]:
    seen = Counter()
    for j in range(len(flat) - L + 1):
        seen[tuple(flat[j:j+L])] += 1
    reps = [(k, v) for k, v in seen.items() if v >= 2]
    w(f"  {L}-grams repeated >=2x: {len(reps)} distinct; max repeat = {max((v for k,v in reps), default=0)}")
    # expected number of repeated L-grams under random with N^L cells
    n = len(flat) - L + 1
    cells = N ** L
    exp_pairs = n * (n - 1) / 2 / cells
    w(f"      expected colliding pairs (random) ~ {exp_pairs:.2f}")

# ===== 3c. POSITIONAL rune-frequency bias =====
w("\n=== 3c. POSITIONAL RUNE-FREQ BIAS (does position-in-line bias the rune?) ===")
# build lines
LINES = []
for i, p in enumerate(RAW):
    if i > 55: continue
    for ln in p.split('\n'):
        li = page_idx(ln)
        if li: LINES.append(li)
# rune dist at line position 0 vs overall
pos0 = Counter(li[0] for li in LINES if li)
overall = Counter(ALL.tolist())
tot0 = sum(pos0.values())
exp0 = {r: overall[r] / Ntot * tot0 for r in range(N)}
chi0 = sum((pos0[r] - exp0[r]) ** 2 / exp0[r] for r in range(N) if exp0[r] > 0)
w(f"line-start rune dist chi-square vs overall = {chi0:.1f} df={N-1} (n={tot0} lines)")
top0 = sorted(pos0.items(), key=lambda x: -x[1])[:5]
w("  most common line-START runes: " + ', '.join(f"{g.IDX_TO_TRANS[r]}={c}" for r, c in top0))
# page start
pstart = Counter(idx[0] for i, idx in PAGES)
w("  page-START runes: " + ', '.join(f"{g.IDX_TO_TRANS[r]}={c}" for r, c in sorted(pstart.items(), key=lambda x:-x[1])[:6]))
pend = Counter(idx[-1] for i, idx in PAGES)
w("  page-END runes: " + ', '.join(f"{g.IDX_TO_TRANS[r]}={c}" for r, c in sorted(pend.items(), key=lambda x:-x[1])[:6]))

# ===== 3d. inter-page MUTUAL INFORMATION (shared key at same positions?) =====
w("\n=== 3d. INTER-PAGE positional agreement (shared keystream test) ===")
# For each pair of pages, align at position 0, count matches over overlap; compare to chance 1/N
seqs = [np.array(idx) for i, idx in PAGES]
import itertools
match_rates = []
for a, b in itertools.combinations(range(len(seqs)), 2):
    L = min(len(seqs[a]), len(seqs[b]))
    if L < 50: continue
    m = np.sum(seqs[a][:L] == seqs[b][:L]) / L
    match_rates.append(m)
match_rates = np.array(match_rates)
w(f"page-pair head-aligned match rate: mean={match_rates.mean():.4f} max={match_rates.max():.4f} (chance=1/29={1/N:.4f})")
w(f"  pairs with match > 2x chance: {np.sum(match_rates > 2/N)} of {len(match_rates)}")
# also end-aligned
match_end = []
for a, b in itertools.combinations(range(len(seqs)), 2):
    L = min(len(seqs[a]), len(seqs[b]))
    if L < 50: continue
    m = np.sum(seqs[a][-L:] == seqs[b][-L:]) / L
    match_end.append(m)
match_end = np.array(match_end)
w(f"page-pair tail-aligned match rate: mean={match_end.mean():.4f} max={match_end.max():.4f}")

# ===== 4. GEMATRIA PRIME-VALUE STREAM =====
w("\n=== 4. GEMATRIA PRIME-VALUE STREAM STRUCTURE ===")
primes = np.array(g.PRIMES)
pstream_all = []
linesums = []
for i, p in enumerate(RAW):
    if i > 55: continue
    for ln in p.split('\n'):
        li = page_idx(ln)
        if li:
            s = sum(primes[r] for r in li)
            linesums.append(s)
            pstream_all.extend(primes[r] for r in li)
pstream_all = np.array(pstream_all)
w(f"prime-stream: n={len(pstream_all)} sum={pstream_all.sum()} mean={pstream_all.mean():.2f}")
# total corpus sum mod small numbers (Cicada loves 3301, totient, etc.)
tot = int(pstream_all.sum())
for m in [3, 7, 3301, 1033, 29, 109]:
    w(f"  total prime-sum mod {m} = {tot % m}")
# line-sum mod patterns
linesums = np.array(linesums)
w(f"  line prime-sums: n={len(linesums)} mean={linesums.mean():.1f}")
for m in [3, 7, 29, 3301]:
    c = Counter((linesums % m).tolist())
    exp = len(linesums) / m
    chi = sum((c[k] - exp) ** 2 / exp for k in range(m)) if m < 50 else None
    if chi is not None:
        w(f"  line-sum mod {m}: chi={chi:.2f} df={m-1} counts={[c[k] for k in range(m)]}")
    else:
        w(f"  line-sum mod {m}: distinct residues hit = {len(c)}")
# is consecutive prime-stream difference flat (already known) - confirm modular structure
w(f"  prime-stream IoC by VALUE residue mod 29 == rune IoC (same), skipping")

out.close()
print("\n[wrote RESULTS2.txt]")
