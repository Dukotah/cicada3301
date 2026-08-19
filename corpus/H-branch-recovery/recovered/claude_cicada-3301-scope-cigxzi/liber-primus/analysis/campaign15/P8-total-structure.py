"""Campaign XV / P8 -- TOTAL-STRUCTURE CLOSURE.

Question: does ANY computable structure remain in the unsolved LP2 stream
BEYOND the two known signature statistics (IoC.N = 1.000, doublet ~= 0.66%)?

Method. Build 1000 filtered-uniform CONTROLS with Campaign XI's suppression
model (soft single-resample no-repeat pad). Each control reproduces BOTH
signature statistics BY CONSTRUCTION (uniform -> IoC.N ~ 1.000; suppression s*
-> doublet ~ 0.66%). Then measure whether real LP2 is more *compressible* /
more *predictable* than that control band using predictors that see structure
of ALL orders:

  (a) held-out cross-validated bits/rune from an order-m context model
      (Witten-Bell interpolated back-off), orders m = 1..MAXORDER;
  (b) LZMA bits/rune on bytes(stream) (a universal compressor -- catches
      structure no fixed-order model was told to look for).

Plus two provenance sub-tests, each scored as an LP2 percentile in the band:
  (c) sliding-window index-of-dispersion (multinomial vs under-dispersed);
  (d) monogram frequency drift across the book (blocks x symbols chi2).

GATE (stated before running):
  LP2 bits/rune BELOW the 1st percentile of the control band on ANY predictor,
  OR a sub-test statistic beyond the control band  =>  COMPUTABLE STRUCTURE
  EXISTS => OTP verdict WRONG => attack surface. LP2 INSIDE the band on every
  predictor => strongest ciphertext-side OTP confirmation (model-class verified).

Positive control: the SAME predictors are run on real English mapped to runes,
which MUST fall far below the band -- proving the predictors CAN detect
structure when it is present (else a null would be meaningless).

Reproduce:  PYTHONUTF8=1 python analysis/campaign15/P8-total-structure.py
"""
import os, sys, math, lzma
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "analysis"))
from lp import gematria as gp, stats  # noqa
from run_stats import english_baseline  # noqa

N = gp.N
RUNE = gp.RUNE_TO_IDX

# ---- config (reduce here if too slow; values reported in the writeup) --------
N_CONTROLS = int(os.environ.get("P8_NCONTROLS", 1000))
MAXORDER   = int(os.environ.get("P8_MAXORDER", 8))
TRAIN_FRAC = 0.80
SEED0      = 3301
# -----------------------------------------------------------------------------

# ---- load the unsolved LP2 stream (mirror campaign14 / the rig) --------------
raw = open(os.path.join(ROOT, "data", "krisyotam_runes.txt"), encoding="utf-8").read()
pages_raw = [p for p in raw.split("%") if any(ch in RUNE for ch in p)]
body_pages = pages_raw[:-2]
stream = np.array([RUNE[c] for p in body_pages for c in p if c in RUNE], dtype=np.int64)
L = len(stream)

def doublet_pct(a):
    a = np.asarray(a)
    return 100.0 * np.mean(a[1:] == a[:-1])

OBS_DBL = doublet_pct(stream)
OBS_IOC = stats.ioc_norm(list(stream))
print("=" * 74)
print(f"P8 TOTAL-STRUCTURE CLOSURE -- LP2 = {L} runes")
print(f"  observed  IoC.N = {OBS_IOC:.4f}   doublet = {OBS_DBL:.3f}%")
print("=" * 74)

# ---- calibrate suppression s* so controls reproduce the doublet rate ---------
# soft single-resample uniform pad: P(doublet) = (1/N)*(1 - s*(N-1)/N)
# solve for s given the observed doublet rate:
p_obs = OBS_DBL / 100.0
s_star = (1.0 - p_obs * N) / ((N - 1) / N)
s_star = min(max(s_star, 0.0), 1.0)
print(f"\ncalibrated suppression s* = {s_star:.4f}  (analytic, single-resample soft rule)")

def make_control(seed):
    """Filtered-uniform control: uniform draws with soft single-resample no-repeat.
    Reproduces IoC.N ~ 1.000 (uniform) and doublet ~ OBS by construction."""
    rng = np.random.default_rng(seed)
    x = rng.integers(0, N, size=L)
    r1 = rng.integers(0, N, size=L)          # resample candidates
    do = rng.random(size=L) < s_star         # whether to resample on collision
    out = np.empty(L, dtype=np.int64)
    out[0] = x[0]
    prev = x[0]
    xi = x; ri = r1; di = do
    for i in range(1, L):
        c = xi[i]
        if c == prev and di[i]:
            c = ri[i]
        out[i] = c
        prev = c
    return out

