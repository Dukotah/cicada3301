#!/usr/bin/env python3
"""Analyze inter-token gaps within a line to find glyph-splitting threshold."""
import sys, numpy as np
from PIL import Image
from scipy import ndimage
THRESH=128
def load_ink(p):
    a=np.asarray(Image.open(p).convert('L')); return (a<THRESH).astype(np.uint8)
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
def lines(ink):
    r=ink.sum(1)>0; out=[]; st=None
    for y,v in enumerate(r):
        if v and st is None: st=y
        elif not v and st is not None: out.append((st,y)); st=None
    if st is not None: out.append((st,len(r)))
    return out
ink=load_ink(sys.argv[1]); mh=med_h(ink); c=clean(ink,mh)
gaps=[]; widths=[]
for y0,y1 in lines(c):
    cols=c[y0:y1].sum(0)>0
    toks=[]; st=None
    for x,v in enumerate(cols):
        if v and st is None: st=x
        elif not v and st is not None: toks.append((st,x)); st=None
    if st is not None: toks.append((st,len(cols)))
    for i in range(len(toks)):
        widths.append(toks[i][1]-toks[i][0])
        if i>0: gaps.append(toks[i][0]-toks[i-1][1])
gaps=np.array(sorted(gaps)); widths=np.array(sorted(widths))
print('med_h',mh)
print('GAP pctiles:',[int(np.percentile(gaps,p)) for p in (10,25,50,60,70,75,80,90)])
print('gap histogram (bins of 5):')
import collections
h=collections.Counter((g//5)*5 for g in gaps)
for k in sorted(h): print(f'  {k:3d}-{k+4:3d}: {h[k]}')
print('WIDTH pctiles:',[int(np.percentile(widths,p)) for p in (5,10,25,50,75,90)])
