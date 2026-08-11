"""Track GEOMETRY — stage 2: the four measurements nobody has taken.

  A. GLYPH-SHAPE OUTLIERS. These pages are a font render. Every instance of a
     given rune must therefore be identical modulo sub-pixel placement phase and
     JPEG noise. Any real outlier -- a rotation, a mirror, a modified stroke, a
     substituted face -- is deliberate by construction. This is the decisive test
     and it has never been run: the vision armada tried to READ glyphs, never to
     COMPARE them.
  B. INTER-GLYPH ADVANCE. Micro-spacing is the classic covert channel in a
     typeset document (wide/narrow = 1/0). A ~13,000-bit channel if bimodal.
     Measured only between adjacent runes with NO separator between them, so the
     word-separator gap cannot manufacture false bimodality.
  C. BASELINE JITTER. Same test on the vertical axis, measured WITHIN rune class
     so that per-glyph shape differences cannot manufacture spread.
  D. ORNAMENT INVENTORY. The segmenters in this repo explicitly discard
     "ornament components far from the dominant text column". Nobody has ever
     listed what was thrown away.
"""
import os, sys, json, collections
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'src'))
from lp.gematria import RUNE_TO_IDX, IDX_TO_TRANS

d = np.load(os.path.join(HERE, 'glyphs.npz'))
page, x0, y0, x1, y1, area, bmp = (d['page'], d['x0'], d['y0'], d['x1'], d['y1'],
                                   d['area'], d['bmp'])
H, W = y1 - y0, x1 - x0
SEP = H < 30                                   # separator dots


