"""T1 -- the per-rune reader, end to end.  ONE code path for every measurement.

Pipeline per page:
  1. segment          connected components, rune-height band, Y inner-stroke attached
  2. classify         native-resolution translation-minimised Hamming to an exemplar bank
  3. repair merges    a >90px component is CUT if and only if its pieces match exemplars
  4. repair initials  an illuminated initial is READ if and only if a scale-normalised
                      crop of it matches an exemplar
  5. align            difflib against canon, reporting equal / replace / insert / delete

LEAVE-ONE-PAGE-OUT.  A bitmap's label is the consensus of canon's calls at the OTHER
positions where that bitmap occurs.  When a page is being measured, every crop on that
page is removed from the consensus first, so no glyph is ever judged using its own page.
"""
import os, sys, json, difflib, collections
import numpy as np
import t1_reader as T
import t1_extract as E
import t1_align as A
import t1_split as SP
from t1_match import Matcher, canvas

sys.path.insert(0, os.path.join(T.LP, 'src'))
from lp.gematria import IDX_TO_TRANS  # noqa: E402

WORK = os.path.join(T.HERE, 'work')
INIT_H = 200          # a component taller than this is an illuminated initial candidate


def build(face='LP2'):
    r = A.run(face, verbose=True)
    S, blab = r['S'], r['blab']
    z = S.z
    # per-bitmap, per-page canon vote table (needed for leave-one-page-out)
    pred = r['pred']
    votes = collections.defaultdict(collections.Counter)
    for p in S.pages:
        if not r['cpage'][p]:
            continue
        idx = S.idx_by_page[p]
        m, f = A.align_page(list(pred[idx]), r['cpage'][p])
        for a, b in m + f:
            bm = int(S.ids[idx[a]])
            if S.small[bm]:
                votes[bm][(p, r['cpage'][p][b])] += 1
    return r, votes


def labels_excluding(S, blab, votes, drop_pages):
    """bitmap -> rune, with every crop on `drop_pages` removed from the consensus."""
    out = {}
    for b, c in votes.items():
        cc = collections.Counter()
        for (p, rn), n in c.items():
            if p not in drop_pages:
                cc[rn] += n
        if cc:
            out[b] = cc.most_common(1)[0][0]
    return out


class Bank:
    """The exemplar bank, built ONCE.  Leave-one-page-out then only re-labels and
    re-masks it (Matcher.set_view), because dropping a page cannot change any pixel."""

    def __init__(self, S, votes, blab):
        self.S, self.votes = S, votes
        self.ids = np.array(sorted(k for k in blab if k in S.sm_pos))
        self.pos = {int(b): i for i, b in enumerate(self.ids)}
        self.full = Matcher(S.X[[S.sm_pos[int(k)] for k in self.ids]],
                            np.array([blab[int(k)] for k in self.ids]))
        self.freq = collections.Counter(int(b) for b in S.ids)
        self.blab = blab
        self._rep_cache = {}

    def fastview(self, drop_pages=frozenset()):
        """The per-page read table: bitmap -> (label, d0, d1) with `drop_pages` removed
        from the label consensus."""
        import t1_fast
        if not hasattr(self, '_d1'):
            self._d0, self._d1, self._lab1 = t1_fast.build(self.S, self.blab)
        lab = labels_excluding(self.S, self.blab, self.votes, drop_pages)
        return dict(key2id=self.S.key2id, lab=lab, d0=self._d0, d1=self._d1)

    def view(self, drop_pages=frozenset()):
        lab = labels_excluding(self.S, self.blab, self.votes, drop_pages)
        active = np.array([int(b) in lab for b in self.ids])
        labels = np.array([lab.get(int(b), -1) for b in self.ids])
        self.full.set_view(labels, active)
        key = tuple(sorted(drop_pages))
        if key not in self._rep_cache:
            rep = {}
            for b in self.ids:
                l = lab.get(int(b))
                if l is None:
                    continue
                if l not in rep or self.freq[int(b)] > self.freq[rep[l]]:
                    rep[l] = int(b)
            rid = np.array([rep[l] for l in sorted(rep)])
            self._rep_cache[key] = Matcher(
                self.S.X[[self.S.sm_pos[int(k)] for k in rid]],
                np.array([lab[int(k)] for k in rid]))
        return self.full, self._rep_cache[key], lab


