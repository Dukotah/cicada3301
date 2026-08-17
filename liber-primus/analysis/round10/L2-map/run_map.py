"""Round 10 lane L2-MAP - "its words are the map".

Runs every reading pre-registered in PREREG.md (G0, G1, M1-M6, M8) with its null
control, and writes results.json + a human table to stdout.

    python analysis/round10/L2-map/run_map.py            # everything
    python analysis/round10/L2-map/run_map.py G1 M4      # named readings only
"""
import os, sys, json, math, itertools, random
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mapcommon as M
from mapcommon import ng_score, eng_score, zscore, N

NNULL = 8
OUT = {}
LET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


def atbash(seq):
    return [N - 1 - x for x in seq]


def shifted(seq, k):
    return [(x + k) % N for x in seq]


# =====================================================================  G0 ==
def G0():
    d = M.parse()
    W = d['words']
    fl = M.flat(W)
    ct = list(np.frombuffer(open(os.path.join(M.ROOT, 'analysis', 'seed_sweep',
                                              'ct.bin'), 'rb').read(), np.uint8))
    res = dict(words=len(W), runes=len(fl), segments=len(d['pages']),
               lines=len(d['lines']),
               matches_ct_bin=(fl == ct),
               mean_word_len=round(len(fl) / len(W), 4))
    res['PASS'] = (len(W) == 2928 and len(fl) == 12956 and res['matches_ct_bin'])
    OUT['G0'] = res
    print('G0 parse gate:', json.dumps(res))
    if not res['PASS']:
        raise SystemExit('G0 FAILED - lane aborts')
    return d


# =====================================================================  G1 ==
def chi2(counts, expected):
    c = np.asarray(counts, float); e = np.asarray(expected, float)
    e = e * c.sum() / e.sum()
    return float(((c - e) ** 2 / e).sum())


def G1(d):
    from scipy import stats
    W = d['words']
    pages = d['pages']
    lines = [l for l in d['lines'] if l]
    pooled = M.flat(W)
    uni = np.bincount(pooled, minlength=N).astype(float)

    def dist(seq):
        return np.bincount(seq, minlength=N).astype(float)

    positions = {
        'word-initial':  [w[0] for w in W],
        'word-final':    [w[-1] for w in W],
        'line-initial':  [l[0] for l in lines],
        'line-final':    [l[-1] for l in lines],
        'page-initial':  [p[0] for p in pages],
    }
    nulls = [M.null_A(W, 900 + s) for s in range(NNULL)]
    rows = []
    for name, seq in positions.items():
        c = dist(seq)
        x_u = chi2(c, np.ones(N)); x_p = chi2(c, uni)
        p_u = 1 - stats.chi2.cdf(x_u, N - 1)
        p_p = 1 - stats.chi2.cdf(x_p, N - 1)
        # null: same positional extraction on shuffled-content words
        nx = []
        for nw in nulls:
            if name == 'word-initial':
                s2 = [w[0] for w in nw]
            elif name == 'word-final':
                s2 = [w[-1] for w in nw]
            else:
                # rebuild lines/pages from the shuffled flat stream, same lengths
                f2 = M.flat(nw); k = 0
                if name == 'page-initial':
                    s2 = []
                    for p in pages:
                        s2.append(f2[k]); k += len(p)
                else:
                    s2 = []
                    for l in lines:
                        s2.append(f2[k] if name == 'line-initial' else f2[k + len(l) - 1])
                        k += len(l)
            nx.append(chi2(dist(s2), uni))
        rows.append(dict(position=name, n=len(seq),
                         chi2_vs_uniform=round(x_u, 2), p_vs_uniform=float('%.3g' % p_u),
                         chi2_vs_unigram=round(x_p, 2), p_vs_unigram=float('%.3g' % p_p),
                         null_chi2_mean=round(float(np.mean(nx)), 2),
                         null_chi2_max=round(float(np.max(nx)), 2),
                         z_vs_null=round(zscore(x_p, nx), 2)))
    hit = any(r['p_vs_uniform'] < 1e-4 or r['p_vs_unigram'] < 1e-4 for r in rows)
    OUT['G1'] = dict(rows=rows, threshold='p < 1e-4 (Bonferroni 0.001/10)', HIT=hit)
    print('\nG1 word/line/page-boundary FORCING detector')
    for r in rows:
        print('   %-13s n=%5d  chi2/uni=%7.2f p=%8.3g | chi2/unigram=%7.2f p=%8.3g'
              '  null_mean=%7.2f  z=%+5.2f' %
              (r['position'], r['n'], r['chi2_vs_uniform'], r['p_vs_uniform'],
               r['chi2_vs_unigram'], r['p_vs_unigram'], r['null_chi2_mean'], r['z_vs_null']))
    print('   HIT =', hit)


