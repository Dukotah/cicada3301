import numpy as np, json
from PIL import Image

def load(path):
    im = Image.open(path).convert('L')
    return im, (np.asarray(im).astype(np.float32)<128).astype(np.uint8)

def find_tokens(ink, r0, r1):
    """find 8 token clusters (2-char groups) in row band; return list of (x0,x1)."""
    band = ink[r0:r1]
    colsum = band.sum(axis=0)
    on = colsum > 0
    # raw char segments
    segs=[]; s=None
    for i,v in enumerate(on):
        if v and s is None: s=i
        elif not v and s is not None:
            segs.append([s,i]); s=None
    if s is not None: segs.append([s,len(on)])
    # merge segments into 8 tokens by gap size: intra-token gaps small, inter-token gaps large
    if len(segs)<2: return segs
    gaps = sorted((segs[i+1][0]-segs[i][1]) for i in range(len(segs)-1))
    # 7 largest gaps separate 8 tokens
    if len(gaps)>=7:
        gap_thr = gaps[-7]  # threshold between 7th-largest gap
        # use midpoint below the 7 big gaps
        big = sorted(gaps)[-7]
        small = sorted(gaps)[:-7]
        thr = (max(small) + big)/2 if small else big-1
    else:
        thr = 30
    tokens=[]; cur=[segs[0][0], segs[0][1]]
    for i in range(1,len(segs)):
        gap = segs[i][0]-cur[1]
        if gap > thr:
            tokens.append(tuple(cur)); cur=[segs[i][0], segs[i][1]]
        else:
            cur[1]=segs[i][1]
    tokens.append(tuple(cur))
    return tokens

targets = [
 # idx, page, central_row_y0,y1, col, expect_token
 (25, 49, 1787,1856, 1, "3I"),
 (175,50, 2599,2668, 7, "0I"),
 (182,50, 2773,2847, 6, "2l"),
 (199,51, 809, 878,  7, "0l"),
 (215,51, 1167,1236, 7, "1O"),
 (237,51, 1704,1773, 5, "0W"),
]
# also a POSITIVE CONTROL non-contested cell: idx 24 p49 tr3 col0 = "1n" ; and idx 200 p51 tr2 col0="1o"
controls = [
 (24, 49, 1787,1856, 0, "1n"),
 (176,50, 2773,2847, 0, "3t"),  # p50 tr12 col0
 (200,51, 1346,1416, 0, "0v"),  # p51 tr4 col0
]

imgs={}
def get(p):
    if p not in imgs: imgs[p]=load(f"/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/relikd/p{p}.jpg")
    return imgs[p]

meta=[]
for label,rows in [("contested",targets),("control",controls)]:
    for tup in rows:
        idx,p,y0,y1,col,exp = tup
        im,ink = get(p)
        toks = find_tokens(ink,y0,y1)
        if col>=len(toks):
            print(f"idx {idx}: only {len(toks)} tokens found, want col {col}"); continue
        x0,x1 = toks[col]
        pad=12
        crop = im.crop((max(0,x0-pad), y0-8, min(im.size[0],x1+pad), y1+8))
        scale=6
        crop_big = crop.resize((crop.size[0]*scale, crop.size[1]*scale), Image.NEAREST)
        fn=f"crops/{label}_idx{idx}_p{p}_col{col}_exp{exp}.png"
        crop_big.save(fn)
        meta.append(dict(idx=idx,page=p,col=col,expect=exp,ntoks=len(toks),x=[int(x0),int(x1)],y=[y0,y1],file=fn))
        print(f"idx {idx:3d} p{p} col{col} exp='{exp}' ntoks={len(toks)} x=[{x0},{x1}] -> {fn}")
json.dump(meta,open("crops/meta.json","w"),indent=2)
