import os,random,numpy as np
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
labs=list(allg); random.seed(7)
hits=defaultdict(int)
for _ in range(20000):
    a,b=random.sample(labs,2)
    ma=random.choice(allg[a]); mb=random.choice(allg[b])
    if ma.shape==mb.shape and np.array_equal(ma,mb):
        pair=tuple(sorted([a,b])); hits[pair]+=1
        # what area?
print('cross-rune identical pairs by rune-pair (20k samples):')
for k,v in sorted(hits.items(),key=lambda x:-x[1]):
    # sample area
    print(f'  {k[0]} vs {k[1]}: {v}  (areas ~{int(np.median([m.sum() for m in allg[k[0]]]))},{int(np.median([m.sum() for m in allg[k[1]]]))})')