# =====================================================================  M1 ==
def _acrostic_variants(seq):
    """29 shifts x {id, atbash} x {fwd, rev}"""
    for base, bn in ((seq, 'id'), (atbash(seq), 'atbash')):
        for rev, rn in ((base, 'fwd'), (base[::-1], 'rev')):
            for k in range(N):
                yield f'{bn}/{rn}/+{k}', shifted(rev, k)


def _best_acrostic(streams):
    best = (-99.0, None)
    for sname, seq in streams.items():
        if len(seq) < 24:
            continue
        for vname, v in _acrostic_variants(seq):
            s = ng_score(v)
            if s > best[0]:
                best = (s, f'{sname} {vname}')
    return best


def M1(d):
    W = d['words']
    Wf = [[r for r in w if r != M.F_IDX] or [w[0]] for w in W]   # F stripped

    def streams_of(words):
        return {'first-of-word': [w[0] for w in words],
                'last-of-word': [w[-1] for w in words]}

    real_streams = {}
    real_streams.update(streams_of(W))
    real_streams.update({k + '/noF': v for k, v in streams_of(Wf).items()})
    real = _best_acrostic(real_streams)

    nulls = []
    for s in range(NNULL):
        nw = M.null_A(W, 100 + s)
        nulls.append(_best_acrostic(streams_of(nw))[0])

    # per-segment (page) acrostics
    seg_best = (-99.0, None)
    for pg in range(55):
        sw = [w for w, p in zip(W, d['w_page']) if p == pg]
        b = _best_acrostic(streams_of(sw))
        if b[0] > seg_best[0]:
            seg_best = (b[0], f'page{pg} {b[1]}')
    seg_nulls = []
    for s in range(NNULL):
        nw = M.null_A(W, 200 + s)
        bb = -99.0
        for pg in range(55):
            sw = [w for w, p in zip(nw, d['w_page']) if p == pg]
            bb = max(bb, _best_acrostic(streams_of(sw))[0])
        seg_nulls.append(bb)

    OUT['M1'] = dict(
        pooled=dict(best=round(real[0], 4), reading=real[1],
                    null_mean=round(float(np.mean(nulls)), 4),
                    null_sd=round(float(np.std(nulls, ddof=1)), 4),
                    null_max=round(float(np.max(nulls)), 4),
                    z=round(zscore(real[0], nulls), 2)),
        per_segment=dict(best=round(seg_best[0], 4), reading=seg_best[1],
                         null_mean=round(float(np.mean(seg_nulls)), 4),
                         null_max=round(float(np.max(seg_nulls)), 4),
                         z=round(zscore(seg_best[0], seg_nulls), 2)),
        threshold='ng >= -13.5 and z >= +5',
        HIT=bool(real[0] >= -13.5 and zscore(real[0], nulls) >= 5))
    print('\nM1 word-initial/final acrostics (%d readings pooled + %d per-segment)' %
          (4 * 2 * 29 * 2, 55 * 2 * 29 * 2 * 2))
    print('   pooled  best %+8.4f  (%s)   null %.4f+-%.4f max %.4f  z=%+.2f' %
          (real[0], real[1], np.mean(nulls), np.std(nulls, ddof=1), np.max(nulls),
           zscore(real[0], nulls)))
    print('   segment best %+8.4f  (%s)   null max %.4f  z=%+.2f' %
          (seg_best[0], seg_best[1], np.max(seg_nulls), zscore(seg_best[0], seg_nulls)))
    print('   HIT =', OUT['M1']['HIT'])


