import numpy as np, json
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

def char_boxes_in_token(ink,x0,x1,y0,y1):
    """split a token into its individual chars by x-gap, return (charx0,charx1,ytop,ybot,width,height)."""
    span=115; ymid=(y0+y1)//2; yy0=max(0,ymid-span)
    sub=ink[yy0:ymid+span, x0:x1]
    on=sub.sum(axis=0)>0
    segs=[];s=None
    for i,v in enumerate(on):
        if v and s is None:s=i
        elif not v and s is not None:segs.append([s,i]);s=None
    if s is not None:segs.append([s,len(on)])
    # merge tiny gaps within a char (<=8px)
    merged=[]
    for seg in segs:
        if merged and seg[0]-merged[-1][1]<=8: merged[-1][1]=seg[1]
        else: merged.append(seg)
    out=[]
    for a,b in merged:
        col=sub[:,a:b]; rows=np.where(col.sum(axis=1)>0)[0]
        if len(rows)==0: continue
        out.append(dict(x0=int(x0+a),x1=int(x0+b),ytop=int(yy0+rows.min()),ybot=int(yy0+rows.max()+1),
                        w=int(b-a),h=int(rows.max()-rows.min()+1)))
    return out

cells=[
 (25,49,1787,1856,1,"3I"),(175,50,2599,2668,7,"0I"),(182,50,2773,2847,6,"2l"),
 (199,51,809,878,7,"0l"),(215,51,1167,1236,7,"1O"),(237,51,1704,1773,5,"0W"),
 (24,49,1787,1856,0,"1n"),(172,50,2599,2668,4,"2S"),
]
imgs={}
def get(p):
    if p not in imgs:imgs[p]=load(f"/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/relikd/p{p}.jpg")
    return imgs[p]
for idx,p,y0,y1,col,exp in cells:
    im,ink=get(p); toks=token_boxes(ink,y0,y1); x0,x1=toks[col]
    chars=char_boxes_in_token(ink,x0,x1,y0,y1)
    desc=" | ".join(f"w{c['w']} h{c['h']} top{c['ytop']} bot{c['ybot']}" for c in chars)
    print(f"idx{idx:3d} '{exp}': {len(chars)} chars: {desc}")
