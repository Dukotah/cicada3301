"""Diagnostic: width distribution of rune-band components; how much of the count delta
is explained by TOUCHING glyphs (one component holding two runes)."""
import numpy as np, json
import t1_reader as T

# image page -> canon entry (canonical_pages.json skips the near-blank image p50)
def img2canon(p):
    if p <= 49: return p
    if p == 50: return None
    return p - 1

canon = T.canon_pages()
allw = []
rows = []
for p in range(58):
    path = T.relikd_path(p) if p <= 55 else T.vendor_path('%d.jpg' % (p + 17))
    ink = T.page_ink(path)
    cands = T.rune_candidates(T.components(ink))
    w = np.array([c['w'] for c in cands])
    allw.append(w)
    ce = img2canon(p)
    cn = len(canon.get(ce, '')) if ce is not None else 0
    wide = int((w > 90).sum()); wide2 = int((w > 130).sum())
    narrow = int((w < 15).sum())
    rows.append((p, len(cands), cn, len(cands) - cn, wide, wide2, narrow))
W = np.concatenate(allw)
print('all rune-band components: n=%d  width med %d  p95 %d  p99 %d  p99.9 %d  max %d'
      % (len(W), np.median(W), np.percentile(W, 95), np.percentile(W, 99),
         np.percentile(W, 99.9), W.max()))
for t in [85, 88, 90, 92, 95, 100]:
    print('  w > %3d : %d' % (t, (W > t).sum()))
print()
tot = [0, 0, 0, 0, 0]
for (p, n, cn, d, wide, wide2, narrow) in rows:
    if cn and abs(d) > 0:
        print('p%-2d seg %4d canon %4d delta %+4d  wide>90 %2d  wide>130 %d  narrow<15 %d'
              % (p, n, cn, d, wide, wide2, narrow))
    tot[0] += n; tot[1] += cn; tot[2] += wide; tot[3] += wide2; tot[4] += narrow
print('\nTOTAL seg %d canon %d delta %+d | wide>90 %d  wide>130 %d  narrow<15 %d'
      % (tot[0], tot[1], tot[0] - tot[1], tot[2], tot[3], tot[4]))
print('delta if every wide>90 component were split into 2: %+d'
      % (tot[0] + tot[2] - tot[1]))
