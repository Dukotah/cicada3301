"""Diagnostic: exact glyph-level layout of the two LP2 solved control pages,
compared to their canon rune strings.  Locates every segmentation miss."""
import sys, os, numpy as np
import t1_reader as T
sys.path.insert(0, os.path.join(T.LP, 'src'))
from lp.gematria import RUNE_TO_IDX, IDX_TO_TRANS

canon = T.canon_pages()
FW = {'F':0.711,'U':1.251,'TH':0.772,'O':0.819,'R':0.745,'C':1.081,'G':1.036,'W':0.857,
      'H':1.157,'N':0.797,'I':0.369,'J':1.031,'EO':0.940,'P':0.988,'X':1.352,'S':0.856,
      'T':1.133,'B':0.775,'E':1.211,'M':1.402,'L':0.707,'NG':1.093,'OE':0.957,'D':1.205,
      'A':0.752,'AE':0.785,'Y':1.172,'IA':1.200,'EA':1.845}

for img, ce, name in [(56, 55, '73.jpg'), (57, 56, '74.jpg')]:
    path = T.vendor_path(name)
    ink = T.page_ink(path)
    comps = T.components(ink)
    cands = T.rune_candidates(comps)
    rows = T.group_rows(cands)
    runes = canon[ce]
    tr = [IDX_TO_TRANS[RUNE_TO_IDX[c]] for c in runes]
    print('\n===== %s (LP2 p%d)  canon %d runes, segmented %d, rows %d'
          % (name, img, len(runes), len(cands), len(rows)))
    print('canon:', ' '.join(tr))
    k = 0
    for ri, r in enumerate(rows):
        ws = [cands[j]['w'] for j in r]
        print(' row %d n=%2d  widths %s' % (ri, len(r), ws))
    # near-band components that were rejected
    near = [c for c in comps if (60 <= c['h'] < 95) or (135 < c['h'] <= 200)]
    print(' rejected components with h in [60,95)u(135,200]: %d  -> %s'
          % (len(near), [(c['h'], c['w']) for c in near][:20]))
