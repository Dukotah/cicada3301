"""ITER-7 GAME-THEORIST: doubling-restoration oracle with PER-SEGMENT KEY RESET.

Hypothesis under test: Cicada re-seeds the keystream at structural cleartext
boundaries (page '%', line '/', clause '.'). A continuous-keystream assumption
masks a per-segment pad. Using the PLAINTEXT-BLIND doubling-restoration oracle,
restart the generator index at each boundary and measure per-segment restoration.

Oracle validation (see reset_oracle_validate output): on synthetic English
enciphered with a totient pad, correct decrypt restores ratio 0.15 while wrong
pads sit at 0.55-1.0. Oracle is real at length >~300; noisy below ~120.

The doubling ratio = observed adjacent-equal / expected-under-unigram. English
~0.15, random pad ~0.85-1.0.
"""
import sys, os, json, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'liber-primus', 'src'))
from lp import ciphers, gematria as gp
from collections import Counter

RUNE_LO, RUNE_HI = 0x16A0, 0x16FF
N = gp.N


def is_rune(ch):
    return RUNE_LO <= ord(ch) <= RUNE_HI


def doubling_ratio(idxs):
    n = len(idxs)
    if n < 3:
        return None
    obs = sum(1 for i in range(1, n) if idxs[i] == idxs[i - 1])
    c = Counter(idxs)
    tot = len(idxs)
    p2 = sum((v / tot) ** 2 for v in c.values())
    exp = (n - 1) * p2
    return obs / exp if exp > 0 else None


def bigram_plausibility(idxs):
    """Plaintext-blind: fraction of adjacent pairs that are 'common English-ish'
    is not computable without a PT model; instead use a language-agnostic
    proxy = normalized bigram entropy. English index streams have LOWER
    conditional entropy than random. Return H(x_i | x_{i-1}) in bits."""
    n = len(idxs)
    if n < 20:
        return None
    from math import log2
    pair = Counter()
    uni = Counter()
    for i in range(1, n):
        pair[(idxs[i - 1], idxs[i])] += 1
        uni[idxs[i - 1]] += 1
    H = 0.0
    tot = sum(pair.values())
    for (a, b), c in pair.items():
        p_ab = c / tot
        p_b_given_a = c / uni[a]
        H -= p_ab * log2(p_b_given_a)
    return H


# ------------------------------------------------------------- generators
def gen_totient(length, start=0):
    return ciphers.prime_totient_stream(length, start=start)


def gen_totient_int(length, start=2):
    return ciphers.totient_stream(length, start=start)


def gen_prime(length, start=0):
    return ciphers.prime_stream(length, start=start)


def _fib(length):
    out = [1, 1]
    while len(out) < length + 1:
        out.append(out[-1] + out[-2])
    return [out[i] % N for i in range(length)]


def gen_fib(length, start=0):
    full = _fib(length + start)
    return full[start:start + length]


GENERATORS = {
    'totient(prime-1)': gen_totient,
    'totient(int)': gen_totient_int,
    'prime': gen_prime,
    'fibonacci': gen_fib,
}


# ------------------------------------------------------------- segmentation
def load_pages():
    raw = open(os.path.join(os.path.dirname(__file__), '..', '..', '..',
               'liber-primus', 'data', 'krisyotam_runes.txt'),
               encoding='utf-8').read()
    return raw.split('%')


def segments_by_boundary(raw_text, boundary):
    """Split a raw page-chunk string into segments at the boundary char,
    returning list of rune-index lists (non-runes dropped)."""
    if boundary == 'none':
        chunks = [raw_text]
    else:
        chunks = raw_text.split(boundary)
    out = []
    for ch in chunks:
        idxs = [gp.RUNE_TO_IDX[c] for c in ch if c in gp.RUNE_TO_IDX]
        if idxs:
            out.append(idxs)
    return out


def decrypt_segment(idxs, genfn, sign=-1):
    stream = genfn(len(idxs))
    return [(c + sign * stream[i]) % N for i, c in enumerate(idxs)]


# ------------------------------------------------------------- main attack
def run():
    pages = load_pages()
    unsolved = '%'.join(pages[i] for i in range(55))  # pages 0-54 as one blob w/ % kept? no
    # keep page structure: process page-by-page so '%' reset is meaningful
    results = {}

    # aggregate raw baseline
    all_ct = []
    for i in range(55):
        all_ct += [gp.RUNE_TO_IDX[c] for c in pages[i] if c in gp.RUNE_TO_IDX]
    raw_ratio = doubling_ratio(all_ct)
    raw_bg = bigram_plausibility(all_ct)

    ENGLISH_TARGET = 0.15   # from AN-END/PARABLE + synthetic validation
    ENGLISH_BAND = (0.10, 0.40)

    rows = []
    for boundary in ('none', '/', '.', '%_page'):
        for gname, genfn in GENERATORS.items():
            # collect decrypted stream across all pages 0-54 with per-segment reset
            dec_all = []
            for i in range(55):
                page_raw = pages[i]
                if boundary == '%_page':
                    segs = segments_by_boundary(page_raw, 'none')  # reset per page
                else:
                    segs = segments_by_boundary(page_raw, boundary)
                for seg in segs:
                    dec_all += decrypt_segment(seg, genfn)
            r = doubling_ratio(dec_all)
            bg = bigram_plausibility(dec_all)
            rows.append({
                'boundary': boundary, 'generator': gname,
                'doubling_ratio': round(r, 4), 'bigram_H_bits': round(bg, 4),
                'n': len(dec_all),
            })

    # controls: random-key decrypt band at full length, and shuffled-pad
    ctrl = []
    for s in range(200):
        random.seed(s)
        rk = [random.randrange(N) for _ in all_ct]
        rp = [(c - rk[i]) % N for i, c in enumerate(all_ct)]
        ctrl.append(doubling_ratio(rp))
    ctrl.sort()
    control_band = {
        'mean': round(sum(ctrl) / len(ctrl), 4),
        'p5': round(ctrl[10], 4), 'p95': round(ctrl[189], 4),
        'min': round(ctrl[0], 4),
    }

    results = {
        'raw_ct_doubling_ratio': round(raw_ratio, 4),
        'raw_ct_bigram_H_bits': round(raw_bg, 4),
        'english_target_ratio': ENGLISH_TARGET,
        'english_band': ENGLISH_BAND,
        'random_control_band': control_band,
        'cells': rows,
    }

    # find best cell = closest doubling ratio to ENGLISH_TARGET that also BEATS raw
    def score(row):
        return abs(row['doubling_ratio'] - ENGLISH_TARGET)
    best = min(rows, key=score)
    results['best_cell'] = best
    results['best_beats_raw'] = best['doubling_ratio'] < raw_ratio
    results['note'] = ('raw ct already at %.3f which is INSIDE the english band; '
                       'any decrypt must be judged vs whether it moves TOWARD 0.15 '
                       'AND out of the random band, not merely low.' % raw_ratio)
    return results


if __name__ == '__main__':
    res = run()
    print(json.dumps(res, indent=2))
    out = os.path.join(os.path.dirname(__file__), 'reset_results.json')
    with open(out, 'w') as f:
        json.dump(res, f, indent=2)