# =====================================================================  M2 ==
def _word_numbers(words):
    sp = np.array([sum(gp_primes[r] for r in w) for w in words])
    si = np.array([sum(w) for w in words])
    ln = np.array([len(w) for w in words])
    return sp, si, ln


from lp.gematria import PRIMES as gp_primes  # noqa: E402


def _M2_best(words):
    sp, si, ln = _word_numbers(words)
    best_r = (-99.0, None); best_l = (-99.0, None)
    for nm, arr in (('Sprime', sp), ('Sidx', si), ('len', ln)):
        r29 = (arr % N).tolist()
        for base, bn in ((r29, 'id'), (atbash(r29), 'atbash')):
            for k in range(N):
                s = ng_score(shifted(base, k))
                if s > best_r[0]:
                    best_r = (s, f'{nm} mod29 {bn} +{k}')
        r26 = (arr % 26).tolist()
        for k in range(26):
            txt = ''.join(LET[(x + k) % 26] for x in r26)
            s = eng_score(txt)
            if s > best_l[0]:
                best_l = (s, f'{nm} mod26 +{k}')
    return best_r, best_l


def null_B(words, seed):
    """Permute the WORD ORDER. This is the correct null for readings derived from
    word LENGTHS, which NULL-A leaves invariant by construction."""
    rng = random.Random(seed)
    w = words[:]
    rng.shuffle(w)
    return w


def M2(d):
    W = d['words']
    Wf = [[r for r in w if r != M.F_IDX] or [w[0]] for w in W]
    rr, rl = _M2_best(W)
    fr, fl = _M2_best(Wf)
    if fr[0] > rr[0]:
        rr = (fr[0], fr[1] + ' noF')
    if fl[0] > rl[0]:
        rl = (fl[0], fl[1] + ' noF')
    nr, nl = [], []
    for s in range(NNULL):
        nw = M.null_A(W, 300 + s)
        a, b = _M2_best(nw)
        nr.append(a[0]); nl.append(b[0])
        nw = null_B(W, 350 + s)              # NULL-B: word ORDER permuted
        a, b = _M2_best(nw)
        nr.append(a[0]); nl.append(b[0])
    OUT['M2'] = dict(
        rune=dict(best=round(rr[0], 4), reading=rr[1],
                  null_mean=round(float(np.mean(nr)), 4),
                  null_max=round(float(np.max(nr)), 4),
                  z=round(zscore(rr[0], nr), 2), threshold='>= -13.5 and z>=+5'),
        letter=dict(best=round(rl[0], 4), reading=rl[1],
                    null_mean=round(float(np.mean(nl)), 4),
                    null_max=round(float(np.max(nl)), 4),
                    z=round(zscore(rl[0], nl), 2), threshold='>= -6.0 and z>=+5'),
        HIT=bool((rr[0] >= -13.5 and zscore(rr[0], nr) >= 5) or
                 (rl[0] >= -6.0 and zscore(rl[0], nl) >= 5)))
    print('\nM2 word NUMBERS (gematria sums / lengths) reduced to symbols')
    print('   rune   best %+8.4f (%s)  null %.4f max %.4f  z=%+.2f' %
          (rr[0], rr[1], np.mean(nr), np.max(nr), zscore(rr[0], nr)))
    print('   letter best %+8.4f (%s)  null %.4f max %.4f  z=%+.2f' %
          (rl[0], rl[1], np.mean(nl), np.max(nl), zscore(rl[0], nl)))
    print('   HIT =', OUT['M2']['HIT'])


# =====================================================================  M3 ==
def _bits_readings(bits):
    """-> list of (name, score, kind, extra)"""
    out = []
    b = np.asarray(bits, np.uint8)
    for order in ('msb', 'lsb'):
        for off in range(8):
            v = b[off:]
            n8 = len(v) // 8
            if n8 > 8:
                g = v[:n8 * 8].reshape(n8, 8)
                if order == 'lsb':
                    g = g[:, ::-1]
                vals = g.dot(1 << np.arange(7, -1, -1))
                printable = float(np.mean((vals >= 32) & (vals < 127)))
                txt = ''.join(chr(x) for x in vals)
                out.append((f'ascii/{order}/off{off}', eng_score(txt), 'ascii', printable))
        for off in range(5):
            v = b[off:]
            n5 = len(v) // 5
            if n5 > 8:
                g = v[:n5 * 5].reshape(n5, 5)
                if order == 'lsb':
                    g = g[:, ::-1]
                vals = g.dot(1 << np.arange(4, -1, -1))
                txt = ''.join(LET[x % 26] for x in vals)
                out.append((f'bacon/{order}/off{off}', eng_score(txt), 'bacon', 1.0))
    return out


