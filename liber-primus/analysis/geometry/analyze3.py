"""Track GEOMETRY — stage 3: corrected shape and spacing tests.

Two fixes over stage 2:

  A. SHAPE. Stage 2 compared 160px crops centred on each glyph, so adjacent
     glyphs intruded into the window and dominated the residual (values >1.0 of
     the mask area). Here each glyph is masked to its OWN bounding box before
     comparison. Two independent shape statistics are reported:
       A1  bbox metrics (width, height, ink area) per rune class -- needs no
           alignment at all, so it cannot be broken by registration error. In a
           font render at fixed size these must be constant to within
           rasterisation phase (+/-1 px).
       A2  masked-bitmap residual against the class consensus, after registering
           each instance on its bbox.

  B. SPACING. Stage 2 measured raw ink gaps, which mix glyph-shape variation
     (a rune's right edge shape) into the spacing signal. Here we measure PITCH
     residual: (x0[i+1] - x0[i]) minus the median pitch for the class of glyph i.
     That isolates the typesetter's advance decision, which is what a
     micro-spacing channel would modulate.
"""
import os, sys, json, collections
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'src'))
from lp.gematria import RUNE_TO_IDX, IDX_TO_TRANS

CAN = 160
d = np.load(os.path.join(HERE, 'glyphs2.npz'))
page, line, x0, y0, x1, y1, area = (d['page'], d['line'], d['x0'], d['y0'],
                                    d['x1'], d['y1'], d['area'])
crop_packed = d['crop']
H, W = y1 - y0, x1 - x0
SEP = H < 30


def masked(i):
    """the glyph's own ink, isolated from neighbours, as a (h,w) mask"""
    c = np.unpackbits(crop_packed[i], axis=-1)[:, :CAN]
    cy, cx = CAN // 2, CAN // 2
    h, w = int(H[i]), int(W[i])
    top = cy - (h + 1) // 2
    left = cx - (w + 1) // 2
    return c[max(0, top):max(0, top)+h, max(0, left):max(0, left)+w]


def jd(o):
    if isinstance(o, np.integer): return int(o)
    if isinstance(o, np.floating): return float(o)
    raise TypeError(str(type(o)))


# ---------------------------------------------- rebuild the stage-2 alignment
img = collections.OrderedDict()
for i in range(len(page)):
    img.setdefault(int(line[i]), []).append(i)
img_lines = []
for ln, idxs in img.items():
    idxs.sort(key=lambda j: x0[j])
    img_lines.append((int(page[idxs[0]]),
                      [j for j in idxs if not SEP[j]],
                      [j for j in idxs if SEP[j]]))

txt = open(os.path.join(ROOT, 'data', 'krisyotam_runes.txt'), encoding='utf-8').read()
canon = []
for si, seg in enumerate(txt.split('%')):
    for ln in seg.split('/'):
        rs = [RUNE_TO_IDX[c] for c in ln if c in RUNE_TO_IDX]
        if rs:
            canon.append((si, rs))

A_ = [len(r) for _, r, _ in img_lines]
B_ = [len(r) for _, r in canon]
na, nb = len(A_), len(B_)
INF = 10**9
dp = np.full((na+1, nb+1), INF, np.int64); bk = np.zeros((na+1, nb+1), np.int8)
dp[0, 0] = 0
for i in range(na+1):
    for j in range(nb+1):
        if dp[i, j] == INF: continue
        if i < na and j < nb:
            c = dp[i, j] + abs(A_[i]-B_[j])
            if c < dp[i+1, j+1]: dp[i+1, j+1] = c; bk[i+1, j+1] = 1
        if i < na:
            c = dp[i, j] + 12
            if c < dp[i+1, j]: dp[i+1, j] = c; bk[i+1, j] = 2
        if j < nb:
            c = dp[i, j] + 12
            if c < dp[i, j+1]: dp[i, j+1] = c; bk[i, j+1] = 3
