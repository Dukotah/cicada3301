"""Align this lane's crop stream to canon, and label the distinct bitmaps.

THE IDEA THAT MAKES THIS WORK
-----------------------------
These pages are Ghostscript renders of a typeset font.  13,122 rune crops collapse to
~830 DISTINCT bitmaps.  A rune's identity is therefore a property of its BITMAP, shared
with hundreds of other positions in the book.  That converts the transcription audit
into something much sharper than "read the page":

    for each distinct bitmap b, canon assigns labels at all n_b positions where b occurs.
    If canon is internally consistent every one of those labels is the same rune.  Every
    position whose canon label differs from its bitmap's consensus is a LOCATED candidate
    transcription error -- decidable from pixels, because the same pixels are called
    something else hundreds of times elsewhere in the same book.

The evidence against a position comes from the OTHER occurrences of its bitmap, so no
classifier is ever trained on the position it judges.

BOOTSTRAP
---------
Alignment needs labels and labels need alignment, so:
  1. seed from LP2 pages whose segmented count equals canon's count exactly;
  2. classify every distinct bitmap by nearest labelled bitmap;
  3. difflib-align each page's classified stream to that page's canon runes;
  4. re-vote bitmap labels from the matched pairs; iterate to a fixed point.
"""
import os, sys, json, difflib, collections
import numpy as np
import t1_reader as T
import t1_extract as E
import t1_bank as B

sys.path.insert(0, os.path.join(T.LP, 'src'))
from lp.gematria import RUNE_TO_IDX, IDX_TO_TRANS  # noqa: E402

WORK = os.path.join(T.HERE, 'work')
MAXW = 90          # a component wider than this holds more than one rune (see d3/d4)
CH, CW = 144, 100
OVERSIZE = -2      # sentinel label for a merge candidate: never matches a canon rune


def img2canon(p):
    """LP2 image page -> canonical_pages.json entry.  Image p50 is the near-blank page
    (2 rune-band components); canonical_pages.json has no entry for it."""
    if p <= 49:
        return p
    if p == 50:
        return None
    return p - 1


class Stream:
    def __init__(self, face):
        self.face = face
        z, mask = E.load(face)
        self.z, self.mask = z, mask
        blob = z['blob'].tobytes(); off = z['off']
        key2id, ids, keys = {}, np.empty(len(z['h']), np.int32), []
        for i in range(len(z['h'])):
            k = (int(z['h'][i]), int(z['w'][i]), blob[off[i]:off[i + 1]])
            j = key2id.get(k)
            if j is None:
                j = len(keys); key2id[k] = j; keys.append(k)
            ids[i] = j
        self.ids, self.keys = ids, keys
        self.n = len(ids)
        self.page, self.w = z['page'], z['w']
        self.small = np.array([w <= MAXW for h, w, p in keys])
        self.sm_idx = np.where(self.small)[0]                 # bitmap ids that are single
        self.sm_pos = {int(b): i for i, b in enumerate(self.sm_idx)}
        self.X = B.to_canvas([keys[b] for b in self.sm_idx], CH, CW)
        self.pages = sorted(set(int(p) for p in self.page))
        self.idx_by_page = {p: np.where(self.page == p)[0] for p in self.pages}
        print('%s: %d crops, %d distinct bitmaps (%d single-width, %d merge candidates)'
              % (face, self.n, len(keys), self.small.sum(), (~self.small).sum()))

    def bitmap(self, b):
        h, w, p = self.keys[b]
        return np.unpackbits(np.frombuffer(p, np.uint8))[:h * w].reshape(h, w).astype(bool)


