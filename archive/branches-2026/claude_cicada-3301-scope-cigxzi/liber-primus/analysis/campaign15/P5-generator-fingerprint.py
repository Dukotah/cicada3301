"""Campaign XV / P5 -- Generator-fingerprint suite.

Pin down HOW the filtered keystream was produced. Test the 'hand-generated pad'
loophole against a memoryless rejection-sampler null.

NULL (H0): the ciphertext is soft-filtered uniform noise -- each rune drawn iid
uniform over N=29, and when it equals the previous output it is resampled once
with probability s (soft ~83% adjacent-repeat suppression, campaign XI). This is
what a machine rejection-sampler leaves behind. s is pinned from LP2's own
doublet rate.

FOUR falsifiable tests, each reduced to a scalar and z-scored against a
200-sample control band of synthetic filtered-uniform streams (same L, same s):

  (1) Conditional next-rune distribution following each rune value. The resampler
      leaves each row = analytic prediction (uniform-over-28 with the current
      value suppressed). Fisher-Yates / shuffle-bag / swap leaves detectable
      under-dispersion. Statistic: total chi2 over all 29 conditional rows.
  (2) Windowed monogram chi2 dispersion sweep (windows 50..500). Machine
      multinomial = at-dispersion (mean chi2 ~ df). Shuffle-bag = UNDER-dispersed.
      Human = OVER-dispersed/biased. Statistic: mean windowed chi2 per window size.
  (3) Doublet-gap law: gaps between surviving doublets. Soft-iid predicts
      geometric. Statistic: KS distance of gaps vs fitted geometric + CoV.
  (4) Monogram frequency DRIFT across book order (fatigue/hand signature):
      regress per-page monogram chi2 on page index. Statistic: slope / Pearson r.

GATE: any deviation beyond the control band (|z|>~3) = a NEW exploitable
regularity + a generator fingerprint = attack surface. Full conformance = the
'hand-generated pad' loophole is formally closed, OTP verdict confirmed at the
generator level.

Reproduce:  PYTHONUTF8=1 python analysis/campaign15/P5-generator-fingerprint.py
"""
import os, sys, math
import numpy as np
from scipy import stats as sstats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
from lp import gematria as gp  # noqa

N = gp.N
RUNE = gp.RUNE_TO_IDX
raw = open(os.path.join(ROOT, "data", "krisyotam_runes.txt"), encoding="utf-8").read()
pages_raw = [p for p in raw.split("%") if any(ch in RUNE for ch in p)]
body_pages = pages_raw[:-2]
page_idx = [[RUNE[c] for c in p if c in RUNE] for p in body_pages]
page_lens = [len(p) for p in page_idx]
stream = np.array([i for pg in page_idx for i in pg], dtype=np.int64)
L = len(stream)

NCTRL = 200
SEED = 3301
rng = np.random.default_rng(SEED)

# --- pin s from LP2 doublet rate (analytic soft-filter relation) ---
d_obs = int(np.sum(stream[1:] == stream[:-1]))
p_d = d_obs / (L - 1)
# p_d = (1-s)/N + s/N^2  ->  s = ((1/N) - p_d) / ((1/N) - 1/N^2)
s_star = ((1.0 / N) - p_d) / ((1.0 / N) - 1.0 / N**2)
s_star = float(np.clip(s_star, 0.0, 1.0))

print("=" * 72)
print(f"CAMPAIGN XV  P5  generator-fingerprint -- L={L}, {len(page_idx)} pages, N={N}")
print(f"observed doublets={d_obs} ({100*p_d:.4f}%)  ->  pinned suppression s*={s_star:.4f}")
print(f"control band: {NCTRL} synthetic filtered-uniform streams (seed {SEED})")
print("=" * 72)


def gen_filtered_uniform(length, s, r):
    """Memoryless rejection sampler: iid uniform, resample once w.p. s on repeat."""
    out = np.empty(length, dtype=np.int64)
    draws = r.integers(0, N, size=length)
    resample = r.integers(0, N, size=length)
    coin = r.random(size=length)
    out[0] = draws[0]
    prev = out[0]
    for i in range(1, length):
        c = draws[i]
        if c == prev and coin[i] < s:
            c = resample[i]
        out[i] = c
        prev = c
    return out


