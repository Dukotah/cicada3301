import numpy as np, json
from PIL import Image

def load(path):
    im = Image.open(path).convert('L')
    return im, (np.asarray(im).astype(np.float32)<128).astype(np.uint8)

def token_boxes(ink, y0, y1):
    band = ink[y0:y1]
    colsum = band.sum(axis=0); on=colsum>0
    segs=[]; s=None
    for i,v in enumerate(on):
        if v and s is None: s=i
        elif not v and s is not None: segs.append([s,i]); s=None
    if s is not None: segs.append([s,len(on)])
    if len(segs)<2: return [tuple(x) for x in segs]
    gaps=[segs[i+1][0]-segs[i][1] for i in range(len(segs)-1)]
    sg=sorted(gaps); thr=(sg[-7]+sg[-8])/2 if len(sg)>=8 else (sg[-7]-1 if len(sg)>=7 else 30)
    toks=[]; cur=[segs[0][0],segs[0][1]]
    for i in range(1,len(segs)):
        if segs[i][0]-cur[1]>thr: toks.append(tuple(cur)); cur=[segs[i][0],segs[i][1]]
        else: cur[1]=segs[i][1]
    toks.append(tuple(cur))
    return toks

def tight_vert(ink, x0, x1, ymid, span=120):
    """find true vertical extent of ink in the x-window around ymid."""
    sub = ink[max(0,ymid-span):ymid+span, x0:x1]
    rows=np.where(sub.sum(axis=1)>0)[0]
    if len(rows)==0: return ymid-40, ymid+40
    return max(0,ymid-span)+rows.min(), max(0,ymid-span)+rows.max()+1

cells=[
 (25,49,1787,1856,1,"3I","contested"),
 (175,50,2599,2668,7,"0I","contested"),
 (182,50,2773,2847,6,"2l","contested"),
 (199,51,809,878,7,"0l","contested"),
 (215,51,1167,1236,7,"1O","contested"),
 (237,51,1704,1773,5,"0W","contested"),
 (24,49,1787,1856,0,"1n","control"),
 (172,50,2599,2668,4,"2S","control"),
 (200,51,1346,1416,0,"0v","control"),
 (198,51,809,878,6,"1j","control"),  # neighbor of 199, has descender j
]
imgs={}
def get(p):
    if p not in imgs: imgs[p]=load(f"/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/relikd/p{p}.jpg")
    return imgs[p]
meta=[]
for idx,p,y0,y1,col,exp,label in cells:
    im,ink=get(p)
    toks=token_boxes(ink,y0,y1)
    if col>=len(toks): print(f"idx{idx}: {len(toks)} toks"); continue
    x0,x1=toks[col]; ymid=(y0+y1)//2
    ty0,ty1=tight_vert(ink,max(0,x0-5),x1+5,ymid,span=110)
    padx=max(25,int((x1-x0)*0.4)); pady=15
    box=(max(0,x0-padx),max(0,ty0-pady),min(2400,x1+padx),min(3600,ty1+pady))
    crop=im.crop(box)
    sc=max(1,int(260/crop.size[1]))
    big=crop.resize((crop.size[0]*sc,crop.size[1]*sc),Image.LANCZOS)
    fn=f"crops/v3_idx{idx}_p{p}_{exp}.png"
    big.save(fn)
    meta.append(dict(idx=idx,page=p,col=col,expect=exp,label=label,box=list(box),file=fn,tokx=[int(x0),int(x1)]))
    print(f"idx{idx:3d} p{p} col{col} '{exp}' x=[{x0},{x1}] y=[{ty0},{ty1}] -> {fn} {big.size}")
json.dump(meta,open("crops/meta3.json","w"),indent=2)
