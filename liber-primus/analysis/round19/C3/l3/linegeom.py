"""L3 / B-12 -- line geometry and line fill as a data channel.

Nine channels, per PREREG section I-3.  Round 8's GEOMETRY track already swept
inter-glyph ADVANCE (1.86 sigma, unimodal) and BASELINE JITTER (BIC rejects two
components); neither is re-run here.  What was never measured is the LINE-level and
PAGE-level typesetting decision: how full a line is, where the margins sit, how many words
and runes the typesetter put on each line, and where they chose to break.

Image side  : per text row -- y span, x span, rune-body component count, separator-dot
              count, inter-word gaps, left/right margin against the page's own text column.
Canon side  : per line     -- rune count, word count, word lengths, and whether the line
              break lands on a word boundary.

Writes linegeom.json.
"""
import os, sys, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
import reader as R                                                     # noqa: E402
sys.path.insert(0, os.path.join(R.LP, 'src'))
from lp.gematria import RUNE_TO_IDX                                    # noqa: E402

IMG = os.path.join(R.LP, 'data', 'relikd')
RUNE_BODY = (95, 140)
SEP_MAX = 30


def canon():
    txt = open(os.path.join(R.LP, 'data', 'krisyotam_runes.txt'), encoding='utf-8').read()
    segs = []
    for si, seg in enumerate(txt.split('%')):
        lines = []
        for ln in seg.split('/'):
            runes = [RUNE_TO_IDX[c] for c in ln if c in RUNE_TO_IDX]
            if not runes:
                continue
            words, cur = [], []
            for c in ln:
                if c in RUNE_TO_IDX:
                    cur.append(RUNE_TO_IDX[c])
                elif c in '-.' and cur:
                    words.append(cur); cur = []
            if cur:
                words.append(cur)
            lines.append(dict(n_runes=len(runes), n_words=len(words),
                              word_lens=[len(w) for w in words],
                              runes=runes,
                              ends_midword=(ln.rstrip()[-1:] not in '-.' if ln.strip() else True)))
        if lines:
            segs.append(dict(seg=si, lines=lines))
    return segs


def page_rows(path):
    ct = R.comp_table(path)
    h = ct['y1'] - ct['y0']; w = ct['x1'] - ct['x0']
    body = (h >= RUNE_BODY[0]) & (h <= RUNE_BODY[1]) & (w < 300)
    idx = np.where(body)[0]
    if not len(idx):
        return []
    order = idx[np.argsort(ct['y0'][idx])]
    rows, cur = [], [order[0]]
    for i in order[1:]:
        ytop = min(ct['y0'][j] for j in cur); ybot = max(ct['y1'][j] for j in cur)
        if ct['y0'][i] < ybot - 0.45 * (ybot - ytop):
            cur.append(i)
        else:
            rows.append(cur); cur = [i]
    rows.append(cur)
    sepmask = (h <= SEP_MAX) & (w <= SEP_MAX)
    sidx = np.where(sepmask)[0]
    out = []
    for r in rows:
        r = sorted(r, key=lambda j: ct['x0'][j])
        y0 = int(min(ct['y0'][j] for j in r)); y1 = int(max(ct['y1'][j] for j in r))
        x0 = int(min(ct['x0'][j] for j in r)); x1 = int(max(ct['x1'][j] for j in r))
        mine = [s for s in sidx if y0 - 12 <= (ct['y0'][s] + ct['y1'][s]) / 2 <= y1 + 12
                and x0 - 40 <= ct['x0'][s] <= x1 + 40]
        xs = sorted(float(ct['x0'][s]) for s in mine)
        boxes = [(float(ct['x0'][j]), float(ct['x1'][j])) for j in r]
        gaps = [boxes[i + 1][0] - boxes[i][1] for i in range(len(boxes) - 1)]
        out.append(dict(y0=y0, y1=y1, x0=x0, x1=x1, n_body=len(r), n_sep=len(mine),
                        sep_x=xs, gaps=[round(g, 1) for g in gaps]))
    return out


