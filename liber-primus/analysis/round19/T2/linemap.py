"""T2 -- the image<->canon LINE MAP, with its own control.

relikd image numbering is NOT krisyotam segment numbering (documented in
analysis/stones/pipeline.py: "relikd p54 == krisyotam page 53"). recon.py measured
the offset: identity for relikd p0..p49, relikd p50 is the runeless illustration
page, and relikd p51..p55 -> segments 50..54. Segments 55 and 56 are LP2 pages 56
and 57, which relikd does not carry; they come from the scream314 vendor assets
(73.jpg / 74.jpg), which C3 established render at the identical 2400x3600.

Within a page, image rows are matched to canon lines by a DP on
|rune-components - canon runes| with row-drop allowed (page headers, folio marks
and decorative rows are dropped) and canon-line-drop forbidden.

CONTROL: the map is only accepted for a page if every canon line receives a row and
the summed |ncomp - nrune| residual is small; the residual is reported per page and
is itself the segmentation-quality statistic frontB never had.

Writes out_linemap.json.
"""
import os
import json
import numpy as np
import t2lib as T

PAGE_TO_SEG = {}
for p in range(0, 50):
    PAGE_TO_SEG[('relikd', p)] = p
for p in range(51, 56):
    PAGE_TO_SEG[('relikd', p)] = p - 1
PAGE_TO_SEG[('vendor', 73)] = 55
PAGE_TO_SEG[('vendor', 74)] = 56

ROW_DROP = 14.0

# An "illuminated initial": a decorative oversized first glyph of a page/paragraph.
# Measured inventory (dbg_bigcomp.py): 11 of them, every one with x0 == 601 and
# h in 497..608 px against a 113 px rune body.  R9's diff_report.json bucket A --
# "15 loci, all pinned at position 0, x=601, a mechanical DP edge effect" -- is
# THIS, mis-diagnosed.  Its ink cannot be template-matched (the templates are
# 108-120 px tall), so the slot is EXCLUDED from adjudication rather than misread.
INIT_H = (140, 900)
INIT_W = (40, 320)


def path_of(src, num):
    return (os.path.join(T.RELIKD, 'p%d.jpg' % num) if src == 'relikd'
            else os.path.join(T.VENDOR, '%d.jpg' % num))


def initials(path):
    """Large in-column components that sit at a text row's left edge."""
    ink = T.page_ink(path)
    return [c for c in T.components(ink)
            if INIT_H[0] <= c['h'] <= INIT_H[1] and INIT_W[0] <= c['w'] <= INIT_W[1]
            and 400 < c['x0'] and (c['x0'] + c['x1']) / 2 < 2070]


def align_rows(rows, lines):
    """DP: rows may be dropped, canon lines may not."""
    na, nb = len(rows), len(lines)
    INF = 1e18
    dp = np.full((na + 1, nb + 1), INF)
    bk = np.zeros((na + 1, nb + 1), np.int8)
    dp[0, 0] = 0.0
    for i in range(na + 1):
        for j in range(nb + 1):
            if dp[i, j] == INF:
                continue
            if i < na and j < nb:
                c = dp[i, j] + abs(rows[i][4] - len(lines[j]['runes']))
                if c < dp[i + 1, j + 1]:
                    dp[i + 1, j + 1] = c
                    bk[i + 1, j + 1] = 1
            if i < na:
                c = dp[i, j] + ROW_DROP
                if c < dp[i + 1, j]:
                    dp[i + 1, j] = c
                    bk[i + 1, j] = 2
    if dp[na, nb] >= INF:
        return None, None
    pairs = []
    i, j = na, nb
    while i > 0 or j > 0:
        m = bk[i, j]
        if m == 1:
            pairs.append((i - 1, j - 1))
            i -= 1
            j -= 1
        elif m == 2:
            i -= 1
        else:
            return None, None
    pairs.reverse()
    return pairs, float(dp[na, nb])


def build():
    canon = T.canon_lines()
    byseg = {}
    for i, c in enumerate(canon):
        byseg.setdefault(c['seg'], []).append((i, c))
    out = []
    report = []
    for (src, num), seg in sorted(PAGE_TO_SEG.items(), key=lambda kv: kv[1]):
        p = path_of(src, num)
        rows = T.text_rows(p)
        inits = initials(p)
        lines = [c for _, c in byseg[seg]]
        gidx = [i for i, _ in byseg[seg]]
        pairs, cost = align_rows(rows, lines)
        if pairs is None or len(pairs) != len(lines):
            report.append(dict(src=src, num=num, seg=seg, ok=False,
                               rows=len(rows), lines=len(lines)))
            continue
        def eff(a, b):
            """rune components + 1 if an illuminated initial covers this row"""
            n = rows[a][4]
            if any(c['x1'] <= rows[a][2] + 30 and abs(c['y0'] - rows[a][0]) < 80
                   for c in inits):
                n += 1
            return n
        resid = sum(abs(eff(a, b) - len(lines[b]['runes'])) for a, b in pairs)
        exact = sum(1 for a, b in pairs if eff(a, b) == len(lines[b]['runes']))
        for a, b in pairs:
            y0, y1, x0, x1, nc = rows[a]
            ini = [c for c in inits
                   if c['x1'] <= x0 + 30 and abs(c['y0'] - y0) < 80]
            out.append(dict(gline=gidx[b], seg=seg, line_in_seg=lines[b]['line_in_seg'],
                            src=src, num=num, path=os.path.relpath(p, T.ROOT),
                            y0=y0, y1=y1, x0=x0, x1=x1, ncomp=nc,
                            nrune=len(lines[b]['runes']),
                            initial=(1 if ini else 0)))
        report.append(dict(src=src, num=num, seg=seg, ok=True, rows=len(rows),
                           lines=len(lines), dropped=len(rows) - len(pairs),
                           resid=resid, count_exact=exact))
    return out, report, canon


def main():
    out, report, canon = build()
    ok = [r for r in report if r['ok']]
    print('pages mapped %d/%d   canon lines covered %d/%d'
          % (len(ok), len(report), len(out), len(canon)))
    tot_exact = sum(r['count_exact'] for r in ok)
    tot_lines = sum(r['lines'] for r in ok)
    print('rune-component count EXACT on %d/%d lines (%.1f%%)  -- R9 raw-band DP got '
          '232/604 (38.4%%)' % (tot_exact, tot_lines, 100.0 * tot_exact / tot_lines))
    resid = sum(r['resid'] for r in ok)
    print('summed |ncomp - nrune| residual: %d over %d runes'
          % (resid, sum(x['nrune'] for x in out)))
    bad = [r for r in report if not r['ok']]
    for r in bad:
        print('  UNMAPPED', r)
    for r in ok:
        if r['resid'] > 6:
            print('  high-residual page: src=%s num=%s seg=%s resid=%d dropped=%d'
                  % (r['src'], r['num'], r['seg'], r['resid'], r['dropped']))
    json.dump(dict(map=out, report=report),
              open(os.path.join(T.HERE, 'out_linemap.json'), 'w'))
    print('wrote out_linemap.json')


if __name__ == '__main__':
    main()
