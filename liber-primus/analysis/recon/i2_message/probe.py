"""NAIVE-OUTSIDER probe: is there even a MESSAGE in the unsolved LP2 runes,
or are they deliberate high-entropy FILLER/decoration?

We do NOT re-run any substitution/keytext lane. We test the *null hypothesis*:
the unsolved runes are statistically indistinguishable from
  (A) a true random-pad enciphering of meaningful English plaintext, and
  (B) a true random-pad enciphering of MEANINGLESS filler (uniform noise),
each pushed through the SAME ~83% doublet-suppression filter the book uses.

If LP2 == filler-under-OTP and LP2 == message-under-OTP are BOTH true (LP2 sits
inside both null bands), then by construction content is unrecoverable from the
ciphertext alone -> "unknown / by design".

But we hunt for any residual a true random pad would NOT leave:
  - a bias in the marginal rune distribution (chi2)
  - a forbidden/over-represented bigram beyond the known doublet rule
  - a positional regularity (autocorrelation of the rune stream at lags)
  - a compressibility gap (does LP2 compress more than a true pad? -> structure)
  - conditional entropy H(X_i | X_{i-1}) below the filtered-pad expectation

Everything is compared to Monte-Carlo bands from many independent pads so a
"difference" only counts if it exceeds the natural spread of true random pads.

Run: PYTHONUTF8=1 python analysis/recon/i2_message/probe.py
"""
import os, sys, math, random, zlib, bz2, lzma, collections, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
from lp import gematria as gp, stats  # noqa

N = gp.N
RNG = random.Random(3301)

# ---------------------------------------------------------------------------
# Load the unsolved runes (pages 0..54; last two segments = AN END / PARABLE).
# ---------------------------------------------------------------------------
def load_unsolved():
    txt = open(os.path.join(ROOT, "data", "krisyotam_runes.txt"), encoding="utf-8").read()
    pages = [gp.runes_to_indices(s) for s in txt.split("%")]
    pages = [p for p in pages if p]
    return [i for p in pages[:-2] for i in p], pages

# ---------------------------------------------------------------------------
# English-runic plaintext (real meaning) from KJV, mapped to Gematria indices.
# ---------------------------------------------------------------------------
def english_plain(n):
    import re
    kjv = os.path.join(ROOT, "data", "kjv.txt")
    t = re.sub(r"[^A-Za-z]", "", open(kjv, encoding="utf-8", errors="ignore").read())
    return gp.keyword_to_indices(t[10000:])[:n]

# ---------------------------------------------------------------------------
# Doublet-suppression encipher: additive OTP with a soft no-repeat filter.
# The ledger pins the mechanism at ~83% suppression of would-be doublets.
# We reproduce it: draw a fresh random key symbol; if the emitted ciphertext
# rune equals the previous one, with prob p_suppress redraw the key so it does
# not (soft filter). This is the model that reproduces LP2's 0.66% doublets.
# ---------------------------------------------------------------------------
def otp_encipher(plain, rng, p_suppress=0.83):
    out = []
    prev = None
    for pt in plain:
        k = rng.randrange(N)
        c = (pt + k) % N
        if prev is not None and c == prev and rng.random() < p_suppress:
            # redraw key to avoid the doublet (soft)
            choices = [j for j in range(N) if (pt + j) % N != prev]
            k = rng.choice(choices)
            c = (pt + k) % N
        out.append(c)
        prev = c
    return out

def uniform_filler(n, rng, p_suppress=0.83):
    """Meaningless high-entropy filler with the SAME doublet filter but no
    plaintext at all (author just drew runes to fill the page)."""
    out = []
    prev = None
    for _ in range(n):
        c = rng.randrange(N)
        if prev is not None and c == prev and rng.random() < p_suppress:
            c = rng.choice([j for j in range(N) if j != prev])
        out.append(c)
        prev = c
    return out

