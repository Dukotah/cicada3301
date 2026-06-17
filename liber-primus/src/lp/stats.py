"""Statistical cryptanalysis primitives over the 29-symbol Gematria Primus.

These measure how far a rune stream is from English and what kind of cipher it
implies. Key diagnostics:
  - IoC (index of coincidence), normalised by alphabet size: ~1.0 = random /
    polyalphabetic; >1.5 = monoalphabetic-English-like.
  - doublet rate: fraction of adjacent equal runes. Random over 29 = 1/29 =
    3.45%. English plaintext is HIGHER (LL, SS, EE...). A rate far BELOW random
    is the Liber Primus anomaly — a fingerprint of a cipher that suppresses
    doublets (running-key / autokey).
  - Kasiski: spacings between repeated trigrams hint at a polyalphabetic period.
"""
import collections
import math

from . import gematria as gp

N = gp.N


def ioc(idxs):
    """Raw index of coincidence."""
    if len(idxs) < 2:
        return 0.0
    counts = collections.Counter(idxs)
    num = sum(c * (c - 1) for c in counts.values())
    return num / (len(idxs) * (len(idxs) - 1))


def ioc_norm(idxs):
    """IoC * alphabet size. ~1.0 random, higher = more peaked (mono/English)."""
    return ioc(idxs) * N


def doublet_rate(idxs):
    if len(idxs) < 2:
        return 0.0
    d = sum(1 for a, b in zip(idxs, idxs[1:]) if a == b)
    return d / (len(idxs) - 1)


def doublet_count(idxs):
    return sum(1 for a, b in zip(idxs, idxs[1:]) if a == b)


def chi2_uniform(idxs):
    """Chi-square vs a uniform 29-symbol distribution. Low = flat (cipher-like)."""
    n = len(idxs)
    if n == 0:
        return 0.0
    exp = n / N
    counts = collections.Counter(idxs)
    return sum((counts.get(i, 0) - exp) ** 2 / exp for i in range(N))


def shannon_entropy(idxs):
    """Bits per symbol. Max = log2(29) ≈ 4.858."""
    n = len(idxs)
    if n == 0:
        return 0.0
    counts = collections.Counter(idxs)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def freq_table(idxs):
    counts = collections.Counter(idxs)
    n = len(idxs) or 1
    return {gp.IDX_TO_TRANS[i]: counts.get(i, 0) / n for i in range(N)}


def kasiski(idxs, min_len=3, max_gap_report=12):
    """Find repeated n-grams and the GCD-friendly spacings between them.
    Returns Counter of spacing -> frequency (small spacings are noise)."""
    spacings = collections.Counter()
    for L in (min_len, min_len + 1):
        seen = {}
        for i in range(len(idxs) - L + 1):
            g = tuple(idxs[i:i + L])
            if g in seen:
                spacings[i - seen[g]] += 1
            seen[g] = i
    return spacings


def summary(idxs):
    return {
        "n": len(idxs),
        "ioc_norm": round(ioc_norm(idxs), 4),
        "doublet_rate_pct": round(100 * doublet_rate(idxs), 3),
        "doublets": doublet_count(idxs),
        "chi2_uniform": round(chi2_uniform(idxs), 1),
        "entropy_bits": round(shannon_entropy(idxs), 4),
    }
