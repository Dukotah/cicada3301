import os,numpy as np
from PIL import Image
exec(open("analysis/round30/A1-font/variant_cluster.py").read().split("if __name__")[0])
t=open('data/krisyotam_runes.txt').read().split('%')
kp=[parse(b) for b in t if parse(b)]
from collections import defaultdict
allg=defaultdict(list)
for pi in range(min(len(kp),54)):
    path=f'data/relikd/p{pi}.jpg'
    if not os.path.exists(path): continue
    for r,pos,m in extract(path,kp[pi]):
        if m.size>0: allg[r].append((pi,m))
# montage of first 24 clean instances of a few distinctive runes
for rune in ['ᛗ','ᚷ','ᛝ','ᚫ']:
    items=allg[rune]
    ws=np.array([m.shape[1] for _,m in items]); ars=np.array([int(m.sum()) for _,m in items])
    mw=np.median(ws); ma=np.median(ars)
    clean=[m for _,m in items if 0.7*mw<=m.shape[1]<=1.4*mw and 0.7*ma<=int(m.sum())<=1.3*ma][:24]
    ch=max(m.shape[0] for m in clean)+4; cw=max(m.shape[1] for m in clean)+4
    cols=8; rows=(len(clean)+cols-1)//cols
    canvas=np.ones((rows*ch,cols*cw))
    for i,m in enumerate(clean):
        r=i//cols; c=i%cols
        canvas[r*ch:r*ch+m.shape[0], c*cw:c*cw+m.shape[1]]=1-m
    Image.fromarray((canvas*255).astype('uint8')).save(f'analysis/round30/A1-font/montage_{ord(rune):x}.png')
    print('wrote montage for',rune,'n=',len(clean))
