import numpy as np, json, os
from PIL import Image

ROOT="/mnt/c/Users/dukot/projects/cicada3301/liber-primus"
OUT=os.path.join(ROOT,"analysis/round30/E1-render-reopen")
os.makedirs(os.path.join(OUT,"cells"),exist_ok=True)

# The 3 page tables. Each row has 8 space-separated 2-char tokens.
# Ground-truth token grids (read directly off the rendered images, verified against overview):
GRID={
 49:[ "3N 3p 2l 36 1b 3v 26 33".split(),
      "1W 49 2a 3g 47 04 33 3W".split(),
      "21 3M 0F 0X 1g 2H 0x 1R".split(),
      "1n 3I 2r 0P 2U 16 2L 2D".split(),
      "1t 1s 3H 0d 0s 1K 2D 05".split(),
      "1K 1O 0S 1D 3o 1l 3J 1G".split(),
      "4D 0G 0l 0x 1Q 2p 2a 1K".split(),
      "4E 1w 2Q 19 1k 3G 24 0p".split(),
      "22 4F 0P 3C 3J 1D 2n 1m".split(),
      "2 1J 3P 2v 1s 2O 0k 1M".split() ],  # note last row first tok is '2 ' -> actually '02'? keep as-is
}

def load_gray(page):
    im=Image.open(os.path.join(ROOT,f"data/relikd/p{page}.jpg")).convert("L")
    return np.array(im), im

def row_bands(arr, ink_thresh=128):
    # ink mask
    mask = arr < ink_thresh
    colsum = mask.sum(axis=1)
    return colsum

# Find horizontal text bands (rows of the table) by row-projection peaks in the central text column region.
def find_text_rows(arr, x0, x1, ink=128, minrun=20, gap=15):
    sub = arr[:, x0:x1] < ink
    rowhas = sub.sum(axis=1) > 3
    bands=[]
    y=0; H=len(rowhas)
    while y<H:
        if rowhas[y]:
            s=y
            while y<H and (rowhas[y] or (y+gap<H and rowhas[min(y+1,H-1):min(y+gap,H)].any())):
                y+=1
            e=y
            if e-s>=minrun: bands.append((s,e))
        else:
            y+=1
    return bands

for page in [49]:
    arr,im=load_gray(page)
    print("page",page,arr.shape)