def _M3_streams(words):
    ln = np.array([len(w) for w in words])
    med = int(np.median(ln))
    preds = {'even': (ln % 2 == 0), 'gt_med': (ln > med), 'ge5': (ln >= 5),
             'prime': np.isin(ln, [2, 3, 5, 7, 11, 13])}
    for nm, p in list(preds.items()):
        preds[nm + '_inv'] = ~p
    return preds


def _M3_best(words):
    best_a = (-99.0, None, 0.0); best_b = (-99.0, None)
    for nm, p in _M3_streams(words).items():
        for rn, sc, kind, extra in _bits_readings(p.astype(np.uint8)):
            if kind == 'ascii':
                if sc > best_a[0]:
                    best_a = (sc, f'{nm} {rn}', extra)
            else:
                if sc > best_b[0]:
                    best_b = (sc, f'{nm} {rn}')
    return best_a, best_b


def M3(d):
    W = d['words']
    a, b = _M3_best(W)
    na, nb = [], []
    rng = random.Random(4242)
    for s in range(NNULL):
        sw = W[:]; rng.shuffle(sw)          # NULL-B: shuffled word-length sequence
        x, y = _M3_best(sw)
        na.append(x[0]); nb.append(y[0])
    OUT['M3'] = dict(
        ascii=dict(best=round(a[0], 4), reading=a[1], printable=round(a[2], 4),
                   null_max=round(float(np.max(na)), 4), z=round(zscore(a[0], na), 2),
                   threshold='printable>=0.90 and score_norm>=-6.0'),
        baconian=dict(best=round(b[0], 4), reading=b[1],
                      null_mean=round(float(np.mean(nb)), 4),
                      null_max=round(float(np.max(nb)), 4),
                      z=round(zscore(b[0], nb), 2), threshold='>=-6.0 and z>=+5'),
        HIT=bool((a[2] >= 0.90 and a[0] >= -6.0) or
                 (b[0] >= -6.0 and zscore(b[0], nb) >= 5)))
    print('\nM3 word-length BIT channel -> ASCII / Baconian')
    print('   ascii  best %+8.4f (%s) printable=%.3f  null_max %.4f  z=%+.2f' %
          (a[0], a[1], a[2], np.max(na), zscore(a[0], na)))
    print('   bacon  best %+8.4f (%s)  null %.4f max %.4f  z=%+.2f' %
          (b[0], b[1], np.mean(nb), np.max(nb), zscore(b[0], nb)))
    print('   HIT =', OUT['M3']['HIT'])


# =====================================================================  M4 ==
def _M4_best(words, book):
    B = len(book)
    sp, si, ln = _word_numbers(words)
    fams = {
        'len': ln, 'len-1': ln - 1,
        'Sprime': sp, 'Sidx': si,
        'cumSprime': np.cumsum(sp), 'cumSidx': np.cumsum(si),
        'idx+Sidx': si + np.arange(len(words)),
        'idx+Sprime': sp + np.arange(len(words)),
    }
    per = {}
    best = (-99.0, None, None)
    for nm, arr in fams.items():
        for base in (0, 1):
            ptr = (np.asarray(arr) - base) % B
            words_out = [book[i] for i in ptr]
            s = eng_score(' '.join(words_out))
            per[f'{nm} base{base}'] = (s, ' '.join(words_out[:14]),
                                       int(len(set(ptr.tolist()))))
            if s > best[0]:
                best = (s, f'{nm} base{base}', ' '.join(words_out[:14]))
    return best, per