def jdefault(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    raise TypeError(str(type(o)))


# ------------------------------------------------------------- line grouping
def page_rows(p):
    idx = np.where(page == p)[0]
    if not len(idx):
        return []
    big = idx[~SEP[idx]]
    order = big[np.argsort(y0[big])]
    rows, cur = [], [order[0]]
    for i in order[1:]:
        ytop = min(y0[j] for j in cur)
        ybot = max(y1[j] for j in cur)
        if y0[i] < ybot - 0.45 * (ybot - ytop):
            cur.append(i)
        else:
            rows.append(cur); cur = [i]
    rows.append(cur)
    # attach separator dots to the row whose vertical span contains them
    out = []
    seps = idx[SEP[idx]]
    for r in rows:
        ytop = min(y0[j] for j in r); ybot = max(y1[j] for j in r)
        mine = [s for s in seps if ytop - 10 <= (y0[s] + y1[s]) / 2 <= ybot + 10]
        out.append((sorted(r, key=lambda j: x0[j]), sorted(mine, key=lambda j: x0[j])))
    return out


def merge_row(row):
    """merge components that horizontally overlap -- one rune rendered as two
    ink blobs (disconnected strokes)."""
    out = []
    for j in row:
        if out:
            g = out[-1]
            glo = min(x0[i] for i in g); ghi = max(x1[i] for i in g)
            ov = min(ghi, x1[j]) - max(glo, x0[j])
            if ov > 0.55 * min(ghi - glo, W[j]):
                g.append(j); continue
        out.append([j])
    return [tuple(g) for g in out]


def gbox(g):
    return (min(x0[i] for i in g), min(y0[i] for i in g),
            max(x1[i] for i in g), max(y1[i] for i in g))


# ------------------------------------------------------- canonical alignment
txt = open(os.path.join(ROOT, 'data', 'krisyotam_runes.txt'), encoding='utf-8').read()
canon_lines = []
for si, seg in enumerate(txt.split('%')):
    for ln in seg.split('/'):
        rs = [RUNE_TO_IDX[c] for c in ln if c in RUNE_TO_IDX]
        if rs:
            canon_lines.append((si, rs))


def main():
    rep = {}
    img_lines, ornaments = [], []
    for p in range(56):
        rows = page_rows(p)
        if not rows:
            continue
        spans = [(min(x0[j] for j in r), max(x1[j] for j in r)) for r, _ in rows]
        med_lo, med_hi = np.median([s[0] for s in spans]), np.median([s[1] for s in spans])
        for r, seps in rows:
            g = merge_row(r)
            lo = min(gbox(q)[0] for q in g); hi = max(gbox(q)[2] for q in g)
            hs = [gbox(q)[3] - gbox(q)[1] for q in g]
            if hi < med_lo - 50 or lo > med_hi + 50 or np.median(hs) > 240:
                ornaments.append((int(p), int(lo), int(hi), len(g), int(np.median(hs))))
                continue
            img_lines.append((p, g, seps))
    n = min(len(img_lines), len(canon_lines))
    exact = [i for i in range(n) if len(img_lines[i][1]) == len(canon_lines[i][1])]
    print('image text lines %d | canonical lines %d | exact count match %d (%.1f%%)'
          % (len(img_lines), len(canon_lines), len(exact), 100.0*len(exact)/n))
    rep.update(lines_image=len(img_lines), lines_canon=len(canon_lines),
               lines_exact=len(exact))

    # --------------------------------------------- B. advance, separator-free
    gaps = []
    for p, g, seps in img_lines:
        boxes = [gbox(q) for q in g]
        sx = [(x0[s] + x1[s]) / 2 for s in seps]
        for i in range(len(boxes) - 1):
            a, b = boxes[i][2], boxes[i+1][0]
            if any(a - 4 <= s <= b + 4 for s in sx):
                continue                      # a separator sits in this gap
            gap = b - a
            if -20 < gap < 60:
                gaps.append(gap)
    gaps = np.array(gaps, float)

    def gmm(x, k, iters=300):
        mu = np.quantile(x, np.linspace(0.2, 0.8, k))
        sd = np.full(k, x.std() / k + 1e-6)
        w = np.full(k, 1.0 / k)
        for _ in range(iters):
            pr = np.stack([w[j] * np.exp(-0.5*((x-mu[j])/sd[j])**2)/(sd[j]*np.sqrt(2*np.pi))
                           for j in range(k)]) + 1e-300
            r = pr / pr.sum(0); nk = r.sum(1)
            w = nk/len(x); mu = (r*x).sum(1)/nk
            sd = np.sqrt((r*(x-mu[:, None])**2).sum(1)/nk) + 1e-6
        ll = np.log(np.stack([w[j]*np.exp(-0.5*((x-mu[j])/sd[j])**2)/(sd[j]*np.sqrt(2*np.pi))
                              for j in range(k)]).sum(0) + 1e-300).sum()
        return -2*ll + (3*k-1)*np.log(len(x)), mu, sd, w

    print('\n--- B. inter-glyph advance, separator-free (n=%d) ---' % len(gaps))
    print('mean %.2f sd %.2f  pct %s' % (gaps.mean(), gaps.std(),
          np.percentile(gaps, [1, 5, 25, 50, 75, 95, 99]).round(1)))
    b1, *_ = gmm(gaps, 1); b2, mu2, sd2, w2 = gmm(gaps, 2)
    print('BIC 1comp %.0f  2comp %.0f  delta %.0f  means %s  sd %s  w %s'
          % (b1, b2, b1-b2, mu2.round(2), sd2.round(2), w2.round(3)))
    sep_sig = float(abs(mu2[1]-mu2[0]) / sd2.mean())
    print('component separation: %.2f sigma  (a usable 1-bit channel needs >~2)'
          % sep_sig)
    rep['advance'] = dict(n=len(gaps), mean=float(gaps.mean()), sd=float(gaps.std()),
                          bic1=float(b1), bic2=float(b2),
                          means=mu2.round(3).tolist(), sep_sigma=sep_sig)

    # ------------------------------------------------ label glyphs (A and C)
    labels, gl = [], []
    for i in exact:
        p, g, seps = img_lines[i]
        for q, r in zip(g, canon_lines[i][1]):
            gl.append(q); labels.append(r)
    labels = np.array(labels)
    print('\nlabelled glyphs: %d (from %d count-exact lines)' % (len(gl), len(exact)))
    rep['labelled_glyphs'] = len(gl)

    # ---------------------------------------- C. baseline jitter within class
    base_off = []
    for i in exact:
        p, g, seps = img_lines[i]
        boxes = [gbox(q) for q in g]
        base = np.median([b[3] for b in boxes])
        for b in boxes:
            base_off.append(b[3] - base)
    base_off = np.array(base_off, float)
    within = []
    for r in range(29):
        m = labels == r
        if m.sum() < 30:
            continue
        v = base_off[:len(labels)][m]
        within.append(v - np.median(v))
    within = np.concatenate(within)
    print('\n--- C. baseline offset, within rune class (n=%d) ---' % len(within))
    print('mean %.3f sd %.3f  pct %s' % (within.mean(), within.std(),
          np.percentile(within, [1, 5, 25, 50, 75, 95, 99]).round(1)))
    b1, *_ = gmm(within, 1); b2, mu2, sd2, w2 = gmm(within, 2)
    print('BIC 1comp %.0f  2comp %.0f  delta %.0f  means %s' %
          (b1, b2, b1-b2, mu2.round(2)))
    rep['baseline'] = dict(n=len(within), sd=float(within.std()),
                           bic1=float(b1), bic2=float(b2),
                           means=mu2.round(3).tolist())

    # ------------------------------------------------ A. glyph-shape outliers
    print('\n--- A. glyph-shape outliers (the decisive test) ---')
    B = bmp[np.array([q[0] for q in gl])].reshape(len(gl), -1).astype(np.float32)
    # use the merged group's own bitmap only when the group is a single blob;
    # multi-blob groups are re-rendered from the union box
    res = {}
    outliers = []
    for r in range(29):
        m = np.where(labels == r)[0]
        if len(m) < 20:
            continue
        X = B[m]
        mean = X.mean(0)
        dist = np.abs(X - mean).sum(1) / X.shape[1]      # mean |pixel| residual
        mu, sd = dist.mean(), dist.std()
        z = (dist - mu) / (sd + 1e-9)
        res[r] = dict(n=len(m), mean_resid=float(mu), sd=float(sd),
                      max_z=float(z.max()))
        for k in np.argsort(z)[::-1][:5]:
            if z[k] > 6:
                gi = gl[m[k]][0]
                outliers.append(dict(rune=IDX_TO_TRANS[r], z=float(z[k]),
                                     page=int(page[gi]), x=int(x0[gi]), y=int(y0[gi])))
    tab = sorted(res.items(), key=lambda kv: -kv[1]['max_z'])
    print('%-5s %5s %10s %8s %8s' % ('rune', 'n', 'meanresid', 'sd', 'max z'))
    for r, v in tab[:10]:
        print('%-5s %5d %10.4f %8.4f %8.2f' %
              (IDX_TO_TRANS[r], v['n'], v['mean_resid'], v['sd'], v['max_z']))
    print('classes measured: %d   instances with z>6: %d' % (len(res), len(outliers)))
    rep['shape'] = dict(classes=len(res), outliers=outliers[:60],
                        max_z_overall=max(v['max_z'] for v in res.values()))

    # ----------------------------------------------------------- D. ornaments
    print('\n--- D. ornament / non-text rows ---')
    print('rows rejected as ornament: %d across %d pages'
          % (len(ornaments), len(set(o[0] for o in ornaments))))
    rep['ornament_rows'] = len(ornaments)
    json.dump(ornaments, open(os.path.join(HERE, 'ornaments.json'), 'w'), default=jdefault)
    json.dump(rep, open(os.path.join(HERE, 'geometry_report.json'), 'w'),
              indent=1, default=jdefault)
    print('\nwrote geometry_report.json')


if __name__ == '__main__':
    main()
