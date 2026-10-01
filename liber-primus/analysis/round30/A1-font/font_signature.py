#!/usr/bin/env python3
"""
Confirm the font signature across the WHOLE book and test the variant channel.
For each rune label, gather all clean instances across all 56 relikd pages,
then within each label cluster by exact-shape (best-aligned IoU>=0.97 = same
glyph outline). Report:
  - does each rune have at least one large pixel-identical cluster? (font proof)
  - how many distinct exact-shape clusters per rune? (variant count)
  - if variants exist, are they a real second glyph design or segmentation noise?
To beat segmentation noise we KEEP only 'clean' crops: a crop is clean if its
width is within [0.55,1.5]*median width for that rune AND its area within
[0.6,1.4]*median area. Noise crops (merged/split) are excluded from variant
counting but counted as 'unclassified'.
"""
import os, itertools, random, json
import numpy as np
from PIL import Image
from scipy import ndimage

THRESH=128
RUNES='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'
R2I={r:i for i,r in enumerate(RUNES)}

def load_ink(p):
    a=np.asarray(Image.open(p).convert('L')); return (a<THRESH).astype(np.uint8)
def med_h(ink):
    lbl,n=ndimage.label(ink); sl=ndimage.find_objects(lbl)
    hs=sorted((s[0].stop-s[0].start) for s in sl if s); return hs[len(hs)//2] if hs else 0
def clean_img(ink,mh):
    lbl,n=ndimage.label(ink); sl=ndimage.find_objects(lbl); keep=np.zeros_like(ink)
    for i,s in enumerate(sl,1):
        if not s: continue
        h=s[0].stop-s[0].start; w=s[1].stop-s[1].start; area=int((lbl[s]==i).sum())
        if h>1.6*mh or w>1.6*mh: continue
        if h<0.30*mh and area<0.04*mh*mh: continue
        keep[s][lbl[s]==i]=1
    return keep
def find_lines(ink,mh):
    r=ink.sum(1)>0; out=[]; st=None
    for y,v in enumerate(r):
        if v and st is None: st=y
        elif not v and st is not None: out.append((st,y)); st=None
    if st is not None: out.append((st,len(r)))
    return [(a,b) for a,b in out if (b-a)>0.5*mh]
def valley_boundaries(cols,n,min_w):
    W=len(cols)
    if n<=1: return [0,W]
    order=sorted(range(1,W),key=lambda x:cols[x]); chosen=[]; mx=cols.max()
    for x in order:
        if cols[x]>mx*0.6: continue
        if x>=min_w and x<=W-min_w and all(abs(x-c)>=min_w for c in chosen): chosen.append(x)
        if len(chosen)==n-1: break
    return [0]+sorted(chosen)+[W]
def trim(m):
    ys,xs=np.where(m)
    if len(ys)==0: return m
    return m[ys.min():ys.max()+1,xs.min():xs.max()+1]
def extract(path,kris):
    ink=load_ink(path); mh=med_h(ink); c=clean_img(ink,mh); dl=find_lines(c,mh)
    if len(dl)!=len(kris):
        m=min(len(dl),len(kris)); dl=dl[:m]; kris=kris[:m]
    out=[]
    for (y0,y1),krow in zip(dl,kris):
        band=c[y0:y1]; cs=band.sum(0); nz=np.where(cs>0)[0]
        if len(nz)==0: continue
        xL,xR=nz[0],nz[-1]+1; sub=band[:,xL:xR]; cols=sub.sum(0).astype(float)
        n=len(krow); min_w=max(4,int((xR-xL)/n*0.40)); b=valley_boundaries(cols,n,min_w)
        if len(b)-1!=n: b=[int(round((xR-xL)*k/n)) for k in range(n+1)]
        for k,rune in enumerate(krow):
            out.append((rune,trim(sub[:,b[k]:b[k+1]])))
    return out
def best_iou(m1,m2,ms=5):
    H=max(m1.shape[0],m2.shape[0])+2*ms; W=max(m1.shape[1],m2.shape[1])+2*ms
    A=np.zeros((H,W),bool); A[ms:ms+m1.shape[0],ms:ms+m1.shape[1]]=m1.astype(bool)
    best=0.0
    for dy in range(-ms,ms+1):
        for dx in range(-ms,ms+1):
            B=np.zeros((H,W),bool); y0=ms+dy; x0=ms+dx
            B[y0:y0+m2.shape[0],x0:x0+m2.shape[1]]=m2.astype(bool)
            u=(A|B).sum()
            if u:
                v=(A&B).sum()/u
                if v>best: best=v
    return best

def parse(blk):
    L=[]
    for ln in blk.replace('/','\n').split('\n'):
        rs=[c for c in ln if c in R2I]
        if rs: L.append(rs)
    return L

if __name__=='__main__':
    t=open('data/krisyotam_runes.txt').read().split('%')
    kp=[parse(b) for b in t if parse(b)]
    from collections import defaultdict
    allg=defaultdict(list)
    npages=min(len(kp), 54)  # LP2 unsolved pages have krisyotam runes; relikd p0..p53
    for pi in range(npages):
        path=f'data/relikd/p{pi}.jpg'
        if not os.path.exists(path): continue
        for r,m in extract(path,kp[pi]):
            if m.size>0: allg[r].append((pi,m))
    # keep clean crops per rune (width & area near median)
    report={}
    for r,items in allg.items():
        ws=np.array([m.shape[1] for _,m in items]); ars=np.array([int(m.sum()) for _,m in items])
        mw=np.median(ws); ma=np.median(ars)
        clean=[(pi,m) for (pi,m) in items if 0.6*mw<=m.shape[1]<=1.5*mw and 0.6*ma<=int(m.sum())<=1.4*ma]
        report[r]=dict(total=len(items),clean=len(clean),items=clean)
    # For 6 distinctive runes, measure max same-rune IoU on clean crops (font proof)
    print('=== FONT SIGNATURE: max same-rune IoU on CLEAN crops (across book) ===')
    fontproof={}
    for r in RUNES:
        cl=report[r]['items']
        if len(cl)<3:
            print(f'  {r}: only {len(cl)} clean, skip'); continue
        random.seed(2)
        idx=list(range(len(cl))); random.shuffle(idx); idx=idx[:20]
        best=0.0; nident=0
        pairs=list(itertools.combinations(idx,2))[:120]
        vs=[]
        for i,j in pairs:
            v=best_iou(cl[i][1],cl[j][1]); vs.append(v)
            if v>=0.97: nident+=1
        vs=np.array(vs)
        fontproof[r]=dict(clean=len(cl),maxIoU=round(float(vs.max()),3),
                          p90=round(float(np.percentile(vs,90)),3),
                          frac_ident=round(nident/len(vs),3))
        print(f'  {r}: clean={len(cl):3d} maxIoU={vs.max():.3f} p90={np.percentile(vs,90):.3f} frac>=0.97={nident/len(vs):.2f}')
    json.dump({k:v for k,v in fontproof.items()}, open('analysis/round30/A1-font/font_signature.json','w'), indent=1)
    print('wrote font_signature.json')