pairs, skipped = [], []
i, j = na, nb
while i > 0 or j > 0:
    m = bk[i, j]
    if m == 1: pairs.append((i-1, j-1)); i -= 1; j -= 1
    elif m == 2: skipped.append(i-1); i -= 1
    else: j -= 1
pairs.reverse()
exact = [(a, b) for a, b in pairs if A_[a] == B_[b]]

gl, lab, nxt = [], [], []
for a, b in exact:
    runes = img_lines[a][1]
    for k, (q, r) in enumerate(zip(runes, canon[b][1])):
        gl.append(q); lab.append(r)
        nxt.append(runes[k+1] if k+1 < len(runes) else -1)
gl = np.array(gl); lab = np.array(lab); nxt = np.array(nxt)
print('labelled glyphs: %d across %d exact-count lines' % (len(gl), len(exact)))

rep = {'labelled': int(len(gl)), 'exact_lines': len(exact)}

# ------------------------------------------ A1. bbox metrics per rune class
print('\n--- A1. bbox metrics per rune class (alignment-free) ---')
print('%-5s %5s  %-16s %-16s %-18s' % ('rune', 'n', 'width', 'height', 'ink area'))
a1 = {}
worst = []
for r in range(29):
    m = np.where(lab == r)[0]
    if len(m) < 25: continue
    w, h, ar = W[gl[m]], H[gl[m]], area[gl[m]]
    a1[IDX_TO_TRANS[r]] = dict(n=int(len(m)),
                               w=[int(w.min()), int(np.median(w)), int(w.max())],
                               h=[int(h.min()), int(np.median(h)), int(h.max())],
                               area_sd_pct=float(100*ar.std()/ar.mean()))
    print('%-5s %5d  %3d/%3d/%-3d      %3d/%3d/%-3d      med %5d sd %4.1f%%'
          % (IDX_TO_TRANS[r], len(m), w.min(), np.median(w), w.max(),
             h.min(), np.median(h), h.max(), np.median(ar), 100*ar.std()/ar.mean()))
    # flag instances more than 3 px off the class median in either dimension
    dev = (np.abs(w - np.median(w)) > 3) | (np.abs(h - np.median(h)) > 3)
    for k in np.where(dev)[0]:
        worst.append(dict(rune=IDX_TO_TRANS[r], page=int(page[gl[m[k]]]),
                          x=int(x0[gl[m[k]]]), y=int(y0[gl[m[k]]]),
                          w=int(w[k]), h=int(h[k]),
                          wmed=int(np.median(w)), hmed=int(np.median(h))))
print('instances >3px off their class median bbox: %d / %d' % (len(worst), len(gl)))
rep['bbox'] = a1
rep['bbox_deviants'] = worst[:60]
rep['bbox_deviant_count'] = len(worst)

# --------------------------------- A2. masked-bitmap residual vs class consensus
print('\n--- A2. masked shape residual vs class consensus ---')
print('%-5s %5s %9s %8s %8s  %s' % ('rune', 'n', 'resid', 'sd', 'maxz', 'worst instance'))
rows, outl = [], []
for r in range(29):
    m = np.where(lab == r)[0]
    if len(m) < 25: continue
    hh = int(np.median(H[gl[m]])); ww = int(np.median(W[gl[m]]))
    X = np.zeros((len(m), hh, ww), np.float32)
    for t, k in enumerate(m):
        g = masked(gl[k]).astype(np.float32)
        gh, gw = g.shape
        if gh == 0 or gw == 0: continue
        y = min(gh, hh); x = min(gw, ww)
        X[t, :y, :x] = g[:y, :x]
    cons = (X.mean(0) > 0.5).astype(np.float32)
    denom = max(cons.sum(), 1.0)
    resid = np.abs(X - cons).sum(axis=(1, 2)) / denom
    mu, sd = resid.mean(), resid.std()
    z = (resid - mu) / (sd + 1e-9)
    k = int(np.argmax(z)); gi = gl[m[k]]
    rows.append((IDX_TO_TRANS[r], len(m), float(mu), float(sd), float(z.max()),
                 int(page[gi]), int(x0[gi]), int(y0[gi])))
    for kk in np.argsort(z)[::-1][:6]:
        if z[kk] > 5:
            g2 = gl[m[kk]]
            outl.append(dict(rune=IDX_TO_TRANS[r], z=float(z[kk]),
                             page=int(page[g2]), x=int(x0[g2]), y=int(y0[g2]),
                             resid=float(resid[kk])))
