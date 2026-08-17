"""T0c-real — the detection floor measured on a REAL edition difference.

The synthetic indel model in positive_control.py is a model.  This is the same
question with no model in it: take a 2,928-word passage of one English Bible
translation as the "plaintext", plant LP2's interrupter pattern into it, and ask
whether the scan finds the corresponding passage of a DIFFERENT translation that
is sitting in the corpus.

Both translations render the same source text, in the same order, chapter by
chapter -- i.e. exactly the "right work, wrong edition" case that a real attack
against an unknown published plaintext would face.  If the scan cannot bridge
KJV <-> Douay-Rheims, then it can only ever identify a plaintext that is
word-for-word the copy in the corpus.

Windows 2928 / 400 / 120 / 40, because the shorter the window the fewer word
insertions/deletions fall inside it.
"""
import os, sys, json
import numpy as np
import skel, scanner
from positive_control import plant

HERE = os.path.dirname(os.path.abspath(__file__))
RNG = np.random.default_rng(11)


def main():
    extra = tuple(sys.argv[1:])
    C, _ = skel.load_corpus(extra_globs=extra)
    src = [k for k in C if 'douay' in k.lower()]
    tgt = [k for k in C if k.endswith('kjv.txt') or 'kjv' in k.lower()]
    print('source (plant from):', src, ' target in corpus:', tgt)
    if not src or not tgt:
        print('missing a translation pair'); return
    A, B = C[src[0]], C[tgt[0]]

    pats, truth = [], {}
    fracs = [0.15, 0.35, 0.55, 0.75]          # relative positions in the book
    for W in (2928, 400, 120, 40):
        for fr in fracs:
            off = int(fr * (len(A) - W))
            obs, fcp = plant(A[off:off + W], RNG)
            nm = 'X_W%d_f%02d' % (W, int(fr * 100))
            truth[nm] = dict(offset=off, frac=fr, W=W)
            pats.append(scanner.Pattern(nm + ':interval',
                                        skel.groups_interval(obs, fcp), W))
        off = int(0.5 * (len(A) - W))
        obs, fcp = plant(A[off:off + W], RNG)
        sh = RNG.permutation(W)
        pats.append(scanner.Pattern('Xnull_W%d:interval' % W,
                                    skel.groups_interval(obs[sh], fcp[sh]), W))

    best, per_text = scanner.scan_corpus(C, pats, progress=200)
    rows = []
    for k, (b, tn, off) in sorted(best.items()):
        base = k.split(':')[0]
        W = int(base.split('_W')[1].split('_')[0])
        tr = truth.get(base, {})
        expect = None
        if tr:
            expect = int(tr['frac'] * (len(B) - W))
        rows.append(dict(pattern=k, count=b, pct=100 * b / W, text=tn,
                         offset=off, window=W, expected_kjv_offset=expect))
        print('%-22s %5.0f/%4d (%5.1f%%) -> %-38s @%-8d  (expected ~KJV @%s)'
              % (k, b, W, 100 * b / W, tn, off, expect))
    json.dump(rows, open(os.path.join(HERE, 't0c_real.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
