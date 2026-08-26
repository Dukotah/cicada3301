"""Precompute, ONCE, what every distinct bitmap needs at read time.

Every ordinary crop in the book is byte-identical to one of ~875 distinct bitmaps, so its
distance to the exemplar bank is a property of the BITMAP, not of the occurrence.  We
therefore compute, for each distinct bitmap:

    d1[b]   the distance to the nearest exemplar carrying a DIFFERENT label
            -- i.e. the margin by which the call is made, and the quantity the
               confidence in the adjudication is calibrated against

d0 is 0 for any bitmap that is itself in the bank (the crop matches an exemplar exactly).
This makes a leave-one-page-out read of all 58 pages a table lookup instead of 8.8 TFLOP of
matrix multiply, and it is exactly equivalent -- `test_t1.py` asserts that.
"""
import os
import numpy as np
import t1_reader as T
import t1_align as A
from t1_match import Matcher

CACHE = os.path.join(T.HERE, 'work', 'fast_%s.npz')


def build(S, blab, face='LP2'):
    path = CACHE % face
    if os.path.exists(path):
        z = np.load(path)
        if len(z['d1']) == len(S.keys):
            return z['d0'], z['d1'], z['lab1']
    ids = np.array(sorted(k for k in blab if k in S.sm_pos))
    Y = S.X[[S.sm_pos[int(k)] for k in ids]]
    BL = np.array([blab[int(k)] for k in ids])
    M = Matcher(Y, BL)
    d0 = np.full(len(S.keys), np.inf, np.float32)
    d1 = np.full(len(S.keys), np.inf, np.float32)
    lab1 = np.full(len(S.keys), -1, np.int32)
    q = np.array([b for b in range(len(S.keys)) if S.small[b]])
    for s in range(0, len(q), 256):
        chunk = q[s:s + 256]
        X = S.X[[S.sm_pos[int(b)] for b in chunk]]
        D = M.distances(X)
        for k, b in enumerate(chunk):
            row = D[k]
            mine = blab.get(int(b))
            d0[b] = row.min()
            if mine is None:
                d1[b] = np.partition(row, 1)[1]
                lab1[b] = BL[int(row.argsort()[1])]
            else:
                mask = BL != mine
                if mask.any():
                    j = int(np.where(mask)[0][row[mask].argmin()])
                    d1[b] = row[j]; lab1[b] = BL[j]
        print('   margins %d/%d' % (min(s + 256, len(q)), len(q)), flush=True)
    np.savez_compressed(path, d0=d0, d1=d1, lab1=lab1)
    return d0, d1, lab1
