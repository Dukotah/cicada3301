"""L3 / B-12 stages (b) and (c) + the mandatory line-fill positive control C-3.

Stage (a) (bimodality) ran in `linegeom.py`.  Five channels cleared the pre-registered
2.0-sigma / dBIC>10 screen -- which is necessary, not sufficient: a channel is only a
CHANNEL if the two states carry a message or track something real.  This script:

  0. CONFOUND TEST -- the obvious non-covert explanation for two-state line geometry is the
     LAST LINE of a paragraph/segment (short) and the SHORT SECTION PAGES.  Re-fit the GMM
     with those removed.  A channel whose bimodality evaporates is layout, not data.
  b. BIT DECODE  -- median-threshold the channel, pack 8 ways, look for English/file magic,
     score against a size-matched shuffle null.
  c. CORRELATION -- Spearman rho against per-line rune statistics, Bonferroni over 27 tests.
  C-3. POSITIVE CONTROL -- plant a known 64-bit message in the channel at the MEASURED noise
     level and require >=95% bit recovery, else report the power ceiling.

Writes linetests.json.
"""
import os, sys, json, itertools
import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
import reader as R                                                     # noqa: E402
sys.path.insert(0, os.path.join(R.LP, 'src'))
from lp.gematria import RUNE_TO_IDX                                    # noqa: E402
from linegeom import gmm2, canon                                       # noqa: E402

RNG = np.random.default_rng(3301)
BONF_C = 0.001 / 27


def load():
    return json.load(open(os.path.join(HERE, 'linegeom.json')))


def english_score(s):
    """Crude but null-calibrated: count of common English 4-grams."""
    G = ['THAT', 'THER', 'WITH', 'TION', 'HERE', 'OULD', 'IGHT', 'HAVE', 'HICH',
         'WHIC', 'THIS', 'THIN', 'THEY', 'ATIO', 'EVER', 'FROM', 'OUGH', 'WERE',
         'HING', 'MENT', 'PRIM', 'SACR', 'CICA', 'INST']
    s = s.upper()
    return sum(s.count(g) for g in G)