def gmm2(x, iters=400):
    """1-vs-2 component GMM; returns (bic1, bic2, sep_sigma, means, weights)."""
    x = np.asarray(x, float)
    n = len(x)
    if n < 20 or x.std() == 0:
        return None
    ll1 = -0.5 * n * (np.log(2 * np.pi * x.var()) + 1)
    bic1 = -2 * ll1 + 2 * np.log(n)
    mu = np.quantile(x, [0.25, 0.75]).astype(float)
    sd = np.full(2, x.std() / 2 + 1e-9)
    w = np.array([0.5, 0.5])
    for _ in range(iters):
        p = w * np.exp(-0.5 * ((x[:, None] - mu) / sd) ** 2) / (sd * np.sqrt(2 * np.pi))
        s = p.sum(1, keepdims=True)
        s[s == 0] = 1e-300
        g = p / s
        nk = g.sum(0) + 1e-9
        mu = (g * x[:, None]).sum(0) / nk
        sd = np.sqrt((g * (x[:, None] - mu) ** 2).sum(0) / nk) + 1e-9
        w = nk / n
    p = w * np.exp(-0.5 * ((x[:, None] - mu) / sd) ** 2) / (sd * np.sqrt(2 * np.pi))
    ll2 = float(np.log(np.clip(p.sum(1), 1e-300, None)).sum())
    bic2 = -2 * ll2 + 5 * np.log(n)
    sep = abs(mu[0] - mu[1]) / max(np.sqrt((sd ** 2 * w).sum()), 1e-9)
    return dict(bic1=float(bic1), bic2=float(bic2), delta_bic=float(bic1 - bic2),
                sep_sigma=float(sep), means=[round(float(v), 3) for v in mu],
                sds=[round(float(v), 3) for v in sd],
                weights=[round(float(v), 3) for v in w], n=int(n))


def main():
    rows_all, per_page = [], []
    for p in range(56):
        rs = page_rows(os.path.join(IMG, 'p%d.jpg' % p))
        xs0 = np.array([r['x0'] for r in rs], float)
        xs1 = np.array([r['x1'] for r in rs], float)
        col_lo = float(np.median(xs0)) if len(rs) else 0.0
        col_hi = float(np.median(xs1)) if len(rs) else 0.0
        width = max(col_hi - col_lo, 1.0)
        for i, r in enumerate(rs):
            r['page'] = p
            r['row'] = i
            r['left_margin'] = r['x0'] - col_lo
            r['right_margin'] = col_hi - r['x1']
            r['fill'] = (r['x1'] - r['x0']) / width
            r['mean_sep_gap'] = float(np.mean([g for g in r['gaps'] if 0 < g < 120])) \
                if any(0 < g < 120 for g in r['gaps']) else None
        per_page.append(dict(page=p, n_rows=len(rs), col_lo=col_lo, col_hi=col_hi,
                             col_width=width,
                             n_body=int(sum(r['n_body'] for r in rs)),
                             n_sep=int(sum(r['n_sep'] for r in rs))))
        rows_all += rs
        print('p%-2d rows %2d col [%.0f,%.0f] body %4d sep %3d'
              % (p, len(rs), col_lo, col_hi, per_page[-1]['n_body'],
                 per_page[-1]['n_sep']), flush=True)

    cn = canon()
    res = dict(rows=rows_all, pages=per_page,
               canon_segments=[dict(seg=s['seg'],
                                    n_lines=len(s['lines']),
                                    n_runes=sum(l['n_runes'] for l in s['lines']),
                                    n_words=sum(l['n_words'] for l in s['lines']),
                                    line_runes=[l['n_runes'] for l in s['lines']],
                                    line_words=[l['n_words'] for l in s['lines']],
                                    ends_midword=[l['ends_midword'] for l in s['lines']])
                              for s in cn])

    # ------- channel bimodality (PREREG I-3a): PASS iff sep >= 2.0 sigma AND dBIC > 10
    chans = {
        'fill_ratio': [r['fill'] for r in rows_all],
        'left_margin': [r['left_margin'] for r in rows_all],
        'right_margin': [r['right_margin'] for r in rows_all],
        'row_height': [r['y1'] - r['y0'] for r in rows_all],
        'body_per_line': [r['n_body'] for r in rows_all],
        'sep_per_line': [r['n_sep'] for r in rows_all],
        'mean_sep_gap': [r['mean_sep_gap'] for r in rows_all if r['mean_sep_gap']],
        'runes_per_line': [n for s in cn for n in [l['n_runes'] for l in s['lines']]],
        'words_per_line': [n for s in cn for n in [l['n_words'] for l in s['lines']]],
        'words_per_page': [sum(l['n_words'] for l in s['lines']) for s in cn],
        'lines_per_page': [len(s['lines']) for s in cn],
    }
    res['bimodality'] = {}
    print('\n--- I-3a bimodality (PASS iff sep>=2.0 sigma AND dBIC>10) ---')
    for k, v in chans.items():
        g = gmm2(v)
        if g is None:
            res['bimodality'][k] = None
            print('%-16s n<20, skipped' % k)
            continue
        g['pass'] = bool(g['sep_sigma'] >= 2.0 and g['delta_bic'] > 10)
        res['bimodality'][k] = g
        print('%-16s n=%-5d sep=%5.2f sigma  dBIC=%9.1f  -> %s'
              % (k, g['n'], g['sep_sigma'], g['delta_bic'],
                 'PASS' if g['pass'] else 'fail'))

    json.dump(res, open(os.path.join(HERE, 'linegeom.json'), 'w'), indent=1)
    print('\nwrote linegeom.json  (%d text rows over %d pages)'
          % (len(rows_all), len(per_page)))


if __name__ == '__main__':
    main()
