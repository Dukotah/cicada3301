#!/usr/bin/env python3
"""Valley-based line segmentation: choose exactly N-1 boundaries at the lowest-ink
columns, with a minimum-cell-width constraint, to split a line into N rune cells.
Then render a debug overlay for one line."""
import sys, os, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
THRESH=128
R2I={r:i for i,r in enumerate('ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ')}

def load_ink(p):
    a=np.asarray(Image.open(p).convert('L')); return (a<THRESH).astype(np.uint8), a
def med_h(ink):
    lbl,n=ndimage.label(ink); sl=ndimage.find_objects(lbl)
    hs=sorted((s[0].stop-s[0].start) for s in sl if s); return hs[len(hs)//2] if hs else 0
def clean(ink,mh):
    lbl,n=ndimage.label(ink); sl=ndimage.find_objects(lbl); keep=np.zeros_like(ink)
    for i,s in enumerate(sl,1):
        if not s: continue
        h=s[0].stop-s[0].start; w=s[1].stop-s[1].start
        if h>1.6*mh or w>1.6*mh: continue
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
    """Return n+1 boundaries splitting [0,W] into n cells. Greedy: pick the n-1
    lowest-ink columns s.t. each is >=min_w from neighbors and cell edges."""
    W=len(cols)
    if n<=1: return [0,W]
    # candidate cut columns sorted by ink asc; ties broken by proximity to equal spacing
    order=sorted(range(1,W), key=lambda x:(cols[x], ))
    chosen=[]
    for x in order:
        if all(abs(x-c)>=min_w for c in chosen) and x>=min_w and x<=W-min_w:
            chosen.append(x)
        if len(chosen)==n-1: break
    chosen=sorted(chosen)
    return [0]+chosen+[W]

def main(path, line_idx, kris_line_runes):
    ink,gray=load_ink(path); mh=med_h(ink); c=clean(ink,mh)
    lines=find_lines(c,mh)
    y0,y1=lines[line_idx]
    band=c[y0:y1]; cols=band.sum(0).astype(float)
    n=len(kris_line_runes)
    W=len(cols)
    min_w=max(6,int(W/n*0.45))
    b=valley_boundaries(cols,n,min_w)
    # debug overlay
    crop=Image.open(path).convert('RGB').crop((0,y0,ink.shape[1],y1))
    d=ImageDraw.Draw(crop)
    for x in b:
        d.line([(x,0),(x,y1-y0)],fill=(255,0,0),width=2)
    crop.save('analysis/round30/A1-font/debug_line.png')
    print('line',line_idx,'y',(y0,y1),'W',W,'n',n,'bounds',len(b)-1,'min_w',min_w)
    print('boundaries:',b)
    print('kris runes:', ''.join(kris_line_runes))

if __name__=='__main__':
    t=open('data/krisyotam_runes.txt').read().split('%')
    blk=t[0]; lines=[]
    for ln in blk.replace('/','\n').split('\n'):
        rs=[c for c in ln if c in R2I]
        if rs: lines.append(rs)
    main('data/relikd/p0.jpg', int(sys.argv[1]) if len(sys.argv)>1 else 1, lines[int(sys.argv[1]) if len(sys.argv)>1 else 1])