# ---------------------------------------------------------------------------
# Fingerprint statistics
# ---------------------------------------------------------------------------
def cond_entropy(idxs):
    """H(X_i | X_{i-1}) in bits — sensitive to any first-order structure."""
    joint = collections.Counter(zip(idxs, idxs[1:]))
    prev = collections.Counter(idxs[:-1])
    n = len(idxs) - 1
    h = 0.0
    for (a, b), c in joint.items():
        p_ab = c / n
        p_b_given_a = c / prev[a]
        h -= p_ab * math.log2(p_b_given_a)
    return h

def compress_ratios(idxs):
    b = bytes(idxs)  # each symbol 0..28 fits a byte
    raw = len(b)
    return {
        "zlib": len(zlib.compress(b, 9)) / raw,
        "bz2":  len(bz2.compress(b, 9)) / raw,
        "lzma": len(lzma.compress(b, preset=9)) / raw,
    }

def bigram_chi2(idxs):
    """Chi2 of the 29x29 bigram table vs expectation under the marginals,
    EXCLUDING the diagonal (doublets) which we already know is suppressed.
    A real random pad has ~0 off-diagonal structure; a hidden non-additive
    combiner or leaked plaintext would show a forbidden/over bigram."""
    joint = collections.Counter(zip(idxs, idxs[1:]))
    marg1 = collections.Counter(idxs[:-1])
    marg2 = collections.Counter(idxs[1:])
    n = len(idxs) - 1
    chi = 0.0
    dof = 0
    for a in range(N):
        for b in range(N):
            if a == b:
                continue  # skip diagonal
            exp = marg1[a] * marg2[b] / n
            if exp < 1:
                continue
            obs = joint.get((a, b), 0)
            chi += (obs - exp) ** 2 / exp
            dof += 1
    return chi, dof

def autocorr(idxs, lags):
    """Fraction of positions where x[i]==x[i-lag], minus 1/N (random baseline),
    in units of the random std. Detects any periodic/positional regularity."""
    n = len(idxs)
    res = {}
    for L in lags:
        eq = sum(1 for i in range(L, n) if idxs[i] == idxs[i - L])
        m = n - L
        p = 1 / N
        z = (eq / m - p) / math.sqrt(p * (1 - p) / m)
        res[L] = round(z, 2)
    return res

def diff_hist(idxs):
    """Distribution of consecutive differences (x[i]-x[i-1]) mod N.
    Ledger notes a 'hole at 0' (the doublet deficit). Anything else non-flat?"""
    d = collections.Counter((b - a) % N for a, b in zip(idxs, idxs[1:]))
    n = len(idxs) - 1
    exp = n / N
    chi_nonzero = sum((d.get(k, 0) - exp) ** 2 / exp for k in range(1, N))
    return d, chi_nonzero

# ---------------------------------------------------------------------------
def fingerprint(idxs):
    s = stats.summary(idxs)
    ce = cond_entropy(idxs)
    cr = compress_ratios(idxs)
    bc, bdof = bigram_chi2(idxs)
    dh, dchi = diff_hist(idxs)
    return {
        "n": len(idxs),
        "ioc_norm": s["ioc_norm"],
        "doublet_pct": s["doublet_rate_pct"],
        "entropy": s["entropy_bits"],
        "cond_entropy": round(ce, 4),
        "chi2_uniform": s["chi2_uniform"],
        "bigram_chi2": round(bc, 1),
        "bigram_dof": bdof,
        "diff_chi2_nonzero": round(dchi, 1),
        "zlib": round(cr["zlib"], 4),
        "bz2": round(cr["bz2"], 4),
        "lzma": round(cr["lzma"], 4),
    }

def band(samples):
    """min..max and mean/std of a list of scalars."""
    return {
        "mean": round(statistics.mean(samples), 4),
        "std": round(statistics.pstdev(samples), 4),
        "min": round(min(samples), 4),
        "max": round(max(samples), 4),
    }

