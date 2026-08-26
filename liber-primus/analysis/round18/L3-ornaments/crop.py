"""L3 stage 2 -- crop every catalogued band from the verified master renders.

Emits crops/<id>_p<page>.png at 1:1 plus a 3x upscale for bands under 200 px tall
(the "short band" candidates P-9 names).  Images are the sha256-verified
data/relikd/p*.jpg (verify_capsule.py --only images = PASS 56/56).
"""
import os, json, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
IMG = os.path.join(ROOT, 'data', 'relikd')
OUT = os.path.join(HERE, 'crops')
os.makedirs(OUT, exist_ok=True)

inv = json.load(open(os.path.join(HERE, 'inventory.json')))
MAXH = int(sys.argv[1]) if len(sys.argv) > 1 else 500

cache = {}
n = 0
for r in inv:
    if r['h'] > MAXH:
        continue
    p = r['page']
    if p not in cache:
        cache[p] = Image.open(os.path.join(IMG, 'p%d.jpg' % p)).convert('L')
    im = cache[p]
    pad = 12
    box = (max(0, r['x'][0] - pad), max(0, r['y'][0] - pad),
           min(im.width, r['x'][1] + pad), min(im.height, r['y'][1] + pad))
    c = im.crop(box)
    z = 3 if c.height < 200 else 1
    if z > 1:
        c = c.resize((c.width * z, c.height * z), Image.LANCZOS)
    # cap width so the viewer sees detail
    c.save(os.path.join(OUT, '%s_p%02d_n%02d.png' % (r['id'], p, r['n'])))
    n += 1
print('cropped %d bands with h<=%d -> %s' % (n, MAXH, OUT))
