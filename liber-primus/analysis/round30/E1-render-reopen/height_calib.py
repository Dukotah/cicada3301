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
        out.append((yy0+rows.min(),yy0+rows.max()+1,b-a))
    return out
imgs={}
def get(p):
    if p not in imgs:imgs[p]=load(f"/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/relikd/p{p}.jpg")
    return imgs[p]

# For each contested/ref cell, report the 2nd char's [top,bot] vs the FIRST char's [top,bot] (digit=cap ref)
cells=[
 (25,49,1787,1856,1,"3?"),(175,50,2599,2668,7,"0?"),(182,50,2773,2847,6,"2?"),(199,51,809,878,7,"0?"),
 (246,51,1883,1952,6,"3?"),
 # KNOWN L reference: idx45 = "1L" cap L. p49 tr5 col5 -> central row 8? tr5->central 5+3=8 y=[2145,2217]
 (45,49,2145,2217,5,"1L"),
 # a token known lowercase-l unambiguously? idx182/199 are the l candidates. hard.
]
for idx,p,y0,y1,col,name in cells:
    im,ink=get(p);toks=token_boxes(ink,y0,y1)
    if col>=len(toks): print(f"idx{idx} fail {len(toks)}toks"); continue
    x0,x1=toks[col];ext=char_extents(ink,x0,x1,y0,y1)
    if len(ext)<2: 
        print(f"idx{idx} '{name}': only {len(ext)} char extents: {ext}"); continue
    c1,c2=ext[0],ext[-1]
    print(f"idx{idx:3d} '{name}': digit top={c1[0]} bot={c1[1]} h={c1[1]-c1[0]} w={c1[2]} || 2nd top={c2[0]} bot={c2[1]} h={c2[1]-c2[0]} w={c2[2]}  (2nd ascends {c1[0]-c2[0]:+d} above cap, descends {c2[1]-c1[1]:+d} below base)")
