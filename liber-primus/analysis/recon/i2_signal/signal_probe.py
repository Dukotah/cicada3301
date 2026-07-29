"""
NAIVE-OUTSIDER lens (iteration i2): treat the unsolved LP2 rune sequence as a
1-D signal, not text. Run DSP: FFT power spectrum, full autocorrelation,
spectral entropy, and hunt for hidden PERIODICITY / carrier the substitution
framing would ignore.

Compared corpora:
  A) LP2 unsolved  = krisyotam segments 0..54 (indices 0..28)
  B) solved plaintext runes = segment 56 (PARABLE, plaintext transliteration)
     -- the closest available "pre-encryption plaintext runes" for LP2.
  C) random control = uniform 29-symbol i.i.d. of matched length.

A significant periodic component in (A) but NOT in (C) -- and not merely an
artifact of the non-uniform symbol distribution -- would argue for a
transposition/interleave/keystream-generator rather than a one-time pad.

Bounded numpy. No solve claimed. Reports signal vs null honestly.
"""
import numpy as np
import json, sys, os

RUNES = list('ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ')
R2I = {r: i for i, r in enumerate(RUNES)}
N = 29

DATA = os.path.join(os.path.dirname(__file__), '..', '..', '..',
                    'data', 'krisyotam_runes.txt')

def load_segments():
    raw = open(DATA, encoding='utf-8').read()
    segs = raw.split('%')
    out = []
    for s in segs:
        idx = [R2I[c] for c in s if c in R2I]
        out.append(np.array(idx, dtype=float))
    return out

rng = np.random.default_rng(3301)

# ---------- DSP primitives ----------

def power_spectrum(x):
    """One-sided normalized power spectrum of a mean-removed integer series."""
    x = x - x.mean()
    if x.std() > 0:
        x = x / x.std()
    F = np.fft.rfft(x)
    P = (np.abs(F) ** 2) / len(x)
    freqs = np.fft.rfftfreq(len(x))
    return freqs, P

def autocorr(x, maxlag=None):
    x = x - x.mean()
    n = len(x)
    if maxlag is None:
        maxlag = n - 1
    # full autocorrelation via FFT
    f = np.fft.rfft(x, 2 * n)
    ac = np.fft.irfft(f * np.conj(f), 2 * n)[:n]
    if ac[0] != 0:
        ac = ac / ac[0]
    return ac[1:maxlag + 1]  # lags 1..maxlag, normalized so lag0=1

def spectral_entropy(P):
    """Shannon entropy of the (positive-freq) normalized power spectrum, in
    nats, and its ratio to the max (uniform => flat noise)."""
    p = P[1:]  # drop DC
    p = p / p.sum()
    p = p[p > 0]
    H = -(p * np.log(p)).sum()
    Hmax = np.log(len(p))
    return H, H / Hmax

# ---------- statistical test against a null ensemble ----------

def peak_significance(x, nperm=2000, categorical=True):
    """
    Test whether the tallest non-DC spectral peak of x exceeds what a shuffled
    version of the SAME multiset produces. Shuffling preserves the symbol
    histogram exactly, so a surviving peak means genuine ORDER/periodicity, not
    an artifact of the non-uniform alphabet distribution.
    Returns (observed_peak, peak_freq, p_value, peak_lag_period).
    """
    _, P = power_spectrum(x)
    Pnd = P[1:]                       # drop DC
    obs = Pnd.max()
    kobs = 1 + int(np.argmax(Pnd))    # freq bin index
    freqs = np.fft.rfftfreq(len(x))
    fpeak = freqs[kobs]
    period = (1.0 / fpeak) if fpeak > 0 else np.inf

    null_max = np.empty(nperm)
    xv = x.copy()
    for i in range(nperm):
        perm = rng.permutation(xv)
        _, Pp = power_spectrum(perm)
        null_max[i] = Pp[1:].max()
    p = (np.sum(null_max >= obs) + 1) / (nperm + 1)
    return float(obs), float(fpeak), float(p), float(period), float(null_max.mean()), float(null_max.max())

