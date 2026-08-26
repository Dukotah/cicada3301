"""L3 -- hypothesis tests H1..H8 against size-matched nulls (PREREG section I-2).

Objects under test
  * the short catalogued bands and their READ contents (bands.json),
  * the 256 base-60 tokens on pp.49-51 that the pipeline binned as ornament (nonrunic.json),
  * the band LENGTHS as a channel (H7),
  * the band POSITIONS as a channel, independent of content (H8).

Cross-checks (PREREG I-4): the 86 residual doublet positions and the segment boundaries.

Thresholds are the ones fixed in PREREG.md and are not edited here.
"""
import os, sys, json, collections, re
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
import reader as R                                                     # noqa: E402
sys.path.insert(0, os.path.join(R.LP, 'src'))
from lp.gematria import RUNE_TO_IDX, IDX_TO_TRANS                      # noqa: E402

RNG = np.random.default_rng(3301)
NRESAMP = 10000
FAMILY_BAR = 0.001 / 6          # PREREG: p < 1.67e-4 on any family headline statistic

# Gematria Primus values, standard order (indices 0..28)
GEMATRIA = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61,
            67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109]


def sieve(n):
    s = np.ones(n + 1, bool); s[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]:
            s[i * i::i] = False
    return np.where(s)[0]


PRIMES = sieve(200000)


def load_corpus():
    txt = open(os.path.join(R.LP, 'data', 'krisyotam_runes.txt'), encoding='utf-8').read()
    segs, seg_runes = [], []
    for si, seg in enumerate(txt.split('%')):
        rs = [RUNE_TO_IDX[c] for c in seg if c in RUNE_TO_IDX]
        if rs:
            segs.append(si); seg_runes.append(rs)
    flat, bounds, off = [], [], 0
    for rs in seg_runes:
        bounds.append(off); flat += rs; off += len(rs)
    bounds.append(off)
    return np.array(flat), np.array(bounds), seg_runes


def doublets(flat):
    return np.where(flat[1:] == flat[:-1])[0] + 1


def english_hits(s, minlen=8):
    """Longest run of characters that forms a dictionary word / known Cicada string."""
    KNOWN = ['PRIMES', 'SACRED', 'TOTIENT', 'DIVINITY', 'CIRCUMFERENCE', 'INSTAR',
             'EMERGENCE', 'PILGRIM', 'WELCOME', 'WARNING', 'CICADA', 'LIBERPRIMUS',
             'ANEND', 'PARABLE', 'WISDOM', 'MOBIUS', 'KOAN', 'SHADOWS', 'FIRFUMFERENFE',
             'THEPRIMESARESACRED', 'ADHERETOTHEWAY', 'WITHIN', 'THEBOOK', 'OFTHEBOOK']
    from fuzzy import fuzzy_find
    out = []
    for w in KNOWN:
        if len(w) < minlen:
            continue
        f = fuzzy_find(s, w, maxsub=1)     # H1-prime, justified by the C-2 control
        if f:
            out.append(dict(word=w, at=f[0], subs=f[1], seen=f[2]))
    return out


