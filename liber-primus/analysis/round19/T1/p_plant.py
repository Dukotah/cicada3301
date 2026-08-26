"""PLANT-AND-RECOVER (PREREG section 4).  Doctrine mechanic 2: a null from an unvalidated
instrument is not a negative.  Job 2's most likely outcome is "canon holds" -- a null --
and that is worth nothing unless the reader is shown able to SEE a transcription error
that is really there.

So: substitute the PIXELS of k glyphs at known positions with the pixels of a different
rune, run the whole pipeline unchanged, and require that the planted positions come back
as disagreements with canon.

  P-1  substitutions anywhere in the 29 runes
  P-2  substitutions confined to the {O, A, AE} triple -- the exact shape Job 2 turns on
"""
import os, sys, json, random, collections
import numpy as np
import t1_reader as T, t1_run as R, t1_align as A
sys.path.insert(0, os.path.join(T.LP, 'src'))
from lp.gematria import IDX_TO_TRANS  # noqa: E402

TRIPLE = [i for i in range(29) if IDX_TO_TRANS[i] in ('O', 'A', 'AE')]
PAGES = [56, 57] + [p for p in range(56) if p != 50]   # every LP2 page with canon


def page_path(p):
    return T.relikd_path(p) if p <= 55 else T.vendor_path('%d.jpg' % (p + 17))


def donors(S, blab):
    """One canonical crop per rune class, taken from the corpus."""
    freq = collections.Counter(int(b) for b in S.ids)
    best = {}
    for b, l in blab.items():
        if b in S.sm_pos and (l not in best or freq[b] > freq[best[l]]):
            best[l] = b
    return {l: S.bitmap(b) for l, b in best.items()}


def plant(page, boxes, newlab, don):
    """Return a modified ink array for `page` with the glyphs occupying the given
    (x0,y0,x1,y1) boxes replaced by the donor crop of `newlab`.

    Boxes, not indices: the reader's output sequence contains split parts and
    illuminated initials, so its index is NOT the component index.  Addressing the plant
    by pixel box removes that whole class of harness error.
    """
    ink = T.page_ink(page_path(page)).copy()
    for (x0, y0, x1, y1), nl in zip(boxes, newlab):
        ink[y0:y1, x0:x1] = False
        m = don[nl]
        h, w = m.shape
        y = y1 - h                              # share the baseline
        x = x0 + (x1 - x0 - w) // 2             # centre in the vacated cell
        if y < 0 or x < 0 or x + w > ink.shape[1] or y + h > ink.shape[0]:
            continue
        ink[y:y + h, x:x + w] |= m
    return ink


def run(kind, seed=3301, k=100, min_sep=4, gap=8):
    r, votes = R.build('LP2')
    S = r['S']
    bank = R.Bank(S, votes, r['blab'])
    don = donors(S, r['blab'])
    rng = random.Random(seed)

    # choose k positions across PAGES whose canon rune is known and (for P-2) in the triple
    pool = []
    for p in PAGES:
        canon = r['cpage'][p]
        if not canon:
            continue
        full, small, lab = bank.view({p})
        seq, _ = R.read_page(page_path(p), full, small, page=p, fast=bank.fastview({p}))
        rep, pairs, bad = R.align_report(seq, canon)
        for (i, j, ok) in pairs:
            if not ok or seq[i]['kind'] != 'glyph':
                continue
            c = canon[j]
            if kind == 'P-2' and c not in TRIPLE:
                continue
            o = seq[i]
            # require clear whitespace either side, so the donor crop cannot TOUCH a
            # neighbour and turn the plant into a segmentation collision instead of the
            # label substitution it is meant to be
            nb = [q for q in seq if q['row'] == o['row'] and q is not o]
            L = [q['x0'] + q['w'] for q in nb if q['x0'] + q['w'] <= o['x0']]
            Rr = [q['x0'] for q in nb if q['x0'] >= o['x0'] + o['w']]
            if (L and o['x0'] - max(L) < gap) or (Rr and min(Rr) - (o['x0'] + o['w']) < gap):
                continue
            pool.append((p, (o['x0'], o['y0'], o['x0'] + o['w'], o['y0'] + o['h']), j, c))
    rng.shuffle(pool)
    chosen, taken = [], collections.defaultdict(list)
    for rec in pool:
        p, box, j, c = rec
        if any(abs(j - jj) < min_sep for jj in taken[p]):
            continue         # never plant two errors within min_sep of each other
        taken[p].append(j); chosen.append(rec)
        if len(chosen) >= k:
            break
    byp = collections.defaultdict(list)
    for (p, box, j, c) in chosen:
        alts = TRIPLE if kind == 'P-2' else list(range(29))
        nl = rng.choice([a for a in alts if a != c])
        byp[p].append((box, j, c, nl))

    det = miss = collat = 0
    rows = []
    for p, items in sorted(byp.items()):
        ink = plant(p, [b for b, j, c, nl in items], [nl for b, j, c, nl in items], don)
        full, small, lab = bank.view({p})
        seq, _ = R.read_page(page_path(p), full, small, page=p,
                             fast=bank.fastview({p}), ink=ink)
        canon = r['cpage'][p]
        rep, pairs, bad = R.align_report(seq, canon)
        call = {}
        for (i, j, ok) in pairs:
            call[j] = seq[i]['lab']
        planted = {j: (c, nl) for b, j, c, nl in items}
        pcol = 0
        for j, (c, nl) in planted.items():
            got = call.get(j)
            hit = (got is not None and got != c)
            exact = (got == nl)
            det += hit; miss += (not hit)
            rows.append(dict(page=p, cpos=int(j), canon=IDX_TO_TRANS[c],
                             planted=IDX_TO_TRANS[nl],
                             read=IDX_TO_TRANS[got] if got is not None else None,
                             detected=bool(hit), exact=bool(exact),
                             lost=bool(got is None),
                             blind=bool(got is not None and got == c)))
        for j, got in call.items():
            if j not in planted and got != canon[j]:
                collat += 1; pcol += 1
        if pcol or sum(1 for x in rows if x['page'] == p and not x['detected']):
            print('  %s p%-2d  planted %2d  detected %2d  collateral %d'
                  % (kind, p, len(items),
                     sum(1 for x in rows if x['page'] == p and x['detected']), pcol),
                  flush=True)
    exact = sum(1 for x in rows if x['exact'])
    lost = sum(1 for x in rows if x['lost'])
    blind = sum(1 for x in rows if x['blind'])
    n = len(rows)
    print('%s: k=%d  DETECTED %d = %.2f%%   named the planted rune exactly %d = %.2f%%'
          % (kind, n, det, 100.0*det/n, exact, 100.0*exact/n))
    print('     misses: %d reader-BLIND (canon rune read back)  +  %d LOST to alignment'
          ' (the plant perturbed segmentation, not the label)   collateral %d'
          % (blind, lost, collat))
    print('     detection conditional on the position surviving alignment: %d/%d = %.2f%%'
          % (det, n - lost, 100.0*det/(n-lost) if n-lost else 0))
    return dict(kind=kind, k=n, detected=int(det), detection_rate=det/n,
                exact=int(exact), exact_rate=exact/n, blind=int(blind), lost=int(lost),
                detection_given_aligned=(det/(n-lost)) if n-lost else None,
                collateral=int(collat), rows=rows)


if __name__ == '__main__':
    out = {}
    for kind in ['P-1', 'P-2']:
        out[kind] = run(kind)
    json.dump(out, open(os.path.join(T.HERE, 'out_plant.json'), 'w'), indent=1)
    print('-> out_plant.json')