# ---------------------------------------------------------------------------
def main():
    unsolved, pages = load_unsolved()
    n = len(unsolved)
    print(f"unsolved runes: {n}")

    lp = fingerprint(unsolved)
    lp_ac = autocorr(unsolved, [1, 2, 3, 5, 7, 11, 13, 29, 41, 100])

    TRIALS = 200
    keys = ["ioc_norm", "doublet_pct", "entropy", "cond_entropy",
            "chi2_uniform", "bigram_chi2", "diff_chi2_nonzero",
            "zlib", "bz2", "lzma"]

    # Baseline A: real English plaintext under a true random pad (+filter)
    plain = english_plain(n)
    print(f"english plaintext runes available: {len(plain)}")
    msg_samples = {k: [] for k in keys}
    for t in range(TRIALS):
        rng = random.Random(1000 + t)
        ct = otp_encipher(plain, rng)
        fp = fingerprint(ct)
        for k in keys:
            msg_samples[k].append(fp[k])

    # Baseline B: meaningless uniform filler under the same doublet filter
    fil_samples = {k: [] for k in keys}
    for t in range(TRIALS):
        rng = random.Random(5000 + t)
        ct = uniform_filler(n, rng)
        fp = fingerprint(ct)
        for k in keys:
            fil_samples[k].append(fp[k])

    # Report
    out = []
    def P(*a):
        line = " ".join(str(x) for x in a)
        print(line); out.append(line)

    P("=" * 78)
    P("NAIVE-OUTSIDER: is there even a MESSAGE in the unsolved runes?")
    P("=" * 78)
    P(f"\nUnsolved corpus n={n}\n")
    P(f"{'stat':22s} {'LP2':>12} {'MSG-under-OTP band':>26} {'FILLER band':>26}  z_msg z_fil")
    P("-" * 118)
    for k in keys:
        mb = band(msg_samples[k])
        fb = band(fil_samples[k])
        zmsg = (lp[k] - mb["mean"]) / mb["std"] if mb["std"] > 0 else float("nan")
        zfil = (lp[k] - fb["mean"]) / fb["std"] if fb["std"] > 0 else float("nan")
        P(f"{k:22s} {lp[k]:>12} "
          f"{mb['min']:>10}..{mb['max']:<10} "
          f"{fb['min']:>10}..{fb['max']:<10} "
          f"{zmsg:>6.2f} {zfil:>6.2f}")

    P("\n-- Autocorrelation (z-score vs random 1/N) of LP2 rune stream --")
    P("  lag:z  " + "  ".join(f"{L}:{z}" for L, z in lp_ac.items()))

    P("\n-- Diff-histogram of LP2 (consecutive difference counts) --")
    dh, _ = diff_hist(unsolved)
    exp = (n - 1) / N
    P(f"  expected/cell ~ {exp:.1f}")
    P("  " + "  ".join(f"{k}:{dh.get(k,0)}" for k in range(N)))

    # verdict logic
    P("\n" + "=" * 78)
    P("VERDICT LOGIC")
    P("=" * 78)
    inside_msg = all(abs((lp[k] - band(msg_samples[k])["mean"]) /
                         (band(msg_samples[k])["std"] or 1e9)) < 4 for k in keys)
    inside_fil = all(abs((lp[k] - band(fil_samples[k])["mean"]) /
                         (band(fil_samples[k])["std"] or 1e9)) < 4 for k in keys)
    P(f"LP2 inside MESSAGE-under-OTP band (|z|<4 all stats): {inside_msg}")
    P(f"LP2 inside FILLER-under-OTP band  (|z|<4 all stats): {inside_fil}")

    # can we separate message-under-OTP from filler-under-OTP at all?
    P("\n-- Can the two hypotheses even be told apart post-filter? --")
    for k in keys:
        mb = band(msg_samples[k]); fb = band(fil_samples[k])
        overlap = not (mb["max"] < fb["min"] or fb["max"] < mb["min"])
        P(f"  {k:22s} msg[{mb['min']},{mb['max']}] fil[{fb['min']},{fb['max']}] "
          f"{'OVERLAP' if overlap else 'SEPARABLE'}")

    open(os.path.join(HERE, "probe_output.txt"), "w").write("\n".join(out) + "\n")
    print("\nwrote probe_output.txt")

if __name__ == "__main__":
    main()