def bits_to_text(bits, packing):
    order, width = packing
    b = bits[::-1] if order == 'rev' else bits
    n = (len(b) // width) * width
    out = []
    for i in range(0, n, width):
        v = 0
        for k in range(width):
            v = (v << 1) | int(b[i + k])
        out.append(v)
    if width == 8:
        return ''.join(chr(v) if 32 <= v < 127 else '.' for v in out)
    return ''.join('ABCDEFGHIJKLMNOPQRSTUVWXYZ.,?!'[v % 30] for v in out)


def bit_decode(x, tag, res):
    x = np.asarray(x, float)
    bits = (x > np.median(x)).astype(int)
    best = None
    for packing in itertools.product(('fwd', 'rev'), (5, 8)):
        for phase in range(8):
            t = bits_to_text(bits[phase:], packing)
            sc = english_score(t)
            if best is None or sc > best[0]:
                best = (sc, str(packing), phase, t[:120])
    # size-matched null: shuffle the channel, redo
    null = []
    for _ in range(2000):
        sh = RNG.permutation(bits)
        b2 = None
        for packing in itertools.product(('fwd', 'rev'), (5, 8)):
            for phase in range(8):
                sc = english_score(bits_to_text(sh[phase:], packing))
                b2 = sc if b2 is None else max(b2, sc)
        null.append(b2)
    null = np.array(null)
    p = float((null >= best[0]).mean())
    res[tag] = dict(best_score=int(best[0]), packing=best[1], phase=best[2],
                    text=best[3], null_mean=float(null.mean()),
                    null_max=int(null.max()), p=p,
                    verdict='PASS' if p < 0.001 else 'FAIL')
    print('  bit-decode %-16s best %3d  null mean %5.1f max %3d  p=%.4f -> %s'
          % (tag, best[0], null.mean(), null.max(), p, res[tag]['verdict']))


def main():
    d = load()
    rows = d['rows']
    cn = canon()
    res = dict()

    # ------------------------------------------------------------------ 0. confound
    print('--- 0. CONFOUND: is the bimodality just "last line of a segment"? ---')
    seg_line_runes, seg_last = [], []
    for s in cn:
        for i, l in enumerate(s['lines']):
            seg_line_runes.append(l['n_runes'])
            seg_last.append(i == len(s['lines']) - 1)
    seg_line_runes = np.array(seg_line_runes); seg_last = np.array(seg_last)

    conf = {}
    g_all = gmm2(seg_line_runes)
    g_nolast = gmm2(seg_line_runes[~seg_last])
    conf['runes_per_line'] = dict(all=g_all, last_lines_removed=g_nolast)
    print('runes_per_line   all: sep %.2f sigma | last-lines removed: sep %.2f sigma'
          % (g_all['sep_sigma'], g_nolast['sep_sigma']))

    # image-side channels, last row of each page removed
    lastrow = {}
    for r in rows:
        lastrow[r['page']] = max(lastrow.get(r['page'], -1), r['row'])
    keep = np.array([r['row'] != lastrow[r['page']] for r in rows])
    for name, vals in [('row_height', [r['y1'] - r['y0'] for r in rows]),
                       ('body_per_line', [r['n_body'] for r in rows]),
                       ('fill_ratio', [r['fill'] for r in rows])]:
        v = np.array(vals, float)
        ga, gk = gmm2(v), gmm2(v[keep])
        conf[name] = dict(all=ga, last_rows_removed=gk)
        print('%-16s all: sep %.2f sigma | last-rows removed: sep %.2f sigma'
              % (name, ga['sep_sigma'], gk['sep_sigma']))

    # pages with < 8 rows removed (section-title / short pages)
    npg = {}
    for r in rows:
        npg[r['page']] = npg.get(r['page'], 0) + 1
    keep2 = np.array([npg[r['page']] >= 8 for r in rows])
    for name, vals in [('row_height', [r['y1'] - r['y0'] for r in rows]),
                       ('body_per_line', [r['n_body'] for r in rows])]:
        v = np.array(vals, float)
        gk = gmm2(v[keep2 & keep])
        conf[name]['short_pages_and_last_rows_removed'] = gk
        print('%-16s short pages + last rows removed: sep %.2f sigma'
              % (name, gk['sep_sigma']))
    res['confound'] = conf

    # ------------------------------------------------------------------ b. bit decode
    print('\n--- b. BIT DECODE (PASS iff p<0.001 vs size-matched shuffle null) ---')
    res['bit_decode'] = {}
    chans = {
        'fill_ratio': [r['fill'] for r in rows],
        'left_margin': [r['left_margin'] for r in rows],
        'right_margin': [r['right_margin'] for r in rows],
        'row_height': [r['y1'] - r['y0'] for r in rows],
        'body_per_line': [r['n_body'] for r in rows],
        'sep_per_line': [r['n_sep'] for r in rows],
        'runes_per_line': seg_line_runes,
        'words_per_line': [n for s in cn for n in [l['n_words'] for l in s['lines']]],
    }
    for k, v in chans.items():
        bit_decode(v, k, res['bit_decode'])

    # --------------------------------------------------------------- c. correlation
    print('\n--- c. CORRELATION with the rune stream (Bonferroni p<3.7e-5) ---')
    per_line = [l for s in cn for l in s['lines']]
    stat = {
        'mean_rune_idx': [float(np.mean(l['runes'])) for l in per_line],
        'doublets': [int(sum(1 for a, b in zip(l['runes'], l['runes'][1:]) if a == b))
                     for l in per_line],
        'ioc': [float(sum(c * (c - 1) for c in np.bincount(l['runes'], minlength=29)) /
                      max(len(l['runes']) * (len(l['runes']) - 1), 1)) for l in per_line],
    }
    res['correlation'] = {}
    n = min(len(rows), len(per_line))
    for ck, cv in chans.items():
        cvv = np.asarray(cv, float)
        for sk, sv in stat.items():
            m = min(len(cvv), len(sv))
            rho, p = stats.spearmanr(cvv[:m], np.asarray(sv, float)[:m])
            res['correlation']['%s~%s' % (ck, sk)] = dict(
                rho=float(rho), p=float(p), n=int(m),
                verdict='PASS' if p < BONF_C else 'FAIL')
            if p < BONF_C:
                print('  %-16s ~ %-14s rho=%+.3f p=%.3g  PASS' % (ck, sk, rho, p))
    npass = sum(1 for v in res['correlation'].values() if v['verdict'] == 'PASS')
    print('  %d / %d correlations clear the Bonferroni bar'
          % (npass, len(res['correlation'])))

    # ---------------- explain the one surviving correlation (typographic justification)
    print('BROKEN--- c2. Is runes_per_line ~ mean_rune_idx a covert channel or justification? ---')
    # mean advance per rune class, measured from the image rows themselves
    import collections as _c
    widths = _c.defaultdict(list)
    read = json.load(open(os.path.join(R.LP, 'analysis', 'retranscribe', 'read_lines.json')))
    mp = R.load_mapping()
    for rec in read:
        g = rec['glyphs']
        for i in range(len(g) - 1):
            r = mp.get(g[i][0], -1)
            adv = g[i + 1][1] - g[i][1]
            if r >= 0 and 20 < adv < 200:
                widths[r].append(adv)
    wmean = {k: float(np.mean(v)) for k, v in widths.items() if len(v) > 20}
    per_line = [l for s_ in cn for l in s_['lines']]
    pred_w = [float(np.mean([wmean.get(r, np.nan) for r in l['runes']])) for l in per_line]
    pred_w = np.array(pred_w, float)
    ok = ~np.isnan(pred_w)
    rpl = np.array([l['n_runes'] for l in per_line], float)
    mri = np.array([float(np.mean(l['runes'])) for l in per_line])
    r1, p1 = stats.spearmanr(rpl[ok], mri[ok])
    r2, p2 = stats.spearmanr(rpl[ok], pred_w[ok])
    r3, p3 = stats.spearmanr(mri[ok], pred_w[ok])
    # partial correlation of rpl~mri controlling for mean glyph width
    def resid(y, x):
        A = np.vstack([x, np.ones_like(x)]).T
        b = np.linalg.lstsq(A, y, rcond=None)[0]
        return y - A @ b
    rp, pp = stats.spearmanr(resid(rpl[ok], pred_w[ok]), resid(mri[ok], pred_w[ok]))
    print('  runes_per_line ~ mean_rune_idx        rho=%+.3f p=%.3g' % (r1, p1))
    print('  runes_per_line ~ mean GLYPH WIDTH     rho=%+.3f p=%.3g' % (r2, p2))
    print('  mean_rune_idx  ~ mean GLYPH WIDTH     rho=%+.3f p=%.3g' % (r3, p3))
    print('  PARTIAL runes_per_line ~ mean_rune_idx | width   rho=%+.3f p=%.3g' % (rp, pp))
    res['justification_test'] = dict(
        rho_rpl_mri=float(r1), p_rpl_mri=float(p1),
        rho_rpl_width=float(r2), p_rpl_width=float(p2),
        rho_mri_width=float(r3), p_mri_width=float(p3),
        partial_rho=float(rp), partial_p=float(pp),
        interpretation=('the correlation is mediated by glyph width if the partial '
                        'correlation collapses toward zero'),
        rune_mean_advance_px={str(k): round(v, 1) for k, v in sorted(wmean.items())})

    # ------------------------------------------------------------ C-3 positive control
    print('BROKEN--- C-3a POWER CEILING: plant 64 bits in fill_ratio at k*sd separation ---')
    base = np.array([r['fill'] for r in rows], float)
    noise = float(base.std())
    msg = np.array([int(b) for ch in 'CICADA33' for b in format(ord(ch), '08b')])
    ctrl = []
    for k in (0.5, 1, 2, 3, 4, 6, 8):
        planted = base.copy()
        planted[:len(msg)] = base.mean() + msg * (k * noise) + RNG.normal(0, noise, len(msg))
        g = gmm2(planted[:len(msg)])
        rec_bits = (planted[:len(msg)] > np.median(planted[:len(msg)])).astype(int)
        recall = float((rec_bits == msg).mean())
        ctrl.append(dict(k_sd=k, planted_sep_px=round(k * noise, 5),
                         gmm_sep_sigma=round(g['sep_sigma'], 3),
                         bit_recovery=round(recall, 4),
                         pass_=bool(g['sep_sigma'] >= 2.0 and recall >= 0.95)))
        print('  sep %4.1f sd  GMM %5.2f sigma  bit recovery %.3f -> %s'
              % (k, g['sep_sigma'], recall, 'PASS' if ctrl[-1]['pass_'] else 'below ceiling'))
    ceiling = min([c['k_sd'] for c in ctrl if c['pass_']], default=None)

    print('BROKEN--- C-3b DECODER VALIDATION: plant real ASCII in the bit channel, noise-free ---')
    plain = ('THEPRIMESARESACREDTHATTHEREISNOTHINGWITHINWHICHTHEYWERE'
             'THEREFORETHISWASTHEIRONLYPATHFROM')
    mb = [int(b) for ch in plain for b in format(ord(ch), '08b')]
    mb = (mb * (len(base) // max(len(mb), 1) + 1))[:len(base)]
    chan = np.array(mb, float) + RNG.normal(0, 0.05, len(base))
    tmp = {}
    bit_decode(chan, 'PLANTED_ASCII', tmp)
    res['control_C3'] = dict(measured_noise_sd=noise,
                             message='CICADA33 (64 bits)',
                             ceiling_k_sd=ceiling, trials=ctrl,
                             decoder_validation=tmp['PLANTED_ASCII'],
                             verdict=('PASS' if (ceiling is not None and
                                                 tmp['PLANTED_ASCII']['verdict'] == 'PASS')
                                      else 'CEILING-ONLY'),
                             note=('the bit-decode null is only meaningful if the decoder '
                                   'recovers a noise-free planted message; that is what '
                                   'decoder_validation measures.'))
    json.dump(res, open(os.path.join(HERE, 'linetests.json'), 'w'), indent=1)
    print('\nwrote linetests.json')


if __name__ == '__main__':
    main()
