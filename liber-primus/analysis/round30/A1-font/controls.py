import os,itertools,random,numpy as np,json
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
# NEG control: cross-rune byte-identity should be ZERO
neg_ident=0; neg_pairs=0
labs=list(allg)
random.seed(7)
for _ in range(3000):
    a,b=random.sample(labs,2)
    ma=random.choice(allg[a]); mb=random.choice(allg[b])
    neg_pairs+=1
    if ma.shape==mb.shape and np.array_equal(ma,mb): neg_ident+=1
# POS: within-rune byte-identity count (clean)
pos_ident=0; pos_pairs=0
for r in labs:
    items=allg[r]
    ws=np.array([m.shape[1] for m in items]); mw=np.median(ws)
    clean=[m for m in items if abs(m.shape[1]-mw)<=3]
    random.seed(9); random.shuffle(clean); clean=clean[:40]
    for a,b in itertools.combinations(clean,2):
        pos_pairs+=1
        if a.shape==b.shape and np.array_equal(a,b): pos_ident+=1
print(f'NEG (different runes): {neg_ident}/{neg_pairs} byte-identical pairs')
print(f'POS (same rune, clean): {pos_ident}/{pos_pairs} byte-identical pairs')
json.dump(dict(neg_ident=neg_ident,neg_pairs=neg_pairs,pos_ident=pos_ident,pos_pairs=pos_pairs),
          open('analysis/round30/A1-font/controls.json','w'),indent=1)