def M4(d):
    W = d['words']
    book = M.solved_english_words()
    real, per = _M4_best(W, book)
    nA = [_M4_best(M.null_A(W, 500 + s), book)[0][0] for s in range(NNULL)]
    nB = [_M4_best(null_B(W, 550 + s), book)[0][0] for s in range(NNULL)]
    nulls = nA + nB
    OUT['M4'] = dict(best=round(real[0], 4), reading=real[1], sample=real[2],
                     book_words=len(book),
                     per_family={k: dict(score=round(v[0], 4), distinct_pointers=v[2],
                                         sample=v[1]) for k, v in per.items()},
                     null_A_max=round(float(np.max(nA)), 4),
                     null_B_max=round(float(np.max(nB)), 4),
                     null_mean=round(float(np.mean(nulls)), 4),
                     null_max=round(float(np.max(nulls)), 4),
                     z=round(zscore(real[0], nulls), 2),
                     threshold='score_norm >= -5.5 and z >= +5',
                     HIT=bool(real[0] >= -5.5 and zscore(real[0], nulls) >= 5))
    print('\nM4 Liber Primus as its OWN book cipher (%d solved English words)' % len(book))
    for k, v in sorted(per.items(), key=lambda kv: -kv[1][0]):
        print('   %-18s %+8.4f  distinct-pointers=%4d' % (k, v[0], v[2]))
    print('   best %+8.4f (%s)  nullA_max %.4f nullB_max %.4f  z=%+.2f' %
          (real[0], real[1], np.max(nA), np.max(nB), zscore(real[0], nulls)))
    print('   sample: %s ...' % real[2])
    print('   HIT =', OUT['M4']['HIT'])


