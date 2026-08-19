"""FRONT D2 red-team: independently recompute the load-bearing LP2 statistics
from raw runes. Check for miscounts, wrong-stream, interrupter/solved-page leakage,
page-join artifacts.

POSITIVE CONTROL FIRST: recover a planted English signal through the scorer/null.
"""
import os, sys, math, collections, random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "analysis"))

from lp import gematria as gp, stats  # noqa
sys.path.insert(0, os.path.join(ROOT, "analysis", "round11"))
import lib_numchannel as nc  # noqa

N = gp.N
KRIS = os.path.join(ROOT, "data", "krisyotam_runes.txt")

def banner(s): print("\n" + "="*70 + "\n" + s + "\n" + "="*70)

# ---------------------------------------------------------------- POSITIVE CONTROL
banner("POSITIVE CONTROL: plant English, recover through scorer vs null")
# take a solved-page English plaintext, encode to indices, score it
eng = gp.keyword_to_indices("THEPRIMESARESACREDTHETOTIENTFUNCTIONISSACREDALLTHINGSSHOULDBEENCRYPTEDKNOWTHISFINDYOURTRUTH"*3)
noise = nc.shuffled(eng, seed=999)
s_eng = nc.eng_norm(eng)
s_noise = nc.eng_norm(noise)
print(f"planted English score_norm = {s_eng:.3f}  (target ~ -4.4 English)")
print(f"shuffled  noise score_norm = {s_noise:.3f}  (target ~ -7.5 noise)")
CONTROL_OK = (s_eng >= -5.5 and s_noise <= -6.5 and s_eng > s_noise + 1.5)
print(f"CONTROL_OK = {CONTROL_OK}  (jump {s_eng - s_noise:.2f})")

# ---------------------------------------------------------------- load pages independently
banner("Independent raw-rune parse & page inventory")
txt = open(KRIS, encoding="utf-8").read()
segs = txt.split("%")
pages = []
for s in segs:
    idxs = gp.runes_to_indices(s)
    if idxs:
        pages.append(idxs)
print(f"num nonempty page-segments: {len(pages)}")
print(f"per-page rune counts: {[len(p) for p in pages]}")

# stream the repo uses
unsolved = [i for p in pages[:-2] for i in p]
print(f"\nrepo 'unsolved' = pages[:-2] flattened: n = {len(unsolved)}  (claimed 12956)")

# ---------------------------------------------------------------- doublet: overall vs page-join
banner("DOUBLET RATE: flattened-with-joins vs per-page (no cross-page adjacency)")
def dblcount(idxs): return sum(1 for a,b in zip(idxs, idxs[1:]) if a==b)

flat_d = dblcount(unsolved)
flat_pairs = len(unsolved) - 1
print(f"flattened: {flat_d} doublets / {flat_pairs} adj pairs = {100*flat_d/flat_pairs:.3f}%")

# per-page (exclude cross-page joins)
perpage_d = sum(dblcount(p) for p in pages[:-2])
perpage_pairs = sum(len(p)-1 for p in pages[:-2])
print(f"per-page : {perpage_d} doublets / {perpage_pairs} adj pairs = {100*perpage_d/perpage_pairs:.3f}%")
join_pairs = flat_pairs - perpage_pairs
join_d = flat_d - perpage_d
print(f"cross-page joins: {join_pairs} pairs, {join_d} of them doublets")

# ---------------------------------------------------------------- interrupter inclusion
banner("INTERRUPTER (F-rune idx 0) inclusion effect")
F = gp.RUNE_TO_IDX[gp.INTERRUPTER]
nF = sum(1 for i in unsolved if i == F)
print(f"F-rune count in stream: {nF} ({100*nF/len(unsolved):.2f}% of runes)")
# doublets involving F
FF = sum(1 for a,b in zip(unsolved, unsolved[1:]) if a==b==F)
print(f"F-F doublets: {FF}")
# strip interrupters per-page then recompute doublet
stripped_pages = [[i for i in p if i != F] for p in pages[:-2]]
strip_flat = [i for p in stripped_pages for i in p]
sd = dblcount(strip_flat)
print(f"strip-F flattened doublet rate: {100*sd/(len(strip_flat)-1):.3f}% (n={len(strip_flat)})")
sd_pp = sum(dblcount(p) for p in stripped_pages)
sd_pp_pairs = sum(len(p)-1 for p in stripped_pages)
print(f"strip-F per-page  doublet rate: {100*sd_pp/sd_pp_pairs:.3f}%")