# ======================================================================= TEST 1
# Conditional next-rune distribution: total chi2 over all 29 rows vs the
# analytic resampler prediction.
def cond_chi2(seq):
    # counts[v, w] = # of transitions v -> w
    a = seq[:-1]; b = seq[1:]
    counts = np.zeros((N, N), dtype=np.float64)
    np.add.at(counts, (a, b), 1.0)
    row_tot = counts.sum(axis=1)
    # analytic expected row distribution given prev=v:
    #   p(w!=v) = 1/N + s/N^2 ;  p(w=v) = (1-s)/N + s/N^2
    base = 1.0 / N + s_star / N**2
    diag = (1.0 - s_star) / N + s_star / N**2
    chi2 = 0.0
    for v in range(N):
        if row_tot[v] == 0:
            continue
        exp = np.full(N, base) * row_tot[v]
        exp[v] = diag * row_tot[v]
        # guard tiny expected
        chi2 += np.sum((counts[v] - exp) ** 2 / exp)
    return chi2


# ======================================================================= TEST 2
# Windowed monogram chi2 dispersion. For each window size, mean chi2 across
# non-overlapping windows.
WINS = [50, 100, 200, 300, 500]
def windowed_meanchi2(seq):
    res = {}
    for w in WINS:
        nwin = len(seq) // w
        vals = []
        exp = w / N
        for k in range(nwin):
            chunk = seq[k * w:(k + 1) * w]
            cnt = np.bincount(chunk, minlength=N)
            vals.append(np.sum((cnt - exp) ** 2 / exp))
        res[w] = float(np.mean(vals))
    return res


# ======================================================================= TEST 3
# Doublet-gap law. Gaps (in runes) between successive surviving doublets.
def doublet_gap_stats(seq):
    pos = np.where(seq[1:] == seq[:-1])[0]  # indices i where seq[i+1]==seq[i]
    if len(pos) < 5:
        return None
    gaps = np.diff(pos).astype(np.float64)
    mean_gap = gaps.mean()
    cov = gaps.std() / mean_gap  # geometric -> CoV ~ sqrt(1-p) ~ 1
    # fit geometric via mean, KS on the gap distribution (integer-ish, treat continuous)
    p_hat = 1.0 / mean_gap
    # KS vs geometric CDF F(x)=1-(1-p)^x
    xs = np.sort(gaps)
    cdf_emp = np.arange(1, len(xs) + 1) / len(xs)
    cdf_the = 1.0 - (1.0 - p_hat) ** xs
    ks = float(np.max(np.abs(cdf_emp - cdf_the)))
    return {"mean_gap": mean_gap, "cov": float(cov), "ks": ks, "n": len(gaps)}


# ======================================================================= TEST 4
# Monogram drift across book order: per-page monogram chi2 vs page index slope.
def drift_slope(seq, lens):
    idx = 0
    chi2s = []
    for w in lens:
        chunk = seq[idx:idx + w]; idx += w
        cnt = np.bincount(chunk, minlength=N)
        exp = w / N
        chi2s.append(np.sum((cnt - exp) ** 2 / exp))
    chi2s = np.array(chi2s)
    x = np.arange(len(chi2s), dtype=np.float64)
    slope, intercept, r, pval, se = sstats.linregress(x, chi2s)
    return {"slope": float(slope), "r": float(r), "p": float(pval)}


# ---- LP2 observed statistics ----
lp_t1 = cond_chi2(stream)
lp_t2 = windowed_meanchi2(stream)
lp_t3 = doublet_gap_stats(stream)
lp_t4 = drift_slope(stream, page_lens)

