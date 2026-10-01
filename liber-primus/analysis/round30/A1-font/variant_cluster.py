#!/usr/bin/env python3
"""
Variant channel test. For each rune, take CLEAN crops, build an IoU graph
(best-aligned), single-linkage cluster at threshold 0.90. Count clusters with
>=5 members ('real' shape clusters). If a rune has 2+ big clusters that are
mutually distinct (cross-cluster IoU well below 0.90), that's a genuine glyph
variant = a candidate hidden channel. Otherwise 1 dominant cluster + noise.

We also compute, for the dominant cluster, a 'canonical' averaged glyph and
report each rune's variant count. Then, IF variants exist, we extract the
per-occurrence variant label in reading order and test it as data (entropy).
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
    out=[]; pos=0
    for (y0,y1),krow in zip(dl,kris):
        band=c[y0:y1]; cs=band.sum(0); nz=np.where(cs>0)[0]
        if len(nz)==0: continue
        xL,xR=nz[0],nz[-1]+1; sub=band[:,xL:xR]; cols=sub.sum(0).astype(float)
        n=len(krow); min_w=max(4,int((xR-xL)/n*0.40)); b=valley_boundaries(cols,n,min_w)
        if len(b)-1!=n: b=[int(round((xR-xL)*k/n)) for k in range(n+1)]
        for k,rune in enumerate(krow):
            out.append((rune,pos,trim(sub[:,b[k]:b[k+1]]))); pos+=1
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

def single_linkage(masks, thr=0.90, cap=60):
    n=len(masks); parent=list(range(n))
    def find(x):
        while parent[x]!=x: parent[x]=parent[parent[x]]; x=parent[x]
        return x
    def uni(a,b):
        ra,rb=find(a),find(b)
        if ra!=rb: parent[ra]=rb
    idx=list(range(n))
    if n>cap:
        random.seed(3); random.shuffle(idx); idx=idx[:cap]
    for a,b in itertools.combinations(idx,2):
        if best_iou(masks[a],masks[b])>=thr: uni(a,b)
    from collections import defaultdict
    cl=defaultdict(list)
    for i in idx: cl[find(i)].append(i)
    return sorted(cl.values(),key=len,reverse=True), idx

if __name__=='__main__':
    t=open('data/krisyotam_runes.txt').read().split('%')
    kp=[parse(b) for b in t if parse(b)]
    from collections import defaultdict
    allg=defaultdict(list)
    for pi in range(min(len(kp),54)):
        path=f'data/relikd/p{pi}.jpg'
        if not os.path.exists(path): continue
        for r,pos,m in extract(path,kp[pi]):
            if m.size>0: allg[r].append(m)
    print('=== VARIANT CLUSTERING (single-linkage IoU>=0.90 on clean crops) ===')
    summary={}
    for r in RUNES:
        items=allg[r]
        ws=np.array([m.shape[1] for m in items]); ars=np.array([int(m.sum()) for m in items])
        mw=np.median(ws); ma=np.median(ars)
        clean=[m for m in items if 0.7*mw<=m.shape[1]<=1.4*mw and 0.7*ma<=int(m.sum())<=1.3*ma]
        if len(clean)<6:
            print(f'  {r}: clean={len(clean)} too few'); summary[r]=dict(clean=len(clean),big_clusters=None); continue
        clusters,used=single_linkage(clean,thr=0.90,cap=60)
        big=[c for c in clusters if len(c)>=5]
        sizes=[len(c) for c in clusters[:5]]
        summary[r]=dict(clean=len(clean),sampled=len(used),cluster_sizes=sizes,n_big=len(big))
        print(f'  {r}: clean={len(clean):3d} sampled={len(used)} top-cluster-sizes={sizes} big(>=5)={len(big)}')
    json.dump(summary, open('analysis/round30/A1-font/variant_clusters.json','w'), indent=1)
    print('wrote variant_clusters.json')
    # verdict
    multi=[r for r,v in summary.items() if v.get('n_big') and v['n_big']>=2]
    print('RUNES WITH >=2 BIG SHAPE CLUSTERS (variant candidates):', multi if multi else 'NONE')
