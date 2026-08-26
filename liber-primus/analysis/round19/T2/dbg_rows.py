import os
import sys
from PIL import Image
import t2lib as T

p = sys.argv[1]
ylo, yhi = int(sys.argv[2]), int(sys.argv[3])
path = os.path.join(T.VENDOR, p) if not p.startswith('p') else os.path.join(T.RELIKD, p)
Image.open(path).convert('L').crop((250, ylo - 30, 2150, yhi + 30)).save(
    os.path.join(T.HERE, 'crop_dbg.png'))
ink = T.page_ink(path)
cs = [c for c in T.components(ink) if c['y0'] < yhi and c['y1'] > ylo]
for c in sorted(cs, key=lambda c: c['x0']):
    tag = 'KEEP' if (c['h'] >= 40 and 330 < (c['x0'] + c['x1']) / 2 < 2070) else 'drop'
    print('%s h=%3d w=%3d x=%4d..%4d y=%4d..%4d' %
          (tag, c['h'], c['w'], c['x0'], c['x1'], c['y0'], c['y1']))
