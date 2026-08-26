"""Build the exemplar bank by UNSUPERVISED shape clustering.  No labels are shown.

The 13,122 LP2 rune crops collapse to 862 distinct exact bitmaps (d5_twins.py), so the
whole classification problem is: assign a class to each of ~862 objects.  We do that by
single-linkage clustering under translation-minimised Hamming distance, and we look for
a THRESHOLD PLATEAU at ~29 clusters -- if the pixel-identical-twin premise is right the
number of clusters should be flat in tau over a wide range, and that flatness is the
evidence that the partition is the font's and not the threshold's.
"""
import os, sys, json, collections
import numpy as np
import t1_reader as T
import t1_extract as E

WORK = os.path.join(T.HERE, 'work')
MAXW = 90            # above this a component is a merge candidate, not an exemplar
CANVAS = (144, 100)  # covers h<=135, w<=90 crops with margin for +-2 shift


def distinct(face, maxw=MAXW):
    """The distinct exact bitmaps among this face's crops (excluding merge candidates)."""
    z, mask = E.load(face)
    blob = z['blob'].tobytes(); off = z['off']
    key2id, ids, keys = {}, np.full(len(z['h']), -1, np.int32), []
    for i in range(len(z['h'])):
        if z['w'][i] > maxw:
            continue
        k = (int(z['h'][i]), int(z['w'][i]), blob[off[i]:off[i + 1]])
        j = key2id.get(k)
        if j is None:
            j = len(keys); key2id[k] = j; keys.append(k)
        ids[i] = j
    return z, mask, ids, keys


def to_canvas(keys, ch=CANVAS[0], cw=CANVAS[1]):
    X = np.zeros((len(keys), ch, cw), np.float32)
    for j, (h, w, p) in enumerate(keys):
        b = np.unpackbits(np.frombuffer(p, np.uint8))[:h * w].reshape(h, w)
        y, x = (ch - h) // 2, (cw - w) // 2
        X[j, y:y + h, x:x + w] = b
    return X


def pairwise(X, shift=2):
    """Min over +-shift translations of the Hamming distance between all pairs."""
    n, ch, cw = X.shape
    A = X.reshape(n, -1)
    nA = A.sum(1)
    best = None
    for dy in range(-shift, shift + 1):
        for dx in range(-shift, shift + 1):
            S = np.zeros_like(X)
            ys, yd = (max(0, dy), max(0, -dy))
            xs, xd = (max(0, dx), max(0, -dx))
            hh = ch - abs(dy); ww = cw - abs(dx)
            S[:, yd:yd + hh, xd:xd + ww] = X[:, ys:ys + hh, xs:xs + ww]
            B = S.reshape(n, -1)
            D = nA[:, None] + B.sum(1)[None, :] - 2.0 * (A @ B.T)
            best = D if best is None else np.minimum(best, D)
    return np.minimum(best, best.T)


def single_linkage(D, tau):
    """Connected components of the graph {d <= tau}."""
    n = D.shape[0]
    adj = D <= tau
    lab = np.full(n, -1, np.int32)
    c = 0
    for s in range(n):
        if lab[s] >= 0:
            continue
        stack = [s]; lab[s] = c
        while stack:
            u = stack.pop()
            for v in np.where(adj[u] & (lab < 0))[0]:
                lab[v] = c; stack.append(v)
        c += 1
    return lab, c


def build(face, tau=None, verbose=True):
    z, mask, ids, keys = distinct(face)
    X = to_canvas(keys)
    D = pairwise(X)
    sweep = []
    for t in range(0, 260, 5):
        lab, k = single_linkage(D, float(t))
        sweep.append((t, k))
    if verbose:
        print('%s: %d distinct bitmaps' % (face, len(keys)))
        print('  tau sweep (tau -> #clusters):')
        print('   ', ', '.join('%d:%d' % (t, k) for t, k in sweep))
    if tau is None:
        # pick the MIDPOINT of the widest tau-run whose cluster count is exactly 29
        runs, cur = [], None
        for t, k in sweep:
            if k == 29:
                cur = [t, t] if cur is None else [cur[0], t]
            elif cur is not None:
                runs.append(cur); cur = None
        if cur is not None:
            runs.append(cur)
        if not runs:
            raise SystemExit('no tau gives exactly 29 clusters for %s: %s' % (face, sweep))
        lo, hi = max(runs, key=lambda r: r[1] - r[0])
        tau = (lo + hi) / 2.0
        if verbose:
            print('  29-cluster plateau: tau in [%d, %d]  -> tau=%.1f' % (lo, hi, tau))
    lab, k = single_linkage(D, tau)
    if verbose:
        sizes = collections.Counter(lab[j] for j in ids if j >= 0)
        print('  tau=%.1f -> %d clusters; crop coverage per cluster: %s'
              % (tau, k, sorted(sizes.values(), reverse=True)))
    return dict(z=z, ids=ids, keys=keys, X=X, D=D, lab=lab, k=k, tau=tau)


if __name__ == '__main__':
    for face in ['LP2', 'LP1']:
        b = build(face)
        np.savez_compressed(os.path.join(WORK, 'bank_%s.npz' % face),
                            ids=b['ids'], lab=b['lab'], tau=np.array([b['tau']]),
                            k=np.array([b['k']]))
        print()


def pairwise_cross(X, Y, shift=2):
    """Min over +-shift translations of Hamming distance between rows of X and rows of Y."""
    n, ch, cw = X.shape
    A = X.reshape(n, -1)
    nA = A.sum(1)
    best = None
    for dy in range(-shift, shift + 1):
        for dx in range(-shift, shift + 1):
            S = np.zeros_like(Y)
            ys, yd = (max(0, dy), max(0, -dy))
            xs, xd = (max(0, dx), max(0, -dx))
            hh = ch - abs(dy); ww = cw - abs(dx)
            S[:, yd:yd + hh, xd:xd + ww] = Y[:, ys:ys + hh, xs:xs + ww]
            Bm = S.reshape(len(Y), -1)
            D = nA[:, None] + Bm.sum(1)[None, :] - 2.0 * (A @ Bm.T)
            best = D if best is None else np.minimum(best, D)
    return best
