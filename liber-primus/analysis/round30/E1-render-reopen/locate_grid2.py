import numpy as np
from PIL import Image

def load_ink(path):
    im = Image.open(path).convert('L')
    a = np.asarray(im).astype(np.float32)
    return im, (a<128).astype(np.uint8)

# central text region: crop out the trees. From overview, text sits roughly middle 55%.
# img width 2400 -> use x in [600,1800] to avoid trees.
XC0, XC1 = 620, 1800

def rows_in_center(ink):
    band = ink[:, XC0:XC1]
    rowsum = band.sum(axis=1)
    thr = max(rowsum.max()*0.03, 5)
    on = rowsum > thr
    rows=[]; s=None
    for i,v in enumerate(on):
        if v and s is None: s=i
        elif not v and s is not None:
            if i-s>25: rows.append((s,i))
            s=None
    if s is not None and len(on)-s>25: rows.append((s,len(on)))
    return rows

for p in (49,50,51):
    im,ink = load_ink(f"/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/relikd/p{p}.jpg")
    rows = rows_in_center(ink)
    print(f"=== p{p}: {len(rows)} central rows ===")
    for ri,(r0,r1) in enumerate(rows):
        print(f"  row{ri:2d} y=[{r0},{r1}] h={r1-r0}")