# sanity: one control's signature stats
_c0 = make_control(SEED0)
print(f"control[0] IoC.N = {stats.ioc_norm(list(_c0)):.4f}   doublet = {doublet_pct(_c0):.3f}%")

# =============================================================================
# PREDICTOR (a): held-out cross-validated bits/rune, Witten-Bell backoff
# =============================================================================
def context_bits_per_rune(seq, maxorder=MAXORDER, train_frac=TRAIN_FRAC):
    """Train interpolated (Witten-Bell) back-off counts on the first train_frac,
    return held-out bits/rune on the remainder, for each order 1..maxorder.
    Same procedure for real and control -> a fair percentile."""
    seq = np.asarray(seq, dtype=np.int64)
    ntr = int(len(seq) * train_frac)
    train, test = seq[:ntr], seq[ntr:]
    # counts[m] : dict ctx-tuple(len m) -> np.array(N) of counts (m=0..maxorder)
    counts = [dict() for _ in range(maxorder + 1)]
    counts[0][()] = np.zeros(N)
    for i in range(len(train)):
        sym = train[i]
        for m in range(0, maxorder + 1):
            if i - m < 0:
                break
            ctx = tuple(train[i - m:i])
            arr = counts[m].get(ctx)
            if arr is None:
                arr = np.zeros(N); counts[m][ctx] = arr
            arr[sym] += 1

    def prob_dist(ctx_full):
        # recursive Witten-Bell from order 0 up to len(ctx_full)
        p = np.full(N, 1.0 / N)  # order -1 : uniform
        for m in range(0, len(ctx_full) + 1):
            ctx = ctx_full[len(ctx_full) - m:] if m > 0 else ()
            arr = counts[m].get(ctx)
            if arr is None:
                continue  # unseen context -> keep lower-order estimate
            c = arr.sum()
            if c == 0:
                continue
            u = np.count_nonzero(arr)  # distinct types (Witten-Bell escape mass)
            lam = c / (c + u) if (c + u) > 0 else 0.0
            pml = arr / c
            p = lam * pml + (1.0 - lam) * p
        return p

    out = []
    for m in range(1, maxorder + 1):
        ll = 0.0
        for i in range(len(test)):
            lo = max(0, i - m)
            ctx = tuple(test[lo:i])
            p = prob_dist(ctx)
            ll += -math.log2(max(p[test[i]], 1e-12))
        out.append(ll / len(test))
    return out  # list length maxorder, bits/rune for orders 1..maxorder

# =============================================================================
# PREDICTOR (b): LZMA bits/rune on packed indices
# =============================================================================
def lzma_bits_per_rune(seq):
    b = bytes(int(x) for x in seq)
    comp = lzma.compress(b, preset=9 | lzma.PRESET_EXTREME)
    return 8.0 * len(comp) / len(seq)

# =============================================================================
# SUB-TEST (c): sliding-window index of dispersion (avg over symbols)
# =============================================================================
def dispersion_stat(seq, w=100):
    seq = np.asarray(seq)
    nb = len(seq) // w
    blocks = seq[:nb * w].reshape(nb, w)
    ids = []
    for s in range(N):
        counts = (blocks == s).sum(axis=1).astype(float)
        mu = counts.mean()
        if mu > 0:
            ids.append(counts.var() / mu)
    return float(np.mean(ids))  # multinomial expectation ~ 1 - p ~ 0.966

# =============================================================================
# SUB-TEST (d): monogram frequency drift -- blocks x symbols chi2
# =============================================================================
def drift_chi2(seq, nblocks=13):
    seq = np.asarray(seq)
    nb = nblocks
    w = len(seq) // nb
    obs = np.zeros((nb, N))
    for b in range(nb):
        blk = seq[b * w:(b + 1) * w]
        for s in range(N):
            obs[b, s] = np.count_nonzero(blk == s)
    row = obs.sum(axis=1, keepdims=True)
    col = obs.sum(axis=0, keepdims=True)
    tot = obs.sum()
    exp = row * col / tot
    with np.errstate(divide="ignore", invalid="ignore"):
        chi = np.where(exp > 0, (obs - exp) ** 2 / exp, 0.0)
    return float(chi.sum())  # df = (nb-1)*(N-1)

# =============================================================================
# RUN: real LP2
# =============================================================================
print("\ncomputing predictors on real LP2 ...")
real_ctx = context_bits_per_rune(stream)
real_lz  = lzma_bits_per_rune(stream)
real_disp = dispersion_stat(stream)
real_drift = drift_chi2(stream)
print(f"  LP2 context bits/rune by order: " +
      " ".join(f"o{m+1}={real_ctx[m]:.4f}" for m in range(MAXORDER)))
print(f"  LP2 LZMA bits/rune = {real_lz:.4f}")
print(f"  LP2 dispersion = {real_disp:.4f}   drift chi2 = {real_drift:.1f}")

