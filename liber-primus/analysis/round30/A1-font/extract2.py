#!/usr/bin/env python3
"""
Improved anchored extractor v2.
Key fixes over v1:
 - trim each line band to its ink x-extent before cutting (kills margin cuts)
 - remove separator glyphs (word-dots '·', hyphens) via small-component filter
   BEFORE cutting, so cell count == rune count
 - valley-cut within the ink extent with min-width guard
 - register each glyph by bbox-trim + pad-to-common-box before IoU
Outputs per-page glyph masks (npz) + labels, and runs the control.
"""
import sys, os, json, itertools, random
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

def clean(ink,mh):
    """remove ornaments (too big) AND separators (dots/hyphens, too small)."""
    lbl,n=ndimage.label(ink); sl=ndimage.find_objects(lbl)
    keep=np.zeros_like(ink)
    for i,s in enumerate(sl,1):
        if not s: continue
        h=s[0].stop-s[0].start; w=s[1].stop-s[1].start
        area=int((lbl[s]==i).sum())
        if h>1.6*mh or w>1.6*mh: continue           # ornament/dropcap
        if h<0.30*mh and area<0.04*mh*mh: continue   # separator dot
        keep[s][lbl[s]==i]=1
    return keep

def find_lines(ink,mh):
    r=ink.sum(1)>0; out=[]; st=None
    for y,v in enumerate(r):
        if v and st is None: st=y
        elif not v and st is not None: out.append((st,y)); st=None
    if st is not None: out.append((st,len(r)))
    return [(a,b) for a,b in out if (b-a)>0.5*mh]

def valley_boundaries(cols, n, min_w):
    W=len(cols)
    if n<=1: return [0,W]
    order=sorted(range(1,W), key=lambda x:cols[x])
    chosen=[]
    for x in order:
        if cols[x] > cols.max()*0.6:  # don't cut through thick ink
            continue
        if x>=min_w and x<=W-min_w and all(abs(x-c)>=min_w for c in chosen):
            chosen.append(x)
        if len(chosen)==n-1: break
    return [0]+sorted(chosen)+[W]

def trim(m):
    ys,xs=np.where(m)
    if len(ys)==0: return m
    return m[ys.min():ys.max()+1, xs.min():xs.max()+1]

def extract_page(path, kris_lines):
    ink=load_ink(path); mh=med_h(ink); c=clean(ink,mh)
    dlines=find_lines(c,mh)
    glyphs=[]
    if len(dlines)!=len(kris_lines):
        m=min(len(dlines),len(kris_lines))
        dlines=dlines[:m]; kris_lines=kris_lines[:m]
    for (y0,y1),krow in zip(dlines,kris_lines):
        band=c[y0:y1]
        # trim to ink x-extent
        colsum=band.sum(0)
        nz=np.where(colsum>0)[0]
        if len(nz)==0: continue
        xL,xR=nz[0],nz[-1]+1
        sub=band[:,xL:xR]
        cols=sub.sum(0).astype(float)
        n=len(krow)
        min_w=max(4,int((xR-xL)/n*0.40))
        b=valley_boundaries(cols,n,min_w)
        if len(b)-1!=n:
            # fallback: equal spacing
            b=[int(round((xR-xL)*k/n)) for k in range(n+1)]
        for k,rune in enumerate(krow):
            cell=sub[:,b[k]:b[k+1]]
            tm=trim(cell)
            glyphs.append(dict(rune=rune,page=os.path.basename(path),line=int(y0),
                               h=int(tm.shape[0]),w=int(tm.shape[1]),area=int(tm.sum()),mask=tm))
    return glyphs, mh

def reg_iou(m1,m2):
    """align by centroid within a common box, then IoU."""
    H=max(m1.shape[0],m2.shape[0]); W=max(m1.shape[1],m2.shape[1])
    def place(m):
        b=np.zeros((H,W),bool); b[:m.shape[0],:m.shape[1]]=m.astype(bool); return b
    A=place(m1);B=place(m2)
    u=(A|B).sum(); return (A&B).sum()/u if u else 1.0

def control(glyphs):
    from collections import defaultdict
    by=defaultdict(list)
    for g in glyphs: by[g['rune']].append(g['mask'])
    intra=[]
    per={}
    for r,ms in by.items():
        if len(ms)<2: continue
        pairs=list(itertools.combinations(range(len(ms)),2))
        random.seed(0); random.shuffle(pairs); pairs=pairs[:40]
        v=float(np.mean([reg_iou(ms[i],ms[j]) for i,j in pairs]))
        per[r]=(len(ms),v); intra.append(v)
    # cross
    labs=[r for r in by if len(by[r])>=2]
    cross=[]
    for a,bb in itertools.combinations(labs,2):
        cv=np.mean([reg_iou(by[a][i],by[bb][j]) for i in range(min(3,len(by[a]))) for j in range(min(3,len(by[bb])))])
        cross.append(cv)
    return per, float(np.mean(intra)), float(np.mean(cross))

if __name__=='__main__':
    t=open('data/krisyotam_runes.txt').read().split('%')
    def parse(blk):
        L=[]
        for ln in blk.replace('/','\n').split('\n'):
            rs=[c for c in ln if c in R2I]
            if rs: L.append(rs)
        return L
    kp=[parse(b) for b in t if parse(b)]
    g,mh=extract_page('data/relikd/p0.jpg', kp[0])
    print('p0 glyphs',len(g),'expected',sum(len(l) for l in kp[0]),'med_h',mh)
    per,intra,cross=control(g)
    print('MEAN intra-label IoU:',round(intra,3),' MEAN cross-label IoU:',round(cross,3),
          ' separation:',round(intra-cross,3))
    for r in sorted(per,key=lambda r:-per[r][1]):
        print(f'  {r} n={per[r][0]:2d} IoU={per[r][1]:.3f}')