# ---------------------------------------------------------------- IoC and entropy
banner("IoC.N and entropy independent recompute")
def ioc_norm(idxs):
    c = collections.Counter(idxs); n = len(idxs)
    return (sum(v*(v-1) for v in c.values())/(n*(n-1)))*N
def ent(idxs):
    c = collections.Counter(idxs); n=len(idxs)
    return -sum((v/n)*math.log2(v/n) for v in c.values())
print(f"IoC.N (with F, flattened)   = {ioc_norm(unsolved):.4f}  (claimed 1.000)")
print(f"IoC.N (strip F)             = {ioc_norm(strip_flat):.4f}")
print(f"entropy (with F)            = {ent(unsolved):.4f}  (claimed 4.857)")
print(f"entropy (strip F)           = {ent(strip_flat):.4f}")
print(f"max entropy log2(29)        = {math.log2(29):.4f}")
print(f"max entropy log2(28) [no F] = {math.log2(28):.4f}")

# random expectation for doublet under uniform 29
print(f"\nrandom doublet baseline 1/29 = {100/29:.3f}%")

# ---------------------------------------------------------------- solved page leakage check
banner("SOLVED-PAGE LEAKAGE: are known-solved pages inside pages[:-2]?")
# Known solved LP2 pages decode to English. Test each page: does a simple
# shift/atbash/known-key make it English? Cheap proxy: per-page IoC.N and doublet.
# Solved (plaintext-ish under known key) pages would show English stats only AFTER
# decode; ciphertext pages look flat. But the FIRST pages of LP (intro) are solved.
for i, p in enumerate(pages):
    tag = ""
    if i >= len(pages)-2: tag = " <-- excluded (AN END / PARABLE)"
    print(f"page {i:2d}: n={len(p):4d} IoC.N={ioc_norm(p):.3f} dbl={100*dblcount(p)/(len(p)-1):.2f}%{tag}")

# ---------------------------------------------------------------- period bound p*
banner("PERIOD BOUND p* — where does ~400 come from?")
# IoC-based unicity / Friedman: for a periodic (Vigenere) key of period L over the
# flat stream, expected column IoC. If stream is truly flat, no period detectable.
# The '~400' bound: check what statistic yields it. Compute per-period mean column
# IoC.N for L=1..60 to see if any period lifts above flat.
def period_col_iocN(idxs, L):
    cols = [idxs[j::L] for j in range(L)]
    vals = [ioc_norm(c) for c in cols if len(c) > 30]
    return sum(vals)/len(vals) if vals else float('nan')
print("L : mean column IoC.N (flat ~1.0; a real period would spike >1.3)")
best = (0, 0.0)
for L in list(range(1,21)) + [30,40,41,50,60,82,164]:
    v = period_col_iocN(unsolved, L)
    if v > best[1]: best = (L, v)
    print(f"  L={L:4d}: {v:.4f}")
print(f"best period column IoC.N: L={best[0]} val={best[1]:.4f}")

# ---------------------------------------------------------------- null on the real stream
banner("NULL BAND on real unsolved stream (n>=200)")
mean, mx, vals = nc.null_band(nc.eng_norm, unsolved, n=200)
real = nc.eng_norm(unsolved)
print(f"real stream eng_norm       = {real:.3f}")
print(f"shuffle null mean/max      = {mean:.3f} / {mx:.3f}")
print(f"FP ceiling (null_max+0.5)  = {mx+0.5:.3f}")

print("\nDONE")
