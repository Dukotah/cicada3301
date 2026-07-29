#!/usr/bin/env python3
"""H2: re-run the doublet-continuity test RESTRICTED to the red-section joins.

The published continuity test averaged over ALL page joins (doublet rate at '%'
boundaries = 0.0000) and could dilute a sparse-boundary signal. If a per-section
key reset exists, doublet behaviour at the ~14 red-page joins should differ from
the interior joins.

We measure, at each PAGE JOIN (last rune of page p, first rune of page p+1):
  - "doublet" = last rune of p equals first rune of p+1 (the no-adjacent-repeat
    suppression the cipher's ~83% doublet filter imposes; interior doublet rate
    is near 0 everywhere).
Then also the WITHIN-page adjacent-equal (doublet) rate as the interior baseline
the filter should hold, and compare red-join vs non-red-join behaviour.

A per-section RESET would let the filter "forget" across a section boundary, so
we'd expect ELEVATED adjacent-equal frequency crossing a red join relative to
crossing a non-red join.
"""
import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))
from lp import gematria as gp

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
RED = {0, 3, 6, 7, 8, 15, 23, 27, 33, 37, 39, 40, 53, 54}

data = open(os.path.join(ROOT, "data/krisyotam_runes.txt"), encoding="utf-8").read()
segs = data.split("%")
pages = []
for p in range(55):
    pages.append([gp.RUNE_TO_IDX[c] for c in segs[p] if c in gp.RUNE_TO_IDX])

# ---- interior baseline: adjacent-equal (doublet) rate WITHIN pages 0..54
adj_eq = 0
adj_tot = 0
for pg in pages:
    for i in range(len(pg) - 1):
        adj_tot += 1
        if pg[i] == pg[i + 1]:
            adj_eq += 1
interior_rate = adj_eq / adj_tot
print(f"[baseline] interior adjacent-equal rate = {adj_eq}/{adj_tot} = {interior_rate:.5f}")
print(f"           (the ~doublet-suppressed continuity signal; near 0 confirms filter)")

# ---- page joins: last of p vs first of p+1
# A join is "red" if page p+1 is a red section head (a reset would occur AT the
# opener). We test both conventions (p+1 red, and p red) to be safe.
joins = []
for p in range(54):
    last = pages[p][-1]
    first = pages[p + 1][0]
    eq = (last == first)
    is_red_next = (p + 1) in RED
    is_red_here = p in RED
    joins.append((p, eq, is_red_next, is_red_here))

def rate(sub):
    if not sub:
        return 0.0, 0
    e = sum(1 for _, eq, *_ in sub if eq)
    return e / len(sub), len(sub)

red_next = [j for j in joins if j[2]]
non_red_next = [j for j in joins if not j[2]]
rn_rate, rn_n = rate(red_next)
nr_rate, nr_n = rate(non_red_next)
print(f"\n[joins] total page joins = {len(joins)}")
print(f"  red-section joins (page p+1 is red head): n={rn_n}  "
      f"adjacent-equal rate = {rn_rate:.5f}  (equals={sum(1 for j in red_next if j[1])})")
print(f"  non-red joins:                            n={nr_n}  "
      f"adjacent-equal rate = {nr_rate:.5f}  (equals={sum(1 for j in non_red_next if j[1])})")

# ---- significance: permutation test. Under H0 (no reset), the join-equal flags
# are exchangeable; is the red-join equal-count significantly higher than chance?
obs_red_eq = sum(1 for j in red_next if j[1])
all_flags = [j[1] for j in joins]
rng = random.Random(7)
iters = 100000
ge = 0
for _ in range(iters):
    samp = rng.sample(all_flags, rn_n)
    if sum(samp) >= obs_red_eq:
        ge += 1
pval = ge / iters
print(f"\n[perm test] P(red-join equal-count >= {obs_red_eq} | H0 exchangeable) = {pval:.4f} "
      f"({iters} perms)")

# Also compare crossing-join equal rate vs the INTERIOR adjacent-equal rate:
# if a reset exists, red joins should look MORE like independent draws (higher eq)
# than the interior filtered stream.
p_indep = sum((pages[p].count(v) for p in range(55) for v in [0]))  # placeholder
# expected equal rate if last/first were independent uniform-ish: sum p_i^2
from collections import Counter
allc = Counter(v for pg in pages for v in pg)
tot = sum(allc.values())
p_coll = sum((c / tot) ** 2 for c in allc.values())
print(f"[ref] independent-draw collision prob (sum p_i^2) = {p_coll:.5f}")
print(f"      interior filtered rate {interior_rate:.5f} << {p_coll:.5f} confirms suppression.")

# ---- verdict
print("\n" + "=" * 60)
sig = (pval < 0.01) and (rn_rate > nr_rate) and (obs_red_eq > 0)
# also require the red rate to actually deviate from interior in the reset direction
elevated = rn_rate > p_coll * 0.5   # would need to approach independence
print(f"H2 red-join equal rate {rn_rate:.5f} vs non-red {nr_rate:.5f} vs interior {interior_rate:.5f}")
print(f"H2 perm p={pval:.4f}  (need <0.01 AND red>non-red AND toward-independence for SIGNAL)")
print(f"H2 VERDICT: {'SIGNAL (escalate)' if sig and elevated else 'CLEAN NULL (sealed)'}")
