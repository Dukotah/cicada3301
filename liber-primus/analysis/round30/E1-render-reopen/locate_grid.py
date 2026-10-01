import numpy as np
from PIL import Image

def load_bin(path):
    im = Image.open(path).convert('L')
    a = np.asarray(im).astype(np.float32)
    ink = (a < 128).astype(np.uint8)  # black glyphs on white
    return im, a, ink

def find_rows(ink, min_gap=20):
    rowsum = ink.sum(axis=1)
    thr = rowsum.max()*0.02
    on = rowsum > thr
    rows=[]; s=None
    for i,v in enumerate(on):
        if v and s is None: s=i
        elif not v and s is not None:
            if i-s>10: rows.append((s,i)); 
            s=None
    if s is not None: rows.append((s,len(on)))
    return rows

def find_cols_in_band(ink, r0, r1, expect=8):
    band = ink[r0:r1]
    colsum = band.sum(axis=0)
    thr = colsum.max()*0.02
    on = colsum > thr
    segs=[]; s=None
    for i,v in enumerate(on):
        if v and s is None: s=i
        elif not v and s is not None:
            segs.append((s,i)); s=None
    if s is not None: segs.append((s,len(on)))
    return segs

for p in (49,50,51):
    im,a,ink = load_bin(f"/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/relikd/p{p}.jpg")
    rows = find_rows(ink)
    print(f"=== p{p}: {len(rows)} ink rows, img {im.size} ===")
    for ri,(r0,r1) in enumerate(rows):
        segs = find_cols_in_band(ink,r0,r1)
        print(f"  row{ri:2d} y=[{r0},{r1}] h={r1-r0} nsegs={len(segs)}")
