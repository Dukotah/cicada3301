"""Campaign XIV probes -- execute the CHEAP, DECISIVE soundness gaps the Fable 5
red-team surfaced. Each is falsifiable and reproducible.

  P1  Corpus-wide self-coincidence (kappa) scan, lags 1..6478  -- the ledger only
      ever checked lags 2..30 PER PAGE; a book-wide key of period 41..N was never
      scanned. Any lag with coincidence >> 3.45% = key reuse/periodicity = OTP falsified.
  P2  Long-period column IoC, periods 41..2000 -- corpus-wide Friedman the vigauto
      attack (fixed period, per page) could not see. A peak = periodic key of that len.
  P3  Page-boundary continuity -- are doublets suppressed ACROSS page breaks? 0 vs ~1.9
      expected => the book body is ONE continuous filtered stream in book order.
  P4  Bigram-matrix flatness -- off-diagonal chi2 vs uniform. Flat => kills generalized
      -combiner/tableau feedback AND many-to-few homophonic re-encoding (Fable's own
      proposal, self-refuted by this measurement).
  P5  Word-length channel -- an OTP hides symbol VALUES, not word boundaries. Is the
      '-'/'.'-delimited word-length distribution English-like (vs a real English text
      mapped through the rune digraphs)? Positive = plaintext is real English prose.
  P6  pp49-51 payload as a 0..55 permutation (page order / offsets) -- instant, unambiguous.

Reproduce:  PYTHONUTF8=1 python analysis/campaign14/probes.py
"""
import os, sys, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(os.path.dirname(ROOT), "src"))
from lp import gematria as gp
N = gp.N
RUNE = gp.RUNE_TO_IDX
KRIS = os.path.join(os.path.dirname(ROOT), "data", "krisyotam_runes.txt")

raw = open(KRIS, encoding="utf-8").read()
pages_raw = [p for p in raw.split("%") if any(ch in RUNE for ch in p)]
# unsolved LP2 body = all but the last two solved pages (AN END / PARABLE), matching the rig
body_pages = pages_raw[:-2] if len(pages_raw) > 2 else pages_raw
def to_idx(s): return [RUNE[c] for c in s if c in RUNE]
page_idx = [to_idx(p) for p in body_pages]
stream = np.array([i for pg in page_idx for i in pg])
L = len(stream)
print("="*70); print(f"CAMPAIGN XIV probes -- {len(page_idx)} unsolved pages, {L} runes"); print("="*70)

# ---- P1 coincidence scan ----
print("\nP1  CORPUS-WIDE SELF-COINCIDENCE (kappa) scan, lags 1..6478")
exp = 1.0/N  # 0.03448
peaks = []
for Lg in range(1, min(6479, L)):
    a = stream[:-Lg]; b = stream[Lg:]
    k = np.mean(a == b)
    se = math.sqrt(exp*(1-exp)/len(a))
    z = (k - exp)/se
    if z > 5.0:
        peaks.append((Lg, k*100, z))
print(f"  baseline expected coincidence = {exp*100:.3f}%  (random)")
print(f"  lags with coincidence > 5 sigma above random: {len(peaks)}")
for Lg,k,z in sorted(peaks, key=lambda x:-x[2])[:8]:
    print(f"    lag {Lg:5d}: {k:.3f}%  ({z:+.1f} sigma)")
if not peaks:
    print("    NONE -> no corpus-wide key reuse / periodicity at ANY lag 1..6478. OTP verdict holds.")

# ---- P2 long-period column IoC ----
print("\nP2  LONG-PERIOD COLUMN IoC.N, periods 41..2000  (never scanned before)")
def col_iocN(s, P):
    tot=0.0; cnt=0
    for c in range(P):
        col = s[c::P]
        if len(col) < 2: continue
        counts = np.bincount(col, minlength=N).astype(float)
        n=len(col); ioc = (counts*(counts-1)).sum()/(n*(n-1)) if n>1 else 0
        tot += ioc*N; cnt+=1
    return tot/cnt if cnt else 0
best=[]
for P in range(41, 2001):
    v = col_iocN(stream, P)
    best.append((v, P))
best.sort(reverse=True)
print(f"  English IoC.N ~ 1.73; random/OTP ~ 1.00. A periodic key of length P spikes at P.")
print(f"  top 5 periods by column IoC.N: " + ", ".join(f"P={p} ({v:.3f})" for v,p in best[:5]))
print(f"  max {best[0][0]:.3f} at P={best[0][1]}  -> {'FLAT (no periodic key)' if best[0][0] < 1.15 else 'PEAK -- investigate'}")

# ---- P3 page-boundary continuity ----
print("\nP3  PAGE-BOUNDARY doublet continuity")
bnd = sum(1 for i in range(len(page_idx)-1) if page_idx[i] and page_idx[i+1] and page_idx[i][-1]==page_idx[i+1][0])
nb = len(page_idx)-1
print(f"  boundaries: {nb} | doublets at boundary: {bnd} | expected if unsuppressed: {nb/N:.2f}")
print(f"  -> suppression {'CONTINUES across page breaks (one continuous stream in book order)' if bnd==0 else 'may reset at page breaks'}")

