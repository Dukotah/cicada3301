#!/usr/bin/env python3
"""Deep structural fingerprint of the unsolved Liber Primus corpus (pages 0-55).
Source: data/krisyotam_runes.txt (chunk 56 = solved AN END page, excluded)."""
import sys, math, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from lp import gematria as g
import numpy as np
from collections import Counter

N = g.N  # 29
DATA = open(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'krisyotam_runes.txt')).read()
RAW_PAGES = DATA.split('%')

def page_idx(p):
    return [g.RUNE_TO_IDX[ch] for ch in p if ch in g.RUNE_TO_IDX]

# Pages 0-55 are unsolved; chunk 56 is solved -> exclude.
PAGES = []
for i, p in enumerate(RAW_PAGES):
    if i > 55:
        continue
    idx = page_idx(p)
    if idx:
        PAGES.append((i, idx))

# Per-line structure (lines within a page split by newline)
LINES = []
for i, p in enumerate(RAW_PAGES):
    if i > 55:
        continue
    for ln in p.split('\n'):
        li = page_idx(ln)
        if li:
            LINES.append((i, li))

ALL = []
for i, idx in PAGES:
    ALL.extend(idx)
ALL = np.array(ALL, dtype=int)
Ntot = len(ALL)
print(f"Unsolved corpus: {len(PAGES)} pages, {Ntot} runes, {len(LINES)} lines")

out = open(os.path.join(os.path.dirname(__file__), 'RESULTS.txt'), 'w')
def w(*a):
    s = ' '.join(str(x) for x in a)
    print(s); out.write(s + '\n')

w(f"=== UNSOLVED CORPUS: pages 0-55, {Ntot} runes, {len(PAGES)} pages, {len(LINES)} lines ===\n")

# ---- 1. Unigram freq ----
unifreq = np.array([np.sum(ALL == r) for r in range(N)], dtype=float)
unip = unifreq / Ntot
w("--- 1. UNIGRAM FREQUENCIES ---")
for r in range(N):
    w(f"  {g.IDX_TO_TRANS[r]:>3} idx{r:2d}: {unifreq[r]:5.0f}  {100*unip[r]:5.2f}%")
H1 = -np.sum(unip[unip > 0] * np.log2(unip[unip > 0]))
w(f"unigram entropy = {H1:.4f} bits (max = {math.log2(N):.4f})")
# chi-square vs uniform
exp_uni = Ntot / N
chi_uni = np.sum((unifreq - exp_uni) ** 2 / exp_uni)
w(f"chi-square vs uniform: {chi_uni:.1f}  (df={N-1}, crit_0.01~{49.6})\n")

# ---- 1b. Bigram adjacency matrix ----
w("--- 1b. BIGRAM ADJACENCY (within-page only) ---")
B = np.zeros((N, N), dtype=int)
nbig = 0
for i, idx in PAGES:
    for a, b in zip(idx, idx[1:]):
        B[a, b] += 1
        nbig += 1
w(f"total adjacent bigrams (within-page): {nbig}")

# expected under independence using observed unigram marginals
# use the marginal of the FIRST and SECOND position to be precise
row_marg = B.sum(axis=1).astype(float)  # count as first member
col_marg = B.sum(axis=0).astype(float)  # count as second member
exp = np.outer(row_marg, col_marg) / nbig

# Doublet analysis (diagonal)
diag_obs = np.diag(B).sum()
diag_exp = np.sum([row_marg[r] * col_marg[r] / nbig for r in range(N)])
w(f"DOUBLETS observed (diagonal): {diag_obs} ({100*diag_obs/nbig:.3f}%)")
w(f"DOUBLETS expected (independence): {diag_exp:.1f} ({100*diag_exp/nbig:.3f}%)")
w(f"suppression ratio: {diag_exp/max(diag_obs,1e-9):.2f}x\n")

