"""Task 5: Primes/totients as TRANSPOSITION order or INTERRUPTER schedule.

(a) Prime-defined columnar transposition -> then mono/Vigenere decode + score.
(b) Prime/totient POSITIONS as interrupter schedule + short keyword Vigenere.

Non-additive use of number sequences. Additive streams already eliminated.
"""
import sys, os, itertools
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from lp import gematria as gp, score as _score, ciphers

SC = _score.default()
N = gp.N


def sieve_primes(count):
    primes, cand = [], 2
    while len(primes) < count:
        if all(cand % p for p in primes if p * p <= cand):
            primes.append(cand)
        cand += 1
    return primes


def totient(n):
    result, m, p = n, n, 2
    while p * p <= m:
        if m % p == 0:
            while m % p == 0:
                m //= p
            result -= result // p
        p += 1
    if m > 1:
        result -= result // m
    return result


def load_pages():
    data = open(os.path.join(os.path.dirname(__file__), "..", "..",
                "data", "krisyotam_runes.txt"), encoding="utf-8").read()
    pages = []
    for p in data.split('%'):
        idx = gp.runes_to_indices(p)
        if len(idx) >= 40:
            pages.append(idx)
    return pages[:-2]  # drop solved tail like attack.py


def idx_to_text(idxs):
    return gp.indices_to_translit(idxs)


# ----------------------------------------------------------- TRANSPOSITION
def columnar_order_from_seq(ncols, seq):
    """Produce a column-read order: sort columns by the seq value (stable)."""
    keys = [seq[i] for i in range(ncols)]
    return sorted(range(ncols), key=lambda c: (keys[c], c))


def columnar_transpose_decrypt(idxs, ncols, order):
    """Standard columnar transposition decrypt: ciphertext was read off by
    columns in `order`; reconstruct the row-wise grid."""
    n = len(idxs)
    nrows = (n + ncols - 1) // ncols
    # number of full cells; last row may be short
    n_full = n  # actual chars
    # column lengths: columns 0..(n%ncols-1) have nrows, rest nrows-1 (if ragged)
    rem = n % ncols
    col_len = [nrows if (rem == 0 or c < rem) else nrows - 1 for c in range(ncols)]
    # ciphertext was written column-by-column in `order`
    grid = [[None] * ncols for _ in range(nrows)]
    pos = 0
    for c in order:
        for r in range(col_len[c]):
            grid[r][c] = idxs[pos]
            pos += 1
    out = []
    for r in range(nrows):
        for c in range(ncols):
            if grid[r][c] is not None:
                out.append(grid[r][c])
    return out


def columnar_transpose_encrypt_inverse(idxs, ncols, order):
    """Alternative: treat ciphertext as the row-wise grid, read off by columns
    in order (i.e. the *other* transposition direction)."""
    n = len(idxs)
    nrows = (n + ncols - 1) // ncols
    grid = [[None] * ncols for _ in range(nrows)]
    pos = 0
    for r in range(nrows):
        for c in range(ncols):
            if pos < n:
                grid[r][c] = idxs[pos]
                pos += 1
    out = []
    for c in order:
        for r in range(nrows):
            if grid[r][c] is not None:
                out.append(grid[r][c])
    return out


def best_mono_shift(idxs):
    """Try all 29 monoalphabetic Caesar shifts + atbash, return best score."""
    best = (-99.0, None, None)
    for sign in (-1, 1):
        for k in range(N):
            dec = [(c + sign * k) % N for c in idxs]
            s = SC.score_norm(idx_to_text(dec))
            if s > best[0]:
                best = (s, f"caesar{sign:+d}_{k}", dec)
    # atbash then caesar
    ab = [(N - 1) - c for c in idxs]
    for k in range(N):
        dec = [(c + k) % N for c in ab]
        s = SC.score_norm(idx_to_text(dec))
        if s > best[0]:
            best = (s, f"atbash_caesar_{k}", dec)
    return best


