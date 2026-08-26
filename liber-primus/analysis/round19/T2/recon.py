"""T2 step 0 -- establish the image<->canon LINE MAP and measure the mark classes.

Nothing is scored here. This fixes the geometry every later measurement stands on:
  * which image file carries which canon line,
  * the height/width classes of rune / ornament / separator ink,
  * per-page rune-component count vs canon rune count (the segmentation gap frontB hit).

Writes out_recon.json.
"""
import os
import json
import collections
import numpy as np
import t2lib as T


def main():
    canon = T.canon_lines()
    print('canon lines %d  runes %d' % (len(canon), sum(len(c['runes']) for c in canon)))
    segs = collections.defaultdict(list)
    for i, c in enumerate(canon):
        segs[c['seg']].append(i)

    pages = [('relikd', os.path.join(T.RELIKD, 'p%d.jpg' % p), p) for p in range(56)]
    pages += [('vendor', os.path.join(T.VENDOR, '73.jpg'), 73),
              ('vendor', os.path.join(T.VENDOR, '74.jpg'), 74)]

    rows = {}
    for src, path, num in pages:
        r = T.text_rows(path)
        rows[(src, num)] = r
        print('%-7s %-3s rows=%2d comps=%s' % (src, num, len(r), [x[4] for x in r]),
              flush=True)

    # ---- page -> canon segment, by matching the per-page row-count / comp-count
    #      signature against the segment's line lengths.
    seglen = {s: [len(canon[i]['runes']) for i in idx] for s, idx in segs.items()}
    assign = {}
    for (src, num), r in rows.items():
        comps = [x[4] for x in r]
        best, bestc = None, None
        for s, L in seglen.items():
            if len(L) != len(comps):
                continue
            c = sum(abs(a - b) for a, b in zip(comps, L))
            if bestc is None or c < bestc:
                best, bestc = s, c
        assign[(src, num)] = (best, bestc, len(comps))
    print('\npage -> segment (exact row-count match only):')
    for k in sorted(assign, key=lambda k: (k[0], k[1])):
        print('  %-7s %-3s -> seg %-4s cost %-5s rows %d'
              % (k[0], k[1], assign[k][0], assign[k][1], assign[k][2]))

    # ---- mark classes: heights/widths of everything in the text column
    hh = collections.Counter()
    ww = collections.Counter()
    hw = collections.Counter()
    for path in [os.path.join(T.RELIKD, 'p3.jpg'), os.path.join(T.RELIKD, 'p45.jpg'),
                 os.path.join(T.VENDOR, '73.jpg')]:
        ink = T.page_ink(path)
        for c in T.components(ink):
            xc = (c['x0'] + c['x1']) / 2
            hh[(os.path.basename(path), min(c['h'], 200))] += 1
            if c['h'] < 40 and 330 < xc < 2070:
                ww[(os.path.basename(path), c['w'])] += 1
                hw[(os.path.basename(path), c['h'], c['w'])] += 1
    print('\nsmall-mark (h<40, text column) width histogram:')
    for k in sorted(ww):
        print('   %s w=%d  n=%d' % (k[0], k[1], ww[k]))
    print('\nsmall-mark (h,w) top:')
    for k, v in hw.most_common(20):
        print('   %s h=%d w=%d n=%d' % (k[0], k[1], k[2], v))

    json.dump(dict(
        rows={'%s:%s' % k: v for k, v in rows.items()},
        assign={'%s:%s' % k: v for k, v in assign.items()},
        small_marks_hw=[[k[0], k[1], k[2], v] for k, v in hw.most_common(60)],
        canon_lines=len(canon),
    ), open(os.path.join(T.HERE, 'out_recon.json'), 'w'), indent=1)
    print('\nwrote out_recon.json')


if __name__ == '__main__':
    main()
