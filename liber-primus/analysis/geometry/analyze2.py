"""Track GEOMETRY — stage 2 (v2): the four measurements, on v2 segmentation.

  A. GLYPH-SHAPE OUTLIERS  (decisive: a font render must repeat each rune exactly)
  B. INTER-GLYPH ADVANCE   (micro-spacing channel; separator gaps excluded)
  C. BASELINE JITTER       (within rune class)
  D. ORNAMENT INVENTORY    (what every prior pipeline discarded)

Image lines are aligned to canonical lines by DP over per-line rune counts,
allowing image bands to be skipped (headers/ornaments). Only lines that align
with an exact count match are used for the labelled tests, and that coverage is
reported rather than assumed.
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


def crop(i):
    return np.unpackbits(crop_packed[i], axis=-1)[:, :CAN].astype(np.float32)


def jd(o):
    if isinstance(o, np.integer): return int(o)
    if isinstance(o, np.floating): return float(o)
    raise TypeError(str(type(o)))


# ------------------------------------------------------------- image lines
img = collections.OrderedDict()
for i in range(len(page)):
    img.setdefault(int(line[i]), []).append(i)
img_lines = []
for ln, idxs in img.items():
    idxs.sort(key=lambda j: x0[j])
    runes = [j for j in idxs if not SEP[j]]
    seps = [j for j in idxs if SEP[j]]
    img_lines.append((int(page[idxs[0]]), runes, seps))

# ---------------------------------------------------------- canonical lines
txt = open(os.path.join(ROOT, 'data', 'krisyotam_runes.txt'), encoding='utf-8').read()
canon = []
for si, seg in enumerate(txt.split('%')):
    for ln in seg.split('/'):
        rs = [RUNE_TO_IDX[c] for c in ln if c in RUNE_TO_IDX]
        if rs:
            canon.append((si, rs))

# ------------------------------------------------- DP alignment on rune counts
A = [len(r) for _, r, _ in img_lines]
Bc = [len(r) for _, r in canon]
na, nb = len(A), len(Bc)
INF = 10**9
dp = np.full((na+1, nb+1), INF, np.int64)
bk = np.zeros((na+1, nb+1), np.int8)
dp[0, 0] = 0
for i in range(na+1):
    for j in range(nb+1):
        if dp[i, j] == INF:
            continue
        if i < na and j < nb:
            c = dp[i, j] + abs(A[i]-Bc[j])
            if c < dp[i+1, j+1]:
                dp[i+1, j+1] = c; bk[i+1, j+1] = 1
        if i < na:                      # image band skipped (ornament/header)
            c = dp[i, j] + 12
            if c < dp[i+1, j]:
                dp[i+1, j] = c; bk[i+1, j] = 2
        if j < nb:                      # canonical line has no image band
            c = dp[i, j] + 12
            if c < dp[i, j+1]:
                dp[i, j+1] = c; bk[i, j+1] = 3
pairs, skipped_img = [], []
i, j = na, nb
while i > 0 or j > 0:
    m = bk[i, j]
    if m == 1:
        pairs.append((i-1, j-1)); i -= 1; j -= 1
    elif m == 2:
        skipped_img.append(i-1); i -= 1
    else:
        j -= 1
pairs.reverse()
exact = [(a, b) for a, b in pairs if A[a] == Bc[b]]
print('image bands %d | canonical lines %d | aligned %d | exact-count %d (%.1f%%)'
      % (na, nb, len(pairs), len(exact), 100.0*len(exact)/nb))
print('image bands skipped as non-text: %d' % len(skipped_img))

rep = dict(image_bands=na, canon_lines=nb, aligned=len(pairs),
           exact_lines=len(exact), skipped_bands=len(skipped_img))


def gmm(x, k, iters=300):
    mu = np.quantile(x, np.linspace(0.2, 0.8, k))
    sd = np.full(k, x.std()/k + 1e-6); w = np.full(k, 1.0/k)
    for _ in range(iters):
        pr = np.stack([w[t]*np.exp(-0.5*((x-mu[t])/sd[t])**2)/(sd[t]*np.sqrt(2*np.pi))
                       for t in range(k)]) + 1e-300
        r = pr/pr.sum(0); nk = r.sum(1)
        w = nk/len(x); mu = (r*x).sum(1)/nk
        sd = np.sqrt((r*(x-mu[:, None])**2).sum(1)/nk) + 1e-6
    ll = np.log(np.stack([w[t]*np.exp(-0.5*((x-mu[t])/sd[t])**2)/(sd[t]*np.sqrt(2*np.pi))
                          for t in range(k)]).sum(0)+1e-300).sum()
    return -2*ll + (3*k-1)*np.log(len(x)), mu, sd, w


# ------------------------------------------------- B. advance, separator-free
gaps = []
for p, runes, seps in img_lines:
    sx = [(x0[s]+x1[s])/2 for s in seps]
    for a, b in zip(runes, runes[1:]):
        if any(x1[a]-6 <= s <= x0[b]+6 for s in sx):
            continue
        g = x0[b] - x1[a]
        if -20 < g < 60:
            gaps.append(g)
gaps = np.array(gaps, float)
print('\n--- B. inter-glyph advance, separator-free (n=%d) ---' % len(gaps))
print('mean %.2f sd %.2f  pct %s' % (gaps.mean(), gaps.std(),
      np.percentile(gaps, [1, 5, 25, 50, 75, 95, 99]).round(1)))
b1, *_ = gmm(gaps, 1); b2, mu2, sd2, w2 = gmm(gaps, 2)
sep_sig = float(abs(mu2[1]-mu2[0])/sd2.mean())
print('BIC 1comp %.0f 2comp %.0f delta %.0f | means %s sd %s w %s | sep %.2f sigma'
      % (b1, b2, b1-b2, mu2.round(2), sd2.round(2), w2.round(3), sep_sig))
uniq = np.unique(gaps)
print('distinct integer gap values: %d, range %d..%d' % (len(uniq), uniq.min(), uniq.max()))
rep['advance'] = dict(n=len(gaps), mean=float(gaps.mean()), sd=float(gaps.std()),
                      bic1=float(b1), bic2=float(b2), sep_sigma=sep_sig,
                      means=mu2.round(3).tolist(), weights=w2.round(4).tolist())

# ------------------------------------------------------------ label glyphs
gl, lab = [], []
for a, b in exact:
    for q, r in zip(img_lines[a][1], canon[b][1]):
        gl.append(q); lab.append(r)
lab = np.array(lab); gl = np.array(gl)
print('\nlabelled glyphs: %d / %d canonical runes (%.1f%%)'
      % (len(gl), sum(Bc), 100.0*len(gl)/sum(Bc)))
rep['labelled'] = int(len(gl))

# --------------------------------------------- C. baseline within rune class
base = []
for a, b in exact:
    runes = img_lines[a][1]
    med = np.median([y1[q] for q in runes])
    for q in runes:
        base.append(y1[q] - med)
base = np.array(base, float)
wc = []
for r in range(29):
    m = lab == r
    if m.sum() < 30:
        continue
    v = base[m]
    wc.append(v - np.median(v))
wc = np.concatenate(wc)
print('\n--- C. baseline offset within rune class (n=%d) ---' % len(wc))
print('sd %.3f  pct %s' % (wc.std(), np.percentile(wc, [1, 5, 25, 50, 75, 95, 99]).round(1)))
b1, *_ = gmm(wc, 1); b2, mu2, sd2, w2 = gmm(wc, 2)
print('BIC 1comp %.0f 2comp %.0f delta %.0f | means %s' % (b1, b2, b1-b2, mu2.round(2)))
rep['baseline'] = dict(n=int(len(wc)), sd=float(wc.std()), bic1=float(b1),
                       bic2=float(b2), means=mu2.round(3).tolist())

# --------------------------------------------------- A. glyph-shape outliers
print('\n--- A. glyph-shape outliers (decisive test) ---')
print('%-5s %5s %9s %8s %8s %8s' % ('rune', 'n', 'resid', 'sd', 'maxz', 'worst'))
rows, outl = [], []
for r in range(29):
    m = np.where(lab == r)[0]
    if len(m) < 25:
        continue
    X = np.stack([crop(gl[k]) for k in m])
    mean = X.mean(0)
    # sub-pixel-free alignment: crops are already centred on the glyph centroid
    # box; residual = fraction of pixels differing from the class consensus mask
    cons = (mean > 0.5).astype(np.float32)
    resid = np.abs(X - cons).mean(axis=(1, 2)) * (CAN * CAN) / np.maximum(cons.sum(), 1)
    mu, sd = resid.mean(), resid.std()
    z = (resid - mu) / (sd + 1e-9)
    k = int(np.argmax(z))
    gi = gl[m[k]]
    rows.append((IDX_TO_TRANS[r], len(m), float(mu), float(sd), float(z.max()),
                 int(page[gi]), int(x0[gi]), int(y0[gi])))
    for kk in np.argsort(z)[::-1][:6]:
        if z[kk] > 5:
            g2 = gl[m[kk]]
            outl.append(dict(rune=IDX_TO_TRANS[r], z=float(z[kk]), page=int(page[g2]),
                             x=int(x0[g2]), y=int(y0[g2]), resid=float(resid[kk])))
rows.sort(key=lambda t: -t[4])
for t in rows[:12]:
    print('%-5s %5d %9.4f %8.4f %8.2f  p%d@(%d,%d)' %
          (t[0], t[1], t[2], t[3], t[4], t[5], t[6], t[7]))
print('classes measured %d | instances z>5: %d' % (len(rows), len(outl)))
rep['shape'] = dict(classes=len(rows), max_z=max(t[4] for t in rows),
                    mean_resid=float(np.mean([t[2] for t in rows])),
                    outliers=outl[:40])

# --------------------------------------------------------------- D. ornaments
orn = []
for a in skipped_img:
    p, runes, seps = img_lines[a]
    if not runes:
        continue
    orn.append(dict(page=int(p), n=len(runes),
                    x=[int(min(x0[q] for q in runes)), int(max(x1[q] for q in runes))],
                    y=[int(min(y0[q] for q in runes)), int(max(y1[q] for q in runes))],
                    medh=int(np.median([H[q] for q in runes]))))
print('\n--- D. non-text bands (never analysed by any prior pipeline) ---')
print('bands: %d across %d pages' % (len(orn), len(set(o['page'] for o in orn))))
cnt = collections.Counter(o['n'] for o in orn)
print('glyph-count histogram of those bands:', dict(sorted(cnt.items())[:12]))
rep['ornaments'] = orn

json.dump(rep, open(os.path.join(HERE, 'geometry_report.json'), 'w'), indent=1, default=jd)
print('\nwrote geometry_report.json')
