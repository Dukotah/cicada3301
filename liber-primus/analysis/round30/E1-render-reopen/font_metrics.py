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
def char_extents(ink,x0,x1,y0,y1,span=115):
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
    out=[]
    for a,b in merged:
        col=sub[:,a:b];rows=np.where(col.sum(axis=1)>0)[0]
        if len(rows)==0:continue
        out.append((int(yy0+rows.min()),int(yy0+rows.max()+1),int(b-a)))
    return out
imgs={}
def get(p):
    if p not in imgs:imgs[p]=load(f"/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/relikd/p{p}.jpg")
    return imgs[p]
# tokens with known glyph types. (idx,p,central-row y0,y1,col,which-char,label)
# p49 tr rows: central = tr+3. p50: central=tr. p51: central=tr (rows0-8).
# row124(tr3 p49)=1n 3I 2r 0P 2U 16 2L 2D
# cap letters: P(col3),U(col4),L(col6),D(col7). lowercase: n(1n col0 2nd),r(2r col2 2nd)
tests=[
 ("CAP_P",49,1787,1856,3,1),  # 0P -> P
 ("CAP_U",49,1787,1856,4,1),  # 2U -> U
 ("CAP_L",49,1787,1856,6,1),  # 2L -> L
 ("CAP_D",49,1787,1856,7,1),  # 2D -> D
 ("low_n",49,1787,1856,0,1),  # 1n -> n
 ("low_r",49,1787,1856,2,1),  # 2r -> r
 ("BAR25_2nd",49,1787,1856,1,1), # 3I bar
 ("low_v_p51",51,1346,1416,0,1), # 0v tr4 -> v
]
for label,p,y0,y1,col,ci in tests:
    im,ink=get(p);toks=token_boxes(ink,y0,y1)
    ext=char_extents(ink,toks[col][0],toks[col][1],y0,y1)
    if ci>=len(ext): 
        print(f"{label}: ext={ext}"); continue
    t,b,w=ext[ci]
    print(f"{label:12s}: top={t} bot={b} h={b-t} w={w}")
