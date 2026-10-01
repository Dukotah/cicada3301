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
def chars(ink,x0,x1,y0,y1,span=118):
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
        out.append(dict(top=int(yy0+rows.min()),bot=int(yy0+rows.max()+1),h=int(rows.max()-rows.min()+1),w=int(b-a)))
    return out
imgs={}
def get(p):
    if p not in imgs:imgs[p]=load(f"/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/relikd/p{p}.jpg")
    return imgs[p]

# CALIBRATION: known cap-height & ascender glyphs in THEIR OWN rows.
# We need cap-height ref and lowercase-l/ascender ref from same rows as targets.
# For each target, measure the bar AND the tallest CAP digit/letter in the same row = cap baseline.
def row_capheight(ink,y0,y1):
    """estimate cap-height top & baseline from all chars in the row (digits are cap-height)."""
    toks=token_boxes(ink,y0,y1)
    tops=[];bots=[]
    for x0,x1 in toks:
        for c in chars(ink,x0,x1,y0,y1):
            if c['h']>55:  # tall glyph = cap/ascender/digit
                tops.append(c['top']);bots.append(c['bot'])
    import statistics as st
    return st.median(tops),st.median(bots)

targets=[
 (25,49,1787,1856,1,"3I","tokI=18 dec i=44"),
 (175,50,2599,2668,7,"0I","tokI=18 dec i=44"),
 (182,50,2773,2847,6,"2l","tokl=47 dec L=21"),
 (199,51,809,878,7,"0l","tokl=47 dec L=21"),
]
for idx,p,y0,y1,col,tok,note in targets:
    im,ink=get(p)
    captop,capbot=row_capheight(ink,y0,y1)
    toks=token_boxes(ink,y0,y1);cs=chars(ink,toks[col][0],toks[col][1],y0,y1)
    bar=cs[-1]  # rightmost char
    asc=captop-bar['top']  # + = ascends above cap
    print(f"idx{idx:3d} tok='{tok}' [{note}]")
    print(f"    row cap-top≈{captop:.0f} base≈{capbot:.0f} | bar: top={bar['top']} bot={bar['bot']} h={bar['h']} w={bar['w']}  ascent_above_cap={asc:+.0f}")
