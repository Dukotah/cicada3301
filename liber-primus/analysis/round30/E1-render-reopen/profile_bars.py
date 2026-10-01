import numpy as np
from PIL import Image
def load(path):
    im=Image.open(path).convert('L'); return im,(np.asarray(im).astype(np.float32)<128).astype(np.uint8)
XC0,XC1=600,1810
def token_boxes(ink,y0,y1):
    band=ink[y0:y1,XC0:XC1]; on=band.sum(axis=0)>0
    segs=[];s=None
    for i,v in enumerate(on):
        if v and s is None:s=i
        elif not v and s is not None:segs.append([s+XC0,i+XC0]);s=None
    if s is not None:segs.append([s+XC0,len(on)+XC0])
    if len(segs)<2:return [tuple(x) for x in segs]
    gaps=[segs[i+1][0]-segs[i][1] for i in range(len(segs)-1)];sg=sorted(gaps)
    thr=(sg[-7]+sg[-8])/2 if len(sg)>=8 else (sg[-7]-1 if len(sg)>=7 else 30)
    toks=[];cur=[segs[0][0],segs[0][1]]
    for i in range(1,len(segs)):
        if segs[i][0]-cur[1]>thr:toks.append(tuple(cur));cur=[segs[i][0],segs[i][1]]
        else:cur[1]=segs[i][1]
    toks.append(tuple(cur));return toks

def second_char_profile(ink,x0,x1,y0,y1,span=115):
    ymid=(y0+y1)//2; yy0=max(0,ymid-span)
    sub=ink[yy0:ymid+span, x0:x1]
    on=sub.sum(axis=0)>0
    segs=[];s=None
    for i,v in enumerate(on):
        if v and s is None:s=i
        elif not v and s is not None:segs.append([s,i]);s=None
    if s is not None:segs.append([s,len(on)])
    merged=[]
    for seg in segs:
        if merged and seg[0]-merged[-1][1]<=8:merged[-1][1]=seg[1]
        else:merged.append(list(seg))
    # take last char cluster as 2nd char (rightmost)
    a,b=merged[-1]
    col=sub[:,a:b]
    rows=np.where(col.sum(axis=1)>0)[0]
    r0,r1=rows.min(),rows.max()
    ch=col[r0:r1+1]
    # per-row ink width
    widths=ch.sum(axis=1)
    # detect DOT: a gap between an upper blob and the main stroke
    rowhas=ch.sum(axis=1)>0
    gaps=[]
    run=0
    for v in rowhas:
        if not v: run+=1
        else:
            if run>0: gaps.append(run)
            run=0
    return dict(h=int(r1-r0+1), wtop=int(widths[0]), wmid=int(widths[len(widths)//2]),
                wbot=int(widths[-1]), wmax=int(widths.max()), wmin=int(widths.min()),
                internal_gaps=gaps, widths=[int(w) for w in widths])

cells=[
 (25,49,1787,1856,1,"3I"),(175,50,2599,2668,7,"0I"),(182,50,2773,2847,6,"2l"),
 (199,51,809,878,7,"0l"),
 # references:
 (246,51,None,None,6,"3i_REF"),  # need coords
]
imgs={}
def get(p):
    if p not in imgs:imgs[p]=load(f"/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/relikd/p{p}.jpg")
    return imgs[p]
# p51 rows: table rows 0-8 at central rows. idx246 = p51 local (246-184=62)-> row 7 col6. central row 7 y=[1883,1952]
refs=[
 (246,51,1883,1952,6,"3i_REF"),   # 3i lowercase i with dot
 (130,49,None,None,None,None),
]
allc=[
 (25,49,1787,1856,1,"3I"),(175,50,2599,2668,7,"0I"),(182,50,2773,2847,6,"2l"),(199,51,809,878,7,"0l"),
 (246,51,1883,1952,6,"3i_REF"),
 (198,51,809,878,6,"1j_REF"),
]
for idx,p,y0,y1,col,exp in allc:
    im,ink=get(p);toks=token_boxes(ink,y0,y1)
    if col>=len(toks): print(f"idx{idx} tok fail"); continue
    x0,x1=toks[col]
    pr=second_char_profile(ink,x0,x1,y0,y1)
    print(f"idx{idx:3d} '{exp}': h={pr['h']} wtop={pr['wtop']} wmid={pr['wmid']} wbot={pr['wbot']} wmax={pr['wmax']} gaps={pr['internal_gaps']}")