def read_page(path, full, small, page=None, fast=None, ink=None):
    """The reader.  Returns a list of records in reading order."""
    if ink is None:
        ink = T.page_ink(path)
    comps = T.components(ink)
    cands = [dict(c) for c in comps if T.RUNE_H[0] <= c['h'] <= T.RUNE_H[1]]
    others = [c for c in comps if not (T.RUNE_H[0] <= c['h'] <= T.RUNE_H[1])]
    for g in cands:
        g.setdefault('n_inner', 0)
    T.attach_inner(cands, others)
    rows = T.group_rows(cands)

    out = []
    used_init = set()          # an initial spans several text rows; emit it ONCE
    for ri, r in enumerate(rows):
        gl = [cands[j] for j in r]
        rowy0 = min(g['y0'] for g in gl); rowy1 = max(g['y1'] for g in gl)
        rowx0 = min(g['x0'] for g in gl)
        # illuminated initials: an oversize component that vertically overlaps this row
        # and lies entirely LEFT of every accepted glyph in it
        for ci, c in enumerate(others):
            if c['h'] <= INIT_H or ci in used_init:
                continue
            if c['y1'] < rowy0 or c['y0'] > rowy1:
                continue
            if c['x1'] > rowx0:
                continue
            used_init.add(ci)
            l, d = SP.read_initial(c['mask'], small)
            if l is not None:
                out.append(dict(kind='initial', row=ri, x0=c['x0'], y0=c['y0'],
                                h=c['h'], w=c['w'], lab=int(l), d0=float(d),
                                d1=float('nan')))
        # ordinary glyphs
        narrow = [g for g in gl if g['w'] <= A.MAXW]
        hit, miss = [], []
        for g in narrow:
            b = fast['key2id'].get(T.crop_key(g)) if fast else None
            (hit if (b is not None and fast['lab'].get(b) is not None) else miss).append((g, b))
        if miss:
            L, D0, D1 = full.match(canvas([g['mask'] for g, _ in miss]))
        res = {}
        for k, (g, b) in enumerate(miss):
            res[id(g)] = (int(L[k]), float(D0[k]), float(D1[k]))
        for g, b in hit:
            res[id(g)] = (int(fast['lab'][b]), float(fast['d0'][b]), float(fast['d1'][b]))
        for g in gl:
            if g['w'] <= A.MAXW:
                l, dd0, dd1 = res[id(g)]
                out.append(dict(kind='glyph', row=ri, x0=g['x0'], y0=g['y0'],
                                h=g['h'], w=g['w'], lab=l, d0=dd0,
                                d1=dd1, n_inner=g.get('n_inner', 0)))
            else:
                parts, cost = SP.split_wide(g['mask'], small)
                if parts is None:
                    out.append(dict(kind='nonrune', row=ri, x0=g['x0'], y0=g['y0'],
                                    h=g['h'], w=g['w'], lab=None, d0=None, d1=None))
                else:
                    for (l, off, d) in sorted(parts, key=lambda t: t[1]):
                        out.append(dict(kind='split', row=ri, x0=g['x0'] + off,
                                        y0=g['y0'], h=g['h'], w=g['w'],
                                        lab=int(l), d0=float(d), d1=float('nan')))
    out.sort(key=lambda o: (o['row'], o['x0']))
    return [o for o in out if o['kind'] != 'nonrune'], out


def align_report(seq, canon):
    pr = [o['lab'] for o in seq]
    sm = difflib.SequenceMatcher(None, pr, canon, autojunk=False)
    eq = rep = ins = dele = 0
    pairs, bad = [], []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            eq += i2 - i1
            pairs += [(i1 + k, j1 + k, True) for k in range(i2 - i1)]
        elif tag == 'replace':
            if (i2 - i1) == (j2 - j1):
                rep += i2 - i1
                pairs += [(i1 + k, j1 + k, False) for k in range(i2 - i1)]
                bad += [(i1 + k, j1 + k) for k in range(i2 - i1)]
            else:
                rep += max(i2 - i1, j2 - j1)
                bad.append((i1, j1))
        elif tag == 'insert':
            ins += j2 - j1
        else:
            dele += i2 - i1
    return dict(equal=eq, replace=rep, insert=ins, delete=dele,
                n_seq=len(pr), n_canon=len(canon)), pairs, bad
