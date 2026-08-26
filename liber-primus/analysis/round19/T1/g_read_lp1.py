"""G-READ on the LP1 typeface, and the density stratification (PREREG section 3).

LP1 is harder to score than LP2 for a reason that is about the CORPUS, not the reader:
`scream314_lp.md`'s LP1 rune blocks are reflowed (one 'line' carries 99 runes; no image
row holds more than ~25), so there is no per-image ground truth to align against.  What
IS available is the five LP1 sections whose plaintext is known BY DECRYPTION -- A WARNING,
WELCOME, SOME WISDOM, A KOAN, A KOAN (circumference), 1,796 runes, all five reproduced by
`tests/validate.py`.  We concatenate those five rune streams and align them against the
concatenation of all 17 LP1 image reads, so the score is a score on decryption-validated
text and the reflow never enters.

LP1 labels are bootstrapped from the LP2 bank (cross-face nearest exemplar) and then
re-voted on LP1's own crops, exactly as the LP2 labelling was bootstrapped.
"""
import os, sys, json, difflib, collections
import numpy as np
import t1_reader as T, t1_align as A, t1_run as R
from t1_match import Matcher, canvas
sys.path.insert(0, os.path.join(T.LP, 'src'))
from lp.gematria import RUNE_TO_IDX, IDX_TO_TRANS  # noqa: E402
from lp import corpus  # noqa: E402

TR = [IDX_TO_TRANS[i] for i in range(29)]
SOLVED = [('Runes - 01.jpg', 'A WARNING'), ('03.jpg', 'WELCOME'), ('05.jpg', 'SOME WISDOM'),
          ('06.jpg', 'A KOAN'), ('14.jpg - 107.jpg', 'A KOAN (circumference)')]


def lp1_canon():
    out, marks = [], []
    for label, title in SOLVED:
        pg = corpus.page_by_label(label)
        r = [RUNE_TO_IDX[c] for c in pg['runes'] if c in RUNE_TO_IDX]
        marks.append((title, len(out), len(out) + len(r)))
        out += r
    return out, marks


def main():
    # LP2 bank, used to bootstrap LP1
    r2, v2 = R.build('LP2')
    S2 = r2['S']
    ids2 = np.array(sorted(k for k in r2['blab'] if k in S2.sm_pos))
    M2 = Matcher(S2.X[[S2.sm_pos[int(k)] for k in ids2]],
                 np.array([r2['blab'][int(k)] for k in ids2]))

    S1 = A.Stream('LP1')
    canonseq, marks = lp1_canon()
    print('LP1 decryption-validated canon: %d runes over %d sections'
          % (len(canonseq), len(marks)))

    # bootstrap: classify LP1 distinct bitmaps with the LP2 bank
    sm = S1.sm_idx
    lab = {}
    for s in range(0, len(sm), 256):
        ch = sm[s:s + 256]
        L, d0, d1 = M2.match(S1.X[[S1.sm_pos[int(b)] for b in ch]])
        for k, b in enumerate(ch):
            lab[int(b)] = int(L[k])
    for it in range(6):
        pred = np.array([lab.get(int(b), A.OVERSIZE) for b in S1.ids])
        m, f = A.align_page(list(pred), canonseq)
        votes = collections.defaultdict(collections.Counter)
        for a, b in m + f:
            bm = int(S1.ids[a])
            if S1.small[bm]:
                votes[bm][canonseq[b]] += 1
        new = dict(lab)
        for b, c in votes.items():
            new[b] = c.most_common(1)[0][0]
        print('  LP1 iter %d: matched %d/%d = %.4f%% (+%d forced)'
              % (it, len(m), len(canonseq), 100.0 * len(m) / len(canonseq), len(f)))
        if new == lab:
            break
        lab = new

    pred = np.array([lab.get(int(b), A.OVERSIZE) for b in S1.ids])
    sm2 = difflib.SequenceMatcher(None, list(pred), canonseq, autojunk=False)
    conf = np.zeros((29, 29), int)
    eq = rep = ins = dele = 0
    for tag, i1, i2, j1, j2 in sm2.get_opcodes():
        if tag == 'equal':
            eq += i2 - i1
            for k in range(i2 - i1):
                conf[canonseq[j1 + k], pred[i1 + k]] += 1
        elif tag == 'replace':
            if (i2 - i1) == (j2 - j1):
                rep += i2 - i1
                for k in range(i2 - i1):
                    conf[canonseq[j1 + k], pred[i1 + k]] += 1
            else:
                rep += max(i2 - i1, j2 - j1)
        elif tag == 'insert':
            ins += j2 - j1
        else:
            dele += i2 - i1
    hit = np.zeros(len(canonseq), bool)
    for tag, i1, i2, j1, j2 in sm2.get_opcodes():
        if tag == 'equal':
            hit[j1:j2] = True
    persec = []
    for (title, a, b) in marks:
        persec.append(dict(title=title, n=b - a, correct=int(hit[a:b].sum()),
                           accuracy=100.0 * hit[a:b].sum() / (b - a)))
        print('   section %-24s canon %4d correct %4d = %.4f%%'
              % (title, b - a, hit[a:b].sum(), 100.0 * hit[a:b].sum() / (b - a)))
    n = len(canonseq)
    print('\nG-READ-LP1 (decryption-validated LP1 text, flat alignment):')
    print('  canon %d  correct %d = %.4f%%   1:1 wrong %d  canon-with-no-glyph %d'
          '  glyph-with-no-canon %d' % (n, eq, 100.0 * eq / n, rep, ins, dele))
    oae = {}
    print('  O/A/AE block:')
    for a in [TR.index(x) for x in ('O', 'A', 'AE')]:
        tot = conf[a].sum()
        print('    %-3s n=%4d recall %8.4f%%  miscalls %s'
              % (TR[a], tot, 100.0 * conf[a][a] / tot if tot else 0,
                 {TR[j]: int(conf[a][j]) for j in range(29) if j != a and conf[a][j]}))
        for b in [TR.index(x) for x in ('O', 'A', 'AE')]:
            if a != b:
                oae['%s->%s' % (TR[a], TR[b])] = dict(n=int(conf[a][b]), of=int(tot))
    json.dump(dict(sections=persec, n_canon=n, correct=eq, accuracy=100.0 * eq / n, wrong=rep,
                   missing=ins, spurious=dele, conf=conf.tolist(), oae=oae),
              open(os.path.join(T.HERE, 'out_gread_lp1.json'), 'w'), indent=1)
    print('-> out_gread_lp1.json')


if __name__ == '__main__':
    main()
