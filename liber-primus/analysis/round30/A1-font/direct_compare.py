#!/usr/bin/env python3
"""
Test whether identical runes render pixel-identically, WITHOUT relying on
line-cutting. We use the anchored cells but then re-extract each glyph's own
connected components restricted to its cell, and compare best-aligned via
cross-correlation (not naive top-left overlay).

If runes are a clean repeated vector font: two instances -> IoU ~0.9+ after
alignment. If hand-drawn/variant: IoU stays low even after best alignment.

Control:
  POS: same-rune best-aligned IoU should be high IF it's a font.
  NEG: different-rune best-aligned IoU should be low.
We report the distribution so the reader can see if there IS a font signature.
"""
import sys, os, itertools, random
import numpy as np
from PIL import Image
from scipy import ndimage
from scipy.signal import fftconvolve

THRESH=128
RUNES='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'
R2I={r:i for i,r in enumerate(RUNES)}

def load_ink(p):
    a=np.asarray(Image.open(p).convert('L')); return (a<THRESH).astype(np.uint8)
def med_h(ink):
    lbl,n=ndimage.label(ink); sl=ndimage.find_objects(lbl)
    hs=sorted((s[0].stop-s[0].start) for s in sl if s); return hs[len(hs)//2] if hs else 0
def clean(ink,mh):
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
    order=sorted(range(1,W),key=lambda x:cols[x]); chosen=[]
    mx=cols.max()
    for x in order:
        if cols[x]>mx*0.6: continue
        if x>=min_w and x<=W-min_w and all(abs(x-c)>=min_w for c in chosen): chosen.append(x)
        if len(chosen)==n-1: break
    return [0]+sorted(chosen)+[W]
def trim(m):
    ys,xs=np.where(m)
    if len(ys)==0: return m
    return m[ys.min():ys.max()+1, xs.min():xs.max()+1]

def extract(path,kris):
    ink=load_ink(path); mh=med_h(ink); c=clean(ink,mh); dl=find_lines(c,mh)
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
            out.append((rune, trim(sub[:,b[k]:b[k+1]])))
    return out

def best_iou(m1,m2,maxshift=6):
    """max IoU over integer shifts of m2 relative to m1 (both trimmed)."""
    H=max(m1.shape[0],m2.shape[0])+2*maxshift; W=max(m1.shape[1],m2.shape[1])+2*maxshift
    A=np.zeros((H,W),bool); A[maxshift:maxshift+m1.shape[0],maxshift:maxshift+m1.shape[1]]=m1.astype(bool)
    best=0.0
    for dy in range(-maxshift,maxshift+1):
        for dx in range(-maxshift,maxshift+1):
            B=np.zeros((H,W),bool)
            y0=maxshift+dy; x0=maxshift+dx
            B[y0:y0+m2.shape[0],x0:x0+m2.shape[1]]=m2.astype(bool)
            u=(A|B).sum()
            if u:
                v=(A&B).sum()/u
                if v>best: best=v
    return best

if __name__=='__main__':
    t=open('data/krisyotam_runes.txt').read().split('%')
    def parse(blk):
        L=[]
        for ln in blk.replace('/','\n').split('\n'):
            rs=[c for c in ln if c in R2I]
            if rs: L.append(rs)
        return L
    kp=[parse(b) for b in t if parse(b)]
    g=extract('data/relikd/p0.jpg',kp[0])
    from collections import defaultdict
    by=defaultdict(list)
    for r,m in g:
        if m.size>0: by[r].append(m)
    # same-rune best-aligned IoU
    same=[];
    per={}
    for r,ms in by.items():
        if len(ms)<2: continue
        pairs=list(itertools.combinations(range(len(ms)),2)); random.seed(1); random.shuffle(pairs); pairs=pairs[:15]
        v=[best_iou(ms[i],ms[j]) for i,j in pairs]
        per[r]=(len(ms),float(np.mean(v)),float(np.max(v))); same.extend(v)
    diff=[]
    labs=list(by)
    for _ in range(200):
        random.seed(); a,b=random.sample(labs,2)
        diff.append(best_iou(random.choice(by[a]),random.choice(by[b])))
    print('SAME-rune best-aligned IoU: mean',round(np.mean(same),3),'median',round(np.median(same),3),'p90',round(np.percentile(same,90),3))
    print('DIFF-rune best-aligned IoU: mean',round(np.mean(diff),3),'median',round(np.median(diff),3),'p90',round(np.percentile(diff,90),3))
    print('--- per-rune (n, mean, max) ---')
    for r in sorted(per,key=lambda r:-per[r][2]):
        print(f'  {r} n={per[r][0]:2d} mean={per[r][1]:.3f} max={per[r][2]:.3f}')
