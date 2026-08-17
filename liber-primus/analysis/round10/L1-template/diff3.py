"""L1-TEMPLATE stage 3 -- diff the label-free read against canon.

Instrument: read4.json, one record per rune-candidate connected component,
labelled by exact-pixel template match against a 29-class alphabet recovered
from the images alone.  90.8% of components match their template at distance
0.00; median runner-up margin 117.6.

Page -> canonical segment map (established in page_map.log from component and
line counts, and cross-checked against the relikd section files, which total
729/1145/1729/1903/1021/1433/1680 runes for segment groups 0-2, 3-7, 8-14,
15-22, 23-26, 27-32, 33-39 -- identical to canon):

    p0..p49  -> seg 0..49        p50, p51 -> seg 50  (the base-60 table spread)
    p52->51   p53->52   p54->53   p55->54

The class->rune permutation is fitted by maximising agreement on lines whose
component count equals the canonical line length.  29 labels against ~12,000
glyph identities: canon cannot be laundered through a channel that narrow.

Then every page is aligned by Needleman-Wunsch (match 0 / substitute 1 / gap 1)
so that SEGMENTATION events (insertions = non-rune components that survived the
filter, deletions = drop caps and touching runes) are separated from IDENTITY
events (substitutions = a genuine transcription divergence).

Null controls: N1 random label permutations, N2 shuffled canon lines,
N3 shuffled image stream doublet rate, N4 planted doublets.
"""
import os, sys, json, collections, random
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'src'))
from lp.gematria import RUNE_TO_IDX, IDX_TO_TRANS

PAGE2SEG = {p: p for p in range(50)}
PAGE2SEG.update({50: 50, 51: 50, 52: 51, 53: 52, 54: 53, 55: 54})

recs = json.load(open(os.path.join(HERE, 'read4.json')))
txt = open(os.path.join(ROOT, 'data', 'krisyotam_runes.txt'), encoding='utf-8').read()
segs = txt.split('%')
canon_lines = {}
for si, s in enumerate(segs):
    ls = [[RUNE_TO_IDX[c] for c in ln if c in RUNE_TO_IDX] for ln in s.split('/')]
    canon_lines[si] = [l for l in ls if l]

# image lines: (page, band) ordered by x
# BASELINE FILTER (canon-free): the runes of a line share a baseline and a
# height; margin-ornament fragments that survive the height filter do not.
# Keep a component only if its top y and its height are both within TOL px of
# the band's modal value.  Nothing canonical is consulted.
TOL = int(os.environ.get('TOL', '5'))
raw = collections.defaultdict(list)
for r in recs:
    raw[(r['page'], r['band'])].append(r)
