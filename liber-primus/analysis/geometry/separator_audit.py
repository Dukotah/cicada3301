"""Audit the WORD SEPARATORS against the page images.

Every transcription-verification effort in this repo compared RUNE STREAMS:
`analysis/transcription/crossdiff.py` found krisyotam / relikd / rtkd identical
13,136 / 13,136, and the vision armada tried to re-read runes. Nobody has ever
checked the *separators*. They are a different object, they descend from the same
single root transcription (rtkd/iddqd 2017), and every downstream attack that
depends on word boundaries -- including this round's SKELETON track -- inherits
whatever errors they contain.

Motivation for looking: LP2's rune-word length (mean 4.43) is longer than
English-in-futhorc (4.10-4.15) by more than all 458 interrupters can account for
(they supply +0.156 runes/word; the gap is +0.32). A small number of MISSING word
separators would produce exactly that -- two words read as one long word.

Method: separator dots are a distinct component class in the render (a uniform
~9x10 px square; 3,027 of them). Compare the dot count per LINE against the
transcription's separator count per line, using the line alignment from
analyze2.py. Per-PAGE comparison is invalid: relikd image numbering != krisyotam
page numbering (see stones/pipeline.py -- relikd p54 == krisyotam page 53), which
is why this works line-wise off the DP alignment instead.
"""
import os, sys, json, collections
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'src'))
from lp.gematria import RUNE_TO_IDX

d = np.load(os.path.join(HERE, 'glyphs2.npz'))
page, line, x0, y0, x1, y1 = d['page'], d['line'], d['x0'], d['y0'], d['x1'], d['y1']
H = (y1 - y0).astype(int)
SEP = H < 30

img = collections.OrderedDict()
for i in range(len(page)):
    img.setdefault(int(line[i]), []).append(i)
img_lines = []
for ln, idxs in img.items():
    idxs.sort(key=lambda j: x0[j])
    img_lines.append(([j for j in idxs if not SEP[j]],
                      [j for j in idxs if SEP[j]]))

txt = open(os.path.join(ROOT, 'data', 'krisyotam_runes.txt'), encoding='utf-8').read()
canon = []
for seg in txt.split('%'):
    for ln in seg.split('/'):
        rs = [c for c in ln if c in RUNE_TO_IDX]
        if rs:
            canon.append((len(rs), ln.count('-'), ln.count('.')))

A = [len(r) for r, _ in img_lines]
B = [c[0] for c in canon]
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
            c = dp[i, j] + 12
            if c < dp[i+1, j]:
                dp[i+1, j] = c; bk[i+1, j] = 2
        if j < nb:
            c = dp[i, j] + 12
            if c < dp[i, j+1]:
                dp[i, j+1] = c; bk[i, j+1] = 3
pairs = []
i, j = na, nb
while i > 0 or j > 0:
    m = bk[i, j]
    if m == 1:
        pairs.append((i-1, j-1)); i -= 1; j -= 1
    elif m == 2:
        i -= 1
    else:
        j -= 1
pairs.reverse()
exact = [(a, b) for a, b in pairs if A[a] == B[b]]
print('aligned lines %d | rune-count-exact lines %d' % (len(pairs), len(exact)))

# on rune-exact lines the segmentation is trustworthy, so separator counts are
# comparable. Solve for dots-per-title-mark first on lines with no title mark.
no_title = [(a, b) for a, b in exact if canon[b][2] == 0]
diffs = np.array([len(img_lines[a][1]) - canon[b][1] for a, b in no_title])
print('\nlines with NO title mark: %d' % len(no_title))
print('image dots minus transcription separators: mean %+.3f  sd %.3f'
      % (diffs.mean(), diffs.std()))
h = collections.Counter(diffs.tolist())
print('difference histogram:', dict(sorted(h.items())))
agree = int((diffs == 0).sum())
print('lines in exact agreement: %d/%d (%.1f%%)'
      % (agree, len(diffs), 100.0*agree/max(len(diffs), 1)))

sus = [(a, b, int(len(img_lines[a][1]) - canon[b][1]))
       for a, b in no_title if len(img_lines[a][1]) != canon[b][1]]
print('\nlines where the image and the transcription disagree: %d' % len(sus))
for a, b, dd in sus[:20]:
    gi = img_lines[a][0][0]
    print('   img line %d (page %d, y=%d): %d dots vs %d separators  (%+d)'
          % (a, page[gi], y0[gi], len(img_lines[a][1]), canon[b][1], dd))

json.dump(dict(aligned=len(pairs), exact=len(exact), no_title=len(no_title),
               mean_diff=float(diffs.mean()) if len(diffs) else None,
               agree=agree, disagreements=[[int(x) for x in s] for s in sus]),
          open(os.path.join(HERE, 'separator_audit.json'), 'w'), indent=1)
print('\nwrote separator_audit.json')
