"""Lane copy of the campaign7 R14 (wordsum_selfkey.py) and R15 (hill5_magic.py) decrypt logic.
Functions are copied verbatim from the archived scripts
(archive/branches-2026/claude_master-roadmap-libra-qk527u/liber-primus/analysis/campaign7/);
only the file-I/O wrappers (run(), json dump, prints, sys.path hacks, SC scorer) were removed; the text loader is
rebuilt on repo data/ files. Run with python -I from this directory."""
import os, sys
LPD = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, os.path.join(LPD, "src"))
from lp import gematria as gp  # noqa
N = gp.N
KRIS = os.path.join(LPD, "data", "krisyotam_runes.txt")


# ---------------------------------------------------------------- R14 wordsum_selfkey (verbatim)
def _totient(n):
    r, m, p = n, n, 2
    while p * p <= m:
        if m % p == 0:
            while m % p == 0:
                m //= p
            r -= r // p
        p += 1
    if m > 1:
        r -= r // m
    return r


def word_pages():
    """Pages as lists of words; each word = list of rune indices."""
    txt = open(KRIS, encoding="utf-8").read()
    pages = []
    for seg in txt.split("%"):
        words, cur = [], []
        for c in seg:
            if gp.is_rune(c):
                cur.append(gp.RUNE_TO_IDX[c])
            elif cur:
                words.append(cur)
                cur = []
        if cur:
            words.append(cur)
        if words:
            pages.append(words)
    return pages


def primesum(word):
    return sum(gp.PRIMES[i] for i in word)


def decrypt_variant(words, variant, sign, atb):
    def tf(c):
        return (N - 1 - c) if atb else c
    plain = []
    if variant == "W5":  # per-rune prime autokey
        flat = [i for w in words for i in w]
        prev = 0
        for c in flat:
            plain.append((tf(c) + sign * (gp.PRIMES[prev] % N)) % N)
            prev = c
        return plain
    k, cum = 0, 0
    for j, w in enumerate(words):
        dec = [(tf(c) + sign * k) % N for c in w]
        plain.extend(dec)
        if variant == "W1":
            k = primesum(w) % N
        elif variant == "W2":
            k = primesum(dec) % N
        elif variant == "W3":
            cum += primesum(w)
            k = cum % N
        elif variant == "W4":
            k = _totient(primesum(w)) % N
    return plain


# ---------------------------------------------------------------- R15 hill5_magic (verbatim)
MATRICES = {
    "M1_1033": [[272, 138, 341, 131, 151], [366, 199, 130, 320, 18],
                [226, 245, 91, 245, 226], [18, 320, 130, 199, 366],
                [151, 131, 341, 138, 272]],
    "M2_3301": [[434, 1311, 312, 278, 966], [204, 812, 934, 280, 1071],
                [626, 620, 809, 620, 626], [1071, 280, 934, 812, 204],
                [966, 278, 312, 1311, 434]],
    "M3_4x4":  [[3258, 3222, 3152, 3038], [3278, 3299, 3298, 2838],
                [3288, 3294, 3296, 2472], [4516, 1206, 708, 820]],
    "M1_phi":  [[289, 139, 341, 131, 151], [367, 199, 131, 425, 19],
                [227, 245, 91, 245, 227], [19, 425, 131, 199, 367],
                [151, 131, 341, 139, 289]],
    "M2_phi":  [[434, 1311, 313, 278, 967], [309, 841, 934, 281, 1071],
                [626, 933, 809, 933, 626], [1071, 281, 934, 841, 309],
                [967, 278, 313, 1311, 434]],
    "M3_phi":  [[3259, 3222, 3152, 3038], [3278, 3299, 3299, 2838],
                [4115, 3294, 3296, 2473], [4517, 1206, 709, 821]],
}


def mat_mod(M):
    return [[v % N for v in row] for row in M]


def mat_inv_mod(M):
    """Gaussian elimination mod prime N; returns inverse or None."""
    n = len(M)
    A = [row[:] + [1 if i == j else 0 for j in range(n)]
         for i, row in enumerate(M)]
    for col in range(n):
        piv = next((r for r in range(col, n) if A[r][col] % N), None)
        if piv is None:
            return None
        A[col], A[piv] = A[piv], A[col]
        inv = pow(A[col][col], N - 2, N)
        A[col] = [(v * inv) % N for v in A[col]]
        for r in range(n):
            if r != col and A[r][col]:
                f = A[r][col]
                A[r] = [(A[r][c] - f * A[col][c]) % N for c in range(2 * n)]
    return [row[n:] for row in A]


def transpose(M):
    return [list(r) for r in zip(*M)]


def apply_hill(idxs, M):
    n = len(M)
    out = []
    for b in range(0, len(idxs) - n + 1, n):
        block = idxs[b:b + n]
        out.extend(sum(M[r][c] * block[c] for c in range(n)) % N for r in range(n))
    return out


def load_pages():
    """run_stats.load_pages equivalent: krisyotam split on '%', gp.runes_to_indices per segment."""
    txt = open(KRIS, encoding="utf-8").read()
    pages = []
    for s in txt.split("%"):
        idxs = gp.runes_to_indices(s)
        if idxs:
            pages.append(idxs)
    return pages


def hill_variants():
    """(matrix, variant) -> mat, the four transforms built exactly as run() builds them."""
    out = {}
    for mname, Mraw in MATRICES.items():
        M = mat_mod(Mraw)
        Minv = mat_inv_mod([r[:] for r in M])
        variants = {"M": M, "MT": transpose(M)}
        if Minv is not None:
            variants["Minv"] = Minv
            MTinv = mat_inv_mod(transpose(M))
            if MTinv is not None:
                variants["MTinv"] = MTinv
        for vn, mat in variants.items():
            out[(mname, vn)] = mat
    return out
