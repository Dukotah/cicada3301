#!/usr/bin/env python3
"""
Ground-truth-anchored glyph extractor + variant clustering.

We KNOW the exact rune sequence of each LP2 page from krisyotam_runes.txt.
Rather than guess glyph boundaries (unreliable for multi-stroke runes), we:
  1. detect text lines robustly (horizontal projection)
  2. map detected lines <-> krisyotam logical lines by rune-count best-alignment
  3. within each line, cut into N equal-ish cells guided by ink centroids so each
     cell = one rune, where N = known rune count for that line
  4. label each extracted glyph with its krisyotam rune
Then:
  POSITIVE CONTROL: for each rune label, do all its instances cluster to ONE
    (or few) exact shapes? If the extractor+font are consistent, instances of
    rune X should be pixel-near-identical -> high intra-label IoU, and
    different runes -> low IoU (NEGATIVE control).
  VARIANT CHANNEL: count exact-shape sub-clusters per rune label across the book.
"""
import sys, os, json
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
    lbl,n=ndimage.label(ink); sl=ndimage.find_objects(lbl); keep=np.zeros_like(ink); rem=0
    for i,s in enumerate(sl,1):
        if not s: continue
        h=s[0].stop-s[0].start; w=s[1].stop-s[1].start
        if h>1.6*mh or w>1.6*mh: rem+=1; continue
        keep[s][lbl[s]==i]=1
    return keep,rem

def find_lines(ink,mh):
    r=ink.sum(1)>0; out=[]; st=None
    for y,v in enumerate(r):
        if v and st is None: st=y
        elif not v and st is not None:
            out.append((st,y)); st=None
    if st is not None: out.append((st,len(r)))
    # keep only bands tall enough to be a text line (>0.5 med_h)
    out=[(a,b) for a,b in out if (b-a)>0.5*mh]
    return out

def kris_pages():
    t=open('data/krisyotam_runes.txt').read().split('%')
    pages=[]
    for blk in t:
        # split logical lines by '/' and newline
        lines=[]
        for ln in blk.replace('/','\n').split('\n'):
            rs=[c for c in ln if c in R2I]
            if rs: lines.append(rs)
        if lines: pages.append(lines)
    return pages

def cut_cells(band_ink, n):
    """Cut a line band into n rune cells using ink column profile.
    Strategy: compute column ink sums, find n cell centers by splitting the
    cumulative ink into n equal-mass segments (each rune ~ equal ink), then
    set boundaries at local minima nearest equal-mass splits."""
    cols=band_ink.sum(0).astype(float)
    total=cols.sum()
    if total<=0 or n<=0: return []
    # candidate boundaries at zero-ink columns
    W=len(cols)
    # equal-mass target boundaries
    cum=np.cumsum(cols)
    bounds=[0]
    for k in range(1,n):
        target=total*k/n
        x=int(np.searchsorted(cum,target))
        # snap to nearest low-ink column within +-window
        w=8
        lo=max(1,x-w); hi=min(W-1,x+w)
        seg=cols[lo:hi]
        if len(seg)>0:
            x=lo+int(np.argmin(seg))
        bounds.append(x)
    bounds.append(W)
    bounds=sorted(set(bounds))
    cells=[(bounds[i],bounds[i+1]) for i in range(len(bounds)-1)]
    return cells

def trim(m):
    ys,xs=np.where(m)
    if len(ys)==0: return m
    return m[ys.min():ys.max()+1, xs.min():xs.max()+1]

def extract_page(path, kris_lines):
    ink=load_ink(path); mh=med_h(ink); c,rem=clean(ink,mh)
    dlines=find_lines(c,mh)
    # align detected lines to kris logical lines by count (they should be equal len ideally)
    # simple: if same number, 1:1; else best contiguous alignment by DP on rune counts
    kcounts=[len(l) for l in kris_lines]
    # if detected != kris count, do greedy nearest
    glyphs=[]
    if len(dlines)==len(kris_lines):
        pairs=list(zip(dlines,kris_lines))
    else:
        # align by cumulative — fall back: use min length
        m=min(len(dlines),len(kris_lines))
        pairs=list(zip(dlines[:m],kris_lines[:m]))
    for (y0,y1),krow in pairs:
        band=c[y0:y1]
        cells=cut_cells(band,len(krow))
        for (x0,x1),rune in zip(cells,krow):
            sub=band[:,x0:x1]
            tm=trim(sub)
            glyphs.append(dict(rune=rune, y0=int(y0),y1=int(y1),x0=int(x0),x1=int(x1),
                               h=int(tm.shape[0]),w=int(tm.shape[1]),
                               area=int(tm.sum()), mask=tm))
    return glyphs, mh, rem, len(dlines)

def iou(m1,m2):
    H=max(m1.shape[0],m2.shape[0]); W=max(m1.shape[1],m2.shape[1])
    A=np.zeros((H,W),bool);B=np.zeros((H,W),bool)
    A[:m1.shape[0],:m1.shape[1]]=m1.astype(bool)
    B[:m2.shape[0],:m2.shape[1]]=m2.astype(bool)
    u=(A|B).sum(); return (A&B).sum()/u if u else 1.0

if __name__=='__main__':
    kp=kris_pages()
    print('kris pages parsed:', len(kp))
    # test on relikd p0
    g,mh,rem,nl=extract_page('data/relikd/p0.jpg', kp[0])
    print('p0 extracted glyphs:', len(g), 'expected', sum(len(l) for l in kp[0]), 'detlines',nl)
    # cluster purity: for each rune label, mean pairwise IoU of its instances
    from collections import defaultdict
    by=defaultdict(list)
    for gg in g: by[gg['rune']].append(gg['mask'])
    print('rune | count | mean_intra_IoU (sampled)')
    import itertools,random
    intra=[]
    for r,ms in sorted(by.items()):
        if len(ms)<2: continue
        pairs=list(itertools.combinations(range(len(ms)),2))
        random.seed(0); random.shuffle(pairs); pairs=pairs[:30]
        v=np.mean([iou(ms[i],ms[j]) for i,j in pairs])
        intra.append(v)
        print(f'  {r} | {len(ms):3d} | {v:.3f}')
    print('MEAN intra-label IoU:', np.mean(intra))
    # negative: cross-label IoU between two different runes
    labs=[r for r in by if len(by[r])>=2]
    a,b=labs[0],labs[1]
    cross=np.mean([iou(by[a][i],by[b][j]) for i in range(min(5,len(by[a]))) for j in range(min(5,len(by[b])))])
    print(f'NEG cross-label IoU {a} vs {b}:', round(cross,3))
