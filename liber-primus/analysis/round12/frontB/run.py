"""Driver: fit cluster->rune permutation on SOLVED pages via forced segmentation,
run positive control, then diff pages 45-54.

The permutation is fit ONLY on solved control pages (p2..p14 text pages that are
cryptographically solved), never on 45-54, so canon on 45-54 cannot leak into the
naming. We then apply the frozen permutation to the forced reads of 45-54.
"""
import os, sys, json, collections
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import forceseg as F
from lp.gematria import IDX_TO_TRANS

# solved / trustworthy control pages (early narrative, decrypt-verified region)
CONTROL_PAGES = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
TARGET_PAGES = list(range(45, 55))

def rune_positions(toks):
    """indices in the forced token stream that are runes, with their rune idx."""
    return [(i, t[1]) for i, t in enumerate(toks) if t[0] == 'r']

def gather(geo, canon, tmpl, pages):
    """for each page/line: forced read (class per token) aligned to canon tokens.
    returns list of dicts."""
    rows = []
    for p in pages:
        lids = F.line_ids_for_page(geo, p)
        a = np.asarray(Image.open(os.path.join(F.IMG, 'p%d.jpg' % p)).convert('L'))
        ink = (a < 128).astype(np.float32)
        for gli in lids:
            if gli >= len(canon):
                continue
            runes = [t for t in F.canon_tokens(canon[gli]) if t[0] == 'r']
            if len(runes) < 2:
                continue
            read = F.read_line_forced(geo, gli, ink, len(runes), tmpl)
            rows.append(dict(page=p, gli=gli, toks=runes, read=read))
    return rows

def fit_mapping(rows):
    """confusion matrix cluster-class -> canon-rune over rune tokens, then 1-1."""
    classes = sorted({c for r in rows for (c, _) in r['read'] if c is not None})
    ci = {c: k for k, c in enumerate(classes)}
    M = np.zeros((len(classes), 29), np.int64)
    for r in rows:
        for (c, _), t in zip(r['read'], r['toks']):
            if t[0] != 'r' or c is None:
                continue
            M[ci[c], t[1]] += 1
    from scipy.optimize import linear_sum_assignment
    rr, cc = linear_sum_assignment(-M)
    mapping = {classes[i]: int(j) for i, j in zip(rr, cc)}
    return mapping, M, classes

def score(rows, mapping):
    hit = tot = 0
    dis = []
    for r in rows:
        for (c, cost), t in zip(r['read'], r['toks']):
            if t[0] != 'r':
                continue
            tot += 1
            m = mapping.get(c)
            if m == t[1]:
                hit += 1
            else:
                dis.append(dict(page=r['page'], gli=r['gli'],
                                image=IDX_TO_TRANS[m] if m is not None else '?',
                                canon=IDX_TO_TRANS[t[1]], cost=round(float(cost), 2)))
    return hit, tot, dis

def main():
    geo = F.load_geo()
    canon = F.load_canon_full()
    tmpl = F.load_templates()
    print('templates: %d classes' % len(tmpl))

    print('reading control pages %s ...' % CONTROL_PAGES, flush=True)
    ctrl = gather(geo, canon, tmpl, CONTROL_PAGES)
    mapping, M, classes = fit_mapping(ctrl)
    hit, tot, dis = score(ctrl, mapping)
    print('CONTROL forced-seg agreement: %d/%d = %.2f%%' % (hit, tot, 100.0 * hit / max(tot, 1)))
    print('control disagreements: %d' % len(dis))

    print('\nreading TARGET pages %s ...' % TARGET_PAGES, flush=True)
    tgt = gather(geo, canon, tmpl, TARGET_PAGES)
    hit2, tot2, dis2 = score(tgt, mapping)
    print('TARGET forced-seg agreement: %d/%d = %.2f%%' % (hit2, tot2, 100.0 * hit2 / max(tot2, 1)))

    conf = collections.Counter((d['image'], d['canon']) for d in dis2)
    out = dict(
        control_pages=CONTROL_PAGES, target_pages=TARGET_PAGES,
        n_control_classes=len(classes),
        control_agreement=100.0 * hit / max(tot, 1), control_compared=tot,
        control_disagreements=len(dis),
        target_agreement=100.0 * hit2 / max(tot2, 1), target_compared=tot2,
        target_disagreements=len(dis2),
        mapping={str(k): int(v) for k, v in mapping.items()},
        target_confusions=[[a, b, n] for (a, b), n in conf.most_common(40)],
        target_dis_detail=dis2,
    )
    json.dump(out, open(os.path.join(HERE, 'results.json'), 'w'), indent=1)
    print('\nwrote results.json')
    print('top target confusions (image->canon):')
    for (a, b), n in conf.most_common(15):
        print('  %-4s -> %-4s  %d' % (a, b, n))

if __name__ == '__main__':
    main()
