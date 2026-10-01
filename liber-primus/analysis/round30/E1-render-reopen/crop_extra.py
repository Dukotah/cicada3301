import numpy as np
from PIL import Image
def load(path):
    im=Image.open(path).convert('L');return im,(np.asarray(im).astype(np.float32)<128).astype(np.uint8)
XC0,XC1=600,1810
def token_boxes(ink,y0,y1):
    band=ink[y0:y1,XC0:XC1];on=band.sum(axis=0)>0
    segs=[];s=None
    for i,v in enumerate(on):
        if v and s is None:s=i
        elif not v and s is not None:segs.append([s+XC0,i+XC0]);s=None
    if s is not None:segs.append([s+XC0,len(on)+XC0])
    gaps=[segs[i+1][0]-segs[i][1] for i in range(len(segs)-1)];sg=sorted(gaps)
    thr=(sg[-7]+sg[-8])/2 if len(sg)>=8 else 30
    toks=[];cur=[segs[0][0],segs[0][1]]
    for i in range(1,len(segs)):
        if segs[i][0]-cur[1]>thr:toks.append(tuple(cur));cur=[segs[i][0],segs[i][1]]
        else:cur[1]=segs[i][1]
    toks.append(tuple(cur));return toks
imgs={}
def get(p):
    if p not in imgs:imgs[p]=load(f"/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/relikd/p{p}.jpg")
    return imgs[p]
# (idx,p,y0,y1,col,name)
extra=[
 (246,51,1883,1952,6,"3i"),      # resolved-i reference
 (130,49,None,None,None,None),
 (199,51,809,878,7,"0l_wide"),
 (198,51,809,878,6,"1j"),
 (26,49,1787,1856,7,"1M"),  # a token with cap M? no col7 row3=2D. skip
]
for idx,p,y0,y1,col,name in extra:
    if y0 is None: continue
    im,ink=get(p);toks=token_boxes(ink,y0,y1);x0,x1=toks[col]
    ymid=(y0+y1)//2
    box=(max(0,x0-30),ymid-120,x1+30,ymid+120)
    crop=im.crop(box);sc=max(1,int(300/crop.size[1]))
    crop.resize((crop.size[0]*sc,crop.size[1]*sc),Image.LANCZOS).save(f"crops/X_{name}_idx{idx}.png")
    print(f"idx{idx} '{name}' x=[{x0},{x1}] saved")