def align_page(pred, canon):
    """difflib alignment.  Returns (matched, forced):
      matched -- pairs where the predicted rune equals canon's rune;
      forced  -- pairs inside an equal-length 'replace' block, i.e. positions whose
                 correspondence is fixed by the surrounding agreement even though the
                 prediction disagrees.  Forced pairs are what let a bitmap that occurs
                 ONCE in the whole book ever receive a label.
    """
    sm = difflib.SequenceMatcher(None, pred, canon, autojunk=False)
    matched, forced = [], []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            matched += [(i1 + k, j1 + k) for k in range(i2 - i1)]
        elif tag == 'replace' and (i2 - i1) == (j2 - j1):
            forced += [(i1 + k, j1 + k) for k in range(i2 - i1)]
    return matched, forced


def canon_by_page(S):
    canon = T.canon_pages()
    out = {}
    for p in S.pages:
        ce = img2canon(p) if S.face == 'LP2' else None
        out[p] = T.canon_indices(canon.get(ce, '')) if ce is not None else []
    return out


def run(face='LP2', iters=8, verbose=True):
    S = Stream(face)
    cpage = canon_by_page(S)
    votes = collections.defaultdict(collections.Counter)
    seeds = [p for p in S.pages if cpage[p] and len(S.idx_by_page[p]) == len(cpage[p])]
    if verbose:
        print('bootstrap seed pages (segmented count == canon count):', seeds)
    for p in seeds:
        for i, ci in zip(S.idx_by_page[p], cpage[p]):
            b = int(S.ids[i])
            if S.small[b]:
                votes[b][ci] += 1

    hist, lab = [], {}
    for it in range(iters):
        lab = {b: c.most_common(1)[0][0] for b, c in votes.items() if c}
        known = np.array(sorted(lab))
        Y = S.X[[S.sm_pos[int(k)] for k in known]]
        D = B.pairwise_cross(S.X, Y)
        nn = known[D.argmin(1)]
        dmin = D.min(1)
        blab = {}
        for i, b in enumerate(S.sm_idx):
            blab[int(b)] = lab.get(int(b), lab[int(nn[i])])   # nn is a bitmap id -> its label
        pred_all = np.array([blab.get(int(b), OVERSIZE) for b in S.ids])

        votes = collections.defaultdict(collections.Counter)
        nmatch = ntot = nforced = 0
        for p in S.pages:
            if not cpage[p]:
                continue
            idx = S.idx_by_page[p]
            matched, forced = align_page(list(pred_all[idx]), cpage[p])
            nmatch += len(matched); ntot += len(cpage[p])
            nforced += len(forced)
            for a, b in matched + forced:
                bm = int(S.ids[idx[a]])
                if S.small[bm]:            # merge candidates get no label
                    votes[bm][cpage[p][b]] += 1
        hist.append((len(lab), nmatch, ntot, nforced))
        if verbose:
            print('  iter %d: labelled bitmaps %d   agreeing %d/%d = %.4f%%  (+%d forced)'
                  % (it, len(lab), nmatch, ntot, 100.0 * nmatch / ntot, nforced))
        if it and hist[-1][1] == hist[-2][1] and hist[-1][0] == hist[-2][0]:
            break
    return dict(S=S, votes=votes, lab=lab, blab=blab, dmin=dmin, cpage=cpage,
                pred=pred_all, hist=hist)


if __name__ == '__main__':
    r = run('LP2')
    S, votes = r['S'], r['votes']
    # purity of each distinct bitmap under canon's labels
    tot = imp = 0
    rows = []
    for b, c in votes.items():
        n = sum(c.values()); m = c.most_common(1)[0][1]
        tot += n; imp += n - m
        if n - m:
            rows.append((n - m, n, b, [(IDX_TO_TRANS[k], v) for k, v in c.most_common()]))
    print('\nbitmap purity under canon: %d/%d matched positions agree with their bitmap'
          ' consensus (%.4f%%); %d disagree' % (tot - imp, tot, 100.0*(tot-imp)/tot, imp))
    rows.sort(reverse=True)
    print('most impure bitmaps:')
    for r_ in rows[:25]:
        print('   impure %3d / n=%4d  bitmap %4d  %s' % (r_[0], r_[1], r_[2], r_[3]))
