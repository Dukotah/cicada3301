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
def last_char(ink,x0,x1,y0,y1,span=115):
    ymid=(y0+y1)//2;yy0=max(0,ymid-span)
    sub=ink[yy0:ymid+span,x0:x1];on=sub.sum(axis=0)>0
    segs=[];s=None
    for i,v in enumerate(on):
        if v and s is None:s=i
        elif not v and s is not None:segs.append([s,i]);s=None
    if s is not None:segs.append([s,len(on)])
    merged=[]
    for seg in segs:
        if merged and seg[0]-merged[-1][1]<=8:merged[-1][1]=seg[1]
        else:merged.append(list(seg))
    a,b=merged[-1];col=sub[:,a:b];rows=np.where(col.sum(axis=1)>0)[0]
    return col[rows.min():rows.max()+1]
imgs={}
def get(p):
    if p not in imgs:imgs[p]=load(f"/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/relikd/p{p}.jpg")
    return imgs[p]
bars={
 "idx25_I":(49,1787,1856,1),"idx175_I":(50,2599,2668,7),
 "idx182_l":(50,2773,2847,6),"idx199_l":(51,809,878,7),"idx246_i?":(51,1883,1952,6),
}
glyphs={}
for name,(p,y0,y1,col) in bars.items():
    im,ink=get(p);toks=token_boxes(ink,y0,y1)
    g=last_char(ink,toks[col][0],toks[col][1],y0,y1)
    glyphs[name]=g
    # width profile per row (top->bottom), normalized to 20 samples
    h,w=g.shape
    rows_w=[int(g[r].sum()) for r in range(h)]
    # sample 10 points
    samp=[rows_w[int(i*(h-1)/9)] for i in range(10)]
    print(f"{name:12s}: h={h} w={w} widthprofile(top→bot)={samp}")
# pairwise: are the bar shapes identical? resize all to 60x12 and compare
def norm(g):
    from PIL import Image as I
    return np.asarray(I.fromarray((g*255).astype(np.uint8)).resize((12,60),I.LANCZOS))>128
base=norm(glyphs["idx25_I"])
for name,g in glyphs.items():
    n=norm(g); diff=(n!=base).sum()
    print(f"  {name:12s} vs idx25_I: {diff}/{n.size} px differ")