def attack_transposition(pages):
    results = []
    primes = sieve_primes(100)
    tots = [totient(n) for n in range(2, 200)]
    seqs = {
        "primes": primes,
        "totients": tots,
        "prime_minus1": [p - 1 for p in primes],
    }
    for pi, idxs in enumerate(pages):
        best = (-99.0, None)
        for ncols in range(2, 21):
            for sname, seq in seqs.items():
                order = columnar_order_from_seq(ncols, seq)
                for direction, fn in (("dec", columnar_transpose_decrypt),
                                       ("enc", columnar_transpose_encrypt_inverse)):
                    trans = fn(idxs, ncols, order)
                    # raw score (transposition alone, no substitution)
                    sraw = SC.score_norm(idx_to_text(trans))
                    if sraw > best[0]:
                        best = (sraw, f"{sname}/cols{ncols}/{direction}/raw")
                    # then best mono shift
                    smono, mlabel, _ = best_mono_shift(trans)
                    if smono > best[0]:
                        best = (smono, f"{sname}/cols{ncols}/{direction}/{mlabel}")
        results.append((pi, best[0], best[1]))
    return results


# ----------------------------------------------------------- INTERRUPTER SCHED
def attack_interrupter_schedule(pages, keywords):
    """Use prime/totient POSITIONS as an interrupter schedule: at scheduled
    positions, the keystream is NOT advanced (the cipher rune is skipped/passed)
    OR the keyword index is held. We test: skip-advance interrupter where
    positions in the prime set cause the Vigenere key index to NOT advance."""
    results = []
    # build position sets up to max page length
    maxlen = max(len(p) for p in pages)
    primes = set(sieve_primes(maxlen * 2))
    # positions that are prime-indexed
    prime_pos = set(i for i in range(maxlen) if (i + 1) in primes)  # 1-based prime positions
    prime_pos0 = set(p for p in primes if p < maxlen)               # value-as-position
    tot_pos = set(i for i in range(maxlen) if totient(i + 2) % 2 == 0)  # placeholder, refine below

    schedules = {
        "prime_1based": prime_pos,
        "prime_value": prime_pos0,
    }

    for pi, idxs in enumerate(pages):
        best = (-99.0, None, "")
        for kw in keywords:
            key = gp.keyword_to_indices(kw)
            if not key:
                continue
            for sname, sched in schedules.items():
                for hold in (True, False):
                    # hold=True: at scheduled positions, hold key index (don't advance)
                    # hold=False: at scheduled positions, skip applying key (plain passes)
                    for sign in (-1, 1):
                        dec = []
                        ki = 0
                        for pos, c in enumerate(idxs):
                            if pos in sched:
                                if hold:
                                    p = (c + sign * key[ki % len(key)]) % N
                                    # do NOT advance ki
                                    dec.append(p)
                                else:
                                    dec.append(c)  # interrupter: pass plain, advance? no
                            else:
                                p = (c + sign * key[ki % len(key)]) % N
                                dec.append(p)
                                ki += 1
                        s = SC.score_norm(idx_to_text(dec))
                        if s > best[0]:
                            best = (s, f"{kw}/{sname}/hold={hold}/sign={sign}",
                                    idx_to_text(dec)[:60])
        results.append((pi, best[0], best[1], best[2]))
    return results


if __name__ == "__main__":
    pages = load_pages()
    print(f"loaded {len(pages)} unsolved pages, lens={[len(p) for p in pages][:10]}...")

    print("\n=== (a) TRANSPOSITION (prime/totient column order) ===")
    tr = attack_transposition(pages)
    tr_sorted = sorted(tr, key=lambda x: -x[1])
    gbest = tr_sorted[0]
    for pi, s, label in tr_sorted[:8]:
        print(f"  p{pi:<2} {s:7.3f}  {label}")
    print(f"  GLOBAL BEST transposition: p{gbest[0]} {gbest[1]:.3f} {gbest[2]}")

    kws = ["DIVINITY", "CIRCUMFERENCE", "FIRFUMFERENCE", "WELCOME", "PILGRIM",
           "INSTAR", "EMERGENCE", "WISDOM", "CICADA", "PRIMES", "SACRED",
           "TRUTH", "MOBIUS", "KOAN", "SHADOW", "LIGHT", "VOID", "ANENDPARABLE",
           "ADHERENCE", "DECEPTION", "CONSUMPTION", "PRESERVATION"]
    print("\n=== (b) INTERRUPTER SCHEDULE + keyword Vigenere ===")
    ir = attack_interrupter_schedule(pages, kws)
    ir_sorted = sorted(ir, key=lambda x: -x[1])
    gbest2 = ir_sorted[0]
    for pi, s, label, txt in ir_sorted[:8]:
        print(f"  p{pi:<2} {s:7.3f}  {label}  {txt}")
    print(f"  GLOBAL BEST interrupter: p{gbest2[0]} {gbest2[1]:.3f} {gbest2[1]}")
    print(f"     text: {gbest2[3]}")