# per-rune doublet detail: is suppression uniform?
w("--- DOUBLET per-rune: obs vs expected on diagonal ---")
w(f"{'rune':>4} {'obs':>4} {'exp':>7} {'ratio':>6} {'(o-e)/sqrt(e)':>13}")
diag_rows = []
for r in range(N):
    o = B[r, r]
    e = row_marg[r] * col_marg[r] / nbig
    z = (o - e) / math.sqrt(e) if e > 0 else 0
    ratio = e / o if o > 0 else float('inf')
    diag_rows.append((r, o, e, ratio, z))
    w(f"{g.IDX_TO_TRANS[r]:>4} {o:>4} {e:>7.2f} {ratio:>6.2f} {z:>13.2f}")
# how uniform? coefficient of variation of the per-rune RATE relative to its expectation
# Use the fraction of expected doublets realized per rune
realized = np.array([B[r, r] / (row_marg[r] * col_marg[r] / nbig) if (row_marg[r] * col_marg[r]) > 0 else 0 for r in range(N)])
w(f"\nrealized-fraction (obs/exp) per rune: mean={realized.mean():.3f} std={realized.std():.3f} min={realized.min():.3f} max={realized.max():.3f}")
w("(if uniform suppression, all ~ equal & small)\n")

# ---- Off-diagonal: forbidden & suppressed pairs ----
w("--- FORBIDDEN PAIRS (obs=0 but expected>=5) ---")
forbidden = []
for a in range(N):
    for b in range(N):
        if B[a, b] == 0 and exp[a, b] >= 5:
            forbidden.append((a, b, exp[a, b]))
forbidden.sort(key=lambda x: -x[2])
if forbidden:
    for a, b, e in forbidden:
        w(f"  {g.IDX_TO_TRANS[a]}->{g.IDX_TO_TRANS[b]}  exp={e:.2f}  ({'DOUBLET' if a==b else ''})")
else:
    w("  NONE with exp>=5")
w(f"total forbidden (exp>=5): {len(forbidden)}, of which doublets: {sum(1 for a,b,e in forbidden if a==b)}\n")

w("--- TOP-20 SUPPRESSED PAIRS by z-score (z<0) ---")
cells = []
for a in range(N):
    for b in range(N):
        e = exp[a, b]
        if e >= 5:
            z = (B[a, b] - e) / math.sqrt(e)
            cells.append((z, a, b, B[a, b], e))
cells.sort()
for z, a, b, o, e in cells[:20]:
    tag = ' <DOUBLET>' if a == b else ''
    w(f"  {g.IDX_TO_TRANS[a]:>3}->{g.IDX_TO_TRANS[b]:<3} obs={o:>4} exp={e:>6.1f} z={z:>7.2f}{tag}")
w("\n--- TOP-10 OVER-represented pairs by z-score ---")
for z, a, b, o, e in cells[-10:][::-1]:
    tag = ' <DOUBLET>' if a == b else ''
    w(f"  {g.IDX_TO_TRANS[a]:>3}->{g.IDX_TO_TRANS[b]:<3} obs={o:>4} exp={e:>6.1f} z={z:>7.2f}{tag}")

# Chi-square on the whole bigram table excluding diagonal vs off-diagonal contribution
chi_full = np.sum((B - exp) ** 2 / np.where(exp > 0, exp, 1))
chi_diag = np.sum([(B[r, r] - exp[r, r]) ** 2 / exp[r, r] for r in range(N) if exp[r, r] > 0])
chi_off = chi_full - chi_diag
w(f"\nbigram chi-square total={chi_full:.1f}, diagonal contribution={chi_diag:.1f} ({100*chi_diag/chi_full:.1f}%), off-diagonal={chi_off:.1f}")
w(f"df={N*N-1}. If off-diagonal ~ df it's consistent with independence except the diagonal.\n")

np.save(os.path.join(os.path.dirname(__file__), 'bigram_matrix.npy'), B)
out.close()
print("\n[wrote RESULTS.txt + bigram_matrix.npy]")