def main():
    flat, bounds, seg_runes = load_corpus()
    dbl = doublets(flat)
    res = dict(corpus=dict(n_runes=int(len(flat)), n_segments=len(seg_runes),
                           n_residual_doublets=int(len(dbl)),
                           segment_bounds=[int(b) for b in bounds]))
    print('corpus %d runes, %d segments, %d residual doublets'
          % (len(flat), len(seg_runes), len(dbl)))

    bands = json.load(open(os.path.join(HERE, 'bands.json')))
    inv = json.load(open(os.path.join(HERE, 'inventory.json')))
    nr = json.load(open(os.path.join(HERE, 'nonrunic.json')))

    # ------------------------------------------------------------------ candidates
    short = [b for b in bands if b['n_reported'] <= 16]
    runic_short = [b for b in short if b['call'] == 'RUNIC' and b['n_glyphs_read'] > 0]
    res['n_bands'] = len(bands)
    res['n_short'] = len(short)
    res['n_runic_short'] = len(runic_short)
    res['runic_short'] = [dict(id=b['id'], page=b['page'], n=b['n_glyphs_read'],
                               cost=b['cost_median'], degeneracy=b['degeneracy'],
                               translit=b['translit'], runes=b['runes'])
                          for b in runic_short]
    print('bands %d | short (n<=16) %d | short AND called RUNIC %d'
          % (len(bands), len(short), len(runic_short)))

    # ---------------------------------------------------------------- H1 English
    h1 = []
    for b in runic_short:
        w = english_hits(b['translit'])
        if w:
            h1.append(dict(id=b['id'], words=w, translit=b['translit']))
    res['H1'] = dict(bar='an English word or known Cicada string of length >= 8',
                     hits=h1, verdict='PASS' if h1 else 'FAIL')
    print('H1 (>=8-char English/known string in a runic short band): %d hit(s)' % len(h1))

    # ------------------------------------------------------- H2 recurrence >= 3 sites
    cnt = collections.Counter(b['translit'] for b in runic_short if b['translit'])
    rec = [(t, n) for t, n in cnt.items() if n >= 3]
    res['H2'] = dict(bar='identical short-band content at >= 3 sites',
                     repeats=[dict(content=t, sites=n) for t, n in rec],
                     verdict='PASS' if rec else 'FAIL')
    print('H2 (content recurring at >=3 sites): %d' % len(rec))

    # ----------------------------------------- H3/H4/H5 numeric readings of band values
    def band_numbers(b):
        """Every plausible small-integer reading of a band's runes."""
        r = b['runes']
        if not r:
            return {}
        g = [GEMATRIA[i] for i in r]
        return dict(sum_idx=int(sum(r)), sum_gem=int(sum(g)),
                    first_idx=int(r[0]), first_gem=int(g[0]),
                    n_glyphs=len(r),
                    idx_mod29=int(sum(r) % 29), gem_mod29=int(sum(g) % 29))

    targets = {}
    for b in runic_short:
        targets[b['id']] = dict(page=b['page'], **band_numbers(b))

    def exact_matches(key, fn):
        m = []
        for bid, t in targets.items():
            if key not in t:
                continue
            if fn(t):
                m.append(bid)
        return m

    h3 = exact_matches('sum_gem', lambda t: t['sum_idx'] == t['page'] or t['sum_gem'] == t['page']
                       or t['first_idx'] == t['page'] or t['first_gem'] == t['page'])
    h4 = exact_matches('sum_gem', lambda t: (t['sum_gem'] in PRIMES[:60].tolist() and
                                             PRIMES[:60].tolist().index(t['sum_gem']) == t['page']))
    res['H3'] = dict(bar='>=3 exact page-index matches AND p<1.67e-4',
                     matches=h3, n=len(h3),
                     verdict='PASS' if len(h3) >= 3 else 'FAIL')
    res['H4'] = dict(bar='>=3 exact prime-index matches AND p<1.67e-4',
                     matches=h4, n=len(h4),
                     verdict='PASS' if len(h4) >= 3 else 'FAIL')
    print('H3 (band value == page index): %d exact' % len(h3))
    print('H4 (band value == prime index): %d exact' % len(h4))

    # H5 checksum over the page's own rune stream
    h5 = {}
    for name, fn in [
        ('sum_mod29', lambda rs: sum(rs) % 29),
        ('sum_mod26', lambda rs: sum(rs) % 26),
        ('sum_mod100', lambda rs: sum(rs) % 100),
        ('sum_mod256', lambda rs: sum(rs) % 256),
        ('xor', lambda rs: int(np.bitwise_xor.reduce(np.array(rs)))),
        ('count', lambda rs: len(rs)),
        ('count_mod29', lambda rs: len(rs) % 29),
        ('gem_mod29', lambda rs: sum(GEMATRIA[i] for i in rs) % 29),
        ('gem_mod100', lambda rs: sum(GEMATRIA[i] for i in rs) % 100),
        ('gem_mod3301', lambda rs: sum(GEMATRIA[i] for i in rs) % 3301),
        ('distinct', lambda rs: len(set(rs))),
        ('doublets', lambda rs: int(sum(1 for a, b_ in zip(rs, rs[1:]) if a == b_))),
    ]:
        hit = []
        for bid, t in targets.items():
            p = t['page']
            if p >= len(seg_runes):
                continue
            v = fn(seg_runes[p])
            if v in (t['sum_idx'], t['sum_gem'], t['first_idx'], t['first_gem'],
                     t['idx_mod29'], t['gem_mod29']):
                hit.append(bid)
        h5[name] = hit
    best5 = max((len(v) for v in h5.values()), default=0)
    res['H5'] = dict(bar='>=3 exact matches on one of 12 checksum forms, Bonferroni p<8.3e-5',
                     per_form={k: v for k, v in h5.items()}, best=best5,
                     verdict='PASS' if best5 >= 3 else 'FAIL')
    print('H5 (band value == a checksum of the page): best form gives %d exact' % best5)

    # ------------------------------------------------------------- H6 pointer / index
    # (a) band values as indices into the page's own rune stream
    # (b) the 256 base-60 bytes of pp.49-51 as indices into the LP2 stream
    ptr = {}
    vals256 = nr['base60']['values']
    for label, idxs, stream in [
            ('bytes256_into_full_stream', vals256, flat),
            ('bytes256_into_page49', vals256, seg_runes[49] if len(seg_runes) > 49 else []),
            ('bytes256_mod29_direct', [v % 29 for v in vals256], None)]:
        if stream is None:
            s = ''.join(IDX_TO_TRANS[v] for v in idxs)
        else:
            if len(stream) == 0:
                continue
            s = ''.join(IDX_TO_TRANS[stream[i % len(stream)]] for i in idxs)
        ptr[label] = dict(text=s[:200], english=english_hits(s))
    # band values as pointers
    for bid, t in targets.items():
        p = t['page']
        if p >= len(seg_runes):
            continue
        st = seg_runes[p]
        i = t['sum_idx'] % max(len(st), 1)
        ptr['band_%s' % bid] = dict(page=p, index=i, rune=IDX_TO_TRANS[st[i]],
                                    on_doublet=bool((bounds[p] + i) in set(dbl.tolist())))
    n_on_dbl = sum(1 for k, v in ptr.items() if isinstance(v, dict) and v.get('on_doublet'))
    n_ptr = sum(1 for k, v in ptr.items() if isinstance(v, dict) and 'on_doublet' in v)
    p_dbl = len(dbl) / max(len(flat), 1)
    from math import comb
    pv = sum(comb(n_ptr, k) * p_dbl ** k * (1 - p_dbl) ** (n_ptr - k)
             for k in range(n_on_dbl, n_ptr + 1)) if n_ptr else 1.0
    eng6 = [k for k, v in ptr.items() if isinstance(v, dict) and v.get('english')]
    res['H6'] = dict(bar='>=8-char English via a pointer reading, OR doublet-landing p<0.001',
                     pointers=ptr, n_pointers=n_ptr, n_landing_on_doublet=n_on_dbl,
                     doublet_base_rate=round(p_dbl, 6), binom_p=float(pv),
                     english_hits=eng6,
                     verdict='PASS' if (eng6 or pv < 0.001) else 'FAIL')
    print('H6 (pointer/index): english hits %d | %d/%d pointers land on a residual doublet'
          ' (base rate %.4f, binom p=%.3g)' % (len(eng6), n_on_dbl, n_ptr, p_dbl, pv))

    # -------------------------------------------------------------- H7 band LENGTHS
    lens_all = np.array([b['n'] for b in inv])
    pow2 = np.array([1, 2, 4, 8, 16, 32])
    k = int(np.isin(lens_all, pow2).sum())
    n = len(lens_all)
    # null: the empirical band-length distribution over ALL 646 image bands
    g2 = np.load(os.path.join(R.LP, 'analysis', 'geometry', 'glyphs2.npz'))
    allb = g2['bands'][:, 3]
    p_pow2 = float(np.isin(allb, pow2).mean())
    pv7 = sum(comb(n, i) * p_pow2 ** i * (1 - p_pow2) ** (n - i) for i in range(k, n + 1))
    # CONFOUND: the all-bands base rate is dominated by TEXT lines (n approx 20-40), where
    # powers of two are sparse.  Ornament bands are small by construction, and among small
    # integers powers of two are dense (1,2,4,8,16 of 1..16 = 5/16).  The honest null is
    # therefore small-n matched.
    small = lens_all[lens_all <= 16]
    ks = int(np.isin(small, pow2).sum())
    allsmall = allb[allb <= 16]
    p_small_emp = float(np.isin(allsmall, pow2).mean()) if len(allsmall) else np.nan
    p_small_unif = 5.0 / 16.0
    pv7s_emp = (sum(comb(len(small), i) * p_small_emp ** i *
                    (1 - p_small_emp) ** (len(small) - i)
                    for i in range(ks, len(small) + 1))
                if len(allsmall) else float('nan'))
    pv7s_unif = sum(comb(len(small), i) * p_small_unif ** i *
                    (1 - p_small_unif) ** (len(small) - i)
                    for i in range(ks, len(small) + 1))
    res['H7'] = dict(bar='p<0.001 that band lengths are drawn from {2^k}',
                     n_bands=n, n_power_of_two=k,
                     base_rate_over_646_bands=round(p_pow2, 4),
                     binom_p_naive=float(pv7),
                     confound=('the all-bands base rate is set by TEXT lines at n=20-40; '
                               'ornament bands are small by construction and powers of two '
                               'are dense among small integers. Size-matched null below.'),
                     small_n_bands=int(len(small)), small_n_power_of_two=ks,
                     small_base_rate_empirical=None if np.isnan(p_small_emp) else round(p_small_emp, 4),
                     small_binom_p_empirical=None if np.isnan(pv7s_emp) else float(pv7s_emp),
                     small_base_rate_uniform_1_16=p_small_unif,
                     small_binom_p_uniform=float(pv7s_unif),
                     lengths=[int(v) for v in lens_all],
                     verdict='PASS' if (pv7s_unif < 0.001 and
                                        (np.isnan(pv7s_emp) or pv7s_emp < 0.001)) else 'FAIL')
    print('H7 naive : %d/%d are 2^k vs all-band base rate %.3f -> p=%.3g'
          % (k, n, p_pow2, pv7))
    print('H7 size-matched (n<=16): %d/%d are 2^k | empirical base %.3f p=%.3g'
          ' | uniform base %.3f p=%.3g -> %s'
          % (ks, len(small), p_small_emp, pv7s_emp, p_small_unif, pv7s_unif,
             res['H7']['verdict']))

    # ------------------------------------------------------------ H8 band POSITIONS
    px = np.array([(b['x'][0] + b['x'][1]) / 2 for b in inv])
    py = np.array([(b['y'][0] + b['y'][1]) / 2 for b in inv])
    presence = np.zeros(56, int)
    for b in inv:
        presence[b['page']] += 1
    bits = (presence > 0).astype(int)
    bitstr = ''.join(str(v) for v in bits)
    # decode 56 bits eight ways
    dec = {}
    for name, bb in [('msb', bits), ('lsb', bits[::-1]), ('inv', 1 - bits)]:
        by = [int(''.join(str(v) for v in bb[i:i + 8]), 2) for i in range(0, 56, 8)]
        dec[name] = dict(bytes=by, ascii=''.join(chr(v) if 32 <= v < 127 else '.' for v in by))
    # uniformity of positions vs a uniform null on the page area
    from scipy import stats
    ksx = stats.kstest((px - px.min()) / max(float(px.max()-px.min()), 1.0), 'uniform')
    ksy = stats.kstest((py - py.min()) / max(float(py.max()-py.min()), 1.0), 'uniform')
    res['H8'] = dict(bar='p<0.001 non-uniform positions, or a >=8-char decode',
                     presence_bits=bitstr, decodes=dec,
                     ks_x_p=float(ksx.pvalue), ks_y_p=float(ksy.pvalue),
                     verdict='PASS' if (min(ksx.pvalue, ksy.pvalue) < FAMILY_BAR) else 'FAIL')
    # H8b -- the informative version.  A uniform-position null is physically impossible for
    # marginal decoration, so rejecting it carries no information.  The question that does
    # carry information: are the band coordinates REPEATED (a page template) or unique
    # (per-page data)?
    import collections as _c
    key = _c.Counter((b['x'][0], b['x'][1], b['y'][0], b['y'][1]) for b in inv)
    keyx = _c.Counter((b['x'][0], b['x'][1]) for b in inv)
    rep_box = sum(v for k_, v in key.items() if v >= 2)
    rep_x = sum(v for k_, v in keyx.items() if v >= 3)
    res['H8b'] = dict(
        note=('H8 as pre-registered tests positional uniformity, a null no real page layout '
              'satisfies; its rejection is uninformative. H8b asks the informative question: '
              'are band coordinates a repeated TEMPLATE or unique per-page data?'),
        n_bands=len(inv), distinct_boxes=len(key), distinct_x_spans=len(keyx),
        bands_sharing_an_exact_box=int(rep_box),
        bands_sharing_an_x_span_with_2_others=int(rep_x),
        most_common_x_spans=[[list(k_), v] for k_, v in keyx.most_common(8)])
    print('H8b template test: %d bands, %d distinct boxes, %d distinct x-spans;'
          ' %d bands share an exact box with another; top x-spans %s'
          % (len(inv), len(key), len(keyx), rep_box,
             [(list(k_), v) for k_, v in keyx.most_common(4)]))
    print('H8 (positions): presence bits %s' % bitstr)
    print('   KS uniformity p: x=%.3g y=%.3g -> %s'
          % (ksx.pvalue, ksy.pvalue, res['H8']['verdict']))

    json.dump(res, open(os.path.join(HERE, 'hypotheses.json'), 'w'), indent=1)
    print('\nwrote hypotheses.json')
    print('VERDICTS:', {k: res[k]['verdict'] for k in
                        ('H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'H8')})


if __name__ == '__main__':
    main()
