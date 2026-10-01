import os,itertools,random,numpy as np
from PIL import Image
from scipy import ndimage
import importlib.util
spec=importlib.util.spec_from_file_location("vc","analysis/round30/A1-font/variant_cluster.py")
vc=importlib.util.module_from_spec(spec); 
# reuse funcs by exec
exec(open("analysis/round30/A1-font/variant_cluster.py").read().split("if __name__")[0])
t=open('data/krisyotam_runes.txt').read().split('%')
kp=[parse(b) for b in t if parse(b)]
from collections import defaultdict
allg=defaultdict(list)
for pi in range(min(len(kp),54)):
    path=f'data/relikd/p{pi}.jpg'
    if not os.path.exists(path): continue
    for r,pos,m in extract(path,kp[pi]):
        if m.size>0: allg[r].append(m)
# For each rune, take clean crops, find biggest cluster at 0.90, average it -> canonical
canon={}
covers={}
for r in RUNES:
    items=allg[r]
    ws=np.array([m.shape[1] for m in items]); ars=np.array([int(m.sum()) for m in items])
    mw=np.median(ws); ma=np.median(ars)
    clean=[m for m in items if 0.7*mw<=m.shape[1]<=1.4*mw and 0.7*ma<=int(m.sum())<=1.3*ma]
    if len(clean)<6: continue
    clusters,used=single_linkage(clean,thr=0.90,cap=60)
    big=clusters[0]
    # canonical = pixel-vote average of big cluster, aligned to first
    ref=clean[big[0]]
    H=ref.shape[0]+10; W=ref.shape[1]+10
    acc=np.zeros((H,W)); cnt=0
    for i in big:
        m=clean[i]
        # best shift vs ref
        bestv=-1; bp=(0,0)
        for dy in range(-4,5):
            for dx in range(-4,5):
                A=np.zeros((H,W),bool); A[5:5+ref.shape[0],5:5+ref.shape[1]]=ref.astype(bool)
                B=np.zeros((H,W),bool)
                y0=5+dy; x0=5+dx
                if y0<0 or x0<0 or y0+m.shape[0]>H or x0+m.shape[1]>W: continue
                B[y0:y0+m.shape[0],x0:x0+m.shape[1]]=m.astype(bool)
                u=(A|B).sum(); v=(A&B).sum()/u if u else 0
                if v>bestv: bestv=v; bp=(y0,x0)
        y0,x0=bp
        acc[y0:y0+m.shape[0],x0:x0+m.shape[1]]+=m
        cnt+=1
    avg=(acc/cnt)
    # crispness: fraction of pixels that are 'always on or always off' (>0.9 or <0.1) among inked region
    inked=avg[avg>0.1]
    crisp=float((inked>0.9).sum()/max(1,inked.size))
    canon[r]=(len(big),len(clean),crisp)
print("rune | biggest_cluster | clean | crispness(frac pixels >0.9 consensus among inked)")
for r in RUNES:
    if r in canon:
        b,c,cr=canon[r]
        print(f"  {r} | {b:3d}/{c:3d} | crisp={cr:.2f}")
