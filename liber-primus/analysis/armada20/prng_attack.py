"""Task 6: Cicada constants as cypherpunk-PRNG seeds.
Seed BBS / LCG / Mersenne-Twister with Cicada constants; generate keystreams.
Test each BOTH as a bounded additive stream (mod 29) AND as an interrupter
schedule driving a short keyword Vigenere.
"""
import sys, os, random, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from lp import gematria as gp
from lp import score as scoremod
from lp import ciphers

Q = scoremod.default()
N = 29

# ---- load pages ----
RAW = open(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'krisyotam_runes.txt')).read()
PAGES = RAW.split('%')
# unsolved LP2 pages 0-55; keep pages with enough runes
PAGE_IDX = [(i, gp.runes_to_indices(p)) for i, p in enumerate(PAGES)]
PAGE_IDX = [(i, idx) for i, idx in PAGE_IDX if len(idx) >= 40]

# Concatenate a representative test set: a few mid-size pages for additive test.
# For additive stream the keystream is position-indexed per page (restart each page),
# but also test continuous (one long stream over all pages concatenated).

# ---- Cicada constants ----
CONSTANTS = {
    '3301': 3301,
    '1033': 1033,
    '1595277641': 1595277641,
    '509': 509,
    '311': 311,            # 3301 reversed-ish / known cicada number
    '7': 7,
    '13': 13,
    '29': 29,
    '845145127': 845145127,  # 3301-related composite sometimes cited
    'feedface': 0xfeedface,
}

# ---- PRNG generators yielding mod-29 values and raw values ----
def bbs_stream(seed, length, p=None, q=None):
    """Blum-Blum-Shub. n=p*q with p,q = 3 mod 4. Output: parity bits packed,
    but we'll take x mod 29 each step (common simplification)."""
    # default Blum primes
    if p is None: p = 1000003 if False else 100000007  # placeholder
    # Use well-known small Blum primes scaled; choose p,q congruent 3 mod 4
    p = 30000000091  # check 3 mod4
    q = 40000000003
    while p % 4 != 3: p += 1
    while q % 4 != 3: q += 1
    n = p * q
    x = (seed * seed) % n
    if x in (0, 1): x = (seed + 2) ** 2 % n
    out = []
    for _ in range(length):
        x = (x * x) % n
        out.append(x % N)
    return out

def lcg_stream(seed, length, a=1103515245, c=12345, m=2**31):
    """glibc-style LCG."""
    out = []
    x = seed % m
    for _ in range(length):
        x = (a * x + c) % m
        out.append(x % N)
    return out

def lcg_stream2(seed, length, a=6364136223846793005, c=1442695040888963407, m=2**64):
    """PCG/Knuth MMIX LCG."""
    out = []
    x = seed % m
    for _ in range(length):
        x = (a * x + c) % m
        out.append((x >> 33) % N)
    return out

def mt_stream(seed, length):
    r = random.Random(seed)
    return [r.randrange(N) for _ in range(length)]

def mt_stream_bits(seed, length):
    """MT producing 0/1 for interrupter schedule via bit."""
    r = random.Random(seed)
    return [r.randrange(2) for _ in range(length)]

GENS = {
    'bbs': bbs_stream,
    'lcg_glibc': lcg_stream,
    'lcg_mmix': lcg_stream2,
    'mt': mt_stream,
}

# ---- additive test ----
def test_additive(genfn, seed, label, results):
    # continuous stream over each page independently (restart) and combined
    for mode in ('perpage', 'continuous'):
        if mode == 'continuous':
            total = sum(len(idx) for _, idx in PAGE_IDX)
            stream = genfn(seed, total)
            pos = 0
            allplain = []
            for _, idx in PAGE_IDX:
                seg = stream[pos:pos+len(idx)]
                pos += len(idx)
                for sign in (-1, +1):
                    pass
            # score with sign -1 and +1 separately over whole concat
            for sign in (-1, 1):
                pos = 0; plain = []
                for _, idx in PAGE_IDX:
                    seg = stream[pos:pos+len(idx)]; pos += len(idx)
                    plain += [(c + sign*seg[j]) % N for j, c in enumerate(idx)]
                txt = gp.indices_to_translit(plain)
                sc = Q.score_norm(txt)
                results.append((sc, f"{label}|add|{mode}|sign{sign}", txt[:60]))
        else:
            for sign in (-1, 1):
                plain = []
                for _, idx in PAGE_IDX:
                    seg = genfn(seed, len(idx))
                    plain += [(c + sign*seg[j]) % N for j, c in enumerate(idx)]
                txt = gp.indices_to_translit(plain)
                sc = Q.score_norm(txt)
                results.append((sc, f"{label}|add|{mode}|sign{sign}", txt[:60]))

# ---- interrupter schedule test ----
# A short keyword Vigenere where the PRNG decides which positions are
# interrupters (key does not advance). We threshold the PRNG output.
SHORT_KEYS = ['DIVINITY', 'CICADA', 'PRIMES', 'WELCOME', 'PILGRIM', 'CIRCUMFERENCE',
              'INSTAR', 'ADHERENCE', 'KOAN', 'WISDOM', 'TRUTH', 'AETHEREAL']

def test_interrupter(genfn, seed, label, results, density=0.1):
    for kw in SHORT_KEYS:
        try:
            key = gp.keyword_to_indices(kw)
        except Exception:
            continue
        for sign in (-1, 1):
            plain = []
            for _, idx in PAGE_IDX:
                sched = genfn(seed, len(idx))
                # interrupter if prng value mod (1/density) == 0  -> roughly density fraction
                thr = max(1, int(round(1/density)))
                k = 0
                for j, c in enumerate(idx):
                    if sched[j] % thr == 0:
                        # interrupter: skip keystream advance, output ciphertext as-is?
                        # convention: interrupter position is a null -> keep symbol, don't advance key
                        plain.append(c)  # passthrough
                        continue
                    p = (c + sign*key[k % len(key)]) % N
                    plain.append(p)
                    k += 1
            txt = gp.indices_to_translit(plain)
            sc = Q.score_norm(txt)
            results.append((sc, f"{label}|int|{kw}|sign{sign}|d{density}", txt[:60]))

def main():
    results = []
    for cname, cval in CONSTANTS.items():
        for gname, gfn in GENS.items():
            lab = f"{gname}:{cname}"
            try:
                test_additive(gfn, cval, lab, results)
            except Exception as e:
                results.append((-999, lab+'|add|ERR', str(e)[:40]))
            try:
                test_interrupter(gfn, cval, lab, results, density=0.1)
                test_interrupter(gfn, cval, lab, results, density=0.2)
            except Exception as e:
                results.append((-999, lab+'|int|ERR', str(e)[:40]))
    results.sort(reverse=True)
    print("=== TOP 30 ===")
    for sc, lab, txt in results[:30]:
        print(f"{sc:7.3f}  {lab:45s}  {txt}")
    # baseline random for reference
    import statistics
    print("\ntotal configs:", len(results))
    best = results[0]
    out = {'best_score': best[0], 'best_label': best[1], 'best_text': best[2],
           'top': [(s,l,t) for s,l,t in results[:30]]}
    json.dump(out, open(os.path.join(os.path.dirname(__file__), 'prng_results.json'), 'w'), indent=2)

if __name__ == '__main__':
    main()