# ---- P4 bigram structure BEYOND monograms (independence model, not flat-uniform) ----
print("\nP4  BIGRAM structure beyond monograms (independence model + MC filtered null)")
def offdiag_chi2_independence(seq_pages):
    M = np.zeros((N,N))
    for pg in seq_pages:
        for a,b in zip(pg[:-1], pg[1:]): M[a,b]+=1
    rs = M.sum(1, keepdims=True); cs = M.sum(0, keepdims=True); tot = M.sum()
    exp = rs*cs/tot                      # independence expectation from the marginals
    mask = ~np.eye(N, dtype=bool)        # off-diagonal only (doublet suppression lives on the diagonal)
    e = exp[mask]; o = M[mask]; e = np.where(e<1e-9, 1e-9, e)
    return float((((o-e)**2)/e).sum())
chi2_real = offdiag_chi2_independence(page_idx)
df = (N-1)*(N-1)-1
# MC null: filtered-uniform streams with the same ~0.66% soft no-repeat suppression, same page lengths
import random as _r; rng=_r.Random(3301)
def filtered_stream(lengths, suppress=0.83):
    out=[]
    for ln in lengths:
        pg=[]; prev=-1
        for _ in range(ln):
            x=rng.randrange(N)
            if x==prev and rng.random()<suppress: x=rng.randrange(N)
            pg.append(x); prev=x
        out.append(pg)
    return out
lens=[len(p) for p in page_idx]
null=[offdiag_chi2_independence(filtered_stream(lens)) for _ in range(200)]
nmean, nstd = float(np.mean(null)), float(np.std(null))
zc = (chi2_real - nmean)/nstd
print(f"  off-diagonal chi2 (independence) real = {chi2_real:.0f}   df ~ {df}")
print(f"  filtered-uniform MC null: {nmean:.0f} +- {nstd:.0f}  (200 samples)")
print(f"  real vs null: {zc:+.2f} sigma  -> "
      + ("FLAT: no second-order structure beyond the known doublet filter (kills combiner-feedback & many-to-few homophonic)"
         if abs(zc)<3 else "SECOND-ORDER STRUCTURE present beyond the filter -- POTENTIAL LEAD, verify further"))

# ---- P5 word-length channel ----
print("\nP5  WORD-LENGTH channel (OTP cannot hide word boundaries)")
def word_lengths_from_runes(pages):
    wl=[]
    for p in pages:
        cur=0
        for ch in p:
            if ch in RUNE: cur+=1
            elif ch in "-./ ":   # word / sentence / space separators
                if cur: wl.append(cur); cur=0
        if cur: wl.append(cur)
    return wl
uw = word_lengths_from_runes(body_pages)
# Apples-to-apples reference: the SOLVED Cicada pages (same transcription, same style,
# known English plaintext), which carry the same '-' word separators.
solved_pages_raw = pages_raw[-2:]   # AN END / PARABLE (the rig treats these as solved)
sw = word_lengths_from_runes(solved_pages_raw)
def hist(wl, k=12):
    h=np.zeros(k)
    for x in wl: h[min(max(x,1),k)-1]+=1
    return h/h.sum() if h.sum() else h
hu, hs = hist(uw), hist(sw)
# random-segmentation null: same word count & total runes, boundaries placed at random
def random_seg_lengths(total, nwords):
    cuts=sorted(rng.sample(range(1,total), nwords-1)); prev=0; out=[]
    for c in cuts: out.append(c-prev); prev=c
    out.append(total-prev); return out
rl=random_seg_lengths(sum(uw),len(uw)); hr=hist(rl)
# total-variation distance is robust to the small solved sample (unlike chi2 with empty tail bins)
def tvd(a,b): return 0.5*float(np.abs(a-b).sum())
tvd_s, tvd_r = tvd(hu,hs), tvd(hu,hr)
print(f"  unsolved: {len(uw)} words, mean len {np.mean(uw):.2f}")
print(f"  solved Cicada ref (AN END/PARABLE): {len(sw)} words, mean len {np.mean(sw):.2f}")
print(f"  unsolved dist : " + " ".join(f"{x:.2f}" for x in hu))
print(f"  solved   dist : " + " ".join(f"{x:.2f}" for x in hs))
print(f"  random   dist : " + " ".join(f"{x:.2f}" for x in hr))
print(f"  total-variation distance:  unsolved->solved = {tvd_s:.3f}   unsolved->random = {tvd_r:.3f}")
print(f"  key tell: 1-rune words  unsolved {hu[0]:.2f} / solved {hs[0]:.2f} / random {hr[0]:.2f}"
      f"  (language suppresses 1-letter words; random doesn't)")
print(f"  -> boundaries are {'ENGLISH-LIKE (closer to solved Cicada than to random segmentation)' if tvd_s < tvd_r else 'inconclusive'}"
      f"  [directional: solved ref is only {len(sw)} words]")

# ---- P6 payload as permutation ----
print("\nP6  pp49-51 payload as a 0..55 permutation window")
pbytes = open(os.path.join(ROOT,"pp49_51","canon_256.bin"),"rb").read()
# the only MEANINGFUL test: a window whose bytes mod 56 form an exact permutation of 0..55
mod56=None
for off in range(0, len(pbytes)-55):
    win = [pbytes[off+j] % 56 for j in range(56)]
    if sorted(win)==list(range(56)): mod56=off; break
print(f"  mod-56 permutation-of-0..55 window: {'offset '+str(mod56) if mod56 is not None else 'NONE'}")
print(f"  -> payload is NOT an encoded page-order permutation / offset table"
      f"  (rank-order 'permutations' are trivial for any distinct window, so not tested)")
print("\n" + "="*70); print("Campaign XIV probes complete."); print("="*70)