img = collections.defaultdict(list)
n_drop = 0
for k, v in raw.items():
    ys = collections.Counter(r['y'] // 2 * 2 for r in v)
    hs = collections.Counter(r['h'] for r in v)
    my = ys.most_common(1)[0][0]; mh = hs.most_common(1)[0][0]
    for r in v:
        if abs(r['y'] - my) <= TOL and abs(r['h'] - mh) <= TOL:
            img[k].append(r)
        else:
            n_drop += 1
print('baseline filter: dropped %d of %d components (TOL=%d)' % (n_drop, len(recs), TOL))
for k in img:
    img[k].sort(key=lambda r: r['x'])
img_lines = collections.defaultdict(list)          # page -> [ [rec,...], ... ]
for (p, b) in sorted(img, key=lambda t: (t[0], t[1])):
    img_lines[p].append(img[(p, b)])

# segment -> list of (page, line index within page)
seg_img = collections.defaultdict(list)
for p in sorted(img_lines):
    for li, L in enumerate(img_lines[p]):
        seg_img[PAGE2SEG[p]].append((p, li, L))


def nw(a, b, sub_cost, gap=1.0):
    """global alignment; returns list of (i or None, j or None)"""
    na, nb = len(a), len(b)
    D = np.zeros((na + 1, nb + 1)); B = np.zeros((na + 1, nb + 1), np.int8)
    D[:, 0] = np.arange(na + 1) * gap; B[1:, 0] = 2
    D[0, :] = np.arange(nb + 1) * gap; B[0, 1:] = 3
    for i in range(1, na + 1):
        ai = a[i - 1]
        row = D[i - 1]
        for j in range(1, nb + 1):
            s = row[j - 1] + sub_cost(ai, b[j - 1])
            u = D[i - 1, j] + gap
            l = D[i, j - 1] + gap
            if s <= u and s <= l:
                D[i, j] = s; B[i, j] = 1
            elif u <= l:
                D[i, j] = u; B[i, j] = 2
            else:
                D[i, j] = l; B[i, j] = 3
    out = []; i, j = na, nb
    while i > 0 or j > 0:
        m = B[i, j]
        if m == 1:
            out.append((i - 1, j - 1)); i -= 1; j -= 1
        elif m == 2:
            out.append((i - 1, None)); i -= 1
        else:
            out.append((None, j - 1)); j -= 1
    out.reverse()
    return out, float(D[na, nb])


def line_pairs():
    """per segment, align image lines to canon lines on counts (DP), return pairs"""
    pairs = []
    for si in sorted(seg_img):
        IL = seg_img[si]; CL = canon_lines[si]
        A = [len(x[2]) for x in IL]; B = [len(x) for x in CL]
        na, nb = len(A), len(B)
        INF = 1e9
        D = np.full((na + 1, nb + 1), INF); Bk = np.zeros((na + 1, nb + 1), np.int8)
        D[0, 0] = 0
        for i in range(na + 1):
            for j in range(nb + 1):
                if D[i, j] >= INF:
                    continue
                if i < na and j < nb:
                    c = D[i, j] + abs(A[i] - B[j])
                    if c < D[i + 1, j + 1]:
                        D[i + 1, j + 1] = c; Bk[i + 1, j + 1] = 1
                if i < na:
                    c = D[i, j] + 25
                    if c < D[i + 1, j]:
                        D[i + 1, j] = c; Bk[i + 1, j] = 2
                if j < nb:
                    c = D[i, j] + 25
                    if c < D[i, j + 1]:
                        D[i, j + 1] = c; Bk[i, j + 1] = 3
        i, j = na, nb
        while i > 0 or j > 0:
            m = Bk[i, j]
            if m == 1:
                pairs.append((si, IL[i - 1], CL[j - 1])); i -= 1; j -= 1
            elif m == 2:
                pairs.append((si, IL[i - 1], None)); i -= 1
            else:
                pairs.append((si, None, CL[j - 1])); j -= 1
    pairs.reverse()
    return pairs


def main():
    pairs = line_pairs()
    matched = [(si, I, C) for si, I, C in pairs if I is not None and C is not None]
    exact = [(si, I, C) for si, I, C in matched if len(I[2]) == len(C)]
    print('image lines %d (%d comps) | canon lines %d (%d runes)'
          % (sum(len(v) for v in img_lines.values()), len(recs),
             sum(len(canon_lines[s]) for s in seg_img),
             sum(len(l) for s in seg_img for l in canon_lines[s])))
    print('line pairs matched %d | count-exact lines %d (%.1f%%)'
          % (len(matched), len(exact), 100.0 * len(exact) / max(len(matched), 1)))

    classes = sorted({r['cls'] for r in recs})
    ci = {c: k for k, c in enumerate(classes)}
    M = np.zeros((len(classes), 29), np.int64)
    for si, I, C in exact:
        for r, ru in zip(I[2], C):
            M[ci[r['cls']], ru] += 1
    from scipy.optimize import linear_sum_assignment
    rr, cceq = linear_sum_assignment(-M)
    mapping = {classes[r]: int(c) for r, c in zip(rr, cceq)}
    hit = sum(M[ci[c], v] for c, v in mapping.items()); tot = int(M.sum())
    print('\nclass->rune bijection over %d classes; agreement on count-exact '
          'lines %d/%d = %.3f%%' % (len(mapping), hit, tot, 100.0 * hit / tot))

    # ---- N1 null: random permutations
    ks = list(mapping.keys()); vs = list(mapping.values())
    null = []
    rng = random.Random(3301)
    for _ in range(200):
        w = vs[:]; rng.shuffle(w)
        null.append(sum(M[ci[k], v] for k, v in zip(ks, w)) / tot)
    null = np.array(null)
    print('N1 label-permutation null: mean %.4f  sd %.4f  max %.4f   -> z = %.1f'
          % (null.mean(), null.std(), null.max(),
             (hit / tot - null.mean()) / max(null.std(), 1e-9)))

    # ---- full NW alignment per line, with the frozen mapping
    def sc(rec, ru):
        return 0.0 if mapping.get(rec['cls'], -1) == ru else 1.0
    subs, ins, dels = [], [], []
    n_al = 0
    for si, I, C in matched:
        al, _ = nw(I[2], C, sc)
        for a, b in al:
            n_al += 1
            if a is None:
                dels.append(dict(seg=si, page=I[0], line=I[1], ci=b,
                                 canon=IDX_TO_TRANS[C[b]]))
            elif b is None:
                r = I[2][a]
                ins.append(dict(seg=si, page=I[0], line=I[1], x=r['x'], y=r['y'],
                                w=r['w'], h=r['h'], d1=r['d1'],
                                image=IDX_TO_TRANS[mapping.get(r['cls'], 0)]))
            else:
                r = I[2][a]
                if mapping.get(r['cls'], -1) != C[b]:
                    subs.append(dict(seg=si, page=I[0], line=I[1], x=r['x'], y=r['y'],
                                     w=r['w'], h=r['h'], d1=r['d1'], d2=r['d2'],
                                     comp=r['comp'],
                                     image=IDX_TO_TRANS[mapping.get(r['cls'], 0)],
                                     canon=IDX_TO_TRANS[C[b]]))
    n_comp = sum(len(I[2]) for si, I, C in matched)
    n_run = sum(len(C) for si, I, C in matched)
    print('\nNW over matched lines: %d comps vs %d runes' % (n_comp, n_run))
    print('  substitutions %d  (%.3f%% of runes)' % (len(subs), 100.0 * len(subs) / n_run))
    print('  insertions    %d  (image has a component canon has no rune for)' % len(ins))
    print('  deletions     %d  (canon has a rune the image read has no component for)' % len(dels))
    cnt = collections.Counter((d['image'], d['canon']) for d in subs)
    print('\ntop substitutions (image -> canon):')
    for (a, b), n in cnt.most_common(15):
        print('   %-4s -> %-4s  %4d   (%.3f%% of runes)' % (a, b, n, 100.0 * n / n_run))
    print('\nsubstitution d1 (match distance) distribution:')
    dd = np.array([s['d1'] for s in subs]) if subs else np.array([0.])
    print('   median %.1f  frac exact(d1<=0.01) %.3f  frac d1>200 %.3f'
          % (np.median(dd), float((dd <= 0.01).mean()), float((dd > 200).mean())))
    print('insertion d1: median %.1f  frac d1>200 %.3f'
          % (np.median([i['d1'] for i in ins]) if ins else -1,
             float(np.mean([i['d1'] > 200 for i in ins])) if ins else -1))

    # ---- N2 null: shuffled canon lines
    rng2 = random.Random(31337)
    allc = [C for si, I, C in matched]
    sh = allc[:]; rng2.shuffle(sh)
    bad = 0; tot2 = 0
    for (si, I, C), C2 in zip(matched, sh):
        n = min(len(I[2]), len(C2))
        for r, ru in zip(I[2][:n], C2[:n]):
            tot2 += 1
            if mapping.get(r['cls'], -1) != ru:
                bad += 1
    print('\nN2 shuffled-canon null: agreement %.4f (expected ~%.4f)'
          % (1 - bad / tot2, 1 / 29))

    # ---- T3 doublet, mapping-free
    def dbl(seq):
        if len(seq) < 2:
            return 0, 0
        return sum(1 for i in range(len(seq) - 1) if seq[i] == seq[i + 1]), len(seq) - 1
    ai = ac = bi = bc = 0
    for si, I, C in exact:
        a, b = dbl([r['cls'] for r in I[2]]); ai += a; ac += b
        a, b = dbl(C); bi += a; bc += b
    print('\nT3 DOUBLET (count-exact lines, mapping-free):')
    print('   image-read adjacent-equal classes %d / %d = %.3f%%' % (ai, ac, 100.0 * ai / max(ac, 1)))
    print('   canon      adjacent-equal runes   %d / %d = %.3f%%' % (bi, bc, 100.0 * bi / max(bc, 1)))
    # over ALL matched lines too
    ai2 = ac2 = 0
    for si, I, C in matched:
        a, b = dbl([r['cls'] for r in I[2]]); ai2 += a; ac2 += b
    print('   image-read over ALL matched lines %d / %d = %.3f%%' % (ai2, ac2, 100.0 * ai2 / max(ac2, 1)))
    # N3 shuffled image stream
    flat = [r['cls'] for si, I, C in matched for r in I[2]]
    rng3 = random.Random(99)
    rates = []
    for _ in range(50):
        f = flat[:]; rng3.shuffle(f)
        a, b = dbl(f); rates.append(100.0 * a / b)
    print('   N3 shuffled-image null doublet %.3f%% +/- %.3f%%' % (np.mean(rates), np.std(rates)))
    # N4 planted doublets: can the statistic see them?
    f = flat[:]
    for i in range(0, len(f) - 1, 200):
        f[i + 1] = f[i]
    a, b = dbl(f)
    print('   N4 planted (1 per 200) -> %.3f%% (expect ~%.3f%%)' % (100.0 * a / b, 100.0 / 200 + 100.0 * ai2 / ac2))

    json.dump(dict(mapping={str(k): int(v) for k, v in mapping.items()},
                   n_comp=n_comp, n_runes=n_run,
                   agreement_exact=100.0 * hit / tot,
                   n_sub=len(subs), n_ins=len(ins), n_del=len(dels),
                   null_perm_mean=float(null.mean()), null_perm_sd=float(null.std()),
                   doublet_image_exact=100.0 * ai / max(ac, 1),
                   doublet_canon_exact=100.0 * bi / max(bc, 1),
                   doublet_image_all=100.0 * ai2 / max(ac2, 1),
                   doublet_null=float(np.mean(rates)),
                   confusions=[[a, b, n] for (a, b), n in cnt.most_common(60)],
                   subs=subs, ins=ins[:400], dels=dels[:400]),
              open(os.path.join(HERE, os.environ.get('REPORT','diff3_report.json')), 'w'), indent=1)
    print('\nwrote ' + os.environ.get('REPORT', 'diff3_report.json'))


if __name__ == '__main__':
    main()