rows.sort(key=lambda t: -t[4])
for t in rows[:12]:
    print('%-5s %5d %9.4f %8.4f %8.2f  p%d@(%d,%d)' % t[:5] + ('' if False else ''))
print('classes %d | max z %.2f | instances z>5: %d'
      % (len(rows), max(t[4] for t in rows), len(outl)))
rep['shape'] = dict(classes=len(rows), max_z=max(t[4] for t in rows),
                    mean_resid=float(np.mean([t[2] for t in rows])),
                    per_class={t[0]: dict(n=t[1], resid=t[2], sd=t[3], maxz=t[4])
                               for t in rows},
                    outliers=outl[:40])

# ------------------------------------------------------ B. pitch residual
print('\n--- B. pitch residual (typesetter advance, glyph shape removed) ---')
pitch_by_class = collections.defaultdict(list)
for t in range(len(gl)):
    if nxt[t] < 0: continue
    if page[gl[t]] != page[nxt[t]]: continue
    p = int(x0[nxt[t]]) - int(x0[gl[t]])
    if 0 < p < 300:
        pitch_by_class[int(lab[t])].append(p)
res = []
for r, v in pitch_by_class.items():
    v = np.array(v, float)
    if len(v) < 25: continue
    res.append(v - np.median(v))
res = np.concatenate(res)
print('n=%d  sd %.3f px  pct %s' % (len(res), res.std(),
      np.percentile(res, [1, 5, 25, 50, 75, 95, 99]).round(1)))
vals, cnts = np.unique(np.round(res).astype(int), return_counts=True)
top = np.argsort(cnts)[::-1][:10]
print('modal residuals:', [(int(vals[t]), int(cnts[t])) for t in sorted(top)])


def gmm(x, k, iters=300):
    mu = np.quantile(x, np.linspace(0.2, 0.8, k))
    sd = np.full(k, x.std()/k + 1e-6); w = np.full(k, 1.0/k)
    for _ in range(iters):
        pr = np.stack([w[t]*np.exp(-0.5*((x-mu[t])/sd[t])**2)/(sd[t]*np.sqrt(2*np.pi))
                       for t in range(k)]) + 1e-300
        rr = pr/pr.sum(0); nk = rr.sum(1)
        w = nk/len(x); mu = (rr*x).sum(1)/nk
        sd = np.sqrt((rr*(x-mu[:, None])**2).sum(1)/nk) + 1e-6
    ll = np.log(np.stack([w[t]*np.exp(-0.5*((x-mu[t])/sd[t])**2)/(sd[t]*np.sqrt(2*np.pi))
                          for t in range(k)]).sum(0)+1e-300).sum()
    return -2*ll + (3*k-1)*np.log(len(x)), mu, sd, w


b1, *_ = gmm(res, 1); b2, mu2, sd2, w2 = gmm(res, 2)
print('BIC 1comp %.0f 2comp %.0f delta %.0f | means %s sd %s w %s'
      % (b1, b2, b1-b2, mu2.round(2), sd2.round(2), w2.round(3)))
print('component separation: %.2f sigma' % (abs(mu2[1]-mu2[0])/sd2.mean()))
rep['pitch'] = dict(n=int(len(res)), sd=float(res.std()), bic1=float(b1),
                    bic2=float(b2), means=mu2.round(3).tolist(),
                    sep_sigma=float(abs(mu2[1]-mu2[0])/sd2.mean()))

json.dump(rep, open(os.path.join(HERE, 'geometry_report3.json'), 'w'),
          indent=1, default=jd)
print('\nwrote geometry_report3.json')
