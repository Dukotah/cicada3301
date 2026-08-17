"""Independent re-transcription — stage 3: recover the alphabet and diff.

Stage 2 read the book as a sequence of TEMPLATE CLASS IDs with no reference to
any transcription. This stage does two things:

 1. Recovers the class -> rune mapping. That is a permutation of ~29 labels,
    chosen to maximise agreement with the canonical transcription. Note the
    information budget: 29 labels are being fitted against ~13,000 glyph
    identities, so canonical cannot be laundered into the result through a
    channel that narrow -- if the image read disagrees systematically, the
    permutation cannot hide it.

 2. Diffs the image read against canonical, line by line, and reports every
    disagreement with page coordinates so it can be adjudicated by eye.

A clean diff retires the last transcription doubt with a measurement rather than
an argument (all three existing lineages descend from one 2017 root, so their
agreement proves consensus, not correctness). A dirty diff is the transcription
discrepancy the program named as one of the three inputs that could reopen the
cryptanalysis.
"""
import os, sys, json, collections
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'src'))
from lp.gematria import RUNE_TO_IDX, IDX_TO_TRANS

read = json.load(open(os.path.join(HERE, 'read_lines.json')))
txt = open(os.path.join(ROOT, 'data', 'krisyotam_runes.txt'), encoding='utf-8').read()
canon = []
for seg in txt.split('%'):
    for ln in seg.split('/'):
        rs = [RUNE_TO_IDX[c] for c in ln if c in RUNE_TO_IDX]
        if rs:
            canon.append(rs)

img = [[g[0] for g in r['glyphs']] for r in read]
meta = [(r['page'], r['glyphs']) for r in read]
A = [len(x) for x in img]
B = [len(x) for x in canon]
print('image lines %d (%d glyphs) | canonical lines %d (%d runes)'
      % (len(A), sum(A), len(B), sum(B)))

# ---- line alignment on counts, image bands may be skipped (headers/ornaments)
na, nb = len(A), len(B)
INF = 10**9
dp = np.full((na+1, nb+1), INF, np.int64); bk = np.zeros((na+1, nb+1), np.int8)
dp[0, 0] = 0
for i in range(na+1):
    for j in range(nb+1):
        if dp[i, j] == INF:
            continue
        if i < na and j < nb:
            c = dp[i, j] + abs(A[i]-B[j])
            if c < dp[i+1, j+1]:
                dp[i+1, j+1] = c; bk[i+1, j+1] = 1
        if i < na:
            c = dp[i, j] + 15
            if c < dp[i+1, j]:
                dp[i+1, j] = c; bk[i+1, j] = 2
        if j < nb:
            c = dp[i, j] + 15
            if c < dp[i, j+1]:
                dp[i, j+1] = c; bk[i, j+1] = 3
pairs, skipped = [], []
i, j = na, nb
while i > 0 or j > 0:
    m = bk[i, j]
    if m == 1:
        pairs.append((i-1, j-1)); i -= 1; j -= 1
    elif m == 2:
        skipped.append(i-1); i -= 1
    else:
        j -= 1
pairs.reverse()
exact = [(a, b) for a, b in pairs if A[a] == B[b]]
print('aligned %d | image bands skipped %d | rune-count-exact lines %d (%.1f%%)'
      % (len(pairs), len(skipped), len(exact), 100.0*len(exact)/nb))

# ---- confusion matrix over count-exact lines, then optimal 1-1 assignment
classes = sorted({c for x in img for c in x})
ci = {c: k for k, c in enumerate(classes)}
M = np.zeros((len(classes), 29), np.int64)
for a, b in exact:
    for c, r in zip(img[a], canon[b]):
        M[ci[c], r] += 1
try:
    from scipy.optimize import linear_sum_assignment
    rr, cc = linear_sum_assignment(-M)
    mapping = {classes[r]: int(c) for r, c in zip(rr, cc)}
except Exception:
    mapping = {}
    used = set()
    for r in np.argsort(-M.max(1)):
        for c in np.argsort(-M[r]):
            if c not in used:
                mapping[classes[r]] = int(c); used.add(int(c)); break
hit = sum(M[ci[c], v] for c, v in mapping.items())
tot = int(M.sum())
print('\nclass->rune assignment recovered for %d classes' % len(mapping))
print('agreement on count-exact lines: %d / %d = %.3f%%' % (hit, tot, 100.0*hit/max(tot, 1)))
unmapped = [c for c in classes if c not in mapping]
if unmapped:
    print('classes with no rune assigned (merge/split artifacts): %s'
          % [(c, int(M[ci[c]].sum())) for c in unmapped])

# ---- per-glyph disagreements
dis = []
for a, b in exact:
    p, gl = meta[a]
    for k, (c, r) in enumerate(zip(img[a], canon[b])):
        m = mapping.get(c)
        if m is None or m == r:
            continue
        dis.append(dict(page=int(p), line=a, pos=k,
                        x=int(gl[k][1]), cost=gl[k][2],
                        image=IDX_TO_TRANS[m], canon=IDX_TO_TRANS[r]))
print('\nper-glyph disagreements on count-exact lines: %d' % len(dis))
cnt = collections.Counter((d['image'], d['canon']) for d in dis)
print('most common confusions (image -> canon):')
for (a_, b_), n in cnt.most_common(12):
    print('   %-4s -> %-4s  %d' % (a_, b_, n))

json.dump(dict(image_lines=len(A), image_glyphs=int(sum(A)),
               canon_lines=len(B), canon_runes=int(sum(B)),
               aligned=len(pairs), exact_lines=len(exact),
               agreement=100.0*hit/max(tot, 1), compared=tot,
               mapping={str(k): int(v) for k, v in mapping.items()},
               confusions=[[a_, b_, n] for (a_, b_), n in cnt.most_common(40)],
               disagreements=dis[:400]),
          open(os.path.join(HERE, 'diff_report.json'), 'w'), indent=1)
print('\nwrote diff_report.json')
