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
    if len(segs)<8: return []
    gaps=[segs[i+1][0]-segs[i][1] for i in range(len(segs)-1)];sg=sorted(gaps)
    thr=(sg[-7]+sg[-8])/2 if len(sg)>=8 else 30
    toks=[];cur=[segs[0][0],segs[0][1]]
    for i in range(1,len(segs)):
        if segs[i][0]-cur[1]>thr:toks.append(tuple(cur));cur=[segs[i][0],segs[i][1]]
        else:cur[1]=segs[i][1]
    toks.append(tuple(cur));return toks
def firstchar_glyph(ink,x0,x1,y0,y1,span=118):
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
    a,b=merged[0];col=sub[:,a:b];rows=np.where(col.sum(axis=1)>0)[0]
    g=col[rows.min():rows.max()+1]
    return np.asarray(Image.fromarray((g*255).astype(np.uint8)).resize((24,40),Image.LANCZOS))>128

# The first char of every token is a digit 0-4. Compare renders of same digit -> variant test.
# rows per page:
rowsets={49:[(49,y0,y1) for y0,y1 in [(1249,1319),(1429,1498),(1608,1677),(1787,1856),(1966,2035),(2145,2217),(2324,2393),(2503,2572),(2683,2755),(2861,2933)]],
         50:[(50,y0,y1) for y0,y1 in [(629,698),(809,878),(987,1056),(1167,1236),(1346,1415),(1525,1594),(1704,1773),(1883,1952),(2062,2131),(2241,2333),(2419,2489),(2599,2668),(2773,2847)]],
         51:[(51,y0,y1) for y0,y1 in [(629,701),(809,878),(987,1056),(1167,1236),(1346,1416),(1525,1594),(1704,1773),(1883,1952),(2062,2131)]]}
imgs={}
def get(p):
    if p not in imgs:imgs[p]=load(f"/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/relikd/p{p}.jpg")
    return imgs[p]
import collections
digit_glyphs=collections.defaultdict(list)
# read relikd tokens to know the first digit of each cell
import re
tokrows=[]
for line in open("/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/relikd/p40-53.txt"):
    if re.match(r'^\s*[0-9A-Za-z]{2}([ \t]+[0-9A-Za-z]{2}){7}\s*$',line):
        tokrows.append(line.split())
# The 3 tables: 10 rows p49, 13 rows p50, 9 rows p51 = but tokrows also include p40-48,52,53.
# match by count: find the run of 10 then 13 then 9? too fragile. Just measure glyph consistency
# of first-chars grouped by their pixel cluster within pages instead.
allg=[]
for p in (49,50,51):
    im,ink=get(p)
    for _,y0,y1 in rowsets[p]:
        for (x0,x1) in token_boxes(ink,y0,y1):
            try: allg.append(firstchar_glyph(ink,x0,x1,y0,y1))
            except: pass
print(f"collected {len(allg)} first-char glyphs")
# cluster: for each pair compute hamming; report distribution of nearest-neighbor distances
G=np.array([g.flatten() for g in allg]).astype(int)
# group identical-ish: build distance matrix
from itertools import combinations
mins=[]
for i in range(len(G)):
    d=np.abs(G-G[i]).sum(axis=1); d[i]=9999
    mins.append(d.min())
print(f"nearest-neighbor hamming distances: min={min(mins)} median={int(np.median(mins))} max={max(mins)}")
print("If a digit had 2 variant forms, we'd see clean bimodal clusters. Distribution of NN dist:")
import numpy as np2
hist,edges=np.histogram(mins,bins=8)
for h,e0,e1 in zip(hist,edges[:-1],edges[1:]):
    print(f"  {e0:5.0f}-{e1:5.0f}: {'#'*h} ({h})")