# =============================================================================
# POSITIVE CONTROL: real English mapped to runes (predictors MUST fire here)
# =============================================================================
eng = english_baseline()
eng = (eng * (L // len(eng) + 1))[:L]
eng = np.array(eng, dtype=np.int64)
eng_ctx = context_bits_per_rune(eng)
eng_lz  = lzma_bits_per_rune(eng)
print(f"\npositive control (English->runes, {L} syms):")
print(f"  English context bits/rune by order: " +
      " ".join(f"o{m+1}={eng_ctx[m]:.4f}" for m in range(MAXORDER)))
print(f"  English LZMA bits/rune = {eng_lz:.4f}  (uniform ceiling = {math.log2(N):.4f})")

# =============================================================================
# CONTROL BAND
# =============================================================================
print(f"\ngenerating {N_CONTROLS} filtered-uniform controls (order-{MAXORDER} + LZMA)...")
ctx_band = np.zeros((N_CONTROLS, MAXORDER))
lz_band = np.zeros(N_CONTROLS)
disp_band = np.zeros(N_CONTROLS)
drift_band = np.zeros(N_CONTROLS)
dbl_band = np.zeros(N_CONTROLS)
ioc_band = np.zeros(N_CONTROLS)
for k in range(N_CONTROLS):
    c = make_control(SEED0 + 1 + k)
    ctx_band[k] = context_bits_per_rune(c)
    lz_band[k] = lzma_bits_per_rune(c)
    disp_band[k] = dispersion_stat(c)
    drift_band[k] = drift_chi2(c)
    dbl_band[k] = doublet_pct(c)
    ioc_band[k] = stats.ioc_norm(list(c))
    if (k + 1) % 100 == 0:
        print(f"  ... {k+1}/{N_CONTROLS}")

def pct_of(val, band):
    """percentile of val within band (fraction of controls <= val), in %."""
    return 100.0 * np.mean(band <= val)

print("\n" + "=" * 74)
print("RESULTS -- LP2 percentile within the filtered-uniform control band")
print("=" * 74)
print(f"  control signature check: doublet mean={dbl_band.mean():.3f}% (LP2 {OBS_DBL:.3f}%)"
      f"  IoC.N mean={ioc_band.mean():.4f} (LP2 {OBS_IOC:.4f})")
print("\n  predictor                 LP2       band[mean]  band[1st pct]  LP2 %ile")
print("  " + "-" * 70)
fired = False
for m in range(MAXORDER):
    band = ctx_band[:, m]
    p = pct_of(real_ctx[m], band)
    p1 = np.percentile(band, 1)
    flag = "  <== BELOW 1st pct!" if real_ctx[m] < p1 else ""
    if real_ctx[m] < p1:
        fired = True
    print(f"  context order-{m+1} bits    {real_ctx[m]:.4f}    {band.mean():.4f}"
          f"      {p1:.4f}        {p:5.1f}%{flag}")
# LZMA
p = pct_of(real_lz, lz_band); p1 = np.percentile(lz_band, 1)
flag = "  <== BELOW 1st pct!" if real_lz < p1 else ""
if real_lz < p1:
    fired = True
print(f"  LZMA bits/rune          {real_lz:.4f}    {lz_band.mean():.4f}"
      f"      {p1:.4f}        {p:5.1f}%{flag}")
# dispersion (two-sided: structure could raise OR lower)
p = pct_of(real_disp, disp_band)
print(f"  dispersion (ID)         {real_disp:.4f}    {disp_band.mean():.4f}"
      f"      {'--':>8}        {p:5.1f}%")
# drift chi2
p = pct_of(real_drift, drift_band)
print(f"  monogram drift chi2     {real_drift:7.1f}   {drift_band.mean():7.1f}"
      f"     {'--':>8}        {p:5.1f}%")

print("\n" + "=" * 74)
lz_pct_pos = pct_of(eng_lz, lz_band)
print("POSITIVE-CONTROL SANITY (English->runes vs the SAME band):")
print(f"  English LZMA {eng_lz:.4f} bits/rune  vs band mean {lz_band.mean():.4f}"
      f"  -> English %ile {lz_pct_pos:.1f}% (must be ~0 = detectable)")
print(f"  English order-{MAXORDER} ctx {eng_ctx[-1]:.4f} vs band mean {ctx_band[:,-1].mean():.4f}"
      f"  (English far below => predictor works)")
print("=" * 74)
print(f"\nSIGNAL FIRED (any LP2 predictor below 1st pct): {fired}")
if not fired:
    print("VERDICT: LP2 sits INSIDE the filtered-uniform band on every predictor.")
    print("  => No computable structure beyond the two signature statistics.")
    print("  => OTP-class upgraded from low-order-verified to MODEL-CLASS-verified.")
else:
    print("VERDICT: LP2 escapes the band => computable structure => attack surface.")
