"""Fast exemplar matcher: the bank's +-2 shifted copies are precomputed ONCE, so a
query batch costs 25 BLAS matmuls regardless of how many times it is called.

Distance is exactly the same quantity as t1_bank.pairwise_cross -- translation-minimised
Hamming distance between native-resolution binary masks on a common canvas.  This class
is a speed refactor of that function and nothing else; `test_t1.py` asserts they agree.
"""
import numpy as np
from PIL import Image

CH, CW = 144, 100
SHIFT = 2


def canvas(masks, ch=CH, cw=CW):
    X = np.zeros((len(masks), ch, cw), np.float32)
    for i, m in enumerate(masks):
        h, w = m.shape
        if h > ch or w > cw:
            m = np.asarray(Image.fromarray((m * 255).astype(np.uint8))
                           .resize((min(w, cw), min(h, ch)), Image.LANCZOS)) > 127
            h, w = m.shape
        y, x = (ch - h) // 2, (cw - w) // 2
        X[i, y:y + h, x:x + w] = m
    return X


class Matcher:
    def __init__(self, Y, labels, shift=SHIFT):
        self.labels = np.asarray(labels)
        self.active = None
        self.shift = shift
        n, ch, cw = Y.shape
        self.S, self.nS = [], []
        for dy in range(-shift, shift + 1):
            for dx in range(-shift, shift + 1):
                T = np.zeros_like(Y)
                ys, yd = max(0, dy), max(0, -dy)
                xs, xd = max(0, dx), max(0, -dx)
                hh, ww = ch - abs(dy), cw - abs(dx)
                T[:, yd:yd + hh, xd:xd + ww] = Y[:, ys:ys + hh, xs:xs + ww]
                F = T.reshape(n, -1)
                self.S.append(np.ascontiguousarray(F.T))
                self.nS.append(F.sum(1))

    def set_view(self, labels=None, active=None):
        """Swap the label vector and/or mask exemplars out WITHOUT rebuilding the
        shifted bank.  This is what makes leave-one-page-out affordable: dropping a
        page changes only which exemplars are eligible and what they are called, never
        the pixels or the distances."""
        if labels is not None:
            self.labels = np.asarray(labels)
        self.active = None if active is None else np.asarray(active, bool)

    def distances(self, X):
        A = X.reshape(len(X), -1)
        nA = A.sum(1)[:, None]
        best = None
        for F, nF in zip(self.S, self.nS):
            D = nA + nF[None, :] - 2.0 * (A @ F)
            best = D if best is None else np.minimum(best, D)
        if getattr(self, 'active', None) is not None:
            best = np.where(self.active[None, :], best, np.inf)
        return best

    def match(self, X):
        """-> (labels, d_best, d_runnerup_of_a_DIFFERENT_label)."""
        D = self.distances(X)
        arg = D.argmin(1)
        lab = self.labels[arg]
        d0 = D[np.arange(len(X)), arg]
        M = D.copy()
        M[self.labels[None, :] == lab[:, None]] = np.inf
        d1 = M.min(1)
        return lab, d0, d1