# =====================================================================  M5 ==
def _M5_best(words, maxlen=400):
    n = len(words)
    sp, si, ln = _word_numbers(words)
    first = np.array([w[0] for w in words]); last = np.array([w[-1] for w in words])
    steps = {'len': ln, 'Sidx29': si % N, 'Sprime29': sp % N, 'Sidxn': si % n,
             'first': first, 'last': last, 'Sidx26p1': si % 26 + 1}
    inits = [w[0] for w in words]
    best = (-99.0, None)
    starts = list(range(0, n, max(1, n // 32)))[:32]
    for nm, f in steps.items():
        f = np.asarray(f)
        for mode in ('self', 'cum'):
            for sgn in (1, -1):
                for st in starts:
                    p = st; acc = 0; path = []
                    seen = set()
                    for _ in range(maxlen):
                        if p in seen:
                            break
                        seen.add(p); path.append(p)
                        d_ = int(f[p])
                        if mode == 'cum':
                            acc += d_; p = (st + sgn * acc) % n
                        else:
                            p = (p + sgn * max(1, d_)) % n
                    if len(path) < 24:
                        continue
                    a = [inits[i] for i in path]
                    s = ng_score(a)
                    if s > best[0]:
                        best = (s, f'{nm}/{mode}/{sgn:+d}/start{st}/initials')
                    b = [r for i in path for r in words[i]]
                    s2 = ng_score(b[:1200])
                    if s2 > best[0]:
                        best = (s2, f'{nm}/{mode}/{sgn:+d}/start{st}/whole')
    return best


def M5(d):
    W = d['words']
    real = _M5_best(W)
    nulls = [_M5_best(M.null_A(W, 700 + s))[0] for s in range(NNULL)]
    OUT['M5'] = dict(best=round(real[0], 4), reading=real[1],
                     null_mean=round(float(np.mean(nulls)), 4),
                     null_sd=round(float(np.std(nulls, ddof=1)), 4),
                     null_max=round(float(np.max(nulls)), 4),
                     z=round(zscore(real[0], nulls), 2),
                     threshold='ng >= -13.5 and z >= +5',
                     HIT=bool(real[0] >= -13.5 and zscore(real[0], nulls) >= 5))
    print('\nM5 WORD-level walk (Round-9 DIRECTION instrument, word granularity)')
    print('   best %+8.4f (%s)  null %.4f+-%.4f max %.4f  z=%+.2f' %
          (real[0], real[1], np.mean(nulls), np.std(nulls, ddof=1), np.max(nulls),
           zscore(real[0], nulls)))
    print('   HIT =', OUT['M5']['HIT'])


# =====================================================================  M6 ==
def M6(d):
    W = d['words']
    seqs = {
        'words-per-line': np.bincount(d['w_line'], minlength=max(d['w_line']) + 1),
        'words-per-page': np.bincount(d['w_page'], minlength=55),
        'words-per-sentence': np.bincount(d['w_sent'], minlength=max(d['w_sent']) + 1),
        'runes-per-line': np.array([len(l) for l in d['lines'] if l]),
        'runes-per-page': np.array([len(p) for p in d['pages']]),
    }
    rows = []
    hit = False
    rng = np.random.default_rng(11)
    for nm, arr in seqs.items():
        arr = np.asarray(arr)
        # letters
        bl = (-99.0, None)
        for k in range(26):
            t = ''.join(LET[(int(x) + k) % 26] for x in arr)
            s = eng_score(t)
            if s > bl[0]:
                bl = (s, f'mod26 +{k}')
        br = (-99.0, None)
        if len(arr) >= 24:
            r29 = (arr % N).tolist()
            for base, bn in ((r29, 'id'), (atbash(r29), 'atbash')):
                for k in range(N):
                    s = ng_score(shifted(base, k))
                    if s > br[0]:
                        br = (s, f'mod29 {bn} +{k}')
        nl, nr = [], []
        for _ in range(100):
            p = rng.permutation(arr)
            b = -99.0
            for k in range(26):
                b = max(b, eng_score(''.join(LET[(int(x) + k) % 26] for x in p)))
            nl.append(b)
            if len(arr) >= 24:
                b2 = -99.0
                r29 = (p % N).tolist()
                for k in range(N):
                    b2 = max(b2, ng_score(shifted(r29, k)))
                nr.append(b2)
        row = dict(seq=nm, n=int(len(arr)),
                   letter_best=round(bl[0], 4), letter_reading=bl[1],
                   letter_null_max=round(float(np.max(nl)), 4),
                   letter_z=round(zscore(bl[0], nl), 2),
                   rune_best=round(br[0], 4), rune_reading=br[1],
                   rune_null_max=(round(float(np.max(nr)), 4) if nr else None),
                   rune_z=(round(zscore(br[0], nr), 2) if nr else None))
        if bl[0] >= -6.0 and row['letter_z'] >= 5:
            hit = True
        if nr and br[0] >= -13.5 and row['rune_z'] >= 5:
            hit = True
        rows.append(row)
    OUT['M6'] = dict(rows=rows, HIT=hit,
                     threshold='letters >=-6.0 z>=+5 ; runes >=-13.5 z>=+5')
    print('\nM6 structural counts as a message')
    for r in rows:
        print('   %-19s n=%4d  letters %+7.4f (null_max %+7.4f z=%+5.2f)  runes %+8.4f'
              ' (null_max %s z=%s)' % (r['seq'], r['n'], r['letter_best'],
              r['letter_null_max'], r['letter_z'], r['rune_best'],
              r['rune_null_max'], r['rune_z']))
    print('   HIT =', hit)


# =====================================================================  M7 ==
def M7(d):
    W = d['words']
    fl = np.array(M.flat(W))
    c = np.bincount(fl, minlength=N).astype(float)
    n = c.sum()
    ioc = (c * (c - 1)).sum() / (n * (n - 1)) * N
    OUT['M7'] = dict(ioc_times_N=round(float(ioc), 4),
                     english_in_futhorc_band='1.7-1.8',
                     rule='word permutation preserves the rune multiset, hence IoC',
                     decision='EXCLUDED (IoC*N < 1.10)' if ioc < 1.10 else 'not excluded')
    print('\nM7 word-level transposition of plaintext (analytic)')
    print('   IoC*N = %.4f  -> %s' % (ioc, OUT['M7']['decision']))


# =====================================================================  M8 ==
def _longest_run(a, b):
    """max over all offsets of the longest run of consecutive exact matches
    of pattern b inside a."""
    best = 0
    A = np.asarray(a); B = np.asarray(b)
    for off in range(len(A) - len(B) + 1):
        eq = (A[off:off + len(B)] == B)
        run = 0
        for e in eq:
            run = run + 1 if e else 0
            if run > best:
                best = run
    return best


def M8(d):
    W = d['words']
    lp2 = np.array([len(w) for w in W], np.int16)
    book = M.solved_english_words()
    eng = np.array([M.rune_len(w) for w in book], np.int16)
    eng = eng[eng > 0]
    real = _longest_run(lp2, eng)
    rng = np.random.default_rng(77)
    nulls = [ _longest_run(rng.permutation(lp2), eng) for _ in range(NNULL) ]
    OUT['M8'] = dict(real_longest_run=int(real), n_pattern=int(len(eng)),
                     n_corpus=int(len(lp2)),
                     null_runs=[int(x) for x in nulls],
                     null_max=int(max(nulls)),
                     threshold='real > max(controls) and real >= 12',
                     HIT=bool(real > max(nulls) and real >= 12))
    print("\nM8 LP's own solved English as the LP2 plaintext skeleton")
    print('   pattern %d words, corpus %d words' % (len(eng), len(lp2)))
    print('   real longest exact-length run = %d ; controls %s (max %d)' %
          (real, nulls, max(nulls)))
    print('   HIT =', OUT['M8']['HIT'])


# =====================================================================  M9 ==
def _M9_best(words):
    """Direct ADDRESSING (not stepping): each word's number is an address into
    the book itself. Distinct from Round-9 DIRECTION families A/B/C (sequential
    walks) and D (predicate sieves)."""
    flat = np.array(M.flat(words))
    L = len(flat)
    n = len(words)
    sp, si, ln = _word_numbers(words)
    wstart = np.concatenate(([0], np.cumsum([len(w) for w in words])[:-1]))
    fams = {
        'Sprime->rune': sp % L, 'Sidx->rune': si % L,
        'cumSprime->rune': np.cumsum(sp) % L, 'cumSidx->rune': np.cumsum(si) % L,
        'Sprime+pos->rune': (sp + wstart) % L, 'Sidx+pos->rune': (si + wstart) % L,
        'Sprime->word-initial': sp % n, 'Sidx->word-initial': si % n,
        'cumSidx->word-initial': np.cumsum(si) % n,
        'len*idx->rune': (ln * np.arange(1, n + 1)) % L,
    }
    inits = np.array([w[0] for w in words])
    best = (-99.0, None)
    for nm, arr in fams.items():
        src = inits if 'word-initial' in nm else flat
        seq = src[np.asarray(arr) % len(src)].tolist()
        for k in range(N):
            s = ng_score([(x + k) % N for x in seq])
            if s > best[0]:
                best = (s, f'{nm} +{k}')
    return best


def M9(d):
    W = d['words']
    real = _M9_best(W)
    nulls = [_M9_best(M.null_A(W, 800 + s))[0] for s in range(NNULL)]
    nulls += [_M9_best(null_B(W, 850 + s))[0] for s in range(NNULL)]
    OUT['M9'] = dict(best=round(real[0], 4), reading=real[1],
                     null_mean=round(float(np.mean(nulls)), 4),
                     null_sd=round(float(np.std(nulls, ddof=1)), 4),
                     null_max=round(float(np.max(nulls)), 4),
                     z=round(zscore(real[0], nulls), 2),
                     threshold='ng >= -13.5 and z >= +5',
                     HIT=bool(real[0] >= -13.5 and zscore(real[0], nulls) >= 5))
    print('\nM9 word numbers as direct ADDRESSES into the book (self-indexing map)')
    print('   best %+8.4f (%s)  null %.4f+-%.4f max %.4f  z=%+.2f' %
          (real[0], real[1], np.mean(nulls), np.std(nulls, ddof=1), np.max(nulls),
           zscore(real[0], nulls)))
    print('   HIT =', OUT['M9']['HIT'])


# =====================================================================  main
def main():
    want = set(a.upper() for a in sys.argv[1:])
    d = G0()
    for name, fn in (('G1', G1), ('M1', M1), ('M2', M2), ('M3', M3), ('M4', M4),
                     ('M5', M5), ('M6', M6), ('M7', M7), ('M8', M8), ('M9', M9)):
        if want and name not in want:
            continue
        fn(d)
    p = os.path.join(HERE, 'results.json')
    json.dump(OUT, open(p, 'w'), indent=1)
    print('\nwrote', p)
    print('ANY HIT:', any(v.get('HIT') for v in OUT.values() if isinstance(v, dict)))


if __name__ == '__main__':
    main()