# ---- build control band ----
ctrl_t1 = np.empty(NCTRL)
ctrl_t2 = {w: np.empty(NCTRL) for w in WINS}
ctrl_t3_cov = np.empty(NCTRL)
ctrl_t3_ks = np.empty(NCTRL)
ctrl_t3_mean = np.empty(NCTRL)
ctrl_t4_slope = np.empty(NCTRL)
for j in range(NCTRL):
    c = gen_filtered_uniform(L, s_star, rng)
    ctrl_t1[j] = cond_chi2(c)
    wm = windowed_meanchi2(c)
    for w in WINS:
        ctrl_t2[w][j] = wm[w]
    g = doublet_gap_stats(c)
    ctrl_t3_cov[j] = g["cov"]; ctrl_t3_ks[j] = g["ks"]; ctrl_t3_mean[j] = g["mean_gap"]
    ctrl_t4_slope[j] = drift_slope(c, page_lens)["slope"]


def zscore(obs, arr):
    m, sd = float(np.mean(arr)), float(np.std(arr, ddof=1))
    z = (obs - m) / sd if sd > 0 else 0.0
    return m, sd, z


print("\n--- TEST 1: conditional next-rune distribution (total chi2, 29 rows) ---")
m, sd, z = zscore(lp_t1, ctrl_t1)
print(f"  LP2 chi2 = {lp_t1:.1f}   control {m:.1f} +/- {sd:.1f}   z = {z:+.2f}")
t1_z = z

print("\n--- TEST 2: windowed monogram chi2 dispersion (mean chi2/window) ---")
print(f"  {'win':>5} {'LP2':>9} {'ctrl_mean':>10} {'ctrl_sd':>8} {'z':>7}")
t2_zs = {}
for w in WINS:
    m, sd, z = zscore(lp_t2[w], ctrl_t2[w])
    t2_zs[w] = z
    print(f"  {w:5d} {lp_t2[w]:9.2f} {m:10.2f} {sd:8.2f} {z:+7.2f}")

print("\n--- TEST 3: doublet-gap law (geometric fit) ---")
mmean, sdmean, zmean = zscore(lp_t3["mean_gap"], ctrl_t3_mean)
mcov, sdcov, zcov = zscore(lp_t3["cov"], ctrl_t3_cov)
mks, sdks, zks = zscore(lp_t3["ks"], ctrl_t3_ks)
print(f"  n gaps = {lp_t3['n']}")
print(f"  mean_gap : LP2 {lp_t3['mean_gap']:.2f}  ctrl {mmean:.2f}+/-{sdmean:.2f}  z={zmean:+.2f}")
print(f"  CoV      : LP2 {lp_t3['cov']:.3f}  ctrl {mcov:.3f}+/-{sdcov:.3f}  z={zcov:+.2f}  (geom->1)")
print(f"  KS(geom) : LP2 {lp_t3['ks']:.3f}  ctrl {mks:.3f}+/-{sdks:.3f}  z={zks:+.2f}")
t3_z = zks

print("\n--- TEST 4: monogram drift across book order (per-page chi2 vs page#) ---")
m, sd, z = zscore(lp_t4["slope"], ctrl_t4_slope)
print(f"  LP2 slope = {lp_t4['slope']:+.4f}  (Pearson r={lp_t4['r']:+.3f}, p={lp_t4['p']:.3f})")
print(f"  control slope {m:+.4f} +/- {sd:.4f}   z = {z:+.2f}")
t4_z = z

# ---- verdict ----
all_z = [abs(t1_z)] + [abs(v) for v in t2_zs.values()] + [abs(zks), abs(zcov)] + [abs(t4_z)]
max_z = max(all_z)
fired = max_z > 3.0
print("\n" + "=" * 72)
print(f"max |z| across all fingerprint tests = {max_z:.2f}")
if fired:
    print("SIGNAL FIRED: a generator fingerprint deviates from the rejection-sampler")
    print("null -> NEW exploitable regularity / attack surface.")
else:
    print("FULL CONFORMANCE: LP2 sits inside the 200-sample filtered-uniform control")
    print("band on every test. The 'hand-generated pad' loophole is closed; the")
    print("keystream is statistically indistinguishable from a machine rejection")
    print("sampler. OTP verdict confirmed at the generator level.")
print("=" * 72)