def autocorr_significance(x, nperm=2000, maxlag=None):
    """Largest |autocorr| over lags vs shuffle null (same histogram)."""
    ac = autocorr(x, maxlag)
    obs = np.abs(ac).max()
    lag = 1 + int(np.argmax(np.abs(ac)))
    null_max = np.empty(nperm)
    for i in range(nperm):
        perm = rng.permutation(x)
        acp = autocorr(perm, maxlag)
        null_max[i] = np.abs(acp).max()
    p = (np.sum(null_max >= obs) + 1) / (nperm + 1)
    return float(obs), int(lag), float(p), float(null_max.mean())

# ---------- run ----------

def analyze(name, x, nperm=2000):
    freqs, P = power_spectrum(x)
    H, Hratio = spectral_entropy(P)
    obs, fpeak, p_peak, period, null_mean, null_max = peak_significance(x, nperm)
    ac_obs, ac_lag, p_ac, ac_null_mean = autocorr_significance(x, nperm, maxlag=min(len(x)-1, 200))
    return {
        'name': name,
        'length': int(len(x)),
        'spectral_entropy_nats': round(H, 4),
        'spectral_entropy_ratio': round(Hratio, 4),   # ~1.0 => white noise
        'top_peak_power': round(obs, 4),
        'top_peak_freq': round(fpeak, 6),
        'top_peak_period': round(period, 3),
        'peak_p_value': round(p_peak, 5),
        'peak_null_mean': round(null_mean, 4),
        'peak_null_max': round(null_max, 4),
        'max_abs_autocorr': round(ac_obs, 5),
        'autocorr_lag': ac_lag,
        'autocorr_p_value': round(p_ac, 5),
        'autocorr_null_mean': round(ac_null_mean, 5),
    }

def main():
    segs = load_segments()
    unsolved = np.concatenate(segs[0:55])          # A: LP2 0..54
    solved_pt = segs[56]                             # B: PARABLE plaintext runes
    ctrl = rng.integers(0, N, size=len(unsolved)).astype(float)  # C

    results = {}
    print("Analyzing... (this runs permutation nulls; ~seconds each)")

    for name, x in [('LP2_unsolved_0-54', unsolved),
                    ('solved_plaintext_PARABLE', solved_pt),
                    ('random_control', ctrl)]:
        print(f"  {name}: len={len(x)}")
        results[name] = analyze(name, x, nperm=2000)

    # Also: per-page peak scan of the unsolved corpus, to catch a periodicity
    # that is per-page rather than global (interleave/generator would leave a
    # consistent per-page period).
    perpage = []
    for i in range(0, 55):
        x = segs[i]
        if len(x) < 16:
            continue
        obs, fpeak, p, period, nm, nx = peak_significance(x, nperm=500)
        perpage.append({'page': i, 'len': int(len(x)),
                        'peak_period': round(period, 2),
                        'peak_p': round(p, 4)})
    results['perpage_peak_scan'] = perpage

    # Bigram/lag-1 differential spectrum: sometimes a keystream generator shows
    # up in first differences mod 29 rather than raw values.
    diff = np.mod(np.diff(unsolved), N).astype(float)
    obs, fpeak, p, period, nm, nx = peak_significance(diff, nperm=2000)
    results['unsolved_firstdiff_mod29'] = {
        'top_peak_period': round(period, 3), 'peak_p_value': round(p, 5),
        'peak_null_mean': round(nm, 4)}

    out = os.path.join(os.path.dirname(__file__), 'results.json')
    with open(out, 'w') as f:
        json.dump(results, f, indent=2)

    # summary table
    print("\n=== SUMMARY ===")
    for k in ['LP2_unsolved_0-54', 'solved_plaintext_PARABLE', 'random_control']:
        r = results[k]
        print(f"{k:28s} Hratio={r['spectral_entropy_ratio']:.4f} "
              f"peakP={r['top_peak_power']:.2f} p={r['peak_p_value']:.4f} "
              f"period={r['top_peak_period']:.1f} | "
              f"maxACF={r['max_abs_autocorr']:.4f}@lag{r['autocorr_lag']} "
              f"ACFp={r['autocorr_p_value']:.4f}")
    sig = [p for p in perpage if p['peak_p'] < 0.05]
    print(f"\nper-page peaks with p<0.05: {len(sig)}/{len(perpage)}  "
          f"(expect ~{0.05*len(perpage):.1f} by chance)")
    for s in sig:
        print("   ", s)
    print("firstdiff mod29:", results['unsolved_firstdiff_mod29'])
    print(f"\nwrote {out}")

if __name__ == '__main__':
    main()
